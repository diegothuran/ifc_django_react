from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)


def validate_ifc_file_size(file):
    """
    Valida o tamanho do arquivo IFC.
    Limite: 100MB para evitar problemas de memória
    """
    max_size = 100 * 1024 * 1024  # 100 MB
    if file.size > max_size:
        raise ValidationError(f'Arquivo muito grande. Tamanho máximo permitido: 100 MB. Tamanho atual: {file.size / 1024 / 1024:.2f} MB')


def validate_ifc_content(file):
    """
    Valida o conteúdo básico do arquivo IFC.
    Verifica se o arquivo começa com o header IFC válido.
    """
    try:
        # Ler os primeiros 1024 bytes para verificar o header
        file.seek(0)
        content = file.read(1024).decode('utf-8', errors='ignore')
        file.seek(0)  # Reset file pointer
        
        # Verificar se contém header IFC válido
        if not content.startswith('ISO-10303-21'):
            raise ValidationError('Arquivo não é um arquivo IFC válido. Deve começar com ISO-10303-21.')
        
        # Verificar se contém seções obrigatórias
        required_sections = ['HEADER', 'DATA']
        for section in required_sections:
            if section not in content:
                raise ValidationError(f'Arquivo IFC inválido: seção {section} não encontrada.')
                
    except UnicodeDecodeError:
        raise ValidationError('Arquivo não é um arquivo IFC válido (erro de codificação).')
    except Exception as e:
        logger.error(f'Erro ao validar arquivo IFC: {e}')
        raise ValidationError('Erro ao validar arquivo IFC.')


class BuildingPlan(models.Model):
    """
    Modelo para representar planos de construção (arquivos IFC).
    Este modelo armazena informações sobre os arquivos de planta industrial
    que serão visualizados no visualizador 3D.
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Nome da Planta",
        help_text="Nome descritivo da planta industrial (ex: 'Planta Principal')"
    )
    
    ifc_file = models.FileField(
        upload_to='ifc_files/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(allowed_extensions=['ifc']),
            validate_ifc_file_size,
            validate_ifc_content
        ],
        verbose_name="Arquivo IFC",
        help_text="Arquivo IFC da planta industrial (.ifc) - Máximo 100 MB"
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Upload",
        help_text="Data e hora em que o arquivo foi enviado"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Descrição opcional da planta industrial"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Define se esta planta está ativa e disponível para visualização"
    )
    
    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Metadados IFC",
        help_text="Metadados extraídos do arquivo IFC (cache)"
    )
    
    metadata_updated_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Metadados Atualizados Em",
        help_text="Data da última extração de metadados"
    )
    
    class Meta:
        verbose_name = "Plano de Construção"
        verbose_name_plural = "Planos de Construção"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.name
    
    def get_file_size(self):
        """Retorna o tamanho do arquivo em formato legível."""
        if self.ifc_file:
            try:
                size = self.ifc_file.size
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
                return f"{size:.1f} TB"
            except (FileNotFoundError, OSError, ValueError):
                return "Arquivo não encontrado"
        return "N/A"
    
    def extract_metadata(self, force_update=False):
        """
        Extrai metadados do arquivo IFC.
        
        Args:
            force_update: Se True, força atualização mesmo se já existir cache
            
        Returns:
            dict: Metadados extraídos do IFC
        """
        from .ifc_processor import IFCProcessor
        
        # Verificar cache
        if self.metadata and not force_update:
            logger.info(f"Usando metadados em cache para planta {self.id}")
            return self.metadata
        
        if not self.ifc_file:
            logger.warning(f"Planta {self.id} não possui arquivo IFC")
            return {}
        
        try:
            logger.info(f"Extraindo metadados do IFC para planta {self.id}")
            processor = IFCProcessor(self.ifc_file.path)
            
            if not processor.open():
                logger.error(f"Falha ao abrir arquivo IFC da planta {self.id}")
                return {}
            
            metadata = {
                'project_info': processor.get_project_info(),
                'building_elements': processor.get_building_elements(),
                'spatial_structure': processor.get_spatial_structure(),
                'statistics': processor.get_statistics(),
                'bounds': processor.get_bounds()
            }
            
            # Salvar cache no banco
            self.metadata = metadata
            self.metadata_updated_at = timezone.now()
            self.save(update_fields=['metadata', 'metadata_updated_at'])
            
            logger.info(f"Metadados extraídos com sucesso para planta {self.id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Erro ao extrair metadados da planta {self.id}: {e}")
            return {}
    
    def get_metadata(self):
        """
        Retorna metadados (com cache).
        
        Returns:
            dict: Metadados do IFC
        """
        return self.extract_metadata(force_update=False)
    
    def refresh_metadata(self):
        """
        Força atualização dos metadados.
        
        Returns:
            dict: Metadados atualizados
        """
        return self.extract_metadata(force_update=True)
