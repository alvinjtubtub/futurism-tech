#!/usr/bin/env node
// Stage 5-6 Quality Gates runner for KAPE Explainer films.
// Runs all 5 mandatory quality gates in exact order (PIPELINE.md Phase 5/6):
//   1. fromto-scan.py compositions/s*.html -> 0 hits
//   2. assemble.py + make-harness.py       -> clean assembly, no missing compositions
//   3. npx hyperframes check               -> passed (Layout 0 errors, Motion 0, Contrast WCAG AA)
//   4. seam-check.py + seam-diff-all.mjs   -> 0.00% outside presenter box on every real seam
//   5. Full-composite snapshots            -> snapshots/composite/ + contact-sheet.jpg for Baet eyeball review
// Writes .hyperframes/gates-report.json. Exits 1 on any gate failure ("Nothing ships on a failed gate").
// Usage (from film root): node <skill>/scripts/run-gates.mjs [--dir <film_dir>] [--box x0,y0,x1,y1]

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { python } from './lib/python.mjs';

const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ENGINE = path.resolve(SKILL, '..', 'spatial-film');
const args = process.argv.slice(2);
const flag = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };

const root = path.resolve(flag('--dir') || process.cwd());
const filmPath = path.join(root, 'film.json');
if (!fs.existsSync(filmPath)) {
  console.error(`run-gates: film.json not found in ${root}`);
  process.exit(1);
}

const film = JSON.parse(fs.readFileSync(filmPath, 'utf8'));
const [py, ...pyArgs] = python();
const isVertical = film.height > film.width;
const box = flag('--box') || (isVertical ? '0,980,500,1720' : '0,380,660,1080');

const run = (cmd, cmdArgs) => spawnSync(cmd, cmdArgs, {
  cwd: root,
  encoding: 'utf8',
  maxBuffer: 1 << 26,
  shell: process.platform === 'win32' && cmd === 'npx',
});

const report = {
  film: film.name,
  timestamp: new Date().toISOString(),
  gates: {},
  all_automated_passed: false,
};

const logDir = path.join(root, '.hyperframes', 'logs');
fs.mkdirSync(logDir, { recursive: true });

function recordGate(id, name, ok, output, detail = '') {
  const logFile = path.join(logDir, `gate-${id}.log`);
  fs.writeFileSync(logFile, output || '', 'utf8');
  report.gates[id] = { name, status: ok ? 'PASS' : 'FAIL', detail, log: path.relative(root, logFile) };
  console.log(`${ok ? 'PASS' : 'FAIL'}  [Gate ${id}] ${name}${detail ? ' — ' + detail : ''}`);
  if (!ok) {
    const tail = (output || '').trim().split('\n').slice(-15).join('\n  ');
    if (tail) console.error(`  ${tail}`);
  }
  return ok;
}

// Gate 1: fromto-scan.py
const compDir = path.join(root, 'compositions');
const sceneIds = (film.scenes || []).map((s) => s[0]);
const sceneFiles = sceneIds.map((id) => path.join('compositions', `${id}.html`)).filter((rel) => fs.existsSync(path.join(root, rel)));
const missingScenes = sceneIds.filter((id) => !fs.existsSync(path.join(compDir, `${id}.html`)));

if (missingScenes.length > 0) {
  recordGate('1-fromto', 'fromto-scan (GSAP fromTo law)', false, `Missing scene files: ${missingScenes.join(', ')}`, `missing ${missingScenes.length} scene(s)`);
} else {
  const r1 = run(py, [...pyArgs, path.join(ENGINE, 'scripts', 'fromto-scan.py'), ...sceneFiles]);
  const out1 = (r1.stdout || '') + (r1.stderr || '');
  recordGate('1-fromto', 'fromto-scan (GSAP fromTo law)', r1.status === 0 && /0 fromTo call\(s\) with from-only/.test(out1), out1, out1.trim().split('\n').pop());
}

// Gate 2: assemble.py + make-harness.py
const r2a = run(py, [...pyArgs, path.join(ENGINE, 'scripts', 'assemble.py')]);
const r2b = run(py, [...pyArgs, path.join(ENGINE, 'scripts', 'make-harness.py')]);
const out2 = (r2a.stdout || '') + (r2a.stderr || '') + '\n' + (r2b.stdout || '') + (r2b.stderr || '');
const noMissingWarn = !/warning: no composition yet/.test(out2);
recordGate(
  '2-assemble',
  'assemble.py + make-harness.py',
  r2a.status === 0 && r2b.status === 0 && noMissingWarn && fs.existsSync(path.join(root, 'index.html')),
  out2,
  noMissingWarn ? 'clean assembly' : 'missing composition warning in assemble.py'
);

// Gate 3: npx hyperframes check
const hfVer = film.hyperframes || '0.8.117';
const r3 = run('npx', ['--prefer-offline', '--yes', `hyperframes@${hfVer}`, 'check']);
const out3 = (r3.stdout || '') + (r3.stderr || '');
const checkPassed = r3.status === 0 && /Check passed/i.test(out3);
recordGate('3-check', `hyperframes@${hfVer} check`, checkPassed, out3, checkPassed ? 'Layout 0 errors, Motion 0, WCAG AA' : 'check failed');

// Gate 4: seam-check.py (generates snapshots/seams) + seam-diff-all.mjs (masked diff outside presenter box)
const r4a = run(py, [...pyArgs, path.join(ENGINE, 'scripts', 'seam-check.py')]);
const out4a = (r4a.stdout || '') + (r4a.stderr || '');
const seamsDir = path.join(root, 'snapshots', 'seams');
const hasSeamFrames = fs.existsSync(seamsDir) && fs.readdirSync(seamsDir).some((f) => f.endsWith('.png'));

let r4b = { status: 1, stdout: '', stderr: 'seam-check did not produce snapshots/seams' };
if (hasSeamFrames) {
  r4b = run(process.execPath, [path.join(SKILL, 'scripts', 'seam-diff-all.mjs'), box]);
}
const out4b = (r4b.stdout || '') + (r4b.stderr || '');
const out4 = `=== seam-check.py (raw) ===\n${out4a}\n=== seam-diff-all.mjs (masked ${box}) ===\n${out4b}`;
const seamsPassed = r4b.status === 0 && /seam-diff-all PASSED/.test(out4b);
recordGate('4-seams', `masked seam diff (box ${box})`, seamsPassed, out4, seamsPassed ? '0.00% outside presenter box on all real seams' : 'seam diff > 0.00%');

// Gate 5: Full-composite snapshots across the film (midpoint of every scene) for Baet eyeball review
const beat = 60 / (film.bpm || 60);
const bar = beat * (film.beats_per_bar || 1);
let cursor = 0;
const snapTimes = [0.25];
for (const [, bars] of film.scenes || []) {
  const dur = bars * bar;
  snapTimes.push(Number((cursor + dur / 2).toFixed(2)));
  cursor += dur;
}
snapTimes.push(Number(Math.max(0.5, cursor - 0.5).toFixed(2)));
const uniqueTimes = [...new Set(snapTimes)].join(',');
const compSnapDir = path.join(root, 'snapshots', 'composite');
fs.rmSync(compSnapDir, { recursive: true, force: true });
const r5 = run('npx', ['--prefer-offline', '--yes', `hyperframes@${hfVer}`, 'snapshot', '.', '--at', uniqueTimes, '--no-end', '--describe', 'false', '-o', compSnapDir]);
const out5 = (r5.stdout || '') + (r5.stderr || '');
const compFiles = fs.existsSync(compSnapDir) ? fs.readdirSync(compSnapDir).filter((f) => f.endsWith('.png')) : [];
const gate5Ok = r5.status === 0 && compFiles.length > 0;
recordGate(
  '5-composite',
  'full-composite snapshots (for Baet eyeball review)',
  gate5Ok,
  out5,
  gate5Ok ? `${compFiles.length} frames + contact-sheet.jpg in snapshots/composite/` : 'snapshot failed'
);

const allPassed = Object.values(report.gates).every((g) => g.status === 'PASS');
report.all_automated_passed = allPassed;
const reportPath = path.join(root, '.hyperframes', 'gates-report.json');
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n', 'utf8');

console.log(`\nGates report written to ${path.relative(root, reportPath)}`);
if (!allPassed) {
  console.error('QUALITY GATES FAILED — repair failing gate(s) and re-run before packaging.');
  process.exit(1);
}
console.log('ALL 5 QUALITY GATES PASSED (remember to eyeball snapshots/composite/contact-sheet.jpg).');
