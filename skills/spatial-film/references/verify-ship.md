# Phase 5 - Assemble, verify, render, ship

## Assemble + check

```bash
<py> <skill>/scripts/assemble.py                         # index.html from film.json (never hand-edit it)
npx --yes hyperframes@<ver> check 2>&1 | tail -40          # lint + runtime + layout + motion + contrast
```

Fix every error. Known check findings and their fix:

| Finding | Fix |
|---|---|
| `content_overlap` on a label under an overlay/busy state | fade the label out with the overlay |
| a label vanishes under an absolutely positioned highlight | wrap its bare text node in a `<span>` |
| `duplicate_audio_track` floods | cues need `data-duration` - assemble.py does it; re-run it |
| contrast on a muted ink | darken the token at `:root` (ink-faint), not per call site |
| contrast on a real brand color (white on the platform's orange button) | leave it - it is the real UI; say so |

## Seams + loop (by pixels, then by eye)

```bash
<py> <skill>/scripts/seam-check.py          # every seam pair + frame 0 vs last frame; PASS under 0.5% differ
```

A FAIL means one side does not hold the shared frame: compare the two PNGs in `snapshots/seams/`, fix the scene
whose pose drifted (usually the plate opacity or a drift tween still moving under it). Whip-pan seams can fail on
motion blur - judge those two frames by eye.

## Motion audit

```bash
HYPERFRAMES_SKILL_BOOTSTRAP_DEPS=1 HYPERFRAMES_SKILL_PKG_VERSION=<ver> node <skill>/../hyperframes-animation/scripts/animation-map.mjs . --out .hyperframes/anim-map --fps 60
```

Read the summary: no dead zones (nothing moving for 1s+ outside the held lockup), no linear eases, no
layout-property tweens. Then snapshot 1 frame per scene midpoint and look at them as a sequence.

## Render (CLI + hardware GPU - never Studio's Export for a final)

```bash
node <skill>/scripts/render-final.mjs <name>-1080p60          # run_in_background; progress in renders/<name>.log
```

- Studio's Export used `software gpu` (~1 frame/s at 4K60, about an hour); the CLI with `--browser-gpu --workers 6`
  rendered the same 60s at 1080p60 in 4m19s, 61.5MB. The script prints the gpu line - it must say hardware.
- 4K master: add `--resolution 4k` (check `render --help` for the exact flag on the pinned version).
- Stopping a render: kill the whole node process tree (Windows `taskkill /T /F /PID <pid>`, macOS/Linux
  `pkill -f "hyperframes.*render"`); stopping only the shell leaves the render running.
- Verify the file: the script's ffprobe shows width/height/60fps/duration. Pull 4 frames into one strip and look:
  `ffmpeg -v error -y -i renders/<name>.mp4 -vf "select='eq(n\,600)+eq(n\,1500)+eq(n\,2340)+eq(n\,3420)',scale=480:-1,tile=4x1" -frames:v 1 strip.png`

## Ship

- Web encode + poster: `node <skill>/scripts/encode-web.mjs renders/<name>.mp4 <out-dir> --name <slug> --poster <t>`
  (keeps the audio; `--silent` for video only). Pick the poster from a frame where the hero UI is fully in.
- Embed: `<video autoplay muted loop playsinline preload="metadata" poster="...">` - browsers only autoplay muted.
- Stop the Studio preview if one is up: `npx hyperframes preview --stop`.
- Commit the project (renders/, .hyperframes/, .media/, snapshots/, source mp3 stay gitignored).

## Done when

`check` passes (0 errors), `seam-check.py` all PASS (or whip pans confirmed by eye), the animation map is clean,
the render log says hardware gpu, ffprobe shows the right size/fps/duration, and the strip looks right.
