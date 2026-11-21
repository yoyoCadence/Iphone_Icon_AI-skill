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
App / tone:  Bramble — plant-care reminders · warm · patient · tactile
Essence:     it grows because you came back
Idea:        a terracotta pot seen slightly from above, one sprout casting a long morning shadow
             (literal object + the moment it changes; the shadow makes "time" visible)
Style:       B Rendered Object
Palette:     tile #F6E7C8 → #E2B98A (pale, warm) · pot #E07A4F → #9C3F22 · leaf #6FCF7F → #2F8A4A
Light:       low sun from the left; long shadow to the right, rim on the leaf edge
Name:        "Bramble" (7 chars)
```
(This category is deliberately not one of `assets/examples/` — never copy an example's concept.)

## 4–6. Build, render and critique, deliver

These steps live in `SKILL.md` (steps 3–5) with the exact commands; the recipes are in `styles.md`,
the critique order in `critique.md`, the delivery details in `ios-delivery.md`. Two reminders that
matter most here: block out the silhouette flat before adding material, and stop polishing when the
29pt tile reads instantly among bright neighbours and the 1024 hero shows one consistent light.
