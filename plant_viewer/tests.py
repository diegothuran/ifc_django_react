from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import BuildingPlan


class BuildingPlanModelTest(TestCase):
    """Testes para o modelo BuildingPlan."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.plant = BuildingPlan.objects.create(
            name="Test Plant",
            description="Test Description"
        )
    
    def test_plant_creation(self):
        """Testa a criação de uma planta."""
        self.assertEqual(self.plant.name, "Test Plant")
        self.assertEqual(self.plant.description, "Test Description")
        self.assertTrue(self.plant.is_active)
        self.assertIsNotNone(self.plant.uploaded_at)
    
    def test_plant_str_representation(self):
        """Testa a representação string do modelo."""
        self.assertEqual(str(self.plant), "Test Plant")


class PlantViewerViewsTest(TestCase):
    """Testes para as views do plant_viewer."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        self.plant = BuildingPlan.objects.create(
            name="Test Plant",
            is_active=True
        )
    
    def test_main_plant_view(self):
        """Testa a view principal da planta."""
        response = self.client.get(reverse('plant_viewer:main_plant_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.plant.name)
    
    def test_plant_list_view(self):
        """Testa a view de lista de plantas."""
        response = self.client.get(reverse('plant_viewer:plant_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('plants', response.context)
    
    def test_plant_detail_view(self):
        """Testa a view de detalhes da planta."""
        response = self.client.get(reverse('plant_viewer:plant_detail', args=[self.plant.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['plant'], self.plant)
    
    def test_plant_data_api(self):
        """Testa a API de dados da planta."""
        response = self.client.get(reverse('plant_viewer:plant_data_api', args=[self.plant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
