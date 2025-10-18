# Script PowerShell para remover a seção databases: do render.yaml
# Use este script se o banco ifc-database JÁ EXISTE no Render

Write-Host "🔧 Removendo seção 'databases:' do render.yaml..." -ForegroundColor Cyan

$renderFile = "render.yaml"

if (Test-Path $renderFile) {
    # Fazer backup
    $backupFile = "render.yaml.backup"
    Copy-Item $renderFile $backupFile
    Write-Host "✅ Backup criado: $backupFile" -ForegroundColor Green
    
    # Ler arquivo
    $content = Get-Content $renderFile -Raw
    
    # Remover seção databases usando regex
    $pattern = "(?ms)^# ⚠️ IMPORTANTE:.*?databases:.*?user: ifc_user\s*$"
    $newContent = $content -replace $pattern, ""
    
    # Salvar
    $newContent | Set-Content $renderFile -NoNewline
    
    Write-Host "✅ Seção 'databases:' removida com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
    Write-Host "  1. Verificar arquivo render.yaml" -ForegroundColor White
    Write-Host "  2. git add render.yaml" -ForegroundColor White
    Write-Host "  3. git commit -m 'Usar banco existente ifc-database'" -ForegroundColor White
    Write-Host "  4. git push origin main" -ForegroundColor White
    Write-Host ""
    Write-Host "💾 Backup disponível em: $backupFile" -ForegroundColor Gray
} else {
    Write-Host "❌ Arquivo render.yaml não encontrado!" -ForegroundColor Red
}

