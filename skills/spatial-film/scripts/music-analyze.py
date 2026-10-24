"""Tempo + loudness shape for each music candidate, numpy only (librosa's numba often breaks on NumPy 2.x).
Decodes with ffmpeg, builds a spectral-flux onset envelope, autocorrelates it for tempo in 80-160 BPM,
then finds the beat phase. Usage: python <skill>/scripts/music-analyze.py ".media/candidates/*.mp3" """
import sys, glob, subprocess
import numpy as np

SR = 22050
HOP = 256

def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)

def onset_env(y):
    n = 1024
    win = np.hanning(n)
    frames = np.lib.stride_tricks.sliding_window_view(y, n)[::HOP] * win
    mag = np.log1p(np.abs(np.fft.rfft(frames, axis=1)) * 10)
    flux = np.maximum(0, np.diff(mag, axis=0)).sum(axis=1)
    flux -= np.convolve(flux, np.ones(16) / 16, mode='same')
    return np.maximum(flux, 0)

def tempo(env):
    fps = SR / HOP
    env = env - env.mean()
    ac = np.correlate(env, env, mode='full')[len(env) - 1:]
    lags = np.arange(len(ac))
    bpm = 60 * fps / np.maximum(lags, 1)
    mask = (bpm >= 80) & (bpm <= 160)
    best = lags[mask][np.argmax(ac[mask])]
    # refine with parabolic interpolation
    a, b, c = ac[best - 1], ac[best], ac[best + 1]
    off = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0
    lag = best + off
    period = lag / fps
    # phase: sum envelope at candidate offsets
    n_off = int(round(lag))
    scores = [env[o::n_off].sum() if o < len(env) else 0 for o in range(n_off)]
    phase = int(np.argmax(scores)) / fps
    return 60 / period, phase

files = []
for a in sys.argv[1:]:
    files += glob.glob(a)
for f in sorted(files):
    y = decode(f)
    env = onset_env(y)
    bpm, phase = tempo(env)
    rms = np.sqrt(np.mean(np.array_split(y ** 2, 8), axis=1)) if False else np.array([np.sqrt(np.mean(s ** 2)) for s in np.array_split(y, 8)])
    shape = ' '.join(f'{v * 100:4.1f}' for v in rms)
    name = f.replace('\\', '/').split('/')[-1]
    print(f'{name:<42} dur {len(y) / SR:5.1f}s  tempo {bpm:6.1f}  first-beat {phase:5.2f}s  loudness(8 parts) {shape}')
