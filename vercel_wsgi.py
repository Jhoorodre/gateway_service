# vercel_wsgi.py - Handler para Vercel
import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Importar aplicação Django
from backend.wsgi import application

# Handler para Vercel
def handler(request, context):
    return application(request, context)
