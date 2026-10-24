---
workflow: general-video
flow: automation
storyboard: yes
message: "API = you ask. Webhook = they tell you."
destination: social (Reels / TikTok / Shorts)
aspect: 1080x1920
fps: 60
language: English
length: 83s
audience: non-technical viewers - VAs, GHL users, small business owners
angle: concept explainer with a mascot presenter
---

## Intent

An 83-second vertical explainer of API vs webhook, narrated by the creator's own recorded voice (supplied MP3,
untouched). The KAPE mascot is the on-screen presenter, so it reads as the creator explaining. Smooth 3D, a bit
spatial where it makes sense: one CSS-3D camera over a light floor grid, objects living in depth, push-throughs
between scenes. Every idea is shown as an everyday picture first (parcel tracking, rider text) before GHL/n8n, so
someone with zero tech background understands it.

## Assets

- `assets/audio/vo.mp3` - narration, 82.21s, the creator's own recording.
- `src/timing/vo-words.json` - faster-whisper word timings of that MP3 (every reveal keys off these).
- `assets/mascot/` - 9 poses, 10 face states, 5 fx, normalised from the pose PNGs by
  `{{SKILL}}/scripts/prep-mascot.py`.
- `assets/fonts/` - Poppins (KAPE type).
- Reference only: screenshots of the real GHL form UI (GHL look) and the engine's `surfaces/n8n.html` (n8n look).

## Customizations

- 2026-10-05, creator: "smooth 3D and a bit spatial where it make sense. Should be smooth."
- 2026-10-05, creator: "make sure that the timing of the audio is perfect and you're using the correct mascot."
- 2026-10-05, creator: "the motion graphic design video should be 60fps."
- 2026-10-05, creator: "visualize how api and webhook works so anyone can understand even without tech background."

## Notes

- Colour = meaning, never decoration: orange = API (you asking, arrow goes OUT from you), teal = webhook (they
  tell you, arrow comes IN to you), gray = "not yet" replies, red = only the struck "either / or".
- Mock data is fictional: "Kape Coffee Co.", contact "Maria Santos", maria@kapecoffee.co. Never real clients.
- Not a loop: a narrated explainer ends on a held lockup, so the skill's loop rule is waived.
- Bans: no emoji, neon glow, purple-to-blue gradient, colored left-border cards, circular spinners, stock people.
