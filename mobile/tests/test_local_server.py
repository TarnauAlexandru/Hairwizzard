"""The local server must serve files only with the token and pass JS messages to Python."""

import http.client
import json
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bridge.local_server import LocalServer


@pytest.fixture
def server(tmp_path: Path):
    (tmp_path / "index.html").write_text("<p>hi</p>")
    (tmp_path / "m.wasm").write_bytes(b"\0asm")
    received: list[tuple[str, str, int]] = []
    srv = LocalServer(tmp_path, lambda env, ch, size, ms: received.append((env["type"], ch, size)))
    srv.start()
    yield srv, received
    srv.stop()


def request(srv: LocalServer, method: str, path: str, body: bytes | None = None):
    conn = http.client.HTTPConnection("127.0.0.1", srv.port, timeout=5)
    headers = {"Content-Type": "application/json"} if body else {}
    conn.request(method, path, body=body, headers=headers)
    res = conn.getresponse()
    return res.status, res.getheader("Content-Type"), res.read()


def test_serves_files_with_token(server) -> None:
    srv, _ = server
    status, _, body = request(srv, "GET", f"/{srv.token}/index.html")
    assert status == 200 and body == b"<p>hi</p>"
    assert request(srv, "GET", f"/{srv.token}/m.wasm")[1] == "application/wasm"


@pytest.mark.parametrize("path", ["/index.html", "/wrong-token/index.html", "/"])
def test_rejects_requests_without_token(server, path: str) -> None:
    srv, _ = server
    assert request(srv, "GET", path)[0] == 403


def test_no_path_traversal(server) -> None:
    srv, _ = server
    status, _, body = request(srv, "GET", f"/{srv.token}/../../etc/passwd")
    assert status == 404 and b"root:" not in body


def test_post_bridge_delivers_message(server) -> None:
    srv, received = server
    msg = json.dumps({"type": "face_result", "sent_ms": time.time() * 1000, "data": {}}).encode()
    assert request(srv, "POST", f"/{srv.token}/bridge", msg)[0] == 204
    assert received == [("face_result", "http", len(msg))]


def test_post_rejects_bad_json_and_wrong_path(server) -> None:
    srv, received = server
    assert request(srv, "POST", f"/{srv.token}/bridge", b"not json")[0] == 400
    assert request(srv, "POST", f"/{srv.token}/other", b"{}")[0] == 403
    assert received == []
