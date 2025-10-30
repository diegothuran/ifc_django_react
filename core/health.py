"""
Health check endpoints para monitoramento do sistema.
Útil para verificar o estado do sistema em produção.
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Endpoint básico de health check.
    Retorna 200 se o sistema está funcionando.
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'IFC Digital Twin'
    })


def health_check_detailed(request):
    """
    Endpoint detalhado de health check.
    Verifica database, cache e outros serviços.
    """
    checks = {
        'database': False,
        'cache': False,
    }
    
    errors = []
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks['database'] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        errors.append(f"Database: {str(e)}")
    
    # Check cache
    try:
        cache_key = 'health_check_test'
        cache.set(cache_key, 'ok', 10)
        cache_value = cache.get(cache_key)
        checks['cache'] = (cache_value == 'ok')
        if not checks['cache']:
            errors.append("Cache: Failed to read/write")
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        errors.append(f"Cache: {str(e)}")
    
    # Determine overall status
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    response_data = {
        'status': 'healthy' if all_healthy else 'unhealthy',
        'timestamp': timezone.now().isoformat(),
        'checks': checks,
        'errors': errors if errors else None
    }
    
    return JsonResponse(response_data, status=status_code)


def readiness_check(request):
    """
    Readiness check para Kubernetes/Docker.
    Verifica se a aplicação está pronta para receber tráfego.
    """
    try:
        # Verificar se consegue fazer queries básicas
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'ready',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=503)


def liveness_check(request):
    """
    Liveness check para Kubernetes/Docker.
    Verifica se a aplicação está viva (não travada).
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': timezone.now().isoformat()
    })

