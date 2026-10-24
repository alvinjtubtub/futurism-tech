"""Normalise a custom mascot folder so build-presenter.py can use it.

usage: <py> <skill>/scripts/prep-mascot.py <mascot_dir>
<mascot_dir>/poses/<name>.png  transparent PNGs, one pose per file. Required: idle, point.
                               Recommended: wave, present, think, thumbs-up, celebrate.
<mascot_dir>/faces/neutral.png + faces/blink.png  optional, same head with eyes open / closed (enables blinks)
<mascot_dir>/fx/*.png          optional effect sprites (kept as they are; none = the demo's are copied in)
Each pose is trimmed to its alpha bbox and scaled with LANCZOS (premultiplied) by ONE factor so the idle pose is
1100px tall; every other pose uses the same factor, so the character keeps one consistent size. Originals are
backed up to <mascot_dir>/originals/ on the first run and re-read from there on later runs (never scaled twice).
Writes manifest.json, then runs blink-fit (../../spatial-film/scripts/blink-fit.py) when both faces exist, else
writes blink-fit.json with every pose blink=false. Needs numpy + Pillow; blink-fit also needs torch (optional).
"""
import sys, json, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image

BODY_H = 1100
HOWTO = "Export each pose as a transparent PNG (e.g. remove.bg or Photoshop), then run this again."

if len(sys.argv) < 2:
    sys.exit(__doc__)
D = Path(sys.argv[1])
P = D / "poses"
if not P.is_dir():
    sys.exit(f"error: {P} not found. {HOWTO}")

# first run: back up the originals; later runs read from the backup so scaling never compounds
O = D / "originals"
if not O.exists():
    O.mkdir()
    for f in P.glob("*.png"):
        if not f.stem.endswith("-blink"):
            shutil.copy2(f, O / f.name)
src = {f.stem: f for f in sorted(O.glob("*.png"))}
for need in ("idle", "point"):
    if need not in src:
        sys.exit(f"error: poses/{need}.png is required. {HOWTO}")


def load(name):
    im = Image.open(src[name])
    if im.mode != "RGBA":
        sys.exit(f"error: poses/{name}.png is {im.mode}, not RGBA (no transparency). {HOWTO}")
    a = np.asarray(im)[..., 3]
    clear = (a < 10).mean()
    if clear < 0.05 or a.max() < 200:
        sys.exit(f"error: poses/{name}.png has no real transparency ({clear:.0%} clear pixels). {HOWTO}")
    ys, xs = np.nonzero(a > 8)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


trimmed = {n: load(n) for n in src}
k = BODY_H / trimmed["idle"].height  # one factor for every pose
manifest, rows = {}, []
for name, im in trimmed.items():
    w, h = max(1, round(im.width * k)), max(1, round(im.height * k))
    out = im.convert("RGBa").resize((w, h), Image.LANCZOS).convert("RGBA")
    out.save(P / f"{name}.png", optimize=True)
    manifest[f"poses/{name}"] = {"w": w, "h": h, "sheet_box": None}
    rows.append((f"poses/{name}", im.width, im.height, w, h))
for p in P.glob("*-blink.png"):  # stale variants belong to the old pixels; blink-fit rebuilds them
    p.unlink()
demo_fx = Path(__file__).resolve().parent.parent / "assets" / "mascot" / "fx"
if not (D / "fx").is_dir() and demo_fx.is_dir():  # no own effects: borrow the demo's (question mark, sparkle...)
    shutil.copytree(demo_fx, D / "fx")
    print("no fx/: copied the demo effect sprites")
for group in ("faces", "fx"):
    for f in sorted((D / group).glob("*.png")) if (D / group).is_dir() else []:
        w, h = Image.open(f).size
        manifest[f"{group}/{f.stem}"] = {"w": w, "h": h, "sheet_box": None}
(D / "manifest.json").write_text(json.dumps(manifest, indent=1))

engine = Path(__file__).resolve().parent.parent.parent / "spatial-film" / "scripts" / "blink-fit.py"
has_faces = (D / "faces/neutral.png").exists() and (D / "faces/blink.png").exists()
if has_faces and engine.exists():
    subprocess.run([sys.executable, str(engine), str(D)], check=True)
else:
    res = {n: {"score": 0, "scale": 1, "x": 0, "y": 0, "blink": False} for n in src}
    (D / "blink-fit.json").write_text(json.dumps(res, indent=1))
    print("no faces/neutral.png + faces/blink.png: blinks off (blink-fit.json written, every pose blink=false)")

fit = json.loads((D / "blink-fit.json").read_text())
print(f"\n{'pose':<18}{'trimmed':>12}{'final':>12}  blink")
for key, tw, th, w, h in rows:
    print(f"{key:<18}{f'{tw}x{th}':>12}{f'{w}x{h}':>12}  {bool(fit.get(key.split('/')[1], {}).get('blink'))}")
print(f"\nscale factor {k:.3f} (idle -> {BODY_H}px). manifest.json + blink-fit.json written in {D}")
missing = [n for n in ("wave", "present", "think", "thumbs-up", "celebrate") if n not in src]
if missing:
    print("recommended poses not found (presenter-track.json may only use poses that exist): " + ", ".join(missing))
