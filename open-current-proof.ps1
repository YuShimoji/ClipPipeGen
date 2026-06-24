param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$relativeTarget = "episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_presentation_review_pack.html"
$fallbackTarget = "episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\current_proof_focused_review.html"
$dashboard = "docs\dashboard\index.html"
$artifacts = "artifacts\ARTIFACTS.md"
$target = Join-Path $repoRoot $relativeTarget
$fallback = Join-Path $repoRoot $fallbackTarget

if (Test-Path -LiteralPath $target -PathType Leaf) {
    Write-Host "Opening current ED-10z tiny render-path-nearer probe pack: $relativeTarget"
    Invoke-Item -LiteralPath $target
    exit 0
}

if (Test-Path -LiteralPath $fallback -PathType Leaf) {
    Write-Host "Current ED-10z tiny render-path-nearer probe pack is not present on this machine:"
    Write-Host "  $relativeTarget"
    Write-Host "Opening retained ED-10v focused proof instead:"
    Write-Host "  $fallbackTarget"
    Invoke-Item -LiteralPath $fallback
    exit 0
}

Write-Host "Current ignored local review pack/proof is not present on this machine:"
Write-Host "  $relativeTarget"
Write-Host "  $fallbackTarget"
Write-Host ""
Write-Host "This is acceptable on a fresh terminal because episodes/ is local evidence, not portable Git evidence."
Write-Host "Start from the tracked surfaces instead:"
Write-Host "  .\open-dashboard.ps1        -> $dashboard"
Write-Host "  .\open-artifacts.ps1        -> $artifacts"
exit 0
