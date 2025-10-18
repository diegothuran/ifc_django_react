from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from plant_viewer.models import BuildingPlan
from sensor_management.models import Sensor, SensorData
from django.utils import timezone
import random


class Command(BaseCommand):
    """
    Comando para configurar dados iniciais do Digital Twin Project.
    
    Este comando cria:
    - Superusuário (se não existir)
    - Planta de exemplo
    - Sensores de demonstração
    - Dados de exemplo para os sensores
    
    Uso:
    python manage.py setup_initial_data [--force]
    
    Opções:
    --force: Força a recriação dos dados mesmo se já existirem
    """
    
    help = 'Configura dados iniciais para o Digital Twin Project'
    
    def add_arguments(self, parser):
        """Adiciona argumentos para o comando."""
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a recriação dos dados mesmo se já existirem'
        )
    
    def handle(self, *args, **options):
        """Função principal do comando."""
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Configurando dados iniciais do Digital Twin Project...')
        )
        
        # Criar superusuário
        self.create_superuser()
        
        # Criar planta de exemplo
        plant = self.create_example_plant(force)
        
        # Criar sensores de exemplo
        sensors = self.create_example_sensors(force)
        
        # Criar dados de exemplo
        if sensors:
            self.create_example_data(sensors, plant)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Dados iniciais configurados com sucesso!')
        )
        
        self.stdout.write(
            self.style.WARNING(
                '\n📋 Informações de acesso:\n'
                '• Admin: http://seu-dominio.com/admin/\n'
                '• Usuário: admin\n'
                '• Senha: admin123\n'
                '• Dashboard: http://seu-dominio.com/dashboard/'
            )
        )
    
    def create_superuser(self):
        """Cria superusuário se não existir."""
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@digitaltwin.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('👤 Superusuário criado: admin/admin123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('👤 Superusuário já existe')
            )
    
    def create_example_plant(self, force=False):
        """Cria planta de exemplo."""
        try:
            if not force and BuildingPlan.objects.exists():
                plant = BuildingPlan.objects.first()
                self.stdout.write(
                    self.style.WARNING(f'🏭 Planta já existe: {plant.name}')
                )
                return plant
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Erro ao verificar plantas existentes: {e}')
            )
            self.stdout.write(
                self.style.WARNING('🔄 Continuando com a criação de nova planta...')
            )
        
        if force:
            BuildingPlan.objects.all().delete()
        
        plant = BuildingPlan.objects.create(
            name='Planta Industrial Exemplo',
            description='Planta de demonstração para o Digital Twin Project. '
                       'Esta planta contém sensores de monitoramento distribuídos '
                       'por diferentes áreas para demonstrar as funcionalidades do sistema.',
            is_active=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'🏭 Planta criada: {plant.name}')
        )
        
        return plant
    
    def create_example_sensors(self, force=False):
        """Cria sensores de exemplo."""
        try:
            if not force and Sensor.objects.exists():
                sensors = list(Sensor.objects.all())
                self.stdout.write(
                    self.style.WARNING(f'📡 Sensores já existem: {len(sensors)} sensores')
                )
                return sensors
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Erro ao verificar sensores existentes: {e}')
            )
            self.stdout.write(
                self.style.WARNING('🔄 Continuando com a criação de novos sensores...')
            )
        
        if force:
            Sensor.objects.all().delete()
        
        sensors_data = [
            {
                'name': 'Sensor Linha 1 - Contador',
                'ip_address': '192.168.1.100',
                'port': 80,
                'sensor_type': 'counter',
                'location_id': 'IFC_001',
                'description': 'Sensor de contagem na linha de produção 1',
                'collection_interval': 60,
                'timeout': 10
            },
            {
                'name': 'Sensor Temperatura - Forno',
                'ip_address': '192.168.1.101',
                'port': 80,
                'sensor_type': 'temperature',
                'location_id': 'IFC_002',
                'description': 'Sensor de temperatura no forno industrial',
                'collection_interval': 30,
                'timeout': 10
            },
            {
                'name': 'Sensor Pressão - Compressor',
                'ip_address': '192.168.1.102',
                'port': 80,
                'sensor_type': 'pressure',
                'location_id': 'IFC_003',
                'description': 'Sensor de pressão no compressor principal',
                'collection_interval': 45,
                'timeout': 10
            },
            {
                'name': 'Sensor Vibração - Motor',
                'ip_address': '192.168.1.103',
                'port': 80,
                'sensor_type': 'vibration',
                'location_id': 'IFC_004',
                'description': 'Sensor de vibração no motor principal',
                'collection_interval': 20,
                'timeout': 10
            },
            {
                'name': 'Sensor Fluxo - Tubulação',
                'ip_address': '192.168.1.104',
                'port': 80,
                'sensor_type': 'flow',
                'location_id': 'IFC_005',
                'description': 'Sensor de fluxo na tubulação principal',
                'collection_interval': 60,
                'timeout': 10
            },
            {
                'name': 'Sensor Nível - Tanque',
                'ip_address': '192.168.1.105',
                'port': 80,
                'sensor_type': 'level',
                'location_id': 'IFC_006',
                'description': 'Sensor de nível no tanque de armazenamento',
                'collection_interval': 90,
                'timeout': 10
            }
        ]
        
        sensors = []
        for sensor_data in sensors_data:
            sensor = Sensor.objects.create(**sensor_data)
            sensors.append(sensor)
            self.stdout.write(
                self.style.SUCCESS(f'📡 Sensor criado: {sensor.name}')
            )
        
        return sensors
    
    def create_example_data(self, sensors, plant):
        """Cria dados de exemplo para os sensores."""
        self.stdout.write('📊 Criando dados de exemplo...')
        
        # Criar dados das últimas 24 horas
        now = timezone.now()
        data_count = 0
        
        for sensor in sensors:
            # Criar dados para as últimas 24 horas
            for hours_ago in range(24, 0, -1):
                timestamp = now - timezone.timedelta(hours=hours_ago)
                
                # Criar 1-4 dados por hora (dependendo do intervalo do sensor)
                readings_per_hour = max(1, 60 // sensor.collection_interval)
                
                for reading in range(readings_per_hour):
                    reading_time = timestamp + timezone.timedelta(
                        minutes=reading * (60 // readings_per_hour)
                    )
                    
                    # Gerar dados baseados no tipo do sensor
                    data = self.generate_sensor_data(sensor, reading_time)
                    
                    SensorData.objects.create(
                        sensor=sensor,
                        count=data['count'],
                        value=data['value'],
                        unit=data['unit'],
                        status=data['status'],
                        quality=data['quality'],
                        timestamp=reading_time,
                        raw_data=data['raw_data']
                    )
                    
                    data_count += 1
        
        # Atualizar timestamp da última coleta para todos os sensores
        for sensor in sensors:
            sensor.last_data_collected = now
            sensor.save(update_fields=['last_data_collected'])
        
        self.stdout.write(
            self.style.SUCCESS(f'📊 {data_count} registros de dados criados')
        )
    
    def generate_sensor_data(self, sensor, timestamp):
        """Gera dados simulados para um sensor."""
        base_time = timestamp.hour + timestamp.minute / 60.0
        
        if sensor.sensor_type == 'counter':
            # Contador: incrementa gradualmente com variação
            base_count = 1000 + int(base_time * 50)
            variation = random.randint(-20, 20)
            count = max(0, base_count + variation)
            
            return {
                'count': count,
                'value': None,
                'unit': 'unidades',
                'status': 'ok',
                'quality': random.uniform(95, 100),
                'raw_data': {
                    'simulated': True,
                    'base_count': base_count,
                    'variation': variation
                }
            }
        
        elif sensor.sensor_type == 'temperature':
            # Temperatura: variação baseada na hora do dia
            base_temp = 20 + 10 * (1 + 0.5 * (base_time / 12 - 1))
            variation = random.uniform(-2, 2)
            temp = base_temp + variation
            
            return {
                'count': 0,
                'value': round(temp, 1),
                'unit': '°C',
                'status': 'ok' if 18 <= temp <= 35 else 'warning',
                'quality': random.uniform(90, 100),
                'raw_data': {
                    'simulated': True,
                    'temperature': temp,
                    'base_temp': base_temp
                }
            }
        
        elif sensor.sensor_type == 'pressure':
            # Pressão: variação industrial
            base_pressure = 5.0 + 2 * (base_time / 24)
            variation = random.uniform(-0.5, 0.5)
            pressure = base_pressure + variation
            
            return {
                'count': 0,
                'value': round(pressure, 2),
                'unit': 'bar',
                'status': 'ok' if 3 <= pressure <= 8 else 'warning',
                'quality': random.uniform(88, 100),
                'raw_data': {
                    'simulated': True,
                    'pressure': pressure,
                    'base_pressure': base_pressure
                }
            }
        
        elif sensor.sensor_type == 'vibration':
            # Vibração: varia com a hora (mais vibração durante operação)
            base_vibration = 2.0 + 3 * (base_time / 24)
            variation = random.uniform(-0.5, 0.5)
            vibration = base_vibration + variation
            
            return {
                'count': 0,
                'value': round(vibration, 2),
                'unit': 'mm/s',
                'status': 'ok' if vibration <= 5 else 'warning',
                'quality': random.uniform(85, 100),
                'raw_data': {
                    'simulated': True,
                    'vibration': vibration,
                    'base_vibration': base_vibration
                }
            }
        
        elif sensor.sensor_type == 'flow':
            # Fluxo: variação de fluxo
            base_flow = 100 + 50 * (base_time / 24)
            variation = random.uniform(-10, 10)
            flow = base_flow + variation
            
            return {
                'count': 0,
                'value': round(flow, 1),
                'unit': 'L/min',
                'status': 'ok' if 80 <= flow <= 200 else 'warning',
                'quality': random.uniform(92, 100),
                'raw_data': {
                    'simulated': True,
                    'flow': flow,
                    'base_flow': base_flow
                }
            }
        
        elif sensor.sensor_type == 'level':
            # Nível: variação gradual
            base_level = 50 + 30 * (base_time / 24)
            variation = random.uniform(-5, 5)
            level = base_level + variation
            
            return {
                'count': 0,
                'value': round(level, 1),
                'unit': '%',
                'status': 'ok' if 20 <= level <= 90 else 'warning',
                'quality': random.uniform(90, 100),
                'raw_data': {
                    'simulated': True,
                    'level': level,
                    'base_level': base_level
                }
            }
        
        else:
            # Outros tipos: dados genéricos
            value = random.uniform(0, 100)
            
            return {
                'count': random.randint(0, 100),
                'value': round(value, 2),
                'unit': 'units',
                'status': 'ok',
                'quality': random.uniform(90, 100),
                'raw_data': {
                    'simulated': True,
                    'generic_value': value
                }
            }
