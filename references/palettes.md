# Palettes — gradient pairs that render clean, with their glyph tones

Each row: tile gradient (top → bottom), glyph tone, shadow tint (use for drop/inner shadows on
that tile), accent (optional, use once), and the moods it carries. Hex values are calibrated so
the top stop is lighter *and* hue-shifted — copy them literally or apply the same logic to a brand
colour (see "Deriving from a brand colour").

## Curated pairs

| Name | Tile top → bottom | Glyph | Shadow tint | Accent | Moods |
|---|---|---|---|---|---|
| Ocean | `#3E9BFF → #0B47B8` | `#FFFFFF`/`#DCE9FF` | `#062A6E` | `#8AF3FF` | trust, clarity, utility |
| Dusk | `#FFB36B → #E8457A → #5B2E8C` (3) | `#FFF4E8` | `#3A1250` | `#FFE08A` | travel, mood, photography |
| Forest | `#5CC88F → #1E6A48` | `#F2FFF6` | `#0A3B26` | `#F8E36A` | habits, nature, growth |
| Ember | `#FF8E5A → #C8102E` | `#FFF3EC` | `#5E0514` | `#FFD36A` | energy, fitness, food |
| Honey (pale tile) | `#FFE38A → #F2A218` | `#4A2600` (dark!) | `#8A4B00` | `#FFFFFF` | warmth, kids, bakery |
| Lavender | `#C2A6FF → #6A48D6` | `#FFFFFF` | `#2D1B6B` | `#FFC6F0` | calm, sleep, journaling |
| Mint (pale tile) | `#D9FBEE → #7FDCB4` | `#0E3B2C` (dark) | `#2E7A5B` | `#FF9A6B` | health, fresh, finance-light |
| Slate | `#6B7C99 → #27314A` | `#FFFFFF` | `#0E1424` | `#FFB020` | tools, professional, data |
| Rose | `#FFC2D4 → #E2497F` | `#FFFFFF` | `#6A1038` | `#FFF1A8` | dating, beauty, gifts |
| Midnight | `#1C2550 → #0A0E24` | `#5EF1FF` (lum.) | — | `#FF7A59` | dev tools, night, music |
| Charcoal+amber | `#3A3F4C → #16181F` | `#FFC24A` | — | `#FFFFFF` | premium, craft, audio |
| Sunrise | `#FFD86B → #FF8C42 → #E4414D` (3) | `#FFFFFF` | `#7A1A1F` | `#5B3FA8` | morning, weather, motivation |
| Aurora | `#43E8C9 → #2E6BFF` | `#FFFFFF` | `#0D2C7A` | `#C8FF6A` | science, AI, learning |
| Clay | `#E9B59A → #B86B4B` | `#FFF5EE` | `#5A2A17` | `#2F5D50` | crafts, pottery, cooking |
| Paper (pale tile) | `#FFF8E7 → #F2E4C4` | `#2B2418` (dark) | `#8B7340` | `#D64545` | notes, reading, planners |

Pale tiles with dark glyphs are under-used on home screens; on a dark wallpaper they pop, on a
light wallpaper they need the bottom stop to be clearly darker than the wallpaper — check both
panels of `preview.png`.

## Deriving from a brand colour (when the page already has one)

Given brand `H S L` (HSL):
- **top stop**: `L + 12`, `S + 5`, hue rotated **toward yellow** (≈ `H − 10°` for blues/violets,
  `H + 10°` for reds/oranges) — warm light from above.
- **bottom stop**: `L − 24`, `S + 8`, hue rotated **toward blue/violet** by ≈ 10° — cool shade below.
- **shadow tint**: bottom stop at `L − 20`, `S + 10`.
- **glyph**: white tinted 6–8% toward the brand hue (`#FFFFFF` → e.g. `#E9F0FF` for blue) if
  brand `L < 60`; otherwise a near-black of the brand hue (`L ≈ 14`, `S ≈ 40`).

Why the rotation: lightening a colour without rotating it looks chalky; darkening without rotating
looks dirty. The ±10° is how paint actually behaves under warm light.

## Combinations to avoid (strongly owned by famous apps)

green tile + white speech bubble · light-blue tile + white bird · rainbow/violet-orange tile + camera ·
red tile + white play triangle · blue tile + white lowercase *f* · orange tile + white arcs ·
yellow tile + white ghost · black tile + white musical note on red · white tile + multicolour *G*.
If the brief lands on one of these, change the hue family *and* the form.

## Colour discipline in one line

Two hues in the tile, one glyph tone, at most one accent, all shadows tinted — then stop.
