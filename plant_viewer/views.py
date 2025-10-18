from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from .models import BuildingPlan


def main_plant_view(request):
    """
    View principal para visualização da planta 3D.
    Carrega o arquivo IFC mais recente e renderiza o visualizador 3D.
    """
    # Busca a planta mais recente e ativa
    latest_plant = BuildingPlan.objects.filter(is_active=True).first()
    
    context = {
        'plant': latest_plant,
        'page_title': 'Visualização da Planta Industrial'
    }
    
    return render(request, 'plant_viewer/main_plant_view.html', context)


class PlantListView(ListView):
    """
    Lista todas as plantas disponíveis.
    """
    model = BuildingPlan
    template_name = 'plant_viewer/plant_list.html'
    context_object_name = 'plants'
    paginate_by = 10
    
    def get_queryset(self):
        """Retorna apenas plantas ativas, ordenadas por data de upload."""
        return BuildingPlan.objects.filter(is_active=True).order_by('-uploaded_at')


class PlantDetailView(DetailView):
    """
    Visualização detalhada de uma planta específica.
    """
    model = BuildingPlan
    template_name = 'plant_viewer/plant_detail.html'
    context_object_name = 'plant'
    
    def get_queryset(self):
        """Retorna apenas plantas ativas."""
        return BuildingPlan.objects.filter(is_active=True)


def get_plant_data_api(request, plant_id):
    """
    API endpoint para obter dados de uma planta específica.
    Retorna informações da planta em formato JSON.
    DEPRECATED: Use a API REST em /api/plants/ ao invés desta.
    """
    plant = get_object_or_404(BuildingPlan, id=plant_id, is_active=True)
    
    data = {
        'id': plant.id,
        'name': plant.name,
        'description': plant.description,
        'ifc_url': plant.ifc_file.url if plant.ifc_file else None,
        'uploaded_at': plant.uploaded_at.isoformat(),
        'file_size': plant.get_file_size()
    }
    
    return JsonResponse(data)


# ==================== REST API ViewSets ====================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import (
    BuildingPlanSerializer,
    BuildingPlanListSerializer,
    BuildingPlanCreateSerializer,
    ElementPropertiesSerializer,
    StatisticsSerializer
)


class BuildingPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para API de BuildingPlan.
    
    Endpoints disponíveis:
    - GET /api/plants/ - Lista todas as plantas ativas
    - GET /api/plants/{id}/ - Detalhes de uma planta específica
    - POST /api/plants/ - Criar nova planta (requer autenticação)
    - PUT/PATCH /api/plants/{id}/ - Atualizar planta (requer autenticação)
    - DELETE /api/plants/{id}/ - Remover planta (requer autenticação)
    - GET /api/plants/{id}/metadata/ - Metadados completos do IFC
    - POST /api/plants/{id}/refresh_metadata/ - Forçar atualização de metadados
    - GET /api/plants/{id}/elements/ - Elementos organizados por tipo
    - GET /api/plants/{id}/element/{element_id}/ - Propriedades de elemento específico
    - GET /api/plants/{id}/statistics/ - Estatísticas do modelo
    - GET /api/plants/{id}/spatial_structure/ - Estrutura espacial hierárquica
    - GET /api/plants/{id}/bounds/ - Limites (bounding box) do modelo
    - GET /api/plants/{id}/search/?q=nome - Buscar elementos por nome
    """
    
    queryset = BuildingPlan.objects.filter(is_active=True).order_by('-uploaded_at')
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Retorna serializer apropriado baseado na action."""
        if self.action == 'list':
            return BuildingPlanListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BuildingPlanCreateSerializer
        return BuildingPlanSerializer
    
    def get_serializer_context(self):
        """Adiciona contexto extra para serializers."""
        context = super().get_serializer_context()
        # Incluir metadados completos apenas em retrieve, não em list
        context['include_metadata'] = (self.action == 'retrieve')
        return context
    
    def retrieve(self, request, *args, **kwargs):
        """
        Obtém detalhes de uma planta específica.
        Query params:
            - include_metadata: true/false (padrão: true)
        """
        instance = self.get_object()
        
        # Verificar se deve incluir metadados
        include_metadata = request.query_params.get('include_metadata', 'true').lower() == 'true'
        
        serializer = self.get_serializer(
            instance,
            context={**self.get_serializer_context(), 'include_metadata': include_metadata}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def metadata(self, request, pk=None):
        """
        Endpoint para obter metadados completos do IFC.
        
        Returns:
            JSON com project_info, building_elements, spatial_structure,
            statistics e bounds
        """
        plant = self.get_object()
        metadata = plant.get_metadata()
        
        if not metadata:
            return Response(
                {'error': 'Não foi possível extrair metadados do arquivo IFC'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(metadata)
    
    @action(detail=True, methods=['post'])
    def refresh_metadata(self, request, pk=None):
        """
        Força atualização dos metadados do IFC.
        Útil quando o arquivo IFC foi atualizado.
        """
        plant = self.get_object()
        metadata = plant.refresh_metadata()
        
        if not metadata:
            return Response(
                {'error': 'Não foi possível atualizar metadados do arquivo IFC'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'message': 'Metadados atualizados com sucesso',
            'metadata': metadata,
            'updated_at': plant.metadata_updated_at
        })
    
    @action(detail=True, methods=['get'])
    def elements(self, request, pk=None):
        """
        Endpoint para obter elementos do IFC organizados por tipo.
        
        Returns:
            JSON com elementos agrupados por tipo (IfcWall, IfcSlab, etc.)
        """
        plant = self.get_object()
        metadata = plant.get_metadata()
        elements = metadata.get('building_elements', {})
        
        # Calcular totais
        totals = {element_type: len(items) for element_type, items in elements.items()}
        
        return Response({
            'elements': elements,
            'totals': totals,
            'total_elements': sum(totals.values())
        })
    
    @action(detail=True, methods=['get'], url_path='element/(?P<element_id>[0-9]+)')
    def element_properties(self, request, pk=None, element_id=None):
        """
        Endpoint para obter propriedades de um elemento específico.
        
        Args:
            element_id: ID do elemento IFC
            
        Returns:
            JSON com propriedades completas do elemento
        """
        from .ifc_processor import IFCProcessor
        
        plant = self.get_object()
        
        if not plant.ifc_file:
            return Response(
                {'error': 'Arquivo IFC não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            processor = IFCProcessor(plant.ifc_file.path)
            if not processor.open():
                return Response(
                    {'error': 'Erro ao abrir arquivo IFC'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            properties = processor.get_element_properties(int(element_id))
            
            if not properties or 'error' in properties:
                return Response(
                    {'error': f'Elemento {element_id} não encontrado ou erro ao processar'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = ElementPropertiesSerializer(properties)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Endpoint para obter estatísticas do modelo IFC.
        
        Returns:
            JSON com estatísticas (total de elementos, tipos, etc.)
        """
        plant = self.get_object()
        metadata = plant.get_metadata()
        stats = metadata.get('statistics', {})
        
        if not stats:
            return Response(
                {'error': 'Estatísticas não disponíveis'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StatisticsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def spatial_structure(self, request, pk=None):
        """
        Endpoint para obter estrutura espacial hierárquica.
        
        Returns:
            JSON com estrutura hierárquica (projeto -> site -> edifício -> andar)
        """
        plant = self.get_object()
        metadata = plant.get_metadata()
        structure = metadata.get('spatial_structure', [])
        
        return Response({
            'spatial_structure': structure,
            'total_nodes': self._count_nodes(structure)
        })
    
    def _count_nodes(self, structure):
        """Helper para contar nós na estrutura espacial."""
        count = 0
        for node in structure:
            count += 1
            if 'children' in node:
                count += self._count_nodes(node['children'])
        return count
    
    @action(detail=True, methods=['get'])
    def bounds(self, request, pk=None):
        """
        Endpoint para obter limites (bounding box) do modelo.
        
        Returns:
            JSON com coordenadas min/max, centro e tamanho
        """
        plant = self.get_object()
        metadata = plant.get_metadata()
        bounds = metadata.get('bounds')
        
        if not bounds:
            return Response(
                {'error': 'Limites do modelo não disponíveis'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(bounds)
    
    @action(detail=True, methods=['get'])
    def search(self, request, pk=None):
        """
        Endpoint para buscar elementos por nome.
        
        Query params:
            - q: termo de busca (obrigatório)
            
        Returns:
            JSON com elementos encontrados
        """
        from .ifc_processor import IFCProcessor
        
        plant = self.get_object()
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {'error': 'Parâmetro "q" é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not plant.ifc_file:
            return Response(
                {'error': 'Arquivo IFC não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            processor = IFCProcessor(plant.ifc_file.path)
            if not processor.open():
                return Response(
                    {'error': 'Erro ao abrir arquivo IFC'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            results = processor.search_elements_by_name(query)
            
            return Response({
                'query': query,
                'results': results,
                'total': len(results)
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def spaces(self, request, pk=None):
        """
        Endpoint para obter espaços IFC com coordenadas para visualização de planta baixa.
        
        Returns:
            JSON com lista de espaços contendo:
            - id, global_id, name, description
            - x_coordinate, y_coordinate, z_coordinate
            - area, volume, height
        """
        from .ifc_processor import IFCProcessor
        
        plant = self.get_object()
        
        if not plant.ifc_file:
            return Response(
                {'error': 'Arquivo IFC não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            processor = IFCProcessor(plant.ifc_file.path)
            if not processor.open():
                return Response(
                    {'error': 'Erro ao abrir arquivo IFC'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            spaces = processor.get_spaces_with_coordinates()
            
            # Calcular estatísticas dos espaços
            total_area = sum(space['area'] for space in spaces if space['area'] > 0)
            total_volume = sum(space['volume'] for space in spaces if space['volume'] > 0)
            
            # Calcular bounds dos espaços
            if spaces:
                x_coords = [s['x_coordinate'] for s in spaces]
                y_coords = [s['y_coordinate'] for s in spaces]
                z_coords = [s['z_coordinate'] for s in spaces]
                
                bounds = {
                    'min': {'x': min(x_coords), 'y': min(y_coords), 'z': min(z_coords)},
                    'max': {'x': max(x_coords), 'y': max(y_coords), 'z': max(z_coords)}
                }
            else:
                bounds = None
            
            return Response({
                'spaces': spaces,
                'total_spaces': len(spaces),
                'total_area': round(total_area, 2),
                'total_volume': round(total_volume, 2),
                'bounds': bounds
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )