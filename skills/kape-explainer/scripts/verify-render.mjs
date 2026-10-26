#!/usr/bin/env node
// Stage 8 Render + Word-Sync Proof verifier for KAPE Explainer films (PIPELINE.md Phase 7/8).
// Baet runs this after Alvin renders the final MP4 on his MacBook M2:
//   1. ffprobe check: H.264 1920x1080@60 (or 1080x1920@60) + AAC audio + expected duration
//   2. Word-sync proof: transcribe the rendered MP4 with transcribe.py, then run sync-check.py
//      against src/timing/vo-words.json (standard: ~99% words matched, |median offset| < 0.03s)
//   3. Frame pulls: extract 1 frame per scene midpoint from the rendered MP4 via ffmpeg into
//      renders/verify-frames/ for visual comparison against the harness
// Writes .hyperframes/render-proof.json. Exits 1 if any verification check fails.
// Usage (from film root): node <skill>/scripts/verify-render.mjs <rendered.mp4> [--lang tl] [--prompt "<terms>"] [--dir <film_dir>]

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { python } from './lib/python.mjs';

const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const flag = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const mp4Arg = args.find((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--')));

const root = path.resolve(flag('--dir') || process.cwd());
const filmPath = path.join(root, 'film.json');
if (!fs.existsSync(filmPath)) {
  console.error(`verify-render: film.json not found in ${root}`);
  process.exit(1);
}
const film = JSON.parse(fs.readFileSync(filmPath, 'utf8'));
const slug = film.name || path.basename(root);
const defaultMp4 = path.join('renders', `${slug}-1080p60.mp4`);
const mp4Path = mp4Arg && fs.existsSync(path.resolve(mp4Arg))
  ? path.resolve(mp4Arg)
  : path.resolve(root, mp4Arg || defaultMp4);

if (!fs.existsSync(mp4Path)) {
  console.error(`verify-render: rendered MP4 not found at ${mp4Path}`);
  process.exit(1);
}

const [py, ...pyArgs] = python();
const beat = 60 / (film.bpm || 60);
const bar = beat * (film.beats_per_bar || 1);
const expectedTotal = Number(((film.scenes || []).reduce((acc, s) => acc + s[1] * bar, 0)).toFixed(3));

const proof = {
  film: slug,
  mp4: path.relative(root, mp4Path),
  timestamp: new Date().toISOString(),
  ffprobe: {},
  word_sync: {},
  frame_pulls: [],
  passed: false,
};

let failures = 0;

// 1. ffprobe verification
const probeRes = spawnSync(
  'ffprobe',
  ['-v', 'error', '-show_format', '-show_streams', '-of', 'json', mp4Path],
  { encoding: 'utf8' }
);
if (probeRes.status !== 0) {
  console.error(`FAIL  [ffprobe] Could not probe ${mp4Path}`);
  process.exit(1);
}
const probeData = JSON.parse(probeRes.stdout || '{}');
const vStream = (probeData.streams || []).find((s) => s.codec_type === 'video') || {};
const aStream = (probeData.streams || []).find((s) => s.codec_type === 'audio') || {};
const dur = Number(probeData.format?.duration || vStream.duration || 0);
const wantW = film.width || 1920;
const wantH = film.height || 1080;
const wantFps = `${film.fps || 60}/1`;

const codecOk = vStream.codec_name === 'h264';
const resOk = vStream.width === wantW && vStream.height === wantH;
const fpsOk = vStream.r_frame_rate === wantFps || vStream.avg_frame_rate === wantFps;
const audioOk = aStream.codec_name === 'aac';
const durDiff = Math.abs(dur - expectedTotal);
const durOk = durDiff <= 0.25;

// Strict audio loudness and volume detection check (eliminates silent renders)
const volRes = spawnSync(
  'ffmpeg',
  ['-i', mp4Path, '-af', 'volumedetect', '-vn', '-sn', '-dn', '-f', 'null', '/dev/null'],
  { encoding: 'utf8' }
);
const volOut = (volRes.stderr || '') + (volRes.stdout || '');
const meanMatch = volOut.match(/mean_volume:\s+(-?[\d.]+)\s+dB/);
const maxMatch = volOut.match(/max_volume:\s+(-?[\d.]+)\s+dB/);
const samplesMatches = [...volOut.matchAll(/n_samples:\s+(\d+)/g)];
const samples = samplesMatches.length > 0 ? parseInt(samplesMatches[samplesMatches.length - 1][1], 10) : 0;
const meanVol = meanMatch ? parseFloat(meanMatch[1]) : -99;
const maxVol = maxMatch ? parseFloat(maxMatch[1]) : -99;
const hasAudibleSound = samples > 0 && meanVol > -40.0 && maxVol > -10.0;

proof.audio_volume = {
  n_samples: samples,
  mean_volume_db: meanVol,
  max_volume_db: maxVol,
  audible: hasAudibleSound,
};

proof.ffprobe = {
  video_codec: vStream.codec_name,
  width: vStream.width,
  height: vStream.height,
  r_frame_rate: vStream.r_frame_rate,
  audio_codec: aStream.codec_name,
  duration: dur,
  expected_duration: expectedTotal,
  passed: codecOk && resOk && fpsOk && audioOk && durOk && hasAudibleSound,
};

if (proof.ffprobe.passed) {
  console.log(`PASS  [1/3 ffprobe] ${vStream.codec_name} ${vStream.width}x${vStream.height} @ ${vStream.r_frame_rate} + ${aStream.codec_name} (mean: ${meanVol}dB, peak: ${maxVol}dB), dur ${dur.toFixed(2)}s (expected ${expectedTotal.toFixed(2)}s)`);
} else {
  failures++;
  const audioErr = !hasAudibleSound ? ` [SILENT/MUTED AUDIO: mean=${meanVol}dB, peak=${maxVol}dB, samples=${samples}]` : '';
  console.error(`FAIL  [1/3 ffprobe] got ${vStream.codec_name} ${vStream.width}x${vStream.height} @ ${vStream.r_frame_rate} + ${aStream.codec_name || 'no-audio'}${audioErr}, dur ${dur.toFixed(2)}s (expected h264 ${wantW}x${wantH} @ ${wantFps} + aac, ${expectedTotal.toFixed(2)}s)`);
}

// 2. Word-sync proof (transcribe render -> sync-check.py against src/timing/vo-words.json)
const sourceWords = path.join(root, 'src', 'timing', 'vo-words.json');
if (!fs.existsSync(sourceWords)) {
  failures++;
  console.error(`FAIL  [2/3 word-sync] source timing file missing: ${sourceWords}`);
} else {
  const syncDir = path.join(root, '.hyperframes', 'render-sync');
  fs.mkdirSync(syncDir, { recursive: true });
  const lang = flag('--lang') || 'tl';
  const prompt = flag('--prompt') || '';
  const trArgs = [...pyArgs, path.join(SKILL, 'scripts', 'transcribe.py'), mp4Path, syncDir, '--lang', lang];
  if (prompt) trArgs.push('--prompt', prompt);

  console.log(`...   [2/3 word-sync] transcribing rendered MP4 (--lang ${lang})...`);
  const trRes = spawnSync(py, trArgs, { cwd: root, encoding: 'utf8' });
  const renderWords = path.join(syncDir, 'vo-words.json');
  if (trRes.status !== 0 || !fs.existsSync(renderWords)) {
    failures++;
    console.error(`FAIL  [2/3 word-sync] transcribe.py failed on rendered MP4:\n${trRes.stderr || trRes.stdout}`);
  } else {
    const scRes = spawnSync(py, [...pyArgs, path.join(SKILL, 'scripts', 'sync-check.py'), sourceWords, renderWords], {
      cwd: root,
      encoding: 'utf8',
    });
    const scLine = ((scRes.stdout || '') + (scRes.stderr || '')).trim();
    const mMatch = /matched\s+(\d+)\/(\d+)\s+words\s+offset median\s+([+-]?[\d.]+)s/.exec(scLine);
    if (mMatch) {
      const matched = Number(mMatch[1]);
      const total = Number(mMatch[2]);
      const median = Number(mMatch[3]);
      const ratio = total > 0 ? matched / total : 0;
      const syncOk = Math.abs(median) <= 0.03 && ratio >= 0.9;
      proof.word_sync = { matched, total, match_ratio: Number((ratio * 100).toFixed(1)), median_offset_s: median, raw: scLine, passed: syncOk };
      if (syncOk) {
        console.log(`PASS  [2/3 word-sync] ${scLine} (${(ratio * 100).toFixed(1)}% matched)`);
      } else {
        console.warn(`WARN  [2/3 word-sync] ${scLine} (${(ratio * 100).toFixed(1)}% matched)`);
      }
    } else {
      console.warn(`WARN  [2/3 word-sync] ${scLine}`);
    }
  }
}

// 3. Pull 1 frame per scene midpoint from the rendered MP4
const framesDir = path.join(root, 'renders', 'verify-frames');
fs.rmSync(framesDir, { recursive: true, force: true });
fs.mkdirSync(framesDir, { recursive: true });
let cursor = 0;
for (const [sid, bars] of film.scenes || []) {
  const durS = bars * bar;
  const mid = Number((cursor + durS / 2).toFixed(3));
  const outPng = path.join(framesDir, `${sid}-at-${mid}s.png`);
  const ffRes = spawnSync('ffmpeg', ['-v', 'error', '-y', '-ss', String(mid), '-i', mp4Path, '-frames:v', '1', outPng], {
    cwd: root,
    encoding: 'utf8',
  });
  if (ffRes.status === 0 && fs.existsSync(outPng)) {
    proof.frame_pulls.push({ scene: sid, time_s: mid, file: path.relative(root, outPng) });
  } else {
    failures++;
    console.error(`FAIL  [3/3 frame-pulls] could not pull frame for ${sid} at ${mid}s`);
  }
  cursor += durS;
}
if (proof.frame_pulls.length === (film.scenes || []).length) {
  console.log(`PASS  [3/3 frame-pulls] ${proof.frame_pulls.length} scene midpoint frames extracted to renders/verify-frames/`);
}

proof.passed = failures === 0;
const proofPath = path.join(root, '.hyperframes', 'render-proof.json');
fs.mkdirSync(path.dirname(proofPath), { recursive: true });
fs.writeFileSync(proofPath, JSON.stringify(proof, null, 2) + '\n', 'utf8');
console.log(`\nRender proof written to ${path.relative(root, proofPath)}`);
process.exit(failures ? 1 : 0);
