# Scene worker brief - {{FILM_NAME}} spatial explainer (1920x1080 landscape, narrated)

PROJECT_DIR = `{{PROJECT_DIR}}`   ENGINE = `{{ENGINE}}`   SKILL = `{{SKILL}}`   PY = `{{PY}}`
Canvas 1920x1080 (LANDSCAPE 16:9), rendered at 60fps. Captions: disabled. Two overlays sit above every scene - the KAPE presenter (compositions/m-kape.html, LEFT third) and the brand corner logo (m-brand, top-right) - not yours, keep out of their zones (frame.md Layout).

## Read, in this order (nothing else unless your block names it)

1. `.hyperframes/frame-packets/_role.md` - your role (core contract + general-video delta).
2. Your packet(s): `.hyperframes/frame-packets/<scene_id>.md` (storyboard block + blueprint + rule recipes).
3. `frame.md` - design truth: tokens, type, camera rig, **smoothness law**, **seam frames**, assets.
4. `references/scene-starter.html` - the known-good scene skeleton. Start your file from it.
5. `assets/kit.css` + `references/snippets.html` - the shared kit. Copy its markup; do not restyle it.
6. (No sketch sheet this film - the storyboard block is the spec.)
7. Extra references your block names. Any file in `{{SKILL}}/../hyperframes-animation/` is fair game.

## Project overrides to the role (these win over `_role.md`)

1. **Output:** `compositions/<scene_id>.html` (a bare `<template>` fragment) + `compositions/<scene_id>.motion.json`.
2. **No captions, landscape zones:** obey frame.md "Layout - landscape frame zones"; keep film labels 60px+ from edges.
3. **Seams are authored INSIDE the scenes** (no transition injector): your first and last frames are the exact
   shared seam frames in `frame.md`, held ~0.1s. This replaces "never author an exit". Lock an exact seam pose
   with a 2D plate outside the camera rig, and while the plate shows nothing else does (hide your rig under an end
   plate; keep your in-rig copy hidden until a start plate hands off) - a copy under it doubles the shadow.
4. **Paths are root-relative:** `assets/...` (never `../assets/`). Link the kit inside the template plus the two
   `@font-face` lines from `frame.md`.
5. **Ids:** composition id = timeline key = `<scene_id>`. Every element the timeline touches gets an id prefixed
   `<scene_id>-`; every class you define is prefixed `<scene_id>-`. Kit classes are used as-is.
6. **GSAP is loaded by the host page** (core only, no plugins). No GSAP script tag, no CustomEase/MotionPath/
   SplitText: built-in eases (`back.out(1.6)` is the spring) and keyframe arrays for arcs. Build the timeline
   synchronously and register it last.
7. **Test through the harness only** (this replaces "you do not run the CLI"), from PROJECT_DIR:
   `node "{{ENGINE}}/scripts/test-scene.mjs" <scene_id> "<t1,t2,...>"`
   It prints lint and writes `.hyperframes/test/<scene_id>/snaps/` (`contact-sheet.jpg` + one PNG per time).
   Read the contact sheet first; open a single PNG only to inspect a detail. Snapshot every phase midpoint plus
   your first and last frame. Iterate until lint shows **0 errors** and every frame reads as the block describes.
   Cap: 8 iterations.
8. **Never touch:** `index.html`, `film.json`, `STORYBOARD.md`, `frame.md`, `assets/`, `references/`, `src/`,
   other scenes' files. No `render`, `preview`, `publish`, no git. Need a kit or asset change? Say so in the report.
9. **Edits:** rewrite your whole file with Write, or for exact multi-line edits write a Python file that calls
   `patch(path, [(old, new), ...])` from `{{ENGINE}}/scripts/patch_exact.py`. Never put patch
   bodies or backslash-heavy text in a Bash heredoc.
10. **Your scratch lives in the project, never the session scratchpad:** generators, templates and temp files go
   in `PROJECT_DIR/.hyperframes/work/<your scene ids>/` and run from there. Parallel workers share the session
   scratchpad - a `gen.py` there was overwritten and run by the wrong worker.

## Lint traps that already bit (avoid them up front)

- A label hidden under an overlay still trips `content_overlap` - fade the label out too.
- Deliberately stacked text (a deck that deals out, a card fading behind another) trips `content_overlap`:
  put `data-layout-allow-overlap` on the TEXT element itself (`<b>`, `<span>`) - on its panel it does nothing.
- A bare text node next to an absolutely positioned highlight can vanish - wrap the text in a `<span>`.
- A tween outside `0..duration` of your scene is clipped at the seam - keep every tween inside.
- Every property in a `fromTo`'s FROM vars must also be in its TO vars (or animated by another tween on the
  same target). GSAP only tweens TO props: a from-only `opacity: 1` shows in the harness (plays in order) and
  is invisible in the render (workers seek mid-scene). Check: `{{PY}} {{ENGINE}}/scripts/fromto-scan.py compositions/<id>.html`.

## Quality bar

- **60fps smooth:** the smoothness law, to the letter.
- **Crisp:** author UI at its closest on-screen size (`.kit-zoom`); captures are 2x PNGs shown at or below native.
- **Spatial:** real 3D with the one rig. Parallax between depths, DOF on far layers, constant drift. Mind the
  flattening traps.
- **Faithful copy:** on-screen words exactly as the storyboard block quotes them (spelling included). The GHL form, n8n canvas and contact
  card are kit components - use them, never redraw them. Anything else is built in-scene from kit tokens +
  `.kit-card` / `.kit-chip` / `.kit-ico`; third-party products are plain text on neutral cards, never their logos.
- **Readable by anyone:** this film teaches non-technical viewers. One idea on screen at a time, big labels, each
  object arrives on the word that names it, and the orange/teal/gray colour code is never broken.
- **On the word:** every hit lands on its narration cue word at the scene-local time your block gives (arrivals start ~0.1s early and land on the word).

## Report back (short)

Files written; lint result; snapshot times checked and what they show; anything not done as specified and why;
kit/asset change requests; your measured seam start/end states.
