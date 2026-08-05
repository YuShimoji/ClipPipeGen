param(
    [string]$EpisodeDir = "episodes/wiki_tensaku_family_20260804",
    [string]$BundleId = "clip-wiki-tensaku-family-turn-v1-001-private-transfer-v1-001"
)

$ErrorActionPreference = "Stop"
$artifactId = "clip-wiki-tensaku-family-turn-v1-001"
$videoId = "1AcId5Yja10"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$output = "$EpisodeDir/transfers/$BundleId.zip"
$receipt = "$output.receipt.json"
$includes = @(
    "$EpisodeDir/corpus/corpus_inventory.json",
    "$EpisodeDir/corpus/corpus_receipt.json",
    "$EpisodeDir/corpus/topic_index.json",
    "$EpisodeDir/corpus/first_slice_editorial_context.json",
    "$EpisodeDir/corpus/rights_manifest.json",
    "$EpisodeDir/corpus/captions",
    "$EpisodeDir/corpus/watch_receipts",
    "$EpisodeDir/corpus/surface_receipts",
    "$EpisodeDir/corpus/slice_inputs",
    "$EpisodeDir/corpus/collector_runs",
    "$EpisodeDir/corpus/materials/$videoId",
    "$EpisodeDir/artifacts/$artifactId"
)

Push-Location $repoRoot
try {
    if (Test-Path -LiteralPath $output) {
        if (-not (Test-Path -LiteralPath $receipt)) {
            throw "immutable transfer archive exists without its receipt: $output"
        }
        uv run --offline --no-project --python 3.13 python -m src.cli.main `
            verify-private-artifact-transfer `
            --archive $output `
            --receipt $receipt `
            --format json
        if ($LASTEXITCODE -ne 0) {
            throw "existing transfer verification failed with exit code $LASTEXITCODE"
        }
        return
    }

    $repoHead = (git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw "git rev-parse HEAD failed" }
    $arguments = @(
        "run", "--offline", "--no-project", "--python", "3.13", "python",
        "-m", "src.cli.main", "build-private-artifact-transfer",
        "--bundle-id", $BundleId,
        "--artifact-id", $artifactId,
        "--source-identity", "youtube:$videoId",
        "--repo-head", $repoHead,
        "--output", $output,
        "--format", "json"
    )
    foreach ($include in $includes) {
        $arguments += @("--include", $include)
    }
    & uv @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "private transfer build failed with exit code $LASTEXITCODE"
    }

    uv run --offline --no-project --python 3.13 python -m src.cli.main `
        verify-private-artifact-transfer `
        --archive $output `
        --receipt $receipt `
        --format json
    if ($LASTEXITCODE -ne 0) {
        throw "private transfer verification failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
