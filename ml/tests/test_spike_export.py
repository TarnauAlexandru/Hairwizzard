"""The ONNX model must give the same answers as the scikit-learn model it came from."""

from pathlib import Path

import numpy as np
import onnxruntime as ort
from export.train_spike_model import export, train


def test_onnx_matches_sklearn(tmp_path: Path) -> None:
    model, rows = train()
    path = export(model, tmp_path / "spike.onnx")

    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    labels, probabilities = session.run(["label", "probabilities"], {"input": rows})

    np.testing.assert_array_equal(labels, model.predict(rows))
    np.testing.assert_allclose(probabilities, model.predict_proba(rows), atol=1e-5)
