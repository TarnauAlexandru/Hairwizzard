"""Phase 0.3 spike: train a tiny classifier on synthetic data and export it to ONNX.

The model has no real meaning. It only proves that an ONNX file made on the laptop
runs with onnxruntime inside the Flet app on Android.

Run from ml/:  uv run python -m export.train_spike_model
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

N_FEATURES = 4
SEED = 42
DEFAULT_OUT = (
    Path(__file__).resolve().parents[2]
    / "mobile"
    / "src"
    / "assets"
    / "models"
    / "spike_classifier.onnx"
)


def train(seed: int = SEED) -> tuple[LogisticRegression, np.ndarray]:
    """Train on synthetic data. Returns the model and a few rows to test parity with."""
    x, y = make_classification(
        n_samples=500, n_features=N_FEATURES, n_informative=3, n_redundant=1, random_state=seed
    )
    x = x.astype(np.float32)
    model = LogisticRegression(max_iter=1000).fit(x, y)
    return model, x[:20]


def export(model: LogisticRegression, out: Path) -> Path:
    """Convert to ONNX with plain tensor outputs: `label` (int64) and `probabilities` (float32)."""
    onnx_model = convert_sklearn(
        model,
        initial_types=[("input", FloatTensorType([None, N_FEATURES]))],
        options={id(model): {"zipmap": False}},
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(onnx_model.SerializeToString())
    return out


def main() -> None:
    model, _ = train()
    path = export(model, DEFAULT_OUT)
    print(f"exported {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
