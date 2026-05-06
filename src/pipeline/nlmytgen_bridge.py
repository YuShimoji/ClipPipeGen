"""NLMYTGen CLI subprocess bridge.

NLMYTGen は別リポ。本リポは CLI subprocess 経由でのみ再利用する（INVARIANTS）。
- 直接 import / コピー / 編集は禁止
- silent fallback は禁止：見つからない／非ゼロ終了は例外で止める
- 設定は config/nlmytgen_path.json（gitignored）。雛形は config/nlmytgen_path.json.example
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_PATH_DEFAULT = "config/nlmytgen_path.json"


class BridgeConfigError(Exception):
    pass


class BridgeExecutionError(Exception):
    """NLMYTGen が見つからない／非ゼロ終了した時に raise する。"""

    def __init__(self, message: str, *, returncode: int | None = None, stdout: str = "", stderr: str = ""):
        super().__init__(message)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@dataclass
class BridgeConfig:
    nlmytgen_root: Path
    python_executable: str

    @classmethod
    def load(cls, config_path: str | Path = CONFIG_PATH_DEFAULT) -> "BridgeConfig":
        p = Path(config_path)
        if not p.exists():
            raise BridgeConfigError(
                f"NLMYTGen bridge config not found: {p}. "
                f"Copy config/nlmytgen_path.json.example to {p} and adjust paths."
            )
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise BridgeConfigError(f"invalid JSON in {p}: {exc}") from exc

        root_str = data.get("nlmytgen_root")
        if not root_str:
            raise BridgeConfigError(f"{p}: nlmytgen_root is required")
        root = Path(root_str)
        if not root.exists():
            raise BridgeConfigError(
                f"nlmytgen_root does not exist: {root}. "
                "Verify the path in your bridge config."
            )
        if not (root / "src" / "cli" / "main.py").exists():
            raise BridgeConfigError(
                f"{root} does not look like an NLMYTGen checkout "
                f"(missing src/cli/main.py)"
            )

        python_exe = data.get("python_executable") or "python"
        if not _resolve_executable(python_exe, root):
            raise BridgeConfigError(
                f"python_executable {python_exe!r} not found on PATH or as absolute path"
            )

        return cls(nlmytgen_root=root, python_executable=python_exe)


def _resolve_executable(name: str, search_root: Path) -> str | None:
    if Path(name).is_absolute() and Path(name).exists():
        return name
    found = shutil.which(name)
    if found:
        return found
    return None


def call_nlmytgen(
    subcommand: str,
    args: list[str],
    *,
    config: BridgeConfig | None = None,
    expect_json: bool = False,
    timeout: float | None = 60.0,
) -> dict[str, Any] | str:
    """NLMYTGen CLI を subprocess で呼ぶ。

    expect_json=True なら stdout を JSON parse して dict を返す。
    非ゼロ終了は BridgeExecutionError。
    """
    cfg = config or BridgeConfig.load()
    cmd = [cfg.python_executable, "-m", "src.cli.main", subcommand, *args]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cfg.nlmytgen_root),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
        )
    except FileNotFoundError as exc:
        raise BridgeExecutionError(
            f"failed to launch NLMYTGen subprocess: {exc}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise BridgeExecutionError(
            f"NLMYTGen subprocess timed out after {timeout}s"
        ) from exc

    if result.returncode != 0:
        raise BridgeExecutionError(
            f"NLMYTGen {subcommand} exited with {result.returncode}",
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    if expect_json:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise BridgeExecutionError(
                f"NLMYTGen {subcommand} stdout is not valid JSON: {exc}",
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            ) from exc
    return result.stdout


def audit_thumbnail_template(
    ymmp_path: str | Path,
    *,
    config: BridgeConfig | None = None,
) -> dict[str, Any]:
    """NLMYTGen audit-thumbnail-template (JSON output)."""
    return call_nlmytgen(
        "audit-thumbnail-template",
        [str(ymmp_path), "--format", "json"],
        config=config,
        expect_json=True,
    )  # type: ignore[return-value]


def patch_thumbnail_template(
    ymmp_path: str | Path,
    patch_payload: dict[str, Any],
    *,
    output_path: str | Path | None,
    dry_run: bool = False,
    config: BridgeConfig | None = None,
    work_dir: Path | None = None,
) -> dict[str, Any]:
    """NLMYTGen patch-thumbnail-template (JSON output).

    patch_payload は NLMYTGen の patch JSON 形式（{"slots": {...}} or
    {"text": {...}, "image": {...}}）。本リポでは flat slots 形式を採用する。
    """
    if work_dir is None:
        work_dir = Path(".")
    work_dir.mkdir(parents=True, exist_ok=True)
    patch_file = work_dir / "_thumbnail_patch.json"
    patch_file.write_text(
        json.dumps(patch_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    args = [str(ymmp_path), "--patch", str(patch_file.resolve()), "--format", "json"]
    if output_path:
        args.extend(["-o", str(Path(output_path).resolve())])
    if dry_run:
        args.append("--dry-run")

    return call_nlmytgen(
        "patch-thumbnail-template",
        args,
        config=config,
        expect_json=True,
    )  # type: ignore[return-value]
