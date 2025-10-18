from django.apps import AppConfig


class PlantViewerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plant_viewer'
    verbose_name = 'Plant Viewer'
    
    def ready(self):
        """Configurações que devem ser executadas quando o app está pronto."""
        pass
