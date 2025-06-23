"""
Django settings for backend project.
Optimized for Vercel deployment.
"""

import os
import sys
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

# Detectar se estamos no Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1'

# Forçar DEBUG = True se estivermos usando o runserver localmente
DEBUG_FOR_RUNSERVER = ('runserver' in sys.argv)
DEBUG = config('DJANGO_DEBUG', default=DEBUG_FOR_RUNSERVER and not IS_VERCEL, cast=bool)

# Hosts - Configuração específica para Vercel e desenvolvimento
if DEBUG and not IS_VERCEL:
    # Para desenvolvimento local
    ALLOWED_HOSTS = ['*', '127.0.0.1', 'localhost']
else:
    # Para produção (incluindo Vercel)
    allowed_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS')
    if allowed_hosts_env:
        ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]
    else:
        # Fallback para Vercel
        vercel_url = os.getenv('VERCEL_URL', '')
        if vercel_url:
            ALLOWED_HOSTS = [vercel_url, f"https://{vercel_url}", '.vercel.app']
        else:
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
    'django.contrib.sessions.middleware.SessionMiddleware',
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
DATABASE_URL_FROM_ENV: str | None = None

if isinstance(_raw_db_url, str) and _raw_db_url.strip():
    DATABASE_URL_FROM_ENV = _raw_db_url

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

# Configuração de STATIC_ROOT otimizada para Vercel
# No Vercel, o único local gravável é /tmp. O build.py criará este diretório.
STATIC_ROOT = '/tmp/staticfiles'

# WhiteNoise configuração otimizada
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configurações adicionais do WhiteNoise para Vercel
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']
WHITENOISE_MAX_AGE = 31536000  # 1 ano

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

# Logging otimizado para Vercel
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if IS_VERCEL else 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Rate Limiting
RATE_LIMIT_PER_MINUTE = config('DJANGO_RATE_LIMIT_PER_MINUTE', default=100, cast=int)

# Configurações de segurança para produção
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'