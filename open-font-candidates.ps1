param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$relativeDoc = "docs\SUBTITLE_FONT_CANDIDATE_SWEEP.md"
$relativeJson = "docs\font_candidates\subtitle-font-candidates.json"
$docPath = Join-Path $repoRoot $relativeDoc
$jsonPath = Join-Path $repoRoot $relativeJson

if (Test-Path -LiteralPath $jsonPath -PathType Leaf) {
    $registry = Get-Content -Raw -Encoding UTF8 -LiteralPath $jsonPath | ConvertFrom-Json
    $candidateCount = @($registry.candidates).Count
    Write-Host "Font candidate registry: $relativeJson"
    Write-Host "Candidate count: $candidateCount"
    Write-Host "Current selected diagnostic base: $($registry.current_selected_diagnostic_overlay_proof_base)"
}

if (Test-Path -LiteralPath $docPath -PathType Leaf) {
    Write-Host "Opening font candidate sweep doc: $relativeDoc"
    Invoke-Item -LiteralPath $docPath
    exit 0
}

Write-Host "Font candidate sweep doc is missing: $relativeDoc"
Write-Host "Open the dashboard instead:"
Write-Host "  .\open-dashboard.ps1"
exit 1
