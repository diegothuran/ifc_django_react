#!/usr/bin/env python
"""
Script para verificar se o projeto está pronto para deploy no Render.
"""

import os
import sys
from pathlib import Path

def check_file(file_path, description):
    """Verifica se um arquivo existe."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} NÃO ENCONTRADO: {file_path}")
        return False

def check_file_content(file_path, search_text, description):
    """Verifica se um arquivo contém determinado texto."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - NÃO ENCONTRADO")
                return False
    except Exception as e:
        print(f"❌ Erro ao ler {file_path}: {e}")
        return False

def main():
    print("🔍 Verificando configuração para deploy no Render...\n")
    
    issues = []
    
    # 1. Arquivos essenciais
    print("📁 Verificando arquivos essenciais...")
    if not check_file('render.yaml', 'Configuração Render'):
        issues.append("render.yaml não encontrado")
    if not check_file('build.sh', 'Script de build'):
        issues.append("build.sh não encontrado")
    if not check_file('start_simple.sh', 'Script de inicialização'):
        issues.append("start_simple.sh não encontrado")
    if not check_file('requirements.txt', 'Dependências'):
        issues.append("requirements.txt não encontrado")
    if not check_file('runtime.txt', 'Versão Python'):
        issues.append("runtime.txt não encontrado")
    if not check_file('manage.py', 'Django manage.py'):
        issues.append("manage.py não encontrado")
    
    print()
    
    # 2. Verificar conteúdo dos arquivos
    print("🔍 Verificando conteúdo dos arquivos...")
    
    if Path('requirements.txt').exists():
        check_file_content('requirements.txt', 'django', 'Django nas dependências')
        check_file_content('requirements.txt', 'gunicorn', 'Gunicorn nas dependências')
        check_file_content('requirements.txt', 'psycopg', 'psycopg nas dependências')
        check_file_content('requirements.txt', 'whitenoise', 'whitenoise nas dependências')
    
    if Path('runtime.txt').exists():
        check_file_content('runtime.txt', 'python-3', 'Versão Python especificada')
    
    if Path('render.yaml').exists():
        check_file_content('render.yaml', 'branch:', 'Branch especificada')
        check_file_content('render.yaml', 'DATABASE_URL', 'DATABASE_URL configurada')
    
    print()
    
    # 3. Verificar estrutura Django
    print("🏗️ Verificando estrutura Django...")
    check_file('ifc_monitoring/settings.py', 'Settings Django')
    check_file('ifc_monitoring/wsgi.py', 'WSGI Django')
    check_file('ifc_monitoring/urls.py', 'URLs Django')
    
    print()
    
    # 4. Verificar apps Django
    print("📦 Verificando apps Django...")
    check_file('core/models.py', 'App core')
    check_file('plant_viewer/models.py', 'App plant_viewer')
    check_file('sensor_management/models.py', 'App sensor_management')
    check_file('dashboard/models.py', 'App dashboard')
    
    print()
    
    # 5. Verificar static files
    print("🎨 Verificando arquivos estáticos...")
    if Path('static').exists():
        print("✅ Diretório static/ existe")
        if any(Path('static').iterdir()):
            print("✅ Diretório static/ tem conteúdo")
        else:
            print("⚠️ Diretório static/ está vazio")
    else:
        print("❌ Diretório static/ não encontrado")
        issues.append("Diretório static/ não encontrado")
    
    print()
    
    # Resumo
    print("=" * 60)
    if issues:
        print(f"\n❌ {len(issues)} PROBLEMA(S) ENCONTRADO(S):\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print("\n⚠️ CORRIJA OS PROBLEMAS ANTES DE FAZER DEPLOY!")
        return 1
    else:
        print("\n✅ TUDO OK! PROJETO PRONTO PARA DEPLOY!")
        print("\n📝 Próximos passos:")
        print("  1. git add .")
        print("  2. git commit -m 'Ready for Render deploy'")
        print("  3. git push origin master")
        print("  4. No Render: Sync Blueprint ou criar novo Web Service")
        return 0

if __name__ == '__main__':
    sys.exit(main())

