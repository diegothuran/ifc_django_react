from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

def redirect_to_dashboard(request):
    """Redireciona a raiz do site para o dashboard público."""
    return redirect('dashboard:public_dashboard')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API REST Framework
    path('api/', include('rest_framework.urls')),
    
    # API Documentation (OpenAPI/Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Apps principais
    path('', redirect_to_dashboard, name='home'),
    path('plant/', include('plant_viewer.urls', namespace='plant_viewer')),
    path('sensors/', include('sensor_management.urls', namespace='sensor_management')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    
    # Core (mantido para compatibilidade)
    path('core/', include('core.urls', namespace='core')),
]

# Servir arquivos de mídia em ambiente de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

