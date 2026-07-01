param(
    [switch]$OpenFolder,
    [switch]$OpenManifest,
    [switch]$OpenAss,
    [switch]$SelectVideo,
    [switch]$PrintPath,
    [switch]$NoInvoke
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$relativeFolder = "episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\representative_micro_scene_v2_cut_window_review_purpose_alignment"
$relativeVideo = Join-Path $relativeFolder "representative_micro_scene_v2_cut_window_review_purpose_alignment.mp4"
$relativeAss = Join-Path $relativeFolder "representative_micro_scene_v2_cut_window_review_purpose_alignment.ass"
$relativeManifest = Join-Path $relativeFolder "representative_micro_scene_v2_cut_window_review_purpose_alignment.local.json"

$folder = Join-Path $repoRoot $relativeFolder
$video = Join-Path $repoRoot $relativeVideo
$ass = Join-Path $repoRoot $relativeAss
$manifest = Join-Path $repoRoot $relativeManifest

function Write-ResolvedVideoReadback {
    $videoItem = Get-Item -LiteralPath $video -ErrorAction SilentlyContinue

    Write-Host "Resolved repo root:"
    Write-Host "  $repoRoot"
    Write-Host "Resolved ED-10ba representative micro-scene v2 MP4:"
    Write-Host "  $video"
    Write-Host "video_exists: $($null -ne $videoItem)"
    if ($null -ne $videoItem) {
        Write-Host "video_size_bytes: $($videoItem.Length)"
    }
}

function Write-FallbackCommands {
    Write-Host ""
    Write-Host "Fallback commands if the default associated player does not appear:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -SelectVideo"
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -OpenFolder"
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -OpenManifest"
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -OpenAss"
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -PrintPath"
}

if ($OpenFolder) {
    if (-not (Test-Path -LiteralPath $folder -PathType Container)) {
        Write-Host "Representative micro-scene v2 folder is missing on this host:"
        Write-Host "  $folder"
        exit 1
    }
    Write-Host "Opening representative micro-scene v2 folder:"
    Write-Host "  $folder"
    Invoke-Item -LiteralPath $folder
    exit 0
}

if ($OpenManifest) {
    if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
        Write-Host "Representative micro-scene v2 manifest is missing on this host:"
        Write-Host "  $manifest"
        exit 1
    }
    Write-Host "Opening representative micro-scene v2 manifest:"
    Write-Host "  $manifest"
    Invoke-Item -LiteralPath $manifest
    exit 0
}

if ($OpenAss) {
    if (-not (Test-Path -LiteralPath $ass -PathType Leaf)) {
        Write-Host "Representative micro-scene v2 ASS file is missing on this host:"
        Write-Host "  $ass"
        exit 1
    }
    Write-Host "Opening representative micro-scene v2 ASS file:"
    Write-Host "  $ass"
    Invoke-Item -LiteralPath $ass
    exit 0
}

if ($PrintPath -or $NoInvoke) {
    Write-ResolvedVideoReadback
    Write-Host "open_attempt_status: not_attempted"
    Write-Host "classification: path_print_only"
    Write-FallbackCommands
    exit 0
}

if ($SelectVideo) {
    if (-not (Test-Path -LiteralPath $video -PathType Leaf)) {
        Write-ResolvedVideoReadback
        Write-Host "open_attempt_status: not_attempted_missing_mp4"
        Write-FallbackCommands
        exit 1
    }

    Write-ResolvedVideoReadback
    Write-Host "Attempting explorer selection for the ED-10ba representative micro-scene v2 MP4."
    $selectArg = "/select,`"$video`""
    $process = Start-Process -FilePath "explorer.exe" -ArgumentList $selectArg -PassThru
    if ($null -ne $process) {
        Write-Host "select_process_id: $($process.Id)"
    }
    Write-Host "open_attempt_status: explorer_select_attempted_not_observed"
    Write-Host "classification: file_verified_but_user_visible_open_not_confirmed"
    Write-FallbackCommands
    exit 0
}

if (-not (Test-Path -LiteralPath $video -PathType Leaf)) {
    Write-Host "Representative micro-scene v2 MP4 is missing on this host:"
    Write-Host "  $video"
    Write-Host ""
    Write-Host "Open the folder if it exists:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\operator\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 -OpenFolder"
    exit 1
}

Write-ResolvedVideoReadback
Write-Host "Attempting ED-10ba representative micro-scene v2 MP4 open via Start-Process."
Write-Host "attempt_method: Start-Process -FilePath <mp4> -PassThru"
try {
    $process = Start-Process -FilePath $video -PassThru
    if ($null -ne $process) {
        Write-Host "process_id: $($process.Id)"
        Write-Host "process_name: $($process.ProcessName)"
    }
    else {
        Write-Host "process_id: unavailable"
    }
    Write-Host "open_attempt_status: start_process_attempted_not_observed"
    Write-Host "classification: file_verified_but_user_visible_open_not_confirmed"
    Write-FallbackCommands
    exit 0
}
catch {
    Write-Host "open_attempt_status: start_process_failed"
    Write-Host "classification: file_association_or_start_process_failed"
    Write-Host "error: $($_.Exception.Message)"
    Write-FallbackCommands
    exit 2
}
