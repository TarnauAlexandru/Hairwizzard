"""Phase 0.2 hello world: one screen, one button. Proves laptop -> phone works."""

import logging

import flet as ft

log = logging.getLogger("strand")
logging.basicConfig(level=logging.INFO)


def main(page: ft.Page) -> None:
    page.title = "Strand"
    page.bgcolor = "#16171A"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    taps = 0
    label = ft.Text("Strand", size=32, color="#F2EFE9", weight=ft.FontWeight.BOLD)

    def on_tap(_: ft.ControlEvent) -> None:
        nonlocal taps
        taps += 1
        label.value = f"Atingeri: {taps}"
        log.info("button tapped %d times", taps)
        page.update()

    page.add(
        label,
        ft.FilledButton("Apasă-mă", on_click=on_tap, bgcolor="#C9A46A", color="#16171A"),
    )
    log.info("Strand started")


# ft.run exists in newer Flet; ft.app in older ones.
(getattr(ft, "run", None) or ft.app)(main)
