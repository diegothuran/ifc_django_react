#!/usr/bin/env python
"""
Script para carregar arquivo IFC no banco de dados do projeto.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifc_monitoring.settings')
django.setup()

from django.core.files import File
from plant_viewer.models import BuildingPlan

def load_ifc_file(file_path, name=None, description=None):
    """
    Carrega um arquivo IFC no banco de dados.
    
    Args:
        file_path: Caminho para o arquivo IFC
        name: Nome da planta (opcional, usa nome do arquivo se não fornecido)
        description: Descrição da planta (opcional)
    """
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        print(f"❌ ERRO: Arquivo não encontrado: {file_path}")
        return False
    
    # Verificar extensão
    if not file_path.lower().endswith('.ifc'):
        print(f"❌ ERRO: Arquivo deve ter extensão .ifc")
        return False
    
    # Nome da planta
    if not name:
        name = Path(file_path).stem
    
    print(f"📁 Carregando arquivo IFC: {file_path}")
    print(f"📝 Nome da planta: {name}")
    
    try:
        # Verificar se já existe uma planta com este nome
        existing = BuildingPlan.objects.filter(name=name).first()
        if existing:
            response = input(f"⚠️  Já existe uma planta com o nome '{name}'. Deseja substituir? (s/n): ")
            if response.lower() != 's':
                print("❌ Operação cancelada.")
                return False
            print(f"🔄 Desativando planta anterior...")
            existing.is_active = False
            existing.save()
        
        # Criar nova planta
        plant = BuildingPlan(
            name=name,
            description=description or f"Planta importada de {os.path.basename(file_path)}",
            is_active=True
        )
        
        # Abrir e anexar arquivo
        with open(file_path, 'rb') as f:
            plant.ifc_file.save(os.path.basename(file_path), File(f), save=False)
        
        # Salvar no banco
        plant.save()
        
        print(f"✅ Planta criada com sucesso! ID: {plant.id}")
        print(f"📊 Tamanho do arquivo: {plant.get_file_size()}")
        
        # Extrair metadados
        print(f"🔍 Extraindo metadados do arquivo IFC...")
        metadata = plant.extract_metadata()
        
        if metadata:
            stats = metadata.get('statistics', {})
            print(f"✅ Metadados extraídos com sucesso!")
            print(f"   - Total de elementos: {stats.get('total_elements', 'N/A')}")
            print(f"   - Elementos com geometria: {stats.get('total_with_geometry', 'N/A')}")
            print(f"   - Schema IFC: {stats.get('schema', 'N/A')}")
            print(f"   - Tipos de elementos: {stats.get('total_types', 'N/A')}")
        else:
            print(f"⚠️  Não foi possível extrair metadados automaticamente.")
        
        print(f"\n🎉 Arquivo carregado com sucesso!")
        print(f"🌐 Acesse a visualização em: http://localhost:8000/plant/view/")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao carregar arquivo: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_current_plants():
    """Verifica plantas existentes no banco de dados."""
    print("=" * 60)
    print("📊 PLANTAS CADASTRADAS NO SISTEMA")
    print("=" * 60)
    
    plants = BuildingPlan.objects.all().order_by('-uploaded_at')
    
    if not plants.exists():
        print("❌ Nenhuma planta encontrada no banco de dados.")
        print("   Isso explica por que o sistema mostra o modelo de exemplo com 6 cubos.")
        return
    
    print(f"Total de plantas: {plants.count()}")
    print(f"Plantas ativas: {BuildingPlan.objects.filter(is_active=True).count()}")
    print("-" * 60)
    
    for plant in plants:
        status = "✅ ATIVO" if plant.is_active else "❌ INATIVO"
        print(f"\nID: {plant.id} | {status}")
        print(f"Nome: {plant.name}")
        print(f"Arquivo: {plant.ifc_file.name if plant.ifc_file else 'Sem arquivo'}")
        print(f"Tamanho: {plant.get_file_size()}")
        print(f"Upload: {plant.uploaded_at.strftime('%d/%m/%Y %H:%M')}")
        if plant.description:
            print(f"Descrição: {plant.description}")
    
    print("-" * 60)


if __name__ == '__main__':
    print("=" * 60)
    print("🏗️  SCRIPT DE CARREGAMENTO DE ARQUIVO IFC")
    print("=" * 60)
    print()
    
    # Verificar plantas atuais
    check_current_plants()
    print()
    
    # Perguntar se deseja carregar novo arquivo
    print("=" * 60)
    print("📁 CARREGAR NOVO ARQUIVO IFC")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Arquivo passado como argumento
        file_path = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else None
        description = sys.argv[3] if len(sys.argv) > 3 else None
        load_ifc_file(file_path, name, description)
    else:
        # Modo interativo
        response = input("\n🤔 Deseja carregar um novo arquivo IFC? (s/n): ")
        if response.lower() == 's':
            file_path = input("📁 Digite o caminho completo do arquivo IFC: ").strip().strip('"')
            name = input("📝 Digite o nome da planta (Enter para usar nome do arquivo): ").strip()
            description = input("📄 Digite a descrição (opcional, Enter para pular): ").strip()
            
            load_ifc_file(
                file_path,
                name if name else None,
                description if description else None
            )

