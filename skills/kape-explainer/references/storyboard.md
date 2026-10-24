# Phase 2 - Storyboard + scene blocks for a narrated explainer

Load at phase 2. The worked example is `<skill>/template/STORYBOARD.example.md` (API vs Webhook v2) - read it
once; it is the shape every block must have (the engine's packet builder reads those fields).

## Cutting scenes from the narration

- Print the words with times: `<py> <skill>/scripts/words.py src/timing/vo-words.json`.
- One scene per paragraph/idea, cut in the PAUSE between sentences. `film.json` runs `bpm 60, beats_per_bar 1`, so
  scene lengths are plain seconds (decimals fine). Sum = narration end + ~1.0s held lockup.
- Check every cut against the LAST word of the line the scene shows: if the title lands at 5.70 and the
  next cut is at 6.5, the title shows 0.25s - move the cut to the next sentence's first word instead.
- Block times are SCENE-LOCAL (global word time - scene start). Arrivals start ~0.1s before the word, land on it.

## Teaching picture rules (the brief: "anyone can understand even without tech background")

- Everyday picture first, real tool second. One idea on screen at a time; each object arrives on the word that
  names it; nothing appears before it is said.
- **Colour = meaning, fixed for the whole film**, chosen once in frame.md (demo example: orange = you ask /
  arrow OUT from the presenter, teal = they tell you / arrow IN to the presenter, gray = the "no reply yet" state,
  red = one struck word).
- A spine motif that carries the lesson through every scene (e.g. a packet that travels an arrow).
- Big type: every scene's top band has a real headline (60-84px), body >= 40px, objects use the full width.
  **Write the headline COPY into every block** ("Top band: `.kit-label.sm` "In short""). A block that
  names only a kicker gets a 28px kicker alone and needs a fix pass. CHECK it before showing the storyboard:
  `grep -n "^## Frame\|headline\|kit-label" STORYBOARD.md` - every Frame heading needs a headline/kit-label line
  under it (title and end-card frames excepted).

## Layout zones - put these in frame.md, they are the contract

**Landscape 1920x1080 (default):** Presenter zone x 40-620, y 420-1060 (LEFT third, feet y 1030, presenter scale 0.5,
home x 330). Corner logo x > 1500, y < 150. Top band x 640-1460, y 60-190, headline centred on x ~1050. Stage x
640-1860, y 200-1020 - the story reads LEFT -> RIGHT (the presenter's side -> the other side), so "OUT from the presenter" packets
fly left-to-right and "IN to the presenter" fly right-to-left. Side-by-side UI (a GHL form + n8n) does not fit at readable
zoom - stack it diagonally. Open: the brand logo + the opener word (brand.json `opener`) above the title. Close: END CARD (logo + the
`cta` line from brand.json) centred x ~1150.

**Vertical 1080x1920 (`--format 9x16`):**
- Top band y 170-430: headline. Stage y 440-1040, x 60-1020: main objects. Lower right x 500-950, y 1000-1500:
  chips / notification / contact card. Presenter zone x 20-480, y 1000-1700: the presenter, never scene content.
  Nothing below y 1720; no text at x > 950 below y 1300 (Reels UI).

## Depth staging (a near/far spine)

- Things lying ON the floor (a road, painted arrows) cannot rise above the floor's horizon (~frame y 560 at the
  identity camera). Put FAR floor-bound objects at frame y >= ~460, or the worker has to tilt the plane (s04's road
  became a ~20deg tilted matrix3d to reach a hub specced at y 380).
- Sign/arrow swing in this rig: a right-pointing plank at **+rotationY** sends its tip AWAY into depth; -rotationY
  brings it toward the camera. Spec the sign that way round.
- A chip "on" something next to the presenter's prop lands on the prop. Spec chips in open stage space (above the
  van, not on the house door), or the chip covers the thing it labels.

## Seams

Canon floor (ground + kit floor, cam/drift at identity, nothing else) between most scenes; a white push-through
into a phone screen where the story goes "into" the phone; a shared STAGE pose where two scenes use the same
objects (give both to ONE worker). No loop - the film ends on a held lockup.
Film start is canon floor too, so s01 opens with the cam at identity - do not spec the example's opening crane
(a worker drops it as a seam violation; the logo fade carries the open).

## Presenter track (`src/presenter-track.json`, built by the engine's `spatial-film/scripts/build-presenter.py`)

Pose per cue word (~0.1s before it): wave on the opener and closer, think on the question, point (mirrored into
the frame) when the stage shows the thing, present on summaries, thumbs-up on a check-in, sit when the story says
the presenter stops doing something. fx: question bubble on the question, sparkle on a win. Use only poses the
mascot has (idle and point always exist). Blinks only on poses `blink-fit.json` marks (none for a mascot without
blink faces); ~13 blinks in 83s read natural.

## Workers (the engine's references/workers.md, with these deltas)

- Pairs: first + last scene (title tiles); every STAGE-pose pair; heaviest scene (GHL/n8n) with its pair.
- The worker prompt must carry the size law and the presenter zone - a first wave without them ships ~33px text in
  the top 45% of the frame and most workers need a second pass.
- Review each worker's contact sheet (never the HTML). Then snapshot the FULL composite
  (`npx hyperframes snapshot . --at <times> --no-end --describe false -o .hyperframes/full-snaps`) to judge the presenter
  against every scene before rendering.
