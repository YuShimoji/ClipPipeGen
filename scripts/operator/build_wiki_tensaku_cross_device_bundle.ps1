param(
    [string]$EpisodeDir = "episodes/wiki_tensaku_family_20260804",
    [string]$ArtifactId = "clip-wiki-tensaku-family-turn-v1-001",
    [string]$BundleId = "",
    [ValidateSet("full-corpus", "artifact-delta")]
    [string]$PayloadMode = "full-corpus"
)

$ErrorActionPreference = "Stop"
$videoId = "1AcId5Yja10"
if (-not $BundleId) {
    $BundleId = "$ArtifactId-private-transfer-v1-001"
}
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$output = "$EpisodeDir/transfers/$BundleId.zip"
$receipt = "$output.receipt.json"
$partsManifest = "$output.parts.json"
$includes = if ($PayloadMode -eq "artifact-delta") {
    @(
        "$EpisodeDir/corpus/slice_inputs/$ArtifactId",
        "$EpisodeDir/artifacts/$ArtifactId"
    )
}
else {
    @(
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
        "$EpisodeDir/artifacts/$ArtifactId"
    )
}

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
    }
    else {
        $repoHead = (git rev-parse HEAD).Trim()
        if ($LASTEXITCODE -ne 0) { throw "git rev-parse HEAD failed" }
        $arguments = @(
            "run", "--offline", "--no-project", "--python", "3.13", "python",
            "-m", "src.cli.main", "build-private-artifact-transfer",
            "--bundle-id", $BundleId,
            "--artifact-id", $ArtifactId,
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

    if (-not (Test-Path -LiteralPath $partsManifest)) {
        uv run --offline --no-project --python 3.13 python -m src.cli.main `
            split-private-artifact-transfer `
            --archive $output `
            --part-size-mib 16 `
            --format json
        if ($LASTEXITCODE -ne 0) {
            throw "private transfer split failed with exit code $LASTEXITCODE"
        }
    }

    uv run --offline --no-project --python 3.13 python -m src.cli.main `
        assemble-private-artifact-transfer `
        --parts-manifest $partsManifest `
        --format json
    if ($LASTEXITCODE -ne 0) {
        throw "private transfer parts verification failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
