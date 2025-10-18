from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Sensor, SensorData, SensorAlert


class SensorModelTest(TestCase):
    """Testes para o modelo Sensor."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.sensor = Sensor.objects.create(
            name="Test Sensor",
            sensor_type="counter",
            ip_address="192.168.1.100",
            port=80,
            location_id="IFC_001",
            description="Sensor de teste"
        )
    
    def test_sensor_creation(self):
        """Testa a criação de um sensor."""
        self.assertEqual(self.sensor.name, "Test Sensor")
        self.assertEqual(self.sensor.sensor_type, "counter")
        self.assertEqual(self.sensor.ip_address, "192.168.1.100")
        self.assertTrue(self.sensor.is_active)
        self.assertIsNotNone(self.sensor.created_at)
    
    def test_sensor_str_representation(self):
        """Testa a representação string do modelo."""
        expected = "Test Sensor (192.168.1.100:80)"
        self.assertEqual(str(self.sensor), expected)
    
    def test_sensor_status_display(self):
        """Testa o status do sensor."""
        # Sensor sem dados
        status = self.sensor.get_status_display()
        self.assertIn("Nunca coletado", status)


class SensorDataModelTest(TestCase):
    """Testes para o modelo SensorData."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.sensor = Sensor.objects.create(
            name="Test Sensor",
            ip_address="192.168.1.100"
        )
        
        self.sensor_data = SensorData.objects.create(
            sensor=self.sensor,
            count=100,
            status='ok',
            quality=95.0
        )
    
    def test_sensor_data_creation(self):
        """Testa a criação de dados de sensor."""
        self.assertEqual(self.sensor_data.sensor, self.sensor)
        self.assertEqual(self.sensor_data.count, 100)
        self.assertEqual(self.sensor_data.status, 'ok')
        self.assertEqual(self.sensor_data.quality, 95.0)
        self.assertIsNotNone(self.sensor_data.timestamp)
    
    def test_sensor_data_display_value(self):
        """Testa o valor de exibição dos dados."""
        # Para sensor tipo counter
        self.sensor.sensor_type = 'counter'
        self.sensor.save()
        
        display_value = self.sensor_data.get_display_value()
        self.assertEqual(display_value, "100")
    
    def test_sensor_data_with_value(self):
        """Testa dados com valor numérico."""
        sensor_data = SensorData.objects.create(
            sensor=self.sensor,
            value=25.5,
            unit='°C',
            status='ok'
        )
        
        self.sensor.sensor_type = 'temperature'
        self.sensor.save()
        
        display_value = sensor_data.get_display_value()
        self.assertEqual(display_value, "25.50 °C")


class SensorAlertModelTest(TestCase):
    """Testes para o modelo SensorAlert."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.sensor = Sensor.objects.create(
            name="Test Sensor",
            ip_address="192.168.1.100"
        )
        
        self.alert = SensorAlert.objects.create(
            sensor=self.sensor,
            alert_type='threshold',
            level='warning',
            message='Limite de temperatura atingido'
        )
    
    def test_alert_creation(self):
        """Testa a criação de um alerta."""
        self.assertEqual(self.alert.sensor, self.sensor)
        self.assertEqual(self.alert.alert_type, 'threshold')
        self.assertEqual(self.alert.level, 'warning')
        self.assertTrue(self.alert.is_active)
        self.assertIsNotNone(self.alert.created_at)


class SensorManagementViewsTest(TestCase):
    """Testes para as views do sensor_management."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        self.sensor = Sensor.objects.create(
            name="Test Sensor",
            ip_address="192.168.1.100"
        )
        
        # Criar alguns dados de teste
        for i in range(5):
            SensorData.objects.create(
                sensor=self.sensor,
                count=i * 10,
                status='ok'
            )
    
    def test_sensor_list_view(self):
        """Testa a view de lista de sensores."""
        response = self.client.get(reverse('sensor_management:sensor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('sensors', response.context)
        self.assertIn('total_sensors', response.context)
    
    def test_sensor_detail_view(self):
        """Testa a view de detalhes do sensor."""
        response = self.client.get(reverse('sensor_management:sensor_detail', args=[self.sensor.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['sensor'], self.sensor)
        self.assertIn('recent_data', response.context)
    
    def test_sensor_data_api(self):
        """Testa a API de dados do sensor."""
        response = self.client.get(reverse('sensor_management:sensor_data_api', args=[self.sensor.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('sensor', data)
        self.assertIn('data', data)
        self.assertEqual(data['sensor']['id'], self.sensor.id)
    
    def test_all_sensors_data_api(self):
        """Testa a API de todos os sensores."""
        response = self.client.get(reverse('sensor_management:all_sensors_data_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('sensors', data)
        self.assertIn('timestamp', data)
    
    def test_sensor_dashboard_view(self):
        """Testa a view do dashboard de sensores."""
        response = self.client.get(reverse('sensor_management:sensor_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_sensors', response.context)
        self.assertIn('active_sensors', response.context)
