# Scene worker brief - {{PRODUCT}} spatial film

PROJECT_DIR = `{{PROJECT_DIR}}`   ENGINE = `{{ENGINE}}`
Canvas {{W}}x{{H}}, rendered at {{FPS}}fps. Captions: disabled.

## Read, in this order (nothing else unless your block names it)

1. `.hyperframes/frame-packets/_role.md` - your role (core contract + general-video delta).
2. Your packet(s): `.hyperframes/frame-packets/<scene_id>.md` (storyboard block + blueprint + rule recipes).
3. `frame.md` - design truth: tokens, type, camera rig, **smoothness law**, **seam frames**, assets.
4. `references/scene-starter.html` - the known-good scene skeleton. Start your file from it.
5. `assets/kit.css` + `references/snippets.html` - the shared kit. Copy its markup; do not restyle it.
6. Your sketch cell in `storyboard.html` - grep for its id (`#frame-NN`) and read only that cell.
7. Extra references your block names. Any file in `{{SKILL}}/../hyperframes-animation/` is fair game.

## Project overrides to the role (these win over `_role.md`)

1. **Output:** `compositions/<scene_id>.html` (a bare `<template>` fragment) + `compositions/<scene_id>.motion.json`.
2. **No captions:** use the whole frame; keep film labels 60px+ from edges.
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
   scratchpad - a `gen.py` there was overwritten and run by the wrong worker (How I made this, 2026-10-06).

## Lint traps that already bit (avoid them up front)

- A label hidden under an overlay still trips `content_overlap` - fade the label out too.
- Deliberately stacked text (a deck that deals out, a card fading behind another) trips `content_overlap`:
  put `data-layout-allow-overlap` on the TEXT element itself (`<b>`, `<span>`) - on its panel it does nothing.
- A bare text node next to an absolutely positioned highlight can vanish - wrap the text in a `<span>`.
- A tween outside `0..duration` of your scene is clipped at the seam - keep every tween inside.
- Camera traps the check does not catch: never two overlapping tweens on the same cam property, and never a camera
  leg under 0.6s at t=0 - a 0.3s "push" starting on frame 0 moved the floor at the seam (API vs Webhook s06,
  1.35% seam diff). Start from identity, move slowly, come home before the end.

## Quality bar

- **{{FPS}}fps smooth:** the smoothness law, to the letter.
- **Crisp:** author UI at its closest on-screen size (`.kit-zoom`); captures are 2x PNGs shown at or below native.
- **Spatial:** real 3D with the one rig. Parallax between depths, DOF on far layers, constant drift. Mind the
  flattening traps.
- **Faithful UI:** product copy exactly as in the snippets/source. Third-party canvases ARE the capture PNGs -
  display them, never redraw them.
- **On the beat:** hits at multiples of {{BEAT}}s scene-time, as your block specifies.

## Report back (short)

Files written; lint result; snapshot times checked and what they show; anything not done as specified and why;
kit/asset change requests; your measured seam start/end states.
