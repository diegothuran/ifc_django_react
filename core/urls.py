from django.urls import path
from . import views, health

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Health check endpoints
    path('health/', health.health_check, name='health'),
    path('health/detailed/', health.health_check_detailed, name='health_detailed'),
    path('health/ready/', health.readiness_check, name='readiness'),
    path('health/live/', health.liveness_check, name='liveness'),
]

