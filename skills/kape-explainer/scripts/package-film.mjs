#!/usr/bin/env node
// Stage 7 Packager for KAPE Explainer films (PIPELINE.md Phase 7).
// Verifies Quality Gates passed, generates CAPTIONS.srt from src/timing/vo-words.json,
// writes render-final.mjs + render.command + RENDER-ON-MAC.md into the project,
// creates <slug>-project.zip (excluding .hyperframes/, snapshots/, renders/, .media/, package/),
// and verifies/collects the upload pack deliverables (SCRIPT.md, CAPTIONS.srt, UPLOAD-PACK.md,
// THUMBNAIL.png 1280x720, TIKTOK-COVER.png 1080x1920) into <out_dir>.
// Usage (from film root): node <skill>/scripts/package-film.mjs [--dir <film_dir>] [--out <out_dir>] [--allow-incomplete-pack]

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { python } from './lib/python.mjs';

const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ENGINE = path.resolve(SKILL, '..', 'spatial-film');
const args = process.argv.slice(2);
const flag = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const has = (k) => args.includes(k);

const root = path.resolve(flag('--dir') || process.cwd());
const filmPath = path.join(root, 'film.json');
if (!fs.existsSync(filmPath)) {
  console.error(`package-film: film.json not found in ${root}`);
  process.exit(1);
}
const film = JSON.parse(fs.readFileSync(filmPath, 'utf8'));
const slug = film.name || path.basename(root);
const outDir = path.resolve(flag('--out') || path.join(root, 'package'));

// 1. Enforce Quality Gates report unless explicitly bypassed
const gatesReportPath = path.join(root, '.hyperframes', 'gates-report.json');
if (!has('--skip-gate-check')) {
  if (!fs.existsSync(gatesReportPath)) {
    console.error('package-film: .hyperframes/gates-report.json not found. Run Stage 5-6 Quality Gates (run-gates.mjs) first.');
    process.exit(1);
  }
  const gatesReport = JSON.parse(fs.readFileSync(gatesReportPath, 'utf8'));
  if (!gatesReport.all_automated_passed) {
    console.error('package-film: Quality Gates did not pass in .hyperframes/gates-report.json. Nothing ships on a failed gate.');
    process.exit(1);
  }
}

fs.mkdirSync(outDir, { recursive: true });

// 2. Generate CAPTIONS.srt from src/timing/vo-words.json if present
const voWordsPath = path.join(root, 'src', 'timing', 'vo-words.json');
const srtPath = path.join(root, 'CAPTIONS.srt');
function fmtSrtTime(sec) {
  const msTotal = Math.max(0, Math.round(sec * 1000));
  const ms = msTotal % 1000;
  const sTotal = Math.floor(msTotal / 1000);
  const s = sTotal % 60;
  const mTotal = Math.floor(sTotal / 60);
  const m = mTotal % 60;
  const h = Math.floor(mTotal / 60);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')},${String(ms).padStart(3, '0')}`;
}

if (fs.existsSync(voWordsPath)) {
  const segs = JSON.parse(fs.readFileSync(voWordsPath, 'utf8'));
  const blocks = segs
    .filter((seg) => seg.text && seg.text.trim())
    .map((seg, idx) => `${idx + 1}\n${fmtSrtTime(seg.s)} --> ${fmtSrtTime(seg.e)}\n${seg.text.trim()}\n`);
  fs.writeFileSync(srtPath, blocks.join('\n'), 'utf8');
  console.log(`OK       CAPTIONS.srt generated (${blocks.length} subtitle blocks)`);
} else if (!fs.existsSync(srtPath)) {
  console.warn('WARN     src/timing/vo-words.json not found; CAPTIONS.srt could not be auto-generated');
}

// 3. Copy render-final.mjs + write render.command + RENDER-ON-MAC.md into film root
const hfVer = film.hyperframes || '0.8.117';
const fps = film.fps || 60;
fs.copyFileSync(path.join(ENGINE, 'scripts', 'render-final.mjs'), path.join(root, 'render-final.mjs'));

const renderCmd = `#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== Rendering ${slug} at ${film.width}x${film.height} @ ${fps}fps (Hardware GPU) ==="
node render-final.mjs "${slug}-1080p60"
echo ""
echo "=== Render complete: renders/${slug}-1080p60.mp4 ==="
`;
const renderCmdPath = path.join(root, 'render.command');
fs.writeFileSync(renderCmdPath, renderCmd, { encoding: 'utf8', mode: 0o755 });
fs.chmodSync(renderCmdPath, 0o755);

const renderMd = `# Render ${slug} on Mac (Apple Silicon GPU)

## One-Click Render
Double-click \`render.command\` in Finder (or run \`./render.command\` in Terminal).

## Direct CLI Command
\`\`\`bash
npx --prefer-offline --yes hyperframes@${hfVer} render --fps ${fps} --browser-gpu --workers 6 -o renders/${slug}-1080p60.mp4
\`\`\`

## Output
- Rendered MP4: \`renders/${slug}-1080p60.mp4\`
- Render log: \`renders/${slug}-1080p60.log\`

Once rendered, hand \`renders/${slug}-1080p60.mp4\` to Baet for the **Stage 8 word-sync proof** (\`verify-render.mjs\`) before uploading.
`;
fs.writeFileSync(path.join(root, 'RENDER-ON-MAC.md'), renderMd, 'utf8');
console.log('OK       render-final.mjs, render.command, RENDER-ON-MAC.md written');

// 4. Create <slug>-project.zip (minus .hyperframes/, snapshots/, renders/, .media/, package/, .DS_Store)
const zipPath = path.join(outDir, `${slug}-project.zip`);
if (fs.existsSync(zipPath)) fs.rmSync(zipPath);
const zipRes = spawnSync(
  'zip',
  [
    '-r',
    '-q',
    zipPath,
    '.',
    '-x',
    '.hyperframes/*',
    'snapshots/*',
    'renders/*',
    '.media/*',
    'package/*',
    '*.DS_Store',
    '.git/*',
    'node_modules/*',
  ],
  { cwd: root, encoding: 'utf8' }
);
if (zipRes.status !== 0) {
  console.error(`package-film: zip failed: ${zipRes.stderr || zipRes.stdout}`);
  process.exit(1);
}
console.log(`OK       ${path.basename(zipPath)} created`);

// 5. Copy & verify deliverables in outDir
const [py, ...pyArgs] = python();
function checkImageSize(filePath, wantW, wantH) {
  if (!fs.existsSync(filePath)) return { exists: false, ok: false, detail: 'missing' };
  const r = spawnSync(py, [...pyArgs, '-c', `from PIL import Image; im=Image.open(${JSON.stringify(filePath)}); print(f"{im.width}x{im.height}")`], { encoding: 'utf8' });
  const got = (r.stdout || '').trim();
  const ok = got === `${wantW}x${wantH}`;
  return { exists: true, ok, detail: got || 'unreadable' };
}

const deliverables = [
  { file: 'SCRIPT.md', required: true },
  { file: 'CAPTIONS.srt', required: true },
  { file: 'UPLOAD-PACK.md', required: true },
  { file: 'THUMBNAIL.png', required: true, size: [1280, 720] },
  { file: 'TIKTOK-COVER.png', required: true, size: [1080, 1920] },
];

let missingDeliverables = 0;
for (const d of deliverables) {
  const src = path.join(root, d.file);
  const dst = path.join(outDir, d.file);
  if (fs.existsSync(src)) {
    if (path.resolve(src) !== path.resolve(dst)) fs.copyFileSync(src, dst);
    if (d.size) {
      const sz = checkImageSize(src, d.size[0], d.size[1]);
      if (sz.ok) console.log(`OK       ${d.file} (${sz.detail})`);
      else {
        console.warn(`WARN     ${d.file} dimension is ${sz.detail} (expected ${d.size[0]}x${d.size[1]})`);
        if (!has('--allow-incomplete-pack')) missingDeliverables++;
      }
    } else {
      console.log(`OK       ${d.file}`);
    }
  } else {
    console.warn(`MISSING  ${d.file}`);
    if (d.required && !has('--allow-incomplete-pack')) missingDeliverables++;
  }
}

if (missingDeliverables > 0) {
  console.error(`\npackage-film: ${missingDeliverables} deliverable check(s) incomplete. Complete them or pass --allow-incomplete-pack.`);
  process.exit(1);
}
console.log(`\nStage 7 Package ready at: ${outDir}`);
