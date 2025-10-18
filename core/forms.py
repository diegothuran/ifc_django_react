from django import forms
from django.forms import ModelForm
from .models import Location
# Importar modelos de sensores do sensor_management (consolidado)
from sensor_management.models import Sensor, SensorAlert, SensorData


class LocationForm(ModelForm):
    """Form para criar/editar localizações."""
    class Meta:
        model = Location
        fields = ['name', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }


# =============================================================================
# FORMS PARA SENSORES MOVIDOS PARA sensor_management
# =============================================================================
# 
# Os forms para Sensor, SensorData e SensorAlert foram movidos.
# Se você precisa de forms para sensores, importe de:
#   from sensor_management.models import Sensor, SensorData, SensorAlert
# 
# E crie forms customizados conforme necessidade, ou use o admin diretamente.
# 
# Exemplo de uso:
# 
# class SensorForm(ModelForm):
#     class Meta:
#         model = Sensor
#         fields = ['name', 'sensor_type', 'ip_address', 'port', 'location_id']
# 
# =============================================================================
