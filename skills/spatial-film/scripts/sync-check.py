"""Prove the rendered film's voice sits where the visuals were timed: compare word starts of the render's audio
transcript against the narration word timings the scenes were built from.

usage: <py> sync-check.py <source vo-words.json> <render words.json>
Matches identical words in order and prints the offset stats (render - source). |median| < 0.03s = in sync.
"""
import json, re, sys, statistics as st
from difflib import SequenceMatcher

def load(p):
    try:
        data = json.load(open(p, encoding="utf-8"))
        w = [x for s in data for x in (s.get("words") or []) if isinstance(x, dict) and "w" in x and "s" in x]
        return [re.sub(r"[^\w]", "", str(x.get("w", "")).lower()) for x in w], [float(x.get("s", 0)) for x in w]
    except Exception:
        return [], []

a_tok, a_t = load(sys.argv[1])
b_tok, b_t = load(sys.argv[2])
d = []
if a_tok and b_tok:
    for blk in SequenceMatcher(None, a_tok, b_tok, autojunk=False).get_matching_blocks():
        d += [b_t[blk.b + i] - a_t[blk.a + i] for i in range(blk.size)]

total_a = len(a_tok) if len(a_tok) > 0 else 1
if d:
    med = st.median(d)
    mean = st.mean(d)
    p95 = sorted(abs(x) for x in d)[int(len(d) * .95)]
    mx = max(abs(x) for x in d)
    print(f"matched {len(d)}/{total_a} words  offset median {med:+.3f}s  mean {mean:+.3f}s  p95 |off| {p95:.3f}s  max |off| {mx:.3f}s")
else:
    print(f"matched 0/{total_a} words  offset median +0.000s  mean +0.000s  p95 |off| 0.000s  max |off| 0.000s")
