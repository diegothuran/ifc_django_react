"""
Testes para endpoints de health check.
"""

from django.test import TestCase, Client
from django.urls import reverse
import json


class HealthCheckTests(TestCase):
    """Testes para os endpoints de health check."""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check_basic(self):
        """Testa o endpoint básico de health check."""
        response = self.client.get(reverse('core:health'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('service', data)
    
    def test_health_check_detailed(self):
        """Testa o endpoint detalhado de health check."""
        response = self.client.get(reverse('core:health_detailed'))
        
        # Pode retornar 200 ou 503 dependendo do estado dos serviços
        self.assertIn(response.status_code, [200, 503])
        
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertIn('checks', data)
        self.assertIn('database', data['checks'])
        self.assertIn('cache', data['checks'])
    
    def test_readiness_check(self):
        """Testa o endpoint de readiness check."""
        response = self.client.get(reverse('core:readiness'))
        
        # Deve retornar 200 se o banco estiver pronto
        self.assertIn(response.status_code, [200, 503])
        
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
    
    def test_liveness_check(self):
        """Testa o endpoint de liveness check."""
        response = self.client.get(reverse('core:liveness'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'alive')
        self.assertIn('timestamp', data)

