// Checks this machine can run the KAPE explainer pipeline and prints the install command for anything missing.
// Writes KAPE_EXPLAINER_HOME/config.json with the Python command that works. Exit 1 if a required item is missing.
// Usage: node <skill>/scripts/setup-check.mjs
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { CANDIDATES, homeDir, okVersion, pythonVersion } from './lib/python.mjs';

const home = homeDir();
const win = process.platform === 'win32';
const run = (cmd, a) => spawnSync(cmd, a, { encoding: 'utf8', shell: win && /^(npx|npm)$/.test(cmd) });
const lines = [];
let missing = 0;
const ok = (what, detail = '') => lines.push(`OK       ${what}${detail ? '  ' + detail : ''}`);
const miss = (what, winCmd, macCmd, required = true) => {
  if (required) missing++;
  lines.push(`${required ? 'MISSING ' : 'OPTIONAL'} ${what}`);
  if (winCmd) lines.push(`           windows: ${winCmd}`);
  if (macCmd) lines.push(`           macos:   ${macCmd}`);
};

// Node
const nodeMajor = Number(process.versions.node.split('.')[0]);
if (nodeMajor >= 20) ok('node', process.versions.node);
else miss(`node >= 20 (found ${process.versions.node})`, 'winget install OpenJS.NodeJS.LTS', 'brew install node');

// Python + packages: prefer the first interpreter that already has every package
const REQUIRED_PKGS = ['numpy', 'PIL', 'scipy', 'faster_whisper'];
const pkgOk = (cmd, mod) => run(cmd[0], [...cmd.slice(1), '-c', `import ${mod}`]).status === 0;
const found = CANDIDATES.map((c) => ({ c, v: pythonVersion(c) })).filter((x) => okVersion(x.v));
const best = found.find((x) => REQUIRED_PKGS.every((m) => pkgOk(x.c, m))) || found[0];
let py = null;
if (!best) {
  miss('python >= 3.10', 'winget install Python.Python.3.12', 'brew install python@3.12');
} else {
  py = best.c;
  ok('python', `${py.join(' ')} (${best.v.join('.')})`);
  const lacking = REQUIRED_PKGS.filter((m) => !pkgOk(py, m));
  for (const m of REQUIRED_PKGS) if (!lacking.includes(m)) ok(`python package ${m}`);
  if (lacking.length) {
    const pip = lacking.map((m) => ({ PIL: 'pillow', faster_whisper: 'faster-whisper' }[m] || m)).join(' ');
    const cmd = `${py.join(' ')} -m pip install ${pip}`;
    miss(`python package(s): ${lacking.join(', ')}`, cmd, cmd);
  }
  if (pkgOk(py, 'torch')) ok('python package torch', '(optional, blink-fit)');
  else lines.push(`NOTE     torch not installed - optional, only needed for mascot blink-fit (${py.join(' ')} -m pip install torch)`);
  fs.mkdirSync(home, { recursive: true });
  fs.writeFileSync(path.join(home, 'config.json'), JSON.stringify({ python: py, checked: new Date().toISOString() }, null, 2) + '\n');
}

// ffmpeg / ffprobe / npx
for (const t of ['ffmpeg', 'ffprobe']) {
  const r = run(t, ['-version']);
  if (r.status === 0) ok(t, (r.stdout.split('\n')[0] || '').slice(0, 40));
  else miss(t, 'winget install Gyan.FFmpeg', 'brew install ffmpeg');
}
const npx = run('npx', ['--version']);
if (npx.status === 0) ok('npx', npx.stdout.trim());
else miss('npx (comes with Node)', 'winget install OpenJS.NodeJS.LTS', 'brew install node');

// HyperFrames skills (sitting next to this skill)
const skillsDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const hfMissing = ['media-use', 'general-video', 'hyperframes-animation'].filter((s) => !fs.existsSync(path.join(skillsDir, s)));
if (!hfMissing.length) ok('HyperFrames skills', 'media-use, general-video, hyperframes-animation');
else {
  const cmd = 'npx hyperframes skills update general-video hyperframes-animation media-use';
  miss(`HyperFrames skills: ${hfMissing.join(', ')} (in ${skillsDir})`, cmd, cmd);
}

// playwright (optional: only for capture-surfaces / measure-surface)
let pw = false;
for (const t of [process.env.PLAYWRIGHT_PATH, 'playwright', path.join(skillsDir, 'playwright-skill', 'node_modules', 'playwright')].filter(Boolean)) {
  try { createRequire(import.meta.url).resolve(t); pw = true; break; } catch {}
}
if (pw) ok('playwright', '(optional)');
else miss('playwright (only for platform-canvas surfaces)', 'npm i -g playwright && npx playwright install chromium', 'npm i -g playwright && npx playwright install chromium', false);

// bundled film engine (sits next to this skill)
const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const engine = path.join(SKILL, '..', 'spatial-film', 'SKILL.md');
if (fs.existsSync(engine)) ok('spatial-film engine', path.dirname(engine));
else miss(`spatial-film engine (expected next to this skill: ${path.dirname(engine)})`, 'reinstall: node install.mjs', 'reinstall: node install.mjs');

// HyperFrames CLI at the pinned version + the headless Chrome it renders with
let hfVer = null;
try { hfVer = JSON.parse(fs.readFileSync(path.join(SKILL, 'template', 'film.json'), 'utf8')).hyperframes; } catch {}
if (hfVer && npx.status === 0) {
  const hf = (a) => run('npx', ['--prefer-offline', '--yes', `hyperframes@${hfVer}`, ...a]);
  const v = hf(['--version']);
  if (v.status === 0) ok('hyperframes', v.stdout.trim());
  else miss(`hyperframes@${hfVer} (npm could not fetch it - check your internet)`, `npx --yes hyperframes@${hfVer} --version`, `npx --yes hyperframes@${hfVer} --version`);
  const b = hf(['browser', 'path']);
  const chrome = (b.stdout || '').trim().split('\n').pop();
  if (b.status === 0 && chrome && fs.existsSync(chrome)) ok('render browser', '(headless Chrome)');
  else { const cmd = `npx --yes hyperframes@${hfVer} browser ensure`; miss('render browser (headless Chrome, ~150 MB)', cmd, cmd); }
}

// free disk: renders + frame cache need ~5 GB
let filmsDir = null;
try { filmsDir = JSON.parse(fs.readFileSync(path.join(home, 'profile', 'brand.json'), 'utf8')).films_dir; } catch {}
for (const d of [...new Set([os.tmpdir(), home, filmsDir].filter((p) => p && fs.existsSync(p)))]) {
  try {
    const s = fs.statfsSync(d);
    const gb = (s.bavail * s.bsize) / 1e9;
    if (gb >= 5) ok('disk space', `${gb.toFixed(0)} GB free at ${d}`);
    else miss(`disk space: ${gb.toFixed(1)} GB free at ${d} (need ~5 GB) - free some space`);
  } catch {}
}

// GPU (optional: hardware path renders ~15x faster)
const gpuNames = win
  ? (run('powershell', ['-NoProfile', '-Command', '(Get-CimInstance Win32_VideoController).Name']).stdout || '')
  : ([...(run('system_profiler', ['SPDisplaysDataType']).stdout || '').matchAll(/Chipset Model: (.+)/g)].map((m) => m[1]).join('\n'));
const gpus = gpuNames.split('\n').map((s) => s.trim()).filter(Boolean);
if (gpus.some((g) => /nvidia|geforce|rtx|radeon|rx \d|arc|apple/i.test(g))) ok('gpu', gpus.join(', '));
else lines.push(`NOTE     no dedicated GPU found${gpus.length ? ` (${gpus.join(', ')})` : ''} - films still render, just much slower`);

// Whisper model (downloads on the first transcribe)
const hfHub = process.env.HF_HUB_CACHE || path.join(process.env.HF_HOME || path.join(os.homedir(), '.cache', 'huggingface'), 'hub');
if (fs.existsSync(path.join(hfHub, 'models--Systran--faster-whisper-medium'))) ok('whisper model', 'medium (cached)');
else lines.push('NOTE     whisper model not downloaded yet - the first transcribe fetches ~1.5 GB (needs internet once)');

// Your inputs: things only you can bring (never block the check - the setup interview fills them)
lines.push('', 'YOUR INPUTS');
const prof = path.join(home, 'profile');
const input = (state, what, hint) => lines.push(`${state.padEnd(8)} ${what}${hint ? '  ' + hint : ''}`);
let brandJson = null;
try { brandJson = JSON.parse(fs.readFileSync(path.join(prof, 'brand.json'), 'utf8')); } catch {}
if (brandJson) input('OK', 'brand profile', `${brandJson.name || ''}`);
else input('TODO', 'brand profile', `- your brand name, colours, call to action: node ${path.join(SKILL, 'scripts', 'profile.mjs')} init --name "<your name>"`);
const logo = brandJson?.logo && path.join(prof, brandJson.logo);
if (logo && fs.existsSync(logo)) input('OK', 'logo', brandJson.logo);
else input('OPTIONAL', 'logo', '- PNG (transparent) or SVG; without one the film uses a text wordmark');
const voice = path.join(prof, 'voice.md');
const voiceEx = path.join(SKILL, 'template', 'profile', 'voice.example.md');
const voiceTxt = fs.existsSync(voice) ? fs.readFileSync(voice, 'utf8') : null;
if (voiceTxt && !(fs.existsSync(voiceEx) && voiceTxt === fs.readFileSync(voiceEx, 'utf8'))) input('OK', 'speaking style', 'voice.md');
else input('TODO', 'speaking style', '- 5 quick questions, or a 5+ min unscripted recording of you talking');
input('ASK', 'voiceover', '- a narration MP3 you make with Gemini 3.8 Flash TTS (manual, no API key) OR a decent mic + quiet room to record one take');
const mascot = path.join(prof, 'mascot');
if (!fs.existsSync(mascot)) input('OK', 'mascot', 'KAPE demo (add your own transparent pose PNGs any time)');
else if (fs.existsSync(path.join(mascot, 'manifest.json'))) input('OK', 'mascot', 'yours, prepped');
else input('TODO', 'mascot', `- yours, not prepped: ${(py || ['python']).join(' ')} ${path.join(SKILL, 'scripts', 'prep-mascot.py')} ${mascot}`);
if (fs.existsSync(path.join(prof, 'music', 'bed.mp3'))) input('OK', 'music', 'music/bed.mp3');
else input('OPTIONAL', 'music', '- a track you own the rights to, the HeyGen catalog, or none');

console.log(lines.join('\n'));
console.log(missing ? `\n${missing} required item(s) missing - install them, then re-run setup-check.` : '\nAll required tools present.');
process.exit(missing ? 1 : 0);
