@echo off
chcp 65001 >nul
echo ================================================================
echo 🏗️  CARREGADOR DE ARQUIVO IFC - Digital Twin Project
echo ================================================================
echo.

REM Verificar se Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não encontrado!
    echo.
    echo Por favor, instale o Python ou adicione ao PATH.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Executar script Python
echo ✅ Python encontrado! Executando script...
echo.

python load_ifc_file.py %*

echo.
echo ================================================================
pause

