# mobile

Flet (Python) Android app. Arrives in Phase 0.2 (hello world on the Galaxy S24) and Phase 6 (app shell).

Planned layout:

```
mobile/
├── src/
│   ├── main.py
│   ├── views/        # Flet screens
│   ├── viewmodels/   # MVVM, testable without UI
│   ├── analysis/     # validation chain, ONNX adapters, AnalysisService
│   ├── bridge/       # Python <-> WebView (JS) bridge
│   ├── services/     # ApiClient + per-resource clients
│   └── storage/      # TokenStore, local catalog cache
├── web/              # HTML + JS: MediaPipe, three.js, procedural 3D hair
├── assets/models/    # .onnx and .task model files
└── tests/
```

Not part of the uv workspace yet: `flet build` packages the app on its own. How it pulls in
`strand_core` is decided in Phase 0.2.
