"""Build one provenance-bound edit-ready Source Packet.

The command composes the existing video/audio acquisition and optional real
STT CLIs. It adds strict transcript-authority selection, input/cache binding,
integrity validation, and a passive operator readback.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import io
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from src.cli import fetch_source_audio, fetch_source_video, transcribe_audio
from src.integrations.stt.vosk_adapter import try_read_wav_info
from src.pipeline.edit_ready_source_packet import (
    READY_STATE,
    AuthorityCandidate,
    SourcePacketBlocked,
    blocked_result,
    build_packet,
    caption_authority_candidate,
    choose_authority,
    display_path,
    input_fingerprint,
    load_json,
    parse_youtube_json3_caption,
    render_report_html,
    save_json,
    sha256_file,
    transcript_authority_candidate,
    validate_packet,
    validate_packet_files,
)
from src.pipeline.rights_manifest import (
    save_rights_manifest,
    validate_rights_manifest,
)

SOURCE_VIDEO_MATERIAL_ID = "source_video"
SOURCE_AUDIO_MATERIAL_ID = "source_audio"


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="build-edit-ready-source-packet",
        description=(
            "Acquire a URL/local source and build a provenance-bound packet for "
            "editorial planning, Timeline IR, subtitle, and render consumers."
        ),
    )
    parser.add_argument("--packet-id", required=True)
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--source-locator", required=True)
    parser.add_argument("--source-identity", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--rights-manifest", required=True)
    parser.add_argument("--caption-track")
    parser.add_argument(
        "--caption-authority",
        choices=("provider_official", "verified_sidecar"),
    )
    parser.add_argument("--caption-provider-locator")
    parser.add_argument("--transcript")
    parser.add_argument("--stt-engine", choices=("vosk",))
    parser.add_argument("--stt-model")
    parser.add_argument("--ffmpeg-path")
    parser.add_argument("--ffprobe-path")
    parser.add_argument("--yt-dlp-path")
    parser.add_argument("--root", default="episodes")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    root = Path(args.root)
    episode_dir = root / args.episode_id
    packet_dir = episode_dir / "source_packet" / args.packet_id
    packet_path = packet_dir / "source_packet.json"
    report_path = packet_dir / "source_packet_report.html"
    normalized_path = packet_dir / "normalized_transcript.json"
    fingerprint_value: str | None = None

    try:
        inputs = _validated_inputs(args)
        fingerprint_value = input_fingerprint(inputs["fingerprint_inputs"])
        resumed = _resume_result(
            args=args,
            packet_path=packet_path,
            report_path=report_path,
            fingerprint_value=fingerprint_value,
        )
        if resumed is not None:
            _print_result(resumed, fmt=args.format)
            return 0
        if packet_path.exists():
            raise SourcePacketBlocked(
                "packet_already_exists",
                f"packet already exists; use --resume or a new packet id: {packet_path}",
            )

        packet_dir.mkdir(parents=True, exist_ok=True)
        evidence_dir = packet_dir / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        rights_snapshot_path = evidence_dir / "rights_snapshot.json"
        shutil.copy2(inputs["rights_path"], rights_snapshot_path)
        runtime_rights_path = episode_dir / "rights_manifest.json"
        runtime_rights = copy.deepcopy(inputs["rights"])
        runtime_rights["episode_id"] = args.episode_id
        runtime_rights["source_packet_snapshot"] = {
            "path": display_path(rights_snapshot_path, Path.cwd()),
            "sha256": inputs["rights_sha256"],
        }
        save_rights_manifest(runtime_rights, runtime_rights_path)

        video_receipt = _acquire_video(args, episode_dir)
        video_path = _resolve_output_path(video_receipt["output_path"])
        if not video_path.exists():
            raise SourcePacketBlocked(
                "acquired_video_missing",
                f"video receipt output does not exist: {video_path}",
            )
        video_sha = sha256_file(video_path)
        if video_sha != video_receipt.get("sha256"):
            raise SourcePacketBlocked(
                "acquired_video_integrity_mismatch",
                "acquired video hash does not match its receipt",
            )
        metadata = video_receipt.get("video_metadata") or {}
        source_duration = _positive_float(
            metadata.get("duration_seconds"),
            code="source_duration_missing",
            label="source video duration",
        )
        resolution = str(metadata.get("resolution") or "")
        if not resolution:
            raise SourcePacketBlocked(
                "source_resolution_missing",
                "source video probe did not report a resolution",
            )

        audio_receipt = _acquire_audio(args, episode_dir, video_path)
        audio_path = _resolve_output_path(audio_receipt["output_path"])
        if not audio_path.exists():
            raise SourcePacketBlocked(
                "acquired_audio_missing",
                f"audio receipt output does not exist: {audio_path}",
            )
        audio_sha = sha256_file(audio_path)
        if audio_sha != audio_receipt.get("sha256"):
            raise SourcePacketBlocked(
                "acquired_audio_integrity_mismatch",
                "acquired audio hash does not match its receipt",
            )
        audio_info = try_read_wav_info(audio_path)
        if audio_info is None or audio_info.duration_seconds <= 0:
            raise SourcePacketBlocked(
                "source_audio_unreadable",
                "normalized source audio must be a readable non-empty WAV",
            )
        source_audio = {
            "path": display_path(audio_path, Path.cwd()),
            "material_id": SOURCE_AUDIO_MATERIAL_ID,
            "sha256": audio_sha,
            "duration_seconds": audio_info.duration_seconds,
            "sample_rate_hz": audio_info.sample_rate_hz,
            "channels": audio_info.channels,
        }

        candidates, evidence_paths = _build_candidates(
            args=args,
            inputs=inputs,
            evidence_dir=evidence_dir,
            episode_dir=episode_dir,
            source_audio=source_audio,
            source_duration=source_duration,
        )
        selected = choose_authority(candidates)
        if selected.transcript is None:
            raise SourcePacketBlocked(
                "selected_authority_transcript_missing",
                "selected transcript authority did not yield normalized segments",
            )
        save_json(selected.transcript, normalized_path)

        video_receipt_path = (
            episode_dir / "materials" / SOURCE_VIDEO_MATERIAL_ID / "fetch_receipt.json"
        )
        audio_receipt_path = (
            episode_dir / "materials" / SOURCE_AUDIO_MATERIAL_ID / "fetch_receipt.json"
        )
        ledger_path = episode_dir / "material_ledger.json"
        video_sidecar = (
            episode_dir / "materials" / SOURCE_VIDEO_MATERIAL_ID / "sidecar.json"
        )
        audio_sidecar = (
            episode_dir / "materials" / SOURCE_AUDIO_MATERIAL_ID / "sidecar.json"
        )
        artifact_paths = [
            ("source_video", video_path),
            ("source_audio", audio_path),
            ("source_video_receipt", video_receipt_path),
            ("source_audio_receipt", audio_receipt_path),
            ("source_video_sidecar", video_sidecar),
            ("source_audio_sidecar", audio_sidecar),
            ("material_ledger", ledger_path),
            ("runtime_rights_manifest", runtime_rights_path),
            ("rights_snapshot", rights_snapshot_path),
            ("normalized_transcript", normalized_path),
            *evidence_paths,
        ]
        artifact_manifest = _artifact_manifest(artifact_paths)
        rights_status = str(
            (inputs["rights"].get("compliance_check") or {}).get("status") or "pending"
        )
        source = {
            "identity": args.source_identity,
            "provider": _source_provider(args.source_identity),
            "locator": _safe_locator(args.source_locator),
            "path": display_path(video_path, Path.cwd()),
            "sha256": video_sha,
            "byte_size": video_path.stat().st_size,
            "duration_seconds": source_duration,
            "resolution": resolution,
            "acquisition_mode": video_receipt["mode"],
            "material_id": SOURCE_VIDEO_MATERIAL_ID,
        }
        acquisition = {
            "source_video": _receipt_readback(video_receipt_path, video_receipt),
            "source_audio": _receipt_readback(audio_receipt_path, audio_receipt),
            "high_cost_stages_executed": ["source_video_acquisition", "audio_normalization"],
            "resume_supported": True,
        }
        materials = {
            "ledger_path": display_path(ledger_path, Path.cwd()),
            "source_video_sidecar": display_path(video_sidecar, Path.cwd()),
            "source_audio_sidecar": display_path(audio_sidecar, Path.cwd()),
            "source_audio": source_audio,
        }
        rights = {
            "snapshot_path": display_path(rights_snapshot_path, Path.cwd()),
            "snapshot_sha256": inputs["rights_sha256"],
            "runtime_manifest_path": display_path(runtime_rights_path, Path.cwd()),
            "status": rights_status,
            "approval": False,
        }
        packet = build_packet(
            packet_id=args.packet_id,
            episode_id=args.episode_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            input_fingerprint_value=fingerprint_value,
            source=source,
            acquisition=acquisition,
            materials=materials,
            rights=rights,
            candidates=candidates,
            selected=selected,
            normalized_transcript_path=normalized_path,
            artifact_manifest=artifact_manifest,
            warnings=[
                f"rights status is {rights_status}; production and publishing remain blocked",
                "transcript authority is operational input, not human editorial acceptance",
                "packet readiness does not approve lyrics, proper names, third-party IP, or public use",
            ],
        )
        issues = validate_packet(packet)
        if issues:
            raise SourcePacketBlocked(
                "packet_contract_invalid",
                "packet failed contract validation",
                details={"issues": issues},
            )
        file_issues = validate_packet_files(packet, base_dir=Path.cwd())
        if file_issues:
            raise SourcePacketBlocked(
                "packet_artifact_integrity_invalid",
                "packet artifact manifest failed validation",
                details={"issues": file_issues},
            )
        save_json(packet, packet_path)
        report_path.write_text(render_report_html(packet), encoding="utf-8")
        result = _success_result(
            packet=packet,
            packet_path=packet_path,
            report_path=report_path,
            resumed=False,
            acquisition_executed=True,
        )
        _print_result(result, fmt=args.format)
        return 0
    except SourcePacketBlocked as exc:
        result = blocked_result(
            packet_id=args.packet_id,
            episode_id=args.episode_id,
            input_fingerprint_value=fingerprint_value,
            error=exc,
        )
        if not packet_path.exists():
            packet_dir.mkdir(parents=True, exist_ok=True)
            save_json(result, packet_dir / "blocked_result.json")
        _print_result(result, fmt=args.format, error=True)
        return 3
    except (OSError, KeyError, TypeError, ValueError) as exc:
        blocked = SourcePacketBlocked(
            "source_packet_build_failed",
            f"source packet build failed: {exc}",
        )
        result = blocked_result(
            packet_id=args.packet_id,
            episode_id=args.episode_id,
            input_fingerprint_value=fingerprint_value,
            error=blocked,
        )
        if not packet_path.exists():
            packet_dir.mkdir(parents=True, exist_ok=True)
            save_json(result, packet_dir / "blocked_result.json")
        _print_result(result, fmt=args.format, error=True)
        return 3


def _validated_inputs(args: argparse.Namespace) -> dict[str, Any]:
    source_is_url = _is_url(args.source_locator)
    source_path: Path | None = None
    source_input_sha: str | None = None
    if source_is_url:
        parsed = urlparse(args.source_locator)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise SourcePacketBlocked(
                "source_url_invalid",
                "source URL must use http(s) and include a host",
            )
    else:
        source_path = Path(args.source_locator).resolve()
        if not source_path.exists() or not source_path.is_file():
            raise SourcePacketBlocked(
                "source_local_file_missing",
                f"local source file does not exist: {source_path}",
            )
        source_input_sha = sha256_file(source_path)

    rights_path = Path(args.rights_manifest).resolve()
    rights = load_json(rights_path, label="rights_manifest")
    rights_issues = validate_rights_manifest(rights)
    if rights_issues:
        raise SourcePacketBlocked(
            "rights_manifest_invalid",
            "rights manifest failed schema validation",
            details={
                "issues": [
                    f"{issue.code}@{issue.field}: {issue.message}"
                    for issue in rights_issues
                ]
            },
        )
    rights_sha = sha256_file(rights_path)

    caption_values = (
        args.caption_track,
        args.caption_authority,
        args.caption_provider_locator,
    )
    if any(caption_values) and not all(caption_values):
        raise SourcePacketBlocked(
            "caption_configuration_incomplete",
            "--caption-track, --caption-authority, and --caption-provider-locator must be supplied together",
        )
    caption_path: Path | None = None
    caption_payload: dict[str, Any] | None = None
    caption_sha: str | None = None
    if args.caption_track:
        caption_path = Path(args.caption_track).resolve()
        caption_payload = load_json(caption_path, label="caption_track")
        caption_sha = sha256_file(caption_path)
        parse_youtube_json3_caption(
            caption_payload,
            language=args.language,
            provider_locator=args.caption_provider_locator,
            source_duration_seconds=None,
        )

    transcript_path: Path | None = None
    transcript_payload: dict[str, Any] | None = None
    transcript_sha: str | None = None
    if args.transcript:
        transcript_path = Path(args.transcript).resolve()
        transcript_payload = load_json(transcript_path, label="transcript")
        transcript_sha = sha256_file(transcript_path)
        stt = (
            transcript_payload.get("stt")
            if isinstance(transcript_payload.get("stt"), dict)
            else {}
        )
        if (
            stt.get("real_transcript") is not True
            or str(stt.get("engine") or "") in {"fake", "fixture", "deterministic_fake"}
            or str(stt.get("provider") or "") in {"fake", "fixture", "deterministic_fake"}
        ):
            raise SourcePacketBlocked(
                "fixture_transcript_authority_forbidden",
                "fixture/fake transcripts cannot become Source Packet authority",
            )
    if args.stt_engine and not args.stt_model:
        raise SourcePacketBlocked(
            "stt_model_missing",
            "--stt-model is required when --stt-engine vosk is configured",
        )
    if args.stt_model and not args.stt_engine:
        raise SourcePacketBlocked(
            "stt_engine_missing",
            "--stt-engine is required when --stt-model is configured",
        )
    if not caption_path and not transcript_path and not args.stt_engine:
        raise SourcePacketBlocked(
            "transcript_authority_input_missing",
            "provide an authoritative caption, real transcript, or configured Vosk STT",
        )

    fingerprint_inputs = {
        "packet_id": args.packet_id,
        "episode_id": args.episode_id,
        "source_identity": args.source_identity,
        "source_locator": _safe_locator(args.source_locator),
        "source_input_sha256": source_input_sha,
        "language": args.language,
        "rights_sha256": rights_sha,
        "caption_sha256": caption_sha,
        "caption_authority": args.caption_authority,
        "caption_provider_locator": args.caption_provider_locator,
        "transcript_sha256": transcript_sha,
        "stt_engine": args.stt_engine,
        "stt_model": display_path(args.stt_model, Path.cwd()) if args.stt_model else None,
    }
    if source_is_url:
        # Query strings are intentionally scrubbed from readback, but may still
        # select different source bytes. Bind a non-reversible digest so resume
        # cannot confuse those inputs without leaking signed URL parameters.
        fingerprint_inputs["source_locator_private_sha256"] = _locator_fingerprint(
            args.source_locator
        )
    return {
        "source_is_url": source_is_url,
        "source_path": source_path,
        "rights_path": rights_path,
        "rights": rights,
        "rights_sha256": rights_sha,
        "caption_path": caption_path,
        "caption_payload": caption_payload,
        "caption_sha256": caption_sha,
        "transcript_path": transcript_path,
        "transcript_payload": transcript_payload,
        "transcript_sha256": transcript_sha,
        "fingerprint_inputs": fingerprint_inputs,
    }


def _resume_result(
    *,
    args: argparse.Namespace,
    packet_path: Path,
    report_path: Path,
    fingerprint_value: str,
) -> dict[str, Any] | None:
    if not args.resume or not packet_path.exists():
        return None
    packet = load_json(packet_path, label="source_packet")
    if packet.get("input_fingerprint") != fingerprint_value:
        raise SourcePacketBlocked(
            "resume_input_fingerprint_mismatch",
            "resume refused because requested inputs differ from the existing packet",
            details={
                "existing": packet.get("input_fingerprint"),
                "requested": fingerprint_value,
            },
        )
    issues = validate_packet(packet)
    issues.extend(validate_packet_files(packet, base_dir=Path.cwd()))
    if not report_path.exists():
        issues.append(f"readback report missing: {report_path}")
    if issues:
        raise SourcePacketBlocked(
            "resume_cache_integrity_invalid",
            "resume refused because the existing packet cache is incomplete or corrupt",
            details={"issues": issues},
        )
    return _success_result(
        packet=packet,
        packet_path=packet_path,
        report_path=report_path,
        resumed=True,
        acquisition_executed=False,
    )


def _acquire_video(
    args: argparse.Namespace,
    episode_dir: Path,
) -> dict[str, Any]:
    cli_args = [
        "--episode-id",
        args.episode_id,
        "--material-id",
        SOURCE_VIDEO_MATERIAL_ID,
        "--root",
        str(episode_dir.parent),
    ]
    if _is_url(args.source_locator):
        cli_args.extend(
            ["--mode", "yt-dlp-video", "--source-url", args.source_locator]
        )
        if args.yt_dlp_path:
            cli_args.extend(["--yt-dlp-path", args.yt_dlp_path])
    else:
        cli_args.extend(
            ["--mode", "local-media-video", "--source-path", args.source_locator]
        )
    if args.ffprobe_path:
        cli_args.extend(["--ffprobe-path", args.ffprobe_path])
    _run_existing_cli(
        fetch_source_video.run,
        cli_args,
        stage="source_video_acquisition",
    )
    return load_json(
        episode_dir / "materials" / SOURCE_VIDEO_MATERIAL_ID / "fetch_receipt.json",
        label="source_video_receipt",
    )


def _acquire_audio(
    args: argparse.Namespace,
    episode_dir: Path,
    video_path: Path,
) -> dict[str, Any]:
    cli_args = [
        "--episode-id",
        args.episode_id,
        "--material-id",
        SOURCE_AUDIO_MATERIAL_ID,
        "--root",
        str(episode_dir.parent),
        "--mode",
        "local-media-audio",
        "--local-media",
        str(video_path),
    ]
    if args.ffmpeg_path:
        cli_args.extend(["--ffmpeg-path", args.ffmpeg_path])
    _run_existing_cli(
        fetch_source_audio.run,
        cli_args,
        stage="source_audio_normalization",
    )
    return load_json(
        episode_dir / "materials" / SOURCE_AUDIO_MATERIAL_ID / "fetch_receipt.json",
        label="source_audio_receipt",
    )


def _build_candidates(
    *,
    args: argparse.Namespace,
    inputs: dict[str, Any],
    evidence_dir: Path,
    episode_dir: Path,
    source_audio: dict[str, Any],
    source_duration: float,
) -> tuple[list[AuthorityCandidate], list[tuple[str, Path]]]:
    candidates: list[AuthorityCandidate] = []
    evidence_paths: list[tuple[str, Path]] = []
    if inputs["caption_path"] is not None:
        caption_snapshot = evidence_dir / "caption_track.json3"
        shutil.copy2(inputs["caption_path"], caption_snapshot)
        caption_segments, caption_readback = parse_youtube_json3_caption(
            inputs["caption_payload"],
            language=args.language,
            provider_locator=args.caption_provider_locator,
            source_duration_seconds=source_duration,
        )
        candidates.append(
            caption_authority_candidate(
                authority_kind=args.caption_authority,
                caption_path=caption_snapshot,
                caption_sha256=inputs["caption_sha256"],
                caption_segments=caption_segments,
                caption_readback=caption_readback,
                episode_id=args.episode_id,
                language=args.language,
                source_audio=source_audio,
            )
        )
        evidence_paths.append(("caption_authority_snapshot", caption_snapshot))

    transcript_path = inputs["transcript_path"]
    transcript_payload = inputs["transcript_payload"]
    transcript_sha = inputs["transcript_sha256"]
    if transcript_path is None and args.stt_engine:
        transcript_path = evidence_dir / "real_stt_transcript.json"
        cli_args = [
            "--episode-id",
            args.episode_id,
            "--source-audio",
            str(_resolve_output_path(source_audio["path"])),
            "--output",
            str(transcript_path),
            "--language",
            args.language,
            "--engine",
            args.stt_engine,
            "--model",
            args.stt_model,
            "--material-ledger",
            str(episode_dir / "material_ledger.json"),
            "--material-id",
            SOURCE_AUDIO_MATERIAL_ID,
            "--format",
            "json",
        ]
        _run_existing_cli(
            transcribe_audio.run,
            cli_args,
            stage="configured_real_stt",
        )
        transcript_payload = load_json(transcript_path, label="real_stt_transcript")
        transcript_sha = sha256_file(transcript_path)
    elif transcript_path is not None:
        transcript_snapshot = evidence_dir / "transcript_authority.json"
        shutil.copy2(transcript_path, transcript_snapshot)
        transcript_path = transcript_snapshot

    if transcript_path is not None and transcript_payload is not None and transcript_sha:
        candidates.append(
            transcript_authority_candidate(
                transcript=transcript_payload,
                transcript_path=transcript_path,
                transcript_sha256=transcript_sha,
                language=args.language,
                source_audio_sha256=str(source_audio["sha256"]),
                source_duration_seconds=source_duration,
                episode_id=args.episode_id,
                source_audio=source_audio,
            )
        )
        evidence_paths.append(("transcript_authority_snapshot", transcript_path))
    return candidates, evidence_paths


def _artifact_manifest(
    items: list[tuple[str, Path]],
) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for role, path in items:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if not resolved.exists() or not resolved.is_file():
            raise SourcePacketBlocked(
                "artifact_manifest_input_missing",
                f"required packet artifact is missing: {resolved}",
            )
        manifest.append(
            {
                "role": role,
                "path": display_path(resolved, Path.cwd()),
                "sha256": sha256_file(resolved),
                "byte_size": resolved.stat().st_size,
            }
        )
    return manifest


def _run_existing_cli(
    command: Callable[[list[str]], int],
    argv: list[str],
    *,
    stage: str,
) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = command(argv)
    if exit_code != 0:
        raise SourcePacketBlocked(
            f"{stage}_failed",
            f"{stage} failed with exit code {exit_code}",
            details={
                "stdout": stdout.getvalue()[-4000:],
                "stderr": stderr.getvalue()[-4000:],
            },
        )


def _success_result(
    *,
    packet: dict[str, Any],
    packet_path: Path,
    report_path: Path,
    resumed: bool,
    acquisition_executed: bool,
) -> dict[str, Any]:
    return {
        "state": READY_STATE,
        "packet_id": packet["packet_id"],
        "packet_path": display_path(packet_path, Path.cwd()),
        "report_path": display_path(report_path, Path.cwd()),
        "input_fingerprint": packet["input_fingerprint"],
        "packet_integrity": packet["packet_integrity"]["canonical_payload_sha256"],
        "source": {
            "identity": packet["source"]["identity"],
            "sha256": packet["source"]["sha256"],
            "duration_seconds": packet["source"]["duration_seconds"],
            "resolution": packet["source"]["resolution"],
        },
        "authority": {
            "kind": packet["authority"]["kind"],
            "reason": packet["authority"]["selection_reason"],
            "language": packet["normalized_transcript"]["language"],
            "segment_count": packet["normalized_transcript"]["segment_count"],
            "coverage_ratio": packet["normalized_transcript"]["coverage_ratio"],
        },
        "resume": resumed,
        "acquisition_executed": acquisition_executed,
        "consumer_readiness": packet["consumer_readiness"],
    }


def _receipt_readback(path: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": receipt.get("mode"),
        "receipt_path": display_path(path, Path.cwd()),
        "receipt_sha256": sha256_file(path),
        "output_path": receipt.get("output_path"),
        "output_sha256": receipt.get("sha256"),
        "byte_size": receipt.get("byte_size"),
        "warnings": receipt.get("warnings") or [],
    }


def _resolve_output_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else Path.cwd() / path


def _positive_float(value: Any, *, code: str, label: str) -> float:
    if not isinstance(value, (int, float)) or float(value) <= 0:
        raise SourcePacketBlocked(code, f"{label} must be a positive number")
    return float(value)


def _source_provider(identity: str) -> str:
    return identity.split(":", 1)[0] if ":" in identity else "local"


def _safe_locator(locator: str) -> str:
    if not _is_url(locator):
        return display_path(Path(locator).resolve(), Path.cwd())
    parsed = urlparse(locator)
    return parsed._replace(query="", fragment="").geturl()


def _is_url(locator: str) -> bool:
    return urlparse(locator).scheme.lower() in {"http", "https"}


def _locator_fingerprint(locator: str) -> str:
    return hashlib.sha256(locator.encode("utf-8")).hexdigest()


def _print_result(
    payload: dict[str, Any],
    *,
    fmt: str,
    error: bool = False,
) -> None:
    stream = sys.stderr if error else sys.stdout
    if fmt == "json":
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        return
    if error:
        reason = payload["blocking_reason"]
        print(f"blocked: {reason['code']}: {reason['message']}", file=stream)
        return
    print(f"state: {payload['state']}", file=stream)
    print(f"packet: {payload['packet_path']}", file=stream)
    print(f"report: {payload['report_path']}", file=stream)
    print(f"source_sha256: {payload['source']['sha256']}", file=stream)
    print(f"authority: {payload['authority']['kind']}", file=stream)
    print(f"segments: {payload['authority']['segment_count']}", file=stream)
    print(f"coverage_ratio: {payload['authority']['coverage_ratio']}", file=stream)
    print(f"resume: {str(payload['resume']).lower()}", file=stream)
    print(
        f"acquisition_executed: {str(payload['acquisition_executed']).lower()}",
        file=stream,
    )
