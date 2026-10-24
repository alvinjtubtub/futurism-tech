# Phase 1 - Intake, brief, storyboard, sketch

Goal: a locked `STORYBOARD.md` whose every block a worker can build without asking. The plan is the cheapest
place to be wrong; the build cannot fix a vague block.

## Intake (one AskUserQuestion, max 3 questions)

Ask only what you cannot find: (1) storyboard review first, or straight to build; (2) aspect - 16:9 only, or also
a vertical cut; (3) music - user supplies a track, or you source one. Everything else comes from the prompt and
the product's source. Default to storyboard review first.

## Read the truth before writing a word

- The product's own HTML/CSS (popup, editor, settings...): copy, layout, tokens, real labels, real states,
  real shortcuts. Write every place the prompt disagrees with the source under BRIEF.md "Accuracy corrections"
  (the worked example prompt put "Copy for AI" in the editor; it lives in the popup).
- Any screenshot the user pasted of the live UI: it beats the prompt.
- Third-party tools shown on screen (GHL, n8n, Zapier, Make...): the user's own real captures, never memory.

## BRIEF.md

Fill `template/BRIEF.md`: front matter (workflow general-video, storyboard yes, message, aspect, length,
audience), Intent, Assets (paths to the real font, mark, source UI, captures), Customizations (user asks, quoted
and dated), Notes (accuracy corrections, mock data, bans).

## Structure the film

- **Arc:** hook (the product's own entry point, e.g. the click) -> 2-4 proof scenes (each one feature with a
  visible proof moment) -> lockup -> loop back to frame 0. 60s holds 6-8 scenes.
- **Beat grid first:** pick the BPM (110 worked: beat 0.5455s, bar 2.1818s). Every scene is a whole or half
  number of bars; list them in `film.json` `scenes`. Long feature scenes 6-6.5 bars, bridges 2-3 bars.
- **Rhythm inside a scene:** long, medium, short (3 platforms: 5.5s, 3.3s, 2.2s) reads as acceleration.
- **The spine:** one visual motif that travels through every scene (worked example: the popup's corner ticks became
  the scan frame, then crop handles, then closed back onto the popup). Plus a second thread if useful (the
  capture is a physical sheet the camera follows).
- **Seams:** choose one shared frame per seam (see the catalogue below) and write them into `frame.md`'s table.
- **Loop:** frame 0 = last frame. Pick a pose both the first and last scene can hold (the toolbar slightly out
  of focus). A dark open cannot loop into a light close - use a focus rack instead of a fade.

## Seam catalogue (all proven)

| Seam | Shared frame | Use when |
|---|---|---|
| Push-through solid | full-frame solid color (camera dives into a button / chat box / page) | the next scene starts "inside" what was clicked |
| Exact plate | one asset at an exact 2D pose (e.g. a sheet flat, width 1920, top -300) over the ground | an object carries across the cut |
| Card plate | a card at an exact rect (1280x720 at 320,180, radius 24) | the next scene opens on that card |
| Whip pan | content streaks out with horizontal motion blur; last/first 2 frames are ground only | energy change between sections |
| Loop pose | identical scene pose in the last and first scene | the film's end -> start |

## Each storyboard block (fill `template/STORYBOARD.md`)

- Fields the packet builder reads: `scene`, `duration`, `poster`, `transition_in`, `status`, `src`,
  `blueprint` (**exactly one id**, `id (Adapt)` - two ids throw), `rules` (**2-3 ids max** - the builder inlines
  every rule a block mentions and caps each packet at 48KB), `confirmed sketch`.
- **World:** every object with size, world position (x, y, z, rotationY), and which snippet/asset it uses.
- **Phases in scene-local seconds** with eases and durations, every hit on a named beat ("clicks on beat 5 (2.73)").
- **Seam in / seam out** stated exactly as in `frame.md`.
- Mock data only (Northwind Dental style). Exact on-screen copy in quotes.
- Browse blueprints/rules in `<skill>/../hyperframes-animation/` by filename; read only the 1-3 you cite.

## Sketch sheet + lock

general-video's sketch review produces `storyboard.html` (one cell per frame, `#frame-NN`, plus close-up cells for
anything that must look exact, e.g. `#frame-02-ghl`). Open it for the user, take corrections, bump the version,
record them under "Changes from vN". **Gate:** the user's explicit "go" recorded under "## Locked". No scene is
built before that.
