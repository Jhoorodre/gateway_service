#!/bin/bash

# Sai imediatamente se um comando falhar
set -e

echo "--- Iniciando build_files_gateway.sh ---"

echo "BUILD_STEP: Instalando dependências..."
pip install -r requirements.txt

echo "BUILD_STEP: Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "BUILD_STEP: Rodando migrações do banco de dados..."
python manage.py migrate --noinput

echo "--- build_files_gateway.sh concluído com sucesso ---"
