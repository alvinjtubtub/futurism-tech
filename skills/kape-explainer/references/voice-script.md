# Phase 0 - The script, in the speaker's own voice

Load before writing any script this skill narrates. **The speaker's own style lives in the profile's `voice.md`
(`<profile>/voice.md`) - read it before writing a line, and write in that voice.** It holds their language, pace,
opener and closer, the words they really use and the ones they never say. If it is still the unfilled template,
fill it first (interview, or `scripts/speech-profile.py` on a 5+ minute unscripted recording).
Opener and closer lines come from `voice.md`; the brand name and end-card line come from `brand.json`
(`opener`, `cta`). Never put a word in the speaker's mouth that `voice.md` does not support.

## Punctuation is direction (the TTS reads it)

- `...` = a trailing pause before a reveal or while listing (~0.5-1s).
- `?` = questions and check-ins to the viewer.
- **Never `!`** - it makes the take sound excited and salesy. Periods everywhere else, including greetings,
  interjections and the closer.
- Short sentences. A sentence that needs a breath in the middle gets a comma where the speaker would pause.
- No `<break>` tags unless one beat truly needs it - punctuation already carries the pauses, and too many explicit breaks cause artifacts.
- Spell things the way they should be SAID: "N-eight-N" not "n8n", "four-oh-four" not "404", "A-P-I" only if the
  speaker spells it. Keep terms the speaker says in English in English - the model reads them cleaner than a
  translated version.

## Shape for an explainer

1. Opener + topic (one line, the speaker's own opener). 2. The question people ask. 3. ONE everyday analogy a
non-technical viewer already lives (parcel tracking, a rider's text, a restaurant order) - told literally, because
every sentence becomes a picture. 4. "So in short..." one-line contrast. 5. The real-tool example. 6. The
takeaway (which one, when). 7. Closer (the speaker's own closer).
Each paragraph = one scene; write paragraphs so each NAMES the thing the scene will show.

## Word count -> length

Length = words / the speaker's pace (wpm in `voice.md`; assume ~140 if unmeasured) at speed 1.0. ~180-210 words
= ~85-90s at 140 wpm; ~100 words = ~45s. Save the script as `<film>/SCRIPT.md` (sections: Script / Scene map /
TTS notes) and count the Script section only (Node or Python one-liner: split on whitespace between the
`## Script` and `## Scene` headings). A first draft usually lands ~15% long - trim it. Hyphenated spoken numbers
("four-oh-four") count as 1 word but speak as 3, so aim low on number-heavy topics. For a shorter cut drop the
second example, not the analogy.

## Gemini 3.8 Flash TTS (manual - no API key)

The user generates the narration themselves: open Gemini (AI Studio or the Gemini app), pick a 3.8 Flash TTS
voice, paste the script, download the MP3 and hand it over. Speed 1.0 (1.1 to fit a short cut). If a take sounds
robotic or mispronounces a word, regenerate that chunk with a different voice, or respell the word the way it
should be SAID. Encode the voice name + speed in the take's filename (e.g. `_voice-Charon_sp100`) so a good take
can be reproduced.

## Chunking

The user generates long scripts in 2-3 chunks split at paragraph breaks (paste each chunk into the Gemini TTS UI), or one take if the tone holds. Ask for ONE mp3 of
the whole script: join chunks before transcribing so the word timings are one continuous timeline. Re-listen to
the join points - the energy should not reset.

## Language

The speaker's language (English, Taglish, other) is set in `voice.md` and `brand.json` `language`. Pass the
matching `--lang` code to `transcribe.py`. Mixed-language speakers: write the mix exactly as they would say it,
and keep their English terms in English.
