// Scaffolds a spatial film project from the template. Refuses a non-empty target.
// Usage: node <skill>/scripts/new-film.mjs <path/to/film> --name <slug>
import { cpSync, existsSync, readdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const SKILL = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [target] = process.argv.slice(2).filter((a) => !a.startsWith('--'));
const ni = process.argv.indexOf('--name');
const name = ni > 0 ? process.argv[ni + 1] : null;
if (!target || !name) { console.error('usage: new-film.mjs <path> --name <slug>'); process.exit(1); }
const dir = resolve(target);
if (existsSync(dir) && readdirSync(dir).length) { console.error(`${dir} is not empty - pick a new folder`); process.exit(1); }

cpSync(join(SKILL, 'template'), dir, { recursive: true });
renameSync(join(dir, 'gitignore.txt'), join(dir, '.gitignore'));
const fill = (rel, pairs) => {
  const p = join(dir, rel);
  let s = readFileSync(p, 'utf8');
  for (const [a, b] of pairs) s = s.split(a).join(b);
  writeFileSync(p, s);
};
const fwd = (p) => p.replace(/\\/g, '/');
fill('film.json', [['FILM_NAME', name]]);
fill('package.json', [['FILM_NAME', name]]);
fill('references/worker-brief.md', [['{{PROJECT_DIR}}', fwd(dir)], ['{{ENGINE}}', fwd(SKILL)], ['{{SKILL_DIR}}', fwd(SKILL)]]);
writeFileSync(join(dir, 'meta.json'), JSON.stringify({ id: name, name, createdAt: new Date().toISOString() }, null, 2) + '\n');
console.log(`film project ready: ${dir}
next: fill BRIEF.md + STORYBOARD.md (phase 1), then frame.md, kit.css tokens, film.json scenes.`);
