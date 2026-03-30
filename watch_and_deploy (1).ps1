# ─────────────────────────────────────────
#  Auto-deploy — Site Antonin Atger
#  Lance ce script une fois, laisse-le tourner.
#  Il deploie automatiquement des que un fichier est modifie.
# ─────────────────────────────────────────

$folder = Split-Path -Parent $MyInvocation.MyCommand.Path
$deploy = Join-Path $folder "deploy.bat"

Write-Host "Surveillance de : $folder" -ForegroundColor Cyan
Write-Host "Fichiers surveilles : *.html, *.css, *.js, *.md" -ForegroundColor Cyan
Write-Host "Ctrl+C pour arreter.`n" -ForegroundColor DarkGray

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path   = $folder
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $false
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName

$extensions = @('.html', '.css', '.js', '.md')

# Delai anti-doublon
$lastDeploy = [datetime]::MinValue

$action = {
    $ext = [System.IO.Path]::GetExtension($Event.SourceEventArgs.Name).ToLower()
    if ($ext -notin $using:extensions) { return }

    $now = Get-Date
    if (($now - $script:lastDeploy).TotalSeconds -lt 5) { return }
    $script:lastDeploy = $now

    $fichier = $Event.SourceEventArgs.Name
    Write-Host "`n[$now] Modifie : $fichier — deploiement en cours..." -ForegroundColor Yellow

    $result = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$using:deploy`"" -Wait -PassThru -NoNewWindow

    if ($result.ExitCode -eq 0) {
        Write-Host "Deploy OK !" -ForegroundColor Green
    } else {
        Write-Host "Erreur lors du push. Verifie ta connexion ou ton depot." -ForegroundColor Red
    }
}

Register-ObjectEvent $watcher Changed -Action $action | Out-Null
Register-ObjectEvent $watcher Created -Action $action | Out-Null
Register-ObjectEvent $watcher Deleted -Action $action | Out-Null
Register-ObjectEvent $watcher Renamed -Action $action | Out-Null

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    $watcher.Dispose()
}
