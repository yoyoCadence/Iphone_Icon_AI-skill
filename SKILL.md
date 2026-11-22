---
name: iphone-icon
description: Design and ship a beautiful, app-specific iPhone home-screen icon (apple-touch-icon) and PWA icon set for a web page, then wire it into the HTML and manifest. Use this whenever a user wants a mobile web page to be saved to / added to the home screen, mentions apple-touch-icon, "Add to Home Screen", PWA or manifest icons, an app icon or logo for a website or web app, a favicon for a phone, or writes 加到主畫面 / 主畫面圖示 / 網頁 icon / app icon / 圖示 — even if they only ask to "make the page installable" or "make it look like an app". Produces an SVG master, PNGs at 1024/512/192/180, a home-screen preview sheet, and the head tags + manifest. Designs the icon from the app's purpose with real lighting and material, not a centred geometric placeholder.
compatibility: Node.js ≥ 18 with Playwright + Chromium for rendering (`npm i -D playwright && npx playwright install chromium`; falls back to rsvg-convert / ImageMagick with reduced fidelity). Python 3 with Pillow for validate.py. Reads PNGs with the Read tool to critique the result.
---

# iPhone home-screen icon

You are designing the smallest piece of brand a product will ever have: a ~60pt tile that must be
read in 200 ms among twenty bright neighbours, must not be confusable with any other app, and must
still look designed at 1024 px. Treat it as a design job with an engineering delivery at the end —
not as "draw a shape on a gradient and export".

Reply in the user's language. Keep the conversation short and the work visible: concept note →
rendered preview → revision → delivery.

## Workflow

### 0. Is there already an icon? (30 seconds, saves the most damage)
Search the project before designing: `apple-touch-icon`, `manifest`, an icon source SVG, an icon
build script (`npm run icons`, `make-icons`, `pwa-asset-generator`…), tests that open the icon PNGs,
and a service worker. If any exist, **the project's pipeline and tests are the contract**: edit its
source, run its build, run its tests, keep its tag wiring and file paths. Render the *current* icon
with `render.js` too, so you critique and present before/after rather than a cold redesign — and
treat an existing icon's colours and motif as brand equity to evolve unless the user asks for new.

### 1. Brief (≤ 2 minutes)
Collect: **name** (as shown under the icon, ≤ 11 chars), **what it does** in one sentence,
**tone** (three adjectives), **existing colours/logo**, **audience**. For an HTML/CSS project run
`python3 scripts/extract_brand.py <files>`. Fill gaps with stated assumptions instead of
questions — one line: "Assuming: calm, outdoorsy, no brand colour yet — say so if wrong."

### 2. Market, concept, style (write it down before drawing)
Read `references/design-process.md` §1–3 the first time you use this skill in a session.

**Map the market first.** Name the 3–5 icons a user of this category already has (Spotify, Apple
Music…) and their language — tile · mark · style. If you can get their PNGs (the user's folder, or an
App Store lookup when the network allows it), keep them in a folder outside the project and use it
as `--neighbours` for every render. Most category leaders are flat brand marks; rendered 3D objects
are the exception (design-process §2a).

Then write the concept note in the format shown there (App/tone · Market · Essence · Idea · Style ·
Palette · Light).
The idea must pass three tests: readable at **29pt** from silhouette alone; **ownable** ("could
this be any app in the category?" must be *no*); **no collision** with a famous icon combo.
Use `references/metaphors.md` for category twists and `references/palettes.md` for colours.
**Choose the style on purpose — this is where icon sets go monotonous.** Shortlist one style from
the *graphic* family (H Brand Mark, F Letterform, E Luminous, D Paper, C Glass) and one from the
*illustrative* family (A Lit Glyph, B Rendered Object, G Scene, I Character). Bring both to **equal
fidelity** — the illustrative one gets its light and material, not just a flat silhouette — then
`render.js --compare a.svg b.svg --neighbours <market>`. Decide: (1) 29pt is a pass/fail gate, not a
ranking; (2) distance from every leader, where style family weighs most if the category shares one;
(3) tone. Never break a tie toward "more volume" or toward "fewer pixels" — each produced a
monoculture in testing. Skip a family only when the brief rules it out, and say why.

The worked examples in `assets/examples/` calibrate quality. When a brief is in an example's
category, don't reuse the example's *twist, palette or execution* — but keep the category's core sign
(a prompt for a terminal, a coin or ledger for money) if legibility needs it; dropping it to be
different trades away the 29pt read. If the user's real brand colours happen to match an example's,
the brand wins: keep the colours and differ in object, composition or which colour is the tile.

### 3. Build the SVG — bold first, beautiful second
1. **Block out** the silhouette in flat colours, render it with `--draft` (step 4; previews only,
   deployable PNGs untouched), and check the 29pt tile among the bright neighbours in `preview.png`. Category leaders' marks cover 15–30 % of the tile
   (median 20 %); rendered objects usually need 25–40 %; line/glow glyphs can be thinner if
   contrast is ≥ 4:1 (`validate.py` reports coverage).
   Refinement never rescues a subject that is too small or too pale — fix that here.
2. **Then finish it by the style's own standard** (`references/styles.md`): graphic styles get exact
   geometry, clean joins and at most one gradient — no shadows, rims or grain, and many are done at
   the block-out; illustrative styles get the full material treatment.
   Styles A/B/E start from `assets/scaffold.svg` (lighting rig pre-wired); the others start from their
   recipe and reuse only the scaffold's filters. For a stroke whose width or colour must change along
   its length (trail, orbit, brush, swoosh), generate it with `scripts/ribbon.py`.

Rules that come from how iOS and SVG behave — not stylistic preferences:
- Full-bleed **opaque square**; no rounded corners, no outer shadow, no transparent margin
  (iOS masks the squircle and composites over black).
- Main subject inside the centre ~62 % (x,y ≈ 195…830); corners carry only background.
- Glyph strokes ≥ 28 px, gaps ≥ 24 px at 1024; text only in style F (an initial, or a wordmark of
  ≤ 5 letters that is still legible at 60pt).
- Illustrative styles: one light source (top-left unless the scene has its own sun); tinted shadows,
  never black. Graphic styles have no light source.
- Filter regions cover the canvas: `filterUnits="userSpaceOnUse" x="-256" y="-256" width="1536" height="1536"`.
  Percentage regions clip stroked and thin shapes into hard edges.
- Colour discipline: two hues in the tile, one hero object/glyph, at most one secondary accent.

### 4. Render → look → critique → revise
```bash
node  scripts/render.js  icon.svg --out icons --preview-dir icon-design --label "Name" --grid   # add --draft for block-outs
python3 scripts/validate.py icon-design/icon-1024.png
```
**Read `icon-design/preview.png`** (renders as an image) and go through `references/critique.md`
in order: 29pt test → neighbour test → ownership → scale/centre → light/material → restraint.
Then open `icon-design/grid.png` (1024) for what the small sheet hides: clipped blurs, sliced tips,
banding, stray seams. Fix the top two findings, re-render, look again. Block-outs and side-by-side
comparisons don't count as rounds; expect one to three material rounds after the block-out, and small
local fixes are fine. If the *concept* had to change twice, go back to step 2. `validate.py` gives mechanical facts
(transparency, coverage, centre of mass, contrast, corner intrusion); your eyes judge the rest.

### 5. Deliver
- **Page without icon wiring:** `python3 scripts/inject.py index.html --name "Name" --bg "#tile-bottom"`.
  It keeps the page's own `theme-color`, status-bar and web-app choices unless you pass the matching
  option (`--theme` = the brand colour for a page that has none), writes or updates the manifest, and
  cache-busts.
- **Pick the URL style by how the site is served:** all pages in one folder (plain HTML, GitHub Pages
  project site) → the default relative URLs; a single-page app with nested routes (`/spot/123`) at the
  domain root → `--web-path /icons`; such an app under a sub-path → `--web-path /<base>/icons`. Relative
  URLs break on nested routes; root-absolute ones break under a sub-path. State the assumption.
- **Page already wired:** `inject.py` refuses and prints the paths in use — render to those paths
  (or run the project's own build) instead of rewiring. `--force` only on explicit request.
- **No HTML yet:** `inject.py --print --out <site-root> --name … --theme … [--web-path /icons]` writes the
  manifest into the site root (e.g. `public/`), `head-snippet.html` into the current folder (not
  deployed), and prints the snippet.
- **Dark apps:** pass `--status-bar black`; the default (`default`) gives a light status bar that looks
  wrong above a dark UI. `black-translucent` draws the page under the status bar and needs
  `env(safe-area-inset-top)` padding.
- **Build-tool layouts** (`public/` in Vite/Next): render with `--out public/icons --preview-dir
  icon-design` so previews are not deployed; web paths then start at `/icons/`.
- **Service worker present:** a cache-first worker keeps serving the old PNG at the same URL — bump
  its cache version (or the project's version script) and say so.

Read `references/ios-delivery.md` for the tags, the standalone trade-off (tell the user in one
sentence) and the two-minute on-device test. Hand off with: the preview image, one sentence on what
the icon depicts and why it fits, the file list, the assumption most likely to be wrong, and the
runner-up concept in one line.

## Output layout
```
<project>/
├── icon.svg                 ← editable master, keep it
├── icons/                   ← deployable: icon-512/192.png, apple-touch-icon.png (180), icon.svg
├── icon-design/             ← not deployed: icon-1024.png (master), preview.png, grid.png, compare.png
├── manifest.webmanifest
└── index.html               ← <head> block injected (or the project's existing wiring, untouched)
```
No project files yet? If the current folder is the user's (empty) project folder, use it directly;
create `./<app-slug>-icon/` only when the current folder is unrelated.

## Quality bar (what "done" means)
- The 29pt tile is nameable and holds its own next to the bright neighbours on both wallpapers.
- The 1024 hero meets its style's finish standard (graphic: exact geometry, no stray effects;
  illustrative: one consistent light, a real material), with no clipped edges in `grid.png`.
- Next to the category's real leaders it differs from each on at least two of style family, hue
  family and silhouette.
- The icon could not be swapped with a competitor's without someone noticing.
- validate.py shows no ✗; the only ⚠ left are ones you can defend in a sentence; the project's own
  icon tests (if any) pass.

## Reference map
| Need | Read |
|---|---|
| process, concept note, tests, light/palette rules | `references/design-process.md` |
| SVG recipes per style A–G, materials, anti-patterns | `references/styles.md` |
| gradient pairs, deriving from a brand colour, collisions | `references/palettes.md` |
| metaphors + twists by app category | `references/metaphors.md` |
| what to look for in preview.png, fixes | `references/critique.md` |
| tags, manifest, caching, service workers, standalone, device test | `references/ios-delivery.md` |
| finished examples with their concept notes | `assets/examples/README.md` |

## Scripts
| Script | Does |
|---|---|
| `scripts/render.js <svg> --out <dir> [--preview-dir <dir>] [--draft] --label <name> [--grid] [--sizes 167,152]` | SVG → PNG set + home-screen preview among bright neighbours (Playwright/Chromium); `--draft` for block-outs; warns on heavy files |
| `scripts/render.js … --neighbours <folder>` | use real icons (e.g. the category's leaders) as neighbours in preview.png and compare.png |
| `scripts/render.js --compare a.svg b.svg [c.svg d.svg] --out icon-design` | variants side by side at hero, 60pt and 29pt among bright neighbours |
| `scripts/validate.py <png> [--json]` | transparency, subject coverage, centre of mass, corner & maskable intrusion, contrast, tonal depth; scene-aware |
| `scripts/inject.py <html> --name [--theme --bg --web-path --start-url --status-bar --no-standalone --force --print --out --snippet]` | head tags + manifest; refuses to rewire an already-wired page; relative URLs by default; idempotent |
| `scripts/ribbon.py --path/--spiral … --width A:B --colors … [--range T0:T1 --cap round --side front\|back]` | variable-width, colour-graded strokes (trails, orbits, brush strokes) as seamless SVG |
| `scripts/extract_brand.py <html/css…>` | title, colours, fonts, copy, existing icon wiring |

## When the environment cannot render
No Node/Playwright: still write `icon.svg` with the full recipe, run `render.js` (it falls back to
rsvg-convert/ImageMagick if present), and tell the user exactly which command to run locally to
get the PNGs and preview. Never hand over a rounded-corner or transparent PNG as the
apple-touch-icon because the fallback produced one — fix the SVG background instead.
