"""Phase 0.3 spike: run an ONNX model with onnxruntime inside the Flet app."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

MODEL_NAME = "spike_classifier.onnx"


def find_model() -> Path:
    """The model ships in src/assets/models. Check every place Flet may have put it."""
    candidates = [Path(__file__).resolve().parent / "assets" / "models" / MODEL_NAME]
    assets_dir = os.getenv("FLET_ASSETS_DIR")
    if assets_dir:
        candidates.append(Path(assets_dir) / "models" / MODEL_NAME)
    for path in candidates:
        if path.is_file():
            return path
    tried = ", ".join(str(p) for p in candidates)
    raise FileNotFoundError(f"{MODEL_NAME} not found; tried: {tried}")


@dataclass(frozen=True)
class Prediction:
    label: int
    probability: float
    ms: float


class OnnxSpike:
    """Loads the model once, then answers predictions and times each one."""

    def __init__(self, path: Path | None = None) -> None:
        import onnxruntime as ort  # imported here so a packaging failure shows up as an error

        self.path = path or find_model()
        start = time.perf_counter()
        self._session = ort.InferenceSession(str(self.path), providers=["CPUExecutionProvider"])
        self.load_ms = (time.perf_counter() - start) * 1000
        self._input = self._session.get_inputs()[0].name
        self.ort_version = ort.__version__

    def predict(self, features: np.ndarray) -> Prediction:
        row = np.asarray(features, dtype=np.float32).reshape(1, -1)
        start = time.perf_counter()
        labels, probabilities = self._session.run(["label", "probabilities"], {self._input: row})
        ms = (time.perf_counter() - start) * 1000
        label = int(labels[0])
        return Prediction(label=label, probability=float(probabilities[0][label]), ms=ms)
