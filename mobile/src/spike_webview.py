"""Phase 0.4 + 0.5 spike: MediaPipe in a WebView and two JS -> Python channels.

Check on the phone with:  adb logcat -d | Select-String "MP |BRIDGE|JS:"
"""

from __future__ import annotations

import inspect
import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import flet as ft
from bridge.local_server import LocalServer, parse_envelope

log = logging.getLogger("strand")

WEB_ROOT = Path(__file__).resolve().parent / "web"
CONSOLE_PREFIX = "STRAND:"
WEBVIEW_PLATFORMS = {ft.PagePlatform.ANDROID, ft.PagePlatform.IOS, ft.PagePlatform.MACOS}


def call(page: ft.Page, fn: Callable[..., Any], *args: Any) -> None:
    """Call a Flet method that is sync in some versions and async in others."""
    result = fn(*args)
    if inspect.isawaitable(result):

        async def wait() -> None:
            await result

        page.run_task(wait)


def missing_assets() -> list[str]:
    needed = [
        "vendor/tasks-vision/vision_bundle.mjs",
        "vendor/models/face_landmarker.task",
        "test_face.jpg",
    ]
    return [p for p in needed if not (WEB_ROOT / p).is_file()]


def build(page: ft.Page, status: ft.Text) -> ft.Control:
    """Start the local server and return the WebView (or a hint on desktop)."""
    missing = missing_assets()
    if missing:
        log.error("MP FAIL missing assets: %s", missing)
        return ft.Text(
            "Lipsesc fișiere în src/web: "
            + ", ".join(missing)
            + "\nRulează scripts/fetch_web_assets.py",
            color="#ff8a80",
        )

    webview_ref: dict[str, Any] = {}

    def on_message(envelope: dict[str, Any], channel: str, size: int, latency_ms: float) -> None:
        kind = envelope["type"]
        data = envelope.get("data") or {}
        log.info("BRIDGE %s type=%s bytes=%d ms=%.1f", channel, kind, size, latency_ms)
        if kind == "face_result" and channel == "http":
            log.info(
                "MP OK points=%d matrix=%s delegate=%s init_ms=%s detect_ms=%s",
                len(data.get("landmarks", [])),
                "yes" if data.get("matrix") else "no",
                data.get("delegate"),
                data.get("init_ms"),
                data.get("detect_ms"),
            )
            status.value = (
                f"MediaPipe: {len(data.get('landmarks', []))} puncte, "
                f"detect {data.get('detect_ms')} ms"
            )
            page.update()
            webview = webview_ref.get("w")
            if webview is not None:
                ack = json.dumps({"points": len(data.get("landmarks", [])), "via": channel})
                call(page, webview.run_javascript, f"window.strandAck({ack})")
        elif kind == "error":
            log.error("MP FAIL %s", data.get("message"))
            status.value = f"MP FAIL: {data.get('message')}"
            page.update()

    server = LocalServer(WEB_ROOT, on_message).start()
    url = server.base_url + "index.html"

    if page.platform not in WEBVIEW_PLATFORMS:
        # Flet's WebView does not run on Windows/Linux: open the page in the browser instead.
        # The HTTP channel still works there, so the page and MediaPipe can be tested.
        log.info("desktop: open %s", url)
        return ft.Column(
            [
                ft.Text("WebView merge doar pe telefon. Pe laptop, deschide pagina în browser:"),
                ft.FilledButton(
                    "Deschide în browser", on_click=lambda _: call(page, page.launch_url, url)
                ),
            ]
        )

    import flet_webview as fwv

    def on_console(e: Any) -> None:
        message: str = e.message
        if message.startswith(CONSOLE_PREFIX):
            try:
                parse_envelope(message[len(CONSOLE_PREFIX) :], "console", on_message)
            except ValueError as exc:
                log.error("BRIDGE console bad message: %s", exc)
        else:
            log.info("JS: %s", message[:300])

    webview = fwv.WebView(
        url=url,
        expand=True,
        on_console_message=on_console,
        on_web_resource_error=lambda e: log.error("JS: resource error %s", e.data),
        on_page_ended=lambda e: log.info("JS: page loaded"),
    )
    webview_ref["w"] = webview
    return webview
