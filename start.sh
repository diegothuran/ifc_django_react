#!/bin/bash
# Script de inicialização para o Render
# Este script garante que os dados iniciais sejam criados apenas uma vez

echo "🚀 Iniciando aplicação Digital Twin Project..."

# Verificar se os dados iniciais já foram criados
echo "🔍 Verificando se dados iniciais já existem..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()

# Verificar se superusuário existe
if not User.objects.filter(is_superuser=True).exists():
    print('👤 Criando superusuário...')
    User.objects.create_superuser('admin', 'admin@digitaltwin.com', 'admin123')
    print('✅ Superusuário criado: admin/admin123')
else:
    print('👤 Superusuário já existe')

# Verificar se planta existe
try:
    from plant_viewer.models import BuildingPlan
    if not BuildingPlan.objects.exists():
        print('🏭 Criando planta de exemplo...')
        plant = BuildingPlan.objects.create(
            name='Planta Industrial Exemplo',
            description='Planta de demonstração para o Digital Twin Project',
            is_active=True
        )
        print(f'✅ Planta criada: {plant.name}')
    else:
        print('🏭 Planta já existe')
except Exception as e:
    print(f'⚠️ Erro ao verificar/criar planta: {e}')

# Verificar se sensores existem
try:
    from sensor_management.models import Sensor
    if not Sensor.objects.exists():
        print('📡 Criando sensores de exemplo...')
        sensors_data = [
            {'name': 'Sensor Linha 1 - Contador', 'ip_address': '192.168.1.100', 'port': 80, 'sensor_type': 'counter', 'location_id': 'IFC_001', 'description': 'Sensor de contagem na linha de produção 1', 'collection_interval': 60, 'timeout': 10},
            {'name': 'Sensor Temperatura - Forno', 'ip_address': '192.168.1.101', 'port': 80, 'sensor_type': 'temperature', 'location_id': 'IFC_002', 'description': 'Sensor de temperatura no forno industrial', 'collection_interval': 30, 'timeout': 10},
            {'name': 'Sensor Pressão - Compressor', 'ip_address': '192.168.1.102', 'port': 80, 'sensor_type': 'pressure', 'location_id': 'IFC_003', 'description': 'Sensor de pressão no compressor principal', 'collection_interval': 45, 'timeout': 10},
            {'name': 'Sensor Vibração - Motor', 'ip_address': '192.168.1.103', 'port': 80, 'sensor_type': 'vibration', 'location_id': 'IFC_004', 'description': 'Sensor de vibração no motor principal', 'collection_interval': 20, 'timeout': 10},
            {'name': 'Sensor Fluxo - Tubulação', 'ip_address': '192.168.1.104', 'port': 80, 'sensor_type': 'flow', 'location_id': 'IFC_005', 'description': 'Sensor de fluxo na tubulação principal', 'collection_interval': 60, 'timeout': 10},
            {'name': 'Sensor Nível - Tanque', 'ip_address': '192.168.1.105', 'port': 80, 'sensor_type': 'level', 'location_id': 'IFC_006', 'description': 'Sensor de nível no tanque de armazenamento', 'collection_interval': 90, 'timeout': 10}
        ]
        
        for sensor_data in sensors_data:
            sensor = Sensor.objects.create(**sensor_data)
            print(f'📡 Sensor criado: {sensor.name}')
        
        print('✅ Sensores de exemplo criados com sucesso!')
    else:
        print('📡 Sensores já existem')
except Exception as e:
    print(f'⚠️ Erro ao verificar/criar sensores: {e}')

print('✅ Verificação/criação de dados iniciais concluída!')
"

# Iniciar o servidor Gunicorn
echo "🌐 Iniciando servidor Gunicorn..."
exec gunicorn ifc_monitoring.wsgi:application --log-file -
