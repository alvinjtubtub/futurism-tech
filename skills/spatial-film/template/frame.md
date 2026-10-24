# frame.md - {{PRODUCT}} spatial film (design truth)

{{W}}x{{H}}, rendered at **{{FPS}}fps**, {{TOTAL}}s, {{N}} scenes. {{ONE-LINE LOOK, e.g. "Light, crisp UI floating in a soft 3D space."}}
Content per scene lives in each storyboard block; this file is the LOOK and the shared rules. Workers obey it to the letter.

## Tokens (from the product's own stylesheet - never invent colors)

| Role | Value |
|---|---|
| canvas / paper (ground) | `{{#}}` (`.kit-ground` = radial paper-hi -> paper) |
| paper-hi | `{{#}}` |
| card / surface, well | `{{#}}`, `{{#}}` |
| ink / ink-soft / ink-faint | `{{#}}` / `{{#}}` / `{{#}}` (ink-faint must pass AA on paper) |
| accent (ONE accent) | `{{#}}` |
| success | `{{#}}` |
| spring ease (CSS) | `cubic-bezier(0.34, 1.56, 0.64, 1)` |

Bans: emoji, neon glow, purple-to-blue gradient, colored left-border cards, circular spinners (use a shimmer
sweep), stock people, "John Doe", hard cuts, empty frames. Data is fictional ({{MOCK BRAND, e.g. Northwind Dental}}).

## Type

{{FONT}} only, weights {{500 and 700}}, shipped at `assets/fonts/`. Every scene declares, inside its template:

```css
@font-face { font-family: '{{FONT}}'; font-weight: 500; src: url('assets/fonts/{{font}}-500.woff2') format('woff2'); }
@font-face { font-family: '{{FONT}}'; font-weight: 700; src: url('assets/fonts/{{font}}-700.woff2') format('woff2'); }
```

Film labels (chips, names, keycaps): 26-34px/700. Lockup wordmark 120-150px/700. Never below 22px for film-level
text. Text inside product UI uses the UI's real sizes, scaled with `.kit-zoom`.

## Shared kit - `assets/kit.css` + `references/snippets.html`

Every scene links it inside its template: `<link rel="stylesheet" href="assets/kit.css">`. Copy markup from the
snippets file; never restyle a kit class inside a scene. Base components: `.kit-ground`, `.kit-grain`, `.kit-zoom`,
`.kit-chip`, `.kit-cursor`, `.kit-key`, `.kit-ring`, `.kit-ck` (corner ticks), `.kit-win` (browser window).
Product components: {{LIST, e.g. ".kit-pop the real popup (header, tabs, CTA, result block)"}}.

- **Scaling UI:** wrap a component in `<div class="kit-zoom" style="--z:2.6">`. CSS zoom re-lays out at the bigger
  size, so text stays sharp. **Never** scale UI up with `transform: scale(>1)` or by pushing it toward the camera
  past its authored size - 3D layers rasterize at their authored size and go soft. Author each piece at the size
  it has in its closest shot; the camera only ever shrinks it.

## Assets (reference them ROOT-RELATIVE as `assets/...` from a scene - never `../assets/`, lint rejects it)

| File | What | Native px |
|---|---|---|
| `{{logo}}.svg` | the real product mark (vector) | any |
| `captures/{{x}}.png` | {{surface}} (pre-rendered, 2x) | {{WxH}} |

Display a capture at or below its native resolution. Annotation targets on a capture are listed in
`references/snippets.html` (1x coordinates).

## The camera (one rig per scene, same lens everywhere)

```html
<div id="<id>-stage" class="clip" data-start="0" data-duration="<dur>" data-track-index="1"
     style="position:absolute; inset:0; perspective:1866px; perspective-origin:50% 50%;">
  <div id="<id>-drift" class="<id>-layer">          <!-- constant breath only -->
    <div id="<id>-cam" class="<id>-layer">          <!-- authored camera legs -->
      <!-- world objects: position:absolute; left:50%; top:50%; then gsap.set(x,y,z,rotationX/Y) -->
    </div>
  </div>
</div>
```

- 1866px perspective = 35mm lens on a 1920 frame. Never change it.
- Move the camera by tweening `#<id>-cam` (inverse transform: to dolly in, tween `z` positive; to orbit, tween
  `rotationY` with a matching `x`). Set `transformOrigin` on the cam to the point you orbit around. Add a third
  nested layer when an orbit and a dolly must run at the same time.
- **Flattening traps:** `opacity < 1`, `filter`, `overflow:hidden`, `clip-path` or `mix-blend-mode` on any ancestor
  that holds 3D children flattens the 3D. Put those only on leaf elements (an image, a card face).
- Depth of field: far layers get a static `filter: blur(4-10px)` on the leaf. A focus rack may tween blur on 1-2
  leaves only.
- Constant life: `#<id>-drift` carries a slow drift for the whole scene (2-3% scale breathing, 1-2deg orbit,
  `sine.inOut`), under the authored moves so nothing is ever fully still.
- Layered shadow on every floating panel: `box-shadow: var(--float)`.

## Smoothness law ({{FPS}}fps)

1. Animate only `x, y, z, rotationX/Y/Z, scale, opacity` (+ a rare `filter` blur, `clipPath` reveal,
   `strokeDashoffset` draw, one `color` swap). Never `width/height/top/left/margin/box-shadow/font-size`.
2. Eases: `back.out(1.4-1.8)` for things that land; `expo.out` / `power3.out` for arrivals; `power2.inOut` /
   `expo.inOut` / `sine.inOut` for camera legs. **No `none`/linear**, no `steps()`, no `snap`, no `roundProps`,
   no `Math.round` on animated values. Text that must clear before something arrives leaves with `power2.in`
   and is gone BEFORE the arrival starts - `expo.in` keeps it near full opacity to the end and ghosts over the
   newcomer (worked example s07: lockup words over the incoming lock window).
3. Camera legs overlap: start the next leg 0.15-0.3s before the previous ends, so speed never drops to zero and
   back. A camera leg is never shorter than 0.6s.
4. Seekable and deterministic: one paused timeline, `fromTo` with explicit start states, `immediateRender: false`
   on every later `fromTo` of the same property, no `Math.random`, no clocks, no CSS transitions/animations.
5. `will-change: transform` on every moving layer; `force3D: true` in tweens that move layers in 3D.
6. Hits land on the beat grid: {{BPM}} BPM, beat = **{{BEAT}}s**, bar = {{BAR}}s. Each scene starts on a bar or
   half-bar, so beat `n` of a scene is at `n * {{BEAT}}` scene-time. Clicks, ticks, stamps and swaps sit on beats.

## Seams - the exact frames both neighbours render

Each seam is one shared picture. The outgoing scene ends on it; the incoming scene starts on it. Both sides hold
it for the last/first ~0.1s. Lock it with a 2D plate OUTSIDE the camera rig. Never author a fade-to-nothing.
While a plate shows, ONLY the plate shows: the outgoing scene hides its rig once its end plate is opaque, and the
incoming scene keeps its in-rig copy hidden until the plate hands off (`tl.set` plate off + rig copy on at the same
time). A copy under the plate doubles the shadow (worked example s05->s06 seam: 3.49% -> 0.00% after this rule).

| Seam | Time | Shared frame |
|---|---|---|
| {{last}} -> {{first}} (loop) | {{TOTAL}} / 0.000 | {{loop pose, owned by the worker who has both scenes}} |
| {{a}} -> {{b}} | {{t}} | {{full-frame solid #hex (camera inside a button / box)}} |
| {{b}} -> {{c}} | {{t}} | {{exact 2D plate: asset, width, left, top, over .kit-ground}} |

`.kit-grain` sits on top of every scene for its whole duration (static).
