# ml

Training code. Nothing in here ships inside the app except the exported `.onnx` files.

```
ml/
├── face_shape/     # landmarks -> proportions -> scikit-learn classifier (Phase 8.2)
├── hair_texture/   # MobileNetV3 transfer learning in PyTorch (Phase 8.3)
└── export/         # ONNX export + output parity checks (Phase 0.3, 8.x)
```

Datasets are never committed. Each dataset gets a data card in `docs/` with its source and license.
