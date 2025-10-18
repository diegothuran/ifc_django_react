from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    verbose_name = 'Dashboard'
    
    def ready(self):
        """Configurações que devem ser executadas quando o app está pronto."""
        pass
