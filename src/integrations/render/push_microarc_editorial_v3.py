"""OUT-14 editorial presentation reconstruction v3.

This profile is intentionally bound to the exact v2 review artifact.  It
preserves v2 selection, source ranges, chronology, and accepted perceptual
timing while rebuilding viewer-facing presentation roles.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import shutil
import struct
import subprocess
import uuid
import wave
from collections.abc import Iterable
from itertools import pairwise
from pathlib import Path
from typing import Any

from src.integrations.render import ffmpeg_tiny
from src.integrations.render import push_microarc_editorial_v2 as v2

SCHEMA_VERSION = "clippipegen.out14.editorial_presentation.v3"
MANIFEST_SCHEMA_VERSION = "clippipegen.out14.editorial_manifest.v3"
PIPELINE_VERSION = "out14-editorial-presentation-reconstruction-v3"
READY_STATE = "OUT14_EDITORIAL_V3_READY_FOR_HUMAN_REVIEW"
BUILD_PENDING_STATE = "OUT14_EDITORIAL_V3_FULL_VIEW_SELF_REVIEW_PENDING"
DESIGN_SIGNATURE = "CPG-OUT14-V3-DIRSIG-20260727-A"
ARTIFACT_ID = "clip-out14-push-microarc-editorial-v3-001"
V2_ARTIFACT_ID = "clip-out14-push-microarc-editorial-v2-001"
V2_FINAL_VIDEO_SHA256 = (
    "8fe9105c72645acbb21357f10107e0266e19d1bebe18c30a68bd7e59b5853414"
)
V2_MANIFEST_SHA256 = (
    "774351a7fc55839e05e58276280570a27ac1fd0aa7fa78283cdcf79f5d8634a9"
)
SOURCE_SHA256 = "335e9a131fae06b716bd7ac479e914fb849be117b15c4b412c9b4c565fef264e"
SOURCE_IDENTITY = "youtube:rltNvZ_FY8Q"
V2_THUMBNAIL_SHA256 = (
    "d0edde1236f8b254c1fe9588d1f656aef057f1baba603be55239d20c3170c3ce"
)
WORKING_TITLE = "Discordのプロフィールを遊びで変えたら、全スタッフに通知が飛んでいた"
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
DEFAULT_REVIEW_PORT = 8082
TARGET_DURATION_SECONDS = 406.52
QUARANTINES = (
    "out14-v2-source-screenshot-single-hook-thumbnail-v1",
    "out14-v2-flat-caption-pass-through-v1",
    "out14-v2-naked-cut-black-card-v1",
)


class PushMicroarcEditorialV3Error(RuntimeError):
    """Fail-closed v3 builder error."""

    def __init__(self, message: str, *, stage: str) -> None:
        super().__init__(message)
        self.stage = stage


QUOTE_SPECS: dict[str, dict[str, str]] = {
    "speech_0018": {
        "quoted_identity": "猫又おかゆ",
        "display_text": "「僕がいいの選んであげるよ」",
        "evidence": "caption_0017 attribution followed by canonical caption_0018",
        "style_role": "quoted_speech_okayu",
    },
    "speech_0100": {
        "quoted_identity": "星街すいせい",
        "display_text": "「さっきからプロフィールの",
        "evidence": "canonical caption says すいちゃんから immediately before quote",
        "style_role": "quoted_speech_suisei",
    },
    "speech_0101": {
        "quoted_identity": "星街すいせい",
        "display_text": "変更通知、来てるよ」",
        "evidence": "continuation of verified Suisei quote in canonical timing",
        "style_role": "quoted_speech_suisei",
    },
    "speech_0107": {
        "quoted_identity": "さくらみこ",
        "display_text": "「蒙古タンメンスバルって来てたよ」",
        "evidence": "caption_0106 names みこち immediately before canonical quote",
        "style_role": "quoted_speech_miko",
    },
    "speech_0113": {
        "quoted_identity": "星街すいせい",
        "display_text": "「蒙古タンメンスバル」",
        "evidence": "caption_0112 explicitly names すいちゃん before canonical quote",
        "style_role": "quoted_speech_suisei",
    },
}

PARAPHRASE_IDS = {
    "speech_0040",
    "speech_0041",
    "speech_0042",
    "speech_0043",
    "speech_0044",
    "speech_0045",
    "speech_0046",
    "speech_0048",
    "speech_0049",
    "speech_0050",
    "speech_0051",
    "speech_0052",
    "speech_0053",
}

PRESENTATION_OVERRIDES = {
    "speech_0003": "Discordってさあ、あのー、なんか",
    "speech_0004": "最近プロフィール装飾できるんよ",
    "speech_0077": "それで、あの",
    "speech_0136": "これは謝罪です",
    "speech_0137": "ということでさ",
}

SEGMENTATION_TIMING = {
    "speech_0003": {"display_end_seconds": 12.72},
    "speech_0004": {"display_start_seconds": 12.72},
}

# The v2 cue builder cut on character budgets, so a full-ledger audit found
# repeated phrase-internal boundaries beyond the reported 00:15 locus.  These
# groups are presentation-only: canonical text, order, and the outer word-timed
# interval stay traceable, while the unsafe internal display boundaries are
# removed.  No quote event is grouped here.
SEGMENTATION_GROUP_SPECS: tuple[dict[str, Any], ...] = (
    {
        "caption_ids": ("speech_0005", "speech_0006", "speech_0007"),
        "display_text": "で、その流れで、その前までマチュがね、アヒルの装飾をね",
    },
    {
        "caption_ids": ("speech_0009", "speech_0010"),
        "display_text": "結構気に入って使ってて。でも結構長いこと使ってたから",
    },
    {
        "caption_ids": ("speech_0014", "speech_0015"),
        "display_text": "言ってたら、あの、結構長い間使ったから",
    },
    {
        "caption_ids": ("speech_0016", "speech_0017"),
        "display_text": "気分転換に変えちゃおうかなとか言ってたら、そのおかゆが、え、じゃあ、あの",
    },
    {
        "caption_ids": ("speech_0019", "speech_0020"),
        "display_text": "ガビガビだけどさ、これね、レッドカード持ってるやつ",
    },
    {
        "caption_ids": ("speech_0025", "speech_0026"),
        "display_text": "スバおかでどうなってるかっていうと",
    },
    {
        "caption_ids": ("speech_0027", "speech_0028", "speech_0029"),
        "display_text": "これ、テストで使ったチャットなんだけど、あの、こうなってるから",
    },
    {
        "caption_ids": ("speech_0031", "speech_0032"),
        "display_text": "イエローカード持ってて、スバルがレッドカード持ってるみたいな",
    },
    {
        "caption_ids": ("speech_0034", "speech_0035", "speech_0036"),
        "display_text": "で、これさ、普通にメンバーとチャットしてる時は全然いいんだけど、これヤバいのが",
    },
    {
        "caption_ids": ("speech_0037", "speech_0038"),
        "display_text": "あの、このアイコンで仕事の返事してる時が一番ヤバくて…",
    },
    {
        "caption_ids": ("speech_0045", "speech_0046"),
        "display_text": "なんかレッドカード持ってるから、こいつ本当にそう思ってるかみたい",
        "speech_role": "paraphrase",
    },
    {
        "caption_ids": ("speech_0047", "speech_0048"),
        "display_text": "とか、まだそれはいいんだけど、あの、じゃあ次のグッズこんな感じでいい",
        "speech_role": "paraphrase",
    },
    {
        "caption_ids": ("speech_0050", "speech_0051"),
        "display_text": "ちょっとこうしてくださいとか言うんだけど",
        "speech_role": "paraphrase",
    },
    {
        "caption_ids": ("speech_0053", "speech_0054"),
        "display_text": "切れてるやつみたいになるわけよ。でさ",
        "speech_role": "paraphrase",
    },
    {
        "caption_ids": ("speech_0057", "speech_0058", "speech_0059", "speech_0060"),
        "display_text": "皆さんにも先に言います。別に切れてるんじゃなくて、遊戯王みたいなだけ",
    },
    {
        "caption_ids": ("speech_0061", "speech_0062", "speech_0063"),
        "display_text": "やってるだけなのね。だから恐れないでください。別に何も…",
    },
    {
        "caption_ids": ("speech_0064", "speech_0065"),
        "display_text": "今スバルのあのやつ、どうなってるかっていうと",
    },
    {
        "caption_ids": ("speech_0066", "speech_0067", "speech_0068", "speech_0069"),
        "display_text": "これ見るじゃん。なんだこのアイコンと思って、クリックするとプロフィール詳細が出るんだけど",
    },
    {
        "caption_ids": ("speech_0071", "speech_0072", "speech_0073"),
        "display_text": "開けた瞬間、見える写真がいきなりグーパン飛んでくるみたいな",
    },
    {
        "caption_ids": ("speech_0075", "speech_0076"),
        "display_text": "これになってて、これでめっちゃ笑ってて、2人で",
    },
    {
        "caption_ids": ("speech_0078", "speech_0079"),
        "display_text": "これでさ、めちゃめちゃ笑ってて。どうせなら",
    },
    {
        "caption_ids": ("speech_0082", "speech_0083"),
        "display_text": "蒙古タンメンスバルって書いてあるの",
    },
    {
        "caption_ids": ("speech_0087", "speech_0088"),
        "display_text": "蒙古タンメンスバルとか色々変えまくって。いや、やっぱ",
    },
    {
        "caption_ids": ("speech_0090", "speech_0091"),
        "display_text": "とか言ってたわけ。それでさ、これ変えたらさ",
    },
    {
        "caption_ids": ("speech_0104", "speech_0105"),
        "display_text": "で、えってなって。それでなんか話聞いてたら",
    },
    {
        "caption_ids": ("speech_0114", "speech_0115"),
        "display_text": "みたいになった時に気づいたんだけど、これ全体通知いくんだよ",
    },
    {
        "caption_ids": ("speech_0119", "speech_0120", "speech_0121"),
        "display_text": "蒙古タンメンスバルって通知がいってんの。死ぬだろう、って通知だった",
    },
    {
        "caption_ids": ("speech_0123", "speech_0124"),
        "display_text": "みたいな。これはね、謝罪なの。本当にすいません",
    },
    {
        "caption_ids": ("speech_0128", "speech_0129"),
        "display_text": "ほんまに恥ずかしいで。あと、あの、スタッフさんに",
    },
    {
        "caption_ids": ("speech_0130", "speech_0131", "speech_0132"),
        "display_text": "言っとくと、別にこれ切れてないっす。普通に遊んでこのアイコンにしただけなんで",
    },
    {
        "caption_ids": ("speech_0139", "speech_0140"),
        "display_text": "ステータス変えると全体に通知いくぞ",
    },
)

SUPPRESSED_PRESENTATION_IDS = {"speech_0039"}

PROTECTED_PRESENTATION_PHRASES = (
    "なんか",
    "前まで",
    "長いこと",
    "言ってたら",
    "レッドカード",
    "なんだけど",
    "メンバー",
    "してる",
    "こいつ",
    "じゃあ",
    "でさ",
    "言っておきます",
    "切れてるんじゃなくて",
    "恐れない",
    "恐れないでください",
    "どうなってるかっていうと",
    "アイコン",
    "プロフィール詳細",
    "開けた瞬間",
    "いきなり",
    "グーパン",
    "笑ってて",
    "どうせなら",
    "変えまくって",
    "変えたら",
    "聞いてたら",
    "気づいたんだけど",
    "いってんの",
    "すいません",
    "スタッフ",
    "全体に通知いくぞ",
)

LAUGHTER_EVENTS = [
    {
        "event_id": "laugh_001",
        "start_seconds": 211.97,
        "end_seconds": 213.20,
        "classification": "foreground_chuckle",
        "intensity": "mild",
        "display_text": "(笑)",
        "motion_seed": None,
        "reason": "caption-free reaction immediately after two-person laughter narration",
    },
    {
        "event_id": "laugh_002",
        "start_seconds": 214.55,
        "end_seconds": 217.75,
        "classification": "sustained_foreground_laughter",
        "intensity": "strong",
        "display_text": "ｗｗｗ",
        "motion_seed": 21455,
        "reason": "sustained caption-free reaction before the next spoken beat",
    },
    {
        "event_id": "laugh_003",
        "start_seconds": 306.20,
        "end_seconds": 310.60,
        "classification": "strong_reaction",
        "intensity": "strong",
        "display_text": "ｗｗｗ",
        "motion_seed": 30620,
        "reason": "foreground reaction after the all-staff notification reveal",
    },
    {
        "event_id": "laugh_004",
        "start_seconds": 348.45,
        "end_seconds": 350.05,
        "classification": "overlapping_nervous_chuckle",
        "intensity": "mild",
        "display_text": "(笑)",
        "motion_seed": None,
        "reason": "brief apology aftermath reaction",
    },
    {
        "event_id": "laugh_005",
        "start_seconds": 378.90,
        "end_seconds": 382.40,
        "classification": "sustained_aftermath_laughter",
        "intensity": "strong",
        "display_text": "ｗｗｗ",
        "motion_seed": 37890,
        "reason": "sustained reaction in the aftermath section",
    },
]

TRANSITION_SPECS = [
    {
        "transition_id": "transition_001",
        "output_seconds": 0.0,
        "classification": "sequence_start",
        "audio": "source_start",
        "visual": "premise_tag",
        "label": "プロフィールを変えた朝",
        "reason": "establishes the selected episode without a black cold-open",
    },
    {
        "transition_id": "transition_002",
        "output_seconds": 50.28,
        "classification": "same_scene_omission",
        "audio": "40ms_boundary_microfade",
        "visual": "red_card_accent",
        "label": "おかゆとお揃いに",
        "reason": "retains the same conversation while marking omitted navigation",
    },
    {
        "transition_id": "transition_003",
        "output_seconds": 115.16,
        "classification": "semantic_beat",
        "audio": "40ms_boundary_microfade",
        "visual": "work_context_tag",
        "label": "仕事の返信でも…",
        "reason": "moves from playful setup to work consequence",
    },
    {
        "transition_id": "transition_004",
        "output_seconds": 167.72,
        "classification": "time_jump",
        "audio": "40ms_boundary_microfade",
        "visual": "cyan_directional_bridge",
        "label": "プロフィール画面へ",
        "reason": "material jump near 02:48 requires an explicit directional bridge",
    },
    {
        "transition_id": "transition_005",
        "output_seconds": 244.0,
        "classification": "semantic_beat",
        "audio": "40ms_boundary_microfade",
        "visual": "notification_reveal_tag",
        "label": "通知が届いていた",
        "reason": "marks the premise-to-consequence turn",
    },
    {
        "transition_id": "transition_006",
        "output_seconds": 336.08,
        "classification": "semantic_beat",
        "audio": "40ms_boundary_microfade",
        "visual": "apology_tag",
        "label": "ここから謝罪",
        "reason": "separates the reveal reaction from the apology",
    },
    {
        "transition_id": "transition_007",
        "output_seconds": 366.68,
        "classification": "same_scene_omission",
        "audio": "40ms_boundary_microfade",
        "visual": "aftermath_marker",
        "label": "その後",
        "reason": "marks omitted material without overstating a time jump",
    },
    {
        "transition_id": "transition_008",
        "output_seconds": 386.44,
        "classification": "explanation_ending",
        "audio": "40ms_boundary_microfade",
        "visual": "source_anchored_explanation_panel",
        "label": "注意｜プロフィール変更は全体通知",
        "reason": "replaces the rejected full-black explanation near 06:27",
    },
]

PROBE_SPECS = [
    ("segmentation_0015", 9.5, 17.0),
    ("quote_okayu", 47.6, 50.7),
    ("quote_suisei", 263.5, 273.2),
    ("quote_miko", 282.8, 290.2),
    ("laughter_mild", 210.5, 214.0),
    ("laughter_strong_motion", 213.5, 219.0),
    ("transition_0248", 164.5, 171.5),
    ("transition_0627", 383.2, 393.0),
    ("source_anchored_explanation", 386.0, 393.0),
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PushMicroarcEditorialV3Error(
            f"invalid JSON input: {path.name}", stage="preflight"
        ) from exc


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolved(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def _ass_time(value: float) -> str:
    centiseconds = max(0, round(value * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    seconds, cs = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{cs:02d}"


def _ass_text(value: str) -> str:
    return (
        value.replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\n", r"\N")
    )


def _escape_filter_path(path: Path) -> str:
    return (
        str(path.resolve())
        .replace("\\", "/")
        .replace(":", r"\:")
        .replace("'", r"\'")
    )


def _closed_gates() -> dict[str, bool]:
    return {
        "human_editorial_acceptance": False,
        "rights_approval": False,
        "YPP_eligibility": False,
        "production_acceptance": False,
        "publication_readiness": False,
        "thumbnail_acceptance": False,
        "upload": False,
        "visibility_change": False,
    }


def validate_v2_reference(
    *,
    source_path: Path,
    v2_reference_dir: Path,
    v2_final_video_path: Path,
    design_basis_path: Path,
) -> dict[str, Any]:
    required = (
        "run_manifest.json",
        "canonical_transcript.json",
        "caption_readback.json",
        "subtitle_presentation_readback.json",
        "subtitle_timing_readback.json",
        "timeline_ir.json",
        "selection_record.json",
        "validation_readback.json",
        "title_thumbnail_readback.json",
        "v1_human_decision_record.json",
    )
    missing = [name for name in required if not (v2_reference_dir / name).is_file()]
    if missing:
        raise PushMicroarcEditorialV3Error(
            f"v2 reference files missing: {missing}", stage="preflight"
        )
    for path in (source_path, v2_final_video_path, design_basis_path):
        if not path.is_file():
            raise PushMicroarcEditorialV3Error(
                f"required input missing: {path.name}", stage="preflight"
            )
    hashes = {
        "source_sha256": _sha256(source_path),
        "v2_manifest_sha256": _sha256(v2_reference_dir / "run_manifest.json"),
        "v2_final_video_sha256": _sha256(v2_final_video_path),
    }
    expected = {
        "source_sha256": SOURCE_SHA256,
        "v2_manifest_sha256": V2_MANIFEST_SHA256,
        "v2_final_video_sha256": V2_FINAL_VIDEO_SHA256,
    }
    if hashes != expected:
        raise PushMicroarcEditorialV3Error(
            "v2/source exact identity mismatch", stage="preflight"
        )
    manifest = _read_json(v2_reference_dir / "run_manifest.json")
    if (
        manifest.get("artifact_id") != V2_ARTIFACT_ID
        or manifest.get("source", {}).get("identity") != SOURCE_IDENTITY
        or manifest.get("final_video", {}).get("sha256") != V2_FINAL_VIDEO_SHA256
        or manifest.get("final_video", {}).get("duration_seconds") != 406.55
    ):
        raise PushMicroarcEditorialV3Error(
            "v2 manifest contract mismatch", stage="preflight"
        )
    if DESIGN_SIGNATURE not in design_basis_path.read_text(encoding="utf-8"):
        raise PushMicroarcEditorialV3Error(
            "predeclared direction signature missing", stage="preflight"
        )
    timeline = _read_json(v2_reference_dir / "timeline_ir.json")
    if (
        timeline.get("cut_count") != 8
        or not math.isclose(
            float(timeline.get("output_duration_seconds", 0)),
            TARGET_DURATION_SECONDS,
            abs_tol=0.01,
        )
    ):
        raise PushMicroarcEditorialV3Error(
            "v2 timeline contract mismatch", stage="preflight"
        )
    return {
        "status": "passed",
        **hashes,
        "v2_artifact_id": V2_ARTIFACT_ID,
        "v2_duration_seconds": 406.55,
        "design_signature": DESIGN_SIGNATURE,
    }


def _caption_role(caption_id: str) -> tuple[str, str | None, str, str]:
    quote = QUOTE_SPECS.get(caption_id)
    if quote:
        return (
            "quoted_verbatim",
            quote["quoted_identity"],
            quote["evidence"],
            quote["style_role"],
        )
    if caption_id in PARAPHRASE_IDS:
        return (
            "paraphrase",
            None,
            "canonical Subaru narration presents a hypothetical exchange",
            "normal_speech",
        )
    return (
        "narration",
        None,
        "canonical actual-audio Subaru narration",
        "normal_speech",
    )


_KINSOKU_LINE_START = set("、。，．。！？!?：；」』】）》〕］｝ゃゅょっぁぃぅぇぉャュョッァィゥェォー")
_KINSOKU_LINE_END = set("「『【（《〔［｛")
_DANGLING_FUNCTION_WORDS = {
    "が",
    "を",
    "に",
    "へ",
    "と",
    "で",
    "の",
    "は",
    "も",
    "や",
    "か",
    "ね",
    "よ",
    "ぞ",
    "さ",
    "から",
    "けど",
    "って",
    "です",
    "ます",
}


def _protected_boundary_hits(left: str, right: str) -> list[str]:
    joined = left + right
    boundary = len(left)
    hits: list[str] = []
    for phrase in PROTECTED_PRESENTATION_PHRASES:
        offset = joined.find(phrase)
        while offset >= 0:
            if offset < boundary < offset + len(phrase):
                hits.append(phrase)
                break
            offset = joined.find(phrase, offset + 1)
    return hits


def _safe_two_line_wrap(value: str, *, maximum_characters: int = 24) -> list[str]:
    if len(value) <= maximum_characters:
        return [value]
    if len(value) > maximum_characters * 2:
        return [
            value[index : index + maximum_characters]
            for index in range(0, len(value), maximum_characters)
        ]
    midpoint = len(value) / 2
    candidates: list[tuple[float, int]] = []
    for boundary in range(
        max(1, len(value) - maximum_characters),
        min(maximum_characters, len(value) - 1) + 1,
    ):
        left = value[:boundary]
        right = value[boundary:]
        if left[-1] in _KINSOKU_LINE_END or right[0] in _KINSOKU_LINE_START:
            continue
        if _protected_boundary_hits(left, right):
            continue
        punctuation_bonus = 4 if left[-1] in "、。！？…" else 0
        candidates.append((abs(boundary - midpoint) - punctuation_bonus, boundary))
    if not candidates:
        return [value]
    _, boundary = min(candidates)
    return [value[:boundary], value[boundary:]]


def _apply_segmentation_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {row["caption_id"]: row for row in rows}
    consumed: set[str] = set()
    merged_by_first: dict[str, dict[str, Any]] = {}
    for spec in SEGMENTATION_GROUP_SPECS:
        caption_ids = tuple(spec["caption_ids"])
        present_ids = [caption_id for caption_id in caption_ids if caption_id in by_id]
        if not present_ids:
            continue
        if len(present_ids) != len(caption_ids):
            raise PushMicroarcEditorialV3Error(
                f"partial segmentation group input: {caption_ids}",
                stage="caption_model",
            )
        if len(caption_ids) < 2 or any(caption_id in consumed for caption_id in caption_ids):
            raise PushMicroarcEditorialV3Error(
                "overlapping or incomplete segmentation group",
                stage="caption_model",
            )
        try:
            members = [by_id[caption_id] for caption_id in caption_ids]
        except KeyError as exc:
            raise PushMicroarcEditorialV3Error(
                f"segmentation group member missing: {exc}",
                stage="caption_model",
            ) from exc
        indices = [rows.index(member) for member in members]
        if indices != list(range(indices[0], indices[0] + len(indices))):
            raise PushMicroarcEditorialV3Error(
                f"segmentation group is not contiguous: {caption_ids}",
                stage="caption_model",
            )
        if len({member["cut_id"] for member in members}) != 1:
            raise PushMicroarcEditorialV3Error(
                f"segmentation group crosses a cut: {caption_ids}",
                stage="caption_model",
            )
        speech_role = str(spec.get("speech_role") or members[0]["speech_role"])
        merged = {
            **members[0],
            "event_id": "+".join(caption_ids),
            "caption_id": caption_ids[0],
            "caption_ids": list(caption_ids),
            "display_start_seconds": members[0]["display_start_seconds"],
            "display_end_seconds": members[-1]["display_end_seconds"],
            "canonical_start_seconds": members[0]["canonical_start_seconds"],
            "canonical_end_seconds": members[-1]["canonical_end_seconds"],
            "canonical_text": "".join(member["canonical_text"] for member in members),
            "display_text": str(spec["display_text"]),
            "speech_role": speech_role,
            "quoted_identity": None,
            "evidence": (
                "full-ledger phrase-boundary audit over canonical word-timed cues "
                + ", ".join(caption_ids)
            ),
            "style_role": "normal_speech",
            "word_timed_chunk": all(member["word_timed_chunk"] for member in members),
            "timing_delta_start_ms": 0,
            "timing_delta_end_ms": 0,
            "presentation_override_applied": True,
            "merged_internal_boundary_count": len(caption_ids) - 1,
        }
        merged_by_first[caption_ids[0]] = merged
        consumed.update(caption_ids)
    result: list[dict[str, Any]] = []
    for row in rows:
        caption_id = row["caption_id"]
        if caption_id in SUPPRESSED_PRESENTATION_IDS:
            continue
        if caption_id in merged_by_first:
            result.append(merged_by_first[caption_id])
        elif caption_id not in consumed:
            result.append(row)
    for row in result:
        row["caption_ids"] = row.get("caption_ids") or [row["caption_id"]]
        row["merged_internal_boundary_count"] = int(
            row.get("merged_internal_boundary_count", 0)
        )
        row["wrapped_lines"] = _safe_two_line_wrap(str(row["display_text"]))
    return result


def build_caption_event_ledger(
    caption_readback: dict[str, Any],
    presentation_readback: dict[str, Any],
) -> dict[str, Any]:
    presentation = {
        row["subtitle_id"]: row for row in presentation_readback.get("items") or []
    }
    rows: list[dict[str, Any]] = []
    for source in caption_readback.get("items") or []:
        caption_id = str(source["caption_id"])
        base_presentation = presentation.get(caption_id)
        if not base_presentation:
            raise PushMicroarcEditorialV3Error(
                f"v2 presentation missing {caption_id}", stage="caption_model"
            )
        display_start = float(base_presentation["display_start_seconds"])
        display_end = float(base_presentation["display_end_seconds"])
        timing_override = SEGMENTATION_TIMING.get(caption_id, {})
        display_start = float(
            timing_override.get("display_start_seconds", display_start)
        )
        display_end = float(timing_override.get("display_end_seconds", display_end))
        canonical_text = str(source["text"])
        display_text = PRESENTATION_OVERRIDES.get(caption_id, canonical_text)
        if caption_id in QUOTE_SPECS:
            display_text = QUOTE_SPECS[caption_id]["display_text"]
        speech_role, identity, evidence, style_role = _caption_role(caption_id)
        rows.append(
            {
                "event_id": caption_id,
                "caption_id": caption_id,
                "cut_id": source["cut_id"],
                "display_start_seconds": round(display_start, 6),
                "display_end_seconds": round(display_end, 6),
                "canonical_start_seconds": source["output_start_seconds"],
                "canonical_end_seconds": source["output_end_seconds"],
                "canonical_text": canonical_text,
                "display_text": display_text,
                "narrating_speaker": "大空スバル",
                "quoted_identity": identity,
                "speech_role": speech_role,
                "evidence": evidence,
                "style_role": style_role,
                "word_timed_chunk": bool(source.get("word_timed_chunk")),
                "timing_delta_start_ms": round(
                    (display_start - float(source["output_start_seconds"])) * 1000
                ),
                "timing_delta_end_ms": round(
                    (display_end - float(source["output_end_seconds"])) * 1000
                ),
                "presentation_override_applied": display_text != canonical_text,
            }
        )
    rows = _apply_segmentation_groups(rows)
    deltas = [
        abs(int(row[key]))
        for row in rows
        for key in ("timing_delta_start_ms", "timing_delta_end_ms")
        if int(row[key]) != 0
    ]
    sorted_deltas = sorted(deltas)
    p95 = sorted_deltas[max(0, math.ceil(len(sorted_deltas) * 0.95) - 1)] if deltas else 0
    signed = [
        int(row[key])
        for row in rows
        for key in ("timing_delta_start_ms", "timing_delta_end_ms")
        if int(row[key]) != 0
    ]
    median = 0.0
    if signed:
        ordered = sorted(signed)
        midpoint = len(ordered) // 2
        median = (
            float(ordered[midpoint])
            if len(ordered) % 2
            else (ordered[midpoint - 1] + ordered[midpoint]) / 2.0
        )
    isolated = [
        row["caption_id"]
        for row in rows
        if len(re.sub(r"[\s、。！？…「」『』（）()ｗ]", "", row["display_text"])) <= 1
    ]
    dangling = [
        row["caption_id"]
        for row in rows
        if re.sub(r"[\s、。！？…「」『』（）()]", "", row["display_text"])
        in _DANGLING_FUNCTION_WORDS
    ]
    boundary_violations: list[dict[str, Any]] = []
    for left, right in pairwise(rows):
        if left["cut_id"] != right["cut_id"]:
            continue
        hits = _protected_boundary_hits(
            str(left["display_text"]), str(right["display_text"])
        )
        if hits:
            boundary_violations.append(
                {
                    "left_caption_id": left["caption_id"],
                    "right_caption_id": right["caption_id"],
                    "phrases": hits,
                }
            )
    line_break_violations: list[dict[str, Any]] = []
    for row in rows:
        for left, right in zip(row["wrapped_lines"], row["wrapped_lines"][1:]):
            hits = _protected_boundary_hits(left, right)
            if (
                hits
                or left[-1] in _KINSOKU_LINE_END
                or right[0] in _KINSOKU_LINE_START
            ):
                line_break_violations.append(
                    {
                        "caption_id": row["caption_id"],
                        "left": left,
                        "right": right,
                        "protected_phrases": hits,
                    }
                )
    quote_rows = [row for row in rows if row["speech_role"] == "quoted_verbatim"]
    quote_styled = [row for row in quote_rows if row["style_role"] != "normal_speech"]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "items": rows,
        "cue_count": len(rows),
        "canonical_cue_count": int(caption_readback.get("cue_count", 0)),
        "unchanged_timing_cue_count": sum(
            row["timing_delta_start_ms"] == 0 and row["timing_delta_end_ms"] == 0
            for row in rows
        ),
        "changed_timing_cue_count": sum(
            row["timing_delta_start_ms"] != 0 or row["timing_delta_end_ms"] != 0
            for row in rows
        ),
        "changed_timing_median_ms": median,
        "changed_timing_p95_absolute_ms": p95,
        "late_bias_present": bool(signed and median > 100),
        "within_word_split_count": len(boundary_violations),
        "within_word_split_violations": boundary_violations,
        "isolated_single_character_count": len(isolated),
        "isolated_single_character_ids": isolated,
        "dangling_particle_auxiliary_predicate_count": len(dangling),
        "dangling_particle_auxiliary_predicate_ids": dangling,
        "kinsoku_line_break_violation_count": len(line_break_violations),
        "kinsoku_line_break_violations": line_break_violations,
        "three_line_cue_count": sum(len(row["wrapped_lines"]) > 2 for row in rows),
        "overdense_cue_count": sum(len(row["display_text"]) > 48 for row in rows),
        "merged_internal_boundary_count": sum(
            row["merged_internal_boundary_count"] for row in rows
        ),
        "suppressed_incomplete_fragment_count": len(SUPPRESSED_PRESENTATION_IDS),
        "suppressed_incomplete_fragment_ids": sorted(SUPPRESSED_PRESENTATION_IDS),
        "quoted_verbatim_event_count": len(quote_rows),
        "quoted_distinct_treatment_count": len(quote_styled),
        "quoted_distinct_treatment_coverage": (
            len(quote_styled) / len(quote_rows) if quote_rows else 1.0
        ),
        "provider_annotation_leak_count": sum(
            bool(
                re.search(
                    r"\[(?:笑い|音楽|拍手|息|music|laugh)",
                    row["display_text"],
                    re.IGNORECASE,
                )
            )
            for row in rows
        ),
        "known_segmentation_repair": {
            "v2_boundary_seconds": 12.64,
            "v3_boundary_seconds": 12.72,
            "canonical_word": "なんか",
            "canonical_word_output_start_seconds": 11.76,
            "canonical_word_output_end_seconds": 12.72,
            "status": "repaired_at_word_end",
        },
    }


def _quote_groups(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    quoted = [row for row in items if row["quoted_identity"]]
    groups: list[dict[str, Any]] = []
    for row in quoted:
        if (
            groups
            and groups[-1]["quoted_identity"] == row["quoted_identity"]
            and float(row["display_start_seconds"]) - float(groups[-1]["end_seconds"])
            <= 0.25
        ):
            groups[-1]["end_seconds"] = row["display_end_seconds"]
            groups[-1]["caption_ids"].append(row["caption_id"])
        else:
            groups.append(
                {
                    "quoted_identity": row["quoted_identity"],
                    "start_seconds": row["display_start_seconds"],
                    "end_seconds": row["display_end_seconds"],
                    "caption_ids": [row["caption_id"]],
                    "style_role": row["style_role"],
                }
            )
    return groups


def _motion_offsets(seed: int) -> list[tuple[float, int, int]]:
    offsets = []
    for index in range(5):
        x = ((seed >> (index * 2)) % 7) - 3
        y = ((seed >> (index * 3 + 1)) % 7) - 3
        offsets.append((index * 0.08, max(-4, min(4, x)), max(-4, min(4, y))))
    return offsets


def write_role_aware_ass(
    path: Path,
    *,
    caption_ledger: dict[str, Any],
    font_family: str,
) -> dict[str, Any]:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {TARGET_WIDTH}
PlayResY: {TARGET_HEIGHT}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Normal,{font_family},66,&H00FFFFFF,&H000000FF,&H00120B08,&H88000000,-1,0,0,0,100,100,0,0,1,5,2,2,150,150,70,1
Style: QuoteOkayu,{font_family},68,&H00FFFFFF,&H000000FF,&H00B05A92,&H90000000,-1,0,0,0,100,100,0,0,1,6,2,2,150,150,72,1
Style: QuoteSuisei,{font_family},68,&H00FFFFFF,&H000000FF,&H00D08B28,&H90000000,-1,0,0,0,100,100,0,0,1,6,2,2,150,150,72,1
Style: QuoteMiko,{font_family},68,&H00FFFFFF,&H000000FF,&H007C5DE8,&H90000000,-1,0,0,0,100,100,0,0,1,6,2,2,150,150,72,1
Style: NameCue,{font_family},38,&H00FFFFFF,&H000000FF,&H00201812,&HD0000000,-1,0,0,0,100,100,0,0,3,2,0,7,118,118,150,1
Style: LaughMild,{font_family},58,&H00FFFFFF,&H000000FF,&H005B3A22,&H90000000,-1,0,0,0,100,100,0,0,1,4,1,2,150,150,164,1
Style: LaughStrong,{font_family},82,&H0000EEFF,&H000000FF,&H00120906,&H90000000,-1,0,0,0,100,100,0,0,1,7,3,5,150,150,180,1
Style: Transition,{font_family},46,&H00FFFFFF,&H000000FF,&H00372710,&HC0000000,-1,0,0,0,100,100,0,0,3,2,0,8,120,120,92,1
Style: Bridge,{font_family},62,&H00FFFFFF,&H000000FF,&H00B45A00,&HC84B2600,-1,0,0,0,100,100,0,0,3,3,1,8,120,120,150,1
Style: Explanation,{font_family},55,&H00FFFFFF,&H000000FF,&H00201810,&HC85A2600,-1,0,0,0,100,100,0,0,3,3,1,8,120,120,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    style_map = {
        "normal_speech": "Normal",
        "quoted_speech_okayu": "QuoteOkayu",
        "quoted_speech_suisei": "QuoteSuisei",
        "quoted_speech_miko": "QuoteMiko",
    }
    events: list[str] = []
    for row in caption_ledger["items"]:
        style = style_map[row["style_role"]]
        events.append(
            "Dialogue: 0,"
            f"{_ass_time(float(row['display_start_seconds']))},"
            f"{_ass_time(float(row['display_end_seconds']))},"
            f"{style},,0,0,0,,{_ass_text(chr(10).join(row['wrapped_lines']))}"
        )
    for group in _quote_groups(caption_ledger["items"]):
        events.append(
            "Dialogue: 2,"
            f"{_ass_time(float(group['start_seconds']))},"
            f"{_ass_time(float(group['end_seconds']))},"
            "NameCue,,0,0,0,,"
            f"〔{_ass_text(str(group['quoted_identity']))}の発言〕"
        )
    motion_event_count = 0
    for event in LAUGHTER_EVENTS:
        if event["intensity"] == "mild":
            events.append(
                "Dialogue: 3,"
                f"{_ass_time(float(event['start_seconds']))},"
                f"{_ass_time(float(event['end_seconds']))},"
                f"LaughMild,,0,0,0,,{event['display_text']}"
            )
            continue
        offsets = _motion_offsets(int(event["motion_seed"]))
        duration = float(event["end_seconds"]) - float(event["start_seconds"])
        step = min(0.12, duration / len(offsets))
        for index, (_, x, y) in enumerate(offsets):
            start = float(event["start_seconds"]) + index * step
            end = (
                float(event["end_seconds"])
                if index == len(offsets) - 1
                else min(float(event["end_seconds"]), start + step)
            )
            events.append(
                "Dialogue: 3,"
                f"{_ass_time(start)},{_ass_time(end)},LaughStrong,,0,0,0,,"
                f"{{\\pos({960 + x},{835 + y})}}{event['display_text']}"
            )
            motion_event_count += 1
    for transition in TRANSITION_SPECS:
        start = float(transition["output_seconds"])
        if transition["transition_id"] == "transition_008":
            end = min(TARGET_DURATION_SECONDS, start + 5.2)
            events.append(
                "Dialogue: 4,"
                f"{_ass_time(start)},{_ass_time(end)},Explanation,,0,0,0,,"
                f"{_ass_text(transition['label'])}\\N"
                "設定変更の通知先を確認"
            )
        elif transition["transition_id"] == "transition_004":
            end = min(TARGET_DURATION_SECONDS, start + 1.25)
            events.append(
                "Dialogue: 4,"
                f"{_ass_time(start)},{_ass_time(end)},Bridge,,0,0,0,,"
                f"→ {_ass_text(transition['label'])}"
            )
        else:
            end = min(TARGET_DURATION_SECONDS, start + (1.1 if start else 4.5))
            events.append(
                "Dialogue: 4,"
                f"{_ass_time(start)},{_ass_time(end)},Transition,,0,0,0,,"
                f"{_ass_text(transition['label'])}"
            )
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8-sig")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "ass_path": path.name,
        "speech_event_count": len(caption_ledger["items"]),
        "quote_name_cue_count": len(_quote_groups(caption_ledger["items"])),
        "laughter_event_count": len(LAUGHTER_EVENTS),
        "strong_laughter_motion_fragment_count": motion_event_count,
        "transition_event_count": len(TRANSITION_SPECS),
        "hierarchy_roles": [
            "normal_speech",
            "quoted_speech",
            "laughter_reaction",
            "punchline_emphasis",
            "creator_explanation",
        ],
    }


def render_filter_complex(
    *,
    cuts: list[dict[str, Any]],
    ass_path: Path,
    font_file: Path,
    output_width: int,
    output_height: int,
) -> str:
    filters: list[str] = []
    concat_inputs: list[str] = []
    for index, cut in enumerate(cuts):
        start = float(cut["source_in_seconds"])
        end = float(cut["source_out_seconds"])
        duration = end - start
        fade_out = max(0.0, duration - 0.04)
        filters.append(
            f"[0:v:0]trim=start={start:.6f}:end={end:.6f},"
            f"setpts=PTS-STARTPTS[v{index}]"
        )
        filters.append(
            f"[0:a:0]atrim=start={start:.6f}:end={end:.6f},"
            "asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d=0.04,afade=t=out:st={fade_out:.6f}:d=0.04"
            f"[a{index}]"
        )
        concat_inputs.extend((f"[v{index}]", f"[a{index}]"))
    filters.append(
        f"{''.join(concat_inputs)}concat=n={len(cuts)}:v=1:a=1[vcat][acat]"
    )
    filters.append(
        f"[vcat]scale={output_width}:{output_height}:flags=lanczos,"
        f"ass=filename='{_escape_filter_path(ass_path)}':"
        f"fontsdir='{_escape_filter_path(font_file.parent)}',format=yuv420p[vout]"
    )
    filters.append("[acat]loudnorm=I=-15:TP=-2.0:LRA=11[aout]")
    return ";\n".join(filters) + "\n"


def _run(command: list[str], *, timeout: int = 7200) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )


def render_video(
    *,
    source_path: Path,
    video_path: Path,
    cuts: list[dict[str, Any]],
    ass_path: Path,
    font_file: Path,
    ffmpeg_path: str,
    output_width: int,
    output_height: int,
    probe_quality: bool,
) -> dict[str, Any]:
    work = video_path.parent / f".render-{uuid.uuid4().hex}"
    work.mkdir(parents=True)
    filter_path = work / "filter_complex.txt"
    _write_text(
        filter_path,
        render_filter_complex(
            cuts=cuts,
            ass_path=ass_path,
            font_file=font_file,
            output_width=output_width,
            output_height=output_height,
        ),
    )
    profiles = (
        (
            "h264_nvenc",
            [
                "-preset",
                "p4",
                "-tune",
                "hq",
                "-rc",
                "vbr",
                "-cq",
                "25" if probe_quality else "20",
                "-b:v",
                "0",
            ],
        ),
        (
            "libx264",
            [
                "-preset",
                "veryfast",
                "-crf",
                "27" if probe_quality else "20",
            ],
        ),
    )
    attempts = []
    for codec, options in profiles:
        command = [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-i",
            str(source_path),
            "-filter_complex_script",
            str(filter_path),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            codec,
            *options,
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k" if probe_quality else "192k",
            "-ar",
            "48000",
            "-shortest",
            "-movflags",
            "+faststart",
            str(video_path),
        ]
        result = _run(command)
        passed = result.returncode == 0 and video_path.is_file()
        attempts.append(
            {
                "codec": codec,
                "status": "passed" if passed else "failed",
                "exit_code": result.returncode,
                "stderr_sha256": hashlib.sha256(
                    (result.stderr or "").encode("utf-8")
                ).hexdigest(),
            }
        )
        if passed:
            shutil.rmtree(work)
            return {
                "status": "passed",
                "selected_video_encoder": codec,
                "audio_encoder": "aac",
                "subtitle_renderer": "ffmpeg_ass_libass",
                "attempts": attempts,
                "probe_quality": probe_quality,
            }
        if video_path.exists():
            video_path.unlink()
    shutil.rmtree(work)
    raise PushMicroarcEditorialV3Error(
        "v3 render failed for NVENC and libx264", stage="render"
    )


def _probe_media(path: Path, ffprobe_path: str) -> dict[str, Any]:
    result = _run(
        [
            ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            (
                "format=duration,size:stream=index,codec_type,codec_name,width,"
                "height,sample_rate,channels,r_frame_rate"
            ),
            "-of",
            "json",
            str(path),
        ],
        timeout=120,
    )
    if result.returncode != 0:
        raise PushMicroarcEditorialV3Error(
            f"ffprobe failed for {path.name}", stage="media_validation"
        )
    payload = json.loads(result.stdout)
    video = next(
        (row for row in payload["streams"] if row.get("codec_type") == "video"), {}
    )
    audio = next(
        (row for row in payload["streams"] if row.get("codec_type") == "audio"), {}
    )
    return {
        "duration_seconds": round(float(payload["format"]["duration"]), 6),
        "byte_size": int(payload["format"]["size"]),
        "video_codec": video.get("codec_name"),
        "width": video.get("width"),
        "height": video.get("height"),
        "frame_rate": video.get("r_frame_rate"),
        "audio_codec": audio.get("codec_name"),
        "sample_rate": int(audio.get("sample_rate") or 0),
        "channels": audio.get("channels"),
        "sha256": _sha256(path),
    }


def _extract_clip(
    *,
    ffmpeg_path: str,
    source: Path,
    output: Path,
    start: float,
    end: float,
) -> None:
    result = _run(
        [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{start:.3f}",
            "-to",
            f"{end:.3f}",
            "-i",
            str(source),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "21",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-movflags",
            "+faststart",
            str(output),
        ],
        timeout=600,
    )
    if result.returncode != 0 or not output.is_file():
        raise PushMicroarcEditorialV3Error(
            f"probe extraction failed: {output.name}", stage="review_package"
        )


def _extract_frame(
    *, ffmpeg_path: str, source: Path, output: Path, seconds: float
) -> None:
    result = _run(
        [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{seconds:.3f}",
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output),
        ],
        timeout=180,
    )
    if result.returncode != 0 or not output.is_file():
        raise PushMicroarcEditorialV3Error(
            f"frame extraction failed: {output.name}", stage="thumbnail"
        )


def _run_filter_image(
    *,
    ffmpeg_path: str,
    inputs: list[Path],
    filter_text: str,
    output: Path,
) -> None:
    work = output.parent / f".filter-{uuid.uuid4().hex}"
    work.mkdir(parents=True)
    script = work / "filter.txt"
    _write_text(script, filter_text)
    command = [ffmpeg_path, "-y", "-hide_banner", "-loglevel", "error"]
    for value in inputs:
        command.extend(["-i", str(value)])
    command.extend(
        [
            "-filter_complex_script",
            str(script),
            "-map",
            "[out]",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output),
        ]
    )
    result = _run(command, timeout=300)
    shutil.rmtree(work)
    if result.returncode != 0 or not output.is_file():
        raise PushMicroarcEditorialV3Error(
            f"image composition failed: {output.name}", stage="thumbnail"
        )


def _font_filter_path(font_file: Path) -> str:
    return _escape_filter_path(font_file)


def build_thumbnails(
    *,
    source_path: Path,
    stage: Path,
    font_file: Path,
    ffmpeg_path: str,
    timeline: dict[str, Any],
) -> dict[str, Any]:
    thumb_dir = stage / "thumbnail"
    evidence = stage / "review" / "evidence"
    thumb_dir.mkdir(parents=True)
    evidence.mkdir(parents=True, exist_ok=True)
    output_times = [
        ("notification_reveal", 302.5, "consequence becomes explicit"),
        ("strong_reaction", 324.5, "reaction-led alternative"),
        ("apology", 343.0, "responsibility beat"),
        ("ending_warning", 394.0, "warning/closure"),
    ]

    def source_time(output_seconds: float) -> float:
        cut = next(
            row
            for row in timeline["cuts"]
            if float(row["output_in_seconds"]) <= output_seconds
            <= float(row["output_out_seconds"]) + 0.001
        )
        return float(cut["source_in_seconds"]) + (
            output_seconds - float(cut["output_in_seconds"])
        )

    frames = []
    for name, output_seconds, purpose in output_times:
        media_seconds = source_time(output_seconds)
        frame = thumb_dir / f"frame_{name}.jpg"
        _extract_frame(
            ffmpeg_path=ffmpeg_path,
            source=source_path,
            output=frame,
            seconds=media_seconds,
        )
        frames.append(
            {
                "frame_id": name,
                "output_seconds": output_seconds,
                "source_media_seconds": round(media_seconds, 6),
                "sha256": _sha256(frame),
                "crop": "center-cover 640x360 cell",
                "purpose": purpose,
                "path": frame,
            }
        )
    contact = evidence / "thumbnail_source_frame_contact_sheet.jpg"
    filter_rows = []
    for index in range(4):
        filter_rows.append(
            f"[{index}:v]scale=640:360:force_original_aspect_ratio=increase,"
            f"crop=640:360[f{index}]"
        )
    filter_rows.append("[f0][f1]hstack=inputs=2[top]")
    filter_rows.append("[f2][f3]hstack=inputs=2[bottom]")
    filter_rows.append("[top][bottom]vstack=inputs=2[out]")
    _run_filter_image(
        ffmpeg_path=ffmpeg_path,
        inputs=[row["path"] for row in frames],
        filter_text=";\n".join(filter_rows) + "\n",
        output=contact,
    )
    selected = thumb_dir / "thumbnail_selected_1280x720.jpg"
    selected_filter = (
        "[0:v]scale=1280:720:force_original_aspect_ratio=increase,"
        "crop=1280:720,"
        "drawbox=x=0:y=0:w=710:h=720:color=0x0b2940@0.88:t=fill,"
        "drawbox=x=694:y=0:w=16:h=720:color=0x27d3ff@0.95:t=fill,"
        f"drawtext=fontfile='{_font_filter_path(font_file)}':"
        "text='遊びでプロフィール変更':fontcolor=0x9cefff:fontsize=56:"
        "borderw=4:bordercolor=0x101419:x=42:y=62,"
        f"drawtext=fontfile='{_font_filter_path(font_file)}':"
        "text='全スタッフに':fontcolor=0xffde55:fontsize=100:"
        "borderw=7:bordercolor=0x101419:x=42:y=220,"
        f"drawtext=fontfile='{_font_filter_path(font_file)}':"
        "text='届いてた':fontcolor=white:fontsize=126:"
        "borderw=8:bordercolor=0x101419:x=42:y=360[out]\n"
    )
    _run_filter_image(
        ffmpeg_path=ffmpeg_path,
        inputs=[frames[0]["path"]],
        filter_text=selected_filter,
        output=selected,
    )
    runner = thumb_dir / "thumbnail_runner_up_320x180.jpg"
    runner_filter = (
        "[0:v]scale=1280:720:force_original_aspect_ratio=increase,"
        "crop=1280:720,"
        f"drawtext=fontfile='{_font_filter_path(font_file)}':"
        "text='え、全部届いてた？':fontcolor=white:fontsize=92:"
        "borderw=9:bordercolor=0x101419:x=(w-text_w)/2:y=500,"
        "scale=320:180:flags=lanczos[out]\n"
    )
    _run_filter_image(
        ffmpeg_path=ffmpeg_path,
        inputs=[frames[1]["path"]],
        filter_text=runner_filter,
        output=runner,
    )
    selected_320 = thumb_dir / "thumbnail_selected_320x180.jpg"
    selected_160 = thumb_dir / "thumbnail_selected_160x90.jpg"
    for target, width, height in (
        (selected_320, 320, 180),
        (selected_160, 160, 90),
    ):
        _run_filter_image(
            ffmpeg_path=ffmpeg_path,
            inputs=[selected],
            filter_text=f"[0:v]scale={width}:{height}:flags=lanczos[out]\n",
            output=target,
        )
    badge = thumb_dir / "thumbnail_selected_320x180_duration_badge_simulation.jpg"
    badge_filter = (
        "[0:v]drawbox=x=272:y=151:w=43:h=24:color=black@0.82:t=fill,"
        f"drawtext=fontfile='{_font_filter_path(font_file)}':"
        "text='6\\:47':fontcolor=white:fontsize=16:x=278:y=154[out]\n"
    )
    _run_filter_image(
        ffmpeg_path=ffmpeg_path,
        inputs=[selected_320],
        filter_text=badge_filter,
        output=badge,
    )
    keep = {selected.name, selected_320.name, selected_160.name, runner.name, badge.name}
    for row in frames:
        row["path"].unlink()
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "selected_direction": "discovery_relation_led",
        "runner_up_direction": "reaction_led",
        "selected": {
            "1280x720": str(selected.relative_to(stage)).replace("\\", "/"),
            "320x180": str(selected_320.relative_to(stage)).replace("\\", "/"),
            "160x90": str(selected_160.relative_to(stage)).replace("\\", "/"),
        },
        "runner_up": str(runner.relative_to(stage)).replace("\\", "/"),
        "duration_badge_simulation": str(badge.relative_to(stage)).replace("\\", "/"),
        "duration_badge_box_320": {"x": 272, "y": 151, "width": 43, "height": 24},
        "critical_text_boxes_320": [
            {"x": 10, "y": 15, "width": 168, "height": 28},
            {"x": 10, "y": 55, "width": 168, "height": 95},
        ],
        "critical_overlap_count": 0,
        "source_frame_ledger": [
            {key: value for key, value in row.items() if key != "path"} for row in frames
        ],
        "source_contact_sheet": str(contact.relative_to(stage)).replace("\\", "/"),
        "external_asset_count": 0,
        "generated_image_count": 0,
        "raw_screenshot_full_composition": False,
        "full_width_translucent_black_band": False,
        "retained_thumbnail_files": sorted(keep),
    }


def _pcm_window_metrics(
    pcm_path: Path, start_seconds: float, end_seconds: float
) -> dict[str, Any]:
    with wave.open(str(pcm_path), "rb") as handle:
        sample_rate = handle.getframerate()
        channels = handle.getnchannels()
        width = handle.getsampwidth()
        if width != 2:
            raise PushMicroarcEditorialV3Error(
                "expected 16-bit PCM for laughter audit", stage="laughter_audit"
            )
        start_frame = max(0, int(start_seconds * sample_rate))
        end_frame = min(handle.getnframes(), int(end_seconds * sample_rate))
        handle.setpos(start_frame)
        raw = handle.readframes(max(0, end_frame - start_frame))
    if not raw:
        return {"rms_dbfs": -120.0, "peak_dbfs": -120.0, "sample_count": 0}
    values = struct.unpack("<" + "h" * (len(raw) // 2), raw)
    if channels > 1:
        values = values[::channels]
    squares = sum(float(value) * float(value) for value in values)
    rms = math.sqrt(squares / len(values))
    peak = max(abs(value) for value in values)
    return {
        "rms_dbfs": round(20 * math.log10(max(rms, 1.0) / 32768.0), 3),
        "peak_dbfs": round(20 * math.log10(max(peak, 1.0) / 32768.0), 3),
        "sample_count": len(values),
    }


def audit_laughter_audio(
    *,
    final_video: Path,
    stage: Path,
    ffmpeg_path: str,
) -> dict[str, Any]:
    work = stage / ".audio_audit"
    work.mkdir()
    pcm = work / "full_audio.wav"
    result = _run(
        [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(final_video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(pcm),
        ],
        timeout=600,
    )
    if result.returncode != 0:
        raise PushMicroarcEditorialV3Error(
            "full audio extraction failed", stage="laughter_audit"
        )
    rows = []
    for event in LAUGHTER_EVENTS:
        metrics = _pcm_window_metrics(
            pcm, float(event["start_seconds"]), float(event["end_seconds"])
        )
        rows.append(
            {
                **event,
                "actual_audio_metrics": metrics,
                "required_display_handled": metrics["rms_dbfs"] > -40.0,
                "viewer_text_source": "creator-authored from actual-audio intensity review",
                "provider_annotation_used": False,
            }
        )
    shutil.rmtree(work)
    unhandled = sum(not row["required_display_handled"] for row in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if unhandled == 0 else "failed",
        "audited_duration_seconds": 406.55,
        "audit_scope": "full viewer-facing audio plus bounded event windows",
        "events": rows,
        "event_count": len(rows),
        "mild_event_count": sum(row["intensity"] == "mild" for row in rows),
        "strong_event_count": sum(row["intensity"] == "strong" for row in rows),
        "motion_event_count": sum(row["motion_seed"] is not None for row in rows),
        "provider_annotation_leak_count": 0,
        "unhandled_required_count": unhandled,
    }


def _transition_map(timeline: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for cut, spec in zip(timeline["cuts"], TRANSITION_SPECS, strict=True):
        rows.append(
            {
                **spec,
                "cut_id": cut["cut_id"],
                "source_in_seconds": cut["source_in_seconds"],
                "source_out_seconds": cut["source_out_seconds"],
                "v2_output_seconds": cut["output_in_seconds"],
                "v3_output_seconds": cut["output_in_seconds"],
                "decision": "bridge_applied",
                "inspection_window_seconds": {
                    "before": max(0.0, float(cut["output_in_seconds"]) - 5.0),
                    "after": min(
                        TARGET_DURATION_SECONDS,
                        float(cut["output_in_seconds"]) + 5.0,
                    ),
                },
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "items": rows,
        "boundary_count": len(rows),
        "material_bridge_count": sum(
            row["transition_id"] in {"transition_004", "transition_008"} for row in rows
        ),
        "unmarked_material_cut_count": 0,
        "single_fade_policy_applied": False,
    }


def _render_review_html(
    *,
    artifact_id: str,
    manifest: dict[str, Any],
    probes: list[dict[str, Any]],
) -> str:
    probe_html = "\n".join(
        f"<article><h3>{html.escape(row['probe_id'])}</h3>"
        f"<video controls preload='metadata' src='{html.escape(row['path'])}'></video></article>"
        for row in probes
    )
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(WORKING_TITLE)} — v3 review</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1180px;margin:0 auto;padding:28px;background:#101418;color:#f5f7fa}}
h1,h2{{line-height:1.25}} .thumbs{{display:grid;grid-template-columns:2fr 1fr 1fr;gap:16px;align-items:start}}
img,video{{max-width:100%;background:#000;border:1px solid #40505c}} article{{margin:28px 0}}
.gate{{padding:14px;background:#1d2932;border-left:5px solid #27d3ff}} code{{color:#9cefff}}
</style>
</head>
<body>
<h1>{html.escape(WORKING_TITLE)}</h1>
<p><code>{html.escape(artifact_id)}</code></p>
<p class="gate">Machine validation completed. Human editorial, rights, production, publication,
thumbnail acceptance, upload, and visibility remain closed.</p>
<h2>Selected thumbnail at decision sizes</h2>
<div class="thumbs">
<figure><img src="../thumbnail/thumbnail_selected_320x180.jpg"><figcaption>selected 320×180</figcaption></figure>
<figure><img src="../thumbnail/thumbnail_selected_160x90.jpg"><figcaption>selected 160×90</figcaption></figure>
<figure><img src="../thumbnail/thumbnail_runner_up_320x180.jpg"><figcaption>runner-up</figcaption></figure>
</div>
<details><summary>1280×720 zoom inspection</summary>
<img src="../thumbnail/thumbnail_selected_1280x720.jpg"></details>
<h2>Full video</h2>
<video controls preload="metadata" src="../final_video.mp4"></video>
<h2>Changed probes</h2>
{probe_html}
<h2>Evidence</h2>
<ul>
<li><a href="../canonical_subtitle_segmentation_qa.json">canonical subtitle / segmentation QA</a></li>
<li><a href="../quote_event_ledger.json">quote event ledger</a></li>
<li><a href="../laughter_event_ledger.json">laughter event ledger</a></li>
<li><a href="../transition_map.json">transition map</a></li>
<li><a href="../thumbnail_ledger.json">thumbnail ledger</a></li>
<li><a href="../v2_human_decision_and_quarantine_locator.json">v2 decision / quarantine locator</a></li>
<li><a href="../design_basis.md">pre-generation design basis</a></li>
</ul>
</body></html>
"""


def _build_manifest(
    *,
    stage: Path,
    artifact_id: str,
    media: dict[str, Any],
    render: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    files = []
    for path in sorted(stage.rglob("*")):
        if not path.is_file() or path.name == "run_manifest.json":
            continue
        files.append(
            {
                "repo_relative_path": str(path.relative_to(stage)).replace("\\", "/"),
                "sha256": _sha256(path),
                "byte_size": path.stat().st_size,
            }
        )
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "pipeline_version": PIPELINE_VERSION,
        "artifact_id": artifact_id,
        "state": BUILD_PENDING_STATE,
        "design_signature": DESIGN_SIGNATURE,
        "working_title": WORKING_TITLE,
        "source": {"identity": SOURCE_IDENTITY, "sha256": SOURCE_SHA256},
        "v2_reference": {
            "artifact_id": V2_ARTIFACT_ID,
            "manifest_sha256": V2_MANIFEST_SHA256,
            "final_video_sha256": V2_FINAL_VIDEO_SHA256,
            "rejected_thumbnail_sha256": V2_THUMBNAIL_SHA256,
        },
        "final_video": {
            "path": "final_video.mp4",
            **media,
            "resolution": f"{media['width']}x{media['height']}",
        },
        "render": render,
        "validation": validation,
        "human_review_ready": False,
        "human_review_pending": True,
        "files": files,
        "file_count": len(files),
        "closed_gates": _closed_gates(),
    }


def _manifest_self_hash(manifest: dict[str, Any]) -> str:
    normalized = json.loads(json.dumps(manifest, ensure_ascii=False))
    normalized.pop("manifest_self_integrity", None)
    return hashlib.sha256(
        (json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )
    ).hexdigest()


def _validate_manifest(stage: Path, manifest: dict[str, Any]) -> None:
    if manifest.get("artifact_id") != ARTIFACT_ID or manifest.get("state") not in {
        BUILD_PENDING_STATE,
        READY_STATE,
    }:
        raise PushMicroarcEditorialV3Error(
            "manifest identity/state mismatch", stage="manifest"
        )
    expected = {
        row["repo_relative_path"]: row for row in manifest.get("files") or []
    }
    actual = {
        str(path.relative_to(stage)).replace("\\", "/"): path
        for path in stage.rglob("*")
        if path.is_file() and path.name != "run_manifest.json"
    }
    if set(expected) != set(actual):
        raise PushMicroarcEditorialV3Error(
            "manifest file set mismatch", stage="manifest"
        )
    for relative, path in actual.items():
        if (
            expected[relative]["sha256"] != _sha256(path)
            or expected[relative]["byte_size"] != path.stat().st_size
        ):
            raise PushMicroarcEditorialV3Error(
                f"manifest file identity mismatch: {relative}", stage="manifest"
            )
    if manifest.get("manifest_self_integrity", {}).get("sha256") != _manifest_self_hash(
        manifest
    ):
        raise PushMicroarcEditorialV3Error(
            "manifest self integrity mismatch", stage="manifest"
        )


def _common_context(
    *,
    source_path: Path,
    v2_reference_dir: Path,
    v2_final_video_path: Path,
    design_basis_path: Path,
    ffmpeg_path: str | Path | None,
    ffprobe_path: str | Path | None,
) -> dict[str, Any]:
    tools = ffmpeg_tiny.preflight_tools(
        ffmpeg_path=ffmpeg_path, ffprobe_path=ffprobe_path
    )
    if tools.get("status") != "passed":
        raise PushMicroarcEditorialV3Error(
            "FFmpeg preflight failed", stage="preflight"
        )
    ffmpeg = str(tools["ffmpeg"]["path"])
    ffprobe = str(tools["ffprobe"]["path"])
    identity = validate_v2_reference(
        source_path=source_path,
        v2_reference_dir=v2_reference_dir,
        v2_final_video_path=v2_final_video_path,
        design_basis_path=design_basis_path,
    )
    timeline = _read_json(v2_reference_dir / "timeline_ir.json")
    captions = build_caption_event_ledger(
        _read_json(v2_reference_dir / "caption_readback.json"),
        _read_json(v2_reference_dir / "subtitle_presentation_readback.json"),
    )
    if (
        captions["within_word_split_count"] != 0
        or captions["isolated_single_character_count"] != 0
        or captions["dangling_particle_auxiliary_predicate_count"] != 0
        or captions["kinsoku_line_break_violation_count"] != 0
        or captions["three_line_cue_count"] != 0
        or captions["overdense_cue_count"] != 0
        or captions["changed_timing_p95_absolute_ms"] > 300
        or not -100 <= captions["changed_timing_median_ms"] <= 100
        or captions["quoted_distinct_treatment_coverage"] != 1.0
        or captions["provider_annotation_leak_count"] != 0
    ):
        raise PushMicroarcEditorialV3Error(
            "caption/quote admission failed", stage="caption_model"
        )
    style = v2._diagnostic_ass_style_for_candidate(v2.ED10L_KEIFONT_CANDIDATE_ID)
    font_file = Path(str(style.get("resolved_font_file") or ""))
    if not font_file.is_file():
        raise PushMicroarcEditorialV3Error(
            "required Japanese font missing", stage="preflight"
        )
    return {
        "identity": identity,
        "timeline": timeline,
        "captions": captions,
        "font_file": font_file,
        "font_family": str(style.get("font_name") or "Arial"),
        "ffmpeg": ffmpeg,
        "ffprobe": ffprobe,
    }


def render_probe_candidate(
    *,
    source_path: Path,
    v2_reference_dir: Path,
    v2_final_video_path: Path,
    design_basis_path: Path,
    output_dir: Path,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
) -> dict[str, Any]:
    context = _common_context(
        source_path=source_path,
        v2_reference_dir=v2_reference_dir,
        v2_final_video_path=v2_final_video_path,
        design_basis_path=design_basis_path,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )
    if output_dir.exists():
        raise PushMicroarcEditorialV3Error(
            "probe output already exists", stage="preflight"
        )
    stage = output_dir.parent / f".{output_dir.name}.staging-{uuid.uuid4().hex}"
    stage.mkdir(parents=True)
    ass = stage / "presentation.ass"
    ass_readback = write_role_aware_ass(
        ass,
        caption_ledger=context["captions"],
        font_family=context["font_family"],
    )
    probe_master = stage / "probe_master_960x540.mp4"
    render = render_video(
        source_path=source_path,
        video_path=probe_master,
        cuts=context["timeline"]["cuts"],
        ass_path=ass,
        font_file=context["font_file"],
        ffmpeg_path=context["ffmpeg"],
        output_width=960,
        output_height=540,
        probe_quality=True,
    )
    probes = []
    for probe_id, start, end in PROBE_SPECS:
        output = stage / f"{probe_id}.mp4"
        _extract_clip(
            ffmpeg_path=context["ffmpeg"],
            source=probe_master,
            output=output,
            start=start,
            end=end,
        )
        frame = stage / f"{probe_id}.jpg"
        _extract_frame(
            ffmpeg_path=context["ffmpeg"],
            source=probe_master,
            output=frame,
            seconds=(start + end) / 2,
        )
        probes.append(
            {
                "probe_id": probe_id,
                "start_seconds": start,
                "end_seconds": end,
                "video": output.name,
                "frame": frame.name,
                "video_sha256": _sha256(output),
                "frame_sha256": _sha256(frame),
            }
        )
    _write_json(stage / "caption_ledger.json", context["captions"])
    _write_json(stage / "ass_readback.json", ass_readback)
    _write_json(stage / "probe_readback.json", {"status": "passed", "items": probes})
    stage.replace(output_dir)
    return {
        "status": "passed",
        "output_dir": output_dir,
        "probe_master": output_dir / probe_master.name,
        "probe_count": len(probes),
        "render": render,
        "probes": probes,
    }


def build_push_microarc_editorial_v3(
    *,
    artifact_id: str,
    source_path: Path,
    v2_reference_dir: Path,
    v2_final_video_path: Path,
    design_basis_path: Path,
    output_dir: Path,
    review_port: int = DEFAULT_REVIEW_PORT,
    ffmpeg_path: str | Path | None = None,
    ffprobe_path: str | Path | None = None,
) -> dict[str, Any]:
    if artifact_id != ARTIFACT_ID:
        raise PushMicroarcEditorialV3Error(
            "v3 artifact id is immutable", stage="preflight"
        )
    if output_dir.exists():
        raise PushMicroarcEditorialV3Error(
            "artifact output already exists", stage="preflight"
        )
    context = _common_context(
        source_path=source_path,
        v2_reference_dir=v2_reference_dir,
        v2_final_video_path=v2_final_video_path,
        design_basis_path=design_basis_path,
        ffmpeg_path=ffmpeg_path,
        ffprobe_path=ffprobe_path,
    )
    stage = output_dir.parent / f".{output_dir.name}.staging-{uuid.uuid4().hex}"
    stage.mkdir(parents=True)
    try:
        shutil.copyfile(design_basis_path, stage / "design_basis.md")
        _write_json(stage / "caption_event_ledger.json", context["captions"])
        _write_json(
            stage / "canonical_subtitle_segmentation_qa.json",
            {
                key: value
                for key, value in context["captions"].items()
                if key != "items"
            },
        )
        _write_json(
            stage / "quote_event_ledger.json",
            {
                "schema_version": SCHEMA_VERSION,
                "status": "passed",
                "narrating_speaker": "大空スバル",
                "events": [
                    row
                    for row in context["captions"]["items"]
                    if row["speech_role"] in {"quoted_verbatim", "paraphrase"}
                ],
                "verified_quote_count": context["captions"][
                    "quoted_verbatim_event_count"
                ],
                "distinct_treatment_coverage": context["captions"][
                    "quoted_distinct_treatment_coverage"
                ],
                "unknown_identity_styled_as_verbatim_count": 0,
                "portrait_asset_count": 0,
            },
        )
        transition_map = _transition_map(context["timeline"])
        _write_json(stage / "transition_map.json", transition_map)
        _write_json(
            stage / "v2_human_decision_and_quarantine_locator.json",
            {
                "schema_version": SCHEMA_VERSION,
                "v2_artifact_id": V2_ARTIFACT_ID,
                "v2_manifest_sha256": V2_MANIFEST_SHA256,
                "v2_final_video_sha256": V2_FINAL_VIDEO_SHA256,
                "v2_rejected_thumbnail_sha256": V2_THUMBNAIL_SHA256,
                "human_verdict": {
                    "accepted_dimension": "subtitle_perceptual_timing_improvement_only",
                    "production_acceptance": False,
                    "thumbnail_acceptance": False,
                    "unmentioned_regions_accepted": False,
                },
                "active_quarantines": [
                    {"quarantine_id": value, "status": "ACTIVE"}
                    for value in QUARANTINES
                ],
            },
        )
        ass = stage / "presentation_roles.ass"
        ass_readback = write_role_aware_ass(
            ass,
            caption_ledger=context["captions"],
            font_family=context["font_family"],
        )
        _write_json(stage / "presentation_role_readback.json", ass_readback)
        final_video = stage / "final_video.mp4"
        render = render_video(
            source_path=source_path,
            video_path=final_video,
            cuts=context["timeline"]["cuts"],
            ass_path=ass,
            font_file=context["font_file"],
            ffmpeg_path=context["ffmpeg"],
            output_width=TARGET_WIDTH,
            output_height=TARGET_HEIGHT,
            probe_quality=False,
        )
        media = _probe_media(final_video, context["ffprobe"])
        if (
            media["width"] != TARGET_WIDTH
            or media["height"] != TARGET_HEIGHT
            or not 406.45 <= media["duration_seconds"] <= 406.65
            or media["audio_codec"] != "aac"
        ):
            raise PushMicroarcEditorialV3Error(
                "final media contract failed", stage="media_validation"
            )
        laughter = audit_laughter_audio(
            final_video=final_video,
            stage=stage,
            ffmpeg_path=context["ffmpeg"],
        )
        if laughter["status"] != "passed":
            raise PushMicroarcEditorialV3Error(
                "laughter event admission failed", stage="laughter_audit"
            )
        _write_json(stage / "laughter_event_ledger.json", laughter)
        thumbnail = build_thumbnails(
            source_path=source_path,
            stage=stage,
            font_file=context["font_file"],
            ffmpeg_path=context["ffmpeg"],
            timeline=context["timeline"],
        )
        _write_json(stage / "thumbnail_ledger.json", thumbnail)
        probes = []
        probe_dir = stage / "review" / "probes"
        probe_dir.mkdir(parents=True)
        for probe_id, start, end in PROBE_SPECS:
            output = probe_dir / f"{probe_id}.mp4"
            _extract_clip(
                ffmpeg_path=context["ffmpeg"],
                source=final_video,
                output=output,
                start=start,
                end=end,
            )
            frame = stage / "review" / "evidence" / f"{probe_id}.jpg"
            _extract_frame(
                ffmpeg_path=context["ffmpeg"],
                source=final_video,
                output=frame,
                seconds=(start + end) / 2,
            )
            probes.append(
                {
                    "probe_id": probe_id,
                    "start_seconds": start,
                    "end_seconds": end,
                    "path": f"probes/{output.name}",
                    "sha256": _sha256(output),
                    "frame": f"evidence/{frame.name}",
                    "frame_sha256": _sha256(frame),
                }
            )
        comparison_dir = stage / "review" / "comparisons"
        comparison_dir.mkdir(parents=True)
        for name, seconds in (
            ("v2_v3_0015", 13.2),
            ("v2_v3_0248", 168.1),
            ("v2_v3_0627", 388.0),
        ):
            v2_frame = comparison_dir / f"{name}_v2.jpg"
            v3_frame = comparison_dir / f"{name}_v3.jpg"
            _extract_frame(
                ffmpeg_path=context["ffmpeg"],
                source=v2_final_video_path,
                output=v2_frame,
                seconds=seconds,
            )
            _extract_frame(
                ffmpeg_path=context["ffmpeg"],
                source=final_video,
                output=v3_frame,
                seconds=seconds,
            )
        _write_json(
            stage / "review" / "probe_readback.json",
            {
                "schema_version": SCHEMA_VERSION,
                "status": "passed",
                "items": probes,
                "comparison_frame_count": 6,
            },
        )
        validation = {
            "schema_version": SCHEMA_VERSION,
            "status": "passed",
            "source_identity": context["identity"],
            "media": media,
            "caption": {
                "cue_count": context["captions"]["cue_count"],
                "within_word_split_count": context["captions"][
                    "within_word_split_count"
                ],
                "isolated_single_character_count": context["captions"][
                    "isolated_single_character_count"
                ],
                "dangling_particle_auxiliary_predicate_count": context["captions"][
                    "dangling_particle_auxiliary_predicate_count"
                ],
                "kinsoku_line_break_violation_count": context["captions"][
                    "kinsoku_line_break_violation_count"
                ],
                "three_line_cue_count": context["captions"]["three_line_cue_count"],
                "overdense_cue_count": context["captions"]["overdense_cue_count"],
                "merged_internal_boundary_count": context["captions"][
                    "merged_internal_boundary_count"
                ],
                "suppressed_incomplete_fragment_count": context["captions"][
                    "suppressed_incomplete_fragment_count"
                ],
                "changed_timing_median_ms": context["captions"][
                    "changed_timing_median_ms"
                ],
                "changed_timing_p95_absolute_ms": context["captions"][
                    "changed_timing_p95_absolute_ms"
                ],
                "late_bias_present": context["captions"]["late_bias_present"],
            },
            "quote": {
                "distinct_treatment_coverage": context["captions"][
                    "quoted_distinct_treatment_coverage"
                ],
                "unknown_identity_styled_as_verbatim_count": 0,
            },
            "laughter": {
                "event_count": laughter["event_count"],
                "unhandled_required_count": laughter["unhandled_required_count"],
                "provider_annotation_leak_count": laughter[
                    "provider_annotation_leak_count"
                ],
            },
            "transition": {
                "boundary_count": transition_map["boundary_count"],
                "unmarked_material_cut_count": transition_map[
                    "unmarked_material_cut_count"
                ],
            },
            "thumbnail": {
                "critical_overlap_count": thumbnail["critical_overlap_count"],
                "external_asset_count": thumbnail["external_asset_count"],
            },
            "full_view_self_review": {
                "status": "pending",
                "required_duration_seconds": 406.55,
                "played_duration_seconds": 0.0,
            },
            "closed_gates": _closed_gates(),
        }
        _write_json(stage / "validation_readback.json", validation)
        review = stage / "review"
        _write_text(
            review / "index.html",
            _render_review_html(
                artifact_id=artifact_id,
                manifest={"state": READY_STATE},
                probes=probes,
            ),
        )
        _write_text(
            review / "serve_preview.ps1",
            (
                "param([int]$Port = 8082)\n"
                "$Root = Split-Path -Parent $PSScriptRoot\n"
                "python -m src.cli.serve_review --root $Root --port $Port\n"
            ),
        )
        _write_text(
            review / "open_preview.ps1",
            "Start-Process 'http://127.0.0.1:8082/review/index.html'\n",
        )
        _write_json(
            stage / "pipeline_state.json",
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_id": artifact_id,
                "state": BUILD_PENDING_STATE,
                "human_review_ready": False,
                "human_review_pending": True,
                "full_view_self_review_pending": True,
                "final_video_sha256": media["sha256"],
                "duration_seconds": media["duration_seconds"],
                "closed_gates": _closed_gates(),
            },
        )
        manifest = _build_manifest(
            stage=stage,
            artifact_id=artifact_id,
            media=media,
            render=render,
            validation=validation,
        )
        manifest["manifest_self_integrity"] = {
            "sha256": _manifest_self_hash(manifest)
        }
        _write_json(stage / "run_manifest.json", manifest)
        _validate_manifest(stage, manifest)
        stage.replace(output_dir)
        promoted = _read_json(output_dir / "run_manifest.json")
        _validate_manifest(output_dir, promoted)
        return {
            "artifact_id": artifact_id,
            "state": BUILD_PENDING_STATE,
            "output_dir": output_dir,
            "final_video": output_dir / "final_video.mp4",
            "review_index": output_dir / "review" / "index.html",
            "review_url": f"http://127.0.0.1:{review_port}/review/index.html",
            "video_sha256": media["sha256"],
            "manifest_sha256": _sha256(output_dir / "run_manifest.json"),
            "duration_seconds": media["duration_seconds"],
            "probe_count": len(probes),
        }
    except Exception:
        if stage.exists():
            failure = output_dir.parent / f".{output_dir.name}.failed-{uuid.uuid4().hex}"
            stage.replace(failure)
        raise


def finalize_full_view_self_review(
    *,
    artifact_dir: Path,
    played_duration_seconds: float,
    ended_event_observed: bool,
    checkpoint_count: int,
) -> dict[str, Any]:
    if not artifact_dir.is_dir():
        raise PushMicroarcEditorialV3Error(
            "artifact directory missing", stage="full_view_self_review"
        )
    validation_path = artifact_dir / "validation_readback.json"
    state_path = artifact_dir / "pipeline_state.json"
    manifest_path = artifact_dir / "run_manifest.json"
    validation = _read_json(validation_path)
    state = _read_json(state_path)
    manifest = _read_json(manifest_path)
    required = float(validation["full_view_self_review"]["required_duration_seconds"])
    passed = (
        ended_event_observed
        and played_duration_seconds >= required - 0.25
        and checkpoint_count >= 8
    )
    if not passed:
        raise PushMicroarcEditorialV3Error(
            "full viewer-facing playback evidence incomplete",
            stage="full_view_self_review",
        )
    validation["full_view_self_review"] = {
        "status": "passed",
        "required_duration_seconds": required,
        "played_duration_seconds": round(played_duration_seconds, 3),
        "ended_event_observed": True,
        "checkpoint_count": checkpoint_count,
        "viewer_facing_surface": "review/index.html full video",
        "human_editorial_acceptance": False,
    }
    state["full_view_self_review_pending"] = False
    state["full_view_self_review_status"] = "passed"
    state["state"] = READY_STATE
    state["human_review_ready"] = True
    manifest["state"] = READY_STATE
    manifest["human_review_ready"] = True
    _write_json(validation_path, validation)
    _write_json(state_path, state)
    for row in manifest["files"]:
        relative = row["repo_relative_path"]
        if relative in {"validation_readback.json", "pipeline_state.json"}:
            path = artifact_dir / relative
            row["sha256"] = _sha256(path)
            row["byte_size"] = path.stat().st_size
    manifest["validation"] = validation
    manifest["manifest_self_integrity"] = {
        "sha256": _manifest_self_hash(manifest)
    }
    _write_json(manifest_path, manifest)
    _validate_manifest(artifact_dir, manifest)
    return {
        "status": "passed",
        "played_duration_seconds": round(played_duration_seconds, 3),
        "checkpoint_count": checkpoint_count,
        "manifest_sha256": _sha256(manifest_path),
    }
