---
name: iphone-icon
description: Design and ship a beautiful, app-specific iPhone home-screen icon (apple-touch-icon) and PWA icon set for a web page, then wire it into the HTML and manifest. Use this whenever a user wants a mobile web page to be saved to / added to the home screen, mentions apple-touch-icon, "Add to Home Screen", PWA or manifest icons, an app icon or logo for a website or web app, a favicon for a phone, or writes 加到主畫面 / 主畫面圖示 / 網頁 icon / app icon / 圖示 — even if they only ask to "make the page installable" or "make it look like an app". Produces an SVG master, PNGs at 1024/512/192/180, a home-screen preview sheet, and the head tags + manifest. Designs the icon from the app's purpose with real lighting and material, not a centred geometric placeholder.
compatibility: Node.js ≥ 18 with Playwright + Chromium for rendering (`npm i -D playwright && npx playwright install chromium`; falls back to rsvg-convert / ImageMagick with reduced fidelity). Python 3 with Pillow for validate.py. Reads PNGs with the Read tool to critique the result.
---

# iPhone home-screen icon

You are designing the smallest piece of brand a product will ever have: a ~60pt tile that must be
read in 200 ms among twenty neighbours, must not be confusable with any other app, and must still
look designed at 1024 px. Treat it as a design job with an engineering delivery at the end —
not as "draw a shape on a gradient and export".

Reply in the user's language. Keep the conversation short and the work visible: concept note →
rendered preview → one revision → delivery.

## Workflow

### 1. Brief (≤ 2 minutes)
Collect: **name** (as shown under the icon, ≤ 11 chars), **what it does** in one sentence,
**tone** (three adjectives), **existing colours/logo**, **audience**. If the user gave an HTML/CSS
file or folder, run `python3 scripts/extract_brand.py <files>` to pull title, colours, fonts and
copy. Fill gaps with stated assumptions instead of questions — one line: "Assuming: calm,
outdoorsy, no brand colour yet — say so if wrong."

### 2. Concept (write it down before drawing)
Read `references/design-process.md` §1–3 the first time you use this skill in a session. Then
produce a six-line concept note in your reply:

```
App / tone · Essence (5 words) · Idea (metaphor + its twist) · Style (A–G) · Palette (top→bottom, glyph, accent) · Light
```

The idea must pass three tests: readable at **29pt** from silhouette alone; **ownable** ("could
this be any app in the category?" must be *no*); **no collision** with a famous icon combo.
Use `references/metaphors.md` for category twists and `references/palettes.md` for gradient pairs.
If tone is genuinely ambiguous (e.g. "finance" with no other cue), make **two** concepts and
render both; otherwise make one and keep a runner-up sentence for the hand-off.

### 3. Build the SVG
Copy `assets/scaffold.svg` (1024 viewBox, lighting rig pre-wired) to the project as `icon.svg`
and follow the recipe for the chosen style in `references/styles.md`. Rules that come from how
iOS treats the file — these are not stylistic preferences:

- Full-bleed **opaque square**; no rounded corners, no outer shadow, no transparent margin
  (iOS masks the squircle and composites over black).
- Main glyph inside the centre ~62 % (x,y ≈ 195…830); corners carry only background.
- Strokes ≥ 28 px, gaps ≥ 24 px at 1024; text only for a monogram (≤ 2 letters, weight ≥ 700).
- One light source (top-left unless the scene defines its own sun); tinted shadows, never black.
- Filters get a generous region (`x="-30%" y="-30%" width="160%" height="160%"`).
- Glyph as paths with **material**: fill gradient + inner shadow + contact shadow + rim at minimum.
  A flat white pictogram is the single biggest tell of a generated icon.

### 4. Render → look → critique → revise
```bash
node  scripts/render.js  icon.svg --out icons --label "Name" --grid
python3 scripts/validate.py icons/icon-1024.png
```
Then **Read `icons/preview.png`** (it renders as an image) and go through
`references/critique.md` in order: 29pt test → neighbour test → ownership → scale/centre →
light/material → restraint. Fix the top two findings, re-render, look again. First drafts are
reliably 10–15 % too small, slightly low, and a little muddy — expect one revision; two is fine;
five means the concept is wrong, go back to step 2. Treat `validate.py` output as mechanical
facts (transparency, extent, contrast, corner intrusion), and your eyes as the judge of beauty.

### 5. Deliver
```bash
python3 scripts/inject.py index.html --name "Name" --theme "#bottom-stop" [--no-standalone]
```
This inserts a managed block (`apple-touch-icon`, manifest link, theme-color, web-app title,
standalone metas), writes `manifest.webmanifest`, cache-busts URLs, and removes competing tags.
If there is no HTML yet, `--print` outputs the block + manifest to paste. Read
`references/ios-delivery.md` for what each tag does, the standalone-mode trade-off (say it to
the user in one sentence), and the two-minute on-device test.

Hand off with: the preview image, one sentence on what the icon depicts and why it fits, the
file list, the assumption most likely to be wrong, and the runner-up concept in one line.

## Output layout
```
<project>/
├── icon.svg                 ← editable master, keep it
├── icons/
│   ├── icon-1024.png  icon-512.png  icon-192.png  apple-touch-icon.png (180)
│   ├── preview.png  grid.png  icon.svg
├── manifest.webmanifest
└── index.html               ← <head> block injected
```
No project? Create `./<app-slug>-icon/` with the same layout.

## Quality bar (what "done" means)
- The 29pt tile is nameable; the 1024 hero shows one consistent light and a real material.
- Two hues in the tile, one glyph tone, at most one accent; gradients hue-shifted, never muddy.
- The icon could not be swapped with a competitor's without someone noticing.
- validate.py shows no ✗; the only ⚠ left are ones you can defend in a sentence.

## Reference map
| Need | Read |
|---|---|
| process, concept note, tests, light/palette rules | `references/design-process.md` |
| SVG recipes per style A–G, materials, anti-patterns | `references/styles.md` |
| gradient pairs, deriving from a brand colour, collisions | `references/palettes.md` |
| metaphors + twists by app category | `references/metaphors.md` |
| what to look for in preview.png, fixes | `references/critique.md` |
| tags, manifest, caching, standalone, device test | `references/ios-delivery.md` |
| finished examples with their concept notes | `assets/examples/README.md` |

## Scripts
| Script | Does |
|---|---|
| `scripts/render.js <svg> --out <dir> --label <name> [--grid] [--sizes 167,152]` | SVG → PNG set + preview sheet (Playwright/Chromium) |
| `scripts/validate.py <png> [--json]` | transparency, glyph extent/centre, corner & maskable intrusion, contrast, tonal depth |
| `scripts/inject.py <html> --name --theme [--bg --start-url --status-bar --no-standalone --print]` | head tags + manifest, idempotent, cache-busted |
| `scripts/extract_brand.py <html/css…>` | title, colours, fonts, copy, existing icon wiring |

## When the environment cannot render
No Node/Playwright: still write `icon.svg` with the full recipe, run `render.js` (it falls back to
rsvg-convert/ImageMagick if present), and tell the user exactly which command to run locally to
get the PNGs and preview. Never hand over a rounded-corner or transparent PNG as the
apple-touch-icon because the fallback produced one — fix the SVG background instead.
