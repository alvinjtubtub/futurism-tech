# Voice profile

Copy to `<profile>/voice.md` and fill it in. Baet reads this before writing any script, so write it as rules a
ghostwriter could follow. Leave a section short rather than guessing - an invented habit sounds worse than none.

## How to fill it

- **Interview (2 minutes):** ask Baet to interview you. It asks five questions: (1) What language do you talk in
  on camera, and do you mix? (2) How do you open a video, word for word? (3) How do you sign off, word for word?
  (4) Which words or phrases do you say all the time, and which would you never say? (5) Fast or slow, punchy or
  flowing - give an example of how you would explain something to a friend.
- **Measured (better):** record 5+ minutes of unscripted talking (explain your job to a friend), then run
  `<py> <skill>/scripts/transcribe.py <recording> <out_dir> --lang <code>` and
  `<py> <skill>/scripts/speech-profile.py <out_dir>/vo-words.json --fillers "your,filler,words"`.
  Copy the wpm, pause lengths, filler rates and recurring phrases below, and set "How measured" to `measured`.

## Language

English

## Visual text rule (set 2026-10-21)

ALL on-screen text in the videos is always in English, even when the narration is Tagalog or
Taglish — headlines, labels, chips, captions, the end card, everything visual. The Tagalog
engagement question in the closing is a SPOKEN (narration) element; if it is ever shown on
screen, it appears in English.

## Pace

wpm: 167 (measured from his 2026-10-20 narration WAV: 465 words in 166.9s)
Rhythm: short bursts, sentence-by-sentence; clear pauses at paragraph breaks

## Opener line

Open with the hook question, spoken as the first line. RULE (set 2026-10-21, for Facebook/TikTok
retention): the hook question must also be DISPLAYED as on-screen text at the very start of the
video (scene 1), so muted scrollers see the question immediately.

## Closer line

Closing structure (set 2026-10-21): first an engaging question or thought in Tagalog that invites
comments (e.g. "Ikaw, ano sa tingin mo? I-comment mo sa baba."), then the sign-off, word for word:
"Follow me for more tech explained. See yah."

## Words I really use

(fillers, restarts, slang, check-ins: e.g. "so", "okay?", "right", "basically")

## Words I never say

(so the script never puts them in your mouth: e.g. "game-changing", "leverage", "folks")

## Tone notes

(e.g. calm and plain, a little dry humour, no hype, never salesy; how you address the viewer)

## How measured

measured (2026-10-20, from the film-1 narration WAV: 465 words in 166.9s = 167 wpm)
