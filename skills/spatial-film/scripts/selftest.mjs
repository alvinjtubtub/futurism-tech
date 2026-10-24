#!/usr/bin/env node
// End-to-end proof that spatial-film works on this machine. Run after ANY edit to the skill.
// Usage: node <skill>/scripts/selftest.mjs [work dir]   (default: a fresh folder in the OS temp dir, kept for a look)
// Steps: new-film -> two scenes from the starter with a shared seam -> harness lint + snapshot -> assemble ->
//        hyperframes check -> seam-check (one seam + the loop) -> render (hardware GPU) -> ffprobe 60 fps -> web encode.
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const work = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), "spatial-film-selftest-"));
const film = path.join(work, "film");
// Python 3.10+: config.json from setup-check, else probe py -3.12 / python3.12 / python3 / python (kept inline: the engine stays standalone)
const pyOk = (c) => { const r = spawnSync(c[0], [...c.slice(1), "--version"], { encoding: "utf8" });
  const m = r.status === 0 && /Python (\d+)\.(\d+)/.exec((r.stdout || "") + (r.stderr || "")); return !!m && (+m[1] > 3 || (+m[1] === 3 && +m[2] >= 10)); };
let PYCMD = null;
const wsRoot = path.resolve(here, "..", "..", "..");
const cfgHome = process.env.KAPE_EXPLAINER_HOME || (fs.existsSync(path.join(wsRoot, "config.json")) ? wsRoot : path.join(os.homedir(), ".kape-explainer"));
try { const c = JSON.parse(fs.readFileSync(path.join(cfgHome, "config.json"), "utf8")).python; if (Array.isArray(c) && pyOk(c)) PYCMD = c; } catch {}
const vbin = (r, d) => path.join(r, d, process.platform === "win32" ? "Scripts" : "bin", process.platform === "win32" ? "python.exe" : "python");
PYCMD ||= [[vbin(wsRoot, ".venv")], [vbin(wsRoot, "venv")], [vbin(path.join(os.homedir(), ".kape-explainer"), "venv")], ["py", "-3.12"], ["python3.12"], ["python3"], ["python"], ["py", "-3"]].find(pyOk);
if (!PYCMD) { console.error("Python 3.10+ not found - run kape-explainer's setup-check.mjs"); process.exit(1); }
const results = [];
const check = (name, ok, detail = "") => results.push(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? "  -- " + detail : ""}`);
// npx is a .cmd shim on Windows, so it needs a shell; node and python must not get one (paths with spaces)
const sh = (cmd, a, cwd = film) => spawnSync(cmd, a, { cwd, encoding: "utf8", maxBuffer: 1 << 28,
  shell: process.platform === "win32" && cmd === "npx" });
const py = (script, a = []) => sh(PYCMD[0], [...PYCMD.slice(1), path.join(here, script), ...a]);
const tail = (r) => (r.error ? r.error.message : `${r.stdout || ""}${r.stderr || ""}`).trim().split("\n").slice(-6).join(" | ");
fs.mkdirSync(work, { recursive: true });

try {
  let r = sh(process.execPath, [path.join(here, "new-film.mjs"), film, "--name", "selftest"], work);
  check("new-film scaffolds the template", r.status === 0 && fs.existsSync(path.join(film, "film.json")), tail(r));

  const cfg = JSON.parse(fs.readFileSync(path.join(film, "film.json"), "utf8"));
  Object.assign(cfg, { scenes: [["s01-open", 2], ["s02-close", 2]], sfx: {}, cues: [] });
  delete cfg.bgm;
  fs.writeFileSync(path.join(film, "film.json"), JSON.stringify(cfg, null, 2));
  const dur = +(2 * 4 * 60 / cfg.bpm).toFixed(4);
  const starter = fs.readFileSync(path.join(film, "references", "scene-starter.html"), "utf8")
    .replace(/^<!--[\s\S]*?-->\s*/, "");
  for (const id of ["s01-open", "s02-close"])
    fs.writeFileSync(path.join(film, "compositions", `${id}.html`), starter.replaceAll("SCENE", id).replaceAll("DUR", String(dur)));

  r = py("make-harness.py");
  check("make-harness builds one test project per scene", r.status === 0, tail(r));
  r = sh(process.execPath, [path.join(here, "test-scene.mjs"), "s01-open", `0.5,${dur - 0.05}`]);
  const snaps = path.join(film, ".hyperframes", "test", "s01-open", "snaps");
  check("harness: scene lints with 0 errors and snapshots", /0 errors/.test(r.stdout) &&
    fs.existsSync(snaps) && fs.readdirSync(snaps).filter((f) => f.endsWith(".png")).length === 2, tail(r));

  r = py("assemble.py");
  check("assemble writes index.html from film.json", r.status === 0 && fs.existsSync(path.join(film, "index.html")), tail(r));
  r = sh("npx", ["--prefer-offline", "--yes", `hyperframes@${cfg.hyperframes}`, "check"]);
  check("hyperframes check passes", r.status === 0 && /Check passed/.test(r.stdout + r.stderr), tail(r));
  r = py("seam-check.py");
  check("seam-check: seam + loop match by pixels", r.status === 0 && /2\/2 seams match/.test(r.stdout), tail(r));

  r = sh(process.execPath, [path.join(here, "render-final.mjs"), "selftest"]);
  const out = r.stdout + r.stderr;
  check("render on the hardware GPU path", r.status === 0 && /gpu mode: hardware/.test(out), tail(r));
  check("render is 1920x1080 at 60 fps", /width=1920/.test(out) && /height=1080/.test(out) && /r_frame_rate=60\/1/.test(out));

  const mp4 = path.join(film, "renders", "selftest.mp4");
  if (fs.existsSync(mp4)) {
    r = sh(process.execPath, [path.join(here, "encode-web.mjs"), mp4, path.join(film, "web"), "--name", "selftest", "--poster", "1", "--silent"]);
    check("web encode + poster", r.status === 0 && fs.existsSync(path.join(film, "web", "selftest-poster.jpg")), tail(r));
  }
} catch (e) {
  check("selftest ran without throwing", false, e.message);
}
console.log(results.join("\n"));
const failed = results.filter((l) => l.startsWith("FAIL")).length;
console.log(failed ? `FAIL (${failed})  work dir: ${work}` : `PASS  work dir: ${work}`);
process.exit(failed ? 1 : 0);
