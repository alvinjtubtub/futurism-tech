// Seam diff for a narrated film: every seam pair seam-check.py wrote to snapshots/seams/, with the presenter box
// masked (he moves across every cut, so a raw diff FAILs on him alone). 0.00% outside-kape on every pair = pass.
// Usage (film root): node <skill>/scripts/seam-diff-all.mjs [x0,y0,x1,y1]   default = landscape Kape zone + margin
// Vertical (9x16): pass 0,980,500,1720.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { python } from './lib/python.mjs';

const box = process.argv[2] || '0,380,660,1080';
const diff = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'spatial-film', 'scripts', 'seam-diff.py');
const seams = path.resolve('snapshots', 'seams');
if (!fs.existsSync(seams)) { console.error('snapshots/seams not found - run from the film root after seam-check.py'); process.exit(1); }
const out = path.resolve('snapshots', 'seamdiff');
fs.mkdirSync(out, { recursive: true });
const [py, ...pyArgs] = python();
const files = fs.readdirSync(seams).filter((f) => /^frame-.*\.png$/.test(f)).sort();
// the last pair is the loop check (last frame vs frame 0) - a narrated film is not a loop, skip it
let bad = 0;
for (let i = 0; i + 1 < files.length - 2; i += 2) {
  const [a, b] = [files[i], files[i + 1]];
  const r = spawnSync(py, [...pyArgs, diff, path.join(seams, a), path.join(seams, b), path.join(out, `pair-${i}.png`), box], { encoding: 'utf8' });
  const last = (r.stdout || r.stderr || String(r.error || '')).trim().split('\n').pop();
  const ok = r.status === 0 && /outside-kape 0\.00%/.test(last);
  if (!ok) bad++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${a} -> ${b}: ${last}`);
}
if (bad) {
  console.error(`seam-diff-all FAILED: ${bad} seam(s) have > 0.00% diff outside presenter box (${box})`);
  process.exit(1);
}
console.log(`seam-diff-all PASSED: all real seams 0.00% outside presenter box (${box})`);
