# Guia Aprimorado: Deploy de Django no Fly.io

Este guia detalha o processo de deploy de uma aplicação Django na plataforma Fly.io, otimizado com boas práticas para um ambiente de produção.

## Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas:

1.  **Docker Desktop:** A Fly.io utiliza Docker para "empacotar" e distribuir sua aplicação de forma consistente.
      * Instale a partir do [site oficial do Docker](https://www.docker.com/products/docker-desktop/).
2.  **flyctl (Fly.io CLI):** A ferramenta de linha de comando para interagir com a plataforma Fly.io.
      * Instale seguindo as instruções no [site oficial da Fly.io](https://fly.io/docs/hands-on/install-flyctl/).

## Passo 1: Iniciação do Projeto (`fly launch`)

Este comando interativo analisa seu código e gera os arquivos de configuração iniciais.

  * **Ação:** No terminal, na pasta raiz do seu projeto, execute:
    ```bash
    flyctl launch
    ```
  * **Responda às perguntas:**
      * **App Name:** Escolha um nome único (ex: `gateway-service-seu-nome`).
      * **Region:** Escolha uma região perto de você ou de seus usuários (ex: `gru` para São Paulo, Brasil).
      * **Postgres database:** Responda **`Yes`**. Isso cria um banco de dados e já configura o `DATABASE_URL` para você.
      * **Deploy now?:** Responda **`No`**. Vamos primeiro ajustar os arquivos gerados.

Isso criará os arquivos `fly.toml` e `Dockerfile`.

## Passo 2: O `Dockerfile` Otimizado

Este arquivo é a "receita" para construir sua aplicação. O gerado pela Fly.io é bom, mas podemos otimizá-lo para Django, garantindo que os arquivos estáticos sejam servidos corretamente pelo `whitenoise`.

  * **Ação:** Abra o `Dockerfile` e substitua seu conteúdo por este:

    ```dockerfile
    # Etapa 1: Builder - Instala dependências e prepara o build
    # Usar uma imagem base de Python leve e segura
    FROM python:3.9-slim-bullseye as builder

    # Define variáveis de ambiente para otimizar o build em Docker
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1

    WORKDIR /app

    # Instala as dependências Python em um ambiente virtual
    RUN python -m venv /opt/venv
    ENV PATH="/opt/venv/bin:$PATH"

    # Copia e instala as dependências de forma otimizada para cache
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Copia todo o código da aplicação
    COPY . .

    # Coleta todos os arquivos estáticos para um diretório que será servido pelo WhiteNoise
    RUN python manage.py collectstatic --noinput


    # Etapa 2: Runner - Cria a imagem final, mais leve
    FROM python:3.9-slim-bullseye

    WORKDIR /app

    # Copia apenas o ambiente virtual com as dependências da etapa anterior
    COPY --from=builder /opt/venv /opt/venv
    # Copia apenas os arquivos da aplicação e os estáticos coletados
    COPY --from=builder /app /app

    # Ativa o ambiente virtual para o comando final
    ENV PATH="/opt/venv/bin:$PATH"

    # Expõe a porta que o Gunicorn irá escutar
    EXPOSE 8000

    # Comando final para iniciar o servidor Gunicorn em produção
    CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
    ```

## Passo 3: O `fly.toml` Completo e Anotado

Este é o arquivo de configuração principal da Fly.io. Vamos garantir que ele esteja completo.

  * **Ação:** Abra seu `fly.toml` e substitua o conteúdo por este exemplo, **ajustando o `app = "..."` para o nome que você escolheu**.

    ```toml
    # fly.toml

    # Nome da sua aplicação na Fly.io. DEVE ser o mesmo que você escolheu no 'fly launch'.
    app = "seu-app-django"
    primary_region = "gru"
    kill_signal = "SIGINT"
    kill_timeout = "5s"

    [build]
      # Informa à Fly.io para usar o Dockerfile local para construir a imagem.
      builder = "dockerfile"

    [deploy]
      # Comando executado automaticamente após um deploy bem-sucedido, antes de liberar a nova versão.
      # Perfeito para rodar migrações do banco de dados.
      release_command = "python manage.py migrate"

    [[http_service]]
      # Porta interna que sua aplicação (Gunicorn) está escutando.
      internal_port = 8000
      # Redireciona automaticamente todo o tráfego HTTP para HTTPS.
      force_https = true
      auto_stop_machines = true
      auto_start_machines = true
      min_machines_running = 0 # Para o plano gratuito, use 0 para que a máquina pare quando não estiver em uso.
      # Se quiser que a máquina fique sempre ligada (pode consumir mais créditos), mude para 1.

      [http_service.concurrency]
        # Configurações de quantas requisições simultâneas uma máquina pode receber.
        type = "connections"
        hard_limit = 25
        soft_limit = 20
    ```

## Passo 4: Configurando os "Secrets"

"Secrets" são as variáveis de ambiente seguras. O `DATABASE_URL` já foi criado, mas precisamos adicionar as outras.

  * **Ação:** Execute os comandos abaixo no seu terminal. **Lembre-se de substituir `seu-app-django` pelo nome real da sua app.**

    ```bash
    # Gere uma nova chave segura para produção! Não use a de desenvolvimento.
    # Você pode usar 'python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"' para gerar uma.
    flyctl secrets set DJANGO_SECRET_KEY="sua-nova-chave-secreta-aqui" --app seu-app-django

    # Suas URLs do provedor externo
    flyctl secrets set EXTERNAL_PROVIDER_API_URL="http://18.228.211.130:4567/api/graphql" --app seu-app-django
    flyctl secrets set EXTERNAL_PROVIDER_BASE_URL="http://18.228.211.130:4567/" --app seu-app-django

    # IMPORTANTE: Configure os hosts permitidos. Use apenas o domínio da Fly.io.
    flyctl secrets set DJANGO_ALLOWED_HOSTS="seu-app-django.fly.dev" --app seu-app-django

    # Garante que o modo DEBUG esteja desativado em produção
    flyctl secrets set DJANGO_DEBUG="False" --app seu-app-django
    ```

## Passo 5: Deploy Final e Verificação

Com tudo pronto, o passo final é realizar o deploy.

  * **Comando de Deploy:**

    ```bash
    flyctl deploy
    ```

  * **Comandos Úteis Pós-Deploy:**

      * **Ver os logs da aplicação:**
        ```bash
        flyctl logs
        ```
      * **Ver o status da aplicação:**
        ```bash
        flyctl status
        ```
      * **Abrir o site no navegador:**
        ```bash
        flyctl open
        ```
      * **Acessar o console do Django (ex: `shell_plus` ou `shell`):**
        ```bash
        flyctl ssh console -C "/app/manage.py shell"
        ```