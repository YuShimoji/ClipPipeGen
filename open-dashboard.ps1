param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$relativeTarget = "docs\dashboard\index.html"
$target = Join-Path $repoRoot $relativeTarget

if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
    Write-Host "Dashboard is missing: $relativeTarget"
    Write-Host "Regenerate it with:"
    Write-Host "  uvx python -m src.cli.main build-docs-dashboard --format json"
    exit 1
}

Write-Host "Opening dashboard: $relativeTarget"
Invoke-Item -LiteralPath $target
