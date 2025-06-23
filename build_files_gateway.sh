#!/bin/bash

# Sai imediatamente se um comando falhar
set -e

echo "--- Iniciando build_files_gateway.sh ---"

echo "BUILD_STEP: Instalando dependências..."
pip install -r requirements.txt

echo "BUILD_STEP: Criando diretório de arquivos estáticos..."
mkdir -p staticfiles

echo "BUILD_STEP: Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "BUILD_STEP: Executando migrações do banco de dados..."
python manage.py migrate --noinput

echo "BUILD_STEP: Listando conteúdo do diretório staticfiles..."
ls -la staticfiles/ || echo "Diretório staticfiles vazio ou não existe"

echo "--- build_files_gateway.sh concluído com sucesso ---"
