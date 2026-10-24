# frame.md - {{FILM_NAME}} spatial explainer (design truth)

1080x1920 vertical, rendered at **60fps**, 83.2s, 10 scenes + a full-film presenter overlay. Light warm paper,
a perspective KAPE grid floor, chunky friendly cards and packets floating in soft 3D, colour that means something.
Content per scene lives in each storyboard block; this file is the LOOK and the shared rules. Workers obey it to the letter.

## Tokens (KAPE whiteboard family - `assets/kit.css` :root; never invent colors)

| Role | Value |
|---|---|
| canvas / paper (ground) | `#F6F2EA` (`.kit-ground` = radial paper-hi -> paper -> paper-lo) |
| paper-hi / paper-lo | `#FCFAF6` / `#ECE5D8` |
| card / surface, well | `#FFFFFF`, `#F3EEE5` |
| ink / ink-soft / ink-faint | `#0B1E3F` / `#33435F` / `#5B6478` (ink-faint is 5.4:1 on paper - AA) |
| API (fill / text) | `#FF7A1A` / `#B8500A` - always "you ask", arrow OUT from Kape |
| Webhook (fill / text) | `#0F9F8F` / `#0A7468` - always "they tell you", arrow IN to Kape |
| reply gray | `#8B93A7` (text `#6B7387`) - the "not yet" answer |
| bad red | `#E5484D` - ONLY the struck "or" in frame 8 |
| floor grid | mint `#94C2AD` plus marks (kit-floor) |
| spring ease (CSS) | `cubic-bezier(0.34, 1.56, 0.64, 1)` |

Colour = meaning. Never use orange or teal decoratively; never put orange on a webhook thing or teal on an API thing.
Bans: emoji, neon glow, purple-to-blue gradient, colored left-border cards, circular spinners (use a shimmer
sweep), stock people, "John Doe", hard cuts, empty frames. Data is fictional (Kape Coffee Co., Maria Santos,
maria@kapecoffee.co, +1 555 0142, Order #KAPE-0912).

## Type

Poppins only, weights 500 and 700, shipped at `assets/fonts/`. Every scene declares, inside its template:

```css
@font-face { font-family: 'Poppins'; font-weight: 500; src: url('assets/fonts/poppins-500.woff2') format('woff2'); }
@font-face { font-family: 'Poppins'; font-weight: 700; src: url('assets/fonts/poppins-700.woff2') format('woff2'); }
```

Vertical phone video: film labels are BIG. Every scene's top band carries a real headline (`.kit-label` 84px or
`.kit-label.sm` 60px) - a 28px kicker alone is too small to be the title. Body text and labels >= 40px; node / UI
micro-labels >= 30px; caption 46px/700; bubbles 38px+; tiles 128px/700. Main objects use the full width (frame x
60-1020) and the height down to frame y ~1040 (first wave shipped scenes at ~33px text in the top 45% of the frame). Text in rebuilt UI (GHL form, n8n, phone
screens) uses the UI's real sizes, scaled up with `.kit-zoom` so it reads on a phone (effective >= 20px).

## Shared kit - `assets/kit.css` + `references/snippets.html`

Every scene links it inside its template: `<link rel="stylesheet" href="assets/kit.css">`. Copy markup from the
snippets file; never restyle a kit class inside a scene. Components: `.kit-ground`, `.kit-grain`, `.kit-floor`,
`.kit-shadow`, `.kit-zoom`, `.kit-chip(.api/.wh/.reply)`, `.kit-cursor`, `.kit-ring`, `.kit-shimmer`,
`.kit-tile(.api/.vs/.wh)`, `.kit-kicker`, `.kit-label(.sm)`, `.kit-caption`, `.kit-card`, `.kit-node(.you)`,
`.kit-packet(.api/.wh/.reply)`, `.kit-bubble(.api/.wh/.reply)`, `.kit-arrow(.api/.wh/.reply)`, `.kit-phone` +
`.kit-phone-screen`, `.kit-notif`, `.kit-parcel` (true 3D cube), `.kit-clock`, `.kit-stamp(.api/.wh/.bad)`,
`.kit-ico` (Lucide paths in snippets), `.kit-ghl-form`, `.kit-n8n` + `.kit-n8n-node`, `.kit-contact`.

- **Scaling UI:** wrap a component in `<div class="kit-zoom" style="--z:1.4">`. CSS zoom re-lays out at the bigger
  size, so text stays sharp. **Never** scale UI up with `transform: scale(>1)` or by pushing it toward the camera
  past its authored size - 3D layers rasterize at their authored size and go soft. Author each piece at the size
  it has in its closest shot; the camera only ever shrinks it.

## Layout - vertical frame zones (frame px)

- **Top band** y 170-430: the scene's label / kicker / caption.
- **Stage** y 440-1000, 60px side margins: the main objects.
- **Lower right** x 500-950, y 1000-1500: secondary objects.
- **Kape zone** x 20-480, y 1000-1700: the presenter overlay (`compositions/m-kape.html`, not yours). Never put
  scene content there and never draw a mascot. Things "at Kape" (Kape's phone, the You node) sit at the zone's
  top-right edge, around frame (430-480, 820-950).
- Nothing below y 1720, no text at x > 950 below y 1300 (Reels UI).

## Branding ({{BRAND_NAME}}) - colours and logo come from `brand.json`, never from this file

- s01 opens on the brand-snippet logo (top band) + "{{OPENER}}" as a kicker: the film opens on the brand.
- Corner logo: the `m-brand` overlay (built by `build-brand.py`) shows it top-centre (above the Reels UI) for the middle of the film.
- End card (last scene): the logo big (`.kit-logo`, --h ~170px) with the `.kit-cta` "{{CTA}}" pill under it, centre-right, held.
- Copy the exact markup from `references/brand-snippet.html`; never hand-write the logo or restyle `.kit-logo` / `.kit-cta`.
  They read only `--brand-ink`, `--brand-accent`, `--brand-accent-dark` (appended to `assets/kit.css` for this film).
- The presenter is {{PRESENTER}} (overlay `m-kape`); scenes never draw it.

## Assets (reference them ROOT-RELATIVE as `assets/...` from a scene - never `../assets/`, lint rejects it)

| File | What | Native px |
|---|---|---|
| `mascot/faces/neutral.png` | Kape's face (the "You" node avatar only) | 480x588 |
| `mascot/fx/*.png` | steam, sparkle-burst, coffee-ring, question, confetti (optional accents) | ~450-550 |
| `fonts/poppins-500.woff2`, `-700` | the only typeface | - |

Mascot poses are the overlay's - scenes do not use `mascot/poses/`.

## The camera (one rig per scene, same lens everywhere)

```html
<div id="<id>-stage" class="clip" data-start="0" data-duration="<dur>" data-track-index="1"
     style="position:absolute; inset:0; perspective:1866px; perspective-origin:50% 50%;">
  <div id="<id>-drift" class="<id>-layer">          <!-- constant breath only -->
    <div id="<id>-cam" class="<id>-layer">          <!-- authored camera legs -->
      <div class="kit-floor"></div>                 <!-- always first, never tweened -->
      <!-- world objects: position:absolute; left:50%; top:50%; then gsap.set(x,y,z,rotationX/Y) -->
    </div>
  </div>
</div>
```

- 1866px perspective. Never change it. World x/y 0 = frame centre (540, 960).
- Move the camera by tweening `#<id>-cam` (inverse transform: to dolly in, tween `z` positive; to orbit, tween
  `rotationY` with a matching `x`). Set `transformOrigin` on the cam to the point you orbit around. Add a third
  nested layer when an orbit and a dolly must run at the same time.
- **Flattening traps:** `opacity < 1`, `filter`, `overflow:hidden`, `clip-path` or `mix-blend-mode` on any ancestor
  that holds 3D children flattens the 3D. Put those only on leaf elements (a card face, an image, a label). The
  `.kit-parcel` cube needs every ancestor up to the cam to keep `transform-style: preserve-3d` - fade the cube by
  fading its six faces, never its wrapper.
- Depth of field: far layers get a static `filter: blur(4-8px)` on the leaf. A focus rack may tween blur on 1-2
  leaves only.
- Constant life: `#<id>-drift` breathes (scale 1 -> 1.02 -> 1, rotationY 0 -> 1.2 -> 0, sine.inOut) and is at
  IDENTITY at t = 0 and t = dur (scene-starter does this). Kape's overlay is always moving too, so no frame is dead.
- Layered shadow on every floating panel: `box-shadow: var(--float)`; `.kit-shadow` under things over the floor.

## Smoothness law (60fps)

1. Animate only `x, y, z, rotationX/Y/Z, scale, opacity` (+ a rare `filter` blur, `clipPath` reveal,
   `strokeDashoffset` draw, one `color` swap). Never `width/height/top/left/margin/box-shadow/font-size`.
2. Eases: `back.out(1.4-1.8)` for things that land; `expo.out` / `power3.out` for arrivals; `power2.inOut` /
   `expo.inOut` / `sine.inOut` for camera legs and packet flights. **No `none`/linear**, no `steps()`, no `snap`,
   no `roundProps`, no `Math.round` on animated values. Text that must clear before something arrives leaves with
   `power2.in` and is gone BEFORE the arrival starts.
3. Camera legs overlap: start the next leg 0.15-0.3s before the previous ends. A camera leg is never shorter than 0.6s.
4. Seekable and deterministic: one paused timeline, `fromTo` with explicit start states, `immediateRender: false`
   on every later `fromTo` of the same property, no `Math.random`, no clocks, no CSS transitions/animations.
5. `will-change: transform` on every moving layer; `force3D: true` in tweens that move layers in 3D.
6. **Narration is the clock.** Every reveal lands on its cue word: the storyboard block gives scene-local seconds
   (global word time minus the scene start). Arrivals START ~0.1s before the word and land on it. Nothing named
   appears before its word. Counter-ticks (e.g. a number changing) use one `tl.set` swap per step.

## Seams - the exact frames both neighbours render

| Seam | Time (global) | Shared frame |
|---|---|---|
| film start | 0.0 | canon floor |
| s01-hook -> s02-question | 7.3 | canon floor |
| s02-question -> s03-parcel | 13.5 | full-frame white `#FFFFFF` plate outside the rig (camera inside the phone screen) |
| s03-parcel -> s04-api | 18.6 | canon floor |
| s04-api -> s05-webhook | 31.2 | the API/webhook STAGE pose (same worker defines it once, identical values both files) |
| s05-webhook -> s06-short | 41.3 | canon floor |
| s06-short -> s07-ghl | 47.3 | canon floor |
| s07-ghl -> s08-together | 62.3 | the GHL/n8n STAGE pose (same worker, identical values both files) |
| s08-together -> s09-when | 66.8 | canon floor |
| s09-when -> s10-close | 77.2 | canon floor |
| film end | 83.2 | the held lockup (not a loop) |

- **Canon floor** = `.kit-ground` + `.kit-floor` with drift and cam at identity and NOTHING else visible. Exits
  finish by dur - 0.08; arrivals start at >= 0.08. Kape's overlay keeps the frame alive across it.
- **White plate** = a full-frame `#FFFFFF` div outside the rig, opaque for the last 0.12s of s02 and the first
  0.12s of s03, and while it is opaque the rig under it is hidden.
- **Stage pose seams** = both files gsap.set the same objects to the same values with cam/drift at identity; the
  outgoing scene's extras are gone by dur - 0.08 and the incoming scene adds nothing before 0.08.

`.kit-grain` sits on top of every scene for its whole duration (static).
