---
format: 1080x1920
duration: 83.2s
fps: 60
message: "API = you ask. Webhook = they tell you."
arc: Hook -> The question -> Parcel setup -> API (you ask) -> Webhook (they tell) -> In short -> GHL + n8n -> Together -> When to use which -> Lockup
audience: non-technical viewers
mode: collaborative
---

# API vs Webhook - KAPE spatial explainer (v3, 16:9) - worked example

## Decisions

- **Format:** 1920x1080 landscape, 60fps, 85.0s (82.21s narration + ~2.8s held end card). Narration is the clock:
  every reveal lands on a word from `src/timing/vo-words.json`. `film.json` runs bpm 60 / 1 beat per bar, so a
  "bar" is one second and scene lengths are plain seconds cut in the pauses between sentences.
- **The spine (the whole lesson in one motif):** a packet that travels along an arrow. Orange packet going OUT
  from Kape = API (you ask). Teal packet coming IN to Kape = webhook (they tell you). Gray packet = the "not yet"
  answer. The same two colours carry from the parcel story into GHL/n8n, so the viewer learns the code once.
- **Presenter:** the KAPE mascot lives on its own full-film overlay (`compositions/m-kape.html`, generated - not a
  worker file). Scenes never draw it and keep content out of its zone (frame x 20-480, y 1000-1700).
- **Camera:** one CSS-3D world per scene, perspective 1866px. The kit floor (perspective grid) gives depth. Cards
  and objects stand in 3D at different z; the camera dollies, cranes and orbits a few degrees; drift breathes.
- **Look:** KAPE whiteboard family (frame.md tokens). Poppins 500/700. Soft long shadows, no glow.
- **Audio:** the creator's MP3 at full level; a soft bed ducked under it; quiet SFX on packets, stamps, the ping.
- **Captions:** off - big 1-3 word labels carry the key words.
- **Bans:** no emoji, neon glow, purple-to-blue gradient, colored left-border cards, circular spinner, stock
  people, slideshow pacing.

## Locked

- 2026-10-06, creator: v3 = landscape 1920x1080 60fps, use the brand logo, end with "{{CTA}}".
- 2026-10-05, creator: "go" on storyboard v1 (defaults kept: 9:16, no captions). v2 = the same plan
  restated as worker blocks (scene-local times). Build contract: `frame.md`, `assets/kit.css` +
  `references/snippets.html`, `assets/mascot/`.

## Layout zones (frame px, 1920x1080 LANDSCAPE; world x/y = frame px minus 960/540 at z 0)

- **Kape zone** x 40-620, y 420-1060: the presenter overlay, LEFT third. Scene content never enters it.
- **Logo corner** x > 1500, y < 150: the {{BRAND_NAME}} corner logo overlay (m-brand, 7.5s-80.3s).
- **Top band** x 640-1460, y 60-190: the headline, centred on x ~1050.
- **Stage** x 640-1860, y 200-1020: the main objects, full height of the right two-thirds.
- v3 (2026-10-06) is a LANDSCAPE PORT of the approved v2 vertical film: same narration, scene cuts, cue words,
  choreography and colour code. Each scene is re-laid out for the stage above; nothing else changes unless a
  block below says so (frames 1 and 10 change - brand logo + CTA).

## Frame 1 - Hook

- scene: Two title tiles rise from the floor: API, a small vs, WEBHOOK, landing on the words.
- duration: 7.3s
- poster: 6.3
- transition_in: canon floor (film start)
- status: planned
- src: compositions/s01-hook.html
- blueprint: titlecard-reveal (Adapt)
- rules: spring-pop-entrance, 3d-text-depth-layers
- confirmed sketch: storyboard.html#frame-01

World: `.kit-tile.api` at world (0, -360, 0); `.kit-tile.vs` at (0, -150, 60); `.kit-tile.wh` at (0, 70, 0) - a
stacked title in the stage, slight rotationX 8deg so their tops catch the light. A `.kit-shadow` under each on the
floor. In the top band: the brand logo (`.kit-logo`, --h ~84px, markup from references/brand-snippet.html) + "{{OPENER}}" (kit-kicker) - the film opens on the brand. Tiles stack in the centre-right (x ~1100), clear of the Kape zone.
Seam out (t = 7.3): canon floor.

Scene 1 (0.00-1.20): camera cranes down - cam from rotationX -10, y -240 to identity over 1.6s power2.inOut. Kicker
fades up at 0.6 (expo.out 0.6s).
Scene 2 (4.46-5.90): API tile rises from z -500 / y +260 below the floor line to its mark on "API" (4.56), back.out(1.6)
0.7s; vs pops on "versus" (5.24) scale 0.4 -> 1 back.out(2) 0.4s; WEBHOOK rises on "webhook" (5.70), 0.7s.
Scene 3 (6.80-7.25): on "So" (6.86) the tiles fly past the camera (z +700, power2.in) and fade, kicker leaves;
the cam stays at identity, so the scene ends exactly on the canon floor at 7.3. The title holds 5.70-6.80.

## Frame 2 - The question

- scene: Two apps, You and Other app, stream little data cubes both ways - why people mix them up.
- duration: 6.2s
- poster: 5.0
- transition_in: canon floor
- status: planned
- src: compositions/s02-question.html
- blueprint: comparison-split (Adapt)
- rules: svg-path-draw, spring-pop-entrance
- confirmed sketch: storyboard.html#frame-02

World: `.kit-node.you` "You" at world (-230, -180, 0); `.kit-node` "Other app" at (230, -180, -120). Two dashed
lanes between them (`.kit-arrow` without arrowheads, ink-faint, dasharray). Caption top band: "Same thing?"
appears at 1.58 ("So what"). A phone (`.kit-phone`, world (240, -60, -700), screen pure white) waits far back
centre-right, out of focus (blur 6px on the phone leaf) - it is the push-through target.
Seam in: canon floor. Seam out (t = 6.2): FULL-FRAME WHITE #FFFFFF (the camera is inside the phone screen).

Scene 1 (0.10-1.10): nodes rise in, You first then Other app 0.15s later, back.out(1.6).
Scene 2 (1.58-2.40): caption "Same thing?" in the top band (kit-caption), expo.out.
Scene 3 (4.30-5.30): on "sending" (4.30) cubes stream along both lanes - 3 small `.kit-packet` (scale .55):
reply-gray from You->app and back, never orange/teal yet (colour meaning starts in frame 4). "data" (5.02) the
lanes pulse once.
Scene 4 (5.34-6.20): on "right?" (5.34) the camera flies to the phone: cam leg to bring the phone screen to fill the
frame (z dolly + x pan, expo.inOut 0.8s); nodes/caption leave power2.in by 5.8; a full-frame white plate (outside
the rig) is opaque from 6.08 to 6.2.

## Frame 3 - The parcel

- scene: Out of the white phone screen: an order card, then a real 3D parcel that starts riding the route.
- duration: 5.1s
- poster: 4.4
- transition_in: full-frame white #FFFFFF (push-through)
- status: planned
- src: compositions/s03-parcel.html
- blueprint: device-surface-showcase (Adapt)
- rules: orbit-3d-entry, svg-path-draw
- confirmed sketch: storyboard.html#frame-03

World: the camera pulls back out of the white to reveal `.kit-phone` (zoom it to fit ~ 470x960 on screen) at world
(130, -140, 0), rotationY -10. On its screen (2D): an order card "Order #KAPE-0912" + "On its way" status row, and
a mini map: Warehouse pin -> dotted route -> Your home pin. Beside the phone, floating at world (-250, -420, 120):
the 3D `.kit-parcel` (--s 150px), slowly rotating.
Seam in: white plate opaque 0-0.12, then fades as the cam pulls back. Seam out (t = 5.1): canon floor.

Scene 1 (0.00-1.00): pull back out of the white (cam z from +1500 to 0, expo.out 1.0s; white plate 1 -> 0 over 0.25s from 0.12).
Scene 2 (1.24-1.90): on "orders" (1.24) the order card pops on the screen (back.out(1.6)).
Scene 3 (3.00-3.70): on "parcel" (3.00) the parcel drops in from above with a spring and lands on its mark,
rotationY tween continues all scene (sine.inOut, ~30deg).
Scene 4 (4.10-4.70): on "on its way" (4.10) the route draws on the phone and a dot starts along it; parcel nudges
right as if travelling.
Scene 5 (4.60-5.05): phone and parcel exit (z -300 + opacity, power2.in), gone by 5.0. Canon floor at 5.1.

## Frame 4 - API: you keep asking

- scene: Kape keeps asking the courier "Is it there yet?" - orange asks out, gray "Not yet" comes back.
- duration: 12.6s
- poster: 7.6
- transition_in: canon floor
- status: planned
- src: compositions/s04-api.html
- blueprint: fixed-anchor-cycle (Adapt)
- rules: svg-path-draw, press-release-spring
- confirmed sketch: storyboard.html#frame-04

World (the STAGE shared with frame 5 - same worker, identical positions): Kape's phone `.kit-phone` small (zoom to
~260x530 on screen) at frame centre ~ (430, 820) i.e. world (-110, -140, 60), screen shows a "Track" button
(orange pill, white "Track") under the order line. `.kit-node` "Courier" at world (290, -420, -160). The route
(dotted, ink-faint) runs across the floor between them at world y +40, the 3D `.kit-parcel` (--s 110px) sits on
it at world (90, 30, 0). `.kit-clock` at world (-330, -560, 40) in the upper left.
Top band: `.kit-label` "API" (orange span) at y 250 + kicker "YOU ARE THE ONE ASKING" under it (appears at 8.28).
Seam in: canon floor. Seam out (t = 12.6): the STAGE pose - phone, Courier node, route, parcel at their marks, cam
and drift at identity; label/kicker/bubbles/clock/chip gone. Frame 5 opens on exactly this pose.

Scene 1 (0.10-1.20): stage builds - phone, Courier, route draws, parcel lands; "API" label lands on "API" (0.36).
Scene 2 (2.20-4.20): "again and again" (2.20) the clock pops in and its minute hand starts turning (keeps turning until
11.0); "tracking" (3.78) Track button glows a little (scale pulse, no glow effect).
Scene 3 (4.74-7.80): ask 1 - Track press (press-release) at 4.74, orange packet + `.kit-bubble.api` "Is it there
yet?" fly phone -> Courier (arc, 0.75s power2.inOut); reply at 5.64: gray packet + `.kit-bubble.reply` "Not yet."
fly back (0.7s). Ask 2: 6.46 / reply "Still not yet." 7.38. Chip "Checks: 2" (kit-chip api) ticks 1 -> 2 at 7.38,
lower right.
Scene 4 (8.28-11.20): "You are the one asking" (8.28): kicker under API; arrows label themselves: small chips
"Question (request)" orange above the out-path, "Answer (response)" gray under the back-path at 8.82. "only answers"
(10.08) Courier node dims to 60% then back to 100% at "asked" (11.12) to show it only answers when asked.
Scene 5 (11.98-12.50): "okay?" (11.98) - label, kicker, chips, clock, bubbles leave power2.in by 12.45; the stage
stays.

## Frame 5 - Webhook: they tell you

- scene: Kape stops asking; the parcel arrives and the rider's message comes IN on its own - teal.
- duration: 10.1s
- poster: 4.6
- transition_in: shared stage from frame 4
- status: planned
- src: compositions/s05-webhook.html
- blueprint: device-surface-showcase (Adapt)
- rules: svg-path-draw, spring-pop-entrance
- confirmed sketch: storyboard.html#frame-05

World: opens on frame 4's exact STAGE pose. Top band: `.kit-label` "WEBHOOK" (teal span) + later kicker "THEY TELL
YOU". A `.kit-notif` "Rider / Hi, I am outside now." lands lower right (frame x ~520-900, y ~1080).
Seam in: frame 4's stage pose. Seam out (t = 10.1): canon floor.

Scene 1 (0.58-1.40): "webhook" (0.58) WEBHOOK label lands; the Track button greys to ink-faint.
Scene 2 (2.02-3.20): "rider" (2.02) parcel slides along the route to the house end (a `.kit-node`-style small
house icon chip appears at the route end, world (300, 40, 0)), lands with a spring.
Scene 3 (2.98-4.40): "texts" (2.98) a teal packet travels Courier -> phone (arc 0.8s); "Hi" (4.34) the
notification lands lower right (back.out 1.6, ping) and the phone screen shows the same banner.
Scene 4 (6.22-7.20): "You no longer need to ask" (6.22) the Track button is struck through and the camera
eases in 6% (cam z +120, power2.inOut 1.2s).
Scene 5 (8.26-9.20): "tell you" (8.26) kicker "THEY TELL YOU"; "when something happens" (8.80) a chip "Delivered"
(kit-chip wh, check icon) pulses on the Courier node - the event that fired the message.
Scene 6 (9.50-10.05): everything leaves power2.in, cam back to identity; canon floor at 10.1.

## Frame 6 - In short

- scene: Two lanes in depth: API arrow You -> Them (orange), webhook arrow Them -> You (teal).
- duration: 6.0s
- poster: 5.2
- transition_in: canon floor
- status: planned
- src: compositions/s06-short.html
- blueprint: comparison-split (Adapt)
- rules: svg-path-draw, split-tilt-cards
- confirmed sketch: storyboard.html#frame-06

World: two lane cards (white `.kit-card`, 900x300) stacked: lane A at world (0, -330, 0), lane B at (0, 30, -80),
both tilted rotationX 14deg like slabs on the floor. Each lane: "You" mini node (Kape face) left, "Them" mini node
(app icon) right, an arrow between. Lane A arrow orange left->right; lane B teal right->left. Labels on the lanes:
"API: you ask" (orange span), "Webhook: they tell you" (teal span), 40px/700.
Kicker top band "IN SHORT" at 0.58 ("in short").
Seam in/out: canon floor.

Scene 1 (0.10-1.20): camera pulls back and tilts (cam from z +300, rotationX -6 to identity, power2.inOut 1.2s);
both lane slabs rise in, staggered 0.15s.
Scene 2 (1.56-2.80): "API" (1.56) orange arrow draws left->right (svg-path-draw 0.6s) with an orange packet riding
it; label lands at 2.32.
Scene 3 (3.92-5.20): "Webhook" (3.92) teal arrow draws right->left with a teal packet; label at 4.54.
Scene 4 (5.45-5.95): exit power2.in; canon floor at 6.0.

## Frame 7 - In GHL

- scene: A GHL form submit fires a webhook to n8n instantly; n8n then calls GHL's API to fetch the full contact.
- duration: 15.0s
- poster: 11.8
- transition_in: canon floor
- status: planned
- src: compositions/s07-ghl.html
- blueprint: cursor-ui-demo (Adapt)
- rules: cursor-click-ripple, svg-path-draw
- confirmed sketch: storyboard.html#frame-07

World: `.kit-ghl-form` (zoom ~1.25) at world (-150, -420, 0) rotationY 8; `.kit-n8n` canvas (zoom ~1.2) at world
(120, 10, -60) rotationY -8, lower; a chip "GHL" over the form, "n8n" over the canvas (kit-chip). Teal path from the
form's Submit to the n8n Webhook node; orange path from the HTTP Request node back up to the form card; the
`.kit-contact` card lands lower right (frame x ~520-940, y ~1040-1420) at the end.
Top band: kicker "IN GHL" (0.96), later `.kit-label.sm` "API: get the details" (orange span) at 13.46.
Seam in: canon floor. Seam out (t = 15.0): the STAGE pose for frame 8 - form and n8n canvas at their marks, cam
identity; cursor, contact card, labels gone. Frame 8 opens on exactly this pose.

Scene 1 (0.10-1.60): "GHL" (0.96) form card flies in (orbit-3d-entry style, back.out), kicker lands.
Scene 2 (2.70-3.60): "submits" (2.70) the cursor glides to Submit and clicks (cursor-click-ripple, click SFX), the
button presses.
Scene 3 (4.50-6.20): "fires" (4.50) teal packet shoots from Submit down to the n8n Webhook node (0.6s, expo.out);
"N8N" (5.90) the n8n canvas has risen in (from 4.3) and its Webhook node outlines teal.
Scene 4 (7.18-7.80): "instant" (7.18) a tiny `.kit-chip.wh` "0.2s" stamp pops beside the Webhook node.
Scene 5 (8.48-11.60): "you need more info" (8.48) the HTTP Request node outlines orange and an orange
packet travels up to the form card (1.0s); "details" (10.92) the contact card flies out of the form card down to
the lower right and its rows fill in one by one by "contact" (11.52).
Scene 6 (13.46-14.20): "API" (13.46) label "API: get the details" lands in the top band (kicker leaves first).
Scene 7 (14.50-14.95): cursor, contact card, chips and label leave power2.in; the stage stays.

## Frame 8 - Together

- scene: The teal and orange paths close into one loop between GHL and n8n - not either/or, AND.
- duration: 4.5s
- poster: 4.0
- transition_in: shared stage from frame 7
- status: planned
- src: compositions/s08-together.html
- blueprint: constellation-hub (Adapt)
- rules: svg-path-draw, kinetic-beat-slam
- confirmed sketch: storyboard.html#frame-08

World: opens on frame 7's stage pose. A loop of two arcs (teal down-right, orange up-left) between the form and the
n8n canvas. Top band: "either / or" in ink, 84px.
Seam in: frame 7's stage. Seam out (t = 4.5): canon floor.

Scene 1 (0.40-1.80): "together" (1.30) both arcs draw at once into one loop, a teal and an orange packet chase
each other round it; the camera orbits 6deg around the pair (cam rotationY, power2.inOut 1.6s).
Scene 2 (3.42-4.10): "either" (3.42) "either / or" lands; on "or" (3.76) "or" gets a red strike (scaleX 0 -> 1
line) and the word swaps to orange "AND" (kinetic-beat-slam).
Scene 3 (4.10-4.45): everything leaves power2.in fast; canon floor at 4.5.

## Frame 9 - When to use which

- scene: Two cards stand up: react right away = WEBHOOK; get or update data anytime = API.
- duration: 10.4s
- poster: 9.8
- transition_in: canon floor
- status: planned
- src: compositions/s09-when.html
- blueprint: comparison-split (Adapt)
- rules: split-tilt-cards, kinetic-beat-slam
- confirmed sketch: storyboard.html#frame-09

World: two `.kit-card` 820x330 stacked: card 1 at world (40, -330, 0), card 2 at world (40, 60, -60), each with a
big icon tile left (bolt in teal well / refresh in orange well) and text right. Card 1 text "React right away when
something happens" (44px/700). Card 2 text "Get or update data any time" (40px/700, 2 lines). Stamps: `.kit-stamp.wh`
"WEBHOOK" over card 1, `.kit-stamp.api` "API" over card 2, rotated -6deg, at the card's right end.
Kicker top band "WHEN TO USE WHICH?" at 0.72.
Seam in/out: canon floor.

Scene 1 (0.38-1.00): kicker lands on "when" / "which?" (0.72).
Scene 2 (1.64-4.80): card 1 stands up from flat on the floor (rotationX 80 -> 0, back.out(1.4) 0.8s) from "If you
want" (1.64); text writes in by "react" (2.40); "webhook" (4.26) the WEBHOOK stamp slams on (scale 1.6 -> 1,
back.out(2), pop SFX).
Scene 3 (5.32-9.80): card 2 stands up from "If you" (5.32), text in by "update" (6.92); "API" (9.30) the API
stamp slams on.
Scene 4 (9.90-10.35): exit power2.in; canon floor at 10.4.

## Frame 10 - End card: {{CTA}}

- scene: The API / vs / WEBHOOK tiles return as the title, then clear for the brand logo and a "{{CTA}}" CTA that holds.
- duration: 7.8s
- poster: 7.0
- transition_in: canon floor
- status: planned
- src: compositions/s10-close.html
- blueprint: logo-assemble-lockup (Adapt)
- rules: spring-pop-entrance, 3d-text-depth-layers
- confirmed sketch: storyboard.html#frame-10

World: the same three tiles as frame 1 (same classes and marks, centre-right). Then the end card in the centre-right
(x ~1150): the brand logo big (`.kit-logo`, --h ~170px, markup from references/brand-snippet.html) with the `.kit-cta` "{{CTA}}" pill under
it. Kape (overlay) waves at "Alright" then gestures toward the CTA at 82.35 global (5.15 local).
Seam in: canon floor. End: held still from ~5.6 to 7.8 (only drift) - the end card is the last frame.

Scene 1 (1.48-2.70): "API" (1.48) API tile rises; "vs" (2.04) pops; "Webhook" (2.34) WEBHOOK rises.
Scene 2 (3.10-3.60): on "Alright" (3.28) the tiles lift away (z -400, power2.in), gone by 3.6.
Scene 3 (3.60-4.60): the brand logo assembles - image pops (back.out 2) at 3.7, wordmark wipes in (clipPath
inset 0.5s expo.out) by "good luck" (3.84).
Scene 4 (4.44-5.20): on "Thank you" (4.44) the "{{CTA}}" pill rises in (back.out 1.6) and settles.
Scene 5 (5.20-7.80): hold - only drift; the pill breathes once (scale 1 -> 1.03 -> 1, sine.inOut 1.6s).
