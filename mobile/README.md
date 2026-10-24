# mobile

Flet (Python) Android app. Phase 0.2 is a hello world (one screen, one button); Phase 6 builds the real app shell.

## Run on your laptop (fastest feedback)

```powershell
cd mobile
uv sync
uv run flet run src/main.py
```

## WebView assets (one time, after cloning)

```powershell
cd mobile
uv run python scripts/fetch_web_assets.py     # MediaPipe JS + WASM + face model -> src/web/vendor/
copy C:\path\to\your\photo.jpg src\web\test_face.jpg   # a front-facing photo of you; never committed
```

The WebView runs only on Android, iOS and macOS. On Windows the app shows a button that opens
the same page in your browser instead (MediaPipe and the HTTP channel work there).

## Tests

```powershell
uv run pytest
```

## Build the APK and install on a phone over USB

```powershell
cd mobile
uv run flet build apk
adb install -r build\apk\app-release.apk
adb logcat -s flutter python
```

The APK path may differ slightly by Flet version: look in `mobile/build/apk/`.
Build output is git-ignored. The full walkthrough is step 0.2 in the project guide.

## Planned layout

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

Not part of the uv workspace: `flet build` packages the app on its own. How it pulls in
`strand_core` is decided in a later phase.
