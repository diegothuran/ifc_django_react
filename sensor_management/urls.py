from django.urls import path
from . import views

app_name = 'sensor_management'

urlpatterns = [
    # Lista de sensores
    path('', views.SensorListView.as_view(), name='sensor_list'),
    
    # Dashboard de sensores
    path('dashboard/', views.sensor_dashboard_view, name='sensor_dashboard'),
    
    # Detalhes de um sensor específico
    path('sensors/<int:pk>/', views.SensorDetailView.as_view(), name='sensor_detail'),
    
    # APIs para dados dos sensores
    path('api/sensors/', views.sensors_list_api, name='sensors_list_api'),  # Novo endpoint v2.3.0
    path('api/sensors/<int:sensor_id>/data/', views.sensor_data_api, name='sensor_data_api'),
    path('api/sensors/all/', views.all_sensors_data_api, name='all_sensors_data_api'),
]
