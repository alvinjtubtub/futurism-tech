"""Per-bar loudness + brightness for one track at a known tempo, to pick a 60s window that aligns
section changes with the film's scene seams. Usage: python <skill>/scripts/music-bars.py <file> <bpm> <first_beat_s>"""
import sys, subprocess
import numpy as np

SR = 22050
f, bpm, first = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
y = np.frombuffer(raw, dtype=np.float32)
bar = 4 * 60 / bpm
t = first
i = 0
while t + bar <= len(y) / SR:
    seg = y[int(t * SR):int((t + bar) * SR)]
    rms = np.sqrt(np.mean(seg ** 2)) * 100
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    freqs = np.fft.rfftfreq(len(seg), 1 / SR)
    cent = float((spec * freqs).sum() / spec.sum())
    low = float(spec[freqs < 150].sum() / spec.sum()) * 100
    print(f'bar {i:3d}  t {t:6.2f}s  rms {rms:5.1f}  {"#" * int(rms)}  centroid {cent:6.0f}Hz  bass {low:4.1f}%')
    t += bar
    i += 1
