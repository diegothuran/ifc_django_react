"""
Testes para validators do plant_viewer.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from plant_viewer.models import validate_ifc_file_size, validate_ifc_content


class IFCValidatorTests(TestCase):
    """Testes para os validators de arquivos IFC."""
    
    def test_validate_ifc_file_size_valid(self):
        """Testa validação de tamanho com arquivo válido."""
        # Arquivo de 1MB (válido)
        content = b'x' * (1024 * 1024)
        file = SimpleUploadedFile("test.ifc", content)
        
        try:
            validate_ifc_file_size(file)
        except ValidationError:
            self.fail("Arquivo válido não deveria gerar erro")
    
    def test_validate_ifc_file_size_too_large(self):
        """Testa validação de tamanho com arquivo muito grande."""
        # Arquivo de 101MB (inválido)
        content = b'x' * (101 * 1024 * 1024)
        file = SimpleUploadedFile("test.ifc", content)
        
        with self.assertRaises(ValidationError) as cm:
            validate_ifc_file_size(file)
        
        self.assertIn('muito grande', str(cm.exception))
    
    def test_validate_ifc_content_valid(self):
        """Testa validação de conteúdo com arquivo IFC válido."""
        # Conteúdo IFC válido básico
        content = b'''ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
FILE_NAME('test.ifc','2024-01-01T00:00:00',('Author'),('Organization'),'PreProc','Application','');
FILE_SCHEMA(('IFC2X3'));
ENDSEC;
DATA;
ENDSEC;
END-ISO-10303-21;
'''
        file = SimpleUploadedFile("test.ifc", content)
        
        try:
            validate_ifc_content(file)
        except ValidationError:
            self.fail("Arquivo IFC válido não deveria gerar erro")
    
    def test_validate_ifc_content_invalid_header(self):
        """Testa validação de conteúdo com header inválido."""
        content = b'NOT-A-VALID-IFC-FILE'
        file = SimpleUploadedFile("test.ifc", content)
        
        with self.assertRaises(ValidationError) as cm:
            validate_ifc_content(file)
        
        self.assertIn('ISO-10303-21', str(cm.exception))
    
    def test_validate_ifc_content_missing_sections(self):
        """Testa validação de conteúdo com seções faltando."""
        # IFC sem seção DATA
        content = b'ISO-10303-21;\nHEADER;\nENDSEC;\n'
        file = SimpleUploadedFile("test.ifc", content)
        
        with self.assertRaises(ValidationError) as cm:
            validate_ifc_content(file)
        
        self.assertIn('DATA', str(cm.exception))

