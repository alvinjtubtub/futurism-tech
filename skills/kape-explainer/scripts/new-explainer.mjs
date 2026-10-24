// Scaffold a KAPE narrated explainer film: the spatial-film engine's project skeleton + this skill's kit (landscape
// 16:9 by default, --format 9x16 for vertical), frame.md, worker brief, presenter track, the mascot (your own from the
// profile, else the bundled KAPE demo), your brand (logo + wordmark + CTA from profile/brand.json) and SFX. Every film
// opens on the brand logo, carries the corner logo (m-brand overlay, scripts/build-brand.py) and ends on the logo + CTA.
// Usage: node <skill>/scripts/new-explainer.mjs [path/to/film] --name <slug> [--format 16x9|9x16] [--mp3 <narration.mp3>]
//   path omitted -> <films_dir from brand.json>/<name>
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { loadBrand, expandHome, profileDir } from './lib/brand.mjs';
import { python } from './lib/python.mjs';

const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ENGINE = path.resolve(SKILL, '..', 'spatial-film');
const args = process.argv.slice(2);
const flag = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const die = (m) => { console.error(m); process.exit(1); };
const fwd = (p) => p.replace(/\\/g, '/').replace(/\/+$/, '');
const target = args.find((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--')));
const name = flag('--name');
const mp3 = flag('--mp3');
const format = flag('--format') || '16x9';
const profArg = flag('--profile');
if (!name || !['16x9', '9x16'].includes(format)) die('usage: new-explainer.mjs [path] --name <slug> [--format 16x9|9x16] [--mp3 <file>] [--profile <id>]');
if (!fs.existsSync(path.join(ENGINE, 'scripts', 'new-film.mjs'))) die('spatial-film engine not found at ' + ENGINE);

let brand;
try { brand = loadBrand(profArg); } catch (e) { die(e.message + '\n(run profile.mjs init first)'); }
const PROFILE = profileDir(profArg);
const dir = path.resolve(target || path.join(expandHome(brand.films_dir), name));

// mascot: the user's own (prepped) beats the bundled demo; a raw pose folder must be prepped first
const ownMascot = path.join(PROFILE, 'mascot');
if (fs.existsSync(ownMascot) && !fs.existsSync(path.join(ownMascot, 'manifest.json'))) {
  die(`${ownMascot} has no manifest.json - run prep-mascot.py on it first (or remove the folder to use the bundled KAPE demo)`);
}
const mascotSrc = fs.existsSync(ownMascot) ? ownMascot : path.join(SKILL, 'assets', 'mascot');

let py;
try { py = python().join(' '); } catch (e) { console.warn('warning: ' + e.message); py = 'python3'; }

// phase 0 saves SCRIPT.md into the film folder before the mp3 exists; new-film.mjs wants an empty folder
const preFiles = fs.existsSync(dir) ? fs.readdirSync(dir) : [];
const isIntakeStash = preFiles.length > 0 && preFiles.every((f) => f === 'SCRIPT.md' || /\.(wav|mp3|m4a)$/i.test(f));
const stashedFiles = [];
if (isIntakeStash) {
  const tmpStash = fs.mkdtempSync(path.join(os.tmpdir(), 'kape-stash-'));
  for (const f of preFiles) {
    const src = path.join(dir, f);
    const dst = path.join(tmpStash, f);
    fs.renameSync(src, dst);
    stashedFiles.push({ name: f, path: dst });
  }
}
execFileSync(process.execPath, [path.join(ENGINE, 'scripts', 'new-film.mjs'), dir, '--name', name], { stdio: 'inherit' });
if (stashedFiles.length) {
  fs.mkdirSync(path.join(dir, 'assets', 'audio'), { recursive: true });
  for (const f of stashedFiles) {
    if (f.name === 'SCRIPT.md') {
      fs.copyFileSync(f.path, path.join(dir, 'SCRIPT.md'));
    } else if (/\.(wav|mp3|m4a)$/i.test(f.name) && !mp3) {
      if (f.name.endsWith('.mp3')) {
        fs.copyFileSync(f.path, path.join(dir, 'assets', 'audio', 'vo.mp3'));
      } else {
        execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', f.path, '-c:a', 'libmp3lame', '-q:a', '2', path.join(dir, 'assets', 'audio', 'vo.mp3')]);
      }
    }
    fs.rmSync(f.path, { force: true });
  }
}

const T = path.join(SKILL, format === '16x9' ? 'template' : 'template-9x16');
const cp = (from, to) => { fs.mkdirSync(path.dirname(to), { recursive: true }); fs.cpSync(from, to, { recursive: true }); };
cp(path.join(T, 'kit.css'), path.join(dir, 'assets', 'kit.css'));
cp(path.join(T, 'frame.md'), path.join(dir, 'frame.md'));
cp(path.join(T, 'src', 'presenter-track.json'), path.join(dir, 'src', 'presenter-track.json'));
for (const f of ['snippets.html', 'scene-starter.html', 'worker-brief.md']) cp(path.join(T, 'references', f), path.join(dir, 'references', f));
for (const f of ['STORYBOARD.example.md', 'BRIEF.example.md']) cp(path.join(T, f), path.join(dir, 'references', f));
// the root BRIEF/STORYBOARD start as the worked example (the engine's own are for unnarrated product films)
cp(path.join(T, 'STORYBOARD.example.md'), path.join(dir, 'STORYBOARD.md'));
cp(path.join(T, 'BRIEF.example.md'), path.join(dir, 'BRIEF.md'));

// film.json: the worked example with this film's name - scenes/cues get replaced in phase 2
const film = JSON.parse(fs.readFileSync(path.join(T, 'film.json'), 'utf8'));
film.name = name;
film._doc = 'KAPE narrated explainer (' + format + '). Worked-example values - replace scenes, cues, audio dur. ' + (film._doc || '');
const ov = film.overlays || [];
if (!ov.some((o) => o.id === 'm-brand')) ov.push({ id: 'm-brand', track: 3, z: 6 });
film.overlays = ov;
fs.writeFileSync(path.join(dir, 'film.json'), JSON.stringify(film, null, 2) + '\n');

// mascot + brand assets (Montserrat) + SFX + music
cp(mascotSrc, path.join(dir, 'assets', 'mascot'));
cp(path.join(SKILL, 'assets', 'brand'), path.join(dir, 'assets', 'brand'));
fs.mkdirSync(path.join(dir, 'assets', 'audio', 'sfx'), { recursive: true });
const sfxCandidates = [
  path.join(SKILL, '..', 'media-use', 'audio', 'assets', 'sfx'),
  path.join(os.homedir(), '.baet', 'skills', 'media-use', 'audio', 'assets', 'sfx'),
];
const sfxDir = sfxCandidates.find((d) => fs.existsSync(d)) || sfxCandidates[1];
let sfxMissing = 0;
for (const f of ['click.mp3', 'pop.mp3', 'ping.mp3', 'whoosh.mp3', 'impact-bass-1.mp3']) {
  const src = path.join(sfxDir, f);
  if (fs.existsSync(src)) fs.copyFileSync(src, path.join(dir, 'assets', 'audio', 'sfx', f)); else sfxMissing++;
}
if (sfxMissing) console.warn(`warning: ${sfxMissing} SFX not found in ${sfxDir} - install with: npx hyperframes skills update media-use (or sfx-search.mjs)`);
const bed = path.join(PROFILE, 'music', 'bed.mp3');
if (fs.existsSync(bed)) fs.copyFileSync(bed, path.join(dir, 'assets', 'audio', 'bed.mp3'));
if (mp3) fs.copyFileSync(mp3, path.join(dir, 'assets', 'audio', 'vo.mp3'));

// brand: film-root brand.json (logo path made film-relative), logo file, voice.md snapshot, snippet, kit.css vars
let logoRel = null;
const logoSrc = brand.logo ? path.join(PROFILE, brand.logo) : null;
if (logoSrc && fs.existsSync(logoSrc)) {
  logoRel = 'assets/brand/logo' + path.extname(logoSrc).toLowerCase();
  fs.copyFileSync(logoSrc, path.join(dir, logoRel));
} else if (brand.logo) console.warn(`warning: logo ${logoSrc} not found - the film uses the wordmark only`);
const voiceSrc = path.join(PROFILE, 'voice.md');
if (fs.existsSync(voiceSrc)) {
  fs.copyFileSync(voiceSrc, path.join(dir, 'references', 'voice.md'));
}
fs.writeFileSync(path.join(dir, 'brand.json'), JSON.stringify({
  ...brand,
  logo: logoRel,
  profile: profArg || process.env.KAPE_PROFILE || 'default',
  workflow: 'kape-explainer-0-8',
}, null, 2) + '\n');
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const w = brand.wordmark;
const gap = w.length > 1 && brand.name.includes(`${w[0]} ${w[1]}`) ? ' ' : '';
const wm = brand.logo_has_text ? '' : w.length > 1
  ? `<b>${esc(w[0])}${gap}<i>${esc(w[1])}</i></b>` : `<b>${esc(w[0])}</b>`;
const snippet = `<div class="kit-logo" style="--h:120px">${logoRel ? `<img src="${logoRel}" alt="">` : ''}${wm}</div>\n<div class="kit-cta">${esc(brand.cta)}</div>\n`;
fs.writeFileSync(path.join(dir, 'references', 'brand-snippet.html'), snippet);
fs.appendFileSync(path.join(dir, 'assets', 'kit.css'),
  `\n/* brand (from brand.json) */\n:root { --brand-ink: ${brand.ink}; --brand-accent: ${brand.accent}; --brand-accent-dark: ${brand.accent_dark}; }\n`);

// fill the {{...}} placeholders in every copied text file of the film (exact tokens only, no other templating)
const vars = {
  PROJECT_DIR: fwd(dir), SKILL: fwd(SKILL), ENGINE: fwd(ENGINE), FILM_NAME: name, BRAND_NAME: brand.name,
  OPENER: brand.opener, CTA: brand.cta, PRESENTER: brand.presenter, PY: py,
};
const SKIP = new Set(['assets', 'node_modules', '.git', '.hyperframes', 'renders', 'snapshots']);
const walk = (d) => {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) { if (!SKIP.has(e.name)) walk(p); continue; }
    if (!/\.(md|html|json)$/i.test(e.name)) continue;
    const s = fs.readFileSync(p, 'utf8');
    const out = s.replace(/\{\{(PROJECT_DIR|SKILL|ENGINE|FILM_NAME|BRAND_NAME|OPENER|CTA|PRESENTER|PY)\}\}/g, (_, k) => vars[k]);
    if (out !== s) fs.writeFileSync(p, out);
  }
};
walk(dir);

console.log(`\nKAPE explainer (${format}) ready: ${dir}\nnext: ${mp3 ? '' : 'drop the MP3 at assets/audio/vo.mp3, then '}${py} "${fwd(SKILL)}/scripts/transcribe.py" assets/audio/vo.mp3 src/timing`);
