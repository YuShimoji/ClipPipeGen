const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const required = [
  "gui/main.cjs",
  "gui/preload.cjs",
  "gui/preview_reader.cjs",
  "gui/renderer.html",
  "gui/renderer.js",
  "gui/styles.css",
  "package.json",
];

for (const file of required) {
  const full = path.join(root, file);
  if (!fs.existsSync(full)) {
    throw new Error(`missing ${file}`);
  }
}

const html = fs.readFileSync(path.join(root, "gui/renderer.html"), "utf8");
for (const id of [
  "view-episode",
  "view-rights",
  "view-materials",
  "view-editing",
  "view-preview",
  "view-thumbnail",
  "view-settings",
]) {
  if (!html.includes(id)) {
    throw new Error(`renderer missing ${id}`);
  }
}
// Phase 2 (SH-03b) + Editing GUI — action panels and confirm modal must be present.
for (const marker of [
  'data-action-form="set-compliance"',
  'data-action-form="register-material"',
  'data-action-form="patch-thumbnail"',
  'data-action-form="init-edit-pack"',
  'data-action-form="validate-edit-pack"',
  'data-action-form="add-cut-candidate"',
  'id="confirm-modal"',
]) {
  if (!html.includes(marker)) {
    throw new Error(`renderer missing ${marker}`);
  }
}

for (const marker of [
  'data-tab="preview"',
  'id="preview-state"',
  'id="preview-summary"',
  'id="preview-warnings"',
  'id="preview-artifacts"',
]) {
  if (!html.includes(marker)) {
    throw new Error(`renderer missing preview marker ${marker}`);
  }
}
for (const forbidden of [
  'data-action-form="build-local-preview-pack"',
  'data-action-form="fetch-source-audio"',
  'data-action-form="fetch-source-video"',
  'data-action-form="render"',
  'data-action-form="upload"',
]) {
  if (html.includes(forbidden)) {
    throw new Error(`renderer must not expose preview-pack execution control ${forbidden}`);
  }
}

const pkg = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
if (!pkg.devDependencies || !pkg.devDependencies.electron) {
  throw new Error("electron devDependency is missing");
}

const main = fs.readFileSync(path.join(root, "gui/main.cjs"), "utf8");
const preload = fs.readFileSync(path.join(root, "gui/preload.cjs"), "utf8");
const renderer = fs.readFileSync(path.join(root, "gui/renderer.js"), "utf8");
const previewReaderSource = fs.readFileSync(path.join(root, "gui/preview_reader.cjs"), "utf8");
for (const marker of ["preview:read", "createPreviewReader", "readPreviewPack"]) {
  if (!main.includes(marker)) {
    throw new Error(`main missing ${marker}`);
  }
}
for (const marker of ["validatePreviewManifest", "createPreviewReader", "material.source_wav is required"]) {
  if (!previewReaderSource.includes(marker)) {
    throw new Error(`preview reader missing ${marker}`);
  }
}
if (!preload.includes("readPreviewPack")) {
  throw new Error("preload missing readPreviewPack");
}
for (const marker of [
  "renderPreview",
  "renderArtifactLinks",
  "previewReadbackRows",
  "activeFeedbackGroup",
  "renderFeedbackPanel",
  "errors: {",
  "loading: {",
  'return state.currentTab === "preview" ? "preview" : "status"',
  "Transcript is visible for review flow only",
  'state.currentTab !== "preview"',
]) {
  if (!renderer.includes(marker)) {
    throw new Error(`renderer missing ${marker}`);
  }
}
const { createPreviewReader, validatePreviewManifest } = require("./preview_reader.cjs");
const reader = createPreviewReader(root);
const missingPreview = reader.readPreviewPack("__missing_preview_pack_for_smoke__");
if (!missingPreview.ok || missingPreview.state !== "missing") {
  throw new Error("preview reader should report missing preview_manifest.json without failing");
}
if (!missingPreview.expectedManifestPath || !missingPreview.expectedManifestPath.endsWith("preview_manifest.json")) {
  throw new Error("missing preview should report expected preview_manifest.json path");
}

const fixture = createPreviewPackFixture();
try {
  const quotedPreview = reader.readPreviewPack(`"${fixture.episodeDir}"`);
  if (!quotedPreview.ok || quotedPreview.state !== "ready") {
    throw new Error(`quoted absolute preview path should ingest: ${JSON.stringify(quotedPreview)}`);
  }
  if (quotedPreview.normalizedInputPath.includes('"')) {
    throw new Error("quoted absolute preview path should strip paired quotes");
  }
  if (path.normalize(quotedPreview.selectedPath) !== path.normalize(fixture.episodeDir)) {
    throw new Error("quoted absolute preview path should resolve to the episode directory");
  }

  const absolutePreview = reader.readPreviewPack(fixture.episodeDir);
  if (!absolutePreview.ok || absolutePreview.state !== "ready") {
    throw new Error("unquoted absolute repo-internal preview path should ingest");
  }

  const relativePreview = reader.readPreviewPack(fixture.relativeEpisodeDir);
  if (!relativePreview.ok || relativePreview.state !== "ready") {
    throw new Error("unquoted repo-relative preview path should ingest");
  }

  const parentPreview = reader.readPreviewPack("episodes");
  if (!parentPreview.ok || parentPreview.state !== "blocked") {
    throw new Error("episodes parent directory should be blocked with guidance");
  }
  if (!String(parentPreview.error).includes("individual episode directory")) {
    throw new Error("episodes parent directory should explain expected input shape");
  }
  if (!(parentPreview.candidateManifests || []).some((candidate) => candidate.relativePath === fixture.relativeManifestPath)) {
    throw new Error("episodes parent directory should include preview_manifest.json candidates");
  }

  const outsidePreview = reader.readPreviewPack(path.join(os.tmpdir(), "clippipegen-outside-preview-pack"));
  if (outsidePreview.ok || outsidePreview.state !== "blocked") {
    throw new Error("outside-repo preview path should be blocked");
  }
  if (!outsidePreview.repoRoot || !outsidePreview.selectedPath || !outsidePreview.relativePath) {
    throw new Error("blocked outside-repo preview path should include repoRoot/selectedPath/relativePath");
  }
} finally {
  fs.rmSync(fixture.episodeDir, { recursive: true, force: true });
}
const validManifestIssues = validatePreviewManifest({
  schema_version: "v1",
  episode_id: "ep",
  created_at: "2026-05-11T00:00:00+00:00",
  input: { kind: "local_media_file", path: "_tmp/input.wav" },
  material: {
    material_id: "src",
    source_wav: "episodes/ep/materials/src/source.wav",
    fetch_receipt: "episodes/ep/materials/src/fetch_receipt.json",
    sidecar: "episodes/ep/materials/src/sidecar.json",
    material_ledger: "episodes/ep/material_ledger.json",
    ledger_entry: { id: "src", kind: "source_audio" },
  },
  source_audio_provenance: { mode: "local-media-audio", provider: "local-media" },
  transcript: { source: "fixture", path: "episodes/ep/transcript.json", segment_count: 1, not_for_acceptance: true },
  cuts: { path: "episodes/ep/edit_pack.json", candidate_count: 1, context_counts: { passed: 1, needs_review: 0, failed: 0, not_checked: 0 } },
  subtitles: { path: "episodes/ep/edit_pack.json", subtitle_count: 1 },
  report: { path: "episodes/ep/preview_report.html" },
  warnings: [],
  next_actions: [],
});
if (validManifestIssues.length !== 0) {
  throw new Error(`valid preview manifest should pass validation: ${validManifestIssues.join(", ")}`);
}
const invalidManifestIssues = validatePreviewManifest({ schema_version: "v1" });
if (!invalidManifestIssues.includes("episode_id is required") || !invalidManifestIssues.includes("input.kind must be local_media_file or existing_source_audio_material")) {
  throw new Error("invalid preview manifest should report required field issues");
}

// Args builders are pure functions; verify their CLI shape without spawning python.
const argsBuilders = require("./args.cjs");
const sc = argsBuilders.buildSetComplianceArgs({
  rights_manifest: "x.json",
  status: "passed",
  checked_by: "user:test",
});
assertEqual(sc, [
  "set-compliance",
  "--rights-manifest", "x.json",
  "--status", "passed",
  "--checked-by", "user:test",
]);

const rm = argsBuilders.buildRegisterMaterialArgs({
  episode_id: "ep_t",
  kind: "character_image",
  subkind: "transparent_png",
  file: "f.png",
  sidecar: "s.json",
  registered_by: "user:test",
  intended_uses: ["thumbnail"],
});
if (!rm.includes("--episode-id") || !rm.includes("--intended-use") || !rm.includes("transparent_png")) {
  throw new Error("register-material args missing expected flags");
}

const pt = argsBuilders.buildPatchThumbnailArgs({ input: "i.json", output_result: "r.json" });
assertEqual(pt, [
  "patch-thumbnail",
  "--input", "i.json",
  "--output-result", "r.json",
]);

let threwOnMissing = false;
try {
  argsBuilders.buildSetComplianceArgs({});
} catch (_e) {
  threwOnMissing = true;
}
if (!threwOnMissing) throw new Error("set-compliance args should fail on missing fields");

// ED action argv builders
const initPack = argsBuilders.buildInitEditPackArgs({
  episode_id: "ep_t",
  root: "samples",
  force: true,
});
if (!initPack.includes("--episode-id") || !initPack.includes("--root") || !initPack.includes("--force")) {
  throw new Error("init-edit-pack args missing expected flags");
}

assertEqual(
  argsBuilders.buildValidateEditPackArgs({ edit_pack: "p.json" }),
  ["validate-edit-pack", "--edit-pack", "p.json"]
);

const addCut = argsBuilders.buildAddCutCandidateArgs({
  edit_pack: "p.json",
  start_seconds: 65.0,
  end_seconds: 110.0,
  cut_id: "cut_001",
  source: "manual",
  reason: "x",
  confidence: 0.7,
  context_status: "passed",
  select: true,
});
for (const flag of ["--start-seconds", "--end-seconds", "--id", "--source", "--reason", "--confidence", "--context-status", "--select"]) {
  if (!addCut.includes(flag)) throw new Error(`add-cut-candidate args missing ${flag}`);
}

let threwOnMissingED = false;
try {
  argsBuilders.buildAddCutCandidateArgs({ edit_pack: "p.json" });
} catch (_e) {
  threwOnMissingED = true;
}
if (!threwOnMissingED) throw new Error("add-cut-candidate args should fail on missing start/end seconds");

console.log("gui smoke: OK");

function createPreviewPackFixture() {
  const episodeId = `000_gui_smoke_preview_${Date.now()}`;
  const episodeDir = path.join(root, "episodes", episodeId);
  const materialDir = path.join(episodeDir, "materials", "src_audio_smoke");
  fs.mkdirSync(materialDir, { recursive: true });
  const previewReport = path.join(episodeDir, "preview_report.html");
  const sourceWav = path.join(materialDir, "source.wav");
  const fetchReceipt = path.join(materialDir, "fetch_receipt.json");
  const sidecar = path.join(materialDir, "sidecar.json");
  const ledger = path.join(episodeDir, "material_ledger.json");
  const transcript = path.join(episodeDir, "transcript.json");
  const editPack = path.join(episodeDir, "edit_pack.json");
  const manifestPath = path.join(episodeDir, "preview_manifest.json");
  for (const file of [previewReport, sourceWav, fetchReceipt, sidecar, ledger, transcript, editPack]) {
    fs.writeFileSync(file, "{}");
  }
  const rel = (fullPath) => path.relative(root, fullPath).replace(/\\/g, "/");
  fs.writeFileSync(
    manifestPath,
    JSON.stringify(
      {
        schema_version: "v1",
        episode_id: episodeId,
        created_at: "2026-05-11T00:00:00+00:00",
        input: { kind: "local_media_file", path: "_tmp/input.wav" },
        material: {
          material_id: "src_audio_smoke",
          source_wav: rel(sourceWav),
          fetch_receipt: rel(fetchReceipt),
          sidecar: rel(sidecar),
          material_ledger: rel(ledger),
          ledger_entry: { id: "src_audio_smoke", kind: "source_audio" },
        },
        source_audio_provenance: {
          mode: "local-media-audio",
          provider: "local-media",
        },
        transcript: {
          source: "fixture",
          path: rel(transcript),
          segment_count: 1,
          not_for_acceptance: true,
        },
        cuts: {
          path: rel(editPack),
          candidate_count: 1,
          context_counts: { passed: 1, needs_review: 0, failed: 0, not_checked: 0 },
        },
        subtitles: { path: rel(editPack), subtitle_count: 1 },
        report: { path: rel(previewReport) },
        warnings: [],
        next_actions: [],
      },
      null,
      2,
    ),
  );
  return {
    episodeDir,
    relativeEpisodeDir: rel(episodeDir),
    relativeManifestPath: rel(manifestPath),
  };
}

function assertEqual(actual, expected) {
  const a = JSON.stringify(actual);
  const b = JSON.stringify(expected);
  if (a !== b) throw new Error(`expected ${b} but got ${a}`);
}
