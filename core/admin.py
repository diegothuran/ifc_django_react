from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User, Location, IFCFile


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Admin personalizado para User usando Unfold.
    Gerencia usuários do sistema com interface moderna.
    """
    pass


@admin.register(Location)
class LocationAdmin(ModelAdmin):
    """
    Admin para Location usando Unfold.
    Gerencia hierarquia de localizações (Prédio > Andar > Sala).
    """
    list_display = ('__str__', 'parent', 'children_count')
    search_fields = ('name',)
    list_filter = ('parent',)
    list_per_page = 25
    compressed_fields = True
    list_display_links = ("__str__",)
    
    def children_count(self, obj):
        """Mostra quantas localizações filhas existem."""
        return obj.children.count()
    children_count.short_description = "Sub-localizações"


@admin.register(IFCFile)
class IFCFileAdmin(ModelAdmin):
    """
    Admin para IFCFile (Legado) usando Unfold.
    
    NOTA: O modelo principal de plantas IFC está em plant_viewer.BuildingPlan
    Este admin é mantido para compatibilidade com arquivos antigos.
    """
    list_display = ('name', 'uploaded_at', 'uploaded_by')
    search_fields = ('name',)
    list_filter = ('uploaded_at',)
    readonly_fields = ('uploaded_at',)
    compressed_fields = True
    list_display_links = ("name",)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'file')
        }),
        ('Metadados', {
            'fields': ('uploaded_at', 'uploaded_by'),
            'classes': ('collapse',)
        }),
    )


# =============================================================================
# ADMIN PARA SENSORES MOVIDO PARA sensor_management
# =============================================================================
# 
# Os admins para Sensor, SensorData e SensorAlert foram MOVIDOS para:
#   sensor_management/admin.py
# 
# Para acessar:
#   /admin/sensor_management/sensor/
#   /admin/sensor_management/sensordata/
#   /admin/sensor_management/sensoralert/
# 
# Motivo: Consolidação em sensor_management para melhor organização
# =============================================================================

