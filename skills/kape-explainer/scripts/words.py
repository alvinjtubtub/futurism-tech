"""Print every narration word with its start time. usage: <py> <skill>/scripts/words.py <vo-words.json>"""
import json, sys

for s in json.load(open(sys.argv[1], encoding="utf-8")):
    print(" ".join(f"{w['w'].strip()}@{w['s']}" for w in s["words"]))
