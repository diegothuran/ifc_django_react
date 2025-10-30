from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import Location
# Importar modelos de sensor_management (consolidado)
from sensor_management.models import Sensor, SensorData, SensorAlert

@login_required
def dashboard(request):
    """
    Dashboard principal do core.
    
    NOTA: Este dashboard usa modelos de sensor_management após a consolidação.
    Para dashboard completo de sensores, veja: /sensors/dashboard/
    Para dashboard público, veja: /dashboard/
    
    OTIMIZADO: Usa select_related e prefetch_related para evitar N+1 queries.
    Usa aggregate para estatísticas eficientes.
    
    NOVO (v2.3.0): Inclui visualização 3D da planta industrial no centro do dashboard.
    """
    from plant_viewer.models import BuildingPlan
    
    # Otimiza queries com select_related e prefetch_related
    sensors = Sensor.objects.filter(is_active=True)
    alerts = SensorAlert.objects.select_related('sensor').filter(is_active=True)
    locations = Location.objects.all()
    
    # Buscar planta ativa mais recente para visualização 3D
    active_plant = BuildingPlan.objects.filter(is_active=True).order_by('-uploaded_at').first()
    
    # Estatísticas básicas usando aggregate
    from django.db.models import Count, Q
    recent_threshold = timezone.now() - timedelta(hours=24)
    
    # Contar total e recente em uma única query
    data_stats = SensorData.objects.aggregate(
        total=Count('id'),
        recent=Count('id', filter=Q(timestamp__gte=recent_threshold))
    )
    
    # Alertas por nível em uma única query
    alerts_aggregated = alerts.values('level').annotate(count=Count('id'))
    alerts_by_level = {
        'critical': 0,
        'error': 0,
        'warning': 0,
        'info': 0,
    }
    for item in alerts_aggregated:
        alerts_by_level[item['level']] = item['count']

    # Últimas leituras (limitado) com select_related
    latest_data = SensorData.objects.select_related('sensor').order_by('-timestamp')[:10]

    context = {
        'sensors_count': sensors.count(),
        'alerts_count': alerts.count(),
        'locations_count': locations.count(),
        'total_data': data_stats['total'],
        'recent_data': data_stats['recent'],
        'alerts_by_level': alerts_by_level,
        'latest_data': latest_data,
        'alerts': alerts[:5],  # Apenas os 5 mais recentes
        'active_plant': active_plant,  # Para visualização 3D
        'page_title': 'Dashboard Core',
    }
    return render(request, 'core/dashboard.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('core:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('core:login')

