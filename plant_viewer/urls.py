from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'plant_viewer'

# Configurar router do Django REST Framework
router = DefaultRouter()
router.register(r'plants', views.BuildingPlanViewSet, basename='api-plant')

urlpatterns = [
    # ==================== Views HTML ====================
    
    # Visualização principal da planta 3D
    path('', views.main_plant_view, name='main_plant_view'),
    
    # Lista de plantas
    path('plants/', views.PlantListView.as_view(), name='plant_list'),
    
    # Detalhes de uma planta específica
    path('plants/<int:pk>/', views.PlantDetailView.as_view(), name='plant_detail'),
    
    # ==================== API REST ====================
    
    # API REST completa (usando DRF Router)
    # Endpoints disponíveis:
    #   GET    /plant-viewer/api/plants/                     - Lista plantas
    #   POST   /plant-viewer/api/plants/                     - Criar planta
    #   GET    /plant-viewer/api/plants/{id}/                - Detalhes da planta
    #   PUT    /plant-viewer/api/plants/{id}/                - Atualizar planta
    #   PATCH  /plant-viewer/api/plants/{id}/                - Atualizar parcial
    #   DELETE /plant-viewer/api/plants/{id}/                - Remover planta
    #   GET    /plant-viewer/api/plants/{id}/metadata/       - Metadados IFC
    #   POST   /plant-viewer/api/plants/{id}/refresh_metadata/ - Atualizar metadados
    #   GET    /plant-viewer/api/plants/{id}/elements/       - Elementos por tipo
    #   GET    /plant-viewer/api/plants/{id}/element/{element_id}/ - Propriedades elemento
    #   GET    /plant-viewer/api/plants/{id}/statistics/     - Estatísticas
    #   GET    /plant-viewer/api/plants/{id}/spatial_structure/ - Estrutura espacial
    #   GET    /plant-viewer/api/plants/{id}/bounds/         - Limites do modelo
    #   GET    /plant-viewer/api/plants/{id}/search/?q=nome  - Buscar elementos
    path('api/', include(router.urls)),
    
    # API legada (DEPRECATED - manter por compatibilidade)
    path('api/plants/<int:plant_id>/', views.get_plant_data_api, name='plant_data_api'),
]
