"""Download the MediaPipe files the WebView page needs into src/web/vendor/.

They are not committed (about 15 MB). Run once after cloning, from mobile/:
    uv run python scripts/fetch_web_assets.py
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import tarfile
import urllib.request
from pathlib import Path

TASKS_VISION_VERSION = "0.10.21"
PACKAGE = "@mediapipe/tasks-vision"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)
VENDOR = Path(__file__).resolve().parents[1] / "src" / "web" / "vendor"
USER_AGENT = "strand-dev-setup"


def get(url: str) -> bytes:
    if not url.startswith("https://"):
        raise ValueError(f"refusing non-https URL: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})  # noqa: S310
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
        data: bytes = response.read()
        return data


def resolve_tarball(version: str) -> str:
    meta = json.loads(get(f"https://registry.npmjs.org/{PACKAGE}"))
    if version not in meta["versions"]:
        latest = meta["dist-tags"]["latest"]
        raise SystemExit(
            f"{PACKAGE}@{version} not found; latest is {latest}. Try --version {latest}"
        )
    tarball: str = meta["versions"][version]["dist"]["tarball"]
    return tarball


def save(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()[:16]
    print(f"  {path.relative_to(VENDOR)}  {len(data) / 1e6:.1f} MB  sha256:{digest}…")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=TASKS_VISION_VERSION)
    args = parser.parse_args()

    print(f"{PACKAGE}@{args.version}")
    blob = io.BytesIO(get(resolve_tarball(args.version)))
    with tarfile.open(fileobj=blob, mode="r:gz") as archive:
        for member in archive.getmembers():
            name = member.name.removeprefix("package/")
            wanted = name == "vision_bundle.mjs" or (name.startswith("wasm/") and member.isfile())
            if not wanted or ".." in Path(name).parts:
                continue
            extracted = archive.extractfile(member)
            if extracted is not None:
                save(VENDOR / "tasks-vision" / name, extracted.read())

    print("face_landmarker.task")
    save(VENDOR / "models" / "face_landmarker.task", get(MODEL_URL))
    (VENDOR / "VERSION").write_text(f"{PACKAGE}@{args.version}\n{MODEL_URL}\n")
    print("done")


if __name__ == "__main__":
    main()
