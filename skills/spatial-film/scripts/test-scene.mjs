// Lint + snapshot ONE scene in its isolated harness (never touches the shared index.html).
// Run from the film project root:  node <skill>/scripts/test-scene.mjs <scene_id> "<t1,t2,...>"
// Snapshots: .hyperframes/test/<id>/snaps/frame-NN-at-Xs.png + contact-sheet.jpg (read the sheet first).
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const [id, times] = process.argv.slice(2);
if (!id || !times) { console.error('usage: test-scene.mjs <scene_id> "<t1,t2,...>"'); process.exit(1); }
if (!fs.existsSync('film.json')) { console.error('run from the film project root (film.json not found)'); process.exit(1); }
const V = JSON.parse(fs.readFileSync('film.json', 'utf8')).hyperframes;
const T = path.join('.hyperframes', 'test', id);
if (!fs.existsSync(T)) { console.error(`no harness for ${id} - run: <py> <skill>/scripts/make-harness.py`); process.exit(1); }
const comp = path.join('compositions', `${id}.html`);
if (!fs.existsSync(comp)) { console.error(`${comp} not written yet`); process.exit(1); }
fs.copyFileSync(comp, path.join(T, 'compositions', `${id}.html`));
// npx is a .cmd shim on Windows, so it needs a shell there; nowhere else
const hf = (a) => {
  const r = spawnSync('npx', ['--prefer-offline', '--yes', `hyperframes@${V}`, ...a], { encoding: 'utf8', shell: process.platform === 'win32', maxBuffer: 1 << 26 });
  return (r.stdout || '') + (r.stderr || '') + (r.error ? String(r.error) : '');
};
const tail = (s, n) => s.replace(/\s+$/, '').split('\n').slice(-n).join('\n');
console.log(`== lint ${id}`);
console.log(tail(hf(['lint', T]), 40));
console.log(`== snapshot ${id} at ${times}`);
fs.rmSync(path.join(T, 'snaps'), { recursive: true, force: true });
console.log(tail(hf(['snapshot', T, '--at', times, '--no-end', '--describe', 'false', '-o', path.join(T, 'snaps')]), 6));
