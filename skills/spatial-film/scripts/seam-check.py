"""Proves every seam and the loop by pixels. Snapshots the assembled film one frame either side of each scene
boundary (both sides hold the shared seam frame, so the pair must match) plus frame 0 vs the last frame.
Run from the project root after assemble.py:  python <skill>/scripts/seam-check.py [--tol 0.5]
PASS = under --tol percent of pixels differ by more than 12 levels. Whip-pan or held-motion seams may need a
look by eye - the PNGs stay in snapshots/seams/."""
import glob, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from film import ROOT, load, hf
from PIL import Image, ImageChops

tol = float(sys.argv[sys.argv.index('--tol') + 1]) if '--tol' in sys.argv else 0.5
f = load()
fr = 1 / f['fps']
pairs = []  # (label, time a, time b)
sl = f['scene_list']
for a, b in zip(sl, sl[1:]):
    pairs.append((f'{a["id"]} -> {b["id"]}', round(b['start'] - fr, 4), round(b['start'] + fr, 4)))
pairs.append((f'loop {sl[-1]["id"]} -> {sl[0]["id"]}', round(f['total'] - fr, 4), 0.0))
times = [t for _, x, y in pairs for t in (x, y)]
out = os.path.join(ROOT, 'snapshots', 'seams')
shutil.rmtree(out, ignore_errors=True)
# argument list, never a command string; npx is a .cmd shim on Windows, so only there it needs a shell
r = subprocess.run(['npx', '--prefer-offline', '--yes', hf(f), 'snapshot', '--at', ','.join(map(str, times)), '--no-end',
                    '--describe', 'false', '-o', out], shell=os.name == 'nt', capture_output=True, text=True, cwd=ROOT)
shots = sorted(glob.glob(os.path.join(out, 'frame-*.png')), key=lambda p: int(os.path.basename(p).split('-')[1]))
if len(shots) != len(times):
    sys.exit(f'expected {len(times)} snapshots, got {len(shots)}\n{r.stdout[-800:]}{r.stderr[-800:]}')
bad = 0
for i, (label, ta, tb) in enumerate(pairs):
    a = Image.open(shots[2 * i]).convert('RGB')
    b = Image.open(shots[2 * i + 1]).convert('RGB')
    diff = ImageChops.difference(a, b).convert('L').point(lambda v: 255 if v > 12 else 0)
    pct = 100 * diff.histogram()[255] / (a.width * a.height)
    ok = pct <= tol
    bad += not ok
    print(f'{"PASS" if ok else "FAIL"}  {label:<34} {ta:>8.4f} vs {tb:<8.4f} {pct:6.2f}% differ')
print(f'{len(pairs) - bad}/{len(pairs)} seams match - frames in snapshots/seams/')
sys.exit(1 if bad else 0)
