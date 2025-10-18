#!/usr/bin/env bash
# Script de build para deploy no Render
# Este script é executado durante o processo de build no Render

set -o errexit  # Exit on error

echo "🚀 Iniciando build do Digital Twin Project..."

# Instalar dependências Python
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Verificar se diretório static existe
if [ ! -d "static" ]; then
    echo "❌ ERRO: Diretório 'static' não encontrado!"
    echo "📁 Conteúdo atual:"
    ls -la
    exit 1
fi

# Criar diretório staticfiles
echo "📂 Criando diretório de arquivos estáticos..."
mkdir -p staticfiles

# Configurar variáveis de ambiente para produção
export DEBUG=False
export SECRET_KEY="temp-key-for-build"

# Coletar arquivos estáticos com debug
echo "📁 Coletando arquivos estáticos..."
echo "📊 Conteúdo do diretório static:"
ls -la static/
echo "📊 Arquivos JS:"
ls -la static/js/
echo "📊 Arquivos CSS:"
ls -la static/css/

# Coletar arquivos estáticos (sem --clear para evitar problemas com manifest)
python manage.py collectstatic --noinput --verbosity 2

# Verificar se arquivos foram coletados
if [ -d "staticfiles" ] && [ "$(ls -A staticfiles)" ]; then
    file_count=$(find staticfiles -type f | wc -l)
    echo "✅ Arquivos estáticos coletados: $file_count arquivos"
    echo "📊 Conteúdo do diretório staticfiles:"
    ls -la staticfiles/
else
    echo "❌ ERRO: Diretório staticfiles vazio ou não existe!"
    echo "📁 Tentando novamente..."
    python manage.py collectstatic --noinput --verbosity 2
    if [ -d "staticfiles" ] && [ "$(ls -A staticfiles)" ]; then
        echo "✅ Segunda tentativa: Arquivos coletados!"
    else
        echo "❌ ERRO CRÍTICO: Falha ao coletar arquivos estáticos!"
        exit 1
    fi
fi

# Aplicar migrações do banco de dados
echo "🗄️ Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

# Criar tabela de cache no PostgreSQL (para armazenar cache de metadados IFC)
echo "💾 Criando tabela de cache no banco de dados..."
python manage.py createcachetable

# Criar superusuário se não existir (opcional)
echo "👤 Verificando se superusuário existe..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superusuário criado: admin/admin123')
else:
    print('✅ Superusuário já existe')
"

# Criar dados de exemplo se em desenvolvimento
if [ "$DEBUG" = "True" ]; then
    echo "🎭 Criando dados de exemplo..."
    python manage.py shell -c "
from plant_viewer.models import BuildingPlan
from sensor_management.models import Sensor

# Criar planta de exemplo se não existir
if not BuildingPlan.objects.exists():
    plant = BuildingPlan.objects.create(
        name='Planta Industrial Exemplo',
        description='Planta de demonstração para o Digital Twin Project',
        is_active=True
    )
    print(f'Planta de exemplo criada: {plant.name}')

# Criar sensores de exemplo se não existirem
if not Sensor.objects.exists():
    sensors_data = [
        {'name': 'Sensor Linha 1', 'ip_address': '192.168.1.100', 'sensor_type': 'counter', 'location_id': 'IFC_001'},
        {'name': 'Sensor Temperatura', 'ip_address': '192.168.1.101', 'sensor_type': 'temperature', 'location_id': 'IFC_002'},
        {'name': 'Sensor Pressão', 'ip_address': '192.168.1.102', 'sensor_type': 'pressure', 'location_id': 'IFC_003'},
        {'name': 'Sensor Vibração', 'ip_address': '192.168.1.103', 'sensor_type': 'vibration', 'location_id': 'IFC_004'},
        {'name': 'Sensor Fluxo', 'ip_address': '192.168.1.104', 'sensor_type': 'flow', 'location_id': 'IFC_005'},
    ]
    
    for sensor_data in sensors_data:
        sensor = Sensor.objects.create(**sensor_data)
        print(f'Sensor criado: {sensor.name}')
    
    print('Sensores de exemplo criados com sucesso!')
"
fi

echo "✅ Build concluído com sucesso!"
echo "🌐 Aplicação pronta para deploy no Render"
