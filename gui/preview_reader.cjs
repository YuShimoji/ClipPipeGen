const fs = require("node:fs");
const path = require("node:path");

function createPreviewReader(repoRoot) {
  const root = path.resolve(repoRoot);

  function resolveRepoPath(inputPath) {
    const rawPath = String(inputPath || "").trim();
    if (!rawPath) return root;
    return path.resolve(root, rawPath);
  }

  function isInsideRepo(fullPath) {
    const relativePath = path.relative(root, fullPath);
    return relativePath === "" || (!relativePath.startsWith("..") && !path.isAbsolute(relativePath));
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
    if (!isInsideRepo(selectedPath)) {
      return {
        ok: false,
        state: "blocked",
        error: "Preview pack ingest is limited to this repository.",
        validationIssues: ["selected path is outside the repository"],
        artifacts: [],
        warnings: [],
      };
    }

    const manifestPath = selectedPath.toLowerCase().endsWith(".json")
      ? selectedPath
      : path.join(selectedPath, "preview_manifest.json");

    if (!pathExists(manifestPath)) {
      return {
        ok: true,
        state: "missing",
        manifestPath,
        episodeDir: path.dirname(manifestPath),
        validationIssues: ["preview_manifest.json is missing"],
        artifacts: [],
        warnings: [],
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
  pushIssue(issues, manifest?.input?.kind === "local_media_file", "input.kind must be local_media_file");
  pushIssue(issues, typeof manifest?.input?.path === "string" && manifest.input.path.length > 0, "input.path is required");
  pushIssue(issues, typeof manifest?.material?.material_id === "string" && manifest.material.material_id.length > 0, "material.material_id is required");
  pushIssue(issues, typeof manifest?.material?.source_wav === "string" && manifest.material.source_wav.length > 0, "material.source_wav is required");
  pushIssue(issues, typeof manifest?.material?.fetch_receipt === "string" && manifest.material.fetch_receipt.length > 0, "material.fetch_receipt is required");
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
