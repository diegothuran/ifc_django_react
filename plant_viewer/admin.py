from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import BuildingPlan


@admin.register(BuildingPlan)
class BuildingPlanAdmin(ModelAdmin):
    """
    Configuração do admin para o modelo BuildingPlan usando Unfold.
    Permite gerenciar plantas industriais através do Django Admin.
    """
    list_display = [
        'name', 
        'is_active_display', 
        'uploaded_at', 
        'get_file_size'
    ]
    
    list_filter = [
        'is_active',
        'uploaded_at',
    ]
    
    search_fields = [
        'name',
        'description'
    ]
    
    readonly_fields = [
        'uploaded_at',
        'get_file_size'
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Arquivo IFC', {
            'fields': ('ifc_file', 'get_file_size')
        }),
        ('Metadados', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_plans', 'deactivate_plans']
    compressed_fields = True
    list_display_links = ("name",)
    
    @display(description="Ativo", boolean=True)
    def is_active_display(self, obj):
        return obj.is_active
    
    @admin.action(description="Ativar plantas selecionadas")
    def activate_plans(self, request, queryset):
        """Ação para ativar plantas selecionadas."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'{updated} planta(s) foram ativada(s) com sucesso.'
        )
    
    @admin.action(description="Desativar plantas selecionadas")
    def deactivate_plans(self, request, queryset):
        """Ação para desativar plantas selecionadas."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'{updated} planta(s) foram desativada(s) com sucesso.'
        )
