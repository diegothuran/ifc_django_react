"""
Tarefas assíncronas do Celery para plant_viewer.
Processa arquivos IFC em background para evitar timeout.
"""

from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_ifc_metadata(self, plant_id):
    """
    Processa metadados de um arquivo IFC de forma assíncrona.
    
    Args:
        plant_id: ID da BuildingPlan a processar
        
    Returns:
        dict: Status do processamento
    """
    from .models import BuildingPlan
    
    try:
        plant = BuildingPlan.objects.get(id=plant_id)
        logger.info(f"Iniciando processamento de metadados IFC para planta {plant_id}")
        
        # Extrair metadados
        metadata = plant.extract_metadata(force_update=True)
        
        if metadata:
            logger.info(f"Metadados extraídos com sucesso para planta {plant_id}")
            return {
                'status': 'success',
                'plant_id': plant_id,
                'metadata_size': len(str(metadata)),
                'processed_at': timezone.now().isoformat()
            }
        else:
            logger.error(f"Falha ao extrair metadados para planta {plant_id}")
            return {
                'status': 'failed',
                'plant_id': plant_id,
                'error': 'Failed to extract metadata'
            }
            
    except BuildingPlan.DoesNotExist:
        logger.error(f"Planta {plant_id} não encontrada")
        return {
            'status': 'error',
            'error': 'BuildingPlan not found'
        }
    except Exception as e:
        logger.error(f"Erro ao processar metadados IFC para planta {plant_id}: {e}")
        # Retry em caso de erro
        try:
            self.retry(countdown=60 * (self.request.retries + 1))
        except self.MaxRetriesExceededError:
            return {
                'status': 'error',
                'error': str(e),
                'max_retries_exceeded': True
            }


@shared_task
def process_pending_ifc_files():
    """
    Processa arquivos IFC que ainda não têm metadados extraídos.
    Executado periodicamente pelo Celery Beat.
    """
    from .models import BuildingPlan
    from django.db.models import Q
    from datetime import timedelta
    
    # Buscar plantas sem metadados ou com metadados antigos (> 7 dias)
    threshold = timezone.now() - timedelta(days=7)
    
    pending_plants = BuildingPlan.objects.filter(
        is_active=True,
        ifc_file__isnull=False
    ).filter(
        Q(metadata__isnull=True) | 
        Q(metadata_updated_at__lt=threshold)
    )
    
    count = 0
    for plant in pending_plants:
        # Agendar processamento assíncrono
        process_ifc_metadata.delay(plant.id)
        count += 1
    
    logger.info(f"Agendado processamento de {count} arquivos IFC")
    return {
        'status': 'success',
        'scheduled_count': count
    }


@shared_task
def bulk_process_ifc_files(plant_ids):
    """
    Processa múltiplos arquivos IFC em batch.
    
    Args:
        plant_ids: Lista de IDs de BuildingPlan
        
    Returns:
        dict: Status do processamento em batch
    """
    from .models import BuildingPlan
    
    results = []
    for plant_id in plant_ids:
        try:
            plant = BuildingPlan.objects.get(id=plant_id)
            metadata = plant.extract_metadata(force_update=True)
            results.append({
                'plant_id': plant_id,
                'status': 'success' if metadata else 'failed'
            })
        except Exception as e:
            logger.error(f"Erro ao processar planta {plant_id}: {e}")
            results.append({
                'plant_id': plant_id,
                'status': 'error',
                'error': str(e)
            })
    
    return {
        'total': len(plant_ids),
        'results': results,
        'processed_at': timezone.now().isoformat()
    }

