"""Fit the sheet's BLINK eye band onto each body pose, so a blink can be an overlay.

usage: <py> <engine>/scripts/blink-fit.py <mascot_dir>
Matches the NEUTRAL face's eye band (glasses + eyes) against each pose at many scales with normalized
cross-correlation, then writes poses/<name>-blink.png (the pose with the BLINK eye band composited in) for every
pose whose match score clears the bar, plus _blink-review.png. A pose that does not fit gets no blink.
Needs torch (optional). Without torch, or without faces/neutral.png + faces/blink.png, it writes
blink-fit.json with every pose blink=false and exits 0.
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image

D = Path(sys.argv[1])


def no_blink(why):
    print(f"blink-fit skipped: {why}. Writing blink-fit.json with blink=false for every pose.")
    res = {p.stem: {"score": 0, "scale": 1, "x": 0, "y": 0, "blink": False}
           for p in sorted((D / "poses").glob("*.png")) if not p.stem.endswith("-blink")}
    (D / "blink-fit.json").write_text(json.dumps(res, indent=1))
    sys.exit(0)


try:
    import torch, torch.nn.functional as F
except ImportError:
    no_blink("torch is not installed (pip install torch; optional, blinks are a nicety)")
if not ((D / "faces/neutral.png").exists() and (D / "faces/blink.png").exists()):
    no_blink("faces/neutral.png + faces/blink.png are not both present")
neutral = Image.open(D / "faces/neutral.png").convert("RGBA")
blink = Image.open(D / "faces/blink.png").convert("RGBA")
# both busts share framing; size blink to neutral
blink = blink.resize(neutral.size, Image.LANCZOS)
W, H = neutral.size
band = (int(W * 0.08), int(H * 0.40), int(W * 0.94), int(H * 0.66))  # glasses + eyes


def gray(im):
    a = np.asarray(im.convert("RGBA")).astype(np.float32) / 255
    g = a[..., :3].mean(-1) * a[..., 3] + (1 - a[..., 3])  # composite on white
    return g


tmpl_full = gray(neutral.crop(band))
DS = 4  # search at 1/4 scale
results = {}
for p in sorted((D / "poses").glob("*.png")):
    if p.stem.endswith("-blink"):
        continue
    pose = Image.open(p).convert("RGBA")
    pg = gray(pose.resize((pose.width // DS, pose.height // DS), Image.LANCZOS))
    pg = pg[: int(pg.shape[0] * 0.45)]  # the eyes are in the head; never search the body
    img = torch.from_numpy(pg)[None, None]
    best = (-1, None)
    for s in np.arange(0.70, 1.30, 0.01):
        tw, th = int(tmpl_full.shape[1] * s / DS), int(tmpl_full.shape[0] * s / DS)
        if tw < 8 or th < 4 or tw >= pg.shape[1] or th >= pg.shape[0]:
            continue
        t = np.asarray(Image.fromarray((tmpl_full * 255).astype(np.uint8)).resize((tw, th), Image.LANCZOS)) / 255.0
        t = torch.from_numpy(t.astype(np.float32))[None, None]
        t = t - t.mean()
        tn = t.pow(2).sum().sqrt()
        num = F.conv2d(img, t)
        ones = torch.ones_like(t)
        mu = F.conv2d(img, ones) / ones.numel()
        var = F.conv2d(img * img, ones) - ones.numel() * mu * mu
        ncc = num / (tn * var.clamp_min(1e-6).sqrt())
        ncc[var < 0.25 * tn * tn] = -1  # flat windows (ground, shirt) make NCC blow up - skip them
        v, idx = ncc.flatten().max(0)
        if v.item() > best[0]:
            y, x = divmod(idx.item(), ncc.shape[-1])
            best = (v.item(), (s, x * DS, y * DS))
    score, (s, x, y) = best
    results[p.stem] = {"score": round(score, 3), "scale": round(float(s), 3), "x": int(x), "y": int(y)}
    print(f"{p.stem:<10} score {score:.3f} scale {s:.2f} at {x},{y}")

GOOD = 0.70
tiles = []
for name, r in results.items():
    pose = Image.open(D / f"poses/{name}.png").convert("RGBA")
    if r["score"] < GOOD:
        r["blink"] = False
        continue
    s = r["scale"]
    eb = blink.crop(band)
    eb = eb.resize((int(eb.width * s), int(eb.height * s)), Image.LANCZOS)
    # feather the band edges so only the eyes change
    m = np.ones((eb.height, eb.width), np.float32)
    f = max(2, int(min(eb.size) * 0.12))
    ramp = np.linspace(0, 1, f)
    m[:f] *= ramp[:, None]; m[-f:] *= ramp[::-1, None]; m[:, :f] *= ramp[None]; m[:, -f:] *= ramp[None, ::-1]
    a = np.asarray(eb).astype(np.float32)
    a[..., 3] *= m
    eb = Image.fromarray(a.astype(np.uint8), "RGBA")
    out = pose.copy()
    out.alpha_composite(eb, (r["x"], r["y"]))
    # never paint outside the pose silhouette
    o = np.asarray(out).copy()
    o[..., 3] = np.minimum(o[..., 3], np.asarray(pose)[..., 3])
    Image.fromarray(o, "RGBA").save(D / f"poses/{name}-blink.png", optimize=True)
    r["blink"] = True
    for im in (pose, Image.fromarray(o, "RGBA")):
        hc = im.crop((0, 0, im.width, int(im.height * 0.45)))
        hc.thumbnail((300, 260))
        t = Image.new("RGB", (310, 270), (20, 26, 40))
        t.paste(hc, (5, 5), hc)
        tiles.append(t)
(D / "blink-fit.json").write_text(json.dumps(results, indent=1))
if tiles:
    cols = 6
    rows = (len(tiles) + cols - 1) // cols
    cs = Image.new("RGB", (cols * 310, rows * 270), (90, 90, 90))
    for i, t in enumerate(tiles):
        cs.paste(t, ((i % cols) * 310, (i // cols) * 270))
    cs.save(D / "_blink-review.png")
print("blink poses:", [k for k, v in results.items() if v.get("blink")])
