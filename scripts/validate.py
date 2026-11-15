#!/usr/bin/env python3
"""
validate.py — objective checks on a rendered icon PNG (ideally the 1024 master).

    python3 validate.py icons/icon-1024.png [--json]

It cannot tell you whether an icon is beautiful. It can tell you the things that
reliably make icons *fail* on a real phone: transparency (iOS fills it with black),
a glyph that is too small or too big for the squircle mask, content in the corners
that iOS will crop, weak contrast at 60pt, or an icon so flat it reads as a placeholder.

Exit code is 0 unless the file cannot be read; findings are advisory.
Only dependency: Pillow (pip install pillow).
"""
import json
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageFilter
except ImportError:  # pragma: no cover
    print("validate.py needs Pillow:  pip install pillow", file=sys.stderr)
    sys.exit(2)

ANALYSIS = 256  # analyse on a downscaled copy; fast and closer to on-device sizes


def rel_lum(rgb):
    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def median_color(pixels):
    if not pixels:
        return (0, 0, 0)
    chans = list(zip(*pixels))
    return tuple(sorted(c)[len(c) // 2] for c in chans[:3])


def saturation(rgb):
    r, g, b = [c / 255.0 for c in rgb[:3]]
    mx, mn = max(r, g, b), min(r, g, b)
    return 0.0 if mx == 0 else (mx - mn) / mx


def inside_squircle(x, y, n=256, exp=5.0):
    # superellipse approximation of the iOS mask, in analysis coordinates
    u = abs((x + 0.5) / n * 2 - 1)
    v = abs((y + 0.5) / n * 2 - 1)
    return u ** exp + v ** exp <= 1.0


def inside_maskable(x, y, n=256):
    # Android maskable safe zone: circle, diameter 80% of the icon
    u = (x + 0.5) / n * 2 - 1
    v = (y + 0.5) / n * 2 - 1
    return u * u + v * v <= 0.8 * 0.8


def analyse(path: Path):
    im = Image.open(path)
    im.load()
    w, h = im.size
    findings = []   # (level, text)  level in {"ok", "warn", "fail"}
    metrics = {"file": str(path), "width": w, "height": h}

    if w != h:
        findings.append(("fail", f"not square ({w}×{h}); iOS stretches non-square icons"))
    if w < 1024:
        findings.append(("warn", f"{w}px master; keep a 1024 master so every size is downscaled, never upscaled"))

    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    hist = alpha.histogram()
    total = w * h
    transparent = sum(hist[:250]) / total
    metrics["transparent_fraction"] = round(transparent, 4)
    if transparent > 0.002:
        corner = [alpha.getpixel((0, 0)), alpha.getpixel((w - 1, 0)), alpha.getpixel((0, h - 1)), alpha.getpixel((w - 1, h - 1))]
        where = "corners" if min(corner) < 250 else "somewhere"
        findings.append(("fail", f"{transparent*100:.1f}% of pixels are transparent ({where}); iOS composites "
                                 "apple-touch-icon over BLACK — paint a full-bleed background"))
    else:
        findings.append(("ok", "opaque, full-bleed"))

    work = rgba.convert("RGB").resize((ANALYSIS, ANALYSIS), Image.LANCZOS)
    n = ANALYSIS
    px = work.load()

    # --- background estimate from the outer ring -------------------------------------------
    ring = int(n * 0.06)
    ring_px = [px[x, y] for y in range(n) for x in range(n) if x < ring or y < ring or x >= n - ring or y >= n - ring]
    bg = median_color(ring_px)
    metrics["background_rgb"] = bg
    bg_l = rel_lum(bg)

    # --- glyph detection: high-frequency content (survives gradients and glows) ------------
    blur = work.filter(ImageFilter.GaussianBlur(10))
    diff = ImageChops.difference(work, blur).convert("L")
    d = diff.load()
    thr = 18
    edge = [(x, y) for y in range(n) for x in range(n) if d[x, y] > thr]
    metrics["edge_pixels"] = len(edge)
    if len(edge) < 40:
        findings.append(("warn", "almost no detail found — reads as a flat tile; add a glyph with real edges"))
        bbox = None
    else:
        xs = [p[0] for p in edge]
        ys = [p[1] for p in edge]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        bw = (bbox[2] - bbox[0] + 1) / n
        bh = (bbox[3] - bbox[1] + 1) / n
        cx = (bbox[0] + bbox[2]) / 2 / n
        cy = (bbox[1] + bbox[3]) / 2 / n
        metrics["glyph_extent"] = {"width": round(bw, 3), "height": round(bh, 3), "cx": round(cx, 3), "cy": round(cy, 3)}
        ext = max(bw, bh)
        if ext < 0.38:
            findings.append(("warn", f"glyph spans only {ext*100:.0f}% of the icon — will look timid at 60pt; most good icons sit at 50–72%"))
        elif ext > 0.9:
            findings.append(("warn", f"detail spans {ext*100:.0f}% of the icon — fine for a full-bleed scene, but then the focal element must sit "
                                     "inside the centre ~62%; for a glyph-on-tile icon this means it touches the mask (iOS crops corners, Android a circle)"))
        else:
            findings.append(("ok", f"glyph spans {ext*100:.0f}% of the icon"))
        off = math.hypot(cx - 0.5, cy - 0.5)
        if off > 0.06:
            findings.append(("warn", f"glyph centre is off by {off*100:.0f}% (cx={cx:.2f}, cy={cy:.2f}); fine if deliberate, "
                                     "but optical centring usually means ≤3% and slightly ABOVE geometric centre"))
        else:
            findings.append(("ok", f"glyph centred (cx={cx:.2f}, cy={cy:.2f})"))

        outside_sq = sum(1 for (x, y) in edge if not inside_squircle(x, y, n))
        outside_mask = sum(1 for (x, y) in edge if not inside_maskable(x, y, n))
        metrics["edge_outside_squircle"] = outside_sq
        metrics["edge_outside_maskable_circle"] = outside_mask
        if outside_sq / len(edge) > 0.01:
            findings.append(("warn", f"{outside_sq/len(edge)*100:.0f}% of detail lies in the corners iOS masks away — "
                                     "unless it is background texture, pull it inward"))
        if outside_mask / len(edge) > 0.08:
            findings.append(("warn", f"{outside_mask/len(edge)*100:.0f}% of detail lies outside the Android maskable safe circle (80%) — "
                                     "acceptable for iOS-only, otherwise keep the core glyph inside"))

        # --- contrast: split the glyph region into its two main tones (Otsu) and compare them --
        pad = 4
        lums, cols = [], []
        for y in range(max(0, bbox[1] - pad), min(n, bbox[3] + pad + 1)):
            for x in range(max(0, bbox[0] - pad), min(n, bbox[2] + pad + 1)):
                p = px[x, y]
                lums.append(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2])
                cols.append(p)
        histo = [0] * 256
        for l in lums:
            histo[min(255, int(l))] += 1
        tot = len(lums)
        sum_all = sum(i * histo[i] for i in range(256))
        w_b = sum_b = 0.0
        best, split = -1.0, 128
        for t in range(256):
            w_b += histo[t]
            if w_b == 0:
                continue
            w_f = tot - w_b
            if w_f == 0:
                break
            sum_b += t * histo[t]
            m_b, m_f = sum_b / w_b, (sum_all - sum_b) / w_f
            between = w_b * w_f * (m_b - m_f) ** 2
            if between > best:
                best, split = between, t
        dark = [c for l, c in zip(lums, cols) if l <= split]
        light = [c for l, c in zip(lums, cols) if l > split]
        if dark and light:
            d_c, l_c = median_color(dark), median_color(light)
            cr = contrast(d_c, l_c)
            metrics["tone_dark_rgb"] = d_c
            metrics["tone_light_rgb"] = l_c
            metrics["glyph_contrast"] = round(cr, 2)
            if cr < 2.0:
                findings.append(("warn", f"main tonal contrast {cr:.1f}:1 — the silhouette will smear at 29–40pt; aim ≥3:1 between glyph and background"))
            elif cr < 3.0:
                findings.append(("ok", f"main tonal contrast {cr:.1f}:1 (acceptable; ≥3:1 is safer on busy wallpapers)"))
            else:
                findings.append(("ok", f"main tonal contrast {cr:.1f}:1"))

    # --- colour richness ----------------------------------------------------------------------
    pal = work.convert("P", palette=Image.ADAPTIVE, colors=64)
    counts = sorted(((c, i) for c, i in pal.getcolors(65536) or []), reverse=True)
    significant = [c for c, _ in counts if c / (n * n) > 0.004]
    metrics["significant_colours"] = len(significant)
    if len(significant) < 4:
        findings.append(("warn", f"only {len(significant)} significant colours — reads as flat clip-art; add gradient, light and shadow"))
    else:
        findings.append(("ok", f"{len(significant)} significant colours (tonal depth present)"))

    sat_bg = saturation(bg)
    metrics["background_luminance"] = round(bg_l, 3)
    if bg_l < 0.01:
        findings.append(("warn", "background is near pure black; iOS dark wallpapers swallow it — try a very dark hue (#0b0f1e-ish) with a lit glyph"))
    if bg_l > 0.9 and sat_bg < 0.1:
        findings.append(("warn", "background is near pure white; on light wallpapers the icon loses its edge — tint it or add a gradient"))

    return findings, metrics


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("--")]
    out = {}
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"validate.py: no such file {p}", file=sys.stderr)
            return 2
        findings, metrics = analyse(path)
        out[p] = {"findings": [{"level": l, "text": t} for l, t in findings], "metrics": metrics}
        if not as_json:
            print(f"\n{p}  ({metrics['width']}×{metrics['height']})")
            icon = {"ok": "  ✓ ", "warn": "  ⚠ ", "fail": "  ✗ "}
            for level, text in findings:
                print(icon[level] + text)
            warns = sum(1 for l, _ in findings if l != "ok")
            print(f"  → {warns} thing(s) to look at" if warns else "  → no mechanical problems; now judge it with your eyes (preview.png)")
    if as_json:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
