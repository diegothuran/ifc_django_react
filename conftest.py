"""
Configuração pytest para o projeto.
Define fixtures globais e configurações de teste.
"""

import pytest
from django.conf import settings
import os


@pytest.fixture(scope='session')
def django_db_setup():
    """Configuração do banco de dados para testes."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('TEST_DB_NAME', 'test_db'),
        'USER': os.getenv('TEST_DB_USER', 'postgres'),
        'PASSWORD': os.getenv('TEST_DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('TEST_DB_HOST', 'localhost'),
        'PORT': os.getenv('TEST_DB_PORT', '5432'),
    }


@pytest.fixture
def api_client():
    """Fixture para cliente da API REST."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(django_user_model):
    """Fixture para cliente da API autenticado."""
    from rest_framework.test import APIClient
    client = APIClient()
    user = django_user_model.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def sample_sensor(db):
    """Fixture para criar um sensor de teste."""
    from sensor_management.models import Sensor
    return Sensor.objects.create(
        name='Test Sensor',
        sensor_type='temperature',
        ip_address='192.168.1.100',
        port=80,
        location_id='TEST_001'
    )


@pytest.fixture
def sample_building_plan(db):
    """Fixture para criar uma planta de teste."""
    from plant_viewer.models import BuildingPlan
    return BuildingPlan.objects.create(
        name='Test Building',
        description='Test building plan',
        is_active=True
    )

