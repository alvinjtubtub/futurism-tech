"""Speech style profile from a word-timed transcript (transcribe.py output): pace, pause lengths, restart words,
filler rates, openers, recurring phrases. Works on any language.

usage: <py> <skill>/scripts/speech-profile.py <vo-words.json> [--fillers "so,okay,like,um"] [--top 25]
--fillers: your own filler/connector words (comma separated). Without it, the most frequent short tokens are
listed instead (stopwords included - read them, the ones you recognise as habits are your fillers).
Record 5+ minutes of unscripted talking, run transcribe.py on it, run this, then fill profile/voice.md.
"""
import argparse, json, re, statistics as st
from collections import Counter

ap = argparse.ArgumentParser()
ap.add_argument("words_json")
ap.add_argument("--fillers", default="")
ap.add_argument("--top", type=int, default=25)
a = ap.parse_args()

segs = json.load(open(a.words_json, encoding="utf-8"))
words = [w for s in segs for w in s["words"]]
toks = [re.sub(r"[^\w'-]", "", w["w"].lower()) for w in words]
if len(words) < 2:
    raise SystemExit("not enough words in the transcript")

# pace: words per minute over speaking time only (gaps > 1.5s excluded)
speak, gaps = 0.0, []
for x, y in zip(words, words[1:]):
    g = y["s"] - x["e"]
    if g > 0.15:
        gaps.append((round(g, 2), x["w"].strip(), y["w"].strip()))
    speak += (x["e"] - x["s"]) + (g if g <= 1.5 else 0)
print(f"words={len(words)} speaking_min={speak/60:.1f} wpm={len(words)/(speak/60):.0f}")

g = [x[0] for x in gaps]
bands = {"0.15-0.3": 0, "0.3-0.6": 0, "0.6-1.0": 0, "1.0-2.0": 0, "2.0+": 0}
for v in g:
    k = "0.15-0.3" if v < .3 else "0.3-0.6" if v < .6 else "0.6-1.0" if v < 1 else "1.0-2.0" if v < 2 else "2.0+"
    bands[k] += 1
if g:
    print("pause bands:", bands, f"median={st.median(g):.2f}")

# pause length after punctuation vs mid-sentence
end = [x[0] for x in gaps if x[1][-1:] in ".?!"]
mid = [x[0] for x in gaps if x[1][-1:] not in ".?!,"]
com = [x[0] for x in gaps if x[1][-1:] == ","]
for name, arr in (("after sentence", end), ("after comma", com), ("mid-clause", mid)):
    if arr: print(f"{name}: n={len(arr)} median={st.median(arr):.2f}")

# which words come right before / after a pause (the speaker's "beat" words)
print("before-pause words:", Counter(re.sub(r"[^\w]", "", x[1].lower()) for x in gaps if x[0] >= .4).most_common(20))
print("after-pause words:", Counter(re.sub(r"[^\w]", "", x[2].lower()) for x in gaps if x[0] >= .4).most_common(20))

c = Counter(toks)
if a.fillers.strip():
    fill = [f.strip().lower() for f in a.fillers.split(",") if f.strip()]
    print("fillers per 100 words:", {f: round(c[f] * 100 / len(toks), 2) for f in fill if c[f]})
else:
    print(f"most frequent tokens per 100 words (no --fillers given): "
          f"{ {t: round(n * 100 / len(toks), 2) for t, n in c.most_common(a.top) if t} }")

# sentence openers + recurring 2-3 word phrases
open_ = Counter(" ".join(s["text"].lower().split()[:2]) for s in segs)
print("segment openers:", open_.most_common(a.top))
tri = Counter(zip(toks, toks[1:], toks[2:]))
print("top trigrams:", [(" ".join(k), v) for k, v in tri.most_common(40)])
sl = [len(s["text"].split()) for s in segs]
print(f"segment length words: median={st.median(sl)} mean={st.mean(sl):.1f}")
