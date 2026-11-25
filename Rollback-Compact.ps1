$ErrorActionPreference = 'Stop'
# Remove only our separate local registration and its separate application data.
Get-AppxPackage -Name 'SoundClaude.Compact80' | ForEach-Object {
    if ($_.Name -ne 'SoundClaude.Compact80') { throw 'Unexpected package identity.' }
    Remove-AppxPackage -Package $_.PackageFullName
}
Write-Host 'Local Compact registration removed. Store SoundCloud was not modified.'
