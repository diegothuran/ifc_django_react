from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from plant_viewer.models import BuildingPlan
import os


class Command(BaseCommand):
    help = 'Remove registros de plantas com arquivos IFC que não existem mais no sistema de arquivos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra quais registros seriam removidos sem realmente removê-los',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Verificando arquivos IFC...')
        
        plants_with_missing_files = []
        total_plants = BuildingPlan.objects.count()
        
        for plant in BuildingPlan.objects.all():
            if plant.ifc_file:
                try:
                    # Verificar se o arquivo existe
                    if default_storage.exists(plant.ifc_file.name):
                        self.stdout.write(f'✓ {plant.name}: Arquivo encontrado')
                    else:
                        plants_with_missing_files.append(plant)
                        self.stdout.write(f'✗ {plant.name}: Arquivo não encontrado - {plant.ifc_file.name}')
                except Exception as e:
                    plants_with_missing_files.append(plant)
                    self.stdout.write(f'✗ {plant.name}: Erro ao verificar arquivo - {e}')
            else:
                self.stdout.write(f'⚠ {plant.name}: Sem arquivo IFC')
        
        if plants_with_missing_files:
            self.stdout.write(f'\nEncontrados {len(plants_with_missing_files)} registros com arquivos ausentes:')
            
            for plant in plants_with_missing_files:
                self.stdout.write(f'  - {plant.name} (ID: {plant.id})')
                if plant.ifc_file:
                    self.stdout.write(f'    Arquivo: {plant.ifc_file.name}')
            
            if dry_run:
                self.stdout.write('\n[DRY RUN] Nenhum registro foi removido.')
                self.stdout.write('Execute sem --dry-run para remover os registros.')
            else:
                # Remover registros
                count = 0
                for plant in plants_with_missing_files:
                    plant_name = plant.name
                    plant.delete()
                    count += 1
                    self.stdout.write(f'Removido: {plant_name}')
                
                self.stdout.write(f'\n{count} registros removidos com sucesso.')
        else:
            self.stdout.write('\n✓ Todos os arquivos IFC estão presentes.')
        
        self.stdout.write(f'\nTotal de plantas verificadas: {total_plants}')
        self.stdout.write('Limpeza concluída.')
