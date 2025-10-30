from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboards principais
    path('', views.public_dashboard_view, name='public_dashboard'),
    path('user/', views.user_dashboard_view, name='user_dashboard'),
    path('admin/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # APIs para dados em tempo real
    path('api/data/', views.dashboard_data_api, name='dashboard_data_api'),
    path('api/plant/', views.plant_data_api, name='plant_data_api'),
    path('api/sensor-data/', views.sensor_data_api, name='sensor_data_api'),
    path('api/heatmap/', views.heatmap_data_api, name='heatmap_data_api'),  # Novo endpoint v2.3.0
]
