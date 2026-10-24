---
name: kape-explainer
description: KAPE Explainer - turn a topic into a narrated 16:9 (1920x1080, 60fps; vertical 1080x1920 on request) spatial 3D motion-design explainer where a mascot presents in the user's own voice and the film carries the user's own brand (logo open, corner logo, end card with their call to action). Writes the script in the user's speaking style, takes their voiceover MP3 (hand-made with Gemini 3.8 Flash TTS, or any recording), transcribes it to word timings, builds the mascot presenter (pose swaps on cue words, blinks, voice bob), storyboards everyday-picture scenes for non-technical viewers, builds them with parallel workers on the bundled spatial-film engine, masters the audio and renders at 60fps with a proven word-sync check. First run sets up their profile (brand, voice, mascot). MUST USE when the user says "kape explainer", "explainer video with my voice", "explainer with my mascot", "make it look like I'm explaining", "motion design explainer", or hands over a voiceover MP3 for an explainer video. For an unnarrated 3D product film use the spatial-film skill.
---

# KAPE Explainer

A narrated explainer = **the speaker's voice is the clock**, a mascot is the presenter, every idea is an everyday
picture first, and the film is **branded to the user** (their logo opens it, sits in the corner, and closes it
with their call to action). Default 1920x1080 at 60fps; `--format 9x16` for a vertical cut. KAPE, the glasses-and-coffee-mug
mascot, ships as the demo presenter until the user brings their own character.

Paths used below:
- `<skill>` = this skill's folder (the directory this SKILL.md is in).
- `<engine>` = `<skill>/../spatial-film` - the film engine: scaffold, harness, workers, assemble, seam-check,
  presenter builder, render. Read its SKILL.md "Narrated films" section when phase 4 starts.
- `<home>` = `KAPE_EXPLAINER_HOME` or `~/.kape-explainer`. Profile = `<home>/profile/`.
- `<py>` = the `python` command saved in `<home>/config.json` by setup-check (e.g. `py -3.12` on Windows,
  `python3` on macOS).

Run every film script from the film project root.

## Context discipline

Load ONE phase reference when its phase starts. Scripts are proven code - run them, never regenerate them. Judge
scenes by contact sheets, never by reading scene HTML in the main session. Workers get file PATHS.

## Phase S - Setup (first run only, skip when `<home>/profile/brand.json` exists)

1. `node <skill>/scripts/setup-check.mjs` - fix every MISSING line with the install command it prints, rerun
   until it exits 0. Tell the user plainly what to install; do not install system tools without asking. Its
   YOUR INPUTS block lists what only the user can bring (TODO / ASK / OPTIONAL) - steps 2-5 fill those.
2. Brand interview, one message (include the voiceover question: a narration MP3 they generate themselves with Gemini 3.8 Flash TTS (manual, no API key), or
   recording themselves with a decent mic in a quiet room - no route = stop and tell them they need one), then `node <skill>/scripts/profile.mjs init --name "<brand>" ...`
   (flags: `--wordmark "Part1,Part2" --logo <file> --logo-has-text --ink #hex --accent #hex --opener "explains"
   --cta "Follow for more" --presenter "<mascot name>" --language "<language>" --films-dir <dir>`).
   A PNG logo goes through `<py> <skill>/scripts/prep-logo.py <logo> <home>/profile` first. No logo = wordmark only.
3. Voice: fill `<home>/profile/voice.md` (the template explains both ways) - 5-question interview, or
   `<py> <skill>/scripts/speech-profile.py` on the transcript of a 5+ minute unscripted recording of them talking.
4. Mascot: keep the KAPE demo, or put their character's transparent pose PNGs in `<home>/profile/mascot/poses/`
   (`idle.png` + `point.png` required; `wave`, `present`, `think`, `thumbs-up`, `celebrate` recommended;
   `faces/neutral.png` + `faces/blink.png` enable blinks) and run `<py> <skill>/scripts/prep-mascot.py
   <home>/profile/mascot`. Show them the summary table.
5. Music (optional): their own licensed bed at `<home>/profile/music/bed.mp3`. Otherwise phase 5 offers the
   HeyGen catalog (`npx hyperframes auth login` once) or no bed.

`node <skill>/scripts/profile.mjs show` prints the merged profile at any time.

## Phases (each ends on a gate)

| # | Phase | Do | Gate |
|---|---|---|---|
| 0 | Script | Load `references/voice-script.md` + `<home>/profile/voice.md`; write the script in THEIR voice; give the Gemini TTS notes (voice pick + punctuation direction, or "record it in one take" tips) | they hand over ONE mp3 |
| 1 | Intake | `node <skill>/scripts/new-explainer.mjs [<film dir>] --name <slug> --mp3 <mp3>` (dir defaults to the profile's films_dir; `--format 9x16` for vertical); `<py> <skill>/scripts/transcribe.py assets/audio/vo.mp3 src/timing --prompt "<names, jargon>" --lang <code>` (code from the profile's `language`: English `en`, Taglish/Tagalog `tl`, Spanish `es`...) | transcript matches the script; mp3 duration noted |
| 2 | Storyboard | Load `references/storyboard.md`; BRIEF.md + STORYBOARD.md (blocks with scene-local word cues), film.json scenes | their explicit "go" under `## Locked` |
| 3 | Contract + presenter | Rewrite frame.md's FILM-SPECIFIC parts (checklist below); master the audio FIRST (`build-presenter.py` reads `vo-master.wav` for the bob): with a bed `<py> <engine>/scripts/bgm-cut.py assets/audio/bed.mp3 assets/audio/bgm-edit.wav --len <total> --a 0 <total+3> --fade-out 2.6`, then `<py> <skill>/scripts/master-audio.py --len <total>`; write `src/presenter-track.json` (only poses the mascot has - see `assets/mascot/manifest.json`); `<py> <engine>/scripts/build-presenter.py`; `<py> <skill>/scripts/build-brand.py`; harness-test `m-kape` + `m-brand` | presenter contact sheet: poses on cue, no jumps; corner logo clear of every headline |
| 4 | Scenes | `<engine>` workers phase: make-harness, frame-packets, 5 parallel worker subagents (2 scenes each), **at most 4 running at once** - launch 4, start the 5th when the first reports; size law + presenter zone in every prompt; workers get `references/worker-brief.md`; review each contact sheet AND snapshot the scene's middle yourself (workers' last sheets often show only the seams) | every contact sheet matches its block; full composite snapshot looks right |
| 5 | Audio | (Bed + master already done in phase 3.) SFX cues in film.json on the cue words, from the storyboard blocks. A new bed only on request: `node <engine>/scripts/music-search.mjs "<mood>"` -> `bgm-cut.py` -> re-run `master-audio.py` | voice ~-16 LUFS, bed ~17 dB under |
| 6 | Ship | `<py> <engine>/scripts/fromto-scan.py compositions/s*.html` -> `<py> <engine>/scripts/assemble.py` -> `npx hyperframes check` -> `<py> <engine>/scripts/seam-check.py` + `node <skill>/scripts/seam-diff-all.mjs` -> `node <engine>/scripts/render-final.mjs <slug>-1080p60` (run in the background) -> transcribe the render into a temp dir with `transcribe.py`, then `<py> <skill>/scripts/sync-check.py src/timing/vo-words.json <render words.json>` -> `node <engine>/scripts/encode-web.mjs renders/<name>.mp4 renders/web --name <slug> --poster <t>` | fromto-scan 0, check 0 errors, seams 0.00% outside the presenter box, gpu hardware, sync median ~0.000s, one frame per scene pulled from the RENDER (ffmpeg) matches the harness |

**frame.md checklist (phase 3) - the template holds a worked example's values:** title + duration line; the two
colour-code rows (orange / teal = what they MEAN in this film) + the red row + the "never swap" line; the
fictional-data line; the logo-corner window (from `build-brand.py`'s output); the asset exceptions (a scene that
shows sprites or a capture); the seams table (every cut, canon floor vs STAGE pose); drop the white-plate rule if
no scene pushes through. Script the edits with `<engine>/scripts/patch_exact.py`, never by hand-editing 10 spots.

**Seams with the presenter:** `node <skill>/scripts/seam-diff-all.mjs` after `seam-check.py` - masks the
presenter box on every pair in `snapshots/seams/`; 0.00% outside the box on every cut = pass.

**Sync check** = transcribe the RENDERED mp4, then `sync-check.py` against the source timings. That is the proof
the picture lands on the words - never claim it from reasoning.

**A new take of an already-filmed script** is a fork: retime the old film (cheap) or a new storyboard - ask.

## Files

| Path | What |
|---|---|
| `scripts/setup-check.mjs` | Checks every tool, saves the Python command, prints install commands for what is missing. |
| `scripts/profile.mjs` | `init` / `show` / `path` for the user's brand profile. |
| `scripts/new-explainer.mjs` | Scaffold a film: engine skeleton + KAPE kit + frame.md + worker brief + presenter track + mascot + brand + SFX. |
| `scripts/prep-logo.py`, `scripts/build-brand.py` | Logo cleanup; the corner-logo overlay (`m-brand`) timed from film.json. |
| `scripts/prep-mascot.py` | Normalise a custom character's pose PNGs, write the manifest, fit blinks when faces exist. |
| `scripts/transcribe.py`, `scripts/words.py` | faster-whisper word timings; print every word with its start time (the storyboard's cue sheet). |
| `scripts/master-audio.py` | Voice loudnorm + sidechain-ducked bed + loudness report. |
| `scripts/sync-check.py`, `scripts/seam-diff-all.mjs` | Render audio vs source word timings; seam diffs with the presenter box masked. |
| `scripts/speech-profile.py` | Measure a speaker's style from a long unscripted recording's transcript. |
| `assets/mascot/` | KAPE demo: 9 poses (+6 blink variants), 10 faces, 5 fx, manifest + blink-fit.json. |
| `assets/brand/` | Montserrat 700 + OFL (logo font). The user's logo is copied in per film. |
| `template/` (16:9) / `template-9x16/` | kit.css (film tokens, floor, tiles, packets, phone, parcel, GHL form, n8n canvas, contact card, `.kit-logo`, `.kit-cta`), frame.md, references/ (snippets, scene-starter, worker brief), presenter-track.json, film.json + BRIEF/STORYBOARD worked example. |
| `template/profile/` | Sample profile: brand.example.json, logo.svg, voice.example.md. |

## Hard rules

1. **The speaker's voice is untouchable** - only loudness mastering; the visuals move to the words, never the reverse.
2. **Non-tech first:** everyday picture before the tool, colour = meaning for the whole film, one idea per frame.
3. **Size + zone law** (in frame.md and every worker prompt BEFORE dispatch): headline 60-84px, body >= 36px
   (40 vertical). Landscape: the presenter owns the LEFT third (x 40-620), the stage is x 640-1860 / y 200-1020,
   the corner logo owns x > 1500, y < 150. Vertical: presenter bottom-left (x 20-480, y 1000-1700), stage full
   width above.
4. **Their brand, every film:** s01 opens on the brand logo + the profile's `opener`; `m-brand` corner logo through
   the middle; the last scene is an END CARD - logo big + `.kit-cta` with the profile's `cta`, landing on the
   closing line and held ~2.5-3s after the voice ends (film total = voice end + ~2.8s). Exact markup:
   `references/brand-snippet.html` in the film.
5. **60fps smoothness law** from the engine; no overlapping tweens on one camera property, no camera leg under
   0.6s at t=0.
6. **No "!" in scripts.** No emoji, neon glow, purple-blue gradients, coloured left-border cards.
7. **Music must be theirs to use** - their own licensed file, the HeyGen catalog, or none. Never pull a track off
   YouTube or a random site.
8. renders/, .media/, .hyperframes/ and audio files stay out of git.

## When things go wrong

| Symptom | Cause | Fix |
|---|---|---|
| A script says "run setup-check first" | no `<home>/config.json` | `node <skill>/scripts/setup-check.mjs` |
| new-explainer says "run prep-mascot.py" | custom mascot folder without manifest.json | `<py> <skill>/scripts/prep-mascot.py <home>/profile/mascot` |
| Title shows for a blink before the cut | cut placed before the last word of that line | move the cut to the next sentence's first word |
| Workers' scenes tiny / top-heavy | size law missing from the prompt | message running workers; fix frame.md |
| seam-check FAILs ~1% on every cut | the presenter moves across seams | `seam-diff-all.mjs`: 0.00% outside the box = pass |
| Floor jumps at a seam | a scene's camera not at identity on its first/last frame | one slow leg from identity, home before the end |
| Phone shows the grid through its screen | object passing behind the 3D floor plane | keep it at z >= +150 while it rises |
| Voice clips after a gain lift | plain gain on a hot take | `master-audio.py` (loudnorm), never plain gain |
| `build-presenter.py` dies in ffmpeg on `vo-master.wav` | audio not mastered yet | run `master-audio.py` first (phase 3) |
| Presenter track names a pose that does not exist | custom mascot has fewer poses than KAPE | use only poses in `assets/mascot/manifest.json` |
| Render is ~15x slower than expected | no GPU / software path | render-final prints the gpu mode; close other GPU apps or accept the wait |
| `check` floods `content_overlap` on a deck/stack that deals out | the overlap is the design | `data-layout-allow-overlap` on the TEXT element itself, not its panel |
| A worker ran another worker's generator | all workers share the session scratchpad | worker-brief rule: scratch in `.hyperframes/work/<ids>/` |
