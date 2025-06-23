#!/usr/bin/env python
"""
Build script for Vercel deployment
"""
import os
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"BUILD_STEP: {description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: {description} failed")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    else:
        print(f"SUCCESS: {description}")
        if result.stdout:
            print(result.stdout)

def main():
    print("--- Iniciando build script para Vercel ---")
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    
    # Create staticfiles directory
    run_command("mkdir -p staticfiles", "Criando diretório de arquivos estáticos")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput --clear", "Coletando arquivos estáticos")
    
    # Run migrations
    run_command("python manage.py migrate --noinput", "Executando migrações do banco de dados")
    
    # List staticfiles contents
    run_command("ls -la staticfiles/ || echo 'Diretório staticfiles vazio'", "Listando conteúdo do diretório staticfiles")
    
    print("--- Build script concluído com sucesso ---")

if __name__ == "__main__":
    main()
