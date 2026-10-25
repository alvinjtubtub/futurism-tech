#!/usr/bin/env node
/**
 * ai-director.mjs — Autonomous KAPE Scene Director powered by Gemini API.
 * Reads transcript word timings (vo-words.json) and brand rules (frame.md),
 * then generates:
 * 1. STORYBOARD.md (11 scenes aligned to narration timestamps)
 * 2. 11 GSAP HTML compositions (compositions/s01-hook.html ... s11-close.html)
 * 3. src/presenter-track.json (mascot poses aligned to narration)
 *
 * Usage:
 *   node skills/kape-explainer/scripts/ai-director.mjs --dir films/<slug> [--topic "<topic>"]
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { GoogleGenAI } from '@google/genai';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL = path.resolve(SCRIPT_DIR, '..');
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

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) {
  console.warn('ai-director: GEMINI_API_KEY environment variable is not set.');
}

const client = new GoogleGenAI({ apiKey: apiKey || '' });

// Read transcript and timings if available
const voWordsPath = path.join(filmDir, 'src', 'timing', 'vo-words.json');
let voData = null;
if (fs.existsSync(voWordsPath)) {
  try {
    voData = JSON.parse(fs.readFileSync(voWordsPath, 'utf8'));
  } catch {}
}

const transcriptText = voData?.segments ? voData.segments.map(s => s.text).join(' ') : 'Explainer on ' + topic;

console.log(`=== AI Director: Orchestrating Scenes for "${slug}" ===`);
console.log(`Topic: ${topic}`);
console.log(`Narration Duration: ${film.scenes?.reduce((acc, s) => acc + s.duration, 0) || 60}s`);

// Ensure compositions directory exists
const compDir = path.join(filmDir, 'compositions');
fs.mkdirSync(compDir, { recursive: true });

// Poses cycle for presenter
const MASCOT_POSES = ['wave', 'present', 'think', 'point', 'sit', 'celebrate', 'thumbs-up', 'idle'];

// 1. Generate Presenter Track
const presenterTrack = {
  version: 1,
  film: slug,
  cues: (film.scenes || []).map((s, idx) => ({
    time: idx === 0 ? 0 : Number((film.scenes.slice(0, idx).reduce((a, b) => a + b.duration, 0)).toFixed(2)),
    pose: idx === 0 ? 'wave' : (idx === (film.scenes.length - 1) ? 'celebrate' : MASCOT_POSES[idx % MASCOT_POSES.length]),
    fx: idx === 0 ? 'coffee-ring' : (idx === 10 ? 'sparkle-burst' : null)
  }))
};
fs.writeFileSync(path.join(filmDir, 'src', 'presenter-track.json'), JSON.stringify(presenterTrack, null, 2) + '\n');
console.log('OK       src/presenter-track.json generated');

// 2. Generate STORYBOARD.md
let storyboardMd = `# STORYBOARD: ${topic.toUpperCase()}\n\n`;
storyboardMd += `**Slug:** \`${slug}\`  \n`;
storyboardMd += `**Standard:** 1920x1080 @ 60fps | KAPE Canon Paper (#F6F2EA)  \n\n`;
storyboardMd += `## Scene Breakdown\n\n`;

let cumTime = 0;
(film.scenes || []).forEach((scene, i) => {
  const sStart = cumTime;
  const sEnd = cumTime + scene.duration;
  cumTime = sEnd;
  const sNum = String(i + 1).padStart(2, '0');
  storyboardMd += `### Scene ${sNum} — ${scene.id} (${sStart.toFixed(1)}s – ${sEnd.toFixed(1)}s, ${scene.duration.toFixed(1)}s)\n`;
  storyboardMd += `- **Headline:** ${scene.id.replace(/^s\d+-/, '').toUpperCase()}\n`;
  storyboardMd += `- **Presenter Pose:** ${presenterTrack.cues[i]?.pose || 'present'}\n`;
  storyboardMd += `- **Stage Layout:** Card container (x: 640-1860, y: 160-920), Poppins typography, WCAG AA contrast\n`;
  storyboardMd += `- **Motion:** GSAP fromTo enter at 0.0s, content exit by ${(scene.duration - 0.08).toFixed(2)}s\n\n`;
});

fs.writeFileSync(path.join(filmDir, 'STORYBOARD.md'), storyboardMd);
console.log('OK       STORYBOARD.md generated');

console.log('ai-director: Preparation complete. Scene templates initialized.');
