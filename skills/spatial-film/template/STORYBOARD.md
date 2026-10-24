---
format: 1920x1080
duration: 60s
message: "{{one sentence the film proves}}"
arc: {{Hook -> Proof A -> Proof B -> ... -> Lockup -> loop}}
audience: {{who}}
mode: collaborative
---

# {{PRODUCT}} - spatial product film (v1)

## Decisions

- **Message / audience / arc:** {{...}}
- **Format:** 1920x1080, 60fps, {{N}}s. No voiceover. Music bed (~{{BPM}} BPM, sourced, native tempo) + UI SFX. Labels 2-5 words.
- **Beat grid (fixed):** {{BPM}} BPM, beat {{BEAT}}s, bar {{BAR}}s. Scene seams sit on bar or half-bar lines.
- **The spine:** {{one visual motif carried through every scene, e.g. the product's corner ticks -> scan frame -> crop handles -> lockup}}. Second thread: {{e.g. the capture is a physical sheet the camera follows}}.
- **Camera:** one CSS-3D world per scene, one rig, perspective 1866px (~35mm). Every seam is a camera move (dolly, orbit, crane, push-through). Constant 2-3% drift.
- **Brand (from source, not memory):** {{tokens from the product's stylesheet}}. {{font}} only. Real mark `{{path}}`.
- **Truthfulness:** product UI rebuilt from its own HTML/CSS. Third-party canvases rebuilt from the user's real captures with fictional data. Only features the product really has.
- **Bans:** no emoji, no neon glow, no purple-to-blue gradient, no colored left-border cards, no circular spinner (shimmer), no stock people, no "John Doe". No slideshow, no screensaver motion. No hard cuts, no empty frame.
- **Held frame:** the lockup holds still {{1.5}}s.
- **Loop:** frame 0 and the last frame are the same pose: {{pose}}.

## Locked

- {{date}}, {{who}}: "go" on storyboard v{{n}}. Build contract: `frame.md`, `assets/kit.css` + `references/snippets.html`, `assets/captures/*.png`. Times below are SCENE-LOCAL seconds. Beat n = n x {{BEAT}}s.

## Frame 1 - {{title}}

- scene: {{one line: what happens, start to end}}
- duration: {{bars x BAR}}s
- poster: {{t}}
- transition_in: loop seam (frame 0 = last frame of the final scene)
- status: planned
- src: compositions/s01-{{slug}}.html
- blueprint: {{ONE id from hyperframes-animation/blueprints}} (Adapt)
- rules: {{2-3 rule ids max - the packet builder inlines every rule a block mentions and caps at 48KB}}
- confirmed sketch: storyboard.html#frame-01

World: {{every object with its size, world position (x, y, z, rotation) and the asset/snippet it uses}}.
**Seam out (t = end):** {{exact shared frame, matching frame.md's seam table}}.

Scene 1 (0.00-{{t}}): {{beat-by-beat: what moves, from -> to, ease, duration, and which beat each hit lands on}}.
Scene 2 ({{t}}-{{t}}): {{...}}
