// Prints 1x boxes [x, y, w, h] of every element matching a selector on a capture surface (+ its first text node),
// so storyboard blocks and workers get exact annotation / crop targets instead of eyeballed ones.
// Run from the film project root:  node <skill>/scripts/measure-surface.cjs src/captures/ghl.html ".gh-card, .gh-trig"
// Paste the output into references/snippets.html under "CAPTURE MAP" (multiply by the display scale in a scene).
const path = require('path');
const fs = require('fs');
const os = require('os');
const [file, selector] = process.argv.slice(2);
if (!file || !selector) { console.error('usage: measure-surface.cjs <surface.html> "<selector>"'); process.exit(1); }
function playwright() {
  for (const t of [process.env.PLAYWRIGHT_PATH, 'playwright',
    path.join(os.homedir(), '.baet/skills/playwright-skill/node_modules/playwright')].filter(Boolean)) {
    try { return require(t); } catch {}
  }
  throw new Error('playwright not found - set PLAYWRIGHT_PATH');
}
(async () => {
  const dir = path.dirname(path.resolve(file));
  const sp = path.join(dir, 'sprite.svg');
  const html = fs.readFileSync(file, 'utf8').replace('<!--SPRITE-->', fs.existsSync(sp) ? fs.readFileSync(sp, 'utf8') : '');
  const tmp = path.join(dir, '.tmp-measure.html');
  fs.writeFileSync(tmp, html);
  const b = await playwright().chromium.launch();
  try {
    const p = await b.newPage({ viewport: { width: 2400, height: 2400 } });
    await p.goto('file:///' + tmp.replace(/\\/g, '/'), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    const out = await p.evaluate((sel) => {
      const s = document.getElementById('surface').getBoundingClientRect();
      const r = (b) => [Math.round(b.x - s.x), Math.round(b.y - s.y), Math.round(b.width), Math.round(b.height)];
      return [...document.querySelectorAll(sel)].map((el) => {
        const tn = [...el.childNodes].find((n) => n.nodeType === 3 && n.textContent.trim());
        let text = null;
        if (tn) { const rg = document.createRange(); rg.selectNodeContents(tn); text = r(rg.getBoundingClientRect()); }
        return { label: el.textContent.replace(/\s+/g, ' ').trim().slice(0, 48), box: r(el.getBoundingClientRect()), text };
      });
    }, selector);
    out.forEach((o) => console.log(JSON.stringify(o)));
  } finally {
    fs.unlinkSync(tmp);
    await b.close();
  }
})();
