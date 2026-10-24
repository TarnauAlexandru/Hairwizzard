// Phase 0.4 + 0.5 spike: MediaPipe Face Landmarker in the WebView, results sent to Python.
// Everything loads from the local server: no CDN, works offline.
import { FaceLandmarker, FilesetResolver } from "./vendor/tasks-vision/vision_bundle.mjs";

const BRIDGE_PREFIX = "STRAND:"; // console messages starting with this are bridge messages
const statusEl = document.getElementById("status");

function show(msg, isError = false) {
  const line = document.createElement("div");
  line.textContent = msg;
  if (isError) line.className = "err";
  statusEl.appendChild(line);
}

// --- the two JS -> Python channels being compared ---------------------------------
function sendConsole(type, data) {
  console.log(BRIDGE_PREFIX + JSON.stringify({ type, sent_ms: Date.now(), data }));
}

async function sendHttp(type, data) {
  const body = JSON.stringify({ type, sent_ms: Date.now(), data });
  const res = await fetch("bridge", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  if (!res.ok) throw new Error(`http bridge ${res.status}`);
}

async function sendBoth(type, data) {
  sendConsole(type, data);
  try {
    await sendHttp(type, data);
  } catch (err) {
    show(`http bridge failed: ${err}`, true);
  }
}

// --- Python -> JS: Python calls this through WebView.run_javascript -----------------
window.strandAck = (info) => show(`Python ack: ${JSON.stringify(info)}`);

// --- face landmarks ---------------------------------------------------------------
const abs = (path) => new URL(path, location.href).href;
const round = (v) => Math.round(v * 1e5) / 1e5;

async function createLandmarker(vision, delegate) {
  return FaceLandmarker.createFromOptions(vision, {
    baseOptions: { modelAssetPath: abs("vendor/models/face_landmarker.task"), delegate },
    runningMode: "IMAGE",
    numFaces: 1,
    outputFacialTransformationMatrixes: true,
  });
}

function draw(points) {
  const img = document.getElementById("face");
  const canvas = document.getElementById("overlay");
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#C9A46A";
  const r = Math.max(1, img.naturalWidth / 400);
  for (const p of points) {
    ctx.beginPath();
    ctx.arc(p.x * canvas.width, p.y * canvas.height, r, 0, 2 * Math.PI);
    ctx.fill();
  }
}

async function detect() {
  const t0 = performance.now();
  const vision = await FilesetResolver.forVisionTasks(abs("vendor/tasks-vision/wasm"));
  let delegate = "GPU";
  let landmarker;
  try {
    landmarker = await createLandmarker(vision, delegate);
  } catch (err) {
    show(`GPU delegate failed (${err}), trying CPU`);
    delegate = "CPU";
    landmarker = await createLandmarker(vision, delegate);
  }
  const initMs = performance.now() - t0;

  const img = document.getElementById("face");
  await img.decode();
  const t1 = performance.now();
  const result = landmarker.detect(img);
  const detectMs = performance.now() - t1;

  const points = result.faceLandmarks[0] ?? [];
  draw(points);
  const matrix = result.facialTransformationMatrixes?.[0]?.data ?? null;
  return {
    landmarks: points.map((p) => [round(p.x), round(p.y), round(p.z)]),
    matrix: matrix ? Array.from(matrix) : null,
    delegate,
    init_ms: Math.round(initMs),
    detect_ms: Math.round(detectMs),
    image: [img.naturalWidth, img.naturalHeight],
  };
}

// ~500 KB of numbers, to measure each channel with a realistic large message.
function bigPayload() {
  const values = Array.from({ length: 27000 }, () => Math.random());
  return { values };
}

async function main() {
  try {
    show("MediaPipe: loading…");
    const face = await detect();
    show(`MediaPipe OK: ${face.landmarks.length} points, delegate ${face.delegate}, ` +
      `init ${face.init_ms} ms, detect ${face.detect_ms} ms`);
    await sendBoth("face_result", face);

    const payload = bigPayload();
    await sendBoth("payload_test", payload);
    show(`payload test sent: ${JSON.stringify(payload).length} bytes per channel`);
  } catch (err) {
    show(`MP FAIL: ${err}`, true);
    await sendBoth("error", { message: String(err), stack: err?.stack ?? null });
  }
}

window.addEventListener("error", (e) => show(`JS error: ${e.message}`, true));
main();
