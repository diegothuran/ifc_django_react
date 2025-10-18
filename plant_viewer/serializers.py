"""
Serializers para API REST do plant_viewer.
"""

from rest_framework import serializers
from .models import BuildingPlan


class BuildingPlanListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de plantas.
    Usado em endpoints de lista para melhor performance.
    """
    
    file_size = serializers.SerializerMethodField()
    ifc_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BuildingPlan
        fields = [
            'id',
            'name',
            'description',
            'uploaded_at',
            'is_active',
            'file_size',
            'ifc_url'
        ]
    
    def get_file_size(self, obj):
        """Retorna tamanho do arquivo formatado."""
        return obj.get_file_size()
    
    def get_ifc_url(self, obj):
        """Retorna URL absoluta do arquivo IFC."""
        if obj.ifc_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.ifc_file.url)
        return None


class BuildingPlanSerializer(serializers.ModelSerializer):
    """
    Serializer completo para BuildingPlan.
    Inclui todos os campos e metadados quando solicitado.
    """
    
    ifc_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    has_metadata = serializers.SerializerMethodField()
    
    class Meta:
        model = BuildingPlan
        fields = [
            'id',
            'name',
            'description',
            'ifc_url',
            'uploaded_at',
            'is_active',
            'file_size',
            'metadata',
            'metadata_updated_at',
            'has_metadata'
        ]
        read_only_fields = ['uploaded_at', 'metadata_updated_at']
    
    def get_ifc_url(self, obj):
        """Retorna URL absoluta do arquivo IFC."""
        if obj.ifc_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.ifc_file.url)
        return None
    
    def get_file_size(self, obj):
        """Retorna tamanho do arquivo formatado."""
        return obj.get_file_size()
    
    def get_metadata(self, obj):
        """
        Retorna metadados apenas se solicitado no contexto.
        Isso evita processamento desnecessário em listagens.
        """
        include_metadata = self.context.get('include_metadata', False)
        if include_metadata:
            return obj.get_metadata()
        return None
    
    def get_has_metadata(self, obj):
        """Indica se a planta tem metadados em cache."""
        return obj.metadata is not None


class BuildingPlanCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de novas plantas.
    """
    
    class Meta:
        model = BuildingPlan
        fields = [
            'name',
            'description',
            'ifc_file',
            'is_active'
        ]
    
    def validate_ifc_file(self, value):
        """
        Valida o arquivo IFC enviado.
        """
        if value:
            # Verificar extensão
            if not value.name.lower().endswith('.ifc'):
                raise serializers.ValidationError("O arquivo deve ter extensão .ifc")
            
            # Verificar tamanho (máximo 100MB)
            max_size = 100 * 1024 * 1024  # 100MB
            if value.size > max_size:
                raise serializers.ValidationError(
                    f"O arquivo é muito grande. Tamanho máximo: 100MB"
                )
        
        return value


class ElementPropertiesSerializer(serializers.Serializer):
    """
    Serializer para propriedades de elementos IFC.
    Não vinculado a modelo, apenas para estruturação de dados.
    """
    
    id = serializers.IntegerField()
    global_id = serializers.CharField()
    name = serializers.CharField(allow_blank=True)
    type = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    properties = serializers.DictField(required=False)
    material = serializers.CharField(required=False, allow_blank=True)


class SpatialStructureSerializer(serializers.Serializer):
    """
    Serializer para estrutura espacial hierárquica.
    """
    
    id = serializers.IntegerField()
    global_id = serializers.CharField()
    name = serializers.CharField()
    type = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    children = serializers.ListField(required=False)


class StatisticsSerializer(serializers.Serializer):
    """
    Serializer para estatísticas do modelo IFC.
    """
    
    total_elements = serializers.IntegerField()
    total_with_geometry = serializers.IntegerField(required=False)
    elements_by_type = serializers.DictField()
    total_types = serializers.IntegerField()
    schema = serializers.CharField()
    total_properties = serializers.IntegerField(required=False)


class BoundsSerializer(serializers.Serializer):
    """
    Serializer para limites (bounding box) do modelo.
    """
    
    min = serializers.DictField()
    max = serializers.DictField()
    center = serializers.DictField()
    size = serializers.DictField()

