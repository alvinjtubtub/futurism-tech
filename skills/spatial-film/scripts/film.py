"""Shared loader for film.json (the one source of scene timing). Imported by assemble.py, make-harness.py
and seam-check.py; run every script from the film project root."""
import ast, json, operator, os, sys

ROOT = os.getcwd()


def load():
    p = os.path.join(ROOT, 'film.json')
    if not os.path.exists(p):
        sys.exit('film.json not found - run this from the film project root')
    f = json.load(open(p, encoding='utf-8'))
    beat = 60 / f['bpm']
    bar = beat * f.get('beats_per_bar', 4)
    scenes, t = [], 0.0
    for sid, bars in f['scenes']:
        if sid[0].isdigit():
            sys.exit(f'scene id {sid!r} starts with a digit - lint rejects it (use s01-...)')
        scenes.append({'id': sid, 'start': round(t, 4), 'dur': round(bars * bar, 4)})
        t += bars * bar
    f.update(beat=beat, bar=bar, total=round(t, 4), scene_list=scenes,
             starts={s['id']: s for s in scenes})
    return f


def cue_time(expr, f, k=None):
    """A cue time is seconds (1.09) or an expression in beats/bars: "4*b", "6*b+0.05", "2*b*k"."""
    if isinstance(expr, (int, float)):
        return float(expr)
    names = {'b': f['beat'], 'bar': f['bar'], 'k': k}
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}

    def ev(n):  # arithmetic on numbers and b/bar/k only - film.json is data, never code
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name) and names.get(n.id) is not None:
            return names[n.id]
        if isinstance(n, ast.BinOp) and type(n.op) in ops:
            return ops[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -ev(n.operand)
        sys.exit(f'cue time {expr!r}: only numbers, b, bar, k and + - * / are allowed')
    return float(ev(ast.parse(expr, mode='eval').body))


def hf(f):
    return f'hyperframes@{f["hyperframes"]}'
