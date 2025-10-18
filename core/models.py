from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):
    """
    Modelo de usuário customizado.
    O Django já fornece campos como username, password, email, etc.
    """
    pass


class Location(models.Model):
    """
    Modelo para representar localizações hierárquicas.
    Exemplo: Prédio A > Andar 2 > Sala 101
    """
    name = models.CharField(
        max_length=100, 
        help_text="Ex: Prédio A, Andar 2, Sala 101"
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        help_text="Localização pai na hierarquia"
    )

    def clean(self):
        # Evita referência circular
        if self.parent and self.parent == self:
            raise ValidationError('Uma localização não pode ser pai de si mesma.')
        
        # Evita referência circular indireta
        if self.parent:
            current = self.parent
            while current:
                if current == self:
                    raise ValidationError('Referência circular detectada na hierarquia de localizações.')
                current = current.parent

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        path = [self.name]
        p = self.parent
        while p:
            path.insert(0, p.name)
            p = p.parent
        return ' / '.join(path)
    
    class Meta:
        verbose_name = "Localização"
        verbose_name_plural = "Localizações"
        ordering = ['name']


class IFCFile(models.Model):
    """
    Modelo para armazenar arquivos IFC uploadados.
    NOTA: O modelo principal de plantas IFC está em plant_viewer.BuildingPlan
    Este modelo é mantido para compatibilidade com código legado.
    """
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='ifc_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Arquivo IFC (Legado)"
        verbose_name_plural = "Arquivos IFC (Legado)"
        ordering = ['-uploaded_at']


# =============================================================================
# MODELOS MIGRADOS PARA sensor_management
# =============================================================================
# 
# Os modelos Sensor, SensorReading e Alert foram MOVIDOS para o app
# sensor_management para melhor organização e funcionalidades expandidas.
# 
# Se você precisa usar esses modelos, importe de:
#   from sensor_management.models import Sensor, SensorData, SensorAlert
# 
# Motivo da migração:
# - Modelo Sensor mais completo (IP, porta, location_id)
# - Melhor suporte para sensores IoT
# - Separação clara de responsabilidades
# - Evita duplicação de código
# 
# Para migrar dados antigos, execute:
#   python manage.py shell < migrate_to_sensor_management.py
# 
# =============================================================================

