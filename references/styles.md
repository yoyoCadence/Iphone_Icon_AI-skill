# Style recipes — SVG that reads as designed, not generated

Every recipe assumes `viewBox="0 0 1024 1024"`, light from the **top-left**, and the layer stack
of `assets/scaffold.svg` (bg → glow → vignette → glyph → sheen → grain). Snippets are complete
enough to paste; rename ids you change. Numbers are starting points calibrated for 1024 — keep
their ratios when you scale.

**Two rules that every snippet below already follows:**
- *Filter regions cover the whole canvas* (`filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024"`).
  Percentage regions are measured on the shape's bounding box *without its stroke*, so they slice the
  tips off stroked glyphs and box thin shapes' blurs into visible rectangles — and only at 1024, where
  `preview.png` is too small to show it. Check `grid.png` / `icon-1024.png` for straight cut edges.
- *Bold before beautiful.* Block the silhouette out in flat colours first and check it at 29pt among
  bright neighbours (`preview.png`); add material only once the flat version already wins. Refinement
  never rescues a subject that is too small or too pale.

Contents
- Shared building blocks (gradients that don't go muddy, shadow, inner shadow, rim, specular, glow, grain)
- A. Lit Glyph · B. Rendered Object · C. Liquid Glass · D. Layered Paper · E. Luminous · F. Monogram · G. Horizon Scene
- Materials cheat-sheet · Anti-patterns

---

## Shared building blocks

**Background gradient that stays clean.** Shift hue, not only lightness. Two stops, top lighter.
Add a third mid-stop only to push saturation (gradients desaturate in the middle otherwise).

```xml
<linearGradient id="bg" x1="0" y1="0" x2="0.15" y2="1">
  <stop offset="0"   stop-color="#5E8BFF"/>   <!-- brand +12% L, +10° toward cyan/yellow -->
  <stop offset="0.5" stop-color="#3F5BE8"/>   <!-- brand, saturation nudged up -->
  <stop offset="1"   stop-color="#2436C9"/>   <!-- brand −25% L, −10° toward violet -->
</linearGradient>
```

**Backlight / glow behind the glyph.** Sells depth for one element.
```xml
<radialGradient id="glow" cx="0.5" cy="0.3" r="0.55">
  <stop offset="0" stop-color="#fff" stop-opacity="0.35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</radialGradient>
<rect width="1024" height="1024" fill="url(#glow)"/>
```

**Contact shadow (tinted, soft, downward).**
```xml
<filter id="shadow" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024">
  <feDropShadow dx="0" dy="22" stdDeviation="22" flood-color="#0A1B6E" flood-opacity="0.45"/>
</filter>
```

**Inner shadow (gives a flat shape thickness; apply to the shape itself).**
```xml
<filter id="inner" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024">
  <feOffset dx="-4" dy="-10"/><feGaussianBlur stdDeviation="12" result="ob"/>
  <feComposite operator="out" in="SourceGraphic" in2="ob" result="inv"/>
  <feFlood flood-color="#1A2A8C" flood-opacity="0.55" result="col"/>
  <feComposite operator="in" in="col" in2="inv" result="sh"/>
  <feComposite operator="over" in="sh" in2="SourceGraphic"/>
</filter>
```
The offset points *toward* the light (here up-left), so the shadow lands on the bottom-right inner
edge — a raised shape lit from the top-left. Point it *away* from the light (`dx="4" dy="10"`) for an
inset / engraved / debossed look (a slot, a stamped label). Getting this backwards turns a dome into
a dent; if a shape looks sunken, flip the sign.

**Rim light** — the same path stroked with a gradient that fades out toward bottom-right:
```xml
<linearGradient id="rim" x1="0" y1="0" x2="0.4" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0.9"/><stop offset="0.5" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<path d="…same d…" fill="none" stroke="url(#rim)" stroke-width="6" stroke-linejoin="round"/>
```

**Specular highlight** (glossy materials only) — a blurred white ellipse near the top-left of the form:
```xml
<filter id="soft" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024"><feGaussianBlur stdDeviation="14"/></filter>
<ellipse cx="430" cy="380" rx="120" ry="60" fill="#fff" opacity="0.55" filter="url(#soft)" transform="rotate(-25 430 380)"/>
```

**Outer glow** (luminous things) — duplicate the shape beneath itself, blurred, at lower opacity.
Two blurs (tight + wide) look far better than one.
```xml
<filter id="glowTight" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="glowWide" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024"><feGaussianBlur stdDeviation="48"/></filter>
<use href="#stroke" filter="url(#glowWide)"  opacity="0.55"/>
<use href="#stroke" filter="url(#glowTight)" opacity="0.8"/>
<use href="#stroke"/>
```

**Grain** — removes plastic flatness; invisible at 60pt, felt at 1024. Costs bytes: noise does not
compress, so it roughly doubles to quadruples PNG size (icon-512 ≈ 250 KB instead of ≈ 100 KB). Keep
alpha ≤ 0.08, and skip it for scenes that already have texture.
```xml
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/>
  <feColorMatrix type="saturate" values="0"/>
  <feComponentTransfer><feFuncA type="table" tableValues="0 0.10"/></feComponentTransfer>
</filter>
<rect width="1024" height="1024" filter="url(#grain)" style="mix-blend-mode:overlay"/>
```

---

## A. Lit Glyph — the refined classic

*When:* utilities, communication, anything that must feel trustworthy at a glance.
*Why it works:* iOS's own icons are this; it reads as native. *Why it usually fails:* a flat white
pictogram with none of the material below — that is what "generated" looks like.

Recipe (= `scaffold.svg`):
1. `bg` gradient + `glow` + bottom vignette (`#000` 0→0.22 from 55% down).
2. Glyph as a single compound path, filled with a white→tinted-white vertical gradient
   (`#FFFFFF → #D9E3FF` for a blue tile; tint toward the background hue).
3. Apply `inner` to the glyph, wrap it in a group with `shadow`, stroke the rim.
4. One **cut** or **counter-shape** inside the glyph in the background colour (a notch, a slot,
   a negative-space arrow) — this is what makes it *this* app's glyph.
5. Optional: a second, small element in the accent colour (a dot, a spark) — never more than one.

Scale: glyph bounding box 55–68% of the tile. Round glyphs slightly larger (they look smaller).

## B. Rendered Object — one thing with volume

*When:* the product has a hero object (coin, lens, pin, bottle, cassette, dice, pill, egg, planet).
*Why it works:* a lit three-dimensional thing is instantly "real" and almost never generic.

Build the object from three stacked copies of its silhouette:
```xml
<!-- 1. body: 3-stop gradient along the light direction -->
<linearGradient id="body" x1="0.1" y1="0" x2="0.9" y2="1">
  <stop offset="0" stop-color="#FFE39A"/><stop offset="0.55" stop-color="#F2B233"/><stop offset="1" stop-color="#B86A0A"/>
</linearGradient>
<!-- 2. ambient occlusion: dark ellipse under the object, heavily blurred -->
<filter id="ao" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024"><feGaussianBlur stdDeviation="30"/></filter>
<ellipse cx="512" cy="760" rx="260" ry="46" fill="#3A1C00" opacity="0.5" filter="url(#ao)"/>
<!-- 3. body + inner shadow for thickness -->
<circle cx="512" cy="500" r="270" fill="url(#body)" filter="url(#inner)"/>
<!-- 4. form shading: a darker crescent on the bottom-right, inside the silhouette -->
<clipPath id="cp"><circle cx="512" cy="500" r="270"/></clipPath>
<circle cx="560" cy="560" r="300" fill="#7A4200" opacity="0.35" clip-path="url(#cp)" filter="url(#soft)"/>
<!-- 5. rim + specular -->
<circle cx="512" cy="500" r="267" fill="none" stroke="url(#rim)" stroke-width="8"/>
<ellipse cx="420" cy="370" rx="110" ry="52" fill="#fff" opacity="0.6" filter="url(#soft)" transform="rotate(-30 420 370)"/>
```
Then **emboss the detail** (the arrow on the coin, the aperture on the lens) with two offset
copies: a lighter one shifted `(-3,-3)`, a darker one shifted `(+3,+3)`, the real one on top.

Perspective: show the object slightly from above (ellipses for tops of cylinders, `ry ≈ 0.35·rx`).
A tilt of 8–15° makes a flat object look placed rather than pasted.

## C. Liquid Glass — translucent plate over colour

*When:* wellness, media, modern consumer apps; anything that should feel native to current iOS.
*Why it works:* layered translucency and bright edges mimic physical glass; the colour under it
makes it unique.

```xml
<rect width="1024" height="1024" fill="#0F1430"/>                        <!-- deep base -->
<filter id="blob" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024"><feGaussianBlur stdDeviation="110"/></filter>
<circle cx="300" cy="300" r="260" fill="#FF6AC1" filter="url(#blob)" opacity="0.9"/>   <!-- 2–3 blobs -->
<circle cx="720" cy="420" r="280" fill="#5B7BFF" filter="url(#blob)" opacity="0.9"/>
<circle cx="520" cy="820" r="240" fill="#38E1C9" filter="url(#blob)" opacity="0.8"/>
<!-- the plate: translucent fill, gradient stroke, top-edge highlight, soft shadow -->
<linearGradient id="plate" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0.34"/><stop offset="1" stop-color="#fff" stop-opacity="0.12"/>
</linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0.95"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.15"/><stop offset="1" stop-color="#fff" stop-opacity="0.6"/>
</linearGradient>
<g filter="url(#shadow)">
  <path id="glyph" d="…" fill="url(#plate)" stroke="url(#edge)" stroke-width="5"/>
</g>
<!-- refraction: the same glyph, filled with a brighter blob colour, shifted 10px, low opacity -->
<use href="#glyph" transform="translate(10 12)" fill="#C8D4FF" opacity="0.18" stroke="none"/>
```
The glyph silhouette must be **bold and simple** (glass loses thin detail). A second, smaller glass
shape overlapping the first gives the signature "stacked panes" look — stop at two.

## D. Layered Paper — stacked flat layers with soft shadows

*When:* notes, planners, documents, education, finance that wants to feel organised.
*Why it works:* layers imply content and order; shadows between layers provide depth without gloss.

```xml
<filter id="paper" filterUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024">
  <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#3B2B00" flood-opacity="0.25"/>
</filter>
<g transform="rotate(-6 512 512)">
  <rect x="262" y="262" width="500" height="560" rx="44" fill="#F4E9D2" filter="url(#paper)"/>
</g>
<g transform="rotate(3 512 512)">
  <rect x="262" y="262" width="500" height="560" rx="44" fill="#FFF8EA" filter="url(#paper)"/>
</g>
<rect x="262" y="262" width="500" height="560" rx="44" fill="url(#sheet)" filter="url(#paper)"/>
<!-- the content mark: ONE bold element on the top sheet (a fold, a tab, three bars, a seal) -->
```
Each layer: slightly different lightness *and* hue, and a vertical gradient of 4–6% lightness.
Rotate layers by small, unequal angles (−6°, +3°, 0°). The top layer carries the one mark.

## E. Luminous — glowing strokes on a dark tile

*When:* developer tools, music, night-time, gaming, anything "on".
*Why it works:* light on dark is high-contrast and rare among productivity icons.

Rules: base is a **dark hue** (`#0B1020`, `#0E1A14`, `#1A0B1E`), never `#000`; main stroke 48–64px
wide with round caps; glow in the *same* hue, white-hot core stroke at 35–40% of main width; a
faint radial haze of the glow colour behind everything so the tile is not flat black.

```xml
<path id="stroke" d="M330 380 L520 512 L330 644" fill="none" stroke="#5EF1FF" stroke-width="56" stroke-linecap="round" stroke-linejoin="round"/>
<use href="#stroke" filter="url(#glowWide)" opacity="0.6"/>
<use href="#stroke" filter="url(#glowTight)" opacity="0.9"/>
<use href="#stroke"/>
<path d="M330 380 L520 512 L330 644" fill="none" stroke="#FFFFFF" stroke-width="20" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>
```
A second colour (a warm accent on a cool glow, e.g. a single orange dot) adds life; a third kills it.

## F. Monogram — one letter with a trick

*When:* the name *is* the brand and no object survives the 29pt test.
*Why it fails by default:* a letter centred on a gradient is a placeholder. The trick is mandatory.

Tricks (pick one): the counter of the letter replaced by a symbol; the letter cut by a diagonal
band in the background colour; two overlapping translucent copies in two brand hues; a letter
built from the object (an **S** that is a river, an **O** that is a sun ring); a drop-cap with a
tiny serif-era flourish; letter extruded 24px downward in a darker tone.

```xml
<text x="512" y="512" text-anchor="middle" dominant-baseline="central"
      font-family="-apple-system,'SF Pro Display',Inter,'Helvetica Neue',Arial,sans-serif"
      font-weight="800" font-size="620" fill="url(#glyphFill)" filter="url(#inner)">S</text>
```
Optical corrections: round letters (O C G S) +4% size and −1% y; letters with a heavy top (T F P)
+2% y; single letter cap height ≈ 56–62% of the tile. Always check the rendered PNG — font metrics
differ by machine; if the letter lands low or clipped, adjust `y`, don't trust the maths.

## G. Horizon Scene — sky, light, ≤3 land layers

*When:* weather, travel, outdoor, mood, sleep, surf, photography.
*Why it works:* a horizon is the most universal "place" and the easiest scene to read at 29pt.

*Why it usually fails:* it becomes a wallpaper — lovely at 1024, a smear at 29pt. A scene is an icon
only if it has **one bold focal shape** that survives alone.

Rules:
- **Focal shape first.** The sun/moon disc (or the one landform, boat, peak, wave) spans **≥ 24% of the
  tile width** (≈ 250 px at 1024) and has the highest contrast in the image. Everything else is support.
- **Horizon height follows the subject.** Subject in the sky (sun, peak, skyline) → horizon at 55–65%.
  Subject on the water/land (swell lines, a field, a road) → horizon at 30–42%, so the subject sits in the
  optical centre.
- The light source is a flat disc with a wide glow, overlapping the horizon or a landform.
- Landforms: 2–3 simple curves that get **lighter and closer to the sky colour as they recede**
  (atmospheric perspective); one foreground layer is the darkest and carries the only sharp detail.
- ≤ 3 recessive layers. No stars by default — they are noise. No photographic texture.
- A full-bleed scene always "touches the mask" in `validate.py` (it reports `scene` instead of warning);
  what must stay inside the centre 62% is the focal shape.

```xml
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2B1E5E"/><stop offset="1" stop-color="#FF9E5E"/></linearGradient>
<rect width="1024" height="1024" fill="url(#sky)"/>
<circle cx="640" cy="560" r="150" fill="#FFF2C8" filter="url(#glowWide)" opacity="0.9"/>
<circle cx="640" cy="560" r="130" fill="#FFF6DA"/>
<path d="M0 640 C 200 560 380 700 560 620 S 900 540 1024 600 V1024 H0 Z" fill="#5A3E86"/>
<path d="M0 760 C 180 700 420 820 640 740 S 900 700 1024 760 V1024 H0 Z" fill="#2E1E4F"/>
```

---

## Materials cheat-sheet

| Material | Gradient | Highlight | Shadow | Extra |
|---|---|---|---|---|
| glossy plastic | 3 stops, strong | sharp specular ellipse | tight, dark | rim stroke 6–8px |
| matte clay | 2 stops, gentle | wide soft highlight, no specular | soft, wide | slight grain |
| brushed metal | 5–7 alternating bands | thin bright band | crisp | desaturated hue |
| glass | translucent fill 0.15–0.35 | gradient edge stroke | soft + colour bleed | refraction offset copy |
| paper | 1–2 stops, 4–6% | none | short, warm | edge 1px lighter stroke |
| neon | flat bright | white core stroke | glow instead | haze behind |

## Anti-patterns (each one is a tell that the icon was assembled, not designed)

- A circle or rounded square *inside* the tile as the "icon" — the tile already is the shape.
- Three or more separate objects; any text longer than two letters; an emoji; a stock pictogram.
- Gradient that passes through gray (e.g. red→green) or spans > 60° of hue without a mid-stop.
- Pure `#000`/`#FFF` backgrounds; black shadows on coloured surfaces; highlights pointing different ways.
- Strokes < 28px at 1024; gaps < 24px; detail in the outer 10%.
- Drop shadow or rounded corners baked into the tile; transparent background (iOS fills it black).
- A glyph that fills < 45% of the tile ("timid") or > 85% ("cropped").
