#!/usr/bin/env node
'use strict';
/**
 * render.js — turn an icon SVG into every PNG an iPhone / PWA home-screen icon needs,
 * plus a "home screen preview" sheet so the icon can be judged at the sizes people see.
 *
 * Usage:
 *   node render.js <icon.svg> [--out <dir>] [--label "App name"] [--sizes 1024,512,192,180]
 *                             [--no-preview] [--grid] [--preview-dir <dir>] [--draft] [--quiet]
 *   node render.js --compare a.svg b.svg [c.svg …] [--out <dir>] [--label "App name"]
 *
 * Outputs (in --out, default: ./icons next to the SVG):
 *   icon.svg               copy of the source (kept so the HTML can also link an SVG favicon)
 *   icon-1024.png          master — in --preview-dir when given (it is a design file, nothing links it)
 *   apple-touch-icon.png   180×180 — what iOS puts on the home screen
 *   icon-512.png           manifest (Android / desktop PWA; also used as "maskable")
 *   icon-192.png           manifest
 *   icon-<n>.png           any extra size passed via --sizes
 *   preview.png            home-screen mock (dark + light wallpaper, small sizes) — LOOK AT THIS
 *   grid.png               (with --grid) 1024 render with the icon grid overlaid
 *
 * Renderer: Playwright + Chromium (full SVG filter support: blur, drop shadow, turbulence,
 * blend modes, system fonts). Falls back to rsvg-convert / ImageMagick when Playwright is
 * missing, with reduced fidelity for filters.
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawnSync } = require('child_process');

const HELP = `render.js — render an icon SVG to iPhone/PWA PNG sizes + a home-screen preview sheet

  node render.js <icon.svg> [options]

  --out <dir>        output directory (default: <svg dir>/icons)
  --label <text>     app name shown under the icon in the preview (default: "App")
  --sizes <list>     comma list of extra PNG sizes (default adds none beyond 1024,512,192,180)
  --no-preview       skip preview.png
  --grid             also write grid.png (icon with the layout grid overlaid)
  --preview-dir <d>  write icon-1024.png, preview.png and grid.png here instead of --out
                     (keeps design files out of a deployed folder such as public/icons)
  --draft            block-out / work-in-progress: render only icon-1024 + preview (+grid) into the
                     preview dir and leave the deployable PNGs in --out untouched
  --compare a b …    render 2–4 SVG variants side by side (hero + 60/29pt among bright neighbours,
                     both wallpapers) into <out>/compare.png — for choosing between concepts
  --quiet            less logging
`;

// The iOS "squircle" (continuous-curvature rounded square), normalized to a 0..1 box.
// Only used for the PREVIEW — the real apple-touch-icon must stay a full-bleed square,
// because iOS applies this mask itself.
const SQUIRCLE = [
  'M0.5,0',
  'C0.726,0 0.864,0 0.932,0.068',
  'C1,0.136 1,0.274 1,0.5',
  'C1,0.726 1,0.864 0.932,0.932',
  'C0.864,1 0.726,1 0.5,1',
  'C0.274,1 0.136,1 0.068,0.932',
  'C0,0.864 0,0.726 0,0.5',
  'C0,0.274 0,0.136 0.068,0.068',
  'C0.136,0 0.274,0 0.5,0 Z',
].join(' ');

function die(msg) {
  console.error(`render.js: ${msg}`);
  process.exit(1);
}

function parseArgs(argv) {
  const args = { svg: null, out: null, label: 'App', sizes: [], preview: true, grid: false, quiet: false, previewDir: null,
    draft: false, compare: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--compare') { args.compare = []; continue; }
    if (args.compare && !a.startsWith('-')) { args.compare.push(a); continue; }
    if (a === '--out' || a === '-o') args.out = argv[++i];
    else if (a === '--draft') args.draft = true;
    else if (a === '--label') args.label = argv[++i];
    else if (a === '--sizes') args.sizes = String(argv[++i]).split(',').map((s) => parseInt(s, 10)).filter((n) => n > 0);
    else if (a === '--no-preview') args.preview = false;
    else if (a === '--grid') args.grid = true;
    else if (a === '--preview-dir') args.previewDir = argv[++i];
    else if (a === '--quiet') args.quiet = true;
    else if (a === '--help' || a === '-h') { console.log(HELP); process.exit(0); }
    else if (a.startsWith('-')) die(`unknown option ${a}\n${HELP}`);
    else if (!args.svg) args.svg = a;
    else die(`unexpected argument ${a}`);
  }
  if (args.compare) {
    if (args.compare.length < 2 || args.compare.length > 4) die('--compare takes 2–4 SVG files');
    for (const f of args.compare) if (!fs.existsSync(f)) die(`no such file: ${f}`);
    if (!args.out) args.out = path.join(path.dirname(path.resolve(args.compare[0])), 'icon-design');
    return args;
  }
  if (!args.svg) die(`missing <icon.svg>\n${HELP}`);
  if (!fs.existsSync(args.svg)) die(`no such file: ${args.svg}`);
  if (!args.out) args.out = path.join(path.dirname(path.resolve(args.svg)), 'icons');
  if (args.draft && !args.previewDir) args.previewDir = path.join(path.dirname(path.resolve(args.out)), 'icon-design');
  return args;
}

/** Make sure the root <svg> has a square viewBox; strip fixed width/height so CSS can size it. */
function normalizeSvg(svgText) {
  const m = svgText.match(/<svg\b[^>]*>/i);
  if (!m) die('input does not look like an SVG (no <svg> root element)');
  let root = m[0];
  const vb = root.match(/viewBox\s*=\s*"([^"]+)"/i);
  let viewBox = vb ? vb[1].trim().split(/[\s,]+/).map(Number) : null;
  if (!viewBox || viewBox.length !== 4) {
    const w = parseFloat((root.match(/\bwidth\s*=\s*"([\d.]+)/i) || [])[1]);
    const h = parseFloat((root.match(/\bheight\s*=\s*"([\d.]+)/i) || [])[1]);
    if (!w || !h) die('SVG needs a viewBox (e.g. viewBox="0 0 1024 1024")');
    viewBox = [0, 0, w, h];
    root = root.replace(/<svg\b/i, `<svg viewBox="0 0 ${w} ${h}"`);
  }
  if (Math.abs(viewBox[2] - viewBox[3]) > 0.01) {
    console.warn(`render.js: WARNING viewBox is not square (${viewBox[2]}×${viewBox[3]}); the icon will be stretched.`);
  }
  root = root.replace(/\s(width|height)\s*=\s*"[^"]*"/gi, '');
  if (!/preserveAspectRatio/i.test(root)) root = root.replace(/<svg\b/i, '<svg preserveAspectRatio="xMidYMid meet"');
  return svgText.replace(m[0], root);
}

function loadPlaywright() {
  const names = ['playwright', 'playwright-core'];
  for (const n of names) { try { return require(n); } catch (_) { /* next */ } }
  try {
    const root = execSync('npm root -g', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    for (const n of names) { try { return require(path.join(root, n)); } catch (_) { /* next */ } }
  } catch (_) { /* no npm */ }
  return null;
}

async function launchBrowser(pw) {
  const opts = { headless: true };
  if (process.env.ICON_CHROME_PATH) opts.executablePath = process.env.ICON_CHROME_PATH;
  try {
    return await pw.chromium.launch(opts);
  } catch (e) {
    const candidates = ['/opt/pw-browsers/chromium', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome',
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'];
    for (const c of candidates) {
      if (fs.existsSync(c)) {
        try { return await pw.chromium.launch({ ...opts, executablePath: c }); } catch (_) { /* next */ }
      }
    }
    throw new Error(`could not launch Chromium (${e.message}).\n  Fix: npx playwright install chromium   (or set ICON_CHROME_PATH=/path/to/chrome)`);
  }
}

/** page.screenshot with retries: under load (several renders at once) Chromium sometimes
 *  answers "Unable to capture screenshot"; a short wait and a second attempt succeeds. */
async function shot(page, opts, tries = 3) {
  for (let i = 1; ; i++) {
    try { return await page.screenshot(opts); } catch (e) {
      if (i >= tries || !/capture screenshot|Target closed|timeout/i.test(String(e && e.message))) throw e;
      await page.waitForTimeout(250 * i);
    }
  }
}

async function renderSize(browser, svgText, size, file) {
  const page = await browser.newPage({ viewport: { width: size, height: size }, deviceScaleFactor: 1 });
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    html,body{margin:0;padding:0;background:transparent;overflow:hidden}
    svg{display:block;width:${size}px;height:${size}px}
  </style></head><body>${svgText}</body></html>`;
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(50);
  await shot(page, { path: file, omitBackground: true, clip: { x: 0, y: 0, width: size, height: size } });
  await page.close();
}

function previewHtml(pngDataUrl, label) {
  // Neighbours look like a real home screen: saturated tiles, bold white glyphs. Muted grey
  // placeholders flatter a timid icon; these don't. Generic shapes only — no real app's icon.
  const G = {
    ring: '<circle cx="60" cy="60" r="30" fill="none" stroke="#fff" stroke-width="13"/>',
    bars: '<rect x="30" y="34" width="60" height="12" rx="6" fill="#fff"/><rect x="30" y="54" width="60" height="12" rx="6" fill="#fff"/><rect x="30" y="74" width="40" height="12" rx="6" fill="#fff"/>',
    drop: '<path d="M60 26 C76 48 84 60 84 72 A24 24 0 0 1 36 72 C36 60 44 48 60 26Z" fill="#fff"/>',
    grid: '<rect x="30" y="30" width="26" height="26" rx="7" fill="#fff"/><rect x="64" y="30" width="26" height="26" rx="7" fill="#fff" opacity=".7"/><rect x="30" y="64" width="26" height="26" rx="7" fill="#fff" opacity=".7"/><rect x="64" y="64" width="26" height="26" rx="7" fill="#fff"/>',
    bolt: '<path d="M66 22 L36 66 H58 L52 98 L84 52 H62 Z" fill="#fff"/>',
    dot: '<circle cx="60" cy="60" r="26" fill="#fff"/><circle cx="60" cy="60" r="11" fill="#1c1c1e"/>',
    wave: '<path d="M26 70 C40 50 52 50 60 62 S80 76 94 56" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round"/>',
  };
  const neighbours = [
    ['#34c759', '#1f9a3e', G.bars, 'Lists'], ['#0a84ff', '#0056d6', G.ring, 'Focus'], ['#ff9f0a', '#e8590c', G.bolt, 'Energy'],
    ['#ff375f', '#c9184a', G.drop, 'Drops'], ['#5e5ce6', '#3a2fb8', G.grid, 'Board'], ['#1c1c1e', '#000000', G.wave, 'Waves'],
    ['#ffd60a', '#f4a100', G.dot, 'Spot'],
  ];
  const placeholders = (n) => Array.from({ length: n }, (_, i) => {
    const [a, b, glyph, name] = neighbours[i % neighbours.length];
    return `<div class="cell"><div class="icon sq" style="background:linear-gradient(180deg,${a},${b})">
      <svg viewBox="0 0 120 120" width="100%" height="100%">${glyph}</svg></div><div class="lbl">${name}</div></div>`;
  }).join('');
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const name = esc(label);
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  :root{--f:-apple-system,"SF Pro Text","Inter","Helvetica Neue",Arial,sans-serif}
  html,body{margin:0;padding:0}
  body{width:1800px;background:#0e0e11;color:#cfd0d6;font-family:var(--f)}
  .sheet{display:grid;grid-template-columns:520px 1fr;gap:36px;padding:36px}
  .sq{clip-path:url(#squircle)}
  .hero{display:flex;flex-direction:column;align-items:center;gap:22px;background:#1a1a20;border-radius:28px;padding:40px 20px}
  .hero .icon{width:420px;height:420px}
  .hero .icon img{width:100%;height:100%;display:block}
  .hero h1{font-size:30px;margin:0;color:#fff;font-weight:600}
  .hero p{margin:0;font-size:18px;color:#8e8f99;text-align:center;line-height:1.5}
  .panel{border-radius:28px;padding:36px 28px 20px}
  .dark{background:radial-gradient(circle at 25% 15%,#3d3f7a 0%,#1b1c33 45%,#0d0e1b 100%)}
  .light{background:linear-gradient(160deg,#fbe3d3 0%,#e9e3f5 50%,#d3e2fb 100%)}
  .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:28px 0;justify-items:center}
  .cell{display:flex;flex-direction:column;align-items:center;gap:10px}
  .icon{width:120px;height:120px;position:relative;overflow:hidden}
  .icon img{width:100%;height:100%;display:block}
  .icon svg{display:block}
  .lbl{font-size:22px;letter-spacing:-.01em}
  .dark .lbl{color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.35)}
  .light .lbl{color:#1b1b1f}
  .right{display:flex;flex-direction:column;gap:36px}
  .sizes{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:36px}
  .sizes .panel{display:flex;align-items:flex-end;justify-content:space-around;gap:20px;padding:34px 28px}
  .s{display:flex;flex-direction:column;align-items:center;gap:10px}
  .s .icon img{width:100%;height:100%}
  .s small{font-size:16px;opacity:.75}
  .dark .s small{color:#fff}.light .s small{color:#1b1b1f}
  .cap{font-size:15px;color:#6e6f78;padding:0 36px 24px;line-height:1.5}
  </style></head><body>
  <svg width="0" height="0" style="position:absolute"><defs><clipPath id="squircle" clipPathUnits="objectBoundingBox"><path d="${SQUIRCLE}"/></clipPath></defs></svg>
  <div class="sheet">
    <div class="hero">
      <div class="icon sq"><img src="${pngDataUrl}" alt=""></div>
      <h1>${name}</h1>
      <p>1024 master, masked the way iOS masks it.<br>Judge composition, lighting and color here.</p>
    </div>
    <div class="right">
      <div class="panel dark"><div class="grid">
        <div class="cell"><div class="icon sq"><img src="${pngDataUrl}" alt=""></div><div class="lbl">${name}</div></div>
        ${placeholders(7)}
      </div></div>
      <div class="panel light"><div class="grid">
        <div class="cell"><div class="icon sq"><img src="${pngDataUrl}" alt=""></div><div class="lbl">${name}</div></div>
        ${placeholders(7)}
      </div></div>
    </div>
    <div class="sizes">
      <div class="panel dark">
        <div class="s"><div class="icon sq" style="width:120px;height:120px"><img src="${pngDataUrl}" alt=""></div><small>60pt · home</small></div>
        <div class="s"><div class="icon sq" style="width:80px;height:80px"><img src="${pngDataUrl}" alt=""></div><small>40pt · spotlight</small></div>
        <div class="s"><div class="icon sq" style="width:58px;height:58px"><img src="${pngDataUrl}" alt=""></div><small>29pt · settings</small></div>
        <div class="s"><div class="icon sq" style="width:40px;height:40px"><img src="${pngDataUrl}" alt=""></div><small>20pt · notif</small></div>
      </div>
      <div class="panel light">
        <div class="s"><div class="icon sq" style="width:120px;height:120px"><img src="${pngDataUrl}" alt=""></div><small>60pt · home</small></div>
        <div class="s"><div class="icon sq" style="width:80px;height:80px"><img src="${pngDataUrl}" alt=""></div><small>40pt · spotlight</small></div>
        <div class="s"><div class="icon sq" style="width:58px;height:58px"><img src="${pngDataUrl}" alt=""></div><small>29pt · settings</small></div>
        <div class="s"><div class="icon sq" style="width:40px;height:40px"><img src="${pngDataUrl}" alt=""></div><small>20pt · notif</small></div>
      </div>
    </div>
  </div>
  <div class="cap">Rendered at 2× (1pt = 2px). The squircle mask here is a close approximation of the one iOS applies; the exported PNGs stay square on purpose.</div>
  </body></html>`;
}

async function svgToDataUrl(browser, svgText, size) {
  const page = await browser.newPage({ viewport: { width: size, height: size }, deviceScaleFactor: 1 });
  await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:transparent}
    svg{display:block;width:${size}px;height:${size}px}</style></head><body>${svgText}</body></html>`, { waitUntil: 'load' });
  await page.waitForTimeout(50);
  const buf = await shot(page, { omitBackground: true, clip: { x: 0, y: 0, width: size, height: size } });
  await page.close();
  return 'data:image/png;base64,' + buf.toString('base64');
}

async function renderCompare(browser, files, label, file) {
  const variants = [];
  // label each variant with the shortest path suffix that tells it apart from the others
  const parts = files.map((f) => path.resolve(f).split(path.sep).filter(Boolean));
  const labelOf = (i) => {
    for (let k = 1; k <= parts[i].length; k++) {
      const tail = parts[i].slice(-k).join('/');
      if (parts.every((q, j) => j === i || q.slice(-k).join('/') !== tail)) {
        const p = parts[i];
        return k <= 2 ? tail : `${p[p.length - k]}/…/${p[p.length - 1]}`;   // the folder that differs + file name
      }
    }
    return parts[i].join('/');
  };
  for (const [i, f] of files.entries()) {
    const shown = labelOf(i);
    variants.push({ name: `${String.fromCharCode(65 + i)} · ${shown}`, url: await svgToDataUrl(browser, normalizeSvg(fs.readFileSync(f, 'utf8')), 512) });
  }
  const tile = (url, px) => `<div class="i sq" style="width:${px}px;height:${px}px"><img src="${url}"></div>`;
  const nb = (bg, glyph) => `<div class="i sq" style="width:104px;height:104px;background:${bg}"><svg viewBox="0 0 120 120" width="100%" height="100%">${glyph}</svg></div>`;
  const ring = '<circle cx="60" cy="60" r="30" fill="none" stroke="#fff" stroke-width="13"/>';
  const bolt = '<path d="M66 22 L36 66 H58 L52 98 L84 52 H62 Z" fill="#fff"/>';
  const col = (v) => `<div class="col"><div class="h">${tile(v.url, 300)}</div><div class="n">${v.name}</div>
    <div class="p dark">${nb('linear-gradient(180deg,#0a84ff,#0056d6)', ring)}${tile(v.url, 104)}${nb('linear-gradient(180deg,#ff9f0a,#e8590c)', bolt)}</div>
    <div class="p light">${nb('linear-gradient(180deg,#34c759,#1f9a3e)', ring)}${tile(v.url, 104)}${tile(v.url, 58)}${tile(v.url, 40)}</div></div>`;
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
  body{margin:0;background:#0e0e11;font-family:-apple-system,"SF Pro Text",Inter,"Helvetica Neue",Arial,sans-serif;color:#fff}
  .w{display:flex;gap:28px;padding:30px}.col{display:flex;flex-direction:column;align-items:center;gap:16px;width:380px}
  .sq{clip-path:url(#squircle)}.i{overflow:hidden;flex:none}.i img{width:100%;height:100%;display:block}
  .n{font-size:20px;color:#cfd0d6}.p{display:flex;gap:18px;align-items:center;justify-content:center;width:380px;height:170px;border-radius:22px}
  .dark{background:radial-gradient(circle at 25% 15%,#3d3f7a 0%,#1b1c33 45%,#0d0e1b 100%)}.light{background:linear-gradient(160deg,#fbe3d3 0%,#e9e3f5 50%,#d3e2fb 100%)}
  </style></head><body><svg width="0" height="0" style="position:absolute"><defs><clipPath id="squircle" clipPathUnits="objectBoundingBox"><path d="${SQUIRCLE}"/></clipPath></defs></svg>
  <div class="w">${variants.map(col).join('')}</div></body></html>`;
  const page = await browser.newPage({ viewport: { width: 60 + variants.length * 408, height: 800 }, deviceScaleFactor: 1 });
  await page.setContent(html, { waitUntil: 'load' });
  await shot(page, { path: file, fullPage: true });
  await page.close();
}

async function renderPreview(browser, masterPng, label, file) {
  const dataUrl = 'data:image/png;base64,' + fs.readFileSync(masterPng).toString('base64');
  const page = await browser.newPage({ viewport: { width: 1800, height: 1000 }, deviceScaleFactor: 1 });
  await page.setContent(previewHtml(dataUrl, label), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(80);
  await shot(page, { path: file, fullPage: true });
  await page.close();
}

async function renderGrid(browser, masterPng, gridSvgPath, file) {
  const dataUrl = 'data:image/png;base64,' + fs.readFileSync(masterPng).toString('base64');
  const grid = fs.readFileSync(gridSvgPath, 'utf8');
  const page = await browser.newPage({ viewport: { width: 1024, height: 1024 }, deviceScaleFactor: 1 });
  await page.setContent(`<!doctype html><html><head><style>html,body{margin:0}
    .w{position:relative;width:1024px;height:1024px}.w img,.w svg{position:absolute;inset:0;width:1024px;height:1024px}</style></head>
    <body><div class="w"><img src="${dataUrl}">${grid}</div></body></html>`, { waitUntil: 'load' });
  await shot(page, { path: file, clip: { x: 0, y: 0, width: 1024, height: 1024 } });
  await page.close();
}

/** Fallback without a browser: rsvg-convert or ImageMagick. Filters/blend modes may degrade. */
function fallbackRender(svgPath, size, file) {
  const tryCmd = (cmd, argv) => {
    const r = spawnSync(cmd, argv, { stdio: 'ignore' });
    return r.status === 0 && fs.existsSync(file);
  };
  if (tryCmd('rsvg-convert', ['-w', String(size), '-h', String(size), '-o', file, svgPath])) return 'rsvg-convert';
  if (tryCmd('magick', ['-background', 'none', '-density', '300', svgPath, '-resize', `${size}x${size}`, file])) return 'magick';
  if (tryCmd('convert', ['-background', 'none', '-density', '300', svgPath, '-resize', `${size}x${size}`, file])) return 'convert';
  return null;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const log = (...a) => { if (!args.quiet) console.log(...a); };
  if (args.compare) {
    const pw = loadPlaywright();
    if (!pw) die('--compare needs Playwright (npm i -D playwright && npx playwright install chromium)');
    fs.mkdirSync(args.out, { recursive: true });
    const browser = await launchBrowser(pw);
    try { await renderCompare(browser, args.compare, args.label, path.join(args.out, 'compare.png')); } finally { await browser.close(); }
    log(`  compare.png  (${args.compare.length} variants) → ${args.out}`);
    return;
  }
  const raw = fs.readFileSync(args.svg, 'utf8');
  const svgText = normalizeSvg(raw);
  const pdir = args.previewDir || args.out;
  fs.mkdirSync(pdir, { recursive: true });
  if (!args.draft) {
    fs.mkdirSync(args.out, { recursive: true });
    fs.writeFileSync(path.join(args.out, 'icon.svg'), raw);
  }
  const plan = [
    { size: 1024, name: 'icon-1024.png', dir: pdir },
    ...(args.draft ? [] : [
      { size: 512, name: 'icon-512.png' },
      { size: 192, name: 'icon-192.png' },
      { size: 180, name: 'apple-touch-icon.png' },
      ...args.sizes.filter((s) => ![1024, 512, 192, 180].includes(s)).map((s) => ({ size: s, name: `icon-${s}.png` })),
    ]),
  ].map((p) => ({ ...p, dir: p.dir || args.out }));

  const pw = loadPlaywright();
  if (!pw) {
    console.warn('render.js: Playwright not found — using fallback renderer (filters may look wrong).');
    console.warn('           For full fidelity: npm i -D playwright && npx playwright install chromium');
    const tmpSvg = path.join(pdir, '.normalized.svg');
    fs.writeFileSync(tmpSvg, svgText.replace(/<svg\b/i, '<svg width="1024" height="1024"'));
    let used = null;
    for (const p of plan) {
      used = fallbackRender(tmpSvg, p.size, path.join(p.dir, p.name));
      if (!used) die('no renderer available. Install Playwright (npm i -D playwright && npx playwright install chromium) or rsvg-convert.');
      log(`  ${p.name}  (${p.size}×${p.size}, via ${used})`);
    }
    fs.unlinkSync(tmpSvg);
    console.warn('render.js: preview.png skipped (needs Playwright).');
    return;
  }

  const browser = await launchBrowser(pw);
  try {
    for (const p of plan) {
      const file = path.join(p.dir, p.name);
      await renderSize(browser, svgText, p.size, file);
      log(`  ${path.relative(process.cwd(), file) || p.name}  (${p.size}×${p.size})`);
    }
    const master = path.join(pdir, 'icon-1024.png');
    if (args.preview) {
      const file = path.join(pdir, 'preview.png');
      await renderPreview(browser, master, args.label, file);
      log(`  preview.png  ← open this and look at it before deciding the icon is done`);
    }
    if (args.grid) {
      const gridSvg = path.join(__dirname, '..', 'assets', 'grid.svg');
      if (fs.existsSync(gridSvg)) {
        const file = path.join(pdir, 'grid.png');
        await renderGrid(browser, master, gridSvg, file);
        log(`  grid.png  (icon + layout grid)`);
      } else {
        console.warn('render.js: assets/grid.svg not found, skipping grid.png');
      }
    }
  } finally {
    await browser.close();
  }
  // file size: grain and photographic texture do not compress; flag what a phone will download
  const kb = (f) => { try { return fs.statSync(path.join(args.out, f)).size / 1024; } catch (_) { return 0; } };
  const heavy = [['apple-touch-icon.png', 100], ['icon-192.png', 100], ['icon-512.png', 300]]
    .filter(([f, lim]) => kb(f) > lim).map(([f, lim]) => `${f} ${kb(f).toFixed(0)} KB (> ${lim})`);
  if (heavy.length) console.warn(`render.js: heavy files: ${heavy.join(', ')} — usually film grain; lower its alpha or drop it`);
  if (args.draft) log(`draft → ${pdir} (deployable PNGs in ${args.out} untouched)`);
  else log(`done → ${args.out}${args.previewDir ? `  (master + previews in ${args.previewDir})` : ''}`);
}

main().catch((e) => { console.error(`render.js: ${e.message}`); process.exit(1); });
