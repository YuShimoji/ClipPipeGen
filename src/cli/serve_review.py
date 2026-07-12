from __future__ import annotations

import argparse
import mimetypes
import posixpath
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


class RangeRequestHandler(BaseHTTPRequestHandler):
    server_version = "ClipPipeGenRangeHTTP/1.0"

    def do_HEAD(self) -> None:
        self._send_file(head_only=True)

    def do_GET(self) -> None:
        self._send_file(head_only=False)

    def _send_file(self, *, head_only: bool) -> None:
        root = Path(self.server.root).resolve()  # type: ignore[attr-defined]
        target = _resolve_request_path(root, self.path)
        if target is None:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        file_size = target.stat().st_size
        range_header = self.headers.get("Range")
        byte_range = _parse_range_header(range_header, file_size)
        if range_header and byte_range is None:
            self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes */{file_size}")
            self.end_headers()
            return

        start = 0
        end = file_size - 1
        status = HTTPStatus.OK
        if byte_range is not None:
            start, end = byte_range
            status = HTTPStatus.PARTIAL_CONTENT

        content_length = max(0, end - start + 1)
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(content_length))
        if status == HTTPStatus.PARTIAL_CONTENT:
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.end_headers()
        if head_only:
            return

        with target.open("rb") as handle:
            handle.seek(start)
            remaining = content_length
            while remaining > 0:
                chunk = handle.read(min(1024 * 256, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)


def _resolve_request_path(root: Path, raw_path: str) -> Path | None:
    path = unquote(urlsplit(raw_path).path)
    if any(part == ".." for part in path.split("/")):
        return None
    normalized = posixpath.normpath(path).lstrip("/")
    target = (root / normalized).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None
    return target


def _parse_range_header(value: str | None, file_size: int) -> tuple[int, int] | None:
    if not value:
        return None
    if not value.startswith("bytes=") or "," in value:
        return None
    start_text, separator, end_text = value[6:].partition("-")
    if separator != "-":
        return None
    try:
        if start_text == "":
            suffix = int(end_text)
            if suffix <= 0:
                return None
            start = max(0, file_size - suffix)
            end = file_size - 1
        else:
            start = int(start_text)
            end = int(end_text) if end_text else file_size - 1
    except ValueError:
        return None
    if start < 0 or end < start or start >= file_size:
        return None
    return start, min(end, file_size - 1)


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve a fixed review package with byte ranges.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8060)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"--root must be a directory: {root}")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), RangeRequestHandler)
    server.root = root  # type: ignore[attr-defined]
    print(f"Serving {root} at http://127.0.0.1:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
