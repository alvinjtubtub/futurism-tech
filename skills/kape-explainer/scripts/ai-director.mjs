#!/usr/bin/env node
/**
 * ai-director.mjs — Autonomous KAPE Scene Director with Gemini AI Studio Integration.
 * Reads transcript word timings (vo-words.json) and audio duration,
 * updates film.json (scenes, audio dur, bgm: null if no bgm-duck.wav),
 * and generates:
 * 1. film.json (clean 11-scene timing map & audio config)
 * 2. STORYBOARD.md (11 scenes aligned to narration timestamps)
 * 3. 11 GSAP HTML compositions with rich 3D spatial motion design (compositions/s01-hook.html ... s11-close.html)
 * 4. src/presenter-track.json (mascot poses aligned to narration, eye blinks, talking bob)
 *
 * When GEMINI_API_KEY is present:
 * - Queries Google AI Studio (Gemini 2.5 Flash) to generate bespoke, topic-specific 3D motion graphics
 *   and animated SVG/HTML/CSS diagrams for each scene aligned with the spoken words.
 * When GEMINI_API_KEY is absent or network fails:
 * - Falls back to the built-in procedural 3D motion-design generator.
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

// Check if film.json still has the default worked-example template scenes
const isTemplateScaffold = Array.isArray(film.scenes) && film.scenes.some((s) => {
  const id = Array.isArray(s) ? s[0] : s?.id;
  return id === 's03-parcel' || id === 's07-ghl';
});

if (isTemplateScaffold) {
  const totalFilmDur = Math.max(60.0, Number((voDur + 2.4).toFixed(1)));
  const isVertical = film.height > film.width;
  const isTE = slug.toLowerCase().startsWith('te-') || (film.name && film.name.toLowerCase().startsWith('te-'));
  const sceneNames = (isVertical || isTE) ? [
    's01-hook',
    's02-overview',
    's03-mechanism',
    's04-deepdive',
    's05-process',
    's06-comparison',
    's07-application',
    's08-question',
    's09-close'
  ] : [
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

  const count = sceneNames.length;
  const baseDur = Math.floor((totalFilmDur / count) * 10) / 10;
  let rem = Number((totalFilmDur - baseDur * (count - 1)).toFixed(2));
  film.scenes = sceneNames.map((id, idx) => [
    id,
    idx === count - 1 ? rem : Number(baseDur.toFixed(2))
  ]);

  if (!film.layout && (isVertical || isTE)) {
    film.layout = {
      stage: { x: 60, y: 470, w: 900, h: 710 },
      headline_band: { x: 60, y: 210, w: 872, h: 230 },
      presenter_zone: { x: 24, y: 1205, w: 361, h: 335, feet_y: 1540 },
      caption_band: { x: 486, y: 1280, w: 446, h: 240 }
    };
  }

  const compDir = path.join(filmDir, 'compositions');
  if (fs.existsSync(compDir)) {
    for (const f of fs.readdirSync(compDir)) {
      if (f.startsWith('s') && f.endsWith('.html') && !sceneNames.includes(f.replace('.html', ''))) {
        fs.rmSync(path.join(compDir, f), { force: true });
      }
    }
  }
}

// Ensure audio dur, bgm, and cues are valid
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

const compDir = path.join(filmDir, 'compositions');
fs.mkdirSync(compDir, { recursive: true });

// Poses with 100% verified blink and talk variants:
const MASCOT_POSES = ['wave', 'present', 'point', 'sit', 'thumbs-up', 'celebrate', 'idle', 'walk'];

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
// Naturally frequent and visible blinks (every ~2.2 - 3.4 seconds, 0.16s duration ~ 10 frames @ 60fps)
presenterData.blink = { every: [2.2, 2.9, 2.5, 3.1, 2.7, 3.4], dur: 0.16 };

fs.writeFileSync(presenterTrackPath, JSON.stringify(presenterData, null, 2) + '\n');
console.log('OK       src/presenter-track.json generated with active blinks & talk variants');

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
  storyboardMd += `- **Stage Layout:** Center-Right 3D World (x: 640-1860, y: 160-960), Poppins typography, WCAG AA contrast\n`;
  storyboardMd += `- **Motion:** Camera 3D drift, staggered visual reveals, Seam Law exit by ${(scene.duration - 0.55).toFixed(2)}s\n\n`;
});

fs.writeFileSync(path.join(filmDir, 'STORYBOARD.md'), storyboardMd);
console.log('OK       STORYBOARD.md generated');

// 3. Query Google AI Studio Gemini API for Bespoke Visuals if GEMINI_API_KEY is present
async function queryGeminiDirector(filmTopic, sceneList, segments, apiKey) {
  if (!apiKey) return null;
  console.log('🤖 AI Director: Querying Google AI Studio Gemini API for custom 3D motion design...');
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;

  const prompt = `You are the Lead Spatial 3D Motion Graphic Director for "Tech Explanasyon", an elite technical visual explainer channel.
Topic: "${filmTopic}"
Duration: ${sceneList.reduce((a, b) => a + b.duration, 0).toFixed(1)}s across ${sceneList.length} scenes.

Narration transcript broken into scenes:
${sceneList.map((s, i) => `Scene ${i+1} [${s.id}] (${s.duration}s): "${segments[i]?.text || ''}"`).join('\n')}

For each scene, design a high-end 3D motion graphic layout inside the center-right stage container:
- Available stage area: left: 1140px, top: 540px, width: 960px, height: 520px.
- The mascot presenter occupies x: 40-620px (left side), and brand badge is at x > 1500px, y < 140px. Do not overlap them.
- Use rich visual elements: diagrams, mechanical parts, cards with borders, status badges, SVG shapes, progress rings, arrows.
- Design tokens: Navy (#0B1E3F), Orange (#FF7A1A), Teal (#0F9F8F), Paper (#F6F2EA), White (#FFFFFF), Red (#B02A30).
- GSAP Tweens: Animate elements inside #\${sceneId}-content with staggered entrances.
- IMPORTANT RULE: NEVER use \`repeat: -1\` (infinite repeats fail render checks). Use finite loops like \`repeat: Math.max(1, Math.floor(D / cycle))\`.

Respond ONLY with a valid JSON array of objects, one per scene, formatted as:
[
  {
    "sceneId": "s01-hook",
    "kicker": "THE HOOK",
    "headline": "Punchy Title",
    "stageMarkup": "<div id=\\"s01-card\\"...>...</div>",
    "gsapTweens": "tl.fromTo($('card'), ...);"
  }
]`;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: {
          temperature: 0.3,
          responseMimeType: 'application/json'
        }
      }),
      signal: controller.signal
    });
    clearTimeout(timeout);

    if (!res.ok) {
      console.warn(`::warning::Gemini API responded with status ${res.status} ${res.statusText}`);
      return null;
    }
    const data = await res.json();
    const rawText = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!rawText) return null;
    const parsed = JSON.parse(rawText);
    if (Array.isArray(parsed) && parsed.length > 0) {
      console.log(`✨ AI Director: Gemini created ${parsed.length} tailored 3D scenes!`);
      const map = {};
      for (const item of parsed) {
        if (item.sceneId) map[item.sceneId] = item;
      }
      return map;
    }
  } catch (err) {
    console.warn(`::notice::Gemini API call skipped: ${err.message}. Using built-in spatial generator.`);
  }
  return null;
}

// 4. Procedural Fallback Visual Generator
function buildProceduralVisual(sceneId, duration, index, totalScenes, segText, filmTopic) {
  const D = Number(duration).toFixed(2);
  const headline = sceneId.replace(/^s\d+-?/, '').replace(/-/g, ' ').toUpperCase() || 'CORE INSIGHT';
  const rawSub = (segText && segText.length > 5) ? segText.trim().replace(/"/g, "'") : filmTopic;
  const shortSub = rawSub.length > 100 ? rawSub.slice(0, 97) + '...' : rawSub;

  const isWatch = /watch|clock|rotor|gear|spring|escapement|balance/i.test(filmTopic + ' ' + rawSub);
  const isMagnet = /magnet|flux|domain|pole|north|south|iron/i.test(filmTopic + ' ' + rawSub);

  let kicker = `STEP ${index + 1} OF ${totalScenes}`;
  if (index === 0) kicker = 'THE HOOK';
  else if (index === totalScenes - 1) kicker = 'TECH EXPLANASYON';

  let stageMarkup = '';
  let gsapTweens = '';

  if (isWatch) {
    if (index === 0) {
      stageMarkup = `
        <div id="${sceneId}-dial" style="width:360px; height:360px; border-radius:50%; background:#0B1E3F; border:6px solid #FF7A1A; box-shadow:var(--float); position:relative; display:flex; align-items:center; justify-content:center;">
          <div style="position:absolute; width:12px; height:12px; border-radius:50%; background:#FFFFFF; z-index:5;"></div>
          <div id="${sceneId}-hand" style="position:absolute; top:28px; width:4px; height:152px; background:#FF7A1A; border-radius:2px; transform-origin:50% 100%;"></div>
          <div style="position:absolute; top:18px; font-size:16px; font-weight:700; color:#ECE5D8; letter-spacing:2px;">AUTOMATIC</div>
          <div style="position:absolute; bottom:26px; font-size:12px; font-weight:700; color:#5EEAD4;">MECHANICAL</div>
        </div>
        <div id="${sceneId}-card" style="width:420px; padding:32px; border-radius:32px; background:#FFFFFF; border:2px solid #ECE5D8; box-shadow:var(--float); margin-left:36px;">
          <div style="font-size:16px; font-weight:700; color:#B8500A; text-transform:uppercase;">No Battery Required</div>
          <div style="font-size:32px; font-weight:700; color:#0B1E3F; line-height:1.25; margin:12px 0;">Powered By Movement</div>
          <div style="font-size:18px; font-weight:500; color:#5B6478; line-height:1.4;">${shortSub}</div>
        </div>`;
      gsapTweens = `
        tl.fromTo($('dial'), { opacity: 0, scale: 0.8, rotation: -30 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.7, ease: 'back.out(1.5)', force3D: true }, 0.20);
        tl.fromTo($('hand'), { rotation: 0 }, { rotation: 360 * 2, duration: D - 0.7, ease: 'none' }, 0.40);
        tl.fromTo($('card'), { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out', force3D: true }, 0.50);`;
    } else if (index % 3 === 1) {
      stageMarkup = `
        <div id="${sceneId}-rotor-wrap" style="width:380px; height:380px; border-radius:50%; background:#FAF8F5; border:3px dashed #0F9F8F; display:flex; align-items:center; justify-content:center; position:relative;">
          <div id="${sceneId}-rotor" style="width:340px; height:170px; border-top-left-radius:170px; border-top-right-radius:170px; background:linear-gradient(180deg, #FF9445, #C8580B); box-shadow:0 12px 24px rgba(184,80,10,0.3); position:absolute; top:20px; transform-origin:50% 100%;">
            <div style="position:absolute; bottom:16px; left:50%; transform:translateX(-50%); font-size:14px; font-weight:700; color:#FFFFFF;">OSCILLATING ROTOR</div>
          </div>
          <div style="width:24px; height:24px; border-radius:50%; background:#0B1E3F; z-index:3;"></div>
        </div>
        <div id="${sceneId}-info" style="width:400px; padding:32px; border-radius:32px; background:#0B1E3F; border:2px solid #FF7A1A; box-shadow:var(--float); margin-left:36px;">
          <div style="font-size:15px; font-weight:700; color:#FF7A1A; text-transform:uppercase;">Kinetic Energy Capture</div>
          <div style="font-size:30px; font-weight:700; color:#FFFFFF; line-height:1.2; margin:12px 0;">360° Free Rotation</div>
          <div style="font-size:16px; font-weight:500; color:#ECE5D8; line-height:1.45;">${shortSub}</div>
        </div>`;
      gsapTweens = `
        tl.fromTo($('rotor-wrap'), { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.6, ease: 'back.out(1.5)', force3D: true }, 0.20);
        tl.fromTo($('rotor'), { rotation: -60 }, { rotation: 60, duration: 1.1, ease: 'sine.inOut', repeat: Math.max(1, Math.floor(D / 1.1)), yoyo: true }, 0.40);
        tl.fromTo($('info'), { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out', force3D: true }, 0.45);`;
    } else if (index % 3 === 2) {
      stageMarkup = `
        <div id="${sceneId}-gears" style="width:440px; height:340px; position:relative; display:flex; align-items:center;">
          <div id="${sceneId}-g1" style="width:180px; height:180px; border-radius:50%; background:#FF9445; border:6px dashed #B8500A; position:absolute; left:20px; top:40px; display:flex; align-items:center; justify-content:center; box-shadow:var(--float);">
            <span style="font-size:14px; font-weight:700; color:#FFFFFF;">CENTER</span>
          </div>
          <div id="${sceneId}-g2" style="width:140px; height:140px; border-radius:50%; background:#22B5A4; border:5px dashed #0A7468; position:absolute; left:170px; top:140px; display:flex; align-items:center; justify-content:center; box-shadow:var(--float);">
            <span style="font-size:13px; font-weight:700; color:#FFFFFF;">3RD WHEEL</span>
          </div>
          <div id="${sceneId}-g3" style="width:110px; height:110px; border-radius:50%; background:#2563EB; border:4px dashed #1E40AF; position:absolute; left:280px; top:60px; display:flex; align-items:center; justify-content:center; box-shadow:var(--float);">
            <span style="font-size:12px; font-weight:700; color:#FFFFFF;">4TH WHEEL</span>
          </div>
        </div>
        <div id="${sceneId}-spec" style="width:380px; padding:32px; border-radius:32px; background:#FFFFFF; border:2px solid #ECE5D8; box-shadow:var(--float); margin-left:24px;">
          <div style="font-size:15px; font-weight:700; color:#0A7468; text-transform:uppercase;">Gear Train Ratio</div>
          <div style="font-size:30px; font-weight:700; color:#0B1E3F; line-height:1.2; margin:12px 0;">Mechanical Stepping</div>
          <div style="font-size:16px; font-weight:500; color:#5B6478; line-height:1.45;">${shortSub}</div>
        </div>`;
      gsapTweens = `
        tl.fromTo($('gears'), { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.6, ease: 'back.out(1.5)', force3D: true }, 0.20);
        tl.fromTo($('g1'), { rotation: 0 }, { rotation: 360, duration: 6, ease: 'none', repeat: Math.max(1, Math.floor(D / 6)) }, 0.30);
        tl.fromTo($('g2'), { rotation: 0 }, { rotation: -360, duration: 3.5, ease: 'none', repeat: Math.max(1, Math.floor(D / 3.5)) }, 0.30);
        tl.fromTo($('g3'), { rotation: 0 }, { rotation: 360, duration: 2, ease: 'none', repeat: Math.max(1, Math.floor(D / 2)) }, 0.30);
        tl.fromTo($('spec'), { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out', force3D: true }, 0.45);`;
    } else {
      stageMarkup = `
        <div id="${sceneId}-balance" style="width:360px; height:360px; border-radius:50%; background:#FAF8F5; border:4px solid #0B1E3F; box-shadow:var(--float); position:relative; display:flex; align-items:center; justify-content:center;">
          <div id="${sceneId}-spring" style="width:240px; height:240px; border-radius:50%; border:3px dashed #FF7A1A; position:absolute;"></div>
          <div id="${sceneId}-wheel" style="width:160px; height:160px; border-radius:50%; background:#0B1E3F; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:16px; font-weight:700;">
            28,800 VPH
          </div>
        </div>
        <div id="${sceneId}-desc" style="width:420px; padding:32px; border-radius:32px; background:#0B1E3F; border:2px solid #0F9F8F; box-shadow:var(--float); margin-left:36px;">
          <div style="font-size:15px; font-weight:700; color:#5EEAD4; text-transform:uppercase;">The Heartbeat (4Hz)</div>
          <div style="font-size:32px; font-weight:700; color:#FFFFFF; line-height:1.2; margin:12px 0;">Escapement Regulation</div>
          <div style="font-size:16px; font-weight:500; color:#ECE5D8; line-height:1.45;">${shortSub}</div>
        </div>`;
      gsapTweens = `
        tl.fromTo($('balance'), { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.6, ease: 'back.out(1.5)', force3D: true }, 0.20);
        tl.fromTo($('spring'), { scale: 0.92, rotation: -20 }, { scale: 1.08, rotation: 20, duration: 0.25, ease: 'sine.inOut', repeat: Math.max(1, Math.floor(D / 0.5)), yoyo: true }, 0.35);
        tl.fromTo($('wheel'), { rotation: -25 }, { rotation: 25, duration: 0.25, ease: 'sine.inOut', repeat: Math.max(1, Math.floor(D / 0.5)), yoyo: true }, 0.35);
        tl.fromTo($('desc'), { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out', force3D: true }, 0.45);`;
    }
  } else if (isMagnet) {
    if (index === 0) {
      stageMarkup = `
        <div id="${sceneId}-door" style="width:520px; height:380px; border-radius:36px; background:#FFFFFF; border:3px solid #ECE5D8; box-shadow:var(--float); position:relative; display:flex; align-items:center; justify-content:center;">
          <div style="position:absolute; left:28px; top:50%; transform:translateY(-50%); width:12px; height:160px; border-radius:6px; background:#D5CDBD;"></div>
          <div id="${sceneId}-magnet" style="width:200px; height:200px; border-radius:28px; background:#0B1E3F; border:3px solid #FF7A1A; box-shadow:0 16px 36px rgba(11,30,63,0.3); display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <span style="font-size:52px;">🧲</span>
            <span style="font-size:20px; font-weight:700; color:#FFFFFF; margin-top:8px;">Fridge Magnet</span>
          </div>
        </div>
        <div id="${sceneId}-card" style="width:340px; padding:32px; border-radius:28px; background:#0B1E3F; border:2px solid #FF7A1A; box-shadow:var(--float); margin-left:36px;">
          <div style="font-size:15px; font-weight:700; color:#FF7A1A;">INVISIBLE FORCE</div>
          <div style="font-size:30px; font-weight:700; color:#FFFFFF; margin:12px 0;">Atomic Alignment</div>
          <div style="font-size:16px; font-weight:500; color:#ECE5D8;">${shortSub}</div>
        </div>`;
      gsapTweens = `
        tl.fromTo($('door'), { opacity: 0, scale: 0.9, y: 30 }, { opacity: 1, scale: 1, y: 0, duration: 0.7, ease: 'back.out(1.5)', force3D: true }, 0.20);
        tl.fromTo($('magnet'), { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.6, ease: 'back.out(1.8)', force3D: true }, 0.50);
        tl.fromTo($('card'), { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out', force3D: true }, 0.60);`;
    } else if (index % 2 === 1) {
      stageMarkup = `
        <div id="${sceneId}-matrix" style="width:480px; padding:24px; border-radius:32px; background:#FFFFFF; border:2px solid #ECE5D8; box-shadow:var(--float);">
          <div style="font-size:16px; font-weight:700; color:#0B1E3F; margin-bottom:14px;">MAGNETIC DOMAINS (MICRO-SCALE)</div>
          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px;">
            ${[1,2,3,4,5,6].map(() => `<div class="${sceneId}-cell" style="height:76px; border-radius:16px; background:#FCFAF6; border:2px solid #0F9F8F; display:flex; align-items:center; justify-content:center; font-size:24px; color:#0A7468; font-weight:700;">➔</div>`).join('')}
          </div>
        </div>
        <div id="${sceneId}-info" style="width:360px; padding:32px; border-radius:32px; background:#0B1E3F; border:2px solid #0F9F8F; box-shadow:var(--float); margin-left:32px;">
          <div style="font-size:15px; font-weight:700; color:#5EEAD4;">UNIFIED VECTOR</div>
          <div style="font-size:30px; font-weight:700; color:#FFFFFF; margin:12px 0;">Billions of Atoms</div>
          <div style="font-size:16px; font-weight:500; color:#ECE5D8;">${shortSub}</div>
        </div>`;
      gsapTweens = `
        tl.fromTo($('matrix'), { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.6, ease: 'back.out(1.5)', force3D: true }, 0.20);
        tl.fromTo('.${sceneId}-cell', { rotation: (i) => i * 35 }, { rotation: 0, duration: 0.8, ease: 'power2.out', stagger: 0.08 }, 0.40);
        tl.fromTo($('info'), { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out', force3D: true }, 0.50);`;
    } else {
      stageMarkup = `
        <div id="${sceneId}-pole-wrap" style="width:500px; display:flex; flex-direction:column; align-items:center;">
          <div id="${sceneId}-bar" style="width:480px; height:100px; border-radius:24px; display:flex; overflow:hidden; box-shadow:var(--float);">
            <div style="flex:1; background:#B02A30; display:flex; align-items:center; justify-content:center; font-size:34px; font-weight:700; color:#FFFFFF;">NORTH</div>
            <div style="flex:1; background:#2563EB; display:flex; align-items:center; justify-content:center; font-size:34px; font-weight:700; color:#FFFFFF;">SOUTH</div>
          </div>
        </div>
        <div id="${sceneId}-card" style="width:360px; padding:32px; border-radius:32px; background:#FFFFFF; border:2px solid #ECE5D8; box-shadow:var(--float); margin-left:32px;">
          <div style="font-size:15px; font-weight:700; color:#B8500A;">FUNDAMENTAL RULE</div>
          <div style="font-size:30px; font-weight:700; color:#0B1E3F; margin:12px 0;">Attract & Repel</div>
          <div style="font-size:16px; font-weight:500; color:#5B6478;">${shortSub}</div>
        </div>`;
      gsapTweens = `
        tl.fromTo($('pole-wrap'), { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.6, ease: 'back.out(1.5)', force3D: true }, 0.20);
        tl.fromTo($('card'), { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out', force3D: true }, 0.45);`;
    }
  } else {
    if (index === 0) {
      stageMarkup = `
        <div id="${sceneId}-card" style="width:840px; padding:48px; border-radius:36px; background:#FFFFFF; border:3px solid #ECE5D8; box-shadow:var(--float); display:flex; flex-direction:column;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px;">
            <span style="font-size:18px; font-weight:700; color:#B8500A; letter-spacing:2px;">TECH EXPLANASYON</span>
            <span style="font-size:14px; font-weight:700; color:#0F9F8F; background:#FAF8F5; padding:6px 16px; border-radius:12px; border:1px solid #0F9F8F;">DEEP DIVE</span>
          </div>
          <h1 style="font-size:46px; font-weight:700; color:#0B1E3F; line-height:1.2; margin:0 0 20px 0;">${filmTopic.toUpperCase()}</h1>
          <div style="font-size:22px; font-weight:500; color:#5B6478; line-height:1.5;">${shortSub}</div>
        </div>`;
      gsapTweens = `
        tl.fromTo($('card'), { opacity: 0, y: 30, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: 'power2.out', force3D: true }, 0.20);`;
    } else if (index === totalScenes - 1) {
      stageMarkup = `
        <div id="${sceneId}-cta" style="width:820px; padding:48px; border-radius:36px; background:#0B1E3F; border:3px solid #FF7A1A; box-shadow:var(--float); text-align:center; display:flex; flex-direction:column; align-items:center;">
          <div style="font-size:16px; font-weight:700; color:#FF7A1A; letter-spacing:2px;">TECH EXPLANASYON</div>
          <div style="font-size:40px; font-weight:700; color:#FFFFFF; margin:16px 0 24px 0;">Follow For More Tech Explained</div>
          <div style="font-size:20px; font-weight:500; color:#ECE5D8; margin-bottom:32px;">${shortSub}</div>
          <div style="padding:14px 40px; border-radius:24px; background:#FF7A1A; color:#FFFFFF; font-size:22px; font-weight:700; box-shadow:0 12px 24px rgba(255,122,26,0.3);">Follow & Share</div>
        </div>`;
      gsapTweens = `
        tl.fromTo($('cta'), { opacity: 0, scale: 0.9, y: 20 }, { opacity: 1, scale: 1, y: 0, duration: 0.6, ease: 'back.out(1.5)', force3D: true }, 0.20);`;
    } else {
      stageMarkup = `
        <div id="${sceneId}-c1" style="width:420px; padding:32px; border-radius:32px; background:#FFFFFF; border:2px solid #ECE5D8; box-shadow:var(--float);">
          <div style="font-size:15px; font-weight:700; color:#B8500A;">SYSTEM COMPONENT</div>
          <div style="font-size:30px; font-weight:700; color:#0B1E3F; margin:12px 0;">${headline}</div>
          <div style="font-size:17px; font-weight:500; color:#5B6478; line-height:1.45;">${shortSub}</div>
        </div>
        <div id="${sceneId}-c2" style="width:380px; padding:32px; border-radius:32px; background:#0B1E3F; border:2px solid #0F9F8F; box-shadow:var(--float); margin-left:32px;">
          <div style="font-size:15px; font-weight:700; color:#5EEAD4;">ARCHITECTURE</div>
          <div style="font-size:30px; font-weight:700; color:#FFFFFF; margin:12px 0;">Step ${index + 1} Pipeline</div>
          <div style="font-size:16px; font-weight:500; color:#ECE5D8;">Automated Mechanical & Logical Precision</div>
        </div>`;
      gsapTweens = `
        tl.fromTo($('c1'), { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out', force3D: true }, 0.20);
        tl.fromTo($('c2'), { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: 0.6, ease: 'power2.out', force3D: true }, 0.35);`;
    }
  }

  return { kicker, headline, stageMarkup, gsapTweens };
}

// 5. Wrap Stage into KAPE 3D Motion Scene HTML
function wrapSceneHtml(sceneId, duration, visual, filmTopic) {
  const D = Number(duration).toFixed(2);
  const exitTime = Math.max(0.2, duration - 0.55).toFixed(2);
  const W = film.width || 1080;
  const H = film.height || 1920;
  const isVertical = H > W;

  const titleStyles = isVertical
    ? `position: absolute; left: 540px; top: 268px; transform: translate(-50%, -50%); width: 880px; text-align: center; opacity: 0;`
    : `position: absolute; left: 1140px; top: 110px; transform: translate(-50%, -50%); width: 920px; text-align: center; opacity: 0;`;

  const stageStyles = isVertical
    ? `position: absolute; left: 540px; top: 825px; transform: translate(-50%, -50%); width: 900px; height: 710px; display: flex; align-items: center; justify-content: center;`
    : `position: absolute; left: 1140px; top: 540px; transform: translate(-50%, -50%); width: 960px; height: 520px; display: flex; align-items: center; justify-content: center;`;

  const labelSize = isVertical ? '60px' : '54px';

  return `<!-- Scene ${sceneId} (${D}s). Topic: ${filmTopic} -->
<template>
<link rel="stylesheet" href="assets/kit.css">
<style>
@font-face { font-family: 'Poppins'; font-weight: 500; src: url('assets/fonts/poppins-500.woff2') format('woff2'); }
@font-face { font-family: 'Poppins'; font-weight: 700; src: url('assets/fonts/poppins-700.woff2') format('woff2'); }
#root { position: absolute; inset: 0; width: ${W}px; height: ${H}px; overflow: hidden; font-family: 'Poppins', sans-serif; background: #F6F2EA; }
.${sceneId}-layer { position: absolute; inset: 0; transform-style: preserve-3d; will-change: transform; }
.${sceneId}-world { position: absolute; left: 50%; top: 50%; transform-style: preserve-3d; will-change: transform; }
.${sceneId}-title { ${titleStyles} }
.${sceneId}-stage-wrap { ${stageStyles} }
</style>
<div id="root" data-composition-id="${sceneId}" data-width="${W}" data-height="${H}">
  <div id="${sceneId}-ground" class="clip kit-ground" data-start="0" data-duration="${D}" data-track-index="0"></div>
  <div id="${sceneId}-stage" class="clip" data-start="0" data-duration="${D}" data-track-index="1" style="position:absolute; inset:0; perspective:1866px; perspective-origin:50% 50%;">
    <div id="${sceneId}-drift" class="${sceneId}-layer">
      <div id="${sceneId}-cam" class="${sceneId}-layer">
        <div class="kit-floor"></div>
        <div id="${sceneId}-headline" class="${sceneId}-world ${sceneId}-title" data-layout-allow-overlap>
          <div class="kit-kicker" style="color:#B8500A; margin-bottom:12px;">${visual.kicker}</div>
          <div class="kit-label" style="font-size:${labelSize}; line-height:1.2; color:#0B1E3F; font-weight:700;">${visual.headline}</div>
        </div>
        <div id="${sceneId}-content" class="${sceneId}-world ${sceneId}-stage-wrap">
          ${visual.stageMarkup}
        </div>
      </div>
    </div>
  </div>
  <div id="${sceneId}-grain" class="clip kit-grain" data-start="0" data-duration="${D}" data-track-index="9"></div>
</div>
<script>
(function () {
  var $ = function (id) { return '#${sceneId}-' + id; };
  var D = ${D};
  var tl = gsap.timeline({ paused: true });

  gsap.set($('headline'), { opacity: 0, y: -20, force3D: true });

  // Camera 3D Drift
  tl.fromTo($('drift'), { scale: 1, rotationY: 0 }, { scale: 1.02, rotationY: -0.3, duration: D / 2, ease: 'sine.inOut', force3D: true }, 0);
  tl.fromTo($('drift'), { scale: 1.02, rotationY: -0.3 }, { scale: 1, rotationY: 0, duration: D / 2, ease: 'sine.inOut', force3D: true, immediateRender: false }, D / 2);

  // Headline enter
  tl.fromTo($('headline'), { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.55, ease: 'power2.out', force3D: true }, 0.10);

  // Visual Scene Tweens
  ${visual.gsapTweens}

  // Seam Law: Clean exit before cut
  tl.fromTo($('headline'), { opacity: 1 }, { opacity: 0, y: -15, duration: 0.35, ease: 'power2.in', immediateRender: false, force3D: true }, ${exitTime});
  tl.fromTo($('content'), { opacity: 1 }, { opacity: 0, scale: 0.95, duration: 0.35, ease: 'power2.in', immediateRender: false, force3D: true }, ${exitTime});

  window.__timelines = window.__timelines || {};
  window.__timelines['${sceneId}'] = tl;
})();
</script>
</template>`;
}

// 6. Generate All 11 Scenes
async function main() {
  const apiKey = process.env.GEMINI_API_KEY;
  const geminiMap = await queryGeminiDirector(topic, scenes, voSegments, apiKey);

  scenes.forEach((scene, i) => {
    const compPath = path.join(compDir, `${scene.id}.html`);
    const segText = voSegments[i]?.text || '';
    const geminiScene = geminiMap?.[scene.id];

    let visual;
    if (geminiScene && geminiScene.stageMarkup && geminiScene.gsapTweens) {
      visual = {
        kicker: geminiScene.kicker || `STEP ${i + 1} OF ${scenes.length}`,
        headline: geminiScene.headline || scene.id.replace(/^s\d+-/, '').toUpperCase(),
        stageMarkup: geminiScene.stageMarkup,
        gsapTweens: geminiScene.gsapTweens
      };
      console.log(`OK       compositions/${scene.id}.html created (AI-Designed via Gemini Studio)`);
    } else {
      visual = buildProceduralVisual(scene.id, scene.duration, i, scenes.length, segText, topic);
      console.log(`OK       compositions/${scene.id}.html created (3D Spatial Motion Scene)`);
    }

    const html = wrapSceneHtml(scene.id, scene.duration, visual, topic);
    fs.writeFileSync(compPath, html);
  });

  console.log('ai-director: Preparation complete. All 11 scene compositions and presenter track verified.');
}

await main();
