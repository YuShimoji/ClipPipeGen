param(
    [string]$EpisodeDir = "episodes/wiki_tensaku_family_20260804",
    [int]$ReviewPort = 8080
)

$ErrorActionPreference = "Stop"
$artifactId = "clip-wiki-tensaku-family-turn-v4-001"
$videoId = "1AcId5Yja10"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$episodePath = Join-Path $repoRoot $EpisodeDir
$corpusPath = Join-Path $episodePath "corpus"
$sliceInputPath = Join-Path $corpusPath "slice_inputs/$artifactId"
$artifactPath = Join-Path $episodePath "artifacts/$artifactId"
$sourcePath = Join-Path $corpusPath "materials/$videoId/source_video.mp4"
$captionPath = Join-Path $corpusPath "captions/$videoId.ja.json3"
$rightsPath = Join-Path $sliceInputPath "rights_manifest.json"
$contextPath = Join-Path $sliceInputPath "editorial_context.json"
$baselineEditPack = Join-Path $EpisodeDir "artifacts/clip-wiki-tensaku-longform-v1-001/edit_pack.json"
$turnOneEditPack = Join-Path $EpisodeDir "artifacts/clip-wiki-tensaku-family-turn-v1-001/edit_pack.json"
$turnTwoEditPack = Join-Path $EpisodeDir "artifacts/clip-wiki-tensaku-family-turn-v2-001/edit_pack.json"
$turnThreeEditPack = Join-Path $EpisodeDir "artifacts/clip-wiki-tensaku-family-turn-v3-001/edit_pack.json"

Push-Location $repoRoot
try {
    node src/integrations/asset_fetch/wiki_tensaku_corpus.mjs `
        --output-dir $corpusPath `
        --reuse-inventory `
        --slice-video-id $videoId `
        --artifact-id $artifactId `
        --offline-existing-evidence `
        --reuse-retained-source-media `
        --selection-profile uncovered-correction-led `
        --exclude-edit-pack $baselineEditPack `
        --exclude-edit-pack $turnOneEditPack `
        --exclude-edit-pack $turnTwoEditPack `
        --exclude-edit-pack $turnThreeEditPack
    if ($LASTEXITCODE -ne 0) { throw "wiki-tensaku fourth uncovered retained-source planning failed with exit code $LASTEXITCODE" }

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
        --artifact-id $artifactId `
        --source $sourcePath `
        --source-identity "youtube:$videoId" `
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
