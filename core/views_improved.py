import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta
from .models import Location
from sensor_management.models import Sensor, SensorData, SensorAlert
from plant_viewer.models import BuildingPlan

@login_required
def unified_dashboard(request):
    """
    Dashboard unificado com Vue.js
    Consolida informações de sensores, alertas e plantas em uma única interface
    """
    # Buscar todos os sensores ativos
    sensors = Sensor.objects.filter(is_active=True).select_related()
    
    # Buscar alertas ativos
    alerts = SensorAlert.objects.filter(
        is_active=True
    ).select_related('sensor').order_by('-created_at')[:20]
    
    # Buscar planta ativa
    active_plant = BuildingPlan.objects.filter(is_active=True).first()
    
    # Serializar dados para JSON
    sensors_data = []
    for sensor in sensors:
        sensors_data.append({
            'id': sensor.id,
            'name': sensor.name,
            'sensor_type': sensor.sensor_type,
            'sensor_type_display': sensor.get_sensor_type_display(),
            'ip_address': sensor.ip_address,
            'port': sensor.port,
            'location_id': sensor.location_id,
            'is_active': sensor.is_active,
            'last_data_collected': sensor.last_data_collected.isoformat() if sensor.last_data_collected else None,
        })
    
    alerts_data = []
    for alert in alerts:
        alerts_data.append({
            'id': alert.id,
            'sensor_id': alert.sensor.id,
            'sensor_name': alert.sensor.name,
            'message': alert.message,
            'severity': alert.level if hasattr(alert, 'level') else 'warning',
            'created_at': alert.created_at.isoformat() if hasattr(alert, 'created_at') else alert.timestamp.isoformat(),
        })
    
    active_plant_data = None
    if active_plant:
        active_plant_data = {
            'id': active_plant.id,
            'name': active_plant.name,
            'description': active_plant.description,
            'file_size': active_plant.get_file_size(),
            'uploaded_at': active_plant.uploaded_at.isoformat(),
            'viewer_url': f'/plant/',
        }
    
    context = {
        'sensors_json': json.dumps(sensors_data, cls=DjangoJSONEncoder),
        'alerts_json': json.dumps(alerts_data, cls=DjangoJSONEncoder),
        'active_plant_json': json.dumps(active_plant_data, cls=DjangoJSONEncoder),
        'sensors': sensors,  # Para o search index
        'active_plant': active_plant,  # Para o search index
        'page_title': 'Dashboard Unificado',
    }
    
    return render(request, 'core/unified_dashboard.html', context)


@login_required
def dashboard(request):
    """
    Dashboard original (mantido para compatibilidade)
    Redireciona para o dashboard unificado
    """
    return redirect('core:unified_dashboard')


def login_view(request):
    """View de login melhorada"""
    if request.user.is_authenticated:
        return redirect('core:unified_dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'core:unified_dashboard')
                return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})


@login_required
def logout_view(request):
    """View de logout"""
    logout(request)
    return redirect('core:login')

