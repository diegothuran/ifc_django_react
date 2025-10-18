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
    """
    # Otimiza queries com select_related e prefetch_related
    sensors = Sensor.objects.filter(is_active=True)
    alerts = SensorAlert.objects.select_related('sensor').filter(is_active=True)
    locations = Location.objects.all()
    
    # Estatísticas básicas
    recent_threshold = timezone.now() - timedelta(hours=24)
    total_data = SensorData.objects.count()
    recent_data = SensorData.objects.filter(
        timestamp__gte=recent_threshold
    ).count()
    
    # Alertas por nível
    alerts_by_level = {
        'critical': alerts.filter(level='critical').count(),
        'error': alerts.filter(level='error').count(),
        'warning': alerts.filter(level='warning').count(),
        'info': alerts.filter(level='info').count(),
    }

    # Últimas leituras (limitado)
    latest_data = SensorData.objects.select_related('sensor').order_by('-timestamp')[:10]

    context = {
        'sensors_count': sensors.count(),
        'alerts_count': alerts.count(),
        'locations_count': locations.count(),
        'total_data': total_data,
        'recent_data': recent_data,
        'alerts_by_level': alerts_by_level,
        'latest_data': latest_data,
        'alerts': alerts[:5],  # Apenas os 5 mais recentes
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

