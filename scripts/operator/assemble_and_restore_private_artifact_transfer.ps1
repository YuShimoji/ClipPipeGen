param(
    [Parameter(Mandatory = $true)]
    [string]$PartsManifest,
    [Parameter(Mandatory = $true)]
    [string]$Receipt,
    [string]$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"
$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$resolvedPartsManifest = (Resolve-Path -LiteralPath $PartsManifest).Path
$resolvedReceipt = (Resolve-Path -LiteralPath $Receipt).Path
$partsReadback = Get-Content -Raw -LiteralPath $resolvedPartsManifest | ConvertFrom-Json
$archive = Join-Path (Split-Path -Parent $resolvedPartsManifest) $partsReadback.archive_name

Push-Location $resolvedRepoRoot
try {
    if (Test-Path -LiteralPath $archive) {
        uv run --offline --no-project --python 3.13 python -m src.cli.main `
            assemble-private-artifact-transfer `
            --parts-manifest $resolvedPartsManifest `
            --format json
    }
    else {
        uv run --offline --no-project --python 3.13 python -m src.cli.main `
            assemble-private-artifact-transfer `
            --parts-manifest $resolvedPartsManifest `
            --output $archive `
            --format json
    }
    if ($LASTEXITCODE -ne 0) {
        throw "private transfer assembly failed with exit code $LASTEXITCODE"
    }

    powershell -NoProfile -ExecutionPolicy Bypass -File `
        scripts\operator\restore_private_artifact_transfer.ps1 `
        -Archive $archive `
        -Receipt $resolvedReceipt `
        -RepoRoot $resolvedRepoRoot
    if ($LASTEXITCODE -ne 0) {
        throw "private transfer restore failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
