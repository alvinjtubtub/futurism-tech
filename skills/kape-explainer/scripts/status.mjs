#!/usr/bin/env node
// Stage 0-8 Status & Multi-Project Inspector for KAPE Explainer films.
// Read-only:
//   - On a single film folder: prints the exact state of Stages 0 through 8 against the
//     authoritative "How a Film Gets Made" workflow diagram.
//   - With --all (or when run on the workspace / films parent folder): lists all independent
//     projects across all configured profiles and their current workflow stage.
// Usage: node <skill>/scripts/status.mjs [<film_dir> | --all]

import fs from 'node:fs';
import path from 'node:path';
import { expandHome, listProfiles } from './lib/brand.mjs';
import { homeDir } from './lib/python.mjs';

const args = process.argv.slice(2);
const wantAll = args.includes('--all');
const posArg = args.find((a) => !a.startsWith('--'));
const targetDir = path.resolve(posArg || process.cwd());

function readJson(dir, rel) {
  try { return JSON.parse(fs.readFileSync(path.join(dir, rel), 'utf8')); } catch { return null; }
}

function inspectFilm(root) {
  const exists = (rel) => fs.existsSync(path.join(root, rel));
  const film = readJson(root, 'film.json');
  const brand = readJson(root, 'brand.json');
  const gates = readJson(root, '.hyperframes/gates-report.json');
  const proof = readJson(root, '.hyperframes/render-proof.json');
  const sceneIds = (film?.scenes || []).map((s) => s[0]);
  const builtScenes = sceneIds.filter((id) => exists(`compositions/${id}.html`));
  const storyboardTxt = exists('STORYBOARD.md') ? fs.readFileSync(path.join(root, 'STORYBOARD.md'), 'utf8') : '';
  const storyboardLocked = /##\s*Locked/i.test(storyboardTxt);
  const isKape = !!brand || exists('src/presenter-track.json') || (film?._doc || '').includes('KAPE');

  const stages = [
    {
      stage: '0',
      name: 'SCRIPT (Baet writes -> Alvin approves)',
      done: exists('SCRIPT.md'),
      detail: exists('SCRIPT.md') ? 'SCRIPT.md present' : 'Pending SCRIPT.md',
    },
    {
      stage: '1',
      name: 'NARRATION (Alvin records/provides MP3)',
      done: exists('assets/audio/vo.mp3'),
      detail: exists('assets/audio/vo.mp3') ? 'assets/audio/vo.mp3 present' : 'Waiting for Alvin MP3',
    },
    {
      stage: '2',
      name: 'INTAKE (Scaffold -> Whisper timings -> -16 LUFS master -> scene map)',
      done: exists('film.json') && exists('src/timing/vo-words.json') && exists('assets/audio/vo-master.wav'),
      detail: [
        exists('film.json') ? 'film.json:ok' : 'film.json:missing',
        exists('src/timing/vo-words.json') ? 'vo-words.json:ok' : 'vo-words.json:missing',
        exists('assets/audio/vo-master.wav') ? 'vo-master.wav:ok' : 'vo-master.wav:missing',
      ].join(', '),
    },
    {
      stage: '3',
      name: 'STORYBOARD + DESIGN LAW (frame.md, m-kape, m-brand -> Alvin says "GO")',
      done: exists('STORYBOARD.md') && exists('frame.md') && exists('compositions/m-kape.html') && exists('compositions/m-brand.html') && storyboardLocked,
      detail: [
        exists('STORYBOARD.md') ? (storyboardLocked ? 'STORYBOARD:locked' : 'STORYBOARD:awaiting Alvin GO') : 'STORYBOARD:missing',
        exists('compositions/m-kape.html') ? 'm-kape:ok' : 'm-kape:missing',
        exists('compositions/m-brand.html') ? 'm-brand:ok' : 'm-brand:missing',
      ].join(', '),
    },
    {
      stage: '4',
      name: 'SCENE BUILDS (Frame packets -> max 4 parallel crews -> contact sheets)',
      done: sceneIds.length > 0 && builtScenes.length === sceneIds.length,
      detail: `${builtScenes.length}/${sceneIds.length} scene compositions built`,
    },
    {
      stage: '5-6',
      name: 'QUALITY GATES (fromto-scan, assemble, check, masked seams, composite review)',
      done: !!gates?.all_automated_passed,
      detail: gates
        ? Object.entries(gates.gates || {}).map(([k, v]) => `${k}:${v.status}`).join(', ')
        : 'Not run yet (run-gates.mjs)',
    },
    {
      stage: '7',
      name: 'PACKAGE (ZIP + render.command, SCRIPT.md, CAPTIONS.srt, UPLOAD-PACK.md, covers)',
      done: exists('CAPTIONS.srt') && exists('render.command') && exists('UPLOAD-PACK.md') && exists('THUMBNAIL.png') && exists('TIKTOK-COVER.png'),
      detail: [
        exists('CAPTIONS.srt') ? 'CAPTIONS.srt:ok' : 'CAPTIONS.srt:missing',
        exists('render.command') ? 'render.command:ok' : 'render.command:missing',
        exists('UPLOAD-PACK.md') ? 'UPLOAD-PACK.md:ok' : 'UPLOAD-PACK.md:missing',
        exists('THUMBNAIL.png') ? 'THUMBNAIL.png:ok' : 'THUMBNAIL.png:missing',
        exists('TIKTOK-COVER.png') ? 'TIKTOK-COVER.png:ok' : 'TIKTOK-COVER.png:missing',
      ].join(', '),
    },
    {
      stage: '8',
      name: 'RENDER + PROOF (Alvin M2 GPU render -> Baet word-sync proof -> Alvin uploads)',
      done: !!proof?.passed,
      detail: proof
        ? `ffprobe:${proof.ffprobe?.passed ? 'PASS' : 'FAIL'}, word-sync:${proof.word_sync?.passed ? 'PASS' : 'FAIL'} (${proof.word_sync?.match_ratio ?? '?'}%, median ${proof.word_sync?.median_offset_s ?? '?'}s)`
        : 'Pending final render & verify-render.mjs',
    },
  ];

  const firstTodo = stages.find((s) => !s.done);
  return {
    name: film?.name || path.basename(root),
    root,
    workflow: isKape ? (brand?.workflow || 'kape-explainer-0-8') : 'spatial-film',
    brandName: brand?.name || (isKape ? 'Tech Explanasyon' : 'Standalone'),
    profileId: brand?.profile || 'default',
    currentStage: firstTodo ? `Stage ${firstTodo.stage}` : 'COMPLETE (Ready to Upload)',
    stages,
  };
}

function discoverProjects() {
  const dirs = new Set();
  const home = homeDir();
  const defaultFilmsDir = path.join(home, 'films');
  if (fs.existsSync(defaultFilmsDir)) dirs.add(defaultFilmsDir);
  for (const p of listProfiles()) {
    if (p.brand?.films_dir) {
      const fd = path.resolve(expandHome(p.brand.films_dir));
      if (fs.existsSync(fd)) dirs.add(fd);
    }
  }
  const projects = [];
  for (const parent of dirs) {
    for (const e of fs.readdirSync(parent, { withFileTypes: true })) {
      if (!e.isDirectory()) continue;
      const full = path.join(parent, e.name);
      if (fs.existsSync(path.join(full, 'film.json')) || fs.existsSync(path.join(full, 'SCRIPT.md'))) {
        projects.push(inspectFilm(full));
      }
    }
  }
  return projects;
}

const isSingleFilm = !wantAll && (fs.existsSync(path.join(targetDir, 'film.json')) || fs.existsSync(path.join(targetDir, 'SCRIPT.md')));

if (isSingleFilm) {
  const info = inspectFilm(targetDir);
  console.log(`=== KAPE Pipeline Status: ${info.name} [${info.brandName} | ${info.workflow}] (${info.root}) ===`);
  for (const s of info.stages) {
    console.log(`[${s.done ? 'DONE' : 'TODO'}] Stage ${s.stage.padEnd(3)} | ${s.name}`);
    console.log(`             └─ ${s.detail}`);
  }
} else {
  const profiles = listProfiles();
  console.log('=== Registered Channel Profiles ===');
  for (const p of profiles) {
    console.log(`  • ${p.id.padEnd(16)} : ${p.brand.name} (films_dir: ${p.brand.films_dir})`);
  }
  const projects = discoverProjects();
  console.log(`\n=== Film Projects (${projects.length}) ===`);
  if (!projects.length) {
    console.log('  (No film projects scaffolded yet in films/)');
  } else {
    for (const proj of projects) {
      console.log(`  • ${proj.name.padEnd(24)} | ${proj.brandName.padEnd(18)} | ${proj.workflow.padEnd(18)} | ${proj.currentStage} | ${proj.root}`);
    }
  }
}
