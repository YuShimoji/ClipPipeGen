param(
    [string]$EpisodeDir = "episodes/wiki_tensaku_family_20260804"
)

$ErrorActionPreference = "Stop"
$artifactId = "clip-wiki-tensaku-longform-v1-003"
$videoId = "Ocqg-RpQURY"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$corpusPath = Join-Path (Join-Path $repoRoot $EpisodeDir) "corpus"

Push-Location $repoRoot
try {
    node src/integrations/asset_fetch/wiki_tensaku_corpus.mjs `
        --output-dir $corpusPath `
        --reuse-inventory `
        --slice-video-id $videoId `
        --artifact-id $artifactId `
        --offline-existing-evidence
    if ($LASTEXITCODE -ne 0) {
        throw "wiki-tensaku third static packet failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
