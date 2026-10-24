"""Intake a manually-generated narration MP3 (e.g. Gemini 3.8 Flash TTS - no API key).

The user generates the narration themselves (paste the script into Gemini, download the MP3)
and hands the file over. This script validates it, copies it to src/audio/voice.mp3 and prints
the duration so the film's timing can be built on it.

Usage: python voice-intake.py <film_dir> <mp3>
"""
import os
import shutil
import subprocess
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python voice-intake.py <film_dir> <mp3>")

film, src = sys.argv[1], sys.argv[2]
if not os.path.isfile(src):
    sys.exit(f"no such file: {src}")
if not src.lower().endswith('.mp3'):
    print(f"warning: {src} is not an .mp3 - continuing anyway")

dst_dir = os.path.join(film, 'src', 'audio')
os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, 'voice.mp3')
shutil.copyfile(src, dst)

dur = None
try:
    probe = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', dst],
        capture_output=True, text=True, timeout=30)
    dur = float(probe.stdout.strip())
except Exception:
    pass

if dur:
    print(f"ok: {dst} ({dur:.1f}s)")
else:
    print(f"ok: {dst} (duration unknown - is ffprobe on PATH?)")
print("next: transcribe it for word timings (faster-whisper with word_timestamps, free and local)")
