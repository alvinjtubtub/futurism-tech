// Lists HeyGen catalog music candidates and downloads the ones worth auditioning.
// Usage: node <skill>/scripts/music-search.mjs "<query>" [limit] [downloadTop] [minDurationS]
// Writes .media/candidates/<id8>.mp3 and prints id, description, duration.
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

const [query = 'minimal electronic product demo', limitArg = '10', topArg = '4', minDurArg = '0'] = process.argv.slice(2);
const headers = heygenAuthHeaders();
if (!headers) { console.error('no HeyGen credential'); process.exit(1); }
const results = (await searchSounds(query, 'music', headers, { limit: Number(limitArg) }))
  .filter((r) => (r.duration ?? 0) >= Number(minDurArg));
const out = join(process.cwd(), '.media', 'candidates');
mkdirSync(out, { recursive: true });
let i = 0;
for (const r of results) {
  i++;
  console.log(`#${i} ${String(r.id).slice(0, 8)} ${r.duration}s  ${r.description}`);
  if (i <= Number(topArg) && r.audio_url) {
    const file = join(out, `${String(r.id).slice(0, 8)}.mp3`);
    if (!existsSync(file)) await downloadTo(r.audio_url, file);
    console.log('   saved', file);
  }
}
