param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$relativeTarget = "artifacts\ARTIFACTS.md"
$target = Join-Path $repoRoot $relativeTarget

if (Test-Path -LiteralPath $target -PathType Leaf) {
    Write-Host "Opening artifact registry: $relativeTarget"
    Invoke-Item -LiteralPath $target
    exit 0
}

Write-Host "Artifact registry is missing: $relativeTarget"
exit 1
