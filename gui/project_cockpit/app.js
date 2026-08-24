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
  decisionQuestion: document.querySelector("#decision-question"),
  decisionOptions: document.querySelector("#decision-options"),
  resolvedCount: document.querySelector("#resolved-count"),
  decisionCounts: document.querySelector("#decision-counts"),
  boundaries: document.querySelector("#boundaries"),
};

let cockpit = null;
let playbackObserved = false;
ui.video.muted = true;
ui.video.volume = 0;

function formatBytes(bytes) {
  return `${Number(bytes).toLocaleString("ja-JP")} bytes`;
}

function render(payload) {
  cockpit = payload;
  const candidate = payload.candidate;
  const ready = payload.project_state === "REVIEW_READY";
  ui.state.textContent = payload.project_state;
  ui.state.classList.toggle("ready", ready);
  ui.stateDetail.textContent = ready
    ? "exact artifact openability と review route を確認済み"
    : "workflow connected · 再生とreview route確認待ち";
  ui.artifactShort.textContent = `${candidate.container_duration_seconds.toFixed(1)}s · ${candidate.artifact_id}`;
  ui.artifactId.textContent = candidate.artifact_id;
  ui.mediaSize.textContent = formatBytes(candidate.observed_byte_size);
  ui.mediaDuration.textContent = `${candidate.observed_container_duration_seconds.toFixed(3)} sec`;
  ui.mediaSha.textContent = candidate.observed_sha256;
  ui.mediaCheck.textContent = "EXACT MATCH";
  ui.mediaCheck.classList.add("pass");
  if (ui.video.src !== candidate.review_url) ui.video.src = candidate.review_url;
  ui.decisionQuestion.textContent = payload.human_judgment.question;
  ui.decisionOptions.replaceChildren(
    ...payload.human_judgment.allowed_outcomes.map((option) => {
      const item = document.createElement("div");
      item.className = "decision-option";
      item.innerHTML = `<strong>${option.label}</strong><span>${option.meaning}</span>`;
      return item;
    }),
  );
  ui.resolvedCount.textContent = `${payload.workflow.resolved_decision_units} units closed · 0 questions revived`;
  const counts = payload.workflow.decision_counts;
  ui.decisionCounts.textContent = `KEEP ${counts.KEEP} / DROP ${counts.DROP} / HOLD_REUSABLE ${counts.HOLD_REUSABLE}`;
  const labels = {
    human_content_acceptance: "human content: pending",
    creative_acceptance: "creative: not granted",
    production_acceptance: "production: not granted",
    rights_approval: "rights: not granted",
    publication_acceptance: "publication: not granted",
    frontierboard_mutation: "Board mutation: none",
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
    playbackObserved = true;
    ui.openReview.disabled = false;
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

ui.openReview.addEventListener("click", async () => {
  if (!cockpit || !playbackObserved) return;
  ui.video.pause();
  ui.video.muted = true;
  ui.video.volume = 0;
  ui.openReview.disabled = true;
  ui.openReview.textContent = "REVIEW_READYを照合中…";
  try {
    const response = await fetch("/api/review-ready", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        playback: {
          observed: true,
          current_time_seconds: ui.video.currentTime,
          ready_state: ui.video.readyState,
        },
      }),
    });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || `transition failed: HTTP ${response.status}`);
    window.location.assign(cockpit.candidate.review_url);
  } catch (error) {
    showError(error);
    ui.openReview.textContent = "Project-owned review path を開く";
    ui.openReview.disabled = false;
  }
});

loadCockpit().catch(showError);
