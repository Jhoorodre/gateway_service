import requests
from urllib.parse import urljoin
from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .api_service import execute_externalprovider_query # Assumindo que api_service.py também será atualizado

# --- Função Auxiliar ---
def _make_graphql_request(query, variables=None, timeout=30):
    external_provider_url = settings.EXTERNAL_PROVIDER_API_URL
    external_provider_url_2 = getattr(settings, 'EXTERNAL_PROVIDER_API_URL_2', None)
    json_payload = {'query': query, 'variables': variables or {}}
    try:
        response = requests.post(external_provider_url, json=json_payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        if 'errors' in data and external_provider_url_2:
            # Se a resposta da primeira URL tem erro, tenta a segunda
            response2 = requests.post(external_provider_url_2, json=json_payload, timeout=timeout)
            response2.raise_for_status()
            data2 = response2.json()
            if 'errors' in data2:
                return None, Response({"error": "Erro nas duas APIs GraphQL do ExternalProvider.", "details": [data['errors'], data2['errors']]}, status=status.HTTP_502_BAD_GATEWAY)
            return data2, None
        if 'errors' in data:
            return None, Response({"error": "Erro na resposta da API GraphQL do ExternalProvider.", "details": data['errors']}, status=status.HTTP_502_BAD_GATEWAY)
        return data, None
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
        # Se a primeira URL falhar, tenta a segunda
        if external_provider_url_2:
            try:
                response2 = requests.post(external_provider_url_2, json=json_payload, timeout=timeout)
                response2.raise_for_status()
                data2 = response2.json()
                if 'errors' in data2:
                    return None, Response({"error": "Erro na segunda API GraphQL do ExternalProvider.", "details": data2['errors']}, status=status.HTTP_502_BAD_GATEWAY)
                return data2, None
            except Exception as e2:
                return None, Response({"error": "Falha ao comunicar com ambas as APIs do ExternalProvider.", "details": [str(e), str(e2)]}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return None, Response({"error": "Falha ao comunicar com o ExternalProvider-Server.", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except ValueError as e:
        return None, Response({"error": "Resposta inválida do ExternalProvider-Server (formato não JSON).", "details": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

# --- Views da API ---

@ratelimit(key='ip', rate=f'{settings.RATE_LIMIT_PER_MINUTE}/m', method='ALL', block=True)
@api_view(['GET'])
def status_check(request):
    return Response({"status": "ok", "message": "API Gateway está funcionando!"})

@api_view(['GET'])
def list_content_providers(request):
    graphql_query = "query GetSourcesList { sources { nodes { id, name, lang, iconUrl, isNsfw } } }"
    data, error_response = _make_graphql_request(graphql_query)
    if error_response: return error_response
    # Adicionando verificação se data é None antes de prosseguir
    if data is None:
        return Response({"error": "Não foi possível obter dados da API ExternalProvider."}, status=status.HTTP_502_BAD_GATEWAY)
    providers_list = data.get("data", {}).get("sources", {}).get("nodes", [])
    formatted_providers = [{"id": p.get("id"),"name": p.get("name"),"language": p.get("lang"),"icon_url_proxy": f"/api/v1/image-proxy/?url={p.get('iconUrl')}" if p.get("iconUrl") else None,"is_nsfw": p.get("isNsfw")} for p in providers_list]
    return Response(formatted_providers)

@api_view(['GET'])
def search_content(request):
    provider_id = request.query_params.get('provider_id')
    search_type = request.query_params.get('type', 'SEARCH').upper()
    query_term = request.query_params.get('query')
    page = int(request.query_params.get('page', 1))
    # Novo: Aceita filtros customizados como JSON serializado
    import json
    filters_json = request.query_params.get('filters')
    filters_dict = None
    if filters_json:
        try:
            filters_dict = json.loads(filters_json)
        except Exception as e:
            return Response({"error": "Formato inválido para o parâmetro 'filters' (deve ser JSON serializado).", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if not provider_id:
        return Response({"error": "Parâmetro 'provider_id' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
    
    mangas_list, has_more = [], False
    data = None # Inicializa data como None

    if search_type == 'SEARCH':
        if not query_term and not filters_dict:
            return Response({"error": "Parâmetro 'query' ou 'filters' é obrigatório para o tipo 'SEARCH'."}, status=status.HTTP_400_BAD_REQUEST)
        graphql_mutation = """
        fragment MANGA_BASE_FIELDS on MangaType {
            id
            title
            thumbnailUrl
            thumbnailUrlLastFetched
            inLibrary
            initialized
            sourceId
            __typename
        }
        mutation GET_SOURCE_MANGAS_FETCH($input: FetchSourceMangaInput!) {
            fetchSourceManga(input: $input) {
                hasNextPage
                mangas {
                    ...MANGA_BASE_FIELDS
                    __typename
                }
                __typename
            }
        }
        """
        # Novo: repassa os filtros customizados se existirem
        input_payload = {
            "type": "SEARCH",
            "source": provider_id,
            "page": page
        }
        if query_term:
            input_payload["query"] = query_term
        if filters_dict:
            input_payload["filters"] = filters_dict
        variables = {"input": input_payload}
        data, error_response = _make_graphql_request(graphql_mutation, variables, timeout=60)
        if error_response: return error_response
        if data is None:
            return Response({"error": "Não foi possível obter dados da busca na API ExternalProvider."}, status=status.HTTP_502_BAD_GATEWAY)
        results_data = data.get("data", {}).get("fetchSourceManga", {})
        mangas_list = results_data.get("mangas", [])
        has_more = results_data.get("hasNextPage", False)
    elif search_type == 'POPULAR':
        page = int(request.query_params.get('page', 1))
        graphql_mutation = "mutation FetchSourceManga($input: FetchSourceMangaInput!) { fetchSourceManga(input: $input) { hasNextPage, mangas { id, title, thumbnailUrl, sourceId } } }"
        variables = {"input": {"type": "POPULAR", "source": provider_id, "page": page}}
        data, error_response = _make_graphql_request(graphql_mutation, variables, timeout=60)
        if error_response: return error_response
        if data is None: # Verificação de data
            return Response({"error": "Não foi possível obter dados de populares na API ExternalProvider."}, status=status.HTTP_502_BAD_GATEWAY)
        results_data = data.get("data", {}).get("fetchSourceManga", {})
        mangas_list = results_data.get("mangas", [])
        has_more = results_data.get("hasNextPage", False)
    elif search_type == 'LATEST':
        page = int(request.query_params.get('page', 1))
        graphql_mutation = "mutation FetchSourceManga($input: FetchSourceMangaInput!) { fetchSourceManga(input: $input) { hasNextPage, mangas { id, title, thumbnailUrl, sourceId } } }"
        variables = {"input": {"type": "LATEST", "source": provider_id, "page": page}}
        data, error_response = _make_graphql_request(graphql_mutation, variables, timeout=60)
        if error_response: return error_response
        if data is None: # Verificação de data
            return Response({"error": "Não foi possível obter dados de latest na API ExternalProvider."}, status=status.HTTP_502_BAD_GATEWAY)
        results_data = data.get("data", {}).get("fetchSourceManga", {})
        mangas_list = results_data.get("mangas", [])
        has_more = results_data.get("hasNextPage", False)
    else:
        return Response({"error": f"Tipo de busca inválido: '{search_type}'. Use 'POPULAR', 'LATEST' ou 'SEARCH'."}, status=status.HTTP_400_BAD_REQUEST)
    
    formatted_results = [{"provider_id": item.get("sourceId"),"content_id": str(item.get("id")),"title": item.get("title"),"thumbnail_url_proxy": f"/api/v1/image-proxy/?url={item.get('thumbnailUrl')}" if item.get("thumbnailUrl") else None} for item in mangas_list]
    return Response({"results": formatted_results, "has_more": has_more})

@api_view(['GET'])
def get_manga_details(request, provider_id, content_id):
    """
    Busca os detalhes e a lista de capítulos de um mangá específico,
    com a estrutura de variáveis para a busca de capítulos corrigida.
    """
    try:
        manga_id_as_int = int(content_id)
    except ValueError:
        return Response({"error": "O content_id deve ser um número válido."}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Primeira Chamada: Buscar os detalhes do Mangá
    details_query = "query GetMangaDetails($id: Int!) { manga(id: $id) { id, sourceId, title, author, artist, description, genre, status, thumbnailUrl } }"
    details_data, error_response = _make_graphql_request(details_query, {"id": manga_id_as_int})
    if error_response: return error_response
    
    # Adicionando a verificação para details_data como sugerido anteriormente para robustez
    if details_data is None:
        return Response({"error": "Não foi possível obter dados de detalhes do mangá da API ExternalProvider (details_data is None)."}, status=status.HTTP_502_BAD_GATEWAY)
        
    manga_details = details_data.get("data", {}).get("manga")
    if not manga_details:
        return Response({"error": f"Conteúdo com id '{content_id}' não encontrado ou dados de mangá ausentes na resposta."}, status=status.HTTP_404_NOT_FOUND)

    # 2. Segunda Chamada: Buscar a lista de Capítulos
    chapters_query = "query GetMangaChapters($condition: ChapterConditionInput, $order: [ChapterOrderInput!]) { chapters(condition: $condition, order: $order) { nodes { id, name, chapterNumber, scanlator, uploadDate } } }"
    
    chapters_variables = {
        "condition": {
            "mangaId": manga_id_as_int
        },
        "order": [{
            "by": "SOURCE_ORDER",
            "byType": "DESC"
        }]
    }

    chapters_data, error_response = _make_graphql_request(chapters_query, variables=chapters_variables)
    chapters_list = []
    if not error_response:
        # Adicionando verificação para chapters_data para robustez
        if chapters_data is None:
            # Considerar logar isso ou decidir se é um erro que deve parar o fluxo
            # Por enquanto, permite que a resposta seja enviada com capítulos vazios se a query falhar silenciosamente
            pass # chapters_list permanecerá vazia
        else:
            chapters_list = chapters_data.get("data", {}).get("chapters", {}).get("nodes", [])

    # 3. Montar a resposta final
    final_response = {
        "provider_id": manga_details.get("sourceId"), 
        "content_id": str(manga_details.get("id")),
        "title": manga_details.get("title"), 
        "author": manga_details.get("author"), 
        "artist": manga_details.get("artist"),
        "description": manga_details.get("description"), 
        "status": manga_details.get("status"), 
        "genres": manga_details.get("genre", []),
        "thumbnail_url_proxy": f"/api/v1/image-proxy/?url={manga_details.get('thumbnailUrl')}" if manga_details.get("thumbnailUrl") else None,
        "chapters": [
            {
                "id": str(c.get("id")),
                "name": c.get("name"),
                "chapter_number": c.get("chapterNumber"),
                "scanlator": c.get("scanlator"),
                "uploaded_at": c.get("uploadDate")
            } for c in chapters_list
        ]
    }
    return Response(final_response)

@api_view(['GET'])
def get_chapter_pages(request, provider_id, content_id, chapter_id):
    """
    PASSO 2 DO FLUXO: Busca as páginas de um capítulo específico.
    """
    try:
        chapter_id_as_int = int(chapter_id)
    except ValueError:
        return Response({"error": "O chapter_id fornecido não é um número válido."}, status=status.HTTP_400_BAD_REQUEST)

    # 2.1: Terceira Chamada (Backend) -> GET_CHAPTER_PAGES_FETCH para obter as URLs das páginas.
    graphql_mutation = "mutation FetchChapterPages($input: FetchChapterPagesInput!) { fetchChapterPages(input: $input) { pages } }"
    variables = {"input": {"chapterId": chapter_id_as_int}}
    data, error_response = _make_graphql_request(graphql_mutation, variables, timeout=90)
    if error_response: return error_response
    if data is None: # Verificação de data
        return Response({"error": "Não foi possível obter dados das páginas do capítulo na API ExternalProvider."}, status=status.HTTP_502_BAD_GATEWAY)
    
    pages_data = data.get("data", {}).get("fetchChapterPages", {})
    # A verificação de pages_data e "pages" in pages_data já estava boa
    if pages_data is None or not isinstance(pages_data, dict) or "pages" not in pages_data or pages_data.get("pages") is None:
        return Response({"error": f"Páginas para o capítulo '{chapter_id}' não encontradas ou resposta inválida do ExternalProvider."}, status=status.HTTP_404_NOT_FOUND)
        
    page_urls = pages_data.get("pages", [])
    if page_urls is None: page_urls = [] # Segurança adicional

    # Retornando a estrutura completa como na versão anterior que funcionava
    formatted_pages = [
        {
            "page_index": i, 
            "proxy_image_url": f"/api/v1/image-proxy/?url={url}" if url else None,
            "original_url": url # Incluindo a original_url
        } for i, url in enumerate(page_urls)
    ]
    return Response({
        "provider_id": provider_id,
        "content_id": content_id,
        "chapter_id": chapter_id,
        "pages": formatted_pages
    })

@api_view(['GET'])
def image_proxy(request):
    original_url = request.query_params.get('url')
    if not original_url:
        return Response({"error": "Parâmetro 'url' não fornecido."}, status=status.HTTP_400_BAD_REQUEST)
    if original_url.startswith('/'):
        external_provider_base_url = settings.EXTERNAL_PROVIDER_BASE_URL
        if not external_provider_base_url:
             return Response({"error": "EXTERNAL_PROVIDER_BASE_URL não está configurada."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        full_image_url = urljoin(external_provider_base_url, original_url)
    else:
        full_image_url = original_url
    try:
        # Adicionando User-Agent como na versão anterior bem-sucedida
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        print(f"Proxying image from: {full_image_url}")
        response = requests.get(full_image_url, stream=True, timeout=20, headers=headers)
        response.raise_for_status()
        return StreamingHttpResponse(response.iter_content(chunk_size=8192), content_type=response.headers['Content-Type'])
    except requests.exceptions.RequestException as e:
        print(f"Falha na requisição da imagem externa ({full_image_url}): {e}")
        return Response({"error": f"Falha na requisição da imagem externa ({original_url}): {e}"}, status=status.HTTP_502_BAD_GATEWAY)

GET_SOURCE_BROWSE_QUERY = """
    query GET_SOURCE_BROWSE($id: LongString!) {
      source(id: $id) {
        id
        name
        filters {
          ... on GroupFilter {
            type: __typename
            name
            filters {
              ... on CheckBoxFilter {
                type: __typename
                name
              }
              ... on SelectFilter {
                 type: __typename
                 name
                 values
              }
              # Adicionar outros tipos de filtro conforme necessário
            }
          }
          # Adicionar outros tipos de filtro de nível superior se existirem
        }
      }
    }
"""

class SourceFiltersView(APIView):
    """
    View para buscar os filtros de uma fonte específica no ExternalProvider.
    """
    def get(self, request, *args, **kwargs):
        provider_id = request.query_params.get('provider_id')

        if not provider_id:
            return JsonResponse({'error': 'O parâmetro provider_id é obrigatório.'}, status=400)

        variables = {'id': provider_id}

        try:
            external_provider_data = execute_externalprovider_query(
                query=GET_SOURCE_BROWSE_QUERY,
                variables=variables
            )

            if external_provider_data.get('errors'):
                 return JsonResponse({'error': 'Erro retornado pela API ExternalProvider', 'details': external_provider_data['errors']}, status=502)

            source_data = external_provider_data.get('data', {}).get('source', {})
            return JsonResponse(source_data)

        except Exception as e:
            return JsonResponse({'error': f'Erro interno no servidor: {str(e)}'}, status=500)