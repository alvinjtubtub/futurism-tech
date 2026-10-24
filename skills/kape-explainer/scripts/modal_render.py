#!/usr/bin/env python3
"""
Modal.com Serverless GPU Renderer + Stage 8 Word-Sync Proof Verifier for Tech Explanasyon (KAPE Pipeline).

Offloads Phase 7 (1080p60 / 9x16@60 HyperFrames GPU rendering) and Phase 8 (ffprobe + faster-whisper word-sync
proof + midpoint frame pulls) from your MacBook to an on-demand NVIDIA T4 GPU in the cloud.

Cost: ~$0.03 - $0.05 per 2-minute video render (covered by Modal's $30/month free credits -> 600+ videos/month free).

One-Time Setup:
  ~/.kape-explainer/venv/bin/pip install modal   (or pipx install modal)
  modal setup

Direct Usage:
  modal run skills/kape-explainer/scripts/modal_render.py --zip-path films/<slug>/package/<slug>-project.zip --out-dir films/<slug>/renders
"""

import json
import os
import re
import shutil
import statistics as st
import subprocess
import tempfile
import time
import zipfile
from difflib import SequenceMatcher
from pathlib import Path

import modal

app = modal.App("kape-explainer-gpu-renderer")

# Build a cached container image with Node.js 22, FFmpeg, Chromium/Vulkan GPU libs, HyperFrames 0.8.117, and faster-whisper
render_image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install(
        "curl",
        "ca-certificates",
        "gnupg",
        "ffmpeg",
        "unzip",
        "zip",
        "git",
        # Headless Chrome + WebGL / Vulkan / EGL hardware GPU dependencies
        "libnss3",
        "libatk1.0-0",
        "libatk-bridge2.0-0",
        "libcups2",
        "libdrm2",
        "libxkbcommon0",
        "libxcomposite1",
        "libxdamage1",
        "libxfixes3",
        "libxrandr2",
        "libgbm1",
        "libasound2",
        "libpango-1.0-0",
        "libcairo2",
        "libegl1",
        "libgl1",
        "libvulkan1",
        "mesa-vulkan-drivers",
        "vulkan-tools",
        "fonts-liberation",
    )
    .run_commands(
        "curl -fsSL https://deb.nodesource.com/setup_22.x | bash -",
        "apt-get install -y nodejs",
        "npm install -g hyperframes@0.8.117",
        "npx --yes hyperframes@0.8.117 browser ensure",
    )
    .pip_install(
        "faster-whisper",
        "av==12.3.0",
        "numpy",
        "pillow",
        "scipy",
    )
    # Pre-cache the faster-whisper medium model into the image so cold starts never wait on a 1.5GB download
    .run_commands(
        "python3 -c 'from faster_whisper import WhisperModel; WhisperModel(\"medium\", device=\"cpu\", compute_type=\"int8\")'"
    )
)


def _sync_check(source_words_path: Path, render_words_path: Path) -> dict:
    """Exact Stage 8 word-sync proof from skills/kape-explainer/scripts/sync-check.py."""
    def load(p: Path):
        data = json.loads(p.read_text(encoding="utf-8"))
        words = [x for seg in data for x in seg.get("words", [])]
        return [re.sub(r"[^\w]", "", x["w"].lower()) for x in words], [x["s"] for x in words]

    a_tok, a_t = load(source_words_path)
    b_tok, b_t = load(render_words_path)
    diffs = []
    for blk in SequenceMatcher(None, a_tok, b_tok, autojunk=False).get_matching_blocks():
        diffs += [b_t[blk.b + i] - a_t[blk.a + i] for i in range(blk.size)]

    matched = len(diffs)
    total = len(a_tok)
    ratio = (matched / total) if total > 0 else 0.0
    median = st.median(diffs) if diffs else 999.0
    mean = st.mean(diffs) if diffs else 999.0
    p95 = sorted(abs(x) for x in diffs)[int(len(diffs) * 0.95)] if diffs else 999.0
    max_off = max(abs(x) for x in diffs) if diffs else 999.0
    raw = (
        f"matched {matched}/{total} words  offset median {median:+.3f}s  "
        f"mean {mean:+.3f}s  p95 |off| {p95:.3f}s  max |off| {max_off:.3f}s"
    )
    passed = abs(median) <= 0.03 and ratio >= 0.90
    return {
        "matched": matched,
        "total": total,
        "match_ratio": round(ratio * 100, 1),
        "median_offset_s": round(median, 3),
        "mean_offset_s": round(mean, 3),
        "p95_offset_s": round(p95, 3),
        "max_offset_s": round(max_off, 3),
        "raw": raw,
        "passed": passed,
    }


@app.function(
    image=render_image,
    gpu="T4",
    cpu=8.0,
    memory=16384,
    timeout=1800,
)
def render_and_verify_remote(
    project_zip_bytes: bytes,
    lang: str = "tl",
    prompt: str = "",
    workers: int = 6,
) -> dict:
    """Unzips the packaged film on a cloud T4 GPU, renders at 60fps, and runs the Stage 8 word-sync proof."""
    from faster_whisper import WhisperModel

    work_dir = Path(tempfile.mkdtemp(prefix="kape-cloud-render-"))
    zip_file = work_dir / "project.zip"
    zip_file.write_bytes(project_zip_bytes)

    project_dir = work_dir / "film"
    project_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_file, "r") as zf:
        zf.extractall(project_dir)

    film_json_path = project_dir / "film.json"
    if not film_json_path.exists():
        raise RuntimeError("film.json not found in uploaded project ZIP")

    film = json.loads(film_json_path.read_text(encoding="utf-8"))
    slug = film.get("name", "film")
    fps = film.get("fps", 60)
    hf_ver = film.get("hyperframes", "0.8.117")
    want_w = film.get("width", 1920)
    want_h = film.get("height", 1080)

    renders_dir = project_dir / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)
    out_name = f"{slug}-1080p60"
    mp4_path = renders_dir / f"{out_name}.mp4"
    log_path = renders_dir / f"{out_name}.log"

    # 1. Run HyperFrames 60fps GPU Render
    t0 = time.time()
    render_cmd = [
        "npx",
        "--prefer-offline",
        "--yes",
        f"hyperframes@{hf_ver}",
        "render",
        "--fps",
        str(fps),
        "--browser-gpu",
        "--workers",
        str(workers),
        "-o",
        str(mp4_path),
    ]
    with open(log_path, "w", encoding="utf-8") as lf:
        res = subprocess.run(render_cmd, cwd=str(project_dir), stdout=lf, stderr=subprocess.STDOUT)

    render_elapsed = round(time.time() - t0, 1)
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    gpu_match = re.search(r'"browserGpuMode":"([a-z]*)"', log_text)
    gpu_mode = gpu_match.group(1) if gpu_match else "unknown"

    if res.returncode != 0 or not mp4_path.exists():
        raise RuntimeError(
            f"HyperFrames render failed (exit {res.returncode}) after {render_elapsed}s.\n"
            f"Log tail:\n{log_text[-3000:]}"
        )

    # 2. Stage 8 Verification: ffprobe check
    beat = 60.0 / (film.get("bpm") or 60.0)
    bar = beat * (film.get("beats_per_bar") or 1.0)
    expected_total = round(sum(s[1] * bar for s in film.get("scenes", [])), 3)

    probe_res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(mp4_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    probe_data = json.loads(probe_res.stdout or "{}")
    streams = probe_data.get("streams", [])
    v_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
    dur = float(probe_data.get("format", {}).get("duration") or v_stream.get("duration") or 0.0)
    want_fps = f"{fps}/1"

    ffprobe_passed = (
        v_stream.get("codec_name") == "h264"
        and v_stream.get("width") == want_w
        and v_stream.get("height") == want_h
        and (v_stream.get("r_frame_rate") == want_fps or v_stream.get("avg_frame_rate") == want_fps)
        and a_stream.get("codec_name") == "aac"
        and abs(dur - expected_total) <= 0.25
    )

    ffprobe_report = {
        "video_codec": v_stream.get("codec_name"),
        "width": v_stream.get("width"),
        "height": v_stream.get("height"),
        "r_frame_rate": v_stream.get("r_frame_rate"),
        "audio_codec": a_stream.get("codec_name"),
        "duration": dur,
        "expected_duration": expected_total,
        "gpu_mode": gpu_mode,
        "render_seconds": render_elapsed,
        "passed": ffprobe_passed,
    }

    # 3. Stage 8 Verification: faster-whisper Word-Sync Proof
    source_words = project_dir / "src" / "timing" / "vo-words.json"
    word_sync_report = {"passed": False, "detail": "src/timing/vo-words.json not found"}
    if source_words.exists():
        wav_tmp = work_dir / "render-audio.wav"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(mp4_path), "-vn", "-ac", "1", "-ar", "16000", str(wav_tmp)],
            check=True,
        )
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        segs, _ = model.transcribe(
            str(wav_tmp),
            language=lang,
            word_timestamps=True,
            condition_on_previous_text=False,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 300},
            initial_prompt=prompt or None,
        )
        rows = [
            {
                "s": round(s.start, 2),
                "e": round(s.end, 2),
                "text": s.text.strip(),
                "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or [])],
            }
            for s in segs
        ]
        render_words = work_dir / "render-vo-words.json"
        render_words.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        word_sync_report = _sync_check(source_words, render_words)

    # 4. Stage 8 Verification: Midpoint Frame Pulls per Scene
    frames_bytes = {}
    frame_pulls = []
    cursor = 0.0
    for sid, bars in film.get("scenes", []):
        dur_s = bars * bar
        mid = round(cursor + dur_s / 2.0, 3)
        fname = f"{sid}-at-{mid}s.png"
        out_png = renders_dir / fname
        ff_res = subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-ss", str(mid), "-i", str(mp4_path), "-frames:v", "1", str(out_png)],
            cwd=str(project_dir),
        )
        if ff_res.returncode == 0 and out_png.exists():
            frames_bytes[fname] = out_png.read_bytes()
            frame_pulls.append({"scene": sid, "time_s": mid, "file": f"renders/verify-frames/{fname}"})
        cursor += dur_s

    proof = {
        "film": slug,
        "mp4": f"renders/{out_name}.mp4",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rendered_on": "Modal Serverless GPU (T4)",
        "ffprobe": ffprobe_report,
        "word_sync": word_sync_report,
        "frame_pulls": frame_pulls,
        "passed": bool(ffprobe_passed and word_sync_report.get("passed")),
    }

    return {
        "slug": slug,
        "mp4_name": f"{out_name}.mp4",
        "mp4_bytes": mp4_path.read_bytes(),
        "log_name": f"{out_name}.log",
        "log_text": log_text,
        "proof": proof,
        "verify_frames": frames_bytes,
    }


@app.local_entrypoint()
def main(
    zip_path: str,
    out_dir: str = "",
    lang: str = "tl",
    prompt: str = "",
    workers: int = 6,
):
    zp = Path(zip_path).resolve()
    if not zp.exists():
        raise SystemExit(f"Project ZIP not found: {zp}")

    film_root = zp.parent.parent if zp.parent.name == "package" else zp.parent
    renders_out = Path(out_dir).resolve() if out_dir else (film_root / "renders")
    renders_out.mkdir(parents=True, exist_ok=True)

    print(f"=== Uploading {zp.name} ({zp.stat().st_size / 1e6:.1f} MB) to Modal Serverless GPU ===")
    t0 = time.time()
    result = render_and_verify_remote.remote(
        zp.read_bytes(),
        lang=lang,
        prompt=prompt,
        workers=workers,
    )

    mp4_dest = renders_out / result["mp4_name"]
    log_dest = renders_out / result["log_name"]
    mp4_dest.write_bytes(result["mp4_bytes"])
    log_dest.write_text(result["log_text"], encoding="utf-8")

    # Save midpoint verification frames
    vf_dir = renders_out / "verify-frames"
    if vf_dir.exists():
        shutil.rmtree(vf_dir)
    vf_dir.mkdir(parents=True, exist_ok=True)
    for fname, fbytes in result.get("verify_frames", {}).items():
        (vf_dir / fname).write_bytes(fbytes)

    # Save Stage 8 render-proof.json
    proof = result["proof"]
    hf_dir = film_root / ".hyperframes"
    hf_dir.mkdir(parents=True, exist_ok=True)
    proof_path = hf_dir / "render-proof.json"
    proof_path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")

    # Also copy into package/ if it exists so the upload pack is 100% self-contained
    pkg_dir = film_root / "package"
    if pkg_dir.exists():
        shutil.copy2(mp4_dest, pkg_dir / result["mp4_name"])
        shutil.copy2(proof_path, pkg_dir / "render-proof.json")

    total_s = round(time.time() - t0, 1)
    ff = proof["ffprobe"]
    ws = proof["word_sync"]
    print(f"\n=== Modal Cloud GPU Render Complete in {total_s}s (GPU mode: {ff.get('gpu_mode')}) ===")
    print(f"MP4      : {mp4_dest} ({mp4_dest.stat().st_size / 1e6:.1f} MB)")
    print(f"ffprobe  : {'PASS' if ff.get('passed') else 'FAIL'} ({ff.get('video_codec')} {ff.get('width')}x{ff.get('height')} @ {ff.get('r_frame_rate')}, dur {ff.get('duration', 0):.2f}s)")
    print(f"word-sync: {'PASS' if ws.get('passed') else 'FAIL'} ({ws.get('raw', ws.get('detail', ''))})")
    print(f"proof    : {proof_path}")
    if not proof.get("passed"):
        raise SystemExit("Stage 8 Verification failed on cloud render — inspect render-proof.json")
