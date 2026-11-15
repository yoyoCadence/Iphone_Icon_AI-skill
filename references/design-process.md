# Design process — from "an app" to "the one image that is this app"

A home-screen icon is the smallest brand a product will ever have: ~60pt, seen among 20 other
icons, glanced at for 200ms. Everything below exists to produce an image that (1) is read
instantly at that size, (2) could not be mistaken for a different app, and (3) rewards a closer
look at full size. Generic icons fail (2); busy icons fail (1); flat icons fail (3).

## 0. Collect the brief (2 minutes, not 20)

Get these five facts. If the user gave an HTML/CSS file or URL, run
`python3 scripts/extract_brand.py <files>` first — it pulls title, colours, fonts and copy.

| Fact | Why it matters | If missing |
|---|---|---|
| **Name** (as it will appear under the icon) | ≤ 11 characters show without truncation; the icon must agree with it | use the `<title>` |
| **What it does, in one sentence** | source of the metaphor | infer from the page copy |
| **Tone: three adjectives** (e.g. calm · precise · friendly) | decides style and palette | infer from typography and colours of the page |
| **Existing colours / logo** | brand continuity beats novelty | derive from `theme-color` or the dominant chromatic colour |
| **Audience & context** (kids? professionals? night use?) | legibility and palette temperature | assume general public |

Do not block on missing facts. State your assumptions in one line and proceed; the user
corrects assumptions far faster than they answer questionnaires.

## 1. Find the idea (the step that separates a logo from a tile)

Write the app's **essence in five words** (what feeling or job, not the feature list).
Then list candidates on the **metaphor ladder**, at least one per rung:

1. **Literal object** — the thing the app is about (coin, wave, leaf, terminal prompt).
2. **Attribute / action** — what the object *does* (rising, curling, growing, blinking).
3. **Feeling / result** — what the user gets (calm, momentum, clarity, warmth).
4. **Letterform** — the initial, only if the brand already lives in its name.

The best icons are usually **rung 1 with a rung-2 twist** ("a coin, *rising* as a stack of three
that forms an arrow") or **rung 1 rendered so specifically it becomes rung 3** ("a legal pad's
torn yellow edge" rather than "a notepad"). Pure rung 1 is clip-art; pure rung 3 is abstract mush.

Score the finalists against three questions:
- **29pt test** — would the silhouette alone still say what it is at 29pt (settings list size)?
- **Ownership test** — "could this be any app in the category?" If yes, it is not done.
- **Collision test** — does it reuse a famous combo (green bubble, blue bird, red play triangle,
  rainbow camera, white *f* on blue, orange RSS arcs, yellow ghost)? If yes, change colour *and* form.

Keep **one** idea. Icons with two ideas lose both at 60pt. See `metaphors.md` for category
starting points with their twists, and for the clichés to avoid.

## 2. Choose a style direction

Pick exactly one from `styles.md`. Match it to the tone, not to taste:

| Tone words | Style |
|---|---|
| trustworthy · clear · everyday utility | **A. Lit Glyph** (gradient tile, white glyph with real material) |
| premium · tactile · playful · product-like | **B. Rendered Object** (one object with volume, light and shadow) |
| modern · airy · iOS-native · wellness | **C. Liquid Glass** (translucent plate over blurred colour) |
| organised · paper · writing · planning | **D. Layered Paper** (stacked flat layers with soft shadows) |
| technical · night · music · gaming | **E. Luminous** (dark tile, glowing strokes) |
| brand-first · name is the identity | **F. Monogram** (one letter with a formal trick) |
| travel · weather · outdoors · mood | **G. Horizon Scene** (sky, light source, ≤3 land layers) |

If two styles fit, choose the one that gives the glyph **more volume** — flatness is the most
common reason an icon looks machine-made.

## 3. Set the palette and the light before drawing

- Pick a gradient pair from `palettes.md` or derive one from the brand colour: top stop = brand
  colour lightened 10–15% and rotated up to 15° toward yellow; bottom stop = darkened 20–30% and
  rotated up to 15° toward blue/violet. Hue shift is what keeps gradients from looking muddy.
- Decide the glyph tone from background luminance: near-white glyph on mid/dark tiles, near-black
  (never pure #000) glyph on pale tiles. Pale tiles with dark glyphs are rarer on home screens and
  therefore distinctive — consider them for warm, friendly brands.
- **Light comes from top-left, ~30° above the surface.** Every highlight, rim, inner shadow and
  contact shadow in the icon must agree with that single statement.
- Shadows are *tinted* (a darker, more saturated version of the surface they fall on), never pure
  black, and highlights are *warm* white on warm palettes, cool white on cool palettes.

Write the decisions down as a 6-line concept note before touching SVG. It takes thirty seconds
and prevents the drift where the icon slowly becomes "gradient + centred pictogram" again:

```
App: Tidewatch — surf & tide forecasts            Tone: calm · precise · outdoors
Essence: know the ocean before you go
Idea: a single wave curl at the moment of breaking, backlit by a low sun (literal + action)
Style: G Horizon Scene with a rendered wave        Palette: dusk sky #FFB36B→#3B2A6B, sea #0E6E9E→#063B5E, foam #FFF7EC
Light: top-left sun behind the curl, rim on the lip
Name under icon: "Tidewatch" (9 chars)
```

## 4. Build the SVG

Start from `assets/scaffold.svg` (1024 viewBox, lighting rig pre-wired) and follow the recipe
for the chosen style in `styles.md`. Non-negotiables that come from how iOS treats the file:

- Full-bleed opaque square. No rounded corners, no transparent margin, no drop shadow around the
  tile — iOS masks and shades the tile itself; anything you add gets doubled or cropped.
- Main glyph within the centre ~62% (x,y ≈ 195…830 at 1024); nothing meaningful within 10% of the
  edge. Corners carry only background.
- Minimum stroke ≈ 28px at 1024 (≈ 5px at 180); minimum gap between shapes ≈ 24px.
- Glyph drawn as paths. Text only for a monogram, with a font stack
  (`-apple-system, "SF Pro Display", Inter, "Helvetica Neue", Arial, sans-serif`) and weight ≥ 700.
- Filters need a generous region (`x="-30%" y="-30%" width="160%" height="160%"`) or blurs clip
  to a hard rectangle.

## 5. Render, look, critique, revise (at least once)

```bash
node scripts/render.js icon.svg --out icons --label "Name" --grid
python3 scripts/validate.py icons/icon-1024.png
```

Then open `icons/preview.png` with the image viewer you have (the `Read` tool renders PNGs) and go
through `critique.md`. First drafts are reliably off in the same places: glyph 10–15% too small,
light slightly inconsistent, gradient a touch muddy, visual centre low. Fix the top two issues,
re-render, look again. Two rounds is normal; stop when the 60pt tile reads instantly *and* the
1024 hero still looks designed rather than assembled.

## 6. Deliver

`python3 scripts/inject.py index.html --name "Name" --theme "#hex"` wires the tags and writes the
manifest (`ios-delivery.md` explains every tag and the on-device test). Show the user the preview,
state what the icon depicts and why, and name the one assumption they are most likely to want to
change (usually tone or colour). Offer the runner-up concept in one sentence — it costs nothing and
often converts.
