// Pure argv builders for ClipPipeGen CLI subcommands.
// Kept Electron-free so that gui/smoke.cjs can import them without
// installing electron.

function requireField(payload, name) {
  const v = payload[name];
  if (v === undefined || v === null || String(v).length === 0) {
    throw new Error(`missing required field: ${name}`);
  }
  return String(v);
}

function buildSetComplianceArgs(payload) {
  return [
    "set-compliance",
    "--rights-manifest",
    requireField(payload, "rights_manifest"),
    "--status",
    requireField(payload, "status"),
    "--checked-by",
    requireField(payload, "checked_by"),
  ];
}

function buildRegisterMaterialArgs(payload) {
  const args = [
    "register-material",
    "--episode-id",
    requireField(payload, "episode_id"),
    "--kind",
    requireField(payload, "kind"),
    "--file",
    requireField(payload, "file"),
    "--sidecar",
    requireField(payload, "sidecar"),
    "--registered-by",
    requireField(payload, "registered_by"),
  ];
  if (payload.root) args.push("--root", String(payload.root));
  if (payload.subkind) args.push("--subkind", String(payload.subkind));
  if (payload.material_id) args.push("--material-id", String(payload.material_id));
  const uses = Array.isArray(payload.intended_uses) ? payload.intended_uses : [];
  if (uses.length === 0) {
    throw new Error("missing required field: intended_uses (at least one)");
  }
  for (const u of uses) {
    args.push("--intended-use", String(u));
  }
  return args;
}

function buildPatchThumbnailArgs(payload) {
  const args = [
    "patch-thumbnail",
    "--input",
    requireField(payload, "input"),
    "--output-result",
    requireField(payload, "output_result"),
  ];
  if (payload.base_dir) args.push("--base-dir", String(payload.base_dir));
  if (payload.config) args.push("--config", String(payload.config));
  if (payload.work_dir) args.push("--work-dir", String(payload.work_dir));
  return args;
}

module.exports = {
  buildSetComplianceArgs,
  buildRegisterMaterialArgs,
  buildPatchThumbnailArgs,
};
