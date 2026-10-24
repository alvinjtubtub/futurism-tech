#!/usr/bin/env node
// Stage 7-8 Cloud Render Orchestrator for KAPE Explainer films.
// Supports Option 2 (GitHub Actions + Google Drive — default) and Option 3 (Modal.com GPU).
//
// Workflow (GitHub Actions mode — default):
//   1. Verifies Stage 5-6 Quality Gates passed (runs `run-gates.mjs` if needed)
//   2. Runs Stage 7 Packager (`package-film.mjs`) to build `package/<slug>-project.zip`, CAPTIONS.srt, and covers
//   3. Commits & pushes `films/<slug>/package/<slug>-project.zip` + `film.json` to GitHub (triggers `.github/workflows/render-film.yml`)
//   4. Optionally watches the GitHub Actions run via `gh` CLI and downloads the verified MP4 + `render-proof.json` when complete
//
// Usage:
//   node skills/kape-explainer/scripts/cloud-render.mjs --dir films/<slug> [--provider github|modal] [--watch] [--lang tl]

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL = path.resolve(SCRIPT_DIR, '..');
const REPO_ROOT = path.resolve(SKILL, '..', '..');
const args = process.argv.slice(2);
const flag = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const has = (k) => args.includes(k);

const root = path.resolve(flag('--dir') || process.cwd());
const filmPath = path.join(root, 'film.json');
if (!fs.existsSync(filmPath)) {
  console.error(`cloud-render: film.json not found in ${root}\nUsage: node skills/kape-explainer/scripts/cloud-render.mjs --dir films/<slug>`);
  process.exit(1);
}

const film = JSON.parse(fs.readFileSync(filmPath, 'utf8'));
const slug = film.name || path.basename(root);
const provider = (flag('--provider') || 'github').toLowerCase();
const lang = flag('--lang') || 'tl';
const prompt = flag('--prompt') || '';
const workers = flag('--workers') || (provider === 'github' ? '4' : '6');

// 1. Ensure Stage 5-6 Quality Gates passed
const gatesReportPath = path.join(root, '.hyperframes', 'gates-report.json');
if (!has('--skip-gate-check')) {
  let gatesOk = false;
  if (fs.existsSync(gatesReportPath)) {
    try {
      gatesOk = !!JSON.parse(fs.readFileSync(gatesReportPath, 'utf8')).all_automated_passed;
    } catch {}
  }
  if (!gatesOk) {
    console.log(`=== [Stage 5-6] Running Quality Gates for ${slug} ===`);
    const gRes = spawnSync(process.execPath, [path.join(SCRIPT_DIR, 'run-gates.mjs'), '--dir', root], { stdio: 'inherit' });
    if (gRes.status !== 0) {
      console.error('cloud-render: Quality Gates failed. Fix scene issues before rendering.');
      process.exit(1);
    }
  } else {
    console.log(`OK       [Stage 5-6] Quality Gates already passed (.hyperframes/gates-report.json)`);
  }
}

// 2. Run Stage 7 Packager to create <slug>-project.zip and verify upload pack
const zipPath = path.join(root, 'package', `${slug}-project.zip`);
console.log(`\n=== [Stage 7] Packaging ${slug} for Cloud Render ===`);
const pkgArgs = [path.join(SCRIPT_DIR, 'package-film.mjs'), '--dir', root];
if (has('--skip-gate-check')) pkgArgs.push('--skip-gate-check');
if (has('--allow-incomplete-pack')) pkgArgs.push('--allow-incomplete-pack');
const pRes = spawnSync(process.execPath, pkgArgs, { stdio: 'inherit' });
if (pRes.status !== 0 || !fs.existsSync(zipPath)) {
  console.error('cloud-render: Stage 7 packaging failed.');
  process.exit(1);
}

// 3A. Option 2: GitHub Actions (Standard Free Tier) + Google Drive
if (provider === 'github') {
  console.log(`\n=== [Stage 7-8] Dispatching ${slug} via GitHub Actions (.github/workflows/render-film.yml) ===`);
  const relFilmDir = path.relative(REPO_ROOT, root);

  // Check if a git remote 'origin' is configured
  const remRes = spawnSync('git', ['remote', 'get-url', 'origin'], { cwd: REPO_ROOT, encoding: 'utf8' });
  if (remRes.status !== 0) {
    console.error(`
ACTION NEEDED: Git remote 'origin' is not linked to your GitHub repo yet.
Create a public GitHub repo (public = unlimited free GitHub Actions minutes for 2+ videos/day) and run:
  cd "${REPO_ROOT}"
  git remote add origin https://github.com/<your-username>/<your-repo>.git
  git add .
  git commit -m "Initialize KAPE pipeline with GitHub Actions renderer"
  git push -u origin main
`);
    process.exit(1);
  }

  // Stage film package + film.json + workflow and push to trigger GitHub Actions
  spawnSync('git', ['add', '.github/workflows/render-film.yml', path.join(relFilmDir, 'film.json'), path.join(relFilmDir, 'package')], {
    cwd: REPO_ROOT,
    stdio: 'inherit',
  });
  spawnSync('git', ['commit', '-m', `Render film: ${slug} (Stage 7 package)`], { cwd: REPO_ROOT, stdio: 'inherit' });
  const pushRes = spawnSync('git', ['push', 'origin', 'main'], { cwd: REPO_ROOT, stdio: 'inherit' });
  if (pushRes.status !== 0) {
    console.error('cloud-render: git push failed.');
    process.exit(1);
  }

  // Also trigger workflow_dispatch explicitly if `gh` CLI is installed
  const ghCheck = spawnSync('gh', ['--version'], { encoding: 'utf8' });
  if (ghCheck.status === 0) {
    spawnSync('gh', ['workflow', 'run', 'render-film.yml', '-f', `slug=${slug}`, '-f', `lang=${lang}`, '-f', `workers=${workers}`], {
      cwd: REPO_ROOT,
      stdio: 'inherit',
    });
    if (has('--watch')) {
      console.log('\nWatching GitHub Actions run and downloading verified MP4 when complete...');
      spawnSync('gh', ['run', 'watch'], { cwd: REPO_ROOT, stdio: 'inherit' });
      spawnSync('gh', ['run', 'download', '-n', `${slug}-verified-upload-pack`, '-D', path.join(root, 'package')], {
        cwd: REPO_ROOT,
        stdio: 'inherit',
      });
    }
  }

  console.log(`
=== Dispatched ${slug} to GitHub Actions ===
  • GitHub Actions will render ${slug}-1080p60.mp4, run the Stage 8 faster-whisper Word-Sync Proof,
    upload the verified pack to Google Drive (03-Completed-Videos/${slug}/), and attach it as a GitHub Artifact.
  • To download the verified pack locally via GitHub CLI once finished:
    gh run download -n "${slug}-verified-upload-pack" -D "films/${slug}/package"
`);
  process.exit(0);
}

// 3B. Option 3 Fallback: Modal.com Serverless GPU
const modalCandidates = [
  'modal',
  path.resolve(SKILL, '..', '..', '.venv', 'bin', 'modal'),
  path.join(os.homedir(), '.kape-explainer', 'venv', 'bin', 'modal'),
  path.join(os.homedir(), '.local', 'bin', 'modal'),
];
const modalBin = modalCandidates.find((bin) => spawnSync(bin, ['--version'], { encoding: 'utf8' }).status === 0);
if (!modalBin) {
  console.error('MISSING  Modal CLI not found. Use --provider github (default) or install modal.');
  process.exit(1);
}
const modalArgs = ['run', path.join(SCRIPT_DIR, 'modal_render.py'), '--zip-path', zipPath, '--out-dir', path.join(root, 'renders'), '--lang', lang, '--workers', String(workers)];
if (prompt) modalArgs.push('--prompt', prompt);
const mRes = spawnSync(modalBin, modalArgs, { stdio: 'inherit', cwd: root });
process.exit(mRes.status || 0);
