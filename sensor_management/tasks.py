"""
Tarefas assíncronas do Celery para sensor_management.
Gerencia coleta de dados de sensores e limpeza de dados antigos.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def collect_sensor_data(sensor_id):
    """
    Coleta dados de um sensor específico de forma assíncrona.
    
    Args:
        sensor_id: ID do sensor a coletar dados
        
    Returns:
        dict: Status da coleta
    """
    from .models import Sensor, SensorData
    import requests
    
    try:
        sensor = Sensor.objects.get(id=sensor_id)
        
        # Construir URL do sensor
        url = f"http://{sensor.ip_address}:{sensor.port}/data"
        
        # Fazer requisição ao sensor
        response = requests.get(url, timeout=sensor.timeout)
        
        if response.status_code == 200:
            data = response.json()
            
            # Criar registro de dados
            sensor_data = SensorData.objects.create(
                sensor=sensor,
                count=data.get('count', 0),
                value=data.get('value'),
                unit=data.get('unit'),
                status=data.get('status', 'ok'),
                quality=data.get('quality', 100.0),
                raw_data=data
            )
            
            # Atualizar última coleta do sensor
            sensor.last_data_collected = timezone.now()
            sensor.save(update_fields=['last_data_collected'])
            
            logger.info(f"Dados coletados com sucesso do sensor {sensor_id}")
            return {
                'status': 'success',
                'sensor_id': sensor_id,
                'data_id': sensor_data.id
            }
        else:
            logger.warning(f"Falha ao coletar dados do sensor {sensor_id}: HTTP {response.status_code}")
            return {
                'status': 'failed',
                'sensor_id': sensor_id,
                'error': f"HTTP {response.status_code}"
            }
            
    except Sensor.DoesNotExist:
        logger.error(f"Sensor {sensor_id} não encontrado")
        return {'status': 'error', 'error': 'Sensor not found'}
    except requests.RequestException as e:
        logger.error(f"Erro de rede ao coletar dados do sensor {sensor_id}: {e}")
        return {'status': 'error', 'error': str(e)}
    except Exception as e:
        logger.error(f"Erro inesperado ao coletar dados do sensor {sensor_id}: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def collect_all_active_sensors():
    """
    Coleta dados de todos os sensores ativos.
    Executado periodicamente pelo Celery Beat.
    """
    from .models import Sensor
    
    active_sensors = Sensor.objects.filter(is_active=True)
    
    count = 0
    for sensor in active_sensors:
        # Agendar coleta assíncrona para cada sensor
        collect_sensor_data.delay(sensor.id)
        count += 1
    
    logger.info(f"Agendada coleta de dados de {count} sensores")
    return {
        'status': 'success',
        'scheduled_count': count
    }


@shared_task
def cleanup_old_sensor_data(days=30):
    """
    Remove dados de sensores mais antigos que X dias.
    Mantém o banco de dados otimizado.
    
    Args:
        days: Número de dias para manter dados (padrão: 30)
        
    Returns:
        dict: Estatísticas de limpeza
    """
    from .models import SensorData
    
    threshold = timezone.now() - timedelta(days=days)
    
    # Contar dados a serem removidos
    old_data = SensorData.objects.filter(timestamp__lt=threshold)
    count = old_data.count()
    
    # Remover dados antigos
    deleted = old_data.delete()
    
    logger.info(f"Removidos {count} registros de dados de sensores mais antigos que {days} dias")
    
    return {
        'status': 'success',
        'deleted_count': count,
        'threshold_date': threshold.isoformat(),
        'days': days
    }


@shared_task
def generate_sensor_report(sensor_id, start_date, end_date):
    """
    Gera relatório de dados de um sensor para um período específico.
    
    Args:
        sensor_id: ID do sensor
        start_date: Data inicial (ISO format)
        end_date: Data final (ISO format)
        
    Returns:
        dict: Relatório com estatísticas
    """
    from .models import Sensor, SensorData
    from django.db.models import Count, Avg, Max, Min
    from datetime import datetime
    
    try:
        sensor = Sensor.objects.get(id=sensor_id)
        
        # Converter datas
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Buscar dados do período
        data = SensorData.objects.filter(
            sensor=sensor,
            timestamp__gte=start,
            timestamp__lte=end
        )
        
        # Calcular estatísticas
        stats = data.aggregate(
            total_readings=Count('id'),
            avg_value=Avg('value'),
            max_value=Max('value'),
            min_value=Min('value'),
            avg_quality=Avg('quality'),
            avg_count=Avg('count'),
            max_count=Max('count'),
            min_count=Min('count')
        )
        
        # Dados por status
        status_distribution = list(
            data.values('status').annotate(count=Count('id'))
        )
        
        report = {
            'sensor_id': sensor_id,
            'sensor_name': sensor.name,
            'period': {
                'start': start_date,
                'end': end_date
            },
            'statistics': stats,
            'status_distribution': status_distribution,
            'generated_at': timezone.now().isoformat()
        }
        
        logger.info(f"Relatório gerado para sensor {sensor_id}")
        return report
        
    except Sensor.DoesNotExist:
        logger.error(f"Sensor {sensor_id} não encontrado")
        return {'status': 'error', 'error': 'Sensor not found'}
    except Exception as e:
        logger.error(f"Erro ao gerar relatório para sensor {sensor_id}: {e}")
        return {'status': 'error', 'error': str(e)}

