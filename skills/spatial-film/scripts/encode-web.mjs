#!/usr/bin/env node
// Web encode of the master render + a poster frame. Keeps the music/SFX (AAC 160k) - the page still autoplays
// muted; add --silent for a video-only file. CRF 21 is the tested sweet spot for flat motion graphics that move
// every frame (about 6 MB per 32 s at 1080p60, SSIM ~0.997 vs the master). Never ship the master itself.
// Usage: node <skill>/scripts/encode-web.mjs <master.mp4> <out dir> [--name film] [--poster 10.8] [--crf 21] [--silent]
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const [master, outDir] = args;
if (!master || !outDir) {
  console.error("usage: encode-web.mjs <master.mp4> <out dir> [--name film] [--poster 10.8] [--crf 21] [--silent]");
  process.exit(1);
}
const opt = (k, d) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const run = (cmd, a) => {
  const r = spawnSync(cmd, a, { encoding: "utf8" });
  if (r.status !== 0) { console.error(r.stderr); process.exit(1); }
  return r.stdout;
};
const name = opt("--name", "film"), poster = opt("--poster", "10.8"), crf = opt("--crf", "21");
const [n, d] = run("ffprobe", ["-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
  "-of", "csv=p=0", master]).trim().split("/").map(Number);
const fps = Math.round(n / (d || 1));
fs.mkdirSync(outDir, { recursive: true });
const mp4 = path.join(outDir, `${name}.mp4`), jpg = path.join(outDir, `${name}-poster.jpg`);
const audio = args.includes("--silent") ? ["-an"] : ["-c:a", "aac", "-b:a", "160k"];
run("ffmpeg", ["-y", "-v", "error", "-i", master, ...audio, "-c:v", "libx264", "-preset", "slower", "-crf", crf,
  "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", fps > 30 ? "4.2" : "4.1", "-tune", "animation",
  "-movflags", "+faststart", "-g", String(fps * 2), mp4]);
run("ffmpeg", ["-y", "-v", "error", "-ss", poster, "-i", master, "-frames:v", "1", "-q:v", "2", jpg]);
console.log(`${mp4} (${(fs.statSync(mp4).size / 1e6).toFixed(1)} MB)\n${jpg}`);
