"""Show where a seam pair differs, OUTSIDE the presenter zone, so the overlay's own motion doesn't mask a real pop.

usage: <py> seam-diff.py <a.png> <b.png> <out.png> [kape_box x0,y0,x1,y1] [thresh_level]
Prints the % of pixels differing (>8/255 default) with and without the Kape zone, and writes a strip a | b | diff.
"""
import sys
import numpy as np
from PIL import Image

a, b = (np.asarray(Image.open(p).convert("RGB")).astype(np.int16) for p in sys.argv[1:3])
box = [int(v) for v in (sys.argv[4] if len(sys.argv) > 4 else "0,380,660,1080").split(",")]
thresh = int(sys.argv[5]) if len(sys.argv) > 5 else 8
d = np.abs(a - b).max(-1) > thresh
mask = np.ones_like(d)
mask[box[1]:box[3], box[0]:box[2]] = False
outside_pct = float(d[mask].mean() * 100)
print(f"all {d.mean() * 100:.2f}%  outside-kape {outside_pct:.2f}%")
heat = np.zeros_like(a, dtype=np.uint8)
heat[d] = (255, 40, 40)
strip = np.concatenate([a.astype(np.uint8), b.astype(np.uint8), heat], 1)
Image.fromarray(strip).resize((strip.shape[1] // 3, strip.shape[0] // 3)).save(sys.argv[3])
sys.exit(1 if round(outside_pct, 2) > 0.0 else 0)
