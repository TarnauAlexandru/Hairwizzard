"""Phase 0 spike app.

0.3: an ONNX model runs with onnxruntime (top line).
0.4 + 0.5: MediaPipe Face Landmarker runs in a WebView and sends its results to Python.

Check on the phone with:  adb logcat -d | Select-String "ONNX|MP |BRIDGE|JS:"
"""

import logging

import flet as ft
import numpy as np
from spike_onnx import OnnxSpike
from spike_webview import build

log = logging.getLogger("strand")
logging.basicConfig(level=logging.INFO)

TEXT = "#F2EFE9"


def onnx_line() -> str:
    try:
        spike = OnnxSpike()
        p = spike.predict(np.array([0.5, -1.2, 0.3, 2.0], dtype=np.float32))
    except Exception as exc:
        log.exception("ONNX FAIL %s: %s", type(exc).__name__, exc)
        return f"ONNX FAIL: {type(exc).__name__}"
    log.info("ONNX OK pred=%d ms=%.2f", p.label, p.ms)
    return f"ONNX OK · {p.ms:.2f} ms"


def main(page: ft.Page) -> None:
    page.title = "Strand"
    page.bgcolor = "#16171A"
    page.padding = 0

    status = ft.Text("MediaPipe: se încarcă…", color=TEXT)
    header = ft.Container(
        ft.Column(
            [
                ft.Text("Strand · spike", size=20, color=TEXT, weight=ft.FontWeight.BOLD),
                ft.Text(onnx_line(), color=TEXT),
                status,
            ],
            spacing=2,
        ),
        padding=12,
    )
    page.add(ft.SafeArea(ft.Column([header, build(page, status)], expand=True), expand=True))


# ft.run exists in newer Flet; ft.app in older ones.
(getattr(ft, "run", None) or ft.app)(main)
