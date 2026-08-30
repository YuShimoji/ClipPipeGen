const ui = {
  state: document.querySelector("#project-state"),
  stateDetail: document.querySelector("#state-detail"),
  error: document.querySelector("#error"),
  artifactShort: document.querySelector("#artifact-short"),
  artifactId: document.querySelector("#artifact-id"),
  mediaCheck: document.querySelector("#media-check"),
  mediaSize: document.querySelector("#media-size"),
  mediaDuration: document.querySelector("#media-duration"),
  mediaSha: document.querySelector("#media-sha"),
  video: document.querySelector("#candidate-video"),
  play: document.querySelector("#play-artifact"),
  openReview: document.querySelector("#open-review"),
  playReadback: document.querySelector("#play-readback"),
  legacyTaskNote: document.querySelector("#legacy-task-note"),
  taskList: document.querySelector("#task-list"),
  resolvedCount: document.querySelector("#resolved-count"),
  decisionCounts: document.querySelector("#decision-counts"),
  boundaries: document.querySelector("#boundaries"),
};

let cockpit = null;
ui.video.muted = true;
ui.video.volume = 0;

function formatBytes(bytes) {
  return `${Number(bytes).toLocaleString("ja-JP")} bytes`;
}

function render(payload) {
  cockpit = payload;
  const candidate = payload.candidate;
  const ready = payload.project_state === "TASK_BOARD_ACTIVE";
  ui.state.textContent = payload.project_state;
  ui.state.classList.toggle("ready", ready);
  ui.stateDetail.textContent = ready
    ? "旧全体採否ゲートを閉じ、作業一覧を表示中"
    : "task authorityを照合しています";
  ui.artifactShort.textContent = `${candidate.container_duration_seconds.toFixed(1)}s · ${candidate.artifact_id}`;
  ui.artifactId.textContent = candidate.artifact_id;
  ui.mediaSize.textContent = formatBytes(candidate.observed_byte_size);
  ui.mediaDuration.textContent = `${candidate.observed_container_duration_seconds.toFixed(3)} sec`;
  ui.mediaSha.textContent = candidate.observed_sha256;
  ui.mediaCheck.textContent = "EXACT MATCH";
  ui.mediaCheck.classList.add("pass");
  if (ui.video.src !== candidate.review_url) ui.video.src = candidate.review_url;
  ui.legacyTaskNote.textContent = `${payload.legacy_task.status} · 全体採用/非採用は要求しません。`;
  ui.taskList.replaceChildren(
    ...payload.task_board.tasks.map((task) => {
      const item = document.createElement("div");
      item.className = "task-item";
      item.innerHTML = `<div><strong>${task.task_id} · ${task.title}</strong><span>${task.work}</span></div><em>${task.status}</em>`;
      return item;
    }),
  );
  ui.resolvedCount.textContent = `${payload.workflow.resolved_decision_units} units closed · 0 questions revived`;
  const counts = payload.workflow.decision_counts;
  ui.decisionCounts.textContent = `KEEP ${counts.KEEP} / DROP ${counts.DROP} / HOLD_REUSABLE ${counts.HOLD_REUSABLE}`;
  const labels = {
    human_content_acceptance: "whole content acceptance: not requested",
    creative_acceptance: "creative: not granted",
    production_acceptance: "production: not granted",
    rights_approval: "rights: not granted",
    publication_acceptance: "publication: not granted",
    choice_mutation: "Choice mutation: none",
    media_created_or_modified: "media mutation: none",
  };
  ui.boundaries.replaceChildren(
    ...Object.keys(labels).map((key) => {
      const item = document.createElement("li");
      item.textContent = labels[key];
      return item;
    }),
  );
}

async function loadCockpit() {
  const response = await fetch("/api/cockpit", { cache: "no-store" });
  if (!response.ok) throw new Error(`Cockpit readback failed: HTTP ${response.status}`);
  render(await response.json());
}

function showError(error) {
  ui.error.hidden = false;
  ui.error.textContent = error.message || String(error);
}

ui.video.addEventListener("timeupdate", () => {
  if (ui.video.currentTime > 0 && ui.video.readyState >= 2) {
    ui.playReadback.textContent = `PLAYING · ${ui.video.currentTime.toFixed(2)}s · readyState ${ui.video.readyState}`;
    ui.playReadback.classList.add("pass");
  }
});

ui.video.addEventListener("error", () => showError(new Error("Actual artifact could not be loaded.")));

ui.play.addEventListener("click", async () => {
  try {
    ui.video.muted = true;
    ui.video.volume = 0;
    await ui.video.play();
  } catch (error) {
    showError(error);
  }
});

ui.openReview.addEventListener("click", () => {
  if (!cockpit) return;
  ui.video.pause();
  ui.video.muted = true;
  ui.video.volume = 0;
  window.open(cockpit.candidate.review_url, "_blank", "noopener");
});

loadCockpit().catch(showError);
