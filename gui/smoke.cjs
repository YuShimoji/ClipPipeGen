const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const required = [
  "gui/main.cjs",
  "gui/preload.cjs",
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

const pkg = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
if (!pkg.devDependencies || !pkg.devDependencies.electron) {
  throw new Error("electron devDependency is missing");
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

function assertEqual(actual, expected) {
  const a = JSON.stringify(actual);
  const b = JSON.stringify(expected);
  if (a !== b) throw new Error(`expected ${b} but got ${a}`);
}
