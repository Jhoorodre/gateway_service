# Etapa 1: Builder - Instala dependências e prepara o build
# Usar uma imagem base de Python leve e segura
FROM python:3.10-slim-bullseye as builder

# Define variáveis de ambiente para otimizar o build em Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instala as dependências Python em um ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia e instala as dependências de forma otimizada para cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Coleta todos os arquivos estáticos para um diretório que será servido pelo WhiteNoise
RUN python manage.py collectstatic --noinput


# Etapa 2: Runner - Cria a imagem final, mais leve
FROM python:3.10-slim-bullseye

WORKDIR /app

# Copia apenas o ambiente virtual com as dependências da etapa anterior
COPY --from=builder /opt/venv /opt/venv
# Copia apenas os arquivos da aplicação e os estáticos coletados
COPY --from=builder /app /app

# Ativa o ambiente virtual para o comando final
ENV PATH="/opt/venv/bin:$PATH"

# Expõe a porta que o Gunicorn irá escutar
EXPOSE 8000

# Comando final para iniciar o servidor Gunicorn em produção
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
