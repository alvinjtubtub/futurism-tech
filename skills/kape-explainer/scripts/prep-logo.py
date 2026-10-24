"""Prepare a brand logo for films: trim the transparent border, upscale to >= 360px tall, save logo.png (or copy an SVG).

usage: <py> prep-logo.py <in.png|svg> <out_dir>
PNG: trims fully transparent edges, upscales with LANCZOS on premultiplied alpha (clean edges, no halos), writes
<out_dir>/logo.png. SVG: copied as <out_dir>/logo.svg. Warns when a PNG has no transparency (a white box on the film).
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

MIN_H = 360

if len(sys.argv) < 3:
    sys.exit(__doc__)
src, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)

if src.suffix.lower() == ".svg":
    shutil.copyfile(src, out_dir / "logo.svg")
    print(out_dir / "logo.svg", "(svg copied)")
    sys.exit(0)

im = Image.open(src).convert("RGBA")
a = np.asarray(im).astype(np.float32)
alpha = a[..., 3:] / 255
if alpha.min() > 0.99:
    print("WARNING: this PNG has no transparency - it will show as a solid box on the film. Use a transparent PNG or an SVG.")
box = im.getchannel("A").getbbox()
if box:
    im = im.crop(box)
    a = np.asarray(im).astype(np.float32)
    alpha = a[..., 3:] / 255
if im.height < MIN_H:
    k = -(-MIN_H // im.height)  # ceil
    pre = np.dstack([a[..., :3] * alpha, a[..., 3:]]).round().clip(0, 255).astype(np.uint8)
    pre = Image.fromarray(pre, "RGBA").resize((im.width * k, im.height * k), Image.LANCZOS)
    p = np.asarray(pre).astype(np.float32)
    pa = p[..., 3:] / 255
    col = np.where(pa > 0, p[..., :3] / np.maximum(pa, 1e-3), 0)
    im = Image.fromarray(np.dstack([col, p[..., 3:]]).round().clip(0, 255).astype(np.uint8), "RGBA")
im.save(out_dir / "logo.png", optimize=True)
print(out_dir / "logo.png", im.size)
