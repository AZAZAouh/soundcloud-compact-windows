$ErrorActionPreference = 'Stop'
$package = Get-AppxPackage -Name 'SoundClaude.Compact80'
if (-not $package) { throw 'Run Register-Compact.ps1 first. Windows Developer Mode is required.' }
Start-Process explorer.exe -ArgumentList "shell:AppsFolder\$($package.PackageFamilyName)!App"
# One bounded startup check; no resident helper or watcher.
for ($attempt = 0; $attempt -lt 20; $attempt++) {
    $localPlayer = Get-Process soundcouch -ErrorAction SilentlyContinue |
        Where-Object Path -eq (Join-Path $PSScriptRoot 'compact-80\soundcouch.exe')
    if ($localPlayer) {
        $localPlayer | ForEach-Object { $_.PriorityClass = 'BelowNormal' }
        break
    }
    Start-Sleep -Milliseconds 250
}
