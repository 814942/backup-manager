# -- CONFIGURACION -------------------------------------------------------------
$backupFolder = "$env:UserProfile\Zomboid\Saves\Sandbox\save"
$restoreTarget = "$env:UserProfile\Zomboid\Saves\Sandbox"
# ------------------------------------------------------------------------------

# Listar backups disponibles
$backups = Get-ChildItem -Path $backupFolder -Directory | Sort-Object LastWriteTime -Descending

if ($backups.Count -eq 0) {
    Write-Host "`nNo se encontraron backups en: $backupFolder" -ForegroundColor Red
    exit
}

Write-Host "`n===== BACKUPS DISPONIBLES =====" -ForegroundColor Cyan
for ($i = 0; $i -lt $backups.Count; $i++) {
    $b = $backups[$i]
    $sizeBytes = (Get-ChildItem $b.FullName -Recurse | Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round($sizeBytes / 1MB, 2)
    Write-Host "[$($i + 1)] $($b.Name)  |  $sizeMB MB  |  $($b.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Yellow
}

Write-Host "`n[0] Cancelar" -ForegroundColor Gray
Write-Host ""

# Seleccion del usuario
$selection = Read-Host "Elegi el numero del backup a restaurar"

if ($selection -eq "0" -or $selection -eq "") {
    Write-Host "Restauracion cancelada." -ForegroundColor Gray
    exit
}

$index = [int]$selection - 1

if ($index -lt 0 -or $index -ge $backups.Count) {
    Write-Host "Seleccion invalida." -ForegroundColor Red
    exit
}

$selectedBackup = $backups[$index]

# Determinar carpeta destino (nombre original sin el timestamp al final)
$originalName = $selectedBackup.Name -replace "-\d{8}_\d{6}$", ""
$destination = Join-Path $restoreTarget $originalName

# Confirmacion
Write-Host "`nVas a restaurar:" -ForegroundColor Cyan
Write-Host "  Backup : $($selectedBackup.Name)" -ForegroundColor Yellow
Write-Host "  Destino: $destination" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Confirmas? (s/n)"

if ($confirm -ne "s") {
    Write-Host "Restauracion cancelada." -ForegroundColor Gray
    exit
}

# Borrar save actual y restaurar
$startTime = Get-Date
Write-Host "`nRestaurando..." -ForegroundColor Yellow

if (Test-Path $destination) {
    Remove-Item -Path $destination -Recurse -Force
    Write-Host "Save anterior eliminado." -ForegroundColor Gray
}

Copy-Item -Path $selectedBackup.FullName -Destination $destination -Recurse -Force

# Reporte
$endTime = Get-Date
$duration = $endTime - $startTime
$totalHours = [math]::Floor($duration.TotalHours)
$minutes = $duration.Minutes.ToString("D2")
$seconds = $duration.Seconds.ToString("D2")

$sizeBytes = (Get-ChildItem $destination -Recurse | Measure-Object -Property Length -Sum).Sum
$sizeMB = [math]::Round($sizeBytes / 1MB, 2)
$sizeGB = [math]::Round($sizeBytes / 1GB, 2)

Write-Host "`nRestauracion completada!" -ForegroundColor Green
Write-Host "`nInicio : $($startTime.ToString('HH:mm:ss'))" -ForegroundColor Yellow
Write-Host "Fin     : $($endTime.ToString('HH:mm:ss'))" -ForegroundColor Yellow
Write-Host "Duracion: $totalHours`:$minutes`:$seconds" -ForegroundColor Yellow

if ($sizeGB -ge 1) {
    Write-Host "`nSize: $sizeGB GB ($sizeMB MB)" -ForegroundColor Yellow
} else {
    Write-Host "`nSize: $sizeMB MB" -ForegroundColor Yellow
}
