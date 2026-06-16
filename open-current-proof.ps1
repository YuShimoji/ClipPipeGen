param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$relativeTarget = "episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_overlay_visual_proof_report.html"
$dashboard = "docs\dashboard\index.html"
$artifacts = "artifacts\ARTIFACTS.md"
$target = Join-Path $repoRoot $relativeTarget

if (Test-Path -LiteralPath $target -PathType Leaf) {
    Write-Host "Opening current proof: $relativeTarget"
    Invoke-Item -LiteralPath $target
    exit 0
}

Write-Host "Current ignored local proof is not present on this machine:"
Write-Host "  $relativeTarget"
Write-Host ""
Write-Host "This is acceptable on a fresh terminal because episodes/ is local evidence, not portable Git evidence."
Write-Host "Start from the tracked surfaces instead:"
Write-Host "  .\open-dashboard.ps1        -> $dashboard"
Write-Host "  .\open-artifacts.ps1        -> $artifacts"
exit 0
