# Gateway Service - Setup e Deploy

## 🚀 Setup Local

### 1. Pré-requisitos
```bash
# Python 3.13+
python --version

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configuração
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env
```

### 3. Configurar Django
```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Criar superuser (opcional)
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic
```

### 4. Executar
```bash
# Desenvolvimento
python manage.py runserver 0.0.0.0:8000

# Produção local
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

## 📦 Deploy

### Railway (Recomendado)
```bash
# Instalar CLI
npm install -g @railway/cli

# Login e deploy
railway login
railway new cubari-proxy-backend
railway up
```

### Vercel
```bash
# Instalar CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Heroku
```bash
# Criar app
heroku create cubari-proxy-backend

# Deploy
git push heroku main
```

## ⚙️ Variáveis de Ambiente

### Obrigatórias
- `DJANGO_SECRET_KEY`: Chave secreta Django
- `SUWAYOMI_API_URL`: URL da API GraphQL
- `SUWAYOMI_BASE_URL`: URL base para imagens

### Opcionais
- `DJANGO_DEBUG`: Modo debug (padrão: False)
- `RATE_LIMIT_PER_MINUTE`: Rate limit (padrão: 60)
- `SUWAYOMI_TIMEOUT`: Timeout requisições (padrão: 30s)

## 🔗 Endpoints

```
GET  /api/v1/status/                           # Status do serviço
GET  /api/v1/content-providers/list/           # Lista provedores
GET  /api/v1/content-discovery/search/         # Busca conteúdo
GET  /api/v1/content/item/{provider}/{id}/detail/  # Detalhes manga
GET  /api/v1/content/item/{provider}/{id}/chapter/{chapter}/pages/  # Páginas
POST /api/v1/image-proxy/                      # Proxy imagens
```

## 🛠 Troubleshooting

### Erro: "No module named 'backend'"
```bash
# Verificar DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE=backend.settings
```

### Erro: Database connection
```bash
# Verificar DATABASE_URL ou usar SQLite
unset DATABASE_URL
```

### Erro: CORS
```bash
# Verificar ALLOWED_HOSTS no .env
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com
```
