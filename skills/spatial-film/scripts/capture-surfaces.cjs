// Pre-renders the "captured" surfaces a film shows (third-party canvases, a long web page, product screens)
// to 2x PNG once, so every scene shows identical pixels and the DOM stays light.
// Run from the film project root:  node <skill>/scripts/capture-surfaces.cjs
// Reads src/captures/jobs.json: [{ "file": "ghl.html", "out": "ghl-sheet.png", "w": 1135, "h": 2022, "scale": 2,
//   "bodyClass": "branded" (optional) }]. Each HTML must wrap the surface in #surface. An optional
//   src/captures/sprite.svg replaces a <!--SPRITE--> comment (shared icon symbols). Output: assets/captures/.
const path = require('path');
const fs = require('fs');
const os = require('os');

function playwright() {
  const tries = [process.env.PLAYWRIGHT_PATH, 'playwright',
    path.join(os.homedir(), '.baet/skills/playwright-skill/node_modules/playwright')].filter(Boolean);
  for (const t of tries) { try { return require(t); } catch {} }
  throw new Error('playwright not found - set PLAYWRIGHT_PATH or npm i -D playwright');
}

const SRC = path.resolve('src/captures');
const OUT = path.resolve('assets/captures');
const jobs = JSON.parse(fs.readFileSync(path.join(SRC, 'jobs.json'), 'utf8'));
const spritePath = path.join(SRC, 'sprite.svg');
const sprite = fs.existsSync(spritePath) ? fs.readFileSync(spritePath, 'utf8') : '';

(async () => {
  const { chromium } = playwright();
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: j.scale || 2 });
    const html = fs.readFileSync(path.join(SRC, j.file), 'utf8').replace('<!--SPRITE-->', sprite);
    const tmp = path.join(SRC, `.tmp-${j.out}.html`);
    fs.writeFileSync(tmp, html);
    try {
      await page.goto('file:///' + tmp.replace(/\\/g, '/'), { waitUntil: 'networkidle' });
      await page.evaluate(async (c) => { if (c) document.body.classList.add(c); await document.fonts.ready; }, j.bodyClass || '');
      await page.waitForTimeout(300);
      await page.locator('#surface').screenshot({ path: path.join(OUT, j.out) });
      console.log('wrote', j.out, `${j.w * (j.scale || 2)}x${j.h * (j.scale || 2)}`);
    } finally {
      fs.unlinkSync(tmp);
      await page.close();
    }
  }
  await browser.close();
})();
