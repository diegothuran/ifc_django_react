# Script PowerShell para limpar comentários do render.yaml
# Use este script se o banco ifc-database NÃO EXISTE ainda

Write-Host "🔧 Limpando comentários do render.yaml..." -ForegroundColor Cyan

$renderFile = "render.yaml"

if (Test-Path $renderFile) {
    # Fazer backup
    $backupFile = "render.yaml.backup"
    Copy-Item $renderFile $backupFile
    Write-Host "✅ Backup criado: $backupFile" -ForegroundColor Green
    
    # Ler arquivo
    $content = Get-Content $renderFile -Raw
    
    # Remover apenas os comentários de warning
    $pattern = "(?ms)^# ⚠️ IMPORTANTE:.*?\n# MANTENHA a seção 'databases:' para criar o banco\.\n\n"
    $newContent = $content -replace $pattern, ""
    
    # Salvar
    $newContent | Set-Content $renderFile -NoNewline
    
    Write-Host "✅ Comentários removidos! Seção 'databases:' mantida." -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
    Write-Host "  1. Verificar arquivo render.yaml" -ForegroundColor White
    Write-Host "  2. git add render.yaml" -ForegroundColor White
    Write-Host "  3. git commit -m 'Criar banco ifc-database no deploy'" -ForegroundColor White
    Write-Host "  4. git push origin main" -ForegroundColor White
    Write-Host ""
    Write-Host "💾 Backup disponível em: $backupFile" -ForegroundColor Gray
} else {
    Write-Host "❌ Arquivo render.yaml não encontrado!" -ForegroundColor Red
}

