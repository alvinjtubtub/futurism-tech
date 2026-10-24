"""Flag gsap fromTo calls whose FROM vars set a property that no TO vars for that target ever animate.

GSAP only tweens the properties in the TO vars. A from-only property (e.g. `opacity: 1` in the from vars of a
lift tween) is applied when the timeline plays through it in order - which is what the harness does - but a
render worker that seeks straight into the middle of a scene never applies it, so the element stays at its
earlier value. HTTP Status Codes 2026-10-07: s09's lifted "4" was visible in every harness snapshot and invisible
in the render until its exit tween. Run before render:

    <py> <skill>/scripts/fromto-scan.py compositions/s*.html

A from-only property is OK when another fromTo/to on the SAME target animates it (a split scale + fade pair).
Fix a real hit by adding the property to the TO vars (e.g. `opacity: 1`). Exit code 1 when anything is flagged.
"""
import re
import sys
from collections import defaultdict

KEY = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*:')
FROMTO = re.compile(r'fromTo\(\s*([^,]+?)\s*,\s*\{([^{}]*)\}\s*,\s*\{([^{}]*)\}')
TO = re.compile(r'\.to\(\s*([^,]+?)\s*,\s*\{([^{}]*)\}')
SKIP = {'immediateRender', 'duration', 'ease', 'force3D', 'delay', 'overwrite', 'transformOrigin', 'stagger'}

bad = 0
for path in sys.argv[1:]:
    lines = open(path, encoding='utf8').read().split('\n')
    animated = defaultdict(set)          # target -> every property some TO vars animate
    calls = []
    for n, line in enumerate(lines, 1):
        for m in FROMTO.finditer(line):
            tgt, frm, to = m.group(1), set(KEY.findall(m.group(2))) - SKIP, set(KEY.findall(m.group(3))) - SKIP
            animated[tgt] |= to
            calls.append((n, tgt, frm - to))
        for m in TO.finditer(line):
            animated[m.group(1)] |= set(KEY.findall(m.group(2))) - SKIP
    for n, tgt, miss in calls:
        real = miss - animated[tgt]
        if real:
            bad += 1
            print(f'{path}:{n}: {tgt} from-only {sorted(real)} - add to the TO vars')
print(f'{bad} fromTo call(s) with from-only properties')
sys.exit(1 if bad else 0)
