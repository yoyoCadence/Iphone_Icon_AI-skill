# Design process — from "an app" to "the one image that is this app"

A home-screen icon is the smallest brand a product will ever have: ~60pt, seen among 20 other
icons, glanced at for 200ms. Everything below exists to produce an image that (1) is read
instantly at that size, (2) could not be mistaken for a different app, and (3) rewards a closer
look at full size. Generic icons fail (2); busy icons fail (1); unconsidered icons fail (3) — at
1024 every edge, curve and colour must look decided, whether the icon is flat or rendered.

## 0. Collect the brief (2 minutes, not 20)

Get these five facts. If the user gave an HTML/CSS file or URL, run
`python3 scripts/extract_brand.py <files>` first — it pulls title, colours, fonts and copy.

| Fact | Why it matters | If missing |
|---|---|---|
| **Name** (as it will appear under the icon) | ≤ 11 characters show without truncation; the icon must agree with it | use the `<title>` |
| **What it does, in one sentence** | source of the metaphor | infer from the page copy |
| **Tone: three adjectives** (e.g. calm · precise · friendly) | decides style and palette | infer from the name, the page's typography and colours, the existing icon and the audience — not from a README's description of method |
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

## 2. Read the market, then choose a style on purpose

### 2a. Map the category (5 minutes)

Name the 3–5 apps a user of this category already has on their home screen and write each icon's
language in one line — *tile · mark · style*. "Spotify: black tile · green disc with three arcs ·
flat mark." If competitor icons are available (the user's folder, screenshots, or an App Store
lookup), put the PNGs in a folder and render every draft among them with
`render.js --neighbours <folder>` — judging against generic placeholders hides how close you are
to the leaders.

What the market actually looks like (27 category leaders across music, messaging, food delivery,
meditation, to-do and language learning, Nov 2026): **about four in five are flat brand marks or
letterforms** on a saturated or white tile — Spotify's arcs, Telegram's plane, Todoist's stacked
ticks, Babbel's and Busuu's B, Headspace's orange disc. A few are short wordmarks (Uber Eats,
Memrise, Calm, LINE). One is a character (Duolingo), one a skeuomorphic object (Things 3). Rendered
3D objects are the exception, not the norm: flat marks scale to 20pt, survive iOS dark and tinted
modes, and become a brand. Flat is not the failure mode — a *stock* shape is.

### 2b. Shortlist two styles from different families, block out both, let the evidence choose

| Family | Style | Fits tone words |
|---|---|---|
| graphic | **H. Brand Mark** — one ownable geometric symbol, 1–2 flat colours | confident · modern · simple · consumer |
| graphic | **F. Letterform** — a custom initial or a ≤ 5-letter wordmark with one trick | brand-first · editorial · the name is the identity |
| graphic | **E. Luminous** — glowing strokes on a dark tile | technical · night · music · gaming |
| graphic | **D. Layered Paper** — stacked flat layers with soft shadows | organised · writing · planning |
| graphic | **C. Liquid Glass** — translucent plates over colour | airy · iOS-native · wellness |
| illustrative | **A. Lit Glyph** — white glyph with light and material | trustworthy · utility |
| illustrative | **B. Rendered Object** — one object with volume, light and shadow | tactile · premium · product-like |
| illustrative | **G. Horizon Scene** — sky, light source, ≤ 3 land layers | travel · weather · outdoors |
| illustrative | **I. Character** — a face or creature with one expression | playful · kids · learning · companionship |

Pick **one style from each family** that fits the tone — unless the brief rules a family out, and
then say why in the concept note.

**Compare them at equal fidelity.** A graphic block-out is nearly a finished icon; a block-out of an
illustrative style is a flat drawing of a 3D thing with its strength — light and material — taken
away. Comparing those two is rigged toward flat (test runs: eight briefs, eight flat winners, the
illustrative candidates losing on block-out colours like red on sage at 1.5:1). So before the
comparison, give each finalist one honest pass in its own idiom: the graphic one gets exact
geometry; the illustrative one gets the scaffold's light rig, a real material and a tile colour
chosen for contrast. Then `render.js --compare a.svg b.svg --neighbours <folder>`.

**Decide in this order — three gates, then tone:**
1. **Gate: read.** Each candidate must be nameable at 29pt among the neighbours, and at 60pt a
   stranger must guess the right *kind* of app: a game has to look like a game, a kids' app like a
   kids' app. One that fails is out. Between two that pass, "the simpler one reads faster" is not
   a reason — every flat mark reads faster than every lit object.
2. **Gate: mark, not pictogram (graphic candidates only).** A flat candidate must be *one
   silhouette*: a letter, a symbol, or parts fused into one outline, with any detail cut into it
   as negative space. Count the separately drawn parts the idea needs to read. Three or more — a car
   body plus tyres, rollers and a wall; an iceberg tip plus three facets; a ticket plus a stub plus
   a bowl — and the flat version is a toolbar pictogram, not a brand mark: it is out, and the idea
   belongs to the illustrative candidate (or goes back to be reduced to one silhouette). Exception:
   the brand's own visual language is flat illustration (a comic ink-line UI) and the candidate is
   drawn in it.
3. **Gate: distance.** Each candidate must differ from *every* leader on at least two of style
   family, hue family and silhouette; one that doesn't is out (or goes back for a new hue or
   silhouette). **Hue family is what dominates the whole icon by area — tile and mark together —
   not the tile alone:** a blue tile does not share a hue with Mario Kart Tour, whose icon reads
   red. Passing is enough — more distance is not a reason to win. Ranking on style family rigs the
   choice: in a category of flat marks every illustrative candidate "wins" automatically (a test run
   picked a retro cassette for a brief that asked for rebellious and modern).
4. **Tone decides between candidates that passed every gate.** Warm · homey · cozy · tactile ·
   crafted · nostalgic · kids · playful-game · premium-object lean illustrative; confident · modern ·
   minimal · precise · utility · fast · rebellious lean graphic. Name the words that decided it.
   - **Read tone from what the user sees, not from how the code works:** the name's promise
     (*Forge* is heat, *GoGoGo* is energy), the UI and its theme, the existing icon, the audience.
     A README's account of method — rigorous, auditable, reproducible, sober — describes the
     engineering; every serious tool says it, so it is not a tone. If a README is all you have, say
     so in the concept note and treat the tone as neutral.
   - **Brand equity outranks tone:** if one candidate kept the brand's colour or motif and the
     other had to give it up to pass the distance gate, keep the one that kept the brand.
   - Only if the tone is genuinely neutral, prefer the candidate whose style family is rarer among
     the leaders.

Never break a tie toward "more volume", "fewer pixels" or "more different" — each habit turned a
set of test icons into one formula (eight lit objects in a row; then eight flat marks; then a
cassette chosen over the brief's own tone). Under equal fidelity, the warm home-cooking brief chose a
rendered pot and the minimal rain-alert brief a flat mark, each decided by tone. Then ten real
projects under the two-gate rule chose flat eight times in nine: the ≠ sign, the folded M and the
allocation ring were right, but an anvil, a top-down race car, a lunch ticket and an iceberg came out
as multi-part flat pictograms whose rendered runners-up were better, two of them decided by "sober"
and "rigorous" lifted from a README. Gates 1–2 and the tone sources above are the fix.

**Differentiate on at least two axes** from each leader: style family, hue family, silhouette.
A flat green disc for a music app differs from Spotify on zero axes that matter; a flat mark on a
*white* tile with a different silhouette differs on two.

**Finish follows the style.** Graphic styles get crisp geometry, exact curves and at most one
subtle gradient — no inner shadows, rim lights or grain. Illustrative styles get the full material
treatment from `styles.md`. Material is not a quality signal: an ownable flat silhouette beats a
beautifully lit generic object every time.

## 3. Set the palette and the light before drawing

- Pick a gradient pair from `palettes.md` or derive one from the brand colour: top stop = brand
  colour lightened 10–15% and rotated up to 15° toward yellow; bottom stop = darkened 20–30% and
  rotated up to 15° toward blue/violet. Hue shift is what keeps gradients from looking muddy.
- Decide the glyph tone from background luminance: near-white glyph on mid/dark tiles, near-black
  (never pure #000) glyph on pale tiles. Pale tiles with dark glyphs are rarer on home screens and
  therefore distinctive — consider them for warm, friendly brands.
- **White or pale tiles are legitimate** for graphic styles (DoorDash, Headspace, Telegram,
  TickTick all use them): the coloured mark carries the icon on any wallpaper. Make the mark large
  and saturated, and keep the tile very slightly tinted rather than `#FFFFFF`.
- **Illustrative styles only — light comes from top-left, ~30° above the surface.** Every
  highlight, rim, inner shadow and contact shadow in the icon must agree with that single
  statement. Graphic styles have no light source; their depth, if any, comes from overlap and
  value steps.
- Shadows are *tinted* (a darker, more saturated version of the surface they fall on), never pure
  black, and highlights are *warm* white on warm palettes, cool white on cool palettes.

Write the decisions down as a concept note before touching SVG. It takes a minute and prevents the
drift where every icon slowly becomes "gradient + centred lit object" again:

```
App / tone:  Bramble — plant-care reminders · warm · patient · tactile
Market:      Planta (green tile, white leaf mark, flat) · Greg (white tile, green sprout, flat) ·
             PictureThis (photo-like leaf) → the category is green, flat and leafy
Essence:     it grows because you came back
Shortlist:   graphic  — H Brand Mark: a terracotta pot silhouette whose rim is a check-mark, flat, cream tile
             illustr. — B Rendered Object: the pot seen from above, one sprout casting a long morning shadow
Chosen:      H — reads at 29pt, and terracotta-on-cream differs from every leader in hue *and* style;
             B read well too but sat in the same "lit object" register as PictureThis
Palette:     tile #FBF3E8 → #F3E6D2 · pot #E07A4F · rim/check #2F8A4A
Light:       none (graphic style) — depth from one overlapping value step on the rim
Name:        "Bramble" (7 chars)
```
(This category is deliberately not one of `assets/examples/` — never copy an example's concept.)

## 4–6. Build, render and critique, deliver

These steps live in `SKILL.md` (steps 3–5) with the exact commands; the recipes are in `styles.md`,
the critique order in `critique.md`, the delivery details in `ios-delivery.md`. Two reminders that
matter most here: block out the silhouette flat before adding material, and stop polishing when the
29pt tile reads instantly among bright neighbours and the 1024 hero shows one consistent light.
