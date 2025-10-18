"""
Management command para converter arquivos IFC para glTF.

Uso:
    python manage.py convert_ifc_to_gltf                    # Converte todas as plantas ativas
    python manage.py convert_ifc_to_gltf --plant-id 1       # Converte planta específica
    python manage.py convert_ifc_to_gltf --force            # Força reconversão mesmo se já existe

Nota: Esta é uma implementação básica. Para produção, considere usar:
    - IfcConvert (parte do IfcOpenShell)
    - BlenderBIM (Blender plugin)
    - Serviços de conversão especializados
"""

from django.core.management.base import BaseCommand, CommandError
from plant_viewer.models import BuildingPlan
import os
import subprocess
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Converte arquivos IFC para glTF para melhor performance na visualização web'

    def add_arguments(self, parser):
        parser.add_argument(
            '--plant-id',
            type=int,
            help='ID específico da planta para converter'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força reconversão mesmo se arquivo glTF já existe'
        )
        
        parser.add_argument(
            '--method',
            type=str,
            default='ifcconvert',
            choices=['ifcconvert', 'blender', 'manual'],
            help='Método de conversão a usar'
        )

    def handle(self, *args, **options):
        plant_id = options.get('plant_id')
        force = options.get('force', False)
        method = options.get('method', 'ifcconvert')
        
        # Filtrar plantas
        if plant_id:
            plants = BuildingPlan.objects.filter(id=plant_id)
            if not plants.exists():
                raise CommandError(f'Planta com ID {plant_id} não encontrada')
        else:
            plants = BuildingPlan.objects.filter(is_active=True)
        
        if not plants.exists():
            self.stdout.write(self.style.WARNING('Nenhuma planta encontrada para converter'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n🔄 Iniciando conversão de {plants.count()} planta(s)...\n'))
        
        success_count = 0
        error_count = 0
        
        for plant in plants:
            self.stdout.write(f'Processando: {plant.name} (ID: {plant.id})')
            
            try:
                result = self.convert_plant(plant, force=force, method=method)
                if result:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {plant.name} convertido com sucesso'))
                    success_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  ⊘ {plant.name} pulado (já existe glTF)'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Erro ao converter {plant.name}: {e}'))
                logger.error(f'Erro ao converter planta {plant.id}: {e}', exc_info=True)
                error_count += 1
        
        # Resumo
        self.stdout.write(self.style.SUCCESS(f'\n📊 Resumo da conversão:'))
        self.stdout.write(f'  ✓ Sucesso: {success_count}')
        self.stdout.write(f'  ✗ Erros: {error_count}')
        self.stdout.write(f'  ⊘ Pulados: {plants.count() - success_count - error_count}')
    
    def convert_plant(self, plant, force=False, method='ifcconvert'):
        """
        Converte um arquivo IFC para glTF.
        
        Args:
            plant: BuildingPlan instance
            force: Se True, reconverte mesmo se já existe
            method: Método de conversão ('ifcconvert', 'blender', 'manual')
            
        Returns:
            bool: True se converteu, False se pulou
            
        Raises:
            Exception: Se houver erro na conversão
        """
        if not plant.ifc_file:
            raise ValueError("Planta não possui arquivo IFC")
        
        # Verificar se arquivo IFC existe
        if not os.path.exists(plant.ifc_file.path):
            raise FileNotFoundError(f"Arquivo IFC não encontrado: {plant.ifc_file.path}")
        
        # Definir caminho do arquivo glTF
        ifc_path = plant.ifc_file.path
        gltf_path = ifc_path.rsplit('.', 1)[0] + '.gltf'
        
        # Verificar se já existe
        if os.path.exists(gltf_path) and not force:
            return False
        
        # Converter baseado no método
        if method == 'ifcconvert':
            return self.convert_with_ifcconvert(ifc_path, gltf_path)
        elif method == 'blender':
            return self.convert_with_blender(ifc_path, gltf_path)
        elif method == 'manual':
            return self.convert_manual(ifc_path, gltf_path)
        
        return False
    
    def convert_with_ifcconvert(self, ifc_path, gltf_path):
        """
        Converte usando IfcConvert (parte do IfcOpenShell).
        
        Requer: IfcConvert instalado e disponível no PATH
        Download: http://ifcopenshell.org/ifcconvert
        """
        self.stdout.write('  Método: IfcConvert')
        
        # Verificar se IfcConvert está disponível
        try:
            result = subprocess.run(
                ['IfcConvert', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise FileNotFoundError('IfcConvert não encontrado')
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.stdout.write(self.style.WARNING(
                '  ⚠ IfcConvert não encontrado. Instale de: http://ifcopenshell.org/ifcconvert'
            ))
            return False
        
        # Executar conversão
        try:
            cmd = ['IfcConvert', '-y', '--use-world-coords', ifc_path, gltf_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0 and os.path.exists(gltf_path):
                return True
            else:
                raise RuntimeError(f'IfcConvert falhou: {result.stderr}')
        except subprocess.TimeoutExpired:
            raise RuntimeError('Conversão excedeu timeout de 5 minutos')
    
    def convert_with_blender(self, ifc_path, gltf_path):
        """
        Converte usando Blender com BlenderBIM addon.
        
        Requer: 
            - Blender instalado
            - BlenderBIM addon instalado
        """
        self.stdout.write('  Método: Blender + BlenderBIM')
        
        # Script Python para Blender
        blender_script = f'''
import bpy
import sys

# Limpar cena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Importar IFC
try:
    bpy.ops.bim.load_project(filepath="{ifc_path}")
except:
    print("ERROR: Failed to load IFC file")
    sys.exit(1)

# Exportar glTF
try:
    bpy.ops.export_scene.gltf(
        filepath="{gltf_path}",
        export_format='GLTF_SEPARATE'
    )
    print("SUCCESS: glTF exported")
except Exception as e:
    print(f"ERROR: Failed to export glTF: {{e}}")
    sys.exit(1)
'''
        
        # Verificar se Blender está disponível
        try:
            result = subprocess.run(
                ['blender', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise FileNotFoundError('Blender não encontrado')
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.stdout.write(self.style.WARNING(
                '  ⚠ Blender não encontrado. Instale de: https://www.blender.org/'
            ))
            return False
        
        # Salvar script temporário
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(blender_script)
            script_path = f.name
        
        try:
            # Executar Blender em modo background
            cmd = ['blender', '--background', '--python', script_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos timeout
            )
            
            if 'SUCCESS' in result.stdout and os.path.exists(gltf_path):
                return True
            else:
                raise RuntimeError(f'Blender conversion failed: {result.stdout}')
        except subprocess.TimeoutExpired:
            raise RuntimeError('Conversão excedeu timeout de 10 minutos')
        finally:
            # Limpar arquivo temporário
            try:
                os.unlink(script_path)
            except:
                pass
    
    def convert_manual(self, ifc_path, gltf_path):
        """
        Conversão manual usando IfcOpenShell Python (limitado).
        
        Esta é uma implementação básica que extrai geometrias e cria
        um arquivo glTF simples. Para produção, use IfcConvert ou Blender.
        """
        self.stdout.write('  Método: Manual (IfcOpenShell Python)')
        self.stdout.write(self.style.WARNING(
            '  ⚠ Conversão manual é limitada. Recomenda-se usar IfcConvert ou Blender.'
        ))
        
        try:
            import ifcopenshell
            import ifcopenshell.geom
            import json
        except ImportError:
            raise ImportError('IfcOpenShell não instalado. Instale: pip install ifcopenshell')
        
        # Abrir arquivo IFC
        ifc_file = ifcopenshell.open(ifc_path)
        
        # Configurar settings de geometria
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)
        
        # Estrutura básica do glTF
        gltf = {
            "asset": {
                "version": "2.0",
                "generator": "IFC Django Converter"
            },
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [],
            "meshes": [],
            "buffers": [],
            "bufferViews": [],
            "accessors": []
        }
        
        # Esta é uma implementação muito simplificada
        # Para produção, use bibliotecas especializadas
        
        self.stdout.write(self.style.WARNING(
            '  ⚠ Implementação manual não está completa. '
            'Use --method=ifcconvert ou --method=blender'
        ))
        
        return False

