from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Avg, Max, Min, Q
from datetime import timedelta
from plant_viewer.models import BuildingPlan
from sensor_management.models import Sensor, SensorData, SensorAlert


def is_admin_user(user):
    """Verifica se o usuário é administrador."""
    return user.is_authenticated and user.is_staff


@staff_member_required
def admin_dashboard_view(request):
    """
    Dashboard administrativo com visualizações avançadas e estatísticas.
    Acesso restrito a administradores.
    """
    # Estatísticas gerais
    total_sensors = Sensor.objects.count()
    active_sensors = Sensor.objects.filter(is_active=True).count()
    total_plants = BuildingPlan.objects.count()
    active_plants = BuildingPlan.objects.filter(is_active=True).count()
    
    # Dados das últimas 24 horas
    recent_threshold = timezone.now() - timedelta(hours=24)
    
    # Estatísticas de dados recentes
    recent_data = SensorData.objects.filter(timestamp__gte=recent_threshold)
    total_readings = recent_data.count()
    
    if total_readings > 0:
        data_stats = recent_data.aggregate(
            avg_quality=Avg('quality'),
            min_quality=Min('quality'),
            max_quality=Max('quality'),
            avg_count=Avg('count'),
            avg_value=Avg('value')
        )
    else:
        data_stats = {}
    
    # Sensores por tipo
    sensors_by_type = Sensor.objects.values('sensor_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Alertas ativos por nível
    alerts_by_level = SensorAlert.objects.filter(is_active=True).values('level').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Sensores com problemas (sem dados recentes)
    problem_sensors = Sensor.objects.filter(
        is_active=True
    ).exclude(
        last_data_collected__gte=recent_threshold
    )
    
    # Dados por hora (últimas 24 horas)
    hourly_data = []
    for i in range(24):
        hour_start = timezone.now() - timedelta(hours=23-i)
        hour_end = hour_start + timedelta(hours=1)
        
        hour_readings = SensorData.objects.filter(
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).count()
        
        hourly_data.append({
            'hour': hour_start.strftime('%H:00'),
            'readings': hour_readings
        })
    
    # Top 5 sensores com mais dados
    top_sensors = Sensor.objects.annotate(
        reading_count=Count('data_readings', filter=Q(
            data_readings__timestamp__gte=recent_threshold
        ))
    ).order_by('-reading_count')[:5]
    
    context = {
        # Estatísticas gerais
        'total_sensors': total_sensors,
        'active_sensors': active_sensors,
        'total_plants': total_plants,
        'active_plants': active_plants,
        
        # Estatísticas de dados
        'total_readings': total_readings,
        'data_stats': data_stats,
        
        # Distribuições
        'sensors_by_type': sensors_by_type,
        'alerts_by_level': alerts_by_level,
        
        # Problemas e alertas
        'problem_sensors': problem_sensors,
        'active_alerts': SensorAlert.objects.filter(is_active=True).order_by('-created_at')[:10],
        
        # Dados para gráficos
        'hourly_data': hourly_data,
        'top_sensors': top_sensors,
        
        # Metadados
        'recent_threshold': recent_threshold,
        'page_title': 'Dashboard Administrativo'
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


def public_dashboard_view(request):
    """
    Dashboard público que combina visualização da planta com dados dos sensores.
    Acesso público, mas com dados limitados.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Buscar planta mais recente
    total_plants = BuildingPlan.objects.count()
    active_plants = BuildingPlan.objects.filter(is_active=True).count()
    
    logger.info(f"Dashboard: Total de plantas: {total_plants}, Plantas ativas: {active_plants}")
    
    latest_plant = BuildingPlan.objects.filter(is_active=True).first()
    
    if latest_plant:
        logger.info(f"Dashboard: Planta encontrada - ID: {latest_plant.id}, Nome: {latest_plant.name}")
    else:
        logger.warning(f"Dashboard: Nenhuma planta ativa encontrada")
    
    # Verificar se a planta tem arquivo IFC válido
    if latest_plant and latest_plant.ifc_file:
        try:
            # Tentar acessar o arquivo para verificar se existe
            file_size = latest_plant.ifc_file.size
            logger.info(f"Dashboard: Arquivo IFC válido - Tamanho: {file_size} bytes")
        except (FileNotFoundError, OSError, ValueError) as e:
            # Se o arquivo não existe, marcar a planta como inválida
            logger.error(f"Dashboard: Erro ao acessar arquivo IFC da planta {latest_plant.id}: {e}")
            latest_plant = None
    elif latest_plant and not latest_plant.ifc_file:
        logger.warning(f"Dashboard: Planta {latest_plant.id} não possui arquivo IFC")
        latest_plant = None
    
    # Dados dos sensores (última hora apenas)
    recent_threshold = timezone.now() - timedelta(hours=1)
    
    # Sensores ativos com dados recentes
    active_sensors = Sensor.objects.filter(is_active=True)
    
    # Dados resumidos dos sensores
    sensor_summaries = []
    for sensor in active_sensors:
        latest_data = sensor.data_readings.filter(
            timestamp__gte=recent_threshold
        ).order_by('-timestamp').first()
        
        if latest_data:
            sensor_summaries.append({
                'sensor': sensor,
                'latest_data': latest_data,
                'status': 'online' if latest_data.timestamp >= recent_threshold else 'offline'
            })
    
    # Estatísticas básicas
    total_active_sensors = len(sensor_summaries)
    online_sensors = len([s for s in sensor_summaries if s['status'] == 'online'])
    
    # Alertas críticos (apenas para dashboard público)
    critical_alerts = SensorAlert.objects.filter(
        is_active=True,
        level='critical'
    ).order_by('-created_at')[:5]
    
    context = {
        'plant': latest_plant,
        'sensor_summaries': sensor_summaries,
        'total_active_sensors': total_active_sensors,
        'online_sensors': online_sensors,
        'critical_alerts': critical_alerts,
        'recent_threshold': recent_threshold,
        'page_title': 'Dashboard Público - Digital Twin'
    }
    
    return render(request, 'dashboard/public_dashboard.html', context)


@login_required
def user_dashboard_view(request):
    """
    Dashboard para usuários autenticados (não administradores).
    Mostra mais informações que o público, mas menos que o admin.
    """
    # Buscar planta mais recente
    latest_plant = BuildingPlan.objects.filter(is_active=True).first()
    
    # Dados dos sensores (últimas 6 horas)
    recent_threshold = timezone.now() - timedelta(hours=6)
    
    # Sensores ativos
    active_sensors = Sensor.objects.filter(is_active=True)
    
    # Dados resumidos dos sensores
    sensor_summaries = []
    for sensor in active_sensors:
        recent_data = sensor.data_readings.filter(
            timestamp__gte=recent_threshold
        ).order_by('-timestamp')[:10]  # Últimos 10 dados
        
        if recent_data.exists():
            avg_quality = recent_data.aggregate(avg=Avg('quality'))['avg']
            sensor_summaries.append({
                'sensor': sensor,
                'recent_data': recent_data,
                'avg_quality': avg_quality,
                'data_count': recent_data.count(),
                'status': 'online' if sensor.last_data_collected and 
                          sensor.last_data_collected >= recent_threshold else 'offline'
            })
    
    # Estatísticas básicas
    total_active_sensors = len(sensor_summaries)
    online_sensors = len([s for s in sensor_summaries if s['status'] == 'online'])
    
    # Alertas (todos os níveis para usuários autenticados)
    recent_alerts = SensorAlert.objects.filter(
        is_active=True,
        created_at__gte=recent_threshold
    ).order_by('-created_at')[:10]
    
    context = {
        'plant': latest_plant,
        'sensor_summaries': sensor_summaries,
        'total_active_sensors': total_active_sensors,
        'online_sensors': online_sensors,
        'recent_alerts': recent_alerts,
        'recent_threshold': recent_threshold,
        'page_title': f'Dashboard - {request.user.username}'
    }
    
    return render(request, 'dashboard/user_dashboard.html', context)


def dashboard_data_api(request):
    """
    API endpoint para dados do dashboard em tempo real.
    Retorna dados em formato JSON para atualização via AJAX.
    """
    # Verificar se é uma requisição AJAX
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Requisição inválida'}, status=400)
    
    # Parâmetros da consulta
    data_type = request.GET.get('type', 'summary')
    hours = int(request.GET.get('hours', 1))
    
    # Calcular período
    since = timezone.now() - timedelta(hours=hours)
    
    if data_type == 'summary':
        # Dados resumidos
        active_sensors = Sensor.objects.filter(is_active=True).count()
        
        recent_data_count = SensorData.objects.filter(
            timestamp__gte=since
        ).count()
        
        active_alerts = SensorAlert.objects.filter(is_active=True).count()
        
        response_data = {
            'timestamp': timezone.now().isoformat(),
            'active_sensors': active_sensors,
            'recent_data_count': recent_data_count,
            'active_alerts': active_alerts,
            'period_hours': hours
        }
        
    elif data_type == 'sensors':
        # Dados detalhados dos sensores
        sensors_data = []
        
        for sensor in Sensor.objects.filter(is_active=True):
            latest_data = sensor.data_readings.filter(
                timestamp__gte=since
            ).order_by('-timestamp').first()
            
            sensor_info = {
                'id': sensor.id,
                'name': sensor.name,
                'type': sensor.sensor_type,
                'location_id': sensor.location_id,
                'status': sensor.get_status_display(),
                'is_online': sensor.last_data_collected and sensor.last_data_collected >= since,
                'latest_data': None
            }
            
            if latest_data:
                sensor_info['latest_data'] = {
                    'timestamp': latest_data.timestamp.isoformat(),
                    'count': latest_data.count,
                    'value': latest_data.value,
                    'unit': latest_data.unit,
                    'quality': latest_data.quality,
                    'display_value': latest_data.get_display_value()
                }
            
            sensors_data.append(sensor_info)
        
        response_data = {
            'timestamp': timezone.now().isoformat(),
            'sensors': sensors_data,
            'period_hours': hours
        }
        
    elif data_type == 'alerts':
        # Alertas recentes
        alerts = SensorAlert.objects.filter(
            is_active=True,
            created_at__gte=since
        ).order_by('-created_at')[:20]
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'sensor_name': alert.sensor.name,
                'alert_type': alert.alert_type,
                'level': alert.level,
                'message': alert.message,
                'created_at': alert.created_at.isoformat()
            })
        
        response_data = {
            'timestamp': timezone.now().isoformat(),
            'alerts': alerts_data,
            'period_hours': hours
        }
        
    else:
        return JsonResponse({'error': 'Tipo de dados inválido'}, status=400)
    
    return JsonResponse(response_data)


def plant_data_api(request):
    """
    API endpoint para dados da planta 3D.
    Retorna informações da planta ativa e sensores associados.
    """
    # Buscar planta ativa
    active_plant = BuildingPlan.objects.filter(is_active=True).first()
    
    if not active_plant:
        return JsonResponse({'error': 'Nenhuma planta ativa encontrada'}, status=404)
    
    # Buscar sensores com localização
    sensors_with_location = Sensor.objects.filter(
        is_active=True,
        location_id__isnull=False
    ).exclude(location_id='')
    
    sensors_data = []
    for sensor in sensors_with_location:
        latest_data = sensor.data_readings.order_by('-timestamp').first()
        
        sensor_info = {
            'id': sensor.id,
            'name': sensor.name,
            'type': sensor.sensor_type,
            'location_id': sensor.location_id,
            'latest_data': None
        }
        
        if latest_data:
            sensor_info['latest_data'] = {
                'value': latest_data.get_display_value(),
                'quality': latest_data.quality,
                'status': latest_data.status,
                'timestamp': latest_data.timestamp.isoformat()
            }
        
        sensors_data.append(sensor_info)
    
    response_data = {
        'plant': {
            'id': active_plant.id,
            'name': active_plant.name,
            'description': active_plant.description,
            'ifc_url': active_plant.ifc_file.url if active_plant.ifc_file else None
        },
        'sensors': sensors_data,
        'timestamp': timezone.now().isoformat()
    }
    
    return JsonResponse(response_data)


def sensor_data_api(request):
    """
    API endpoint para dados dos sensores no formato esperado pelo Digital Twin.
    Retorna dados no formato: [{"id": 1, "name": "Sensor Linha 1", "location_id": "12345", "latest_count": 582, "is_active": true}]
    """
    # Buscar sensores ativos com localização
    sensors = Sensor.objects.filter(
        is_active=True,
        location_id__isnull=False
    ).exclude(location_id='')
    
    sensors_data = []
    for sensor in sensors:
        # Buscar o último dado do sensor
        latest_data = sensor.data_readings.order_by('-timestamp').first()
        
        # Determinar se o sensor está ativo baseado no último dado
        is_sensor_active = False
        latest_count = 0
        
        if latest_data:
            # Considerar ativo se teve dados nas últimas 2 horas
            time_threshold = timezone.now() - timedelta(hours=2)
            is_sensor_active = latest_data.timestamp >= time_threshold
            latest_count = latest_data.count if latest_data.count is not None else 0
        
        sensor_info = {
            'id': sensor.id,
            'name': sensor.name,
            'location_id': sensor.location_id,
            'latest_count': latest_count,
            'is_active': is_sensor_active
        }
        
        sensors_data.append(sensor_info)
    
    return JsonResponse(sensors_data, safe=False)