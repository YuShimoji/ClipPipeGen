from __future__ import annotations

import http.client
import socket
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

from src.cli.serve_review import RangeRequestHandler, create_review_server, run


class _ResettingWriter:
    def write(self, _payload: bytes) -> None:
        raise ConnectionResetError("review tab closed")


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


def test_review_server_treats_closed_media_tab_as_normal_client_exit(
    tmp_path: Path,
) -> None:
    (tmp_path / "video.mp4").write_bytes(b"video bytes")
    handler = object.__new__(RangeRequestHandler)
    handler.server = SimpleNamespace(root=tmp_path)
    handler.path = "/video.mp4"
    handler.headers = {}
    handler.wfile = _ResettingWriter()
    handler.send_response = lambda _status: None
    handler.send_header = lambda _name, _value: None
    handler.end_headers = lambda: None

    handler._send_file(head_only=False)


def test_review_server_factory_is_loopback_only_and_stops_cleanly(
    tmp_path: Path,
) -> None:
    (tmp_path / "index.html").write_text("ok", encoding="utf-8")
    reservation = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reservation.bind(("127.0.0.1", 0))
    port = reservation.getsockname()[1]
    reservation.close()
    server = create_review_server(root=tmp_path, port=port)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        host, port = server.server_address
        assert host == "127.0.0.1"
        connection = http.client.HTTPConnection(host, port, timeout=5)
        connection.request("GET", "/index.html")
        response = connection.getresponse()
        assert response.status == 200
        assert response.read() == b"ok"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert not thread.is_alive()


def test_review_server_refuses_unknown_port_owner_without_stopping_it(
    tmp_path: Path,
) -> None:
    (tmp_path / "index.html").write_text("ok", encoding="utf-8")
    owner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    owner.bind(("127.0.0.1", 0))
    owner.listen(1)
    port = owner.getsockname()[1]
    try:
        assert run(["--root", str(tmp_path), "--port", str(port)]) == 2
        probe = socket.create_connection(("127.0.0.1", port), timeout=5)
        probe.close()
    finally:
        owner.close()
