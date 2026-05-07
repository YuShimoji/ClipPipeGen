const state = {
  status: null,
  currentTab: "episode",
};

const tabs = Array.from(document.querySelectorAll(".tab"));
const views = Array.from(document.querySelectorAll(".view"));
const title = document.querySelector("#view-title");
const form = document.querySelector("#episode-form");
const episodeDirInput = document.querySelector("#episode-dir");
const errorPanel = document.querySelector("#error-panel");

const tabTitles = {
  episode: "Episode",
  rights: "Rights",
  materials: "Materials",
  editing: "Editing",
  thumbnail: "Thumbnail",
  settings: "Settings",
};

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    selectTab(tab.dataset.tab);
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await refreshStatus();
});

function selectTab(tabName) {
  state.currentTab = tabName;
  tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === tabName));
  views.forEach((view) => view.classList.toggle("active", view.id === `view-${tabName}`));
  title.textContent = tabTitles[tabName] || "Episode";
}

async function refreshStatus() {
  hideError();
  const episodeDir = episodeDirInput.value.trim() || "samples/episode_example";
  const response = await window.clipPipe.statusEpisode(episodeDir);
  if (!response.ok) {
    showError(response.error || response.stderr || "status-episode failed");
    return;
  }
  state.status = response.status;
  renderStatus(response.status);
}

function renderStatus(status) {
  renderEpisode(status);
  renderRights(status.rights);
  renderMaterials(status.materials);
  renderEditing(status.editing || {}, status.artifacts?.edit_pack || {});
  renderThumbnail(status.thumbnail);
  renderSettings(status.settings);
  prefillActionForms(status);
}

function renderEditing(editing, edit_pack_artifact) {
  document.querySelector("#editing-state").textContent = editing.state || "missing";
  document.querySelector("#editing-state").className = `badge ${stateClass(editing.state)}`;
  const rows = [
    ["edit_pack", edit_pack_artifact.path || "(missing)"],
    ["cut_candidates_count", editing.cut_candidates_count ?? 0],
    ["selected_cuts_count", editing.selected_cuts_count ?? 0],
    ["schema_issues_count", editing.schema_issues_count ?? 0],
  ];
  renderDetails("#editing-content", rows, editing.schema_issues || []);
}

function renderEpisode(status) {
  const grid = document.querySelector("#status-grid");
  grid.replaceChildren(
    statusCard("Rights", status.rights.state, status.artifacts.rights_manifest.path),
    statusCard("Materials", status.materials.state, status.artifacts.material_ledger.path),
    statusCard("Editing", status.editing?.state || "missing", status.artifacts.edit_pack?.path),
    statusCard("Thumbnail", status.thumbnail.state, status.artifacts.thumbnail_patch_input.path),
    statusCard("Bridge", status.settings.bridge_config.ready ? "ready" : "missing", status.settings.bridge_config.path),
  );

  const action = status.next_action || {};
  document.querySelector("#next-owner").textContent = action.owner || "unknown";
  document.querySelector("#next-owner").className = `badge ${stateClass(action.owner)}`;
  document.querySelector("#next-action").textContent = action.action || "No action";
  document.querySelector("#next-reason").textContent = action.reason || "";
}

function statusCard(label, cardState, path) {
  const article = document.createElement("article");
  article.className = "status-card";
  const top = document.createElement("div");
  top.className = "card-top";
  const h3 = document.createElement("h3");
  h3.textContent = label;
  const badge = document.createElement("span");
  badge.className = `badge ${stateClass(cardState)}`;
  badge.textContent = cardState || "unknown";
  top.append(h3, badge);
  const p = document.createElement("p");
  p.textContent = path || "";
  article.append(top, p);
  return article;
}

function renderRights(rights) {
  document.querySelector("#rights-state").textContent = rights.state || "unknown";
  document.querySelector("#rights-state").className = `badge ${stateClass(rights.state)}`;
  const rows = [
    ["compliance_status", rights.compliance_status || "(none)"],
    ["schema_issues", (rights.schema_issues || []).length],
    ["review_notes", (rights.review_notes || []).length],
  ];
  renderDetails("#rights-content", rows, [...(rights.schema_issues || []), ...(rights.review_notes || [])]);
}

function renderMaterials(materials) {
  document.querySelector("#materials-state").textContent = materials.state || "unknown";
  document.querySelector("#materials-state").className = `badge ${stateClass(materials.state)}`;
  const rows = [
    ["materials_count", materials.materials_count ?? 0],
    ["audit_issues_count", materials.audit_issues_count ?? 0],
  ];
  renderDetails("#materials-content", rows, materials.audit_issues || []);
}

function renderThumbnail(thumbnail) {
  document.querySelector("#thumbnail-state").textContent = thumbnail.state || "unknown";
  document.querySelector("#thumbnail-state").className = `badge ${stateClass(thumbnail.state)}`;
  const rows = [
    ["slots_count", thumbnail.slots_count ?? 0],
    ["input_schema_issues", (thumbnail.input_schema_issues || []).length],
    ["result_errors", (thumbnail.result_errors || []).length],
  ];
  renderDetails("#thumbnail-content", rows, thumbnail.input_schema_issues || []);
}

function renderSettings(settings) {
  const bridge = settings.bridge_config || {};
  document.querySelector("#settings-state").textContent = bridge.ready ? "ready" : "missing";
  document.querySelector("#settings-state").className = `badge ${stateClass(bridge.ready ? "ready" : "missing")}`;
  renderDetails("#settings-content", [
    ["path", bridge.path || ""],
    ["exists", bridge.exists ? "yes" : "no"],
    ["ready", bridge.ready ? "yes" : "no"],
    ["message", bridge.message || ""],
  ]);
}

function renderDetails(selector, rows, issues = []) {
  const container = document.querySelector(selector);
  container.replaceChildren();
  rows.forEach(([key, value]) => {
    const row = document.createElement("div");
    row.className = "detail-row";
    const k = document.createElement("span");
    k.textContent = key;
    const v = document.createElement("strong");
    v.textContent = String(value);
    row.append(k, v);
    container.append(row);
  });
  issues.slice(0, 6).forEach((issue) => {
    const row = document.createElement("div");
    row.className = "issue-row";
    row.textContent = `${issue.code || "ISSUE"} @ ${issue.field || "?"}: ${issue.message || ""}`;
    container.append(row);
  });
}

function stateClass(value) {
  if (["ready", "done", "passed", "assistant"].includes(value)) return "ok";
  if (["manual_needed", "user"].includes(value)) return "manual";
  if (["blocked", "failed", "both"].includes(value)) return "blocked";
  return "missing";
}

function showError(message) {
  errorPanel.textContent = message;
  errorPanel.classList.remove("hidden");
}

function hideError() {
  errorPanel.textContent = "";
  errorPanel.classList.add("hidden");
}

// ---------- Phase 2 (SH-03b) — actions ----------

const actionForms = {
  "set-compliance": document.querySelector('[data-action-form="set-compliance"]'),
  "register-material": document.querySelector('[data-action-form="register-material"]'),
  "patch-thumbnail": document.querySelector('[data-action-form="patch-thumbnail"]'),
  "init-edit-pack": document.querySelector('[data-action-form="init-edit-pack"]'),
  "validate-edit-pack": document.querySelector('[data-action-form="validate-edit-pack"]'),
  "add-cut-candidate": document.querySelector('[data-action-form="add-cut-candidate"]'),
};

const actionResults = {
  "set-compliance": document.querySelector('[data-action-result="set-compliance"]'),
  "register-material": document.querySelector('[data-action-result="register-material"]'),
  "patch-thumbnail": document.querySelector('[data-action-result="patch-thumbnail"]'),
  "init-edit-pack": document.querySelector('[data-action-result="init-edit-pack"]'),
  "validate-edit-pack": document.querySelector('[data-action-result="validate-edit-pack"]'),
  "add-cut-candidate": document.querySelector('[data-action-result="add-cut-candidate"]'),
};

function fieldValue(formEl, name) {
  const el = formEl.querySelector(`[data-field="${name}"]`);
  if (!el) return "";
  return (el.value || "").trim();
}

function setFieldValue(formEl, name, value) {
  const el = formEl.querySelector(`[data-field="${name}"]`);
  if (!el) return;
  if (!el.value || el.dataset.derived === "true") {
    el.value = value;
    el.dataset.derived = "true";
  }
}

function prefillActionForms(status) {
  const epDir = (episodeDirInput.value || "samples/episode_example").trim();
  // CLI convention: episode_id == dir basename. Prefer the basename so init-edit-pack
  // (which writes to <root>/<episode_id>/) lands inside epDir rather than next to it.
  const dirBase = epDir.split(/[\\/]/).pop() || "";
  const epId = dirBase || status.episode_id || "";
  const epRoot = epDir.split(/[\\/]/).slice(0, -1).join("/") || ".";
  const rightsPath = status.artifacts?.rights_manifest?.path || `${epDir}/rights_manifest.json`;
  const editPackPath = status.artifacts?.edit_pack?.path || `${epDir}/edit_pack.json`;
  const thumbInputPath =
    status.artifacts?.thumbnail_patch_input?.path || `${epDir}/thumbnail_patch_input.json`;
  const thumbResultPath = `${epDir}/thumbnail_patch_result.json`;

  if (actionForms["set-compliance"]) {
    setFieldValue(actionForms["set-compliance"], "rights_manifest", rightsPath);
  }
  if (actionForms["register-material"]) {
    setFieldValue(actionForms["register-material"], "episode_id", epId);
  }
  if (actionForms["patch-thumbnail"]) {
    setFieldValue(actionForms["patch-thumbnail"], "input", thumbInputPath);
    setFieldValue(actionForms["patch-thumbnail"], "output_result", thumbResultPath);
  }
  if (actionForms["init-edit-pack"]) {
    setFieldValue(actionForms["init-edit-pack"], "episode_id", epId);
    setFieldValue(actionForms["init-edit-pack"], "root", epRoot);
  }
  if (actionForms["validate-edit-pack"]) {
    setFieldValue(actionForms["validate-edit-pack"], "edit_pack", editPackPath);
  }
  if (actionForms["add-cut-candidate"]) {
    setFieldValue(actionForms["add-cut-candidate"], "edit_pack", editPackPath);
  }
}

// ---------- confirm modal ----------

const confirmModal = document.querySelector("#confirm-modal");
const confirmTitle = document.querySelector("#confirm-title");
const confirmSummary = document.querySelector("#confirm-summary");
const confirmCommand = document.querySelector("#confirm-command");
const confirmReason = document.querySelector("#confirm-reason");
const confirmCancel = document.querySelector("#confirm-cancel");
const confirmOk = document.querySelector("#confirm-ok");

function showConfirm({ title, summary, command, reason }) {
  return new Promise((resolve) => {
    confirmTitle.textContent = title;
    confirmSummary.textContent = summary;
    confirmCommand.textContent = command;
    confirmReason.textContent = reason || "";
    confirmModal.classList.remove("hidden");

    function cleanup(result) {
      confirmModal.classList.add("hidden");
      confirmCancel.removeEventListener("click", onCancel);
      confirmOk.removeEventListener("click", onOk);
      document.removeEventListener("keydown", onKey);
      resolve(result);
    }
    function onCancel() { cleanup(false); }
    function onOk() { cleanup(true); }
    function onKey(e) {
      if (e.key === "Escape") cleanup(false);
      if (e.key === "Enter") cleanup(true);
    }
    confirmCancel.addEventListener("click", onCancel);
    confirmOk.addEventListener("click", onOk);
    document.addEventListener("keydown", onKey);
  });
}

// ---------- result rendering ----------

function renderActionResult(actionKey, result) {
  const pre = actionResults[actionKey];
  if (!pre) return;
  pre.hidden = false;
  pre.classList.remove("ok", "fail");
  pre.classList.add(result.ok ? "ok" : "fail");
  const cmd = (result.command || []).join(" ") || "(command not built)";
  const lines = [
    `$ ${cmd}`,
    `exit: ${result.code === null || result.code === undefined ? "(spawn error)" : result.code}`,
  ];
  if (result.error) lines.push(`error: ${result.error}`);
  if (result.stdout) {
    lines.push("--- stdout ---");
    lines.push(tail(result.stdout, 30));
  }
  if (result.stderr) {
    lines.push("--- stderr ---");
    lines.push(tail(result.stderr, 30));
  }
  pre.textContent = lines.join("\n");
}

function tail(text, maxLines) {
  const arr = (text || "").split(/\r?\n/);
  if (arr.length <= maxLines) return arr.join("\n");
  return ["…(truncated)", ...arr.slice(arr.length - maxLines)].join("\n");
}

// ---------- action submit handlers ----------

const actionMeta = {
  "set-compliance": {
    title: "Run set-compliance",
    reason:
      "set-compliance records rights/compliance status for readback. It does not gate downstream local processing.",
    buildPayload(formEl) {
      return {
        rights_manifest: fieldValue(formEl, "rights_manifest"),
        status: fieldValue(formEl, "status"),
        checked_by: fieldValue(formEl, "checked_by"),
      };
    },
    invoke: (payload) => window.clipPipe.setCompliance(payload),
  },
  "register-material": {
    title: "Run register-material",
    reason:
      "register-material adds an entry to material_ledger.json. Sidecar is validated; hash must match; transparent_png subkind requires PNG color_type 4 or 6.",
    buildPayload(formEl) {
      const usesRaw = fieldValue(formEl, "intended_uses");
      return {
        episode_id: fieldValue(formEl, "episode_id"),
        kind: fieldValue(formEl, "kind"),
        subkind: fieldValue(formEl, "subkind"),
        file: fieldValue(formEl, "file"),
        sidecar: fieldValue(formEl, "sidecar"),
        registered_by: fieldValue(formEl, "registered_by"),
        material_id: fieldValue(formEl, "material_id"),
        intended_uses: usesRaw
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      };
    },
    invoke: (payload) => window.clipPipe.registerMaterial(payload),
  },
  "patch-thumbnail": {
    title: "Run patch-thumbnail",
    reason:
      "patch-thumbnail reads rights/material records, audits slots, patches the template, and writes readback.",
    buildPayload(formEl) {
      return {
        input: fieldValue(formEl, "input"),
        output_result: fieldValue(formEl, "output_result"),
      };
    },
    invoke: (payload) => window.clipPipe.patchThumbnail(payload),
  },
  "init-edit-pack": {
    title: "Run init-edit-pack",
    reason:
      "init-edit-pack writes <root>/<episode_id>/edit_pack.json skeleton. Manual; auto cut detection (ED-02) is not in MVP.",
    buildPayload(formEl) {
      return {
        episode_id: fieldValue(formEl, "episode_id"),
        root: fieldValue(formEl, "root"),
        force: formEl.querySelector('[data-field="force"]').checked,
      };
    },
    invoke: (payload) => window.clipPipe.initEditPack(payload),
  },
  "validate-edit-pack": {
    title: "Run validate-edit-pack",
    reason:
      "validate-edit-pack is read-only schema check. exit 1 means schema/range/reference issues that block downstream Editing work.",
    buildPayload(formEl) {
      return { edit_pack: fieldValue(formEl, "edit_pack") };
    },
    invoke: (payload) => window.clipPipe.validateEditPack(payload),
  },
  "add-cut-candidate": {
    title: "Run add-cut-candidate",
    reason:
      "add-cut-candidate appends one cut to edit_pack.json. context_status is recorded but not auto-checked here (manual judgement).",
    buildPayload(formEl) {
      return {
        edit_pack: fieldValue(formEl, "edit_pack"),
        start_seconds: fieldValue(formEl, "start_seconds"),
        end_seconds: fieldValue(formEl, "end_seconds"),
        cut_id: fieldValue(formEl, "cut_id"),
        source: fieldValue(formEl, "source"),
        reason: fieldValue(formEl, "reason"),
        confidence: fieldValue(formEl, "confidence"),
        context_status: fieldValue(formEl, "context_status"),
        select: formEl.querySelector('[data-field="select"]').checked,
      };
    },
    invoke: (payload) => window.clipPipe.addCutCandidate(payload),
  },
};

function summarisePayload(payload) {
  return Object.entries(payload)
    .filter(([, v]) => v !== "" && v !== undefined && v !== null && v !== false && !(Array.isArray(v) && v.length === 0))
    .map(([k, v]) => `  ${k} = ${Array.isArray(v) ? v.join(",") : v}`)
    .join("\n");
}

const optionalFieldsByAction = {
  "set-compliance": new Set(),
  "register-material": new Set(["subkind", "material_id"]),
  "patch-thumbnail": new Set(),
  "init-edit-pack": new Set(["root", "force"]),
  "validate-edit-pack": new Set(),
  "add-cut-candidate": new Set([
    "cut_id",
    "source",
    "reason",
    "confidence",
    "context_status",
    "select",
  ]),
};

Object.entries(actionForms).forEach(([key, formEl]) => {
  if (!formEl) return;
  formEl.addEventListener("submit", async (event) => {
    event.preventDefault();
    const meta = actionMeta[key];
    const payload = meta.buildPayload(formEl);

    // basic local validation
    const missing = Object.entries(payload).filter(([, v]) => {
      if (Array.isArray(v)) return v.length === 0;
      if (typeof v === "boolean") return false;
      return v === "" || v === undefined || v === null;
    });
    const optional = optionalFieldsByAction[key] || new Set();
    const trulyMissing = missing
      .map(([k]) => k)
      .filter((k) => !optional.has(k));
    if (trulyMissing.length > 0) {
      const pre = actionResults[key];
      pre.hidden = false;
      pre.classList.remove("ok");
      pre.classList.add("fail");
      pre.textContent = `missing required fields: ${trulyMissing.join(", ")}`;
      return;
    }

    const ok = await showConfirm({
      title: meta.title,
      summary: "About to run the following CLI in the repo. This is a local action only; no network calls.",
      command: `python -m src.cli.main ${key}\n${summarisePayload(payload)}`,
      reason: meta.reason,
    });
    if (!ok) return;

    const submit = formEl.querySelector("button[type=submit]");
    submit.disabled = true;
    const original = submit.textContent;
    submit.textContent = "Running…";
    try {
      const result = await meta.invoke(payload);
      renderActionResult(key, result);
      await refreshStatus();
    } finally {
      submit.disabled = false;
      submit.textContent = original;
    }
  });
});

refreshStatus();
