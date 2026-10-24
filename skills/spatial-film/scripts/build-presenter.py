"""Build compositions/m-kape.html - the KAPE presenter overlay for a narrated film.

usage (from the film project root):  python <skill>/scripts/build-presenter.py
Reads src/presenter-track.json (or src/kape-track.json) (poses on cue words, marks, fx, bob, blink), assets/mascot/manifest.json +
blink-fit.json (sprite sizes, head anchors, blink variants), film.json (total length) and the narration audio
(film.json "audio"[0]) for the talking bob. Deterministic: same inputs -> same file. Never hand-edit the output.
A mascot with no faces/ dir and no -blink variants builds fine (every pose blink=false, head anchor from the pose).
If poses/<name>-talk.png (and optionally -talkblink.png) variants exist, the presenter also gets a
speech-driven mouth: the narration envelope flips the mouth open/closed while the voice speaks and
rests it closed in pauses; a blink during an open mouth shows -talkblink. Projects without talk
variants build exactly as before.
"""
import json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path.cwd()
film = json.loads((ROOT / "film.json").read_text(encoding="utf-8"))
TRACK = next(p for p in (ROOT / "src/presenter-track.json", ROOT / "src/kape-track.json") if p.exists())
T = json.loads(TRACK.read_text(encoding="utf-8"))
M = ROOT / "assets/mascot"
fit = json.loads((M / "blink-fit.json").read_text(encoding="utf-8")) if (M / "blink-fit.json").exists() else {}
TOTAL = round(sum(s[1] for s in film["scenes"]) * 60 / film["bpm"] * film.get("beats_per_bar", 4), 4)
S = T["scale"]
HAS_FACES = (M / "faces/neutral.png").exists()
if HAS_FACES:
    NEUTRAL_W = Image.open(M / "faces/neutral.png").width
    BAND_W = int(NEUTRAL_W * 0.94) - int(NEUTRAL_W * 0.08)  # same band as blink-fit.py

# ---- per-pose geometry: head-centre anchor x, feet = sprite bottom ----
poses = sorted({p for _, p in T["poses"]})
geo = {}
for name in poses:
    im = Image.open(M / f"poses/{name}.png")
    w, h = im.size
    f = fit.get(name, {})
    a = np.asarray(im.convert("RGBA"))[..., 3]
    if HAS_FACES and f.get("score", 0) >= 0.70:
        ax = f["x"] + BAND_W * f["scale"] / 2
    else:  # head rows centroid (no raised arm in these poses)
        cols = np.nonzero(a[int(h * 0.04): int(h * 0.26)] > 128)[1]
        if cols.size:
            ax = float(cols.mean())
        else:  # no head match: top-centre of the silhouette
            top = np.nonzero((a > 128).any(1))[0]
            tc = np.nonzero(a[top[0]: top[0] + max(1, h // 50)] > 128)[1] if top.size else []
            ax = float(np.mean(tc)) if len(tc) else w / 2
    geo[name] = {"w": w, "h": h, "ax": ax, "blink": HAS_FACES and bool(f.get("blink")) and (M / f"poses/{name}-blink.png").exists(),
                 "talk": (M / f"poses/{name}-talk.png").exists(),
                 "talkblink": (M / f"poses/{name}-talkblink.png").exists()}
HAS_TALK = any(g["talk"] for g in geo.values())

# ---- voice envelope for the talking bob ----
aud = film["audio"][0]["src"]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / aud), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
rate = T["bob"]["rate"]
hop = int(16000 / rate)
n = len(x) // hop
rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1))
env = np.clip(rms / (np.percentile(rms, 95) + 1e-9), 0, 1)
env[env < 0.12] = 0
sm = np.zeros_like(env)  # fast attack, slower release
for i in range(1, n):
    k = 0.6 if env[i] > sm[i - 1] else 0.25
    sm[i] = sm[i - 1] + k * (env[i] - sm[i - 1])
env = np.round(sm, 3)

# ---- speech-driven mouth schedule (used only when -talk variants exist) ----
# While the voice envelope is in "speech", the mouth flips open/closed roughly every 0.13s
# (seeded jitter, reproducible); during pauses it rests closed. mouth_changes = (t, open).
mouth_changes = []
if HAS_TALK:
    import random
    rng = random.Random(20261021)
    on_th, off_th = 0.22, 0.12
    speaking = False; open_ = False; next_flip = 0.0; quiet = 0
    for i, e in enumerate(env):
        t = i / rate
        if speaking:
            if e < off_th:
                quiet += 1
                if quiet >= 2:  # ~0.13s below the off-threshold: a real pause
                    speaking = False
                    if open_:
                        mouth_changes.append((round(t, 3), False)); open_ = False
            else:
                quiet = 0
        elif e >= on_th:
            speaking = True; quiet = 0; next_flip = t
        if speaking and t >= next_flip:
            open_ = not open_
            mouth_changes.append((round(t, 3), open_))
            next_flip = t + 0.13 + rng.uniform(-0.035, 0.035)
    if open_:
        mouth_changes.append((round(len(env) / rate, 3), False))

# ---- markup ----
P = film.get("overlays", [{}])[0].get("id", "m-presenter")  # the overlay id in film.json
def px(v): return f"{v:.1f}px"
imgs = []
for name, g in geo.items():
    W, H, ax = g["w"] * S, g["h"] * S, g["ax"] * S
    flip = f" transform: scaleX(-1); transform-origin: {px(ax)} 50%;" if name in T["mirror"] else ""
    for suffix in ([""] + (["-blink"] if g["blink"] else []) + (["-talk"] if g["talk"] else []) + (["-talkblink"] if g["talkblink"] else [])):
        imgs.append(f'          <img id="{P}-p-{name}{suffix}" class="{P}-p" src="assets/mascot/poses/{name}{suffix}.png" alt="" '
                    f'style="width:{px(W)}; height:{px(H)}; left:{px(-ax)}; top:{px(-H)};{flip}">')
fx_html = []
for i, fx in enumerate(T.get("fx", [])):
    im = Image.open(M / f"{fx['sprite']}.png")
    w, h = im.width * fx["scale"], im.height * fx["scale"]
    fx_html.append(f'        <img id="{P}-fx{i}" class="{P}-p" src="assets/mascot/{fx["sprite"]}.png" alt="" '
                   f'style="width:{px(w)}; height:{px(h)}; left:{px(fx["dx"] - w / 2)}; top:{px(fx["dy"] - h / 2)};">')

# ---- timeline ----
js = []
home, ent = T["home"], T["enter"]
js.append(f"gsap.set(q('pos'), {{ x: {ent['from_x']}, y: {home['feet']}, force3D: true }});")
js.append(f"tl.fromTo(q('pos'), {{ x: {ent['from_x']} }}, {{ x: {home['x']}, duration: {ent['dur']}, ease: 'expo.out', force3D: true }}, {ent['at']});")
sched = T["poses"]
first = sched[0][1]
# blinks: only on poses that have a blink variant, never within 0.3s of a swap
swaps = [t for t, _ in sched]
def pose_at(t):
    cur = sched[0][1]
    for st, nm in sched:
        if st <= t: cur = nm
    return cur
blink_intervals = []
tb, k, b = 1.9, 0, T["blink"]
while tb < TOTAL - 0.5:
    nm = pose_at(tb)
    if geo[nm]["blink"] and all(abs(tb - s) > 0.3 and abs(tb + b["dur"] - s) > 0.3 for s in swaps):
        blink_intervals.append((round(tb, 3), round(tb + b["dur"], 3)))
    tb += b["every"][k % len(b["every"])]; k += 1
if not HAS_TALK:
    js.append(f"gsap.set('.{P}-p', {{ opacity: 0 }}); gsap.set(q('p-{first}'), {{ opacity: 1 }});")
    for (t, name), prev in zip(sched[1:], sched):
        js.append(f"tl.set(q('p-{prev[1]}'), {{ opacity: 0 }}, {t}); tl.set(q('p-{name}'), {{ opacity: 1 }}, {t});")
        js.append(f"tl.fromTo(q('pop'), {{ scaleX: 1.04, scaleY: 0.95 }}, {{ scaleX: 1, scaleY: 1, duration: 0.42, ease: 'back.out(2.2)', immediateRender: false, force3D: true }}, {t});")
    for bs, be in blink_intervals:
        nm = pose_at(bs)
        js.append(f"tl.set(q('p-{nm}-blink'), {{ opacity: 1 }}, {bs:.2f}); tl.set(q('p-{nm}-blink'), {{ opacity: 0 }}, {be:.2f});")
else:
    # merged face timeline: pose swaps + blinks + mouth resolve to exactly one visible variant per pose
    def variant_for(nm, blinking, mouth_open):
        g = geo[nm]
        if blinking and mouth_open:
            return "-talkblink" if g["talkblink"] else ("-talk" if g["talk"] else ("-blink" if g["blink"] else ""))
        if mouth_open:
            return "-talk" if g["talk"] else ""
        if blinking:
            return "-blink" if g["blink"] else ""
        return ""
    events = {}
    def add_ev(t, kind, val):
        events.setdefault(round(t, 3), []).append((kind, val))
    for t, name in sched[1:]:
        add_ev(t, "pose", name)
    for bs, be in blink_intervals:
        add_ev(bs, "blink", True); add_ev(be, "blink", False)
    for t, open_ in mouth_changes:
        add_ev(t, "mouth", open_)
    cur_pose, cur_blink, cur_mouth = first, False, False
    shown = variant_for(cur_pose, cur_blink, cur_mouth)
    js.append(f"gsap.set('.{P}-p', {{ opacity: 0 }}); gsap.set(q('p-{first}{shown}'), {{ opacity: 1 }});")
    for t in sorted(events):
        swapped = False
        for kind, val in events[t]:
            if kind == "pose":
                cur_pose = val; swapped = True
            elif kind == "blink":
                cur_blink = val
            else:
                cur_mouth = val
        want = variant_for(cur_pose, cur_blink, cur_mouth)
        if swapped:
            prev_pose = pose_at(t - 0.001)
            for suffix in ("", "-blink", "-talk", "-talkblink"):
                if (M / f"poses/{prev_pose}{suffix}.png").exists():
                    js.append(f"tl.set(q('p-{prev_pose}{suffix}'), {{ opacity: 0 }}, {t});")
            js.append(f"tl.set(q('p-{cur_pose}{want}'), {{ opacity: 1 }}, {t});")
            js.append(f"tl.fromTo(q('pop'), {{ scaleX: 1.04, scaleY: 0.95 }}, {{ scaleX: 1, scaleY: 1, duration: 0.42, ease: 'back.out(2.2)', immediateRender: false, force3D: true }}, {t});")
        elif want != shown:
            js.append(f"tl.set(q('p-{cur_pose}{shown}'), {{ opacity: 0 }}, {t}); tl.set(q('p-{cur_pose}{want}'), {{ opacity: 1 }}, {t});")
        shown = want
# breath (1.2% on the breath layer) and talking bob (voice envelope) - fromTo chains, explicit starts
cyc, t = 2.4, 0.0
while t + cyc <= TOTAL:
    js.append(f"tl.fromTo(q('breath'), {{ scaleY: 1 }}, {{ scaleY: 1.012, duration: {cyc / 2}, ease: 'sine.inOut', immediateRender: false, force3D: true }}, {t:.2f});")
    js.append(f"tl.fromTo(q('breath'), {{ scaleY: 1.012 }}, {{ scaleY: 1, duration: {cyc / 2}, ease: 'sine.inOut', immediateRender: false, force3D: true }}, {t + cyc / 2:.2f});")
    t += cyc
by, sq = T["bob"]["y"], T["bob"]["squash"]
js.append(f"var E = {json.dumps(env.tolist())};")
js.append(f"for (var i = 1; i < E.length; i++) {{ if (E[i] === 0 && E[i - 1] === 0) continue;"
          f" tl.fromTo(q('bob'), {{ y: {by} * E[i - 1], scaleY: 1 + {sq} * E[i - 1] }}, {{ y: {by} * E[i], scaleY: 1 + {sq} * E[i],"
          f" duration: {1 / rate:.4f}, ease: 'sine.inOut', immediateRender: false, force3D: true }}, (i - 1) / {rate}); }}")
for i, fx in enumerate(T.get("fx", [])):
    js.append(f"gsap.set(q('fx{i}'), {{ opacity: 0, scale: 0.3, transformOrigin: '50% 100%' }});")
    js.append(f"tl.fromTo(q('fx{i}'), {{ opacity: 0, scale: 0.3, y: 20 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.45, ease: 'back.out(2)', immediateRender: false, force3D: true }}, {fx['at']});")
    js.append(f"tl.fromTo(q('fx{i}'), {{ y: 0 }}, {{ y: -14, duration: {fx['out'] - fx['at'] - 0.7:.2f}, ease: 'sine.inOut', immediateRender: false, force3D: true }}, {fx['at'] + 0.45});")
    js.append(f"tl.fromTo(q('fx{i}'), {{ opacity: 1, scale: 1 }}, {{ opacity: 0, scale: 0.6, duration: 0.25, ease: 'power2.in', immediateRender: false, force3D: true }}, {fx['out'] - 0.25});")

html = f"""<!-- Generated by spatial-film/scripts/build-presenter.py from {TRACK.name} - edit the track, not this file. -->
<template>
<style>
#root {{ position: absolute; inset: 0; width: {film["width"]}px; height: {film["height"]}px; overflow: hidden; }}
.{P}-anchor {{ position: absolute; left: 0; top: 0; width: 0; height: 0; will-change: transform; transform-origin: 0 0; }}
.{P}-p {{ position: absolute; display: block; will-change: opacity; }}
</style>
<div id="root" data-composition-id="{P}" data-width="{film["width"]}" data-height="{film["height"]}">
  <div id="{P}-layer" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="1" style="position:absolute; inset:0;">
    <div id="{P}-pos" class="{P}-anchor">
      <div id="{P}-shadow" style="position:absolute; left:-170px; top:-34px; width:340px; height:68px; border-radius:50%; background:radial-gradient(closest-side, rgba(11,30,63,.24), rgba(11,30,63,0));"></div>
      <div id="{P}-bob" class="{P}-anchor">
        <div id="{P}-breath" class="{P}-anchor">
          <div id="{P}-pop" class="{P}-anchor">
{chr(10).join(imgs)}
          </div>
        </div>
      </div>
{chr(10).join(fx_html)}
    </div>
  </div>
</div>
<script>
(function () {{
  var q = function (id) {{ return '#{P}-' + id; }};
  var tl = gsap.timeline({{ paused: true }});
  {(chr(10) + '  ').join(js)}
  window.__timelines = window.__timelines || {{}};
  window.__timelines['{P}'] = tl;
}})();
</script>
</template>
"""
(ROOT / "compositions").mkdir(exist_ok=True)
(ROOT / f"compositions/{P}.html").write_text(html, encoding="utf-8")
print(f"compositions/{P}.html: {len(sched)} poses, {len(blink_intervals)} blinks, {len(env)} bob frames, total {TOTAL}s")
if HAS_TALK:
    print(f"  talk: {sum(1 for c in mouth_changes if c[1])} mouth opens on poses {[n for n, g in geo.items() if g['talk']]}")
for name, g in geo.items():
    print(f"  {name:<10} {g['w'] * S:6.0f}x{g['h'] * S:4.0f}  anchor {g['ax'] * S:5.1f}  blink {g['blink']}  talk {g['talk']}")
