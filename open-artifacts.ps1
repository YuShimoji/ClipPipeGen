param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$relativeTarget = "artifacts\ARTIFACTS.md"
$dashboard = "docs\dashboard\index.html"
$target = Join-Path $repoRoot $relativeTarget

if (Test-Path -LiteralPath $target -PathType Leaf) {
    Write-Host "Opening artifact registry: $relativeTarget"
    Write-Host "Dashboard artifact surface: $dashboard"
    Invoke-Item -LiteralPath $target
    exit 0
}

Write-Host "Artifact registry is missing: $relativeTarget"
Write-Host "Open the dashboard instead:"
Write-Host "  .\open-dashboard.ps1"
exit 1
