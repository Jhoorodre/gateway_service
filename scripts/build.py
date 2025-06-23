#!/usr/bin/env python
"""
Build script for Vercel deployment - Versão Otimizada
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

def run_command(command, description, ignore_errors=False):
    """Run a shell command and handle errors"""
    print(f"BUILD_STEP: {description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0 and not ignore_errors:
        print(f"ERROR: {description} failed")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        if not ignore_errors:
            sys.exit(1)
    else:
        print(f"SUCCESS: {description}")
        if result.stdout:
            print(result.stdout)
    
    return result.returncode == 0

def main():
    print("--- Iniciando build script otimizado para Vercel ---")
    
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    os.environ['VERCEL'] = '1'
    
    # Create multiple possible staticfiles directories
    static_dirs = [
        '/tmp/staticfiles',
        'staticfiles',
        './staticfiles'
    ]
    
    for static_dir in static_dirs:
        try:
            os.makedirs(static_dir, exist_ok=True)
            print(f"Criado diretório: {static_dir}")
        except (OSError, PermissionError) as e:
            print(f"Não foi possível criar {static_dir}: {e}")
    
    # Try to collect static files with different approaches
    static_commands = [
        "python manage.py collectstatic --noinput --clear --verbosity=0",
        "python manage.py collectstatic --noinput --verbosity=0",
        "python manage.py collectstatic --noinput"
    ]
    
    static_collected = False
    for cmd in static_commands:
        if run_command(cmd, f"Coletando arquivos estáticos: {cmd}", ignore_errors=True):
            static_collected = True
            break
    
    if not static_collected:
        print("WARNING: Não foi possível coletar arquivos estáticos, mas continuando...")
    
    # Run migrations
    migration_commands = [
        "python manage.py migrate --noinput --verbosity=0",
        "python manage.py migrate --noinput"
    ]
    
    migration_success = False
    for cmd in migration_commands:
        if run_command(cmd, f"Executando migrações: {cmd}", ignore_errors=True):
            migration_success = True
            break
    
    if not migration_success:
        print("WARNING: Não foi possível executar migrações, mas continuando...")
    
    # List directory contents for debugging
    run_command("ls -la", "Listando conteúdo do diretório raiz", ignore_errors=True)
    run_command("ls -la /tmp/ | grep static || echo 'Nenhum diretório static em /tmp'", "Verificando /tmp", ignore_errors=True)
    run_command("find . -name 'staticfiles' -type d 2>/dev/null || echo 'Nenhum diretório staticfiles encontrado'", "Procurando staticfiles", ignore_errors=True)
    
    # Test Django setup
    run_command("python -c 'import django; django.setup(); print(\"Django setup OK\")'", "Testando setup do Django", ignore_errors=True)
    
    print("--- Build script concluído ---")

if __name__ == "__main__":
    main()
