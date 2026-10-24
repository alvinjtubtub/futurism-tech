"""One isolated test project per scene under .hyperframes/test/<id>/, so parallel workers lint and snapshot
their own scene without touching the shared index.html. Re-runnable (re-copies assets, skips assets/audio).
Run from the project root:  python <skill>/scripts/make-harness.py"""
import os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from film import ROOT, load

if len(sys.argv) > 1:
    sys.exit(__doc__)  # takes no arguments; a stray --help used to build harnesses from whatever film.json held
f = load()
W, H, G = f['width'], f['height'], f.get('ground', '#000000')
INDEX = '''<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<script src="{gsap_src}"></script>
<style>* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: {G}; }} #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}</style>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{d}" data-width="{W}" data-height="{H}">
  <div id="{id}" data-composition-id="{id}" data-composition-src="compositions/{id}.html" data-start="0" data-duration="{d}" data-track-index="1" data-width="{W}" data-height="{H}"></div>
</div>
<script>const tl = gsap.timeline({{ paused: true }}); window.__timelines["main"] = tl;</script>
</body></html>
'''
# full-film overlay layers (a narrated film's presenter) get a harness too, over the whole film length
units = f['scene_list'] + [{'id': o['id'], 'dur': o.get('dur', f['total'])} for o in f.get('overlays', [])]
for s in units:
    t = os.path.join(ROOT, '.hyperframes', 'test', s['id'])
    os.makedirs(os.path.join(t, 'compositions'), exist_ok=True)
    shutil.rmtree(os.path.join(t, 'assets'), ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(t, 'assets'), ignore=shutil.ignore_patterns('audio'))
    open(os.path.join(t, 'index.html'), 'w', encoding='utf-8').write(
        INDEX.format(W=W, H=H, G=G, gsap_src=('assets/gsap.min.js' if os.path.exists(os.path.join(ROOT, 'assets', 'gsap.min.js')) else f"https://cdn.jsdelivr.net/npm/gsap@{f['gsap']}/dist/gsap.min.js"), id=s['id'], d=s['dur']))
    open(os.path.join(t, 'hyperframes.json'), 'w', encoding='utf-8').write(
        '{"paths":{"blocks":"compositions","assets":"assets"}}\n')
print('harness ready:', ', '.join(f'{s["id"]} ({s["dur"]}s)' for s in units))
