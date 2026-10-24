// Finds the Python 3.10+ that runs the pipeline scripts, and the KAPE_EXPLAINER_HOME user dir.
// config.json (written by setup-check.mjs) wins; else probe local venv, ~/.kape-explainer/venv, py -3.12, python3.12, python3, python (Windows + macOS).
// Usage: import { python, homeDir } from './lib/python.mjs';  python() -> ['py','-3.12'] | ['python3'] ...
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const WORKSPACE_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..');

export const homeDir = () => {
  if (process.env.KAPE_EXPLAINER_HOME) return path.resolve(process.env.KAPE_EXPLAINER_HOME);
  if (fs.existsSync(path.join(WORKSPACE_ROOT, 'profile', 'brand.json'))) return WORKSPACE_ROOT;
  return path.join(os.homedir(), '.kape-explainer');
};

const venvBin = (root, dir) => path.join(root, dir, process.platform === 'win32' ? 'Scripts' : 'bin', process.platform === 'win32' ? 'python.exe' : 'python');

export const CANDIDATES = [
  [venvBin(WORKSPACE_ROOT, '.venv')],
  [venvBin(WORKSPACE_ROOT, 'venv')],
  [venvBin(path.join(os.homedir(), '.kape-explainer'), 'venv')],
  ['py', '-3.12'],
  ['python3.12'],
  ['python3'],
  ['python'],
  ['py', '-3'],
];

// [major, minor] when `cmd` runs and reports a Python, else null
export function pythonVersion(cmd) {
  const r = spawnSync(cmd[0], [...cmd.slice(1), '--version'], { encoding: 'utf8' });
  const m = r.status === 0 && /Python (\d+)\.(\d+)/.exec((r.stdout || '') + (r.stderr || ''));
  return m ? [Number(m[1]), Number(m[2])] : null;
}
export const okVersion = (v) => !!v && (v[0] > 3 || (v[0] === 3 && v[1] >= 10));

export function python() {
  try {
    const cfg = JSON.parse(fs.readFileSync(path.join(homeDir(), 'config.json'), 'utf8'));
    if (Array.isArray(cfg.python) && okVersion(pythonVersion(cfg.python))) return cfg.python;
  } catch {}
  for (const c of CANDIDATES) if (okVersion(pythonVersion(c))) return c;
  throw new Error('Python 3.10+ not found. Run: node <skill>/scripts/setup-check.mjs');
}
