#!/bin/bash
echo "--- Iniciando build_files_gateway.sh ---"
echo "Instalando dependências Python..."
pip install -r requirements.txt
echo "Coletando arquivos estáticos Django..."
python manage.py collectstatic --noinput
echo "Aplicando migrações Django..."
python manage.py migrate --noinput
echo "--- build_files_gateway.sh concluído ---"
