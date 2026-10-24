// Create / inspect the user's brand profile (lives in KAPE_EXPLAINER_HOME/profile by default, or profiles/<id> with --profile <id>).
// Usage: node <skill>/scripts/profile.mjs init --name "<n>" [--profile <id>] [--wordmark "A,B"] [--logo <file>] [--logo-has-text]
//          [--ink #hex] [--accent #hex] [--opener "..."] [--cta "..."] [--presenter "..."] [--language "..."]
//          [--films-dir <dir>] [--force]
//        node <skill>/scripts/profile.mjs show | path | list [--profile <id>]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadBrand, mergeBrand, profileDir, listProfiles } from './lib/brand.mjs';

const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [cmd, ...rest] = process.argv.slice(2);
const flag = (k) => { const i = rest.indexOf(k); return i >= 0 ? rest[i + 1] : undefined; };
const has = (k) => rest.includes(k);
const die = (m) => { console.error(m); process.exit(1); };
const profId = flag('--profile');
const dir = profileDir(profId);
const brandFile = path.join(dir, 'brand.json');

if (cmd === 'path') {
  console.log(dir);
} else if (cmd === 'list') {
  const all = listProfiles();
  if (!all.length) {
    console.log('No profiles found.');
  } else {
    for (const p of all) {
      console.log(`${p.id.padEnd(18)} | ${p.brand.name.padEnd(22)} | films: ${p.brand.films_dir} | ${p.dir}`);
    }
  }
} else if (cmd === 'init') {
  if (!flag('--name')) die('usage: profile.mjs init --name "<n>" [--profile <id>] [--wordmark "A,B"] [--logo <file>] [--logo-has-text] [--ink #hex] [--accent #hex] [--opener ".."] [--cta ".."] [--presenter ".."] [--language ".."] [--films-dir <dir>] [--force]');
  if (fs.existsSync(brandFile) && !has('--force')) die(`${brandFile} exists - pass --force to overwrite`);
  const logoSrc = flag('--logo');
  if (logoSrc && !fs.existsSync(logoSrc)) die(`logo not found: ${logoSrc}`);
  fs.mkdirSync(dir, { recursive: true });
  let logo = null;
  if (logoSrc) {
    const ext = path.extname(logoSrc).toLowerCase() || '.png';
    for (const old of fs.readdirSync(dir)) if (/^logo\./.test(old)) fs.rmSync(path.join(dir, old));
    fs.copyFileSync(logoSrc, path.join(dir, 'logo' + ext));
    logo = 'logo' + ext;
  }
  const brand = mergeBrand({
    name: flag('--name'), wordmark: flag('--wordmark'), logo, logo_has_text: has('--logo-has-text'),
    ink: flag('--ink'), accent: flag('--accent'), opener: flag('--opener'), cta: flag('--cta'),
    presenter: flag('--presenter'), language: flag('--language'), films_dir: flag('--films-dir'),
  });
  fs.writeFileSync(brandFile, JSON.stringify(brand, null, 2) + '\n');
  const voice = path.join(dir, 'voice.md');
  const example = path.join(SKILL, 'template', 'profile', 'voice.example.md');
  if (!fs.existsSync(voice)) {
    if (fs.existsSync(example)) fs.copyFileSync(example, voice);
    else console.warn(`warning: ${example} not found - create ${voice} yourself (your speech style)`);
  }
  console.log(`profile written: ${brandFile}\nnext: edit ${voice} (your speech style), optional mascot/ and music/bed.mp3 in ${dir}`);
} else if (cmd === 'show') {
  let brand;
  try { brand = loadBrand(profId); } catch (e) { die(e.message); }
  console.log(JSON.stringify(brand, null, 2));
  const mascot = path.join(dir, 'mascot');
  console.log(`\nprofile dir: ${dir}`);
  console.log(`logo:     ${brand.logo && fs.existsSync(path.join(dir, brand.logo)) ? 'yes (' + brand.logo + ')' : 'no (wordmark only)'}`);
  console.log(`voice.md: ${fs.existsSync(path.join(dir, 'voice.md')) ? 'yes' : 'MISSING - copy template/profile/voice.example.md'}`);
  console.log(`mascot:   ${!fs.existsSync(mascot) ? 'no (bundled KAPE demo)' : fs.existsSync(path.join(mascot, 'manifest.json')) ? 'yes (prepped)' : 'yes, NOT prepped - run prep-mascot.py'}`);
  console.log(`music:    ${fs.existsSync(path.join(dir, 'music', 'bed.mp3')) ? 'yes (music/bed.mp3)' : 'no'}`);
} else {
  die('usage: profile.mjs init|show|path|list [--profile <id>]   (init needs --name)');
}
