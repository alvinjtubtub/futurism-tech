"""Word-level transcript of a narration (or any recording) with faster-whisper, CPU int8.

usage: <py> <skill>/scripts/transcribe.py <audio-or-video> <out_dir> [--lang en] [--model medium] [--prompt "names, jargon"]
Writes <out_dir>/vo-words.json ([{s, e, text, words:[{w, s, e}]}]) and <out_dir>/vo-transcript.txt.
--lang is a Whisper language code (en, tl, es...; "tl" also handles Taglish). --prompt seeds spelling of names/jargon.
~1.3x realtime for 'medium' on 12 CPU cores; 82s of narration takes ~2 min.
"""
import argparse, json, subprocess, tempfile, time
from pathlib import Path
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--lang", default="en"); ap.add_argument("--model", default="medium")
ap.add_argument("--prompt", default="")
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
wav = Path(tempfile.gettempdir()) / f"kx-{Path(a.src).stem}.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)

model = WhisperModel(a.model, device="cpu", compute_type="int8")
t0 = time.time()
segs, info = model.transcribe(str(wav), language=a.lang, word_timestamps=True, condition_on_previous_text=False,
                              vad_filter=True, vad_parameters={"min_silence_duration_ms": 300},
                              initial_prompt=a.prompt or None)
rows = []
with open(out / "vo-transcript.txt", "w", encoding="utf-8") as f:
    for s in segs:
        rows.append({"s": round(s.start, 2), "e": round(s.end, 2), "text": s.text.strip(),
                     "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or [])]})
        f.write(f"[{s.start:7.2f}] {s.text.strip()}\n")
(out / "vo-words.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
print(f"{len(rows)} segments in {time.time() - t0:.0f}s -> {out / 'vo-words.json'}")
