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
  renderThumbnail(status.thumbnail);
  renderSettings(status.settings);
}

function renderEpisode(status) {
  const grid = document.querySelector("#status-grid");
  grid.replaceChildren(
    statusCard("Rights", status.rights.state, status.artifacts.rights_manifest.path),
    statusCard("Materials", status.materials.state, status.artifacts.material_ledger.path),
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
    ["auto_fail", (rights.auto_fail || []).length],
  ];
  renderDetails("#rights-content", rows, [...(rights.schema_issues || []), ...(rights.auto_fail || [])]);
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

refreshStatus();
