from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import ipaddress


def validate_sensor_ip(value):
    """
    Valida se o IP do sensor é válido e não está em ranges proibidos.
    """
    try:
        ip = ipaddress.ip_address(value)
        
        # Bloquear IPs de loopback em produção (exceto desenvolvimento local)
        if ip.is_loopback:
            # Permitir apenas em desenvolvimento (você pode adicionar uma verificação de DEBUG aqui)
            pass  # Comentário: permitir por enquanto para desenvolvimento
            
        # Bloquear IPs reservados/privados se necessário
        # if ip.is_reserved:
        #     raise ValidationError('Endereço IP reservado não é permitido.')
            
    except ValueError:
        raise ValidationError(f'{value} não é um endereço IP válido.')


class Sensor(models.Model):
    """
    Modelo para representar sensores IoT na planta industrial.
    Cada sensor tem um endereço IP e pode estar associado a um local específico
    no modelo 3D através do location_id.
    """
    
    SENSOR_TYPES = [
        ('counter', 'Contador'),
        ('temperature', 'Temperatura'),
        ('pressure', 'Pressão'),
        ('vibration', 'Vibração'),
        ('flow', 'Fluxo'),
        ('level', 'Nível'),
        ('other', 'Outro'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nome do Sensor",
        help_text="Nome descritivo do sensor (ex: 'Sensor Linha 1')"
    )
    
    sensor_type = models.CharField(
        max_length=20,
        choices=SENSOR_TYPES,
        default='counter',
        verbose_name="Tipo de Sensor",
        help_text="Tipo de sensor IoT"
    )
    
    ip_address = models.GenericIPAddressField(
        validators=[validate_sensor_ip],
        verbose_name="Endereço IP",
        help_text="Endereço IP do sensor na rede industrial"
    )
    
    port = models.PositiveIntegerField(
        default=80,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name="Porta",
        help_text="Porta de comunicação do sensor (1-65535)"
    )
    
    location_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="ID do Local",
        help_text="Identificador para associar o sensor a um local no modelo 3D (ExpressID do IFC)"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Define se o sensor está ativo e coletando dados"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada do sensor e sua função"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação",
        help_text="Data e hora em que o sensor foi cadastrado"
    )
    
    last_data_collected = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Última Coleta",
        help_text="Data e hora da última coleta de dados bem-sucedida"
    )
    
    # Configurações de coleta
    collection_interval = models.PositiveIntegerField(
        default=60,
        verbose_name="Intervalo de Coleta (segundos)",
        help_text="Intervalo em segundos entre coletas de dados"
    )
    
    timeout = models.PositiveIntegerField(
        default=10,
        verbose_name="Timeout (segundos)",
        help_text="Tempo limite para comunicação com o sensor"
    )
    
    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = "Sensores"
        ordering = ['name']
        unique_together = ['ip_address', 'port']
        indexes = [
            models.Index(fields=['is_active', '-last_data_collected']),
            models.Index(fields=['sensor_type', 'is_active']),
            models.Index(fields=['location_id']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.ip_address}:{self.port})"
    
    def get_status_display(self):
        """Retorna o status visual do sensor."""
        if not self.is_active:
            return "❌ Inativo"
        elif self.last_data_collected:
            # Verifica se a última coleta foi recente (dentro do intervalo + 30 segundos de tolerância)
            time_diff = timezone.now() - self.last_data_collected
            if time_diff.total_seconds() <= (self.collection_interval + 30):
                return "✅ Ativo"
            else:
                return "⚠️ Sem dados recentes"
        else:
            return "❓ Nunca coletado"


class SensorData(models.Model):
    """
    Modelo para armazenar dados coletados dos sensores.
    Cada entrada representa uma leitura específica de um sensor em um momento no tempo.
    """
    
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='data_readings',
        verbose_name="Sensor",
        help_text="Sensor que gerou este dado"
    )
    
    # Dados numéricos principais
    count = models.IntegerField(
        default=0,
        verbose_name="Contagem",
        help_text="Valor da contagem de objetos (para sensores de contagem)"
    )
    
    value = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Valor",
        help_text="Valor numérico do sensor (temperatura, pressão, etc.)"
    )
    
    unit = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Unidade",
        help_text="Unidade de medida do valor (ex: '°C', 'bar', 'rpm')"
    )
    
    # Dados de status e qualidade
    status = models.CharField(
        max_length=50,
        default='ok',
        verbose_name="Status",
        help_text="Status da leitura (ok, error, warning, etc.)"
    )
    
    quality = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Qualidade (%)",
        help_text="Qualidade da leitura em percentual (0-100%)"
    )
    
    # Metadados
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp",
        help_text="Data e hora em que o dado foi coletado"
    )
    
    raw_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Dados Brutos",
        help_text="Dados brutos recebidos do sensor em formato JSON"
    )
    
    # Dados adicionais específicos por tipo de sensor
    additional_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Dados Adicionais",
        help_text="Dados específicos do tipo de sensor (JSON)"
    )
    
    class Meta:
        verbose_name = "Dado do Sensor"
        verbose_name_plural = "Dados dos Sensores"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor', '-timestamp']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['sensor', '-timestamp', 'status']),
            models.Index(fields=['status', '-timestamp']),
        ]
    
    def __str__(self):
        sensor_name = self.sensor.name
        if self.sensor.sensor_type == 'counter':
            return f"{sensor_name}: {self.count} (at {self.timestamp.strftime('%H:%M:%S')})"
        elif self.value is not None:
            unit_str = f" {self.unit}" if self.unit else ""
            return f"{sensor_name}: {self.value}{unit_str} (at {self.timestamp.strftime('%H:%M:%S')})"
        else:
            return f"{sensor_name}: {self.status} (at {self.timestamp.strftime('%H:%M:%S')})"
    
    def get_display_value(self):
        """Retorna o valor principal para exibição."""
        if self.sensor.sensor_type == 'counter':
            return str(self.count)
        elif self.value is not None:
            unit_str = f" {self.unit}" if self.unit else ""
            return f"{self.value:.2f}{unit_str}"
        else:
            return self.status


class SensorAlert(models.Model):
    """
    Modelo para armazenar alertas gerados pelos sensores.
    """
    
    ALERT_TYPES = [
        ('threshold', 'Limite Atingido'),
        ('disconnection', 'Desconexão'),
        ('error', 'Erro de Comunicação'),
        ('maintenance', 'Manutenção Necessária'),
        ('other', 'Outro'),
    ]
    
    ALERT_LEVELS = [
        ('info', 'Informação'),
        ('warning', 'Aviso'),
        ('error', 'Erro'),
        ('critical', 'Crítico'),
    ]
    
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name="Sensor"
    )
    
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        verbose_name="Tipo de Alerta"
    )
    
    level = models.CharField(
        max_length=10,
        choices=ALERT_LEVELS,
        default='info',
        verbose_name="Nível do Alerta"
    )
    
    message = models.TextField(
        verbose_name="Mensagem",
        help_text="Mensagem descritiva do alerta"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Define se o alerta está ativo"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Resolução"
    )
    
    class Meta:
        verbose_name = "Alerta do Sensor"
        verbose_name_plural = "Alertas dos Sensores"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sensor', '-created_at']),
            models.Index(fields=['is_active', 'level', '-created_at']),
            models.Index(fields=['level', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sensor.name} - {self.get_level_display()}: {self.message[:50]}..."
