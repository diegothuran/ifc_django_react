import random
import socket
import time
import logging
from datetime import datetime, timezone
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone as django_timezone
from django.db import transaction
from sensor_management.models import Sensor, SensorData, SensorAlert


class Command(BaseCommand):
    """
    Comando Django para coletar dados dos sensores IoT.
    
    Este comando:
    1. Itera sobre todos os sensores ativos
    2. Tenta se conectar com cada sensor via IP/Porta
    3. Coleta dados e salva no banco de dados
    4. Gera alertas para sensores com problemas
    
    Uso:
    python manage.py collect_sensor_data [--simulate] [--sensor-id SENSOR_ID]
    
    Opções:
    --simulate: Simula dados sem tentar conectar com sensores reais
    --sensor-id: Coleta dados apenas de um sensor específico
    --verbose: Exibe informações detalhadas durante a execução
    """
    
    help = 'Coleta dados de todos os sensores IoT ativos'
    
    def add_arguments(self, parser):
        """Adiciona argumentos para o comando."""
        parser.add_argument(
            '--simulate',
            action='store_true',
            help='Simula dados sem conectar com sensores reais (para desenvolvimento)'
        )
        
        parser.add_argument(
            '--sensor-id',
            type=int,
            help='ID do sensor específico para coletar dados'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe informações detalhadas durante a execução'
        )
        
        parser.add_argument(
            '--timeout',
            type=int,
            default=10,
            help='Timeout em segundos para conexão com sensores (padrão: 10)'
        )
    
    def __init__(self):
        super().__init__()
        # Configurar logging
        self.logger = logging.getLogger('sensor_collection')
        
    def handle(self, *args, **options):
        """Função principal do comando."""
        self.simulate = options['simulate']
        self.sensor_id = options['sensor_id']
        self.verbose = options['verbose']
        self.timeout = options['timeout']
        
        if self.verbose:
            self.stdout.write(
                self.style.SUCCESS('Iniciando coleta de dados dos sensores...')
            )
        
        # Configurar logging se verbose
        if self.verbose:
            logging.basicConfig(level=logging.INFO)
        
        try:
            # Buscar sensores
            sensors = self.get_sensors()
            
            if not sensors.exists():
                self.stdout.write(
                    self.style.WARNING('Nenhum sensor ativo encontrado.')
                )
                return
            
            self.stdout.write(f'Encontrados {sensors.count()} sensor(es) ativo(s)')
            
            # Coletar dados de cada sensor
            success_count = 0
            error_count = 0
            
            for sensor in sensors:
                try:
                    self.collect_sensor_data(sensor)
                    success_count += 1
                    
                    if self.verbose:
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Dados coletados do sensor: {sensor.name}')
                        )
                        
                except Exception as e:
                    error_count += 1
                    self.logger.error(f'Erro ao coletar dados do sensor {sensor.name}: {str(e)}')
                    
                    if self.verbose:
                        self.stdout.write(
                            self.style.ERROR(f'✗ Erro no sensor {sensor.name}: {str(e)}')
                        )
                    
                    # Criar alerta de erro
                    self.create_error_alert(sensor, str(e))
            
            # Relatório final
            self.stdout.write(
                self.style.SUCCESS(
                    f'Coleta concluída: {success_count} sucessos, {error_count} erros'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Erro durante a coleta de dados: {str(e)}')
    
    def get_sensors(self):
        """Busca sensores para coleta de dados."""
        queryset = Sensor.objects.filter(is_active=True)
        
        if self.sensor_id:
            queryset = queryset.filter(id=self.sensor_id)
        
        return queryset.order_by('name')
    
    def collect_sensor_data(self, sensor):
        """
        Coleta dados de um sensor específico.
        
        Args:
            sensor (Sensor): Instância do sensor para coletar dados
        """
        if self.simulate:
            # Modo simulação - gera dados aleatórios
            data = self.simulate_sensor_data(sensor)
        else:
            # Modo real - conecta com o sensor
            data = self.read_sensor_data(sensor)
        
        # Salvar dados no banco
        self.save_sensor_data(sensor, data)
        
        # Atualizar timestamp da última coleta
        sensor.last_data_collected = django_timezone.now()
        sensor.save(update_fields=['last_data_collected'])
    
    def simulate_sensor_data(self, sensor):
        """
        Simula dados de um sensor para desenvolvimento/teste.
        
        Args:
            sensor (Sensor): Sensor para simular dados
            
        Returns:
            dict: Dados simulados do sensor
        """
        # Gerar dados baseados no tipo do sensor
        if sensor.sensor_type == 'counter':
            # Contador: incrementa gradualmente com alguma variação
            base_count = random.randint(100, 1000)
            variation = random.randint(-50, 50)
            count = max(0, base_count + variation)
            
            return {
                'count': count,
                'value': None,
                'unit': None,
                'status': 'ok',
                'quality': random.uniform(90, 100),
                'raw_data': {
                    'simulated': True,
                    'base_count': base_count,
                    'variation': variation
                }
            }
            
        elif sensor.sensor_type == 'temperature':
            # Temperatura: variação realista
            temp = random.uniform(15, 35)  # 15-35°C
            
            return {
                'count': 0,
                'value': round(temp, 1),
                'unit': '°C',
                'status': 'ok' if 20 <= temp <= 30 else 'warning',
                'quality': random.uniform(85, 100),
                'raw_data': {
                    'simulated': True,
                    'temperature': temp
                }
            }
            
        elif sensor.sensor_type == 'pressure':
            # Pressão: variação industrial
            pressure = random.uniform(1.0, 10.0)  # 1-10 bar
            
            return {
                'count': 0,
                'value': round(pressure, 2),
                'unit': 'bar',
                'status': 'ok' if 2 <= pressure <= 8 else 'warning',
                'quality': random.uniform(88, 100),
                'raw_data': {
                    'simulated': True,
                    'pressure': pressure
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
    
    def read_sensor_data(self, sensor):
        """
        Lê dados reais de um sensor via rede.
        
        Args:
            sensor (Sensor): Sensor para ler dados
            
        Returns:
            dict: Dados lidos do sensor
            
        Raises:
            ConnectionError: Se não conseguir conectar com o sensor
            TimeoutError: Se a conexão exceder o timeout
        """
        try:
            # Tentar conectar com o sensor
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Conectar
            sock.connect((sensor.ip_address, sensor.port))
            
            # Simular leitura de dados (em implementação real, aqui seria
            # o protocolo específico do sensor)
            time.sleep(0.1)  # Simular tempo de resposta
            
            # Simular recebimento de dados
            # Em implementação real, você leria dados reais do socket
            data = self.simulate_sensor_data(sensor)
            data['raw_data']['real_connection'] = True
            data['raw_data']['ip'] = sensor.ip_address
            data['raw_data']['port'] = sensor.port
            
            sock.close()
            return data
            
        except socket.timeout:
            raise TimeoutError(f'Timeout ao conectar com {sensor.ip_address}:{sensor.port}')
        except ConnectionRefusedError:
            raise ConnectionError(f'Conexão recusada por {sensor.ip_address}:{sensor.port}')
        except Exception as e:
            raise ConnectionError(f'Erro de conexão com {sensor.ip_address}:{sensor.port}: {str(e)}')
    
    @transaction.atomic
    def save_sensor_data(self, sensor, data):
        """
        Salva dados do sensor no banco de dados.
        
        Args:
            sensor (Sensor): Sensor que gerou os dados
            data (dict): Dados coletados do sensor
        """
        sensor_data = SensorData.objects.create(
            sensor=sensor,
            count=data.get('count', 0),
            value=data.get('value'),
            unit=data.get('unit'),
            status=data.get('status', 'ok'),
            quality=data.get('quality', 100.0),
            raw_data=data.get('raw_data', {}),
            additional_data=data.get('additional_data')
        )
        
        # Verificar se há alertas baseados nos dados
        self.check_data_alerts(sensor, sensor_data, data)
    
    def check_data_alerts(self, sensor, sensor_data, data):
        """
        Verifica se os dados coletados geram alertas.
        
        Args:
            sensor (Sensor): Sensor que gerou os dados
            sensor_data (SensorData): Dados salvos no banco
            data (dict): Dados originais coletados
        """
        alerts_created = []
        
        # Alerta de qualidade baixa
        if data.get('quality', 100) < 80:
            alerts_created.append(SensorAlert.objects.create(
                sensor=sensor,
                alert_type='threshold',
                level='warning',
                message=f'Qualidade dos dados baixa: {data.get("quality", 0):.1f}%'
            ))
        
        # Alerta de status de erro
        if data.get('status') == 'error':
            alerts_created.append(SensorAlert.objects.create(
                sensor=sensor,
                alert_type='error',
                level='error',
                message=f'Sensor reportou erro: {data.get("status", "unknown")}'
            ))
        
        # Alerta de temperatura alta (para sensores de temperatura)
        if (sensor.sensor_type == 'temperature' and 
            data.get('value') and 
            data.get('value') > 35):
            alerts_created.append(SensorAlert.objects.create(
                sensor=sensor,
                alert_type='threshold',
                level='warning',
                message=f'Temperatura alta detectada: {data.get("value")}°C'
            ))
        
        # Log de alertas criados
        if alerts_created and self.verbose:
            for alert in alerts_created:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Alerta criado para {sensor.name}: {alert.message}')
                )
    
    def create_error_alert(self, sensor, error_message):
        """
        Cria um alerta de erro para um sensor.
        
        Args:
            sensor (Sensor): Sensor com erro
            error_message (str): Mensagem de erro
        """
        try:
            SensorAlert.objects.create(
                sensor=sensor,
                alert_type='disconnection',
                level='error',
                message=f'Erro de comunicação: {error_message}'
            )
        except Exception as e:
            self.logger.error(f'Erro ao criar alerta para sensor {sensor.name}: {str(e)}')


# Exemplo de uso do comando:
# 
# 1. Coleta normal (modo simulação):
#    python manage.py collect_sensor_data --simulate --verbose
#
# 2. Coleta de sensor específico:
#    python manage.py collect_sensor_data --sensor-id 1 --simulate
#
# 3. Coleta real (com sensores físicos):
#    python manage.py collect_sensor_data --timeout 15
#
# 4. Configurar cron job para execução automática:
#    # Executar a cada 5 minutos
#    */5 * * * * cd /path/to/project && python manage.py collect_sensor_data --simulate
