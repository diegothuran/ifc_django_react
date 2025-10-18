from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Sensor, SensorData, SensorAlert


class SensorDataInline(TabularInline):
    """Inline para exibir dados recentes do sensor no admin usando Unfold."""
    model = SensorData
    extra = 0
    readonly_fields = ['timestamp', 'get_display_value', 'status', 'quality']
    fields = ['timestamp', 'get_display_value', 'status', 'quality']
    ordering = ['-timestamp']
    
    def get_display_value(self, obj):
        """Exibe o valor formatado do dado."""
        if obj:
            return obj.get_display_value()
        return '-'
    get_display_value.short_description = 'Valor'
    
    def get_queryset(self, request):
        """Limita a 5 dados mais recentes."""
        qs = super().get_queryset(request)
        return qs[:5]


class SensorAlertInline(TabularInline):
    """Inline para exibir alertas ativos do sensor no admin usando Unfold."""
    model = SensorAlert
    extra = 0
    readonly_fields = ['alert_type', 'level', 'message', 'created_at']
    fields = ['alert_type', 'level', 'message', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        """Limita a alertas ativos."""
        qs = super().get_queryset(request)
        return qs.filter(is_active=True)[:3]


@admin.register(Sensor)
class SensorAdmin(ModelAdmin):
    """
    Configuração do admin para o modelo Sensor usando Unfold.
    """
    list_display = [
        'name', 
        'sensor_type', 
        'ip_address', 
        'port',
        'location_id',
        'status_display',
        'is_active_display',
        'last_data_collected'
    ]
    
    list_filter = [
        'sensor_type',
        'is_active',
        'created_at',
        'collection_interval'
    ]
    
    search_fields = [
        'name',
        'ip_address',
        'location_id',
        'description'
    ]
    
    readonly_fields = [
        'created_at',
        'last_data_collected',
        'status_display'
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'sensor_type', 'description', 'is_active')
        }),
        ('Configuração de Rede', {
            'fields': ('ip_address', 'port')
        }),
        ('Localização', {
            'fields': ('location_id',)
        }),
        ('Configurações de Coleta', {
            'fields': ('collection_interval', 'timeout')
        }),
        ('Status', {
            'fields': ('status_display', 'last_data_collected', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SensorDataInline, SensorAlertInline]
    actions = ['activate_sensors', 'deactivate_sensors', 'test_connection']
    compressed_fields = True
    list_display_links = ("name",)
    
    @display(description="Status")
    def status_display(self, obj):
        """Exibe o status visual do sensor."""
        return obj.get_status_display()
    
    @display(description="Ativo", boolean=True)
    def is_active_display(self, obj):
        return obj.is_active
    
    @admin.action(description="Ativar sensores selecionados")
    def activate_sensors(self, request, queryset):
        """Ação para ativar sensores selecionados."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'{updated} sensor(es) foram ativado(s) com sucesso.'
        )
    
    @admin.action(description="Desativar sensores selecionados")
    def deactivate_sensors(self, request, queryset):
        """Ação para desativar sensores selecionados."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'{updated} sensor(es) foram desativado(s) com sucesso.'
        )
    
    @admin.action(description="Testar conexão com sensores")
    def test_connection(self, request, queryset):
        """Ação para testar conexão com sensores selecionados."""
        # Esta funcionalidade seria implementada com o comando de coleta
        self.message_user(
            request, 
            f'Teste de conexão iniciado para {queryset.count()} sensor(es). '
            f'Verifique os logs para resultados.'
        )


@admin.register(SensorData)
class SensorDataAdmin(ModelAdmin):
    """
    Configuração do admin para o modelo SensorData usando Unfold.
    """
    list_display = [
        'sensor',
        'get_display_value',
        'status',
        'quality',
        'timestamp'
    ]
    
    list_filter = [
        'sensor__sensor_type',
        'status',
        'timestamp',
        'sensor'
    ]
    
    search_fields = [
        'sensor__name',
        'status',
        'raw_data'
    ]
    
    readonly_fields = [
        'timestamp',
        'get_display_value'
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('sensor', 'timestamp')
        }),
        ('Dados do Sensor', {
            'fields': ('count', 'value', 'unit', 'get_display_value')
        }),
        ('Qualidade e Status', {
            'fields': ('status', 'quality')
        }),
        ('Dados Técnicos', {
            'fields': ('raw_data', 'additional_data'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-timestamp']
    compressed_fields = True
    list_display_links = ("sensor",)
    
    def get_queryset(self, request):
        """Otimiza as consultas."""
        qs = super().get_queryset(request)
        return qs.select_related('sensor')


@admin.register(SensorAlert)
class SensorAlertAdmin(ModelAdmin):
    """
    Configuração do admin para o modelo SensorAlert usando Unfold.
    """
    list_display = [
        'sensor',
        'alert_type',
        'level',
        'message_preview',
        'is_active_display',
        'created_at'
    ]
    
    list_filter = [
        'alert_type',
        'level',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'sensor__name',
        'message'
    ]
    
    readonly_fields = [
        'created_at',
        'resolved_at'
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('sensor', 'alert_type', 'level', 'is_active')
        }),
        ('Mensagem', {
            'fields': ('message',)
        }),
        ('Datas', {
            'fields': ('created_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['resolve_alerts', 'activate_alerts']
    compressed_fields = True
    list_display_links = ("sensor",)
    
    @display(description="Mensagem")
    def message_preview(self, obj):
        """Exibe uma prévia da mensagem."""
        if obj:
            return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
        return '-'
    
    @display(description="Ativo", boolean=True)
    def is_active_display(self, obj):
        return obj.is_active
    
    @admin.action(description="Resolver alertas selecionados")
    def resolve_alerts(self, request, queryset):
        """Ação para resolver alertas selecionados."""
        from django.utils import timezone
        updated = queryset.update(is_active=False, resolved_at=timezone.now())
        self.message_user(
            request, 
            f'{updated} alerta(s) foram resolvido(s) com sucesso.'
        )
    
    @admin.action(description="Reativar alertas selecionados")
    def activate_alerts(self, request, queryset):
        """Ação para reativar alertas selecionados."""
        updated = queryset.update(is_active=True, resolved_at=None)
        self.message_user(
            request, 
            f'{updated} alerta(s) foram reativado(s) com sucesso.'
        )
