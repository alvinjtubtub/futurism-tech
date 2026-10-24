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

English | Taglish | other: (state it, and how you mix: e.g. "English with Tagalog connectors, tech terms stay English")

## Pace

wpm: (e.g. 140; leave blank if unmeasured, Baet assumes ~140)
Rhythm: (e.g. "short bursts of ~5 words, then a pause; ~0.8s after a sentence, ~0.3s after a comma")

## Opener line

(word for word, e.g. "Hi everyone, [name] here, and today it's all about [topic].")

## Closer line

(word for word, e.g. "So that's [topic]. Thanks for watching, see you in the next one.")

## Words I really use

(fillers, restarts, slang, check-ins: e.g. "so", "okay?", "right", "basically")

## Words I never say

(so the script never puts them in your mouth: e.g. "game-changing", "leverage", "folks")

## Tone notes

(e.g. calm and plain, a little dry humour, no hype, never salesy; how you address the viewer)

## How measured

interview | measured (date, recording length, tool)
