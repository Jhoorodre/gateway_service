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
cp .env.example .env

# Editar configurações
# (Edite DJANGO_SECRET_KEY, SUWAYOMI_API_URL, SUWAYOMI_BASE_URL, etc)
```

### 3. Banco de Dados e Django
```bash
# Aplicar migrations
python manage.py makemigrations
python manage.py migrate

# Criar superuser (opcional)
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### 4. Executar
```bash
# Desenvolvimento
python manage.py runserver 0.0.0.0:8000

# Produção local
# (Porta pode ser definida pela variável $PORT)
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

## 📦 Deploy

### Railway (Recomendado)
```bash
npm install -g @railway/cli
railway login
railway up
```

### Vercel
```bash
npm install -g vercel
vercel --prod
```

### Heroku
```bash
heroku create cubari-proxy-backend
git push heroku main
```

## ⚙️ Variáveis de Ambiente

### Obrigatórias
- `DJANGO_SECRET_KEY`: Chave secreta Django
- `SUWAYOMI_API_URL`: URL da API GraphQL
- `SUWAYOMI_BASE_URL`: URL base para imagens

### Opcionais
- `DJANGO_DEBUG`: Modo debug (padrão: False)
- `DJANGO_ALLOWED_HOSTS`: Hosts permitidos (padrão: localhost,127.0.0.1,.vercel.app)
- `RATE_LIMIT_PER_MINUTE`: Limite de requisições (padrão: 60)
- `SUWAYOMI_TIMEOUT`: Timeout das requisições (padrão: 30s)

## 🗂️ Endpoints REST

Todos os endpoints estão sob `/api/v1/`:

```
GET    /api/v1/status/                                 # Status do serviço
GET    /api/v1/content-providers/list/                 # Lista de provedores
GET    /api/v1/content-discovery/search/               # Busca conteúdo
GET    /api/v1/content-discovery/filters/              # Filtros disponíveis
GET    /api/v1/content/item/<provider>/<id>/detail/    # Detalhes do conteúdo
GET    /api/v1/content/item/<provider>/<id>/chapter/<chapter>/pages/  # Páginas do capítulo
POST   /api/v1/image-proxy/                            # Proxy de imagens
```

## 🛠 Troubleshooting

### Erro: "No module named 'backend'"
```bash
# Verifique a variável de ambiente
export DJANGO_SETTINGS_MODULE=backend.settings
```

### Erro: Database connection
```bash
# Verifique DATABASE_URL ou use SQLite
unset DATABASE_URL
```

### Erro: CORS
```bash
# Verifique DJANGO_ALLOWED_HOSTS no .env
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com
```

## 📚 Dependências Principais

- Django 5.2.3
- djangorestframework
- django-cors-headers
- django-ratelimit
- gunicorn
- psycopg2-binary
- python-dotenv / python-decouple
- redis
- requests
- whitenoise
- dj-database-url

---

> Para mais detalhes, consulte a pasta `Docs/` e os arquivos de configuração do projeto.
