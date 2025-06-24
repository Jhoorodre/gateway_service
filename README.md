# Gateway Service - Backend Django

## 🚀 Setup Local

### 1. Pré-requisitos

```bash
# Python 3.10+
python --version

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configuração de Ambiente

```bash
# Copiar arquivo de exemplo
# cp .env.example .env (Se existir um .env.example)

# Crie um arquivo .env e adicione as variáveis necessárias
# Exemplo:
# DJANGO_SECRET_KEY=sua_chave_secreta_aqui
# DATABASE_URL=sqlite:///./db.sqlite3
# EXTERNAL_PROVIDER_API_URL=http://seu_provedor_externo/api/graphql
# EXTERNAL_PROVIDER_BASE_URL=http://seu_provedor_externo/
# DJANGO_DEBUG=True
# DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Banco de Dados e Django

```bash
# Aplicar migrations
python manage.py makemigrations
python manage.py migrate

# Criar superuser (opcional)
python manage.py createsuperuser

# Coletar arquivos estáticos (para produção ou teste com WhiteNoise)
python manage.py collectstatic --noinput
```

### 4. Executar

```bash
# Desenvolvimento
python manage.py runserver 0.0.0.0:8000

# Produção local (simulando Gunicorn)
# (Porta pode ser definida pela variável $PORT)
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

## 📦 Deploy

### Fly.io (Configuração Atual)

Este projeto está configurado para deploy no Fly.io usando Docker.

1. **Instalar `flyctl`**:
   Siga as instruções em [https://fly.io/docs/hands-on/install-flyctl/](https://fly.io/docs/hands-on/install-flyctl/).

2. **Login no Fly.io**:

   ```bash
   flyctl auth login
   ```

3. **Launch Inicial (apenas na primeira vez para um novo app)**:

   ```bash
   flyctl launch
   ```

   * Responda às perguntas. Se for solicitado para ajustar configurações via web, você poderá definir o nome do app (ex: `seu-app-flyio`), região, e selecionar Postgres e Redis.
   * **Importante**: Quando perguntar "Deploy now?", responda **No**.
   * O `flyctl launch` pode gerar um `fly.toml`. Verifique e ajuste-o conforme o `fly.toml` deste projeto (que já está configurado para usar o `Dockerfile` e outras boas práticas).

4. **Configurar Secrets Essenciais**:
   Substitua `seu-app-flyio` pelo nome real da sua aplicação no Fly.io.

   ```bash
   # Gere uma nova chave com: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   flyctl secrets set DJANGO_SECRET_KEY="sua_nova_chave_secreta_aqui" --app seu-app-flyio
   flyctl secrets set EXTERNAL_PROVIDER_API_URL="http://seu_provedor_externo/api/graphql" --app seu-app-flyio
   flyctl secrets set EXTERNAL_PROVIDER_BASE_URL="http://seu_provedor_externo/" --app seu-app-flyio
   flyctl secrets set DJANGO_ALLOWED_HOSTS="seu-app-flyio.fly.dev" --app seu-app-flyio
   flyctl secrets set DJANGO_DEBUG="False" --app seu-app-flyio
   # DATABASE_URL e REDIS_URL são geralmente configurados automaticamente pelo flyctl launch ao criar os serviços.
   ```

5. **Deploy Final**:

   ```bash
   flyctl deploy --app seu-app-flyio
   ```

6. **Criar Superusuário (após o primeiro deploy bem-sucedido)**:

   ```bash
   flyctl ssh console --app seu-app-flyio
   # Dentro do console SSH:
   source /opt/venv/bin/activate
   python manage.py createsuperuser
   exit
   ```

### Outras Plataformas (Configuração Anterior/Exemplos)

#### Railway

```bash
npm install -g @railway/cli
railway login
railway up
```

#### Vercel

```bash
npm install -g vercel
vercel --prod
```

#### Heroku

```bash
# heroku create seu-app-heroku
# git push heroku main
```

## ⚙️ Variáveis de Ambiente (para Fly.io e .env local)

As variáveis de ambiente são gerenciadas como "Secrets" no Fly.io.

### Obrigatórias

* `DJANGO_SECRET_KEY`: Chave secreta Django.
* `DATABASE_URL`: URL de conexão do banco de dados PostgreSQL (configurado automaticamente pelo Fly.io).
* `EXTERNAL_PROVIDER_API_URL`: URL da API GraphQL do provedor externo.
* `EXTERNAL_PROVIDER_BASE_URL`: URL base para imagens do provedor externo.

### Opcionais (com padrões no `settings.py` ou configuráveis via Secrets)

* `DJANGO_DEBUG`: Modo debug (padrão: `False` em produção via secret).
* `DJANGO_ALLOWED_HOSTS`: Hosts permitidos (ex: `seu-app-flyio.fly.dev` via secret).
* `REDIS_URL`: URL de conexão do Redis (configurado automaticamente pelo Fly.io se o serviço for adicionado).
* `RATE_LIMIT_PER_MINUTE`: Limite de requisições (padrão no código: 100).
* `EXTERNAL_PROVIDER_TIMEOUT`: Timeout para requisições ao provedor externo (padrão no código, se houver, ou pode ser adicionado).

## 🗂️ Endpoints REST

Todos os endpoints estão sob `/api/v1/`:

```text
GET    /api/v1/status/                                 # Status do serviço
GET    /api/v1/content-providers/list/                 # Lista de provedores
GET    /api/v1/content-discovery/search/               # Busca conteúdo
GET    /api/v1/content-discovery/filters/              # Filtros disponíveis
GET    /api/v1/content/item/<provider>/<id>/detail/    # Detalhes do conteúdo
GET    /api/v1/content/item/<provider>/<id>/chapter/<chapter>/pages/  # Páginas do capítulo
POST   /api/v1/image-proxy/                            # Proxy de imagens
```

## 🛠 Troubleshooting

### Erro: "No module named 'backend'" ou similar ao rodar `manage.py`

```bash
# Certifique-se de que seu ambiente virtual Python está ativado.
# Se estiver usando Docker, o ambiente virtual é ativado no Dockerfile.
# Para o console do Fly.io:
source /opt/venv/bin/activate
```

### Erro: Database connection

```bash
# No Fly.io, DATABASE_URL é injetado como um secret.
# Localmente, defina DATABASE_URL no seu arquivo .env (ex: sqlite:///./db.sqlite3 ou postgres://...)
```

### Erro: CORS / CSRF

```bash
# Verifique DJANGO_ALLOWED_HOSTS e CSRF_TRUSTED_ORIGINS no settings.py.
# Para o Fly.io, CSRF_TRUSTED_ORIGINS é configurado para usar o seu DJANGO_ALLOWED_HOSTS (ex: https://seu-app-flyio.fly.dev).
```

## 📚 Dependências Principais

* Django 5.2.3
* djangorestframework
* django-cors-headers
* django-ratelimit
* gunicorn
* psycopg2-binary
* python-decouple / python-dotenv
* redis
* requests
* whitenoise
* dj-database-url

---

> Para mais detalhes, consulte a pasta `Docs/` e os arquivos de configuração do projeto.
