from django.apps import AppConfig


class SensorManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sensor_management'
    verbose_name = 'Sensor Management'
    
    def ready(self):
        """Configurações que devem ser executadas quando o app está pronto."""
        pass
