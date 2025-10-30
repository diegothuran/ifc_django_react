# Dockerfile para produção do IFC Digital Twin
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Criar diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput || true

# Criar script de inicialização
RUN echo '#!/bin/bash\n\
python manage.py migrate --noinput\n\
python manage.py createcachetable\n\
exec "$@"' > /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Expor porta
EXPOSE 8000

# Definir entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Comando padrão
CMD ["gunicorn", "ifc_monitoring.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]

