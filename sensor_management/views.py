from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.db.models import Count, Avg, Max, Min
from datetime import timedelta
from .models import Sensor, SensorData, SensorAlert


class SensorListView(ListView):
    """
    Lista todos os sensores com status e informações básicas.
    """
    model = Sensor
    template_name = 'sensor_management/sensor_list.html'
    context_object_name = 'sensors'
    paginate_by = 20
    
    def get_queryset(self):
        """Retorna sensores ordenados por nome."""
        return Sensor.objects.all().order_by('name')
    
    def get_context_data(self, **kwargs):
        """Adiciona estatísticas ao contexto."""
        context = super().get_context_data(**kwargs)
        
        # Estatísticas gerais
        total_sensors = Sensor.objects.count()
        active_sensors = Sensor.objects.filter(is_active=True).count()
        inactive_sensors = total_sensors - active_sensors
        
        # Sensores com dados recentes (última hora)
        recent_threshold = timezone.now() - timedelta(hours=1)
        sensors_with_recent_data = Sensor.objects.filter(
            last_data_collected__gte=recent_threshold,
            is_active=True
        ).count()
        
        # Alertas ativos
        active_alerts = SensorAlert.objects.filter(is_active=True).count()
        
        context.update({
            'total_sensors': total_sensors,
            'active_sensors': active_sensors,
            'inactive_sensors': inactive_sensors,
            'sensors_with_recent_data': sensors_with_recent_data,
            'active_alerts': active_alerts,
        })
        
        return context


class SensorDetailView(DetailView):
    """
    Visualização detalhada de um sensor específico.
    """
    model = Sensor
    template_name = 'sensor_management/sensor_detail.html'
    context_object_name = 'sensor'
    
    def get_context_data(self, **kwargs):
        """Adiciona dados recentes e estatísticas ao contexto."""
        context = super().get_context_data(**kwargs)
        sensor = self.object
        
        # Dados recentes (últimas 24 horas)
        recent_threshold = timezone.now() - timedelta(hours=24)
        recent_data = sensor.data_readings.filter(
            timestamp__gte=recent_threshold
        ).order_by('-timestamp')[:50]
        
        # Estatísticas dos dados recentes
        if recent_data.exists():
            stats = recent_data.aggregate(
                count_avg=Avg('count'),
                count_max=Max('count'),
                count_min=Min('count'),
                value_avg=Avg('value'),
                value_max=Max('value'),
                value_min=Min('value'),
                quality_avg=Avg('quality')
            )
        else:
            stats = {}
        
        # Alertas ativos do sensor
        active_alerts = sensor.alerts.filter(is_active=True)
        
        context.update({
            'recent_data': recent_data,
            'stats': stats,
            'active_alerts': active_alerts,
        })
        
        return context


def sensor_data_api(request, sensor_id):
    """
    API endpoint para obter dados de um sensor específico.
    Retorna dados em formato JSON para uso em dashboards.
    """
    sensor = get_object_or_404(Sensor, id=sensor_id)
    
    # Parâmetros de consulta
    hours = int(request.GET.get('hours', 24))
    limit = int(request.GET.get('limit', 100))
    
    # Calcular período
    since = timezone.now() - timedelta(hours=hours)
    
    # Buscar dados
    data = sensor.data_readings.filter(
        timestamp__gte=since
    ).order_by('-timestamp')[:limit]
    
    # Formatar dados para JSON
    formatted_data = []
    for reading in data:
        formatted_data.append({
            'id': reading.id,
            'timestamp': reading.timestamp.isoformat(),
            'count': reading.count,
            'value': reading.value,
            'unit': reading.unit,
            'status': reading.status,
            'quality': reading.quality,
            'display_value': reading.get_display_value()
        })
    
    # Estatísticas
    if data.exists():
        stats = data.aggregate(
            count_avg=Avg('count'),
            count_max=Max('count'),
            count_min=Min('count'),
            value_avg=Avg('value'),
            value_max=Max('value'),
            value_min=Min('value'),
            quality_avg=Avg('quality'),
            total_readings=Count('id')
        )
    else:
        stats = {'total_readings': 0}
    
    response_data = {
        'sensor': {
            'id': sensor.id,
            'name': sensor.name,
            'sensor_type': sensor.sensor_type,
            'ip_address': sensor.ip_address,
            'port': sensor.port,
            'location_id': sensor.location_id,
            'is_active': sensor.is_active,
            'status': sensor.get_status_display()
        },
        'data': formatted_data,
        'stats': stats,
        'period_hours': hours,
        'total_data_points': len(formatted_data)
    }
    
    return JsonResponse(response_data)


def all_sensors_data_api(request):
    """
    API endpoint para obter dados de todos os sensores ativos.
    """
    # Parâmetros de consulta
    hours = int(request.GET.get('hours', 1))
    
    # Calcular período
    since = timezone.now() - timedelta(hours=hours)
    
    # Buscar sensores ativos
    sensors = Sensor.objects.filter(is_active=True)
    
    response_data = {
        'timestamp': timezone.now().isoformat(),
        'period_hours': hours,
        'sensors': []
    }
    
    for sensor in sensors:
        # Último dado do sensor
        latest_data = sensor.data_readings.filter(
            timestamp__gte=since
        ).order_by('-timestamp').first()
        
        # Contagem de dados no período
        data_count = sensor.data_readings.filter(
            timestamp__gte=since
        ).count()
        
        sensor_info = {
            'id': sensor.id,
            'name': sensor.name,
            'sensor_type': sensor.sensor_type,
            'ip_address': sensor.ip_address,
            'location_id': sensor.location_id,
            'status': sensor.get_status_display(),
            'latest_data': None,
            'data_count': data_count
        }
        
        if latest_data:
            sensor_info['latest_data'] = {
                'timestamp': latest_data.timestamp.isoformat(),
                'count': latest_data.count,
                'value': latest_data.value,
                'unit': latest_data.unit,
                'status': latest_data.status,
                'quality': latest_data.quality,
                'display_value': latest_data.get_display_value()
            }
        
        response_data['sensors'].append(sensor_info)
    
    return JsonResponse(response_data)


def sensor_dashboard_view(request):
    """
    View para dashboard de sensores com visualizações e estatísticas.
    """
    # Estatísticas gerais
    total_sensors = Sensor.objects.count()
    active_sensors = Sensor.objects.filter(is_active=True).count()
    
    # Dados das últimas 24 horas
    recent_threshold = timezone.now() - timedelta(hours=24)
    
    # Sensores por tipo
    sensors_by_type = Sensor.objects.values('sensor_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Alertas ativos
    active_alerts = SensorAlert.objects.filter(is_active=True).order_by('-created_at')
    
    # Sensores com problemas (sem dados recentes)
    problem_sensors = Sensor.objects.filter(
        is_active=True
    ).exclude(
        last_data_collected__gte=recent_threshold
    )
    
    context = {
        'total_sensors': total_sensors,
        'active_sensors': active_sensors,
        'sensors_by_type': sensors_by_type,
        'active_alerts': active_alerts,
        'problem_sensors': problem_sensors,
        'recent_threshold': recent_threshold,
    }
    
    return render(request, 'sensor_management/sensor_dashboard.html', context)


def sensors_list_api(request):
    """
    API endpoint para listar todos os sensores (usado pelo viewer 3D).
    Retorna lista simplificada de sensores com informações básicas.
    """
    # Filtrar por is_active se especificado
    is_active = request.GET.get('is_active')
    
    queryset = Sensor.objects.all()
    if is_active is not None:
        is_active_bool = is_active.lower() in ('true', '1', 'yes')
        queryset = queryset.filter(is_active=is_active_bool)
    
    # Serializar sensores
    sensors_list = []
    for sensor in queryset:
        sensors_list.append({
            'id': sensor.id,
            'name': sensor.name,
            'sensor_type': sensor.sensor_type,
            'location_id': sensor.location_id,
            'ip_address': sensor.ip_address,
            'is_active': sensor.is_active,
            'last_data_collected': sensor.last_data_collected.isoformat() if sensor.last_data_collected else None,
            'status': sensor.get_status_display() if hasattr(sensor, 'get_status_display') else 'unknown',
        })
    
    return JsonResponse({
        'results': sensors_list,
        'count': len(sensors_list),
    })