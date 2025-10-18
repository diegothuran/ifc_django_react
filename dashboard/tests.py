from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from plant_viewer.models import BuildingPlan
from sensor_management.models import Sensor, SensorData, SensorAlert


class DashboardViewsTest(TestCase):
    """Testes para as views do dashboard."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        # Criar usuários
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            password='user123'
        )
        
        # Criar dados de teste
        self.plant = BuildingPlan.objects.create(
            name="Test Plant",
            is_active=True
        )
        
        self.sensor = Sensor.objects.create(
            name="Test Sensor",
            ip_address="192.168.1.100",
            is_active=True
        )
        
        # Criar alguns dados de sensor
        for i in range(5):
            SensorData.objects.create(
                sensor=self.sensor,
                count=i * 10,
                status='ok',
                quality=95.0
            )
    
    def test_public_dashboard_view(self):
        """Testa a view do dashboard público."""
        response = self.client.get(reverse('dashboard:public_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('plant', response.context)
        self.assertIn('sensor_summaries', response.context)
    
    def test_user_dashboard_view_authenticated(self):
        """Testa a view do dashboard do usuário autenticado."""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('dashboard:user_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('sensor_summaries', response.context)
    
    def test_user_dashboard_view_not_authenticated(self):
        """Testa que usuários não autenticados são redirecionados."""
        response = self.client.get(reverse('dashboard:user_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_dashboard_view_staff(self):
        """Testa a view do dashboard admin para staff."""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_sensors', response.context)
        self.assertIn('hourly_data', response.context)
    
    def test_admin_dashboard_view_non_staff(self):
        """Testa que usuários não-staff não podem acessar dashboard admin."""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_dashboard_data_api(self):
        """Testa a API de dados do dashboard."""
        response = self.client.get(
            reverse('dashboard:dashboard_data_api'),
            {'type': 'summary', 'hours': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('active_sensors', data)
        self.assertIn('timestamp', data)
    
    def test_dashboard_data_api_invalid_request(self):
        """Testa a API com requisição inválida (não AJAX)."""
        response = self.client.get(reverse('dashboard:dashboard_data_api'))
        self.assertEqual(response.status_code, 400)
    
    def test_plant_data_api(self):
        """Testa a API de dados da planta."""
        response = self.client.get(reverse('dashboard:plant_data_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('plant', data)
        self.assertIn('sensors', data)
        self.assertEqual(data['plant']['name'], self.plant.name)
    
    def test_plant_data_api_no_plant(self):
        """Testa a API quando não há planta ativa."""
        self.plant.is_active = False
        self.plant.save()
        
        response = self.client.get(reverse('dashboard:plant_data_api'))
        self.assertEqual(response.status_code, 404)


class DashboardContextTest(TestCase):
    """Testes para o contexto dos dashboards."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        # Criar dados de teste
        self.plant = BuildingPlan.objects.create(
            name="Test Plant",
            is_active=True
        )
        
        self.sensor1 = Sensor.objects.create(
            name="Sensor 1",
            ip_address="192.168.1.100",
            is_active=True
        )
        
        self.sensor2 = Sensor.objects.create(
            name="Sensor 2",
            ip_address="192.168.1.101",
            is_active=True
        )
        
        # Criar alerta
        self.alert = SensorAlert.objects.create(
            sensor=self.sensor1,
            alert_type='threshold',
            level='warning',
            message='Test alert'
        )
    
    def test_public_dashboard_context(self):
        """Testa o contexto do dashboard público."""
        response = self.client.get(reverse('dashboard:public_dashboard'))
        
        context = response.context
        self.assertIn('total_active_sensors', context)
        self.assertIn('online_sensors', context)
        self.assertIn('critical_alerts', context)
        self.assertEqual(context['total_active_sensors'], 2)
    
    def test_admin_dashboard_context(self):
        """Testa o contexto do dashboard admin."""
        admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
        
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        
        context = response.context
        self.assertIn('total_sensors', context)
        self.assertIn('active_sensors', context)
        self.assertIn('sensors_by_type', context)
        self.assertIn('hourly_data', context)
        self.assertEqual(context['total_sensors'], 2)
        self.assertEqual(context['active_sensors'], 2)
