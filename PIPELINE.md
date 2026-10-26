# KAPE Explainer — the full video pipeline

How the Tech Explanasyon explainer films are made, end to end: script → narration →
intake → storyboard → scene builds → quality gates → Mac render → verified upload pack.

Package version: 2026-10-21. This supersedes the 2026-10-20 port ZIP (`kape-explainer-baet.zip`).
New since that port: GSAP is vendored locally (no CDN dependency), the mascot blinks and
talks on **all 9 poses**, the brand badge is **Tech Explanasyon**, and the 2026-10-21
production rules below are baked into the profile.

## Folder map

```
kape-pipeline/
  PIPELINE.md                  ← this file
  skills/
    kape-explainer/            ← film workflow: scaffold, transcribe, master audio, brand/mascot prep
    spatial-film/              ← the engine: assemble, presenter, seam/layout gates, render (template/ included)
    general-video/             ← frame packets for scene crews (frame-packets.mjs)
    hyperframes-animation/     ← scene blueprints the storyboard picks from
    media-use/                 ← media lookup helpers
  profile/
    brand.json                 ← channel brand: Tech Explanasyon, ink #1F2937, accent #2563EB
    voice.md                   ← voice + house rules (pace, closer/opener, visual-text law)
    mascot/                    ← the presenter: 9 poses × 4 states (base/blink/talk/talkblink),
                                 faces/, originals/, fx/, blink-fit.json, manifest.json
```

Not included (recreate locally, see Setup): the Python venv (platform-specific binaries),
`node_modules`, and finished film projects — those are delivered per film as their own ZIPs.

## Setup

- **Node.js** 20+ (24 used in production). HyperFrames runs via `npx hyperframes@0.8.117`.
- **ffmpeg / ffprobe** on PATH.
- **Python 3.12 venv** for transcription only:
  `python3 -m venv ~/.kape-explainer/venv && ~/.kape-explainer/venv/bin/pip install faster-whisper torch av==12.3.0`
  The `av==12.3.0` pin is **critical** — PyAV ≥14 removed a kwarg faster-whisper passes and transcription breaks.
  Everything else in the pipeline runs on the system `python3`.
- Skills expect to live at `~/workspace/custom-skills/` and the profile at `~/.kape-explainer/profile/`
  on Baet's machine; adjust paths in the skill docs if you install them elsewhere.

## The workflow

### Phase 0 — Script (Baet writes, Alvin approves)
One paragraph per scene (9 scenes is the 70s–100s vertical house shape). Rules:
- 9:16 Vertical format (1080x1920) at 60fps.
- Target duration: **70s–100s** (~210–250 words total).
- English-dominant Taglish: English carries the technical explanation; Tagalog carries the
  hook, transitions, emphasis, local color, and the closing question.
- No exclamation marks anywhere. Periods are pacing marks.
- Scene 1 opens with a 5-second hook (displayed on-screen as text and spoken); the final paragraph is: recap → **Tagalog closing
  question** (invites comments) → the sign-off, word for word:
  "Follow me for more tech explained. See yah."

### Phase 1 — Narration (Alvin records, never an API)
Alvin generates the voice himself (ElevenLabs or Gemini TTS Kira or mic) and hands
over the WAV/MP3. The pipeline never synthesizes narration by API.

### Phase 2 — Intake
1. Scaffold: `node skills/kape-explainer/scripts/new-explainer.mjs films/<slug> --name <slug> --format 9x16 --mp3 <file>`
   (copies the profile — brand + full Carla mascot with all talk variants — into the project).
2. Transcribe: `python3 skills/kape-explainer/scripts/transcribe.py films/<slug>/assets/audio/vo.mp3 films/<slug>/src/timing --lang tl`
   → `src/timing/vo-words.json` (word-level timings; the authoritative narration check).
3. Master: `python3 skills/kape-explainer/scripts/master-audio.py --dir films/<slug> --len <probed_dur>`
   → target **−16 LUFS / −1.5 dBTP** at 48kHz stereo.
4. Duration check: enforce 70s–100s duration band.

### Phase 3 — Design law + storyboard (Alvin approves before any build)
- Locked 9:16 layout:
  * **Carla Mascot**: scale `0.30`, feet pinned at `y1540`, home `x245`. Natural blinks (`2.2s–3.4s` cadence) and voice-envelope mouth flap.
  * **Captions**: pinned at `y1500` (growing upward to `y1280` to clear Reels UI).
  * **Headlines**: pinned at `y268` (center `x540`, width `880px`, Poppins 700).
  * **3D Spatial Stage**: `x60–960`, `y470–1180` (with 25px headroom above Carla's head).
  * **Floating Badge**: `Tech Explanasyon` top-center.

### Phase 4 — Scene builds
- Packets: `node skills/general-video/scripts/frame-packets.mjs STORYBOARD.md` → `.hyperframes/frame-packets/`.
- Scenes are built in parallel (max 4 crews), each self-testing with
  `node skills/spatial-film/scripts/test-scene.mjs <scene_id> "<times>"` and its contact sheet.
- Every contact sheet is reviewed by Baet before the scene counts as built.
- GSAP law: `fromTo` only (no `from()`, no yoyo/repeat, no CSS transitions/keyframes).

### Phase 5/6 — Quality gates (all must pass, in this order)
1. `python3 skills/spatial-film/scripts/fromto-scan.py compositions/s*.html` → **0 hits**.
2. `python3 skills/spatial-film/scripts/assemble.py` + `make-harness.py` → clean assembly.
3. `npx hyperframes@0.8.117 check` → **passed**: Layout 0 errors, Motion 0, Contrast WCAG AA.
   (The `clip_media_fit` audio warning and the m-kape file-size warning are benign/expected.)
4. `python3 skills/spatial-film/scripts/seam-check.py`, then the **authoritative masked diff**:
   PIL, % of pixels differing by >8 per channel **outside the presenter box (x 0–660, y 380–1080)**
   on each seam pair → must be **0.00% on every real seam** (the loop seam is ignored).
   The raw seam-check FAIL lines are expected noise — the presenter bobs/blinks/talks across cuts.
5. Full-composite snapshots across the film, eyeballed frame by frame.

**The seam law** (why gate 4 exists): the gate snapshots one frame either side of each cut and
the two sides must match — so every scene **opens and closes on the bare canon floor**
(cream #F6F2EA + perspective dot-grid; all content exits by D−0.08), unless two adjacent
scenes share an identical stage pose. The end card is exempt.

### Phase 7 — Package, Mac render, proof
Per film, delivered to `~/workspace/your_files/kape-films/<slug>/`:
- `<slug>-project.zip` — the project (minus `.hyperframes/`, `snapshots/`, `renders/`) with
  `render-final.mjs` + `render.command` + `RENDER-ON-MAC.md`. Alvin renders on his MacBook M2:
  double-click `render.command` → `npx hyperframes@0.8.117 render --fps 60 --browser-gpu --workers 6`
  (GPU ≈ 15× faster than a CPU render). Needs only Node.js on the Mac.
- `SCRIPT.md`, `CAPTIONS.srt` (from `vo-words.json` segments), `UPLOAD-PACK.md` (title,
  description + chapters, hashtags, pinned comment = the Tagalog closing question, the AI
  disclosure line, YouTube/Facebook/TikTok checklists), `THUMBNAIL.png` (1280×720),
  `TIKTOK-COVER.png` (1080×1920, text in the safe middle band).
- Alvin sends the rendered MP4 back → Baet verifies: ffprobe (H.264 1920×1080@60 + AAC,
  expected duration) + the **word-sync proof** (transcribe the render, align against the
  intake timings; the standard is ~99% words matched, median offset +0.000s) + frame pulls.
- Uploading is always Alvin's step. Nothing is ever published by the pipeline.

## Production rules (set 2026-10-21, in force)
1. Scene 1 **displays the hook question as on-screen text at the very start** (for muted scrollers).
2. Closing = Tagalog engagement question (spoken) → "Follow me for more tech explained. See yah."
3. **All on-screen text is English**, even in Tagalog narration. The closing question is
   spoken in Tagalog; if shown, it appears in English.
4. The floating badge reads **Tech Explanasyon** (profile `brand.json`; films copy it at build time).

## Hard-won lessons (do not relearn these)
- **GSAP must be vendored.** Headless Chromium in this pipeline cannot load GSAP from the
  jsdelivr CDN — compositions silently die and renders come out static. `gsap.min.js` (3.14.2)
  lives in `skills/spatial-film/template/assets/` and `assemble.py`/`make-harness.py` prefer it.
- **prep-mascot.py re-reads poses from `originals/`** and overwrites `poses/` on every run.
  Pose fixes go in `originals/` (profile AND project copies), then re-run prep + blink-fit
  (venv python) + talk-bake. Always eyeball every pose PNG against its name before building
  a presenter track — the original cuts were mislabeled (idle/wave swapped, three rotated).
- **Poppins text-rect artifact:** the layout checker's `content_overlap` uses
  `Range.getClientRects`, and Poppins rects are taller than tight line-heights. Fix geometry
  (line-height ≈1.45 + compensating margin/translate so glyphs move ≤1px). Never paper over
  it with allow-overlap. Intentional layering takes `data-layout-allow-overlap` **on the
  text-owning element itself** — it is not inherited from ancestors.
- **Dash-drawn SVG paths** with round linecaps paint a dot at the path start while fully
  dash-offset. Keep them at opacity 0 until the draw starts.
- **Blink/talk baking:** `blink-fit.py` template-matches the neutral face's eye band per pose
  (bar 0.70); `talk-bake.py <mascot_dir>` pastes the mouth patch through that transform.
  All 9 poses in this profile already have fitted transforms (`mascot/blink-fit.json`,
  including the hand-corrected `think` at x80/y205) and baked variants — do not re-fit
  unless the face sheet changes.
- On Baet's VM, `/tmp` is a 512 MB tmpfs: run snapshot/check commands with
  `TMPDIR=/home/hatch/workspace/.render-tmp`.

## Films made with this pipeline
1. What an AI Agent Actually Does All Day (2026-10-20)
2. Can You Still Trust What You See Online? (+ Taglish redo, 2026-10-21)
3. How AI Generates Text 3x Faster (2026-10-20)
4. How Do Self-Driving Cars Know Where to Go? (2026-10-21)
