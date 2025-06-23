"""
Django settings for backend project.
Optimized for Vercel deployment.
"""

import os
import sys  # Adicionado sys
from pathlib import Path
from decouple import config

# Import condicional do dj_database_url
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('DJANGO_SECRET_KEY', default='uma_chave_secreta_local_padrao_deve_ser_forte')

# Forçar DEBUG = True se estivermos usando o runserver localmente
# Isso simplifica a configuração de ALLOWED_HOSTS para desenvolvimento.
# A variável de ambiente DJANGO_DEBUG ainda pode sobrescrever isso se definida explicitamente.
DEBUG_FOR_RUNSERVER = ('runserver' in sys.argv)
DEBUG = config('DJANGO_DEBUG', default=DEBUG_FOR_RUNSERVER, cast=bool)

# Hosts - Configuração específica para Vercel e desenvolvimento
if DEBUG:
    # Para desenvolvimento (incluindo runserver local), permitir hosts mais flexíveis.
    ALLOWED_HOSTS = ['*', '127.0.0.1', 'localhost']
else:
    # Para produção (DEBUG=False), usar a variável de ambiente DJANGO_ALLOWED_HOSTS.
    # O padrão é restrito a '.vercel.app' se a variável não estiver definida.
    allowed_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS')
    if allowed_hosts_env:
        ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]
    else:
        # Fallback para produção se DJANGO_ALLOWED_HOSTS não estiver definida.
        # Adicione o domínio de produção real aqui se não for apenas .vercel.app
        ALLOWED_HOSTS = [host.strip() for host in os.getenv('VERCEL_URL', '.vercel.app').split(',') if host.strip()]
        if not ALLOWED_HOSTS: # Último recurso
             ALLOWED_HOSTS = ['.vercel.app']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Adicionado
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database configuration
_raw_db_url = config('DATABASE_URL', default=None)
DATABASE_URL_FROM_ENV: str | None = None  # Inicializa com tipo explícito

if isinstance(_raw_db_url, str) and _raw_db_url.strip(): # Garante que é uma string não vazia
    DATABASE_URL_FROM_ENV = _raw_db_url
# Se _raw_db_url for None ou uma string vazia, DATABASE_URL_FROM_ENV permanece None.

# Verifica se dj_database_url foi importado com sucesso e DATABASE_URL_FROM_ENV é uma string válida
if DATABASE_URL_FROM_ENV is not None and dj_database_url is not None:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL_FROM_ENV,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # SQLite para desenvolvimento e fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Criação automática do diretório staticfiles se não existir
os.makedirs(STATIC_ROOT, exist_ok=True)

# WhiteNoise para servir arquivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

# External Provider URLs
EXTERNAL_PROVIDER_API_URL = config('EXTERNAL_PROVIDER_API_URL', default='https://seu-servidor-suwayomi.com/api/graphql')
EXTERNAL_PROVIDER_BASE_URL = config('EXTERNAL_PROVIDER_BASE_URL', default='https://seu-servidor-suwayomi.com')

# Logging para debug
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
}

# Rate Limiting
# Você pode ajustar este valor conforme necessário ou defini-lo através de variáveis de ambiente
RATE_LIMIT_PER_MINUTE = config('DJANGO_RATE_LIMIT_PER_MINUTE', default=100, cast=int)
