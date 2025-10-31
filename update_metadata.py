#!/usr/bin/env python
"""
Script para forçar atualização de metadados das plantas IFC.
Executa a extração completa de elementos usando o processador IFC atualizado.

Uso:
    python update_metadata.py [plant_id]
    
Se plant_id não for fornecido, atualiza todas as plantas ativas.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifc_monitoring.settings')
django.setup()

from plant_viewer.models import BuildingPlan
from django.utils import timezone


def update_plant_metadata(plant_id=None):
    """
    Atualiza metadados de uma planta específica ou todas as plantas.
    
    Args:
        plant_id: ID da planta (opcional)
    """
    if plant_id:
        # Atualizar planta específica
        try:
            plant = BuildingPlan.objects.get(id=plant_id)
            plants = [plant]
        except BuildingPlan.DoesNotExist:
            print(f"❌ Planta com ID {plant_id} não encontrada!")
            return
    else:
        # Atualizar todas as plantas ativas
        plants = BuildingPlan.objects.filter(is_active=True)
    
    print(f"🔄 Atualizando metadados de {len(plants)} planta(s)...\n")
    
    for plant in plants:
        print(f"📋 Planta: {plant.name} (ID: {plant.id})")
        print(f"   Arquivo: {plant.ifc_file.name if plant.ifc_file else 'N/A'}")
        
        if not plant.ifc_file:
            print(f"   ⚠️  Sem arquivo IFC\n")
            continue
        
        try:
            # Forçar atualização de metadados
            print(f"   🔍 Extraindo metadados...")
            metadata = plant.refresh_metadata()
            
            if metadata:
                # Mostrar estatísticas
                stats = metadata.get('statistics', {})
                elements = metadata.get('building_elements', {})
                
                total_elements = stats.get('total_elements', 0)
                total_extracted = sum(len(v) for v in elements.values())
                
                print(f"   ✅ Metadados atualizados com sucesso!")
                print(f"   📊 Estatísticas:")
                print(f"      - Total de elementos no IFC: {total_elements}")
                print(f"      - Elementos extraídos: {total_extracted}")
                print(f"      - Tipos de elementos: {len(elements)}")
                print(f"      - Schema IFC: {stats.get('schema', 'N/A')}")
                
                # Mostrar tipos de elementos extraídos
                if elements:
                    print(f"   📦 Tipos extraídos:")
                    for elem_type, elem_list in sorted(elements.items(), key=lambda x: len(x[1]), reverse=True):
                        print(f"      - {elem_type}: {len(elem_list)} elementos")
                
                print(f"   🕒 Atualizado em: {plant.metadata_updated_at}\n")
            else:
                print(f"   ❌ Falha ao extrair metadados\n")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}\n")


def main():
    """Função principal."""
    print("=" * 70)
    print("🔧 Atualização de Metadados IFC - Sistema Digital Twin")
    print("=" * 70)
    print()
    
    # Verificar argumentos
    plant_id = None
    if len(sys.argv) > 1:
        try:
            plant_id = int(sys.argv[1])
        except ValueError:
            print("❌ ID da planta deve ser um número inteiro!")
            sys.exit(1)
    
    # Executar atualização
    update_plant_metadata(plant_id)
    
    print("=" * 70)
    print("✅ Atualização concluída!")
    print("=" * 70)


if __name__ == '__main__':
    main()
