param(
    [switch]$OpenFolder,
    [switch]$OpenManifest,
    [switch]$OpenAss
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$relativeFolder = "episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_render_path_selector_probe"
$relativeVideo = Join-Path $relativeFolder "subtitle_render_path_selector_probe.mp4"
$relativeAss = Join-Path $relativeFolder "subtitle_render_path_selector_probe.ass"
$relativeManifest = Join-Path $relativeFolder "subtitle_render_path_selector_probe.local.json"

$folder = Join-Path $repoRoot $relativeFolder
$video = Join-Path $repoRoot $relativeVideo
$ass = Join-Path $repoRoot $relativeAss
$manifest = Join-Path $repoRoot $relativeManifest

if ($OpenFolder) {
    if (-not (Test-Path -LiteralPath $folder -PathType Container)) {
        Write-Host "Internal review candidate folder is missing on this host:"
        Write-Host "  $folder"
        exit 1
    }
    Write-Host "Opening internal review candidate folder:"
    Write-Host "  $folder"
    Invoke-Item -LiteralPath $folder
    exit 0
}

if ($OpenManifest) {
    if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
        Write-Host "Internal review candidate manifest is missing on this host:"
        Write-Host "  $manifest"
        exit 1
    }
    Write-Host "Opening internal review candidate manifest:"
    Write-Host "  $manifest"
    Invoke-Item -LiteralPath $manifest
    exit 0
}

if ($OpenAss) {
    if (-not (Test-Path -LiteralPath $ass -PathType Leaf)) {
        Write-Host "Internal review candidate ASS file is missing on this host:"
        Write-Host "  $ass"
        exit 1
    }
    Write-Host "Opening internal review candidate ASS file:"
    Write-Host "  $ass"
    Invoke-Item -LiteralPath $ass
    exit 0
}

if (-not (Test-Path -LiteralPath $video -PathType Leaf)) {
    Write-Host "Internal review candidate MP4 is missing on this host:"
    Write-Host "  $video"
    Write-Host ""
    Write-Host "Open the folder if it exists:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\operator\open_internal_review_video_candidate.ps1 -OpenFolder"
    exit 1
}

Write-Host "Opening ED-10ar internal review video candidate MP4:"
Write-Host "  $video"
Invoke-Item -LiteralPath $video
