from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import subprocess
import threading
import webbrowser
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .serve_review import create_review_server

DEFAULT_CONFIG = Path("docs/output_layer/clip_project_cockpit_v2.json")


@dataclass(frozen=True)
class CockpitSnapshot:
    config: dict[str, Any]
    workflow_receipt: dict[str, Any]
    workflow_readback: dict[str, Any]
    navigation_calibration: dict[str, Any]
    legacy_task_rejection: dict[str, Any]
    task_board: dict[str, Any]
    config_path: Path
    workflow_receipt_path: Path
    workflow_readback_path: Path
    navigation_calibration_path: Path
    legacy_task_rejection_path: Path
    task_board_path: Path
    media_path: Path
    state_path: Path
    observed_media_sha256: str
    observed_media_bytes: int
    observed_duration_seconds: float


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root must be an object: {path}")
    return value


def _probe_duration_seconds(media_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(media_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ValueError(f"ffprobe failed for {media_path}: {result.stderr.strip()}")
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise ValueError(f"ffprobe returned invalid duration: {result.stdout!r}") from exc


def load_cockpit_snapshot(
    *,
    repo_root: Path,
    config_path: Path,
    duration_probe: Callable[[Path], float] = _probe_duration_seconds,
) -> CockpitSnapshot:
    root = repo_root.resolve()
    resolved_config_path = (root / config_path).resolve() if not config_path.is_absolute() else config_path.resolve()
    config = _load_json(resolved_config_path)
    if config.get("schema_version") != "clippipegen.project_cockpit.v2":
        raise ValueError("unsupported project cockpit schema_version")

    workflow_config = config.get("workflow_receipt") or {}
    readback_config = config.get("workflow_readback") or {}
    navigation_config = config.get("navigation_calibration") or {}
    rejection_config = config.get("legacy_task_rejection") or {}
    task_board_config = config.get("task_board") or {}
    candidate = config.get("candidate") or {}
    state_receipt = config.get("state_receipt") or {}
    workflow_receipt_path = (root / str(workflow_config.get("path", ""))).resolve()
    workflow_readback_path = (root / str(readback_config.get("path", ""))).resolve()
    navigation_calibration_path = (root / str(navigation_config.get("path", ""))).resolve()
    legacy_task_rejection_path = (root / str(rejection_config.get("path", ""))).resolve()
    task_board_path = (root / str(task_board_config.get("path", ""))).resolve()
    package_root = (root / str(candidate.get("package_root", ""))).resolve()
    media_path = (package_root / str(candidate.get("media_name", ""))).resolve()
    state_path = (root / str(state_receipt.get("path", ""))).resolve()
    for path in (
        resolved_config_path,
        workflow_receipt_path,
        workflow_readback_path,
        navigation_calibration_path,
        legacy_task_rejection_path,
        task_board_path,
        package_root,
        media_path,
        state_path.parent,
    ):
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"cockpit path escapes repo root: {path}") from exc
    if not workflow_receipt_path.is_file():
        raise ValueError(f"workflow receipt is missing: {workflow_receipt_path}")
    if not workflow_readback_path.is_file():
        raise ValueError(f"workflow readback is missing: {workflow_readback_path}")
    if not navigation_calibration_path.is_file():
        raise ValueError(f"navigation calibration is missing: {navigation_calibration_path}")
    if not legacy_task_rejection_path.is_file():
        raise ValueError(f"legacy task rejection is missing: {legacy_task_rejection_path}")
    if not task_board_path.is_file():
        raise ValueError(f"task board is missing: {task_board_path}")
    if not package_root.is_dir():
        raise ValueError(f"candidate package is missing: {package_root}")
    if not media_path.is_file():
        raise ValueError(f"candidate media is missing: {media_path}")

    workflow_sha = _sha256(workflow_receipt_path)
    if workflow_sha != str(workflow_config.get("sha256", "")).lower():
        raise ValueError("workflow receipt SHA-256 does not match cockpit authority")
    workflow_receipt = _load_json(workflow_receipt_path)
    if workflow_receipt.get("status") != workflow_config.get("required_status"):
        raise ValueError("workflow receipt status is not connected for review")
    autonomous = workflow_receipt.get("autonomous_resolution") or {}
    if autonomous.get("decision_units_resolved") != 15:
        raise ValueError("workflow receipt must resolve exactly 15 decision units")
    if autonomous.get("item_level_questions_reemitted") != 0:
        raise ValueError("workflow receipt must not re-emit item-level questions")
    human = workflow_receipt.get("human_judgment") or {}
    if human.get("artifact_id") != candidate.get("artifact_id"):
        raise ValueError("workflow receipt candidate identity does not match cockpit authority")

    readback_sha = _sha256(workflow_readback_path)
    if readback_sha != str(readback_config.get("sha256", "")).lower():
        raise ValueError("workflow readback SHA-256 does not match cockpit authority")
    workflow_readback = _load_json(workflow_readback_path)
    if workflow_readback.get("status") != readback_config.get("required_status"):
        raise ValueError("workflow readback is not connected in nonblocking mode")
    readback_artifact = workflow_readback.get("artifact") or {}
    if readback_artifact.get("artifact_id") != candidate.get("artifact_id"):
        raise ValueError("workflow readback artifact identity does not match cockpit authority")
    if readback_artifact.get("sha256") != str(candidate.get("sha256", "")).lower():
        raise ValueError("workflow readback media SHA-256 does not match cockpit authority")
    decision_path = workflow_readback.get("decision_path") or {}
    if decision_path.get("item_level_questions_reemitted") != 0:
        raise ValueError("workflow readback must not re-emit item-level questions")
    legacy_gate = workflow_readback.get("legacy_gate") or {}
    if legacy_gate.get("blocks_workflow") is not False or legacy_gate.get("mandatory_human_judgment_count") != 0:
        raise ValueError("legacy whole-candidate gate must remain nonblocking")

    navigation_sha = _sha256(navigation_calibration_path)
    if navigation_sha != str(navigation_config.get("sha256", "")).lower():
        raise ValueError("navigation calibration SHA-256 does not match cockpit authority")
    navigation_calibration = _load_json(navigation_calibration_path)
    calibration_scope = navigation_calibration.get("calibration_scope") or {}
    if calibration_scope.get("artifact_identity") != candidate.get("artifact_id"):
        raise ValueError("navigation calibration artifact identity does not match cockpit authority")
    if calibration_scope.get("output_sha256") != str(candidate.get("sha256", "")).lower():
        raise ValueError("navigation calibration media SHA-256 does not match cockpit authority")
    navigation_units = navigation_calibration.get("decision_units") or []
    required_unit_count = int(navigation_config.get("unit_count", 0))
    if required_unit_count != 8 or len(navigation_units) != required_unit_count:
        raise ValueError("navigation calibration must expose exactly eight units")
    previous_end = 0.0
    for index, unit in enumerate(navigation_units):
        output_range = unit.get("output_range_seconds") or []
        if len(output_range) != 2:
            raise ValueError("navigation unit must have an output range")
        start, end = map(float, output_range)
        if start < 0 or end <= start or abs(start - previous_end) > 0.001:
            raise ValueError("navigation units must be positive contiguous ranges")
        if not unit.get("unit_id") or not unit.get("content_label"):
            raise ValueError("navigation unit must have an id and label")
        previous_end = end
    if abs(previous_end - float(candidate.get("editorial_duration_seconds"))) > 0.05:
        raise ValueError("navigation units must cover the editorial duration")
    if previous_end > float(candidate.get("container_duration_seconds")):
        raise ValueError("navigation units exceed the candidate duration")

    rejection_sha = _sha256(legacy_task_rejection_path)
    if rejection_sha != str(rejection_config.get("sha256", "")).lower():
        raise ValueError("legacy task rejection SHA-256 does not match cockpit authority")
    legacy_task_rejection = _load_json(legacy_task_rejection_path)
    if legacy_task_rejection.get("status") != "REJECTED_LEGACY_TASK_SETTING":
        raise ValueError("legacy task rejection is not authoritative")
    if legacy_task_rejection.get("artifact", {}).get("sha256") != str(candidate.get("sha256", "")).lower():
        raise ValueError("legacy task rejection candidate identity does not match cockpit authority")

    task_board_sha = _sha256(task_board_path)
    if task_board_sha != str(task_board_config.get("sha256", "")).lower():
        raise ValueError("task board SHA-256 does not match cockpit authority")
    task_board = _load_json(task_board_path)
    if task_board.get("status") != "ACTIVE_TEMPORARY_PROJECT_WORK_SURFACE":
        raise ValueError("task board is not active")
    tasks = task_board.get("tasks") or []
    if len(tasks) != 10 or len({item.get("task_id") for item in tasks}) != 10:
        raise ValueError("task board must expose exactly ten unique tasks")

    observed_media_bytes = media_path.stat().st_size
    observed_media_sha256 = _sha256(media_path)
    observed_duration_seconds = duration_probe(media_path)
    if observed_media_bytes != candidate.get("byte_size"):
        raise ValueError("candidate byte size does not match cockpit authority")
    if observed_media_sha256 != str(candidate.get("sha256", "")).lower():
        raise ValueError("candidate SHA-256 does not match cockpit authority")
    if abs(observed_duration_seconds - float(candidate.get("container_duration_seconds"))) > 0.05:
        raise ValueError("candidate container duration does not match cockpit authority")
    return CockpitSnapshot(
        config=config,
        workflow_receipt=workflow_receipt,
        workflow_readback=workflow_readback,
        navigation_calibration=navigation_calibration,
        legacy_task_rejection=legacy_task_rejection,
        task_board=task_board,
        config_path=resolved_config_path,
        workflow_receipt_path=workflow_receipt_path,
        workflow_readback_path=workflow_readback_path,
        navigation_calibration_path=navigation_calibration_path,
        legacy_task_rejection_path=legacy_task_rejection_path,
        task_board_path=task_board_path,
        media_path=media_path,
        state_path=state_path,
        observed_media_sha256=observed_media_sha256,
        observed_media_bytes=observed_media_bytes,
        observed_duration_seconds=observed_duration_seconds,
    )


def _read_state(snapshot: CockpitSnapshot) -> dict[str, Any] | None:
    if not snapshot.state_path.is_file():
        return None
    state = _load_json(snapshot.state_path)
    if state.get("artifact_id") != snapshot.config["candidate"]["artifact_id"]:
        raise ValueError("cockpit state artifact identity does not match current candidate")
    if state.get("media_sha256") != snapshot.observed_media_sha256:
        raise ValueError("cockpit state media SHA-256 does not match current candidate")
    return state


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def _range_readback(review_url: str) -> dict[str, Any]:
    request = Request(review_url, headers={"Range": "bytes=0-31"})
    try:
        with urlopen(request, timeout=5) as response:
            body = response.read()
            status = response.status
            content_range = response.headers.get("Content-Range")
    except HTTPError as exc:
        raise ValueError(f"project-owned review route returned HTTP {exc.code}") from exc
    if status != HTTPStatus.PARTIAL_CONTENT or len(body) != 32:
        raise ValueError("project-owned review route did not return the expected 32-byte Range readback")
    return {"http_status": status, "bytes_read": len(body), "content_range": content_range}


def transition_review_ready(
    *,
    snapshot: CockpitSnapshot,
    playback: dict[str, Any],
    review_url: str,
    route_validator: Callable[[str], dict[str, Any]] = _range_readback,
) -> dict[str, Any]:
    if playback.get("observed") is not True:
        raise ValueError("artifact playback was not observed")
    try:
        current_time = float(playback.get("current_time_seconds", 0))
        ready_state = int(playback.get("ready_state", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid playback readback") from exc
    if current_time <= 0 or ready_state < 2:
        raise ValueError("artifact playback must advance beyond 0 seconds with readyState >= 2")
    route_readback = route_validator(review_url)
    now = datetime.now(timezone.utc).isoformat()
    existing = _read_state(snapshot)
    transitioned_at = (existing or {}).get("transition", {}).get("transitioned_at_utc", now)
    candidate = snapshot.config["candidate"]
    workflow_sha = _sha256(snapshot.workflow_receipt_path)
    state = {
        "schema_version": "clippipegen.project_cockpit_task_surface_state.v2",
        "requirement_id": snapshot.config["requirement_id"],
        "cockpit_artifact_id": snapshot.config["artifact_id"],
        "artifact_id": candidate["artifact_id"],
        "status": "ARTIFACT_ROUTE_READY",
        "media_sha256": snapshot.observed_media_sha256,
        "media_bytes": snapshot.observed_media_bytes,
        "container_duration_seconds": snapshot.observed_duration_seconds,
        "transition": {
            "from": "TASK_BOARD_ACTIVE",
            "to": "ARTIFACT_ROUTE_READY",
            "transitioned_at_utc": transitioned_at,
            "last_verified_at_utc": now,
            "meaning": "The exact artifact route is established without creating a whole-artifact judgment gate.",
        },
        "checks": {
            "workflow_receipt_sha256": workflow_sha,
            "workflow_decision_units_resolved": 15,
            "item_level_questions_reemitted": 0,
            "media_playback": {
                "status": "PASS",
                "current_time_seconds": current_time,
                "ready_state": ready_state,
            },
            "review_route_range_readback": {"status": "PASS", **route_readback},
        },
        "legacy_task": {
            "status": "REJECTED_LEGACY_TASK_SETTING",
            "human_gate_count": 0,
            "replacement": snapshot.task_board["artifact_id"],
        },
        "boundaries": snapshot.config["boundaries"],
    }
    _atomic_write_json(snapshot.state_path, state)
    return state


def cockpit_payload(snapshot: CockpitSnapshot, *, review_url: str) -> dict[str, Any]:
    state = _read_state(snapshot)
    candidate = snapshot.config["candidate"]
    return {
        "schema_version": snapshot.config["schema_version"],
        "requirement_id": snapshot.config["requirement_id"],
        "cockpit_artifact_id": snapshot.config["artifact_id"],
        "title": snapshot.config["title"],
        "project_state": "TASK_BOARD_ACTIVE",
        "candidate": {
            **candidate,
            "observed_sha256": snapshot.observed_media_sha256,
            "observed_byte_size": snapshot.observed_media_bytes,
            "observed_container_duration_seconds": snapshot.observed_duration_seconds,
            "review_url": review_url,
        },
        "workflow": {
            "status": snapshot.workflow_readback["status"],
            "legacy_status": snapshot.workflow_receipt["status"],
            "blocks_workflow": False,
            "resolved_decision_units": 15,
            "decision_counts": snapshot.workflow_receipt["autonomous_resolution"]["decision_counts"],
            "item_level_questions_reemitted": 0,
        },
        "navigation_units": [
            {
                "unit_id": unit["unit_id"],
                "label": unit["content_label"],
                "start_seconds": float(unit["output_range_seconds"][0]),
                "end_seconds": float(unit["output_range_seconds"][1]),
            }
            for unit in snapshot.navigation_calibration["decision_units"]
        ],
        "legacy_task": snapshot.legacy_task_rejection,
        "task_board": snapshot.task_board,
        "observation_mode": snapshot.config["observation_mode"],
        "boundaries": snapshot.config["boundaries"],
        "state_receipt": state,
    }


class ProjectCockpitHTTPServer(ThreadingHTTPServer):
    daemon_threads = True


class ProjectCockpitRequestHandler(BaseHTTPRequestHandler):
    server_version = "ClipPipeGenProjectCockpit/1.0"

    def do_GET(self) -> None:
        if self.path == "/api/cockpit":
            self._send_json(HTTPStatus.OK, cockpit_payload(self.server.snapshot, review_url=self.server.review_url))  # type: ignore[attr-defined]
            return
        target = "/index.html" if self.path in ("", "/") else self.path
        asset_name = target.lstrip("/")
        if asset_name not in {"index.html", "app.js", "styles.css"}:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        asset_path = self.server.static_root / asset_name  # type: ignore[attr-defined]
        if not asset_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = asset_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(str(asset_path))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/api/review-ready":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 16_384:
                raise ValueError("invalid request body length")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            state = transition_review_ready(
                snapshot=self.server.snapshot,  # type: ignore[attr-defined]
                playback=payload.get("playback") or {},
                review_url=self.server.review_url,  # type: ignore[attr-defined]
            )
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
            return
        self._send_json(HTTPStatus.OK, {"ok": True, "state": state})

    def _send_json(self, status: HTTPStatus, value: dict[str, Any]) -> None:
        body = (json.dumps(value, ensure_ascii=False) + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def create_project_cockpit_server(
    *,
    snapshot: CockpitSnapshot,
    static_root: Path,
    cockpit_port: int,
    review_url: str,
) -> ProjectCockpitHTTPServer:
    if not static_root.is_dir():
        raise ValueError(f"cockpit static root must be a directory: {static_root}")
    server = ProjectCockpitHTTPServer(("127.0.0.1", cockpit_port), ProjectCockpitRequestHandler)
    server.snapshot = snapshot  # type: ignore[attr-defined]
    server.static_root = static_root.resolve()  # type: ignore[attr-defined]
    server.review_url = review_url  # type: ignore[attr-defined]
    return server


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve the exact current Project Cockpit and review route.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--cockpit-port", type=int, default=8061)
    parser.add_argument("--review-port", type=int, default=8060)
    parser.add_argument("--open", action="store_true", dest="open_browser")
    args = parser.parse_args(argv)
    if not 1 <= args.cockpit_port <= 65_535 or not 1 <= args.review_port <= 65_535:
        parser.error("ports must be between 1 and 65535")
    if args.cockpit_port == args.review_port:
        parser.error("cockpit and review ports must be different")

    repo_root = Path(__file__).resolve().parents[2]
    try:
        snapshot = load_cockpit_snapshot(repo_root=repo_root, config_path=args.config)
        review_server = create_review_server(root=snapshot.media_path.parent, port=args.review_port)
        review_url = f"http://127.0.0.1:{args.review_port}/{snapshot.media_path.name}"
        cockpit_server = create_project_cockpit_server(
            snapshot=snapshot,
            static_root=repo_root / "gui" / "project_cockpit",
            cockpit_port=args.cockpit_port,
            review_url=review_url,
        )
    except (OSError, ValueError) as exc:
        print(f"serve-project-cockpit failed: {exc}")
        return 2

    review_thread = threading.Thread(target=review_server.serve_forever, name="review-route", daemon=True)
    review_thread.start()
    cockpit_url = f"http://127.0.0.1:{args.cockpit_port}/"
    print(
        json.dumps(
            {
                "status": "READY",
                "cockpit_url": cockpit_url,
                "review_url": review_url,
                "artifact_id": snapshot.config["candidate"]["artifact_id"],
                "sha256": snapshot.observed_media_sha256,
                "bytes": snapshot.observed_media_bytes,
                "duration_seconds": snapshot.observed_duration_seconds,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    if args.open_browser:
        webbrowser.open(cockpit_url)
    try:
        cockpit_server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        cockpit_server.server_close()
        review_server.shutdown()
        review_server.server_close()
        review_thread.join(timeout=5)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
