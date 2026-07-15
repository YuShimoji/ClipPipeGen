"""Host-aware recovery commands for the ignored OUT-08 review package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.pipeline.out08_private_review_package_recovery import (
    DEFAULT_CONTRACT_PATH,
    Out08PrivateRecoveryError,
    default_package_path,
    export_package,
    import_package,
    load_contract,
    probe_host,
)


def run(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    contract_path = Path(args.contract)
    if not contract_path.is_absolute():
        contract_path = repo_root / contract_path

    try:
        contract = load_contract(contract_path.resolve())
        if args.package:
            package_argument = Path(args.package)
            if not package_argument.is_absolute():
                package_argument = repo_root / package_argument
            package_path = package_argument.resolve()
        else:
            package_path = default_package_path(repo_root, contract)
        if args.action == "probe":
            result = probe_host(
                package_path=package_path,
                contract=contract,
                repo_root=repo_root,
                port=args.port,
            )
        elif args.action == "export":
            result = export_package(
                package_path=package_path,
                destination=Path(args.destination),
                contract=contract,
                repo_root=repo_root,
            )
        else:
            result = import_package(
                archive_path=Path(args.archive),
                package_path=package_path,
                contract=contract,
                repo_root=repo_root,
                start_server=args.start_server,
                port=args.port,
            )
    except Out08PrivateRecoveryError as exc:
        failure = {
            "status": "failed",
            "category": exc.category,
            "message": str(exc),
        }
        if args.format == "json":
            print(json.dumps(failure, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(
                f"OUT-08 recovery failed [{exc.category}]: {exc}",
                file=sys.stderr,
            )
        return 1

    _print_result(result, output_format=args.format)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recover-out08-private-review-package",
        description=(
            "Probe, export, or atomically import the exact ignored OUT-08 private "
            "review package without regenerating or placing media in Git."
        ),
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT_PATH))
    parser.add_argument("--package")
    parser.add_argument("--format", choices=("text", "json"), default="json")
    subparsers = parser.add_subparsers(dest="action", required=True)

    probe = subparsers.add_parser(
        "probe", help="classify package and local server state"
    )
    probe.add_argument("--port", type=int, default=8071)

    export = subparsers.add_parser(
        "export", help="build a deterministic archive on the last-verified host"
    )
    export.add_argument("--destination", required=True)

    import_parser = subparsers.add_parser(
        "import", help="verify and atomically import a private archive"
    )
    import_parser.add_argument("--archive", required=True)
    import_parser.add_argument("--start-server", action="store_true")
    import_parser.add_argument("--port", type=int, default=8071)
    return parser


def _print_result(result: dict[str, Any], *, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return
    for key, value in result.items():
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
        else:
            rendered = str(value)
        print(f"{key}: {rendered}")
