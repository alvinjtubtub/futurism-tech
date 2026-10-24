# Phase 3 - Harness, packets, parallel scene workers

Goal: all scenes built in ONE wave by fast coding workers (Baet subagents), each lint-clean and seam-exact in its own harness.

## 1. Harness + smoke test (never skip - it caught two contract-level lint rules)

```bash
<py> <skill>/scripts/make-harness.py                     # .hyperframes/test/<id>/ per scene (assets copied, audio skipped)
node -e "const f=require('fs');f.writeFileSync('compositions/<first_id>.html',f.readFileSync('references/scene-starter.html','utf8').replaceAll('SCENE','<first_id>').replaceAll('DUR','<dur>'))"
node <skill>/scripts/test-scene.mjs <first_id> "0.5,<dur-0.05>"
```

Expect 0 lint errors and two sane snapshots. A lint error here is a CONTRACT bug: fix it in frame.md /
worker-brief / starter, never per scene. Then delete the dummy (`rm compositions/<first_id>.html`).

## 2. Packets

```bash
node <skill>/../general-video/scripts/frame-packets.mjs --project . --storyboard STORYBOARD.md
wc -c .hyperframes/frame-packets/*      # each under 48KB; trim a block's rules: if not
```

## 3. Split the work (disjoint files, 1-2 scenes per worker, one wave)

- The first and last scene go to ONE worker (they share the loop pose; define it once, reuse identical values).
- The heaviest scene (most UI, e.g. the editor) gets a worker to itself.
- Two short adjacent scenes can share a worker (their seam becomes internal).
- worked example: W1 s01+s07, W2 s02, W3 s03, W4 s04+s05, W5 s06.

## 4. Dispatch (Baet subagents, run in background, at most 4 at once - queue the 5th)

Prompt per worker - hand file PATHS, never paste the files (saves tokens in both contexts):

```
You are a HyperFrames scene worker building <one|two> scene(s) of a <N>s spatial 3D product film for <PRODUCT>
(<one line: what the product does>).

PROJECT_DIR: <abs path>
Your frame(s): <id> (<dur>s)[, <id> (<dur>s)] - <one line: what happens, start to end>.
[Loop pair only: the last frame of <last> must be pixel-identical to the first frame of <first>: <loop pose>.
Define it once and reuse the identical values in both files.]

Start by reading PROJECT_DIR/references/worker-brief.md and follow it exactly. Then read
.hyperframes/frame-packets/_role.md, .hyperframes/frame-packets/<id>.md, frame.md, references/scene-starter.html,
assets/kit.css, references/snippets.html, and the sketch cell(s) <#frame-NN> in storyboard.html.
<Extra refs by name, e.g. references/platform-canvases.md; blueprint file path if cited.>
<Hard facts: "The platform canvases ARE the PNGs in assets/captures/ (ghl-sheet.png 2270x4044 ...) - display them, never redraw.">

Seams you must hit exactly (frame.md): start = <shared frame>; end = <shared frame> (lock it with a 2D plate outside the rig).

Write compositions/<id>.html (+ .motion.json). Verify with the harness at every phase midpoint plus 0 and <dur>,
read the contact sheet, iterate until lint has 0 errors and the frames match the block.
Report back briefly as the brief asks.
```

## 5. While they run, then after

- Do phase 4 (audio) in the main session meanwhile - it touches no scene file.
- On each report: read the worker's contact sheet (one image), not its HTML. Note kit/asset change requests
  and apply them centrally once all workers are done (never while they run - shared files).
- Main-session fixes after the wave: locate with `grep -n` in the scene, patch the exact lines (patch_exact.py),
  re-run its harness. Never read a whole 20-60KB scene file into the main context.
