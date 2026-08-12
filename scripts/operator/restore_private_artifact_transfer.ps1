param(
    [Parameter(Mandatory = $true)]
    [string]$Archive,
    [Parameter(Mandatory = $true)]
    [string]$Receipt,
    [string]$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"
$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$resolvedArchive = (Resolve-Path -LiteralPath $Archive).Path
$resolvedReceipt = (Resolve-Path -LiteralPath $Receipt).Path

Push-Location $resolvedRepoRoot
try {
    uv run --offline --no-project --python 3.13 python -m src.cli.main `
        verify-private-artifact-transfer `
        --archive $resolvedArchive `
        --receipt $resolvedReceipt `
        --restore-root $resolvedRepoRoot `
        --format json
    if ($LASTEXITCODE -ne 0) {
        throw "private transfer restore failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
