$ErrorActionPreference = 'Stop'
$revision = '2e796663e1fedb93dca51060797ebf3327b3fedb'
$destination = Join-Path $PSScriptRoot 'tools\hermes-dec'
if (Test-Path -LiteralPath $destination) {
    $actual = & git -C $destination rev-parse HEAD
    if ($LASTEXITCODE -ne 0 -or $actual.Trim() -ne $revision) { throw 'Unexpected existing hermes-dec checkout.' }
    Write-Host 'Pinned hermes-dec checkout already present.'
    exit 0
}
New-Item -ItemType Directory -Path $destination | Out-Null
& git -C $destination init --quiet
if ($LASTEXITCODE -ne 0) { throw 'git init failed.' }
& git -C $destination remote add origin 'https://github.com/P1sec/hermes-dec.git'
if ($LASTEXITCODE -ne 0) { throw 'git remote add failed.' }
& git -C $destination fetch --depth 1 origin $revision
if ($LASTEXITCODE -ne 0) { throw 'Could not fetch the pinned hermes-dec revision.' }
& git -C $destination checkout --detach FETCH_HEAD
if ($LASTEXITCODE -ne 0) { throw 'Could not check out hermes-dec.' }
