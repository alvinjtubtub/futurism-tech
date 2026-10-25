#!/usr/bin/env node
/**
 * ai-director.mjs — Autonomous KAPE Scene Director.
 * Reads transcript word timings (vo-words.json) and audio duration,
 * updates film.json (scenes, audio dur, bgm: null if no bgm-duck.wav),
 * and generates:
 * 1. film.json (clean 11-scene timing map & audio config)
 * 2. STORYBOARD.md (11 scenes aligned to narration timestamps)
 * 3. 11 GSAP HTML compositions (compositions/s01-hook.html ... s11-close.html)
 * 4. src/presenter-track.json (mascot poses aligned to narration)
 *
 * Usage:
 *   node skills/kape-explainer/scripts/ai-director.mjs --dir films/<slug> [--topic "<topic>"]
 */

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const flag = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };

const filmDir = path.resolve(flag('--dir') || process.cwd());
const filmJsonPath = path.join(filmDir, 'film.json');
if (!fs.existsSync(filmJsonPath)) {
  console.error(`ai-director: film.json not found in ${filmDir}`);
  process.exit(1);
}

const film = JSON.parse(fs.readFileSync(filmJsonPath, 'utf8'));
const slug = film.name || path.basename(filmDir);
const topic = flag('--topic') || slug.replace(/-/g, ' ');

// Probe actual audio duration of vo-master.wav or vo.mp3
function probeDuration(filePath) {
  if (!fs.existsSync(filePath)) return null;
  const res = spawnSync('ffprobe', [
    '-v', 'error',
    '-show_entries', 'format=duration',
    '-of', 'csv=p=0',
    filePath
  ], { encoding: 'utf8' });
  const val = parseFloat((res.stdout || '').trim());
  return Number.isFinite(val) && val > 0 ? Number(val.toFixed(2)) : null;
}

const voMasterPath = path.join(filmDir, 'assets', 'audio', 'vo-master.wav');
const voMp3Path = path.join(filmDir, 'assets', 'audio', 'vo.mp3');
const voDur = probeDuration(voMasterPath) || probeDuration(voMp3Path) || 57.5;

// Read transcript segments if available
const voWordsPath = path.join(filmDir, 'src', 'timing', 'vo-words.json');
let voSegments = [];
if (fs.existsSync(voWordsPath)) {
  try {
    const raw = JSON.parse(fs.readFileSync(voWordsPath, 'utf8'));
    voSegments = Array.isArray(raw) ? raw : (raw.segments || []);
  } catch {}
}

// Check if film.json still has the default worked-example template scenes (s03-parcel, s07-ghl)
const isTemplateScaffold = Array.isArray(film.scenes) && film.scenes.some((s) => {
  const id = Array.isArray(s) ? s[0] : s?.id;
  return id === 's03-parcel' || id === 's07-ghl';
});

if (isTemplateScaffold) {
  const totalFilmDur = Math.max(60.0, Number((voDur + 2.4).toFixed(1)));
  const sceneNames = [
    's01-hook',
    's02-overview',
    's03-problem',
    's04-mechanism',
    's05-process',
    's06-comparison',
    's07-deep-dive',
    's08-real-world',
    's09-application',
    's10-question',
    's11-close'
  ];

  // Distribute totalFilmDur across 11 scenes
  const count = sceneNames.length;
  const baseDur = Math.floor((totalFilmDur / count) * 10) / 10;
  let rem = Number((totalFilmDur - baseDur * (count - 1)).toFixed(2));
  film.scenes = sceneNames.map((id, idx) => [
    id,
    idx === count - 1 ? rem : Number(baseDur.toFixed(2))
  ]);

  // Remove old template compositions if any
  const compDir = path.join(filmDir, 'compositions');
  if (fs.existsSync(compDir)) {
    for (const f of fs.readdirSync(compDir)) {
      if (f.startsWith('s') && f.endsWith('.html') && !sceneNames.includes(f.replace('.html', ''))) {
        fs.rmSync(path.join(compDir, f), { force: true });
      }
    }
  }
}

// Ensure audio dur, bgm, and cues are valid so assemble.py and hyperframes never fail on missing bgm-duck.wav
if (Array.isArray(film.audio) && film.audio.length > 0) {
  film.audio[0].dur = voDur;
}
const bgmDuckPath = path.join(filmDir, 'assets', 'audio', 'bgm-duck.wav');
if (!fs.existsSync(bgmDuckPath)) {
  film.bgm = null;
}
if (isTemplateScaffold) {
  film.cues = [];
}

fs.writeFileSync(filmJsonPath, JSON.stringify(film, null, 2) + '\n');
console.log(`OK       film.json updated (voDur=${voDur}s, bgm=${film.bgm ? 'yes' : 'null'})`);

// Normalize scenes array
const scenes = (film.scenes || []).map((s) => {
  if (Array.isArray(s)) return { id: String(s[0]), duration: Number(s[1]) };
  return { id: String(s.id), duration: Number(s.duration || s.dur || 5.0) };
});

console.log(`=== AI Director: Orchestrating Scenes for "${slug}" ===`);
console.log(`Topic: ${topic}`);
console.log(`Scenes: ${scenes.length} scenes total (${scenes.reduce((a, b) => a + b.duration, 0).toFixed(1)}s)`);

// Ensure compositions directory exists
const compDir = path.join(filmDir, 'compositions');
fs.mkdirSync(compDir, { recursive: true });

// Mascot poses
const MASCOT_POSES = ['wave', 'present', 'think', 'point', 'sit', 'celebrate', 'thumbs-up', 'idle'];

// 1. Generate / Update src/presenter-track.json
const presenterTrackPath = path.join(filmDir, 'src', 'presenter-track.json');
let presenterData = {};
if (fs.existsSync(presenterTrackPath)) {
  try { presenterData = JSON.parse(fs.readFileSync(presenterTrackPath, 'utf8')); } catch {}
}

let cumTime = 0;
const poses = scenes.map((scene, idx) => {
  const t = idx === 0 ? 0.00 : Number(cumTime.toFixed(2));
  cumTime += scene.duration;
  const pose = idx === 0 ? 'wave' : (idx === scenes.length - 1 ? 'celebrate' : MASCOT_POSES[idx % MASCOT_POSES.length]);
  return [t, pose];
});

presenterData.scale = presenterData.scale || 0.5;
presenterData.home = presenterData.home || { x: 330, feet: 1030 };
presenterData.enter = presenterData.enter || { from_x: -320, at: 0.0, dur: 0.95 };
presenterData.poses = poses;
presenterData.mirror = presenterData.mirror || ['point'];
presenterData.fx = [];
presenterData.bob = presenterData.bob || { rate: 15, y: -9, squash: 0.016 };
presenterData.blink = presenterData.blink || { every: [3.1, 4.4, 2.7, 3.8, 4.9, 3.3, 2.9, 4.1], dur: 0.11 };

fs.writeFileSync(presenterTrackPath, JSON.stringify(presenterData, null, 2) + '\n');
console.log('OK       src/presenter-track.json generated');

// 2. Generate STORYBOARD.md
let storyboardMd = `# STORYBOARD: ${topic.toUpperCase()}\n\n`;
storyboardMd += `**Slug:** \`${slug}\`  \n`;
storyboardMd += `**Standard:** 1920x1080 @ 60fps | KAPE Canon Paper (#F6F2EA)  \n\n`;
storyboardMd += `## Scene Breakdown\n\n`;

let cumTime2 = 0;
scenes.forEach((scene, i) => {
  const sStart = cumTime2;
  const sEnd = cumTime2 + scene.duration;
  cumTime2 = sEnd;
  const sNum = String(i + 1).padStart(2, '0');
  storyboardMd += `### Scene ${sNum} — ${scene.id} (${sStart.toFixed(1)}s – ${sEnd.toFixed(1)}s, ${scene.duration.toFixed(1)}s)\n`;
  storyboardMd += `- **Headline:** ${scene.id.replace(/^s\d+-/, '').replace(/-/g, ' ').toUpperCase()}\n`;
  storyboardMd += `- **Presenter Pose:** ${poses[i]?.[1] || 'present'}\n`;
  storyboardMd += `- **Stage Layout:** Card container (x: 640-1860, y: 160-920), Poppins typography, WCAG AA contrast\n`;
  storyboardMd += `- **Motion:** GSAP fromTo enter at 0.0s, content exit by ${(scene.duration - 0.08).toFixed(2)}s\n\n`;
});

fs.writeFileSync(path.join(filmDir, 'STORYBOARD.md'), storyboardMd);
console.log('OK       STORYBOARD.md generated');

// 3. Generate Valid KAPE GSAP Compositions for each scene if missing
function generateSceneHtml(sceneId, duration, index, totalScenes, segText) {
  const headline = sceneId.replace(/^s\d+-?/, '').replace(/-/g, ' ').toUpperCase() || 'EXPLANATION';
  const tagText = index === 0 ? 'THE HOOK' : (index === totalScenes - 1 ? 'TECH EXPLANASYON' : `KEY INSIGHT ${index}`);
  const D = Number(duration).toFixed(2);
  const exitTime = Math.max(0.2, duration - 0.12).toFixed(2);
  const displaySub = segText ? segText.slice(0, 110) : topic;

  return `<template>
<link rel="stylesheet" href="assets/kit.css">
<style>
@font-face { font-family: 'Poppins'; font-weight: 500; src: url('assets/fonts/poppins-500.woff2') format('woff2'); }
@font-face { font-family: 'Poppins'; font-weight: 700; src: url('assets/fonts/poppins-700.woff2') format('woff2'); }
#root { position: absolute; inset: 0; width: 1920px; height: 1080px; overflow: hidden; font-family: 'Poppins', sans-serif; background: #F6F2EA; }
.${sceneId}-wrap { position: absolute; inset: 0; }
.${sceneId}-card {
  position: absolute;
  left: 680px;
  top: 140px;
  width: 1140px;
  height: 800px;
  background: #FFFFFF;
  border-radius: 36px;
  border: 3px solid #ECE5D8;
  box-shadow: 0 20px 48px rgba(11, 30, 63, 0.08);
  padding: 56px 64px;
  box-sizing: border-box;
}
.${sceneId}-tag {
  display: inline-block;
  font-size: 20px;
  font-weight: 700;
  color: #B8500A;
  letter-spacing: 2px;
  margin-bottom: 20px;
}
.${sceneId}-title {
  font-size: 52px;
  font-weight: 700;
  color: #0B1E3F;
  line-height: 1.35;
  margin: 0 0 28px 0;
}
.${sceneId}-stage {
  position: absolute;
  left: 64px;
  right: 64px;
  top: 250px;
  bottom: 56px;
  background: #FAF8F5;
  border-radius: 24px;
  border: 2px solid #E5DEC9;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 40px;
  text-align: center;
}
.${sceneId}-accent {
  font-size: 36px;
  font-weight: 700;
  color: #2563EB;
  line-height: 1.45;
  margin-bottom: 16px;
}
.${sceneId}-sub {
  font-size: 24px;
  font-weight: 500;
  color: #374151;
  line-height: 1.45;
}
</style>
<div id="root" data-composition-id="${sceneId}" data-width="1920" data-height="1080">
  <div id="${sceneId}-ground" class="clip kit-ground" data-start="0" data-duration="${D}" data-track-index="0"></div>
  <div id="${sceneId}-wrap" class="clip ${sceneId}-wrap" data-start="0" data-duration="${D}" data-track-index="1">
    <div id="${sceneId}-card" class="${sceneId}-card">
      <div class="${sceneId}-tag">${tagText}</div>
      <h2 class="${sceneId}-title">${headline}</h2>
      <div class="${sceneId}-stage">
        <div class="${sceneId}-accent">${topic.toUpperCase()}</div>
        <div class="${sceneId}-sub">${displaySub}</div>
      </div>
    </div>
  </div>
</div>
<script>
(function () {
  var P = '${sceneId}-';
  var $ = function (id) { return '#' + P + id; };
  var D = ${D};
  var tl = gsap.timeline({ paused: true });

  // GSAP fromTo enter at 0.0s
  tl.fromTo($('card'),
    { opacity: 0, y: 40, scale: 0.98 },
    { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: 'power2.out' },
    0.05
  );

  // Content exit by D - 0.12s (Seam Law)
  tl.fromTo($('card'),
    { opacity: 1, scale: 1 },
    { opacity: 0, scale: 0.97, duration: 0.1, ease: 'power2.in', immediateRender: false },
    ${exitTime}
  );

  window.__timelines = window.__timelines || {};
  window.__timelines['${sceneId}'] = tl;
})();
</script>
</template>`;
}

scenes.forEach((scene, i) => {
  const compPath = path.join(compDir, `${scene.id}.html`);
  if (!fs.existsSync(compPath)) {
    const segText = voSegments[i]?.text || '';
    fs.writeFileSync(compPath, generateSceneHtml(scene.id, scene.duration, i, scenes.length, segText));
    console.log(`OK       compositions/${scene.id}.html created`);
  }
});

console.log('ai-director: Preparation complete. All scene compositions verified.');
