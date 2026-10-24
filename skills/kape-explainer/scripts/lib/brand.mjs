// Brand profile helpers shared by profile.mjs and new-explainer.mjs: defaults, merge, accent_dark derivation.
// Usage: import { loadBrand, mergeBrand, profileDir, expandHome } from './lib/brand.mjs';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { homeDir } from './python.mjs';

export const DEFAULTS = {
  name: '', wordmark: null, logo: null, logo_has_text: false, ink: '#1F2937', accent: '#2563EB', accent_dark: null,
  opener: 'explains', cta: 'Follow for more', presenter: 'KAPE', language: 'English', films_dir: '~/KapeExplainer/films',
};

export function profileDir(profileArg = process.env.KAPE_PROFILE) {
  if (!profileArg || profileArg === 'default') return path.join(homeDir(), 'profile');
  if (profileArg.includes('/') || profileArg.includes('\\') || fs.existsSync(profileArg)) {
    return path.resolve(profileArg);
  }
  const named = path.join(homeDir(), 'profiles', profileArg);
  if (fs.existsSync(named)) return named;
  if (profileArg === 'tech-explanasyon' && fs.existsSync(path.join(homeDir(), 'profile', 'brand.json'))) {
    return path.join(homeDir(), 'profile');
  }
  return named;
}

export function listProfiles() {
  const out = [];
  const defDir = path.join(homeDir(), 'profile');
  if (fs.existsSync(path.join(defDir, 'brand.json'))) {
    try {
      const b = mergeBrand(JSON.parse(fs.readFileSync(path.join(defDir, 'brand.json'), 'utf8')));
      out.push({ id: 'default', dir: defDir, brand: b });
    } catch {}
  }
  const profilesRoot = path.join(homeDir(), 'profiles');
  if (fs.existsSync(profilesRoot)) {
    for (const e of fs.readdirSync(profilesRoot, { withFileTypes: true })) {
      if (!e.isDirectory()) continue;
      const pDir = path.join(profilesRoot, e.name);
      if (fs.existsSync(path.join(pDir, 'brand.json'))) {
        try {
          const b = mergeBrand(JSON.parse(fs.readFileSync(path.join(pDir, 'brand.json'), 'utf8')));
          out.push({ id: e.name, dir: pDir, brand: b });
        } catch {}
      }
    }
  }
  return out;
}

export const expandHome = (p) => (p === '~' || /^~[\\/]/.test(p) ? path.join(os.homedir(), p.slice(1)) : p);

// accent darkened ~25% in HSL lightness
export function darken(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex || '');
  if (!m) return '#1E40AF';
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(m[1].slice(i, i + 2), 16) / 255);
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, d = mx - mn;
  let h = 0, s = 0;
  if (d) {
    s = d / (1 - Math.abs(2 * l - 1));
    h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
    h *= 60; if (h < 0) h += 360;
  }
  const l2 = l * 0.75, c = (1 - Math.abs(2 * l2 - 1)) * s, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), mm = l2 - c / 2;
  const [r1, g1, b1] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  return '#' + [r1, g1, b1].map((v) => Math.round((v + mm) * 255).toString(16).padStart(2, '0')).join('').toUpperCase();
}

export function mergeBrand(raw) {
  const b = { ...DEFAULTS, ...Object.fromEntries(Object.entries(raw || {}).filter(([, v]) => v !== undefined)) };
  if (!b.name) throw new Error('brand.json needs a "name"');
  if (typeof b.wordmark === 'string') b.wordmark = b.wordmark.split(',').map((s) => s.trim()).filter(Boolean).slice(0, 2);
  if (!b.wordmark || !b.wordmark.length) { const w = b.name.trim().split(/\s+/); b.wordmark = w.length > 1 ? [w[0], w.slice(1).join(' ')] : [b.name]; }
  if (!b.accent_dark) b.accent_dark = darken(b.accent);
  return b;
}

export function loadBrand(profileArg = process.env.KAPE_PROFILE) {
  const f = path.join(profileDir(profileArg), 'brand.json');
  if (!fs.existsSync(f)) throw new Error(`no profile at ${f} - run: node <skill>/scripts/profile.mjs init --name "<your name>"`);
  return mergeBrand(JSON.parse(fs.readFileSync(f, 'utf8')));
}
