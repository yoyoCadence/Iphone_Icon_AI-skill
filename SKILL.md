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

### 2. Concept (write it down before drawing)
Read `references/design-process.md` §1–3 the first time you use this skill in a session, then write
the concept note in the format shown there (App/tone · Essence · Idea · Style · Palette · Light).
The idea must pass three tests: readable at **29pt** from silhouette alone; **ownable** ("could
this be any app in the category?" must be *no*); **no collision** with a famous icon combo.
Use `references/metaphors.md` for category twists and `references/palettes.md` for colours.
Make **two** concepts only when the brief gives nothing beyond a category; otherwise make one and
keep a runner-up sentence for the hand-off. The worked examples in `assets/examples/` calibrate
quality — if the brief is in an example's category, that example is now the cliché to avoid.

### 3. Build the SVG — bold first, beautiful second
1. **Block out** the silhouette in flat colours, render it (step 4), and check the 29pt tile among
   the bright neighbours in `preview.png`. Solid subjects usually cover ~28–45 % of the tile
   (`validate.py` reports coverage); line/glow glyphs can be thinner if contrast is ≥ 4:1.
   Refinement never rescues a subject that is too small or too pale — fix that here.
2. **Then add material** with the recipe for the chosen style in `references/styles.md`.
   Styles A/B/E/F start from `assets/scaffold.svg` (lighting rig pre-wired); C/D/G start from their
   recipe and reuse only the scaffold's filters. For a stroke whose width or colour must change along
   its length (trail, orbit, brush, swoosh), generate it with `scripts/ribbon.py`.

Rules that come from how iOS and SVG behave — not stylistic preferences:
- Full-bleed **opaque square**; no rounded corners, no outer shadow, no transparent margin
  (iOS masks the squircle and composites over black).
- Main subject inside the centre ~62 % (x,y ≈ 195…830); corners carry only background.
- Glyph strokes ≥ 28 px, gaps ≥ 24 px at 1024; text only for a monogram (≤ 2 letters, weight ≥ 700).
- One light source (top-left unless the scene has its own sun); tinted shadows, never black.
- Filter regions cover the canvas: `filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024"`.
  Percentage regions clip stroked and thin shapes into hard edges.
- Colour discipline: two hues in the tile, one hero object/glyph, at most one secondary accent.

### 4. Render → look → critique → revise
```bash
node  scripts/render.js  icon.svg --out icons --preview-dir icon-design --label "Name" --grid
python3 scripts/validate.py icons/icon-1024.png
```
**Read `icon-design/preview.png`** (renders as an image) and go through `references/critique.md`
in order: 29pt test → neighbour test → ownership → scale/centre → light/material → restraint.
Then open `icon-design/grid.png` (1024) for what the small sheet hides: clipped blurs, sliced tips,
banding, stray seams. Fix the top two findings, re-render, look again. Expect one or two revisions;
a fifth means the concept is wrong — go back to step 2. `validate.py` gives mechanical facts
(transparency, coverage, centre of mass, contrast, corner intrusion); your eyes judge the rest.

### 5. Deliver
- **Page without icon wiring:** `python3 scripts/inject.py index.html --name "Name" --bg "#tile-bottom"`.
  It keeps the page's own `theme-color`, status-bar and web-app choices unless you pass the matching
  option (`--theme` = the brand colour for a page that has none), uses URLs relative to the page
  (sub-path hosting such as GitHub Pages works), writes or updates the manifest, and cache-busts.
- **Page already wired:** `inject.py` refuses and prints the paths in use — render to those paths
  (or run the project's own build) instead of rewiring. `--force` only on explicit request.
- **No HTML yet:** `inject.py --print --out <dir> --name … --theme … [--web-path /icons]` writes
  `head-snippet.html` and the manifest there and prints the snippet.
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
├── icons/                   ← deployable: icon-1024/512/192.png, apple-touch-icon.png (180), icon.svg
├── icon-design/             ← not deployed: preview.png, grid.png
├── manifest.webmanifest
└── index.html               ← <head> block injected (or the project's existing wiring, untouched)
```
No project? Create `./<app-slug>-icon/` with the same layout.

## Quality bar (what "done" means)
- The 29pt tile is nameable and holds its own next to the bright neighbours on both wallpapers.
- The 1024 hero shows one consistent light and a real material, with no clipped edges in `grid.png`.
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
| `scripts/render.js <svg> --out <dir> [--preview-dir <dir>] --label <name> [--grid] [--sizes 167,152]` | SVG → PNG set + home-screen preview among bright neighbours (Playwright/Chromium); warns on heavy files |
| `scripts/validate.py <png> [--json]` | transparency, subject coverage, centre of mass, corner & maskable intrusion, contrast, tonal depth; scene-aware |
| `scripts/inject.py <html> --name [--theme --bg --start-url --status-bar --no-standalone --force --print --out]` | head tags + manifest; refuses to rewire an already-wired page; relative URLs; idempotent |
| `scripts/ribbon.py --path/--spiral … --width A:B --colors …` | variable-width, colour-graded strokes (trails, orbits, brush strokes) as seamless SVG |
| `scripts/extract_brand.py <html/css…>` | title, colours, fonts, copy, existing icon wiring |

## When the environment cannot render
No Node/Playwright: still write `icon.svg` with the full recipe, run `render.js` (it falls back to
rsvg-convert/ImageMagick if present), and tell the user exactly which command to run locally to
get the PNGs and preview. Never hand over a rounded-corner or transparent PNG as the
apple-touch-icon because the fallback produced one — fix the SVG background instead.
