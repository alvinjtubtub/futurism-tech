"""Prove the rendered film's voice sits where the visuals were timed: compare word starts of the render's audio
transcript against the narration word timings the scenes were built from.

usage: <py> <skill>/scripts/sync-check.py <source vo-words.json> <render words.json>
Matches identical words in order and prints the offset stats (render - source). |median| < 0.03s = in sync.
"""
import json, re, sys, statistics as st
from difflib import SequenceMatcher

def load(p):
    w = [x for s in json.load(open(p, encoding="utf-8")) for x in s["words"]]
    return [re.sub(r"[^\w]", "", x["w"].lower()) for x in w], [x["s"] for x in w]

a_tok, a_t = load(sys.argv[1])
b_tok, b_t = load(sys.argv[2])
d = []
for blk in SequenceMatcher(None, a_tok, b_tok, autojunk=False).get_matching_blocks():
    d += [b_t[blk.b + i] - a_t[blk.a + i] for i in range(blk.size)]
print(f"matched {len(d)}/{len(a_tok)} words  offset median {st.median(d):+.3f}s  mean {st.mean(d):+.3f}s  "
      f"p95 |off| {sorted(abs(x) for x in d)[int(len(d) * .95)]:.3f}s  max |off| {max(abs(x) for x in d):.3f}s")
