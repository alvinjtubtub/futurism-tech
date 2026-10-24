// Searches the HeyGen sound-effects catalog and downloads the top hit per query.
// Usage: node <skill>/scripts/sfx-search.mjs "<name>=<query>" ["<name>=<query>" ...]   -> assets/audio/sfx/<name>.mp3
import { mkdirSync, existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
// media-use's vendored REST helper reads ~/.heygen/credentials (written by `npx hyperframes auth login`);
// no heygen CLI needed. media-use is installed by HyperFrames at ~/.baet/skills/media-use (sibling fallback).
const helper = [join(homedir(), '.baet', 'skills', 'media-use'), fileURLToPath(new URL('../../media-use', import.meta.url))]
  .map((d) => join(d, 'audio', 'scripts', 'lib', 'heygen.mjs')).find((f) => existsSync(f));
if (!helper) { console.error('media-use skill not found - run: npx hyperframes skills update media-use'); process.exit(1); }
const { heygenAuthHeaders, searchSounds, downloadTo } = await import(pathToFileURL(helper).href);

const headers = heygenAuthHeaders();
if (!headers) { console.error('no HeyGen credential'); process.exit(1); }
const out = join(process.cwd(), 'assets', 'audio', 'sfx');
mkdirSync(out, { recursive: true });
for (const arg of process.argv.slice(2)) {
  const [name, query] = arg.split('=');
  const res = await searchSounds(query, 'sound_effects', headers, { limit: 3 });
  res.forEach((r, i) => console.log(`${name} #${i + 1} ${r.duration}s ${r.description || r.name}`));
  if (res[0]?.audio_url) {
    await downloadTo(res[0].audio_url, join(out, `${name}.mp3`));
    console.log('  saved', name);
  }
}
