"""Phase 0.3 spike screen: run an ONNX model on the phone and show the result and time.

Check on the phone with:  adb logcat -d | Select-String "ONNX"
"""

import logging

import flet as ft
import numpy as np
from spike_onnx import OnnxSpike

log = logging.getLogger("strand")
logging.basicConfig(level=logging.INFO)

SAMPLE = np.array([0.5, -1.2, 0.3, 2.0], dtype=np.float32)
TEXT = "#F2EFE9"
ACCENT = "#C9A46A"


def main(page: ft.Page) -> None:
    page.title = "Strand"
    page.bgcolor = "#16171A"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    title = ft.Text("Strand · ONNX spike", size=24, color=TEXT, weight=ft.FontWeight.BOLD)
    result = ft.Text("", size=16, color=TEXT, text_align=ft.TextAlign.CENTER)
    rng = np.random.default_rng()

    try:
        spike = OnnxSpike()
    except Exception as exc:
        log.exception("ONNX FAIL %s: %s", type(exc).__name__, exc)
        result.value = f"ONNX FAIL\n{type(exc).__name__}: {exc}"
        page.add(title, result)
        return

    log.info(
        "ONNX loaded ort=%s load_ms=%.1f path=%s", spike.ort_version, spike.load_ms, spike.path
    )

    def run(features: np.ndarray) -> None:
        p = spike.predict(features)
        log.info("ONNX OK pred=%d ms=%.2f", p.label, p.ms)
        result.value = (
            f"onnxruntime {spike.ort_version}\n"
            f"clasa {p.label} (p={p.probability:.2f})\n"
            f"{p.ms:.2f} ms · încărcare {spike.load_ms:.0f} ms"
        )

    def on_tap(_: ft.ControlEvent) -> None:
        run(rng.normal(size=SAMPLE.shape).astype(np.float32))
        page.update()

    run(SAMPLE)
    page.add(
        title,
        result,
        ft.FilledButton("Rulează predicția", on_click=on_tap, bgcolor=ACCENT, color="#16171A"),
    )


# ft.run exists in newer Flet; ft.app in older ones.
(getattr(ft, "run", None) or ft.app)(main)
