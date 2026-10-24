"""Local HTTP server that serves the WebView page and receives messages from JavaScript.

Why a server: the WebView cannot load MediaPipe's WebAssembly from file:// URLs, and
Flet's WebView has no JS -> Python channel. Serving over http://127.0.0.1 solves both:
the page loads normally and can POST JSON back to Python.

Security: other apps on the phone can reach 127.0.0.1 too. So the server listens on
127.0.0.1 only, on a random port, and every URL must start with a random secret
token (/<token>/...). Without it the answer is 403, so no other app can read the
user's photo or send fake results.
"""

from __future__ import annotations

import http.server
import json
import logging
import secrets
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

log = logging.getLogger("strand.bridge")

MAX_BODY_BYTES = 8 * 1024 * 1024
BRIDGE_PATH = "bridge"

# (envelope, channel, payload_bytes, latency_ms)
MessageHandler = Callable[[dict[str, Any], str, int, float], None]


def parse_envelope(raw: str, channel: str, on_message: MessageHandler) -> None:
    """Decode one {"type", "sent_ms", "data"} message from JS and hand it to `on_message`."""
    received_ms = time.time() * 1000
    envelope = json.loads(raw)
    if not isinstance(envelope, dict) or "type" not in envelope:
        raise ValueError("bridge message must be an object with a 'type'")
    latency_ms = received_ms - float(envelope.get("sent_ms", received_ms))
    on_message(envelope, channel, len(raw.encode()), latency_ms)


class _Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map: ClassVar[dict[str, str]] = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".mjs": "text/javascript",
        ".js": "text/javascript",
        ".wasm": "application/wasm",
        ".task": "application/octet-stream",
    }

    # Set per server class in LocalServer.__init__.
    token: str = ""
    on_message: MessageHandler

    def _strip_token(self) -> str | None:
        prefix = f"/{self.token}/"
        if not self.path.startswith(prefix):
            return None
        return self.path[len(prefix) - 1 :]

    def do_GET(self) -> None:
        rest = self._strip_token()
        if rest is None:
            self.send_error(403)
            return
        self.path = rest
        super().do_GET()

    def do_HEAD(self) -> None:
        rest = self._strip_token()
        if rest is None:
            self.send_error(403)
            return
        self.path = rest
        super().do_HEAD()

    def do_POST(self) -> None:
        rest = self._strip_token()
        if rest is None or rest.split("?")[0] != f"/{BRIDGE_PATH}":
            self.send_error(403)
            return
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > MAX_BODY_BYTES:
            self.send_error(413)
            return
        raw = self.rfile.read(length).decode("utf-8")
        try:
            parse_envelope(raw, "http", type(self).on_message)
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_error(400, str(exc))
            return
        self.send_response(204)
        self.end_headers()

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        log.debug("http %s", format % args)


class LocalServer:
    """Serves `root` at http://127.0.0.1:<random port>/<token>/ in a background thread."""

    def __init__(self, root: Path, on_message: MessageHandler) -> None:
        self.token = secrets.token_urlsafe(24)
        directory = str(root)

        handler = type(
            "BoundHandler",
            (_Handler,),
            {"token": self.token, "on_message": staticmethod(on_message)},
        )

        def factory(*args: Any, **kwargs: Any) -> _Handler:
            return handler(*args, directory=directory, **kwargs)

        self._httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), factory)
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/{self.token}/"

    def start(self) -> LocalServer:
        self._thread.start()
        log.info("local server on 127.0.0.1:%d", self.port)
        return self

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
