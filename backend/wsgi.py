"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import traceback  # Importamos a biblioteca de rastreamento
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    # Tentamos inicializar a aplicação normalmente
    application = get_wsgi_application()

except Exception:
    # SE QUALQUER ERRO OCORRER na inicialização, nós o capturamos.
    # Isto é para depuração e deve ser removido depois.
    
    # Imprime o traceback completo para os logs da Vercel
    print("--- ERRO CRÍTICO NA INICIALIZAÇÃO DO DJANGO ---", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    print("---------------------------------------------", file=sys.stderr)
    
    # É importante que o processo ainda falhe para que a Vercel não pense que deu tudo certo.
    # Mas agora, o erro real estará visível nos logs.
    raise
