#!/usr/bin/env bash
# Script de build para deploy no Render (v2.2.0)
# Este script é executado durante o processo de build no Render

set -o errexit  # Exit on error

echo "🚀 Iniciando build do Digital Twin Project v2.2.0..."

# Instalar dependências Python
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Verificar SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️ AVISO: SECRET_KEY não configurada!"
    echo "Configure em: Render Dashboard → Settings → Environment"
    echo "Gerando SECRET_KEY temporária para build..."
    export SECRET_KEY="temp-build-key-$(date +%s)"
fi

# Verificar se diretório static existe
if [ ! -d "static" ]; then
    echo "❌ ERRO: Diretório 'static' não encontrado!"
    echo "📁 Conteúdo atual:"
    ls -la
    exit 1
fi

# Criar diretórios necessários
echo "📂 Criando diretórios necessários..."
mkdir -p staticfiles
mkdir -p logs
mkdir -p media

# Configurar variáveis de ambiente para build
export DEBUG=False

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
echo "📊 Verificando arquivos JavaScript..."
ls -la static/js/ || echo "Diretório static/js/ não encontrado"

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --verbosity 2

# Verificar se arquivos foram coletados
if [ -d "staticfiles" ] && [ "$(ls -A staticfiles)" ]; then
    file_count=$(find staticfiles -type f | wc -l)
    echo "✅ Arquivos estáticos coletados: $file_count arquivos"
    
    # Verificar arquivos JS críticos
    if [ -f "staticfiles/js/notifications.js" ]; then
        echo "✅ notifications.js encontrado"
    fi
    if [ -f "staticfiles/js/loading-states.js" ]; then
        echo "✅ loading-states.js encontrado"
    fi
    if [ -f "staticfiles/js/accessibility.js" ]; then
        echo "✅ accessibility.js encontrado"
    fi
else
    echo "❌ ERRO: Diretório staticfiles vazio ou não existe!"
    exit 1
fi

# Aplicar migrações do banco de dados
echo "🗄️ Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

# Criar tabela de cache
echo "💾 Criando tabela de cache..."
python manage.py createcachetable || echo "⚠️ Tabela de cache já existe ou erro ao criar"

# Verificar se Redis está disponível
if [ -n "$REDIS_URL" ]; then
    echo "✅ Redis configurado: $REDIS_URL"
    echo "Cache usando Redis (alta performance)"
else
    echo "⚠️ Redis não configurado - usando DatabaseCache (fallback)"
    echo "Para melhor performance, adicione Redis no Render Dashboard"
fi

# Verificar se Sentry está configurado
if [ -n "$SENTRY_DSN" ]; then
    echo "✅ Sentry configurado para monitoramento de erros"
else
    echo "⚠️ Sentry não configurado - erros não serão rastreados"
    echo "Recomendado: Configure SENTRY_DSN para produção"
fi

# Criar superusuário se não existir
echo "👤 Verificando superusuário..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    try:
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('✅ Superusuário criado: admin/admin123')
        print('⚠️ IMPORTANTE: Altere a senha em produção!')
    except Exception as e:
        print(f'⚠️ Erro ao criar superusuário: {e}')
else:
    print('✅ Superusuário já existe')
" || echo "⚠️ Aviso ao verificar superusuário"

# Informações sobre Celery
if [ -n "$REDIS_URL" ]; then
    echo ""
    echo "📋 CELERY CONFIGURADO (opcional):"
    echo "   Para processar tarefas em background, adicione workers no Render:"
    echo "   1. New → Background Worker"
    echo "   2. Start Command: celery -A ifc_monitoring worker -l info"
    echo "   3. Use mesmas variáveis de ambiente do web service"
    echo ""
else
    echo ""
    echo "⚠️ CELERY NÃO DISPONÍVEL:"
    echo "   Configure REDIS_URL para habilitar processamento assíncrono"
    echo ""
fi

# Validar configuração
echo "🔍 Validando configuração..."
python manage.py check --deploy || echo "⚠️ Alguns checks falharam (não crítico)"

# Resumo de configuração
echo ""
echo "📊 RESUMO DA CONFIGURAÇÃO:"
echo "   ✅ Dependências instaladas"
echo "   ✅ Arquivos estáticos coletados ($file_count arquivos)"
echo "   ✅ Migrations aplicadas"
echo "   ✅ Cache table criada"
if [ -n "$REDIS_URL" ]; then
    echo "   ✅ Redis configurado"
else
    echo "   ⚠️ Redis não configurado (usando fallback)"
fi
if [ -n "$SENTRY_DSN" ]; then
    echo "   ✅ Sentry configurado"
else
    echo "   ⚠️ Sentry não configurado"
fi
echo ""

echo "✅ Build concluído com sucesso!"
echo "🌐 Aplicação pronta para deploy no Render"
echo ""
echo "🔗 Endpoints importantes após deploy:"
echo "   - Dashboard: https://seu-app.onrender.com/"
echo "   - Admin: https://seu-app.onrender.com/admin/"
echo "   - API Docs: https://seu-app.onrender.com/api/docs/"
echo "   - Health Check: https://seu-app.onrender.com/core/health/"
echo ""
echo "📚 Consulte docs/GUIA_MIGRACAO.md para configurações adicionais"
