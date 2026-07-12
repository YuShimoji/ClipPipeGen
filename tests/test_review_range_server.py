from __future__ import annotations

import http.client
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from src.cli.serve_review import RangeRequestHandler


def _server(root: Path) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("127.0.0.1", 0), RangeRequestHandler)
    server.root = root  # type: ignore[attr-defined]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def test_review_server_supports_head_and_middle_byte_range(tmp_path: Path) -> None:
    payload = bytes(range(256)) * 4
    (tmp_path / "video.mp4").write_bytes(payload)
    server = _server(tmp_path)
    try:
        host, port = server.server_address
        connection = http.client.HTTPConnection(host, port, timeout=5)
        connection.request("HEAD", "/video.mp4")
        response = connection.getresponse()
        response.read()
        assert response.status == 200
        assert response.getheader("Accept-Ranges") == "bytes"
        assert response.getheader("Content-Length") == str(len(payload))

        connection.request("GET", "/video.mp4", headers={"Range": "bytes=100-149"})
        response = connection.getresponse()
        body = response.read()
        assert response.status == 206
        assert response.getheader("Accept-Ranges") == "bytes"
        assert response.getheader("Content-Range") == f"bytes 100-149/{len(payload)}"
        assert response.getheader("Content-Length") == "50"
        assert body == payload[100:150]
    finally:
        server.shutdown()
        server.server_close()


def test_review_server_rejects_path_traversal(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text("ok", encoding="utf-8")
    server = _server(tmp_path)
    try:
        host, port = server.server_address
        connection = http.client.HTTPConnection(host, port, timeout=5)
        connection.request("GET", "/%2e%2e/outside.txt")
        response = connection.getresponse()
        response.read()
        assert response.status == 403
    finally:
        server.shutdown()
        server.server_close()
