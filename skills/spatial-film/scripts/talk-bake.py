"""Bake <pose>-talk.png and <pose>-talkblink.png for poses that cleared blink-fit.

Mirrors blink-fit's compositing: the eye band (face x 8-94%, y 40-66%) matched at pose (x, y)
with scale s defines the face->pose map:  pose_pt = (x, y) + (face_pt - band_origin) * s.
The mouth patch is a TIGHT measured box around the mouth (dark/tongue/teeth cluster detection),
cut from talk.png / talkblink.png through the same map, feathered 3px, alpha-clamped to the
pose silhouette (same guard as blink-fit).
"""
import json
import numpy as np
from PIL import Image
from pathlib import Path
from scipy import ndimage

import sys
M = Path(sys.argv[1]) if len(sys.argv) > 1 else (Path(__file__).resolve().parents[3] / 'profile/mascot')
WORK = M / 'work'
WORK.mkdir(exist_ok=True)
fit = json.loads((M / 'blink-fit.json').read_text())
neutral = Image.open(M / 'faces/neutral.png').convert('RGBA')
talk = Image.open(M / 'faces/talk.png').convert('RGBA')
talkblink = Image.open(M / 'faces/talkblink.png').convert('RGBA')
W, H = neutral.size
BAND = (int(W * 0.08), int(H * 0.40), int(W * 0.94), int(H * 0.66))

def mouth_mask(img):
    a = np.asarray(img.convert('RGBA')).astype(np.int32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    mx = a[..., :3].max(-1); sat = mx - a[..., :3].min(-1)
    dark = (mx < 115) & (a[..., 3] > 128)
    tongue = (R > 140) & (R - B > 70) & (G < 160) & (a[..., 3] > 128)
    white = (mx > 225) & (sat < 32) & (a[..., 3] > 128)
    return dark | tongue | white

def find_mouth(img, zone, centre_test):
    """Union bbox of mouth-coloured clusters inside zone whose centre passes centre_test(cx, cy)."""
    zx0, zy0, zx1, zy1 = zone
    sub = mouth_mask(img)[zy0:zy1, zx0:zx1]
    lab, n = ndimage.label(sub)
    boxes = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < 200: continue
        if xs.min() == 0 or ys.min() == 0 or xs.max() == sub.shape[1] - 1 or ys.max() == sub.shape[0] - 1:
            continue  # border-connected mass (jacket/hair), not a mouth
        cx, cy = (xs.min() + xs.max()) / 2 + zx0, (ys.min() + ys.max()) / 2 + zy0
        if centre_test(cx, cy):
            boxes.append((xs.min() + zx0, ys.min() + zy0, xs.max() + zx0 + 1, ys.max() + zy0 + 1))
    if not boxes: return None
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))

# sheet mouths (face px), zone = lower face
fzone = (int(W * 0.22), int(H * 0.60), int(W * 0.80), int(H * 0.95))
ftest = lambda cx, cy: 0.35 * W < cx < 0.70 * W and 0.68 * H < cy < 0.86 * H
sheet_talk = find_mouth(talk, fzone, ftest)
sheet_tb = find_mouth(talkblink, fzone, ftest)
print(f'sheet talk mouth {sheet_talk}; talkblink mouth {sheet_tb}')

def feather_mask(w, h, f=3):
    m = np.ones((h, w), np.float32)
    up = np.linspace(0, 1, f)
    m[:f] *= up[:, None]; m[-f:] *= up[::-1, None]
    m[:, :f] *= up[None]; m[:, -f:] *= up[::-1][None]
    return m

def paste_patch(base, src_face, box_face, r):
    s = r['scale']
    fx0, fy0, fx1, fy1 = box_face
    patch = src_face.crop(box_face)
    pw, ph = max(2, int((fx1 - fx0) * s)), max(2, int((fy1 - fy0) * s))
    patch = patch.resize((pw, ph), Image.LANCZOS)
    a = np.asarray(patch).astype(np.float32); a[..., 3] *= feather_mask(pw, ph, 3)
    patch = Image.fromarray(a.astype(np.uint8), 'RGBA')
    dx = int(r['x'] + (fx0 - BAND[0]) * s); dy = int(r['y'] + (fy0 - BAND[1]) * s)
    out = base.copy(); out.alpha_composite(patch, (dx, dy))
    o = np.asarray(out).copy()
    o[..., 3] = np.minimum(o[..., 3], np.asarray(base)[..., 3])
    return Image.fromarray(o, 'RGBA'), (dx, dy, pw, ph)

tiles = []
for name, r in fit.items():
    if not r.get('blink'): continue
    pose = Image.open(M / f'poses/{name}.png').convert('RGBA')
    s = r['scale']
    fx0p = r['x'] - BAND[0] * s; fy0p = r['y'] - BAND[1] * s
    pzone = (int(fx0p + W * 0.22 * s), int(fy0p + H * 0.60 * s), int(fx0p + W * 0.80 * s), int(fy0p + H * 0.97 * s))
    ptest = lambda cx, cy: 0.35 * W < (cx - fx0p) / s < 0.70 * W and 0.68 * H < (cy - fy0p) / s < 0.86 * H
    pm = find_mouth(pose, pzone, ptest)
    pm_face = ((pm[0] - r['x']) / s + BAND[0], (pm[1] - r['y']) / s + BAND[1],
               (pm[2] - r['x']) / s + BAND[0], (pm[3] - r['y']) / s + BAND[1])
    um = (min(sheet_talk[0], pm_face[0]), min(sheet_talk[1], pm_face[1]),
          max(sheet_talk[2], pm_face[2]), max(sheet_talk[3], pm_face[3]))
    box = (max(0, int(um[0]) - 7), max(0, int(um[1]) - 7), min(W, int(um[2]) + 7), min(H, int(um[3]) + 7))
    print(f'{name}: pose mouth {pm} -> face {tuple(round(v) for v in pm_face)}; patch box {box}'
          f' (x {box[0]/W:.2f}-{box[2]/W:.2f}, y {box[1]/H:.2f}-{box[3]/H:.2f})')
    out_t, dp = paste_patch(pose, talk, box, r)
    out_t.save(M / f'poses/{name}-talk.png', optimize=True)
    blinked = Image.open(M / f'poses/{name}-blink.png').convert('RGBA')
    out_tb, _ = paste_patch(blinked, talkblink, box, r)
    out_tb.save(M / f'poses/{name}-talkblink.png', optimize=True)
    print(f'   baked {name}-talk.png + {name}-talkblink.png; patch at pose {dp}')
    for im in (pose, out_t, out_tb):
        hc = im.crop((0, 0, im.width, int(im.height * 0.45)))
        hc.thumbnail((340, 300))
        t = Image.new('RGB', (350, 310), (246, 242, 234))
        t.paste(hc, (5, 5), hc); tiles.append(t)
cols = 3
cs = Image.new('RGB', (cols * 350, ((len(tiles) + cols - 1) // cols) * 310), (120, 120, 120))
for i, t in enumerate(tiles): cs.paste(t, ((i % cols) * 350, (i // cols) * 310))
cs.save(WORK / 'talk-review.png')
print('review sheet ->', WORK / 'talk-review.png')
