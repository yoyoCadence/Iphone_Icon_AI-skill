# Critique — how to look at preview.png and what to change

Open `icon-design/preview.png` (it is an image; the `Read` tool shows it). It has four areas: the
1024 hero masked the way iOS masks it, the icon among **bright, bold neighbours** on a dark wallpaper
and on a light wallpaper (they are deliberately as loud as a real home screen), and the small-size
strip (60/40/29/20pt). Finish with `icon-design/grid.png` — the only place clipped blurs, sliced
stroke tips and seams are visible. Go through the questions **in this order**,
because an icon that fails an early one cannot be rescued by passing later ones.

## 1. The 29pt test (small-size strip)
Cover the hero with your hand (mentally). At 29pt, can you name the object or letter?
- If it is a smudge: the silhouette has too many parts or too little contrast. Remove the smallest
  element; thicken strokes; raise glyph/background contrast (validate.py reports the ratio).
- If it reads but as "generic shape": the twist lives in detail that vanished. Move the twist into
  the *silhouette* (a notch, a cut, an asymmetry) rather than into surface detail.

## 2. The neighbour test (dark and light panels)
Among the placeholder apps, does the eye land on it — for the right reason?
- Vanishes on dark wallpaper: tile bottom stop too dark or glyph too dim; add the backlight glow
  or lighten the top stop.
- Vanishes on light wallpaper: tile too pale with no edge; deepen the bottom stop or add a
  subtle inner vignette.
- Lands on it because it is shouting: more than two hues or a saturated accent too large; mute
  the accent, reduce the hue span.

## 3. The ownership test (hero)
Say the app's name, then ask "could this be a competitor's icon?" If yes, name *what* is
generic — usually the glyph is a stock pictogram or the palette is the category default
(blue finance, green health). Apply one twist from `metaphors.md` *or* move the palette one step
off the default (`palettes.md`), not both at once.

## 4. Scale and placement (hero + grid.png)
- Glyph should span **50–72%** of the tile *and* carry real area: `validate.py` prints both the
  bounding-box extent and the subject coverage. A coin poking out of a book can make the extent look
  generous while the book itself covers 20% — judge coverage against the neighbours, not the box.
  First drafts are almost always 10–15% too small because the 1024 canvas feels big.
- **Optical centre**: the visual mass should sit at or *slightly above* the geometric centre
  (1–2%). Pointed/asymmetric shapes (arrows, wedges, triangles) must shift toward their mass or
  they look like they are sliding out of the tile.
- Nothing important within 10% of the edge; corners hold only background.

## 5. Light and material (hero)
- One light source, top-left. Highlights on top-left faces, rim on top-left edges, inner shadow
  and contact shadow toward bottom-right. Any element that disagrees breaks the illusion.
- Shadows tinted (darker, more saturated version of the surface), never black; highlights slightly
  warm or cool to match the palette.
- Does the glyph have **thickness**? If it looks like a sticker: add inner shadow + contact shadow.
  If it looks like plastic: lower the specular, add grain.
- Gradient clean? Muddy = passes through gray or spans too much hue. Fix with a mid-stop and ±10°
  hue rotation rather than more saturation.

## 6. Restraint (hero)
Count the ideas: one glyph, one accent, one texture. Anything beyond that must earn its place
by surviving the 29pt test; otherwise delete it. Grain/sheen must be invisible at 60pt.

## Typical first-draft diagnoses → fixes

| You see | Do |
|---|---|
| "nice but could be any app" | silhouette twist (notch/cut/asymmetry) or a specific object instead of a pictogram |
| flat sticker on a gradient | inner shadow, contact shadow, rim; 3-stop fill on the glyph |
| clip-art | replace flat fills with the Rendered Object recipe; show the object slightly from above |
| muddy gradient | mid-stop; shift top toward yellow, bottom toward blue/violet |
| glyph too small / timid | scale group about (512,512) by 1.12–1.2; a pale subject also needs a darker tile behind it |
| looks fine alone, weak next to the neighbours | bigger silhouette, one stronger value contrast, fewer mid-tones |
| straight cut edge on a glow / sliced tip (grid.png) | filter region too small or shifted by a transform — use the padded region from styles.md, on an untransformed group |
| a raised shape looks dented | inner-shadow offset points away from the light — flip its sign |
| arrow/wedge looks off-centre | translate 2–3% toward the mass |
| smears at 29pt | thicken strokes ≥ 28px, drop the smallest element, raise contrast |
| harsh / plastic | lower specular opacity to 0.3–0.45, widen blur, add grain 0.08 |
| dead on dark wallpaper | add backlight glow; lighten the top stop 8% |
| dead on light wallpaper | deepen the bottom stop 10%; add bottom vignette |
| black corners on device | background not full-bleed / has alpha — paint a 1024 rect first |
| double rounded corners | remove any rounded rect/clip from the tile; iOS masks it |

## When to stop

Stop when: the 29pt tile is instantly nameable, the neighbour panels show it holding its own
without shouting, the hero shows one consistent light and a real material, and the validator
has no `✗`. Two render rounds is typical; a third is fine; a fifth means the concept is wrong —
go back to the metaphor ladder instead of polishing.
