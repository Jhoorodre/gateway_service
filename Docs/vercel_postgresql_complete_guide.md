# 🚀 Guia Completo: Configurando PostgreSQL do Vercel com Django

**Para iniciantes e desenvolvedores que querem uma configuração 100% funcional**

Este guia te levará passo a passo para configurar um banco de dados PostgreSQL no Vercel e conectá-lo ao seu projeto Django. Cada etapa é explicada em detalhes com exemplos práticos.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

- ✅ Projeto Django funcionando localmente
- ✅ Conta no GitHub com seu código
- ✅ Conta no Vercel (gratuita)
- ✅ Python e pip instalados

---

## 🏗️ Parte 1: Preparando o Projeto Django

### 1.1 Instale as Dependências Necessárias

No terminal, dentro da pasta do seu projeto Django:

```bash
pip install psycopg2-binary dj-database-url python-decouple
```

### 1.2 Atualize o requirements.txt

Crie ou atualize o arquivo `requirements.txt` na raiz do projeto:

```txt
Django>=4.0
psycopg2-binary
dj-database-url
python-decouple
gunicorn
whitenoise
```

### 1.3 Configure o settings.py

Substitua as configurações do seu `settings.py`:

```python
import os
import dj_database_url
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='sua-chave-secreta-local-aqui')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.vercel.app']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Seus apps aqui
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para arquivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'seu_projeto.urls'  # Substitua pelo nome do seu projeto

# Database Configuration
# Configuração para produção (Vercel) e desenvolvimento local
if config('DATABASE_URL', default=None):
    # Produção - usando PostgreSQL do Vercel
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Desenvolvimento local - usando SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configurações de segurança para produção
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

### 1.4 Crie o arquivo .env (para desenvolvimento local)

Na raiz do projeto, crie um arquivo `.env`:

```env
SECRET_KEY=sua-chave-secreta-muito-complexa-aqui
DEBUG=True
```

### 1.5 Crie o arquivo vercel.json

Na raiz do projeto, crie `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "seu_projeto/wsgi.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "15mb", "runtime": "python3.9" }
    },
    {
      "src": "build_files.sh",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "staticfiles_build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "seu_projeto/wsgi.py"
    }
  ]
}
```

**⚠️ Importante**: Substitua `seu_projeto` pelo nome real da sua pasta de projeto!

### 1.6 Crie o arquivo build_files.sh

Na raiz do projeto:

```bash
#!/bin/bash

# Instala as dependências
pip install -r requirements.txt

# Coleta arquivos estáticos
python manage.py collectstatic --noinput

# Executa as migrações
python manage.py migrate --noinput
```

Torne o arquivo executável:

```bash
chmod +x build_files.sh
```

---

## 🌐 Parte 2: Configurando no Vercel

### 2.1 Fazendo Deploy Inicial

1. **Acesse**: [vercel.com](https://vercel.com)
2. **Login**: Use sua conta GitHub
3. **Import Project**: Clique em "New Project"
4. **Selecione seu repositório**: Escolha o repo do seu Django
5. **Configure o projeto**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (raiz)
   - **Build Command**: `./build_files.sh`
   - **Install Command**: `pip install -r requirements.txt`
6. **Deploy**: Clique em "Deploy"

### 2.2 Criando o Banco PostgreSQL

Após o deploy inicial:

1. **Acesse seu projeto** no dashboard do Vercel
2. **Vá para Storage**: Clique na aba "Storage"
3. **Create Database**: Clique em "Create"
4. **Selecione PostgreSQL**: Escolha "Postgres"
5. **Configure**:
   - **Database Name**: `meu-projeto-db` (escolha um nome)
   - **Region**: Escolha a região mais próxima (ex: São Paulo)
6. **Create**: Confirme a criação

### 2.3 Obtendo as Credenciais

Após criar o banco:

1. **Clique no banco criado** na lista
2. **Vá para .env.local**: Encontre a seção de credenciais
3. **Copie a DATABASE_URL**: Algo como:
   ```
   postgresql://usuario:senha@host:5432/database
   ```

### 2.4 Configurando Variáveis de Ambiente

1. **Settings**: Vá para "Settings" do seu projeto
2. **Environment Variables**: Clique na seção
3. **Adicione as variáveis**:

   | Nome | Valor | Ambientes |
   |------|-------|-----------|
   | `DATABASE_URL` | Cole a URL copiada | Production, Preview |
   | `SECRET_KEY` | Gere uma chave secreta forte | Production, Preview |
   | `DEBUG` | `False` | Production, Preview |

**🔐 Como gerar SECRET_KEY**:
```python
# Execute no terminal Python:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 🔄 Parte 3: Executando Migrações

### 3.1 Opção 1: Via Build Script (Recomendado)

As migrações já estão configuradas no `build_files.sh`. A cada deploy, elas executarão automaticamente.

### 3.2 Opção 2: Via Vercel CLI (Manual)

Instale a CLI do Vercel:

```bash
npm install -g vercel
```

Execute migrações:

```bash
vercel login
vercel env pull .env.production
python manage.py migrate --settings=seu_projeto.settings
```

### 3.3 Opção 3: Função Serverless para Migrações

Crie `api/migrate.py`:

```python
from django.core.management import execute_from_command_line
import os
import sys

def handler(request):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seu_projeto.settings')
    
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        return {
            'statusCode': 200,
            'body': 'Migrações executadas com sucesso!'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Erro: {str(e)}'
        }
```

Acesse: `https://seu-projeto.vercel.app/api/migrate`

---

## 🧪 Parte 4: Testando a Configuração

### 4.1 Verificando Conexão Local

```bash
# Teste local
python manage.py check --database default
python manage.py migrate
python manage.py runserver
```

### 4.2 Verificando Conexão Produção

1. **Acesse seu site**: `https://seu-projeto.vercel.app`
2. **Verifique logs**: No Vercel dashboard > Functions
3. **Teste admin**: `https://seu-projeto.vercel.app/admin`

### 4.3 Criando Superuser em Produção

Crie `api/create_superuser.py`:

```python
from django.contrib.auth.models import User
import os

def handler(request):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seu_projeto.settings')
    
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@email.com', 'senha123')
            return {'statusCode': 200, 'body': 'Superuser criado!'}
        else:
            return {'statusCode': 200, 'body': 'Superuser já existe!'}
    except Exception as e:
        return {'statusCode': 500, 'body': f'Erro: {str(e)}'}
```

---

## 🔧 Parte 5: Troubleshooting (Resolução de Problemas)

### Erro: "Application Error"

**Solução**:
1. Verifique os logs no Vercel dashboard
2. Confirme se `DJANGO_SETTINGS_MODULE` está correto
3. Verifique se todas variáveis de ambiente estão definidas

### Erro: "Database Connection Failed" 

**Solução**:
1. Confirme se `DATABASE_URL` está correta
2. Verifique se o banco PostgreSQL está ativo
3. Teste conexão local com as credenciais

### Erro: "Static Files Not Found"

**Solução**:
1. Verifique se `whitenoise` está instalado
2. Confirme se `collectstatic` executou no build
3. Verifique configurações `STATIC_*` no settings

### Erro: "Table doesn't exist"

**Solução**:
1. Execute migrações manualmente
2. Verifique se `migrate` está no build script
3. Confirme se models estão corretos

---

## 📈 Parte 6: Otimizações e Boas Práticas

### Configurações de Performance

```python
# Adicione no settings.py para produção
if not DEBUG:
    # Cache de sessões
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    
    # Configurações de conexão do banco
    DATABASES['default']['OPTIONS'] = {
        'MAX_CONNS': 20,
        'OPTIONS': {
            'MAX_CONNS': 20
        }
    }
    
    # Configurações de segurança
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
```

### Monitoramento

```python
# Adicione para logs detalhados
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## ✅ Checklist Final

Antes de considerar concluído:

- [ ] Projeto Django funciona localmente
- [ ] `requirements.txt` atualizado com todas dependências
- [ ] `vercel.json` configurado corretamente
- [ ] `build_files.sh` criado e executável
- [ ] Variáveis de ambiente configuradas no Vercel
- [ ] Banco PostgreSQL criado e conectado
- [ ] Migrações executadas com sucesso
- [ ] Site acessível em produção
- [ ] Admin Django funcionando
- [ ] Arquivos estáticos carregando

---

## 🆘 Precisa de Ajuda?

**Documentações Oficiais**:
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Vercel Python](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel PostgreSQL](https://vercel.com/docs/storage/vercel-postgres)

**Comunidades**:
- [Django Brasil (Telegram)](https://t.me/djangobrasil)
- [Stack Overflow Django](https://stackoverflow.com/questions/tagged/django)

---

🎉 **Parabéns!** Seu projeto Django está rodando com PostgreSQL no Vercel!

> **Dica Pro**: Sempre teste localmente antes de fazer deploy, e mantenha backups regulares do seu banco de dados.