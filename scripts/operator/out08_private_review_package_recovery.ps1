[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("Probe", "Export", "Import")]
    [string]$Action,

    [string]$RepoRoot,
    [string]$Package,
    [string]$Destination,
    [string]$Archive,
    [int]$Port = 8071,
    [switch]$StartServer
)

$ErrorActionPreference = "Stop"
if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}
$arguments = @(
    "python", "-m", "src.cli.main",
    "recover-out08-private-review-package",
    "--repo-root", $RepoRoot,
    "--format", "json"
)

if ($Package) {
    $arguments += @("--package", $Package)
}

switch ($Action) {
    "Probe" {
        $arguments += @("probe", "--port", $Port)
    }
    "Export" {
        if (-not $Destination) {
            throw "Export requires an explicit -Destination outside the repository."
        }
        $arguments += @("export", "--destination", $Destination)
    }
    "Import" {
        if (-not $Archive) {
            throw "Import requires an explicit -Archive path."
        }
        $arguments += @("import", "--archive", $Archive, "--port", $Port)
        if ($StartServer) {
            $arguments += "--start-server"
        }
    }
}

Push-Location $RepoRoot
try {
    & uvx @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "OUT-08 recovery command failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
