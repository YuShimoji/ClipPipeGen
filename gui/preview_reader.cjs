const fs = require("node:fs");
const path = require("node:path");

function createPreviewReader(repoRoot) {
  const root = path.resolve(repoRoot);
  const maxCandidateCount = 5;

  function normalizeInputPath(inputPath) {
    const rawPath = String(inputPath || "").trim();
    if (rawPath.length >= 2) {
      const first = rawPath[0];
      const last = rawPath[rawPath.length - 1];
      if ((first === '"' && last === '"') || (first === "'" && last === "'")) {
        return rawPath.slice(1, -1).trim();
      }
    }
    return rawPath;
  }

  function resolveRepoPath(inputPath) {
    const normalizedPath = normalizeInputPath(inputPath);
    if (!normalizedPath) return root;
    return path.resolve(root, normalizedPath);
  }

  function isInsideRepo(fullPath) {
    const rootCompare = path.normalize(root).replace(/[\\\/]+$/, "").toLowerCase();
    const pathCompare = path.normalize(path.resolve(fullPath)).replace(/[\\\/]+$/, "").toLowerCase();
    return pathCompare === rootCompare || pathCompare.startsWith(`${rootCompare}${path.sep}`);
  }

  function repoRelativePath(fullPath) {
    const relativePath = path.relative(root, fullPath);
    return (relativePath || ".").replace(/\\/g, "/");
  }

  function readbackFor(inputPath, selectedPath, expectedManifestPath = null) {
    const normalizedInputPath = normalizeInputPath(inputPath);
    const payload = {
      repoRoot: root,
      inputPath: String(inputPath || "").trim(),
      normalizedInputPath,
      selectedPath,
      relativePath: repoRelativePath(selectedPath),
    };
    if (expectedManifestPath) {
      payload.expectedManifestPath = expectedManifestPath;
    }
    return payload;
  }

  function isEpisodesParent(fullPath) {
    return repoRelativePath(fullPath).toLowerCase() === "episodes";
  }

  function candidatePreviewManifests() {
    const episodesDir = path.join(root, "episodes");
    if (!pathExists(episodesDir)) return [];
    try {
      return fs.readdirSync(episodesDir, { withFileTypes: true })
        .filter((entry) => entry.isDirectory())
        .map((entry) => path.join(episodesDir, entry.name, "preview_manifest.json"))
        .filter((candidatePath) => pathExists(candidatePath))
        .sort()
        .slice(0, maxCandidateCount)
        .map((candidatePath) => ({
          path: candidatePath,
          relativePath: repoRelativePath(candidatePath),
        }));
    } catch (_error) {
      return [];
    }
  }

  function pathExists(fullPath) {
    try {
      return fs.existsSync(fullPath);
    } catch (_error) {
      return false;
    }
  }

  function toFileUrl(fullPath) {
    return `file:///${fullPath.replace(/\\/g, "/")}`;
  }

  function resolveManifestArtifactPath(displayPath, manifestDir) {
    const value = String(displayPath || "").trim();
    if (!value) return "";
    const repoCandidate = path.resolve(root, value);
    if (pathExists(repoCandidate)) return repoCandidate;
    const episodeCandidate = path.resolve(manifestDir, value);
    if (pathExists(episodeCandidate)) return episodeCandidate;
    return repoCandidate;
  }

  function buildArtifactReadback(manifest, manifestPath) {
    const manifestDir = path.dirname(manifestPath);
    const rows = [
      ["Preview manifest", path.relative(root, manifestPath)],
      ["Preview report", manifest?.report?.path],
      ["Source WAV", manifest?.material?.source_wav],
      ["Fetch receipt", manifest?.material?.fetch_receipt],
      ["Sidecar", manifest?.material?.sidecar],
      ["Material ledger", manifest?.material?.material_ledger],
      ["Transcript", manifest?.transcript?.path],
      ["Edit pack", manifest?.cuts?.path],
    ];
    return rows
      .filter(([_label, displayPath]) => typeof displayPath === "string" && displayPath.length > 0)
      .map(([label, displayPath]) => {
        const fullPath = label === "Preview manifest" ? manifestPath : resolveManifestArtifactPath(displayPath, manifestDir);
        return {
          label,
          path: displayPath,
          fullPath,
          exists: pathExists(fullPath),
          url: toFileUrl(fullPath),
        };
      });
  }

  function readPreviewPack(inputPath) {
    const selectedPath = resolveRepoPath(inputPath || "samples/episode_example");
    const candidates = candidatePreviewManifests();
    if (!isInsideRepo(selectedPath)) {
      const readback = readbackFor(inputPath || "samples/episode_example", selectedPath);
      return {
        ok: false,
        state: "blocked",
        error: "Preview pack ingest is limited to this repository.",
        validationIssues: ["selected path is outside the repository"],
        artifacts: [],
        warnings: [],
        candidateManifests: candidates,
        ...readback,
      };
    }

    const manifestPath = selectedPath.toLowerCase().endsWith(".json")
      ? selectedPath
      : path.join(selectedPath, "preview_manifest.json");
    const readback = readbackFor(inputPath || "samples/episode_example", selectedPath, manifestPath);

    if (isEpisodesParent(selectedPath)) {
      return {
        ok: true,
        state: "blocked",
        error: "The episodes parent directory was selected. Choose an individual episode directory or preview_manifest.json.",
        manifestPath,
        episodeDir: selectedPath,
        validationIssues: ["choose an individual episode directory or preview_manifest.json"],
        artifacts: [],
        warnings: ["Use a repo-relative path such as episodes/<episode_id> or episodes/<episode_id>/preview_manifest.json."],
        candidateManifests: candidates,
        ...readback,
      };
    }

    if (!pathExists(manifestPath)) {
      return {
        ok: true,
        state: "missing",
        manifestPath,
        episodeDir: path.dirname(manifestPath),
        validationIssues: [`preview_manifest.json is missing at ${manifestPath}`],
        artifacts: [],
        warnings: [],
        candidateManifests: candidates,
        ...readback,
      };
    }

    let manifest;
    try {
      manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
    } catch (error) {
      return {
        ok: true,
        state: "blocked",
        manifestPath,
        episodeDir: path.dirname(manifestPath),
        validationIssues: [`preview_manifest.json is not valid JSON: ${error.message}`],
        artifacts: [],
        warnings: [],
        candidateManifests: candidates,
        ...readback,
      };
    }

    const validationIssues = validatePreviewManifest(manifest);
    const artifacts = buildArtifactReadback(manifest, manifestPath);
    const missingArtifacts = artifacts.filter((artifact) => !artifact.exists);
    const warnings = Array.isArray(manifest.warnings) ? [...manifest.warnings] : [];
    if (manifest?.transcript?.not_for_acceptance === true) {
      warnings.push("Transcript is not acceptance material.");
    }
    if (missingArtifacts.length > 0) {
      warnings.push(`Missing artifacts: ${missingArtifacts.map((artifact) => artifact.label).join(", ")}`);
    }

    return {
      ok: true,
      state: validationIssues.length > 0 ? "blocked" : missingArtifacts.length > 0 ? "manual_needed" : "ready",
      manifestPath,
      episodeDir: path.dirname(manifestPath),
      manifest,
      validationIssues,
      artifacts,
      warnings,
      candidateManifests: candidates,
      ...readback,
    };
  }

  return { readPreviewPack };
}

function pushIssue(issues, condition, message) {
  if (!condition) issues.push(message);
}

function validatePreviewManifest(manifest) {
  const issues = [];
  pushIssue(issues, manifest && manifest.schema_version === "v1", "schema_version must be v1");
  pushIssue(issues, typeof manifest?.episode_id === "string" && manifest.episode_id.length > 0, "episode_id is required");
  pushIssue(issues, typeof manifest?.created_at === "string" && manifest.created_at.length > 0, "created_at is required");
  pushIssue(
    issues,
    ["local_media_file", "existing_source_audio_material"].includes(manifest?.input?.kind),
    "input.kind must be local_media_file or existing_source_audio_material",
  );
  pushIssue(issues, typeof manifest?.input?.path === "string" && manifest.input.path.length > 0, "input.path is required");
  pushIssue(issues, typeof manifest?.material?.material_id === "string" && manifest.material.material_id.length > 0, "material.material_id is required");
  pushIssue(issues, typeof manifest?.material?.source_wav === "string" && manifest.material.source_wav.length > 0, "material.source_wav is required");
  pushIssue(issues, typeof manifest?.material?.fetch_receipt === "string" && manifest.material.fetch_receipt.length > 0, "material.fetch_receipt is required");
  pushIssue(issues, typeof manifest?.material?.sidecar === "string" && manifest.material.sidecar.length > 0, "material.sidecar is required");
  pushIssue(issues, typeof manifest?.material?.material_ledger === "string" && manifest.material.material_ledger.length > 0, "material.material_ledger is required");
  pushIssue(issues, typeof manifest?.material?.ledger_entry === "object" && manifest.material.ledger_entry !== null, "material.ledger_entry is required");
  pushIssue(issues, typeof manifest?.source_audio_provenance === "object" && manifest.source_audio_provenance !== null, "source_audio_provenance is required");
  pushIssue(issues, ["fixture", "deterministic_fake"].includes(manifest?.transcript?.source), "transcript.source must be fixture or deterministic_fake");
  pushIssue(issues, typeof manifest?.transcript?.path === "string" && manifest.transcript.path.length > 0, "transcript.path is required");
  pushIssue(issues, manifest?.transcript?.not_for_acceptance === true, "transcript.not_for_acceptance must be true");
  pushIssue(issues, Number.isInteger(manifest?.transcript?.segment_count) && manifest.transcript.segment_count >= 0, "transcript.segment_count must be a non-negative integer");
  pushIssue(issues, typeof manifest?.cuts?.path === "string" && manifest.cuts.path.length > 0, "cuts.path is required");
  pushIssue(issues, Number.isInteger(manifest?.cuts?.candidate_count) && manifest.cuts.candidate_count >= 0, "cuts.candidate_count must be a non-negative integer");
  pushIssue(issues, typeof manifest?.cuts?.context_counts === "object" && manifest.cuts.context_counts !== null, "cuts.context_counts is required");
  pushIssue(issues, typeof manifest?.subtitles?.path === "string" && manifest.subtitles.path.length > 0, "subtitles.path is required");
  pushIssue(issues, Number.isInteger(manifest?.subtitles?.subtitle_count) && manifest.subtitles.subtitle_count >= 0, "subtitles.subtitle_count must be a non-negative integer");
  pushIssue(issues, typeof manifest?.report?.path === "string" && manifest.report.path.length > 0, "report.path is required");
  pushIssue(issues, Array.isArray(manifest?.warnings), "warnings must be an array");
  pushIssue(issues, Array.isArray(manifest?.next_actions), "next_actions must be an array");
  return issues;
}

module.exports = {
  createPreviewReader,
  validatePreviewManifest,
};
