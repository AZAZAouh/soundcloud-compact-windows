$ErrorActionPreference = 'Stop'
# Requires Windows Developer Mode; never replaces the Store package.
Add-AppxPackage -Register (Join-Path $PSScriptRoot 'compact-80\AppxManifest.xml')
$package = Get-AppxPackage -Name 'SoundClaude.Compact80'
if (-not $package) { throw 'Local package was not registered.' }
& (Join-Path $PSScriptRoot 'Launch-Compact.ps1')
