param(
    [string]$EpisodeDir = "episodes/wiki_tensaku_family_20260804",
    [int]$ReviewPort = 8078
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$episodePath = Join-Path $repoRoot $EpisodeDir
$corpusPath = Join-Path $episodePath "corpus"
$artifactPath = Join-Path $episodePath "artifacts/clip-wiki-tensaku-longform-v1-001"
$sourcePath = Join-Path $corpusPath "materials/1AcId5Yja10/source_video.mp4"
$captionPath = Join-Path $corpusPath "captions/1AcId5Yja10.ja.json3"
$rightsPath = Join-Path $corpusPath "rights_manifest.json"
$contextPath = Join-Path $corpusPath "first_slice_editorial_context.json"

Push-Location $repoRoot
try {
    node src/integrations/asset_fetch/wiki_tensaku_corpus.mjs `
        --output-dir $corpusPath `
        --download-first-source
    if ($LASTEXITCODE -ne 0) { throw "wiki-tensaku collector failed with exit code $LASTEXITCODE" }

    $manifestPath = Join-Path $artifactPath "run_manifest.json"
    $failurePath = Join-Path $artifactPath "pipeline_failure.json"
    $resumeArgument = @()
    if (Test-Path -LiteralPath $manifestPath) {
        $resumeArgument = @("--resume")
    }
    elseif (Test-Path -LiteralPath $failurePath) {
        $resumeArgument = @("--force")
    }
    uv run --offline --no-project --python 3.13 --with pytest python -m src.cli.main `
        build-real-video `
        --artifact-id clip-wiki-tensaku-longform-v1-001 `
        --source $sourcePath `
        --source-identity youtube:1AcId5Yja10 `
        --rights-manifest $rightsPath `
        --caption-track $captionPath `
        --caption-mode sidecar `
        --editorial-context $contextPath `
        --output-dir $artifactPath `
        --target-duration 300 `
        --review-port $ReviewPort `
        @resumeArgument `
        --format json
    if ($LASTEXITCODE -ne 0) { throw "build-real-video failed with exit code $LASTEXITCODE" }
}
finally {
    Pop-Location
}
