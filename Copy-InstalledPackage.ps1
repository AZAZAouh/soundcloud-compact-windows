$ErrorActionPreference = 'Stop'
$package = Get-AppxPackage -Name 'SoundcloudLtd.SoundCloud-MusicAudio'
if (-not $package) { throw 'Install SoundCloud from Microsoft Store first.' }
if ($package.Version.ToString() -ne '2.12.4.0' -or $package.Architecture.ToString() -ne 'X64') {
    throw 'Only SoundCloud 2.12.4.0 x64 is supported. Do not patch another build with these offsets.'
}
$source = $package.InstallLocation
$destination = Join-Path $PSScriptRoot 'original'
if (Test-Path -LiteralPath $destination) { throw 'original already exists. Keep the existing snapshot.' }
$bundle = Join-Path $source 'Bundle\index.windows.bundle'
$expected = '68cc48434e2768750836d439c7adbcb9375f26a5d5a39ccb3c855cea7bd405d6'
if ((Get-FileHash -LiteralPath $bundle -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) {
    throw 'Unsupported bundle SHA-256. No files were copied.'
}
New-Item -ItemType Directory -Path $destination | Out-Null
Get-ChildItem -LiteralPath $source -File | Copy-Item -Destination $destination
foreach ($folder in @('Assets', 'Bundle')) {
    Copy-Item -LiteralPath (Join-Path $source $folder) -Destination $destination -Recurse
}
Write-Host 'Copied package files into original. Installed package permissions and files were not changed.'
