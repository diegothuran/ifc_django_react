#!/usr/bin/env bash
# Script de inicialização simples para o Render
# Este script é executado quando o serviço web inicia no Render

set -o errexit  # Exit on error

echo "🚀 Iniciando Digital Twin Project no Render..."

# Verificar se estamos em produção
if [ "$RENDER" = "true" ]; then
    echo "🌐 Ambiente de produção detectado (Render)"
else
    echo "💻 Ambiente de desenvolvimento detectado"
fi

# Iniciar o servidor Gunicorn
echo "🌐 Iniciando servidor Gunicorn..."

# Configurações do Gunicorn otimizadas para Render
# --bind 0.0.0.0:$PORT - Bind no port do Render
# --workers - Número de workers (WEB_CONCURRENCY ou 4)
# --threads - Threads por worker
# --timeout - Timeout para requisições longas (útil para processamento IFC)
# --access-logfile - Log de acesso
# --error-logfile - Log de erros
# --log-level - Nível de log

exec gunicorn ifc_monitoring.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers ${WEB_CONCURRENCY:-4} \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

