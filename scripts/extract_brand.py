#!/usr/bin/env python3
"""
extract_brand.py — pull the design facts out of an existing page before designing its icon.

    python3 extract_brand.py index.html [styles.css ...]

Prints: title / description / theme-color, the most-used colours (hex, rgb, hsl, named CSS
variables), font families, and whether the page already declares icons or a manifest.
Pure stdlib. Treat the output as evidence, not as orders: a page whose CSS is 90% gray
still needs a colourful icon.
"""
import re
import sys
from collections import Counter
from pathlib import Path

NAMED = {"white": "#ffffff", "black": "#000000", "red": "#ff0000", "blue": "#0000ff", "green": "#008000",
         "orange": "#ffa500", "purple": "#800080", "pink": "#ffc0cb", "yellow": "#ffff00", "gray": "#808080", "grey": "#808080"}
BORING = {"#ffffff", "#000000", "#fff", "#000", "#333", "#333333", "#666", "#666666", "#999", "#999999",
          "#ccc", "#cccccc", "#ddd", "#dddddd", "#eee", "#eeeeee", "#f5f5f5", "#fafafa", "#1a1a1a", "#111", "#111111", "#222", "#222222"}


def norm_hex(h):
    h = h.lower()
    if len(h) == 4:
        h = "#" + "".join(c * 2 for c in h[1:])
    return h[:7]


def rgb_to_hex(r, g, b):
    return "#%02x%02x%02x" % (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    text = ""
    for p in argv:
        path = Path(p)
        if path.exists():
            text += "\n" + path.read_text(encoding="utf-8", errors="ignore")
        else:
            print(f"extract_brand.py: skip missing {p}", file=sys.stderr)

    def meta(name):
        m = re.search(r'<meta[^>]*(?:name|property)=["\']%s["\'][^>]*content=["\']([^"\']*)' % re.escape(name), text, re.I)
        if not m:
            m = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*(?:name|property)=["\']%s["\']' % re.escape(name), text, re.I)
        return m.group(1).strip() if m else None

    title = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S)
    print("== identity ==")
    print(f"title:        {title.group(1).strip() if title else '-'}")
    print(f"h1:           {re.sub('<[^>]+>', '', h1.group(1)).strip() if h1 else '-'}")
    print(f"description:  {meta('description') or meta('og:description') or '-'}")
    print(f"theme-color:  {meta('theme-color') or '-'}")
    lang = re.search(r"<html[^>]*\blang=[\"']([^\"']+)", text, re.I)
    print(f"lang:         {lang.group(1) if lang else '-'}")

    colours = Counter()
    # anchors like href="#add" are not colours
    colour_text = re.sub(r"""(?:href|id|aria-controls|for)\s*=\s*["']#?[^"']*["']""", " ", text, flags=re.I)
    for h in re.findall(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b", colour_text):
        colours[norm_hex(h)] += 1
    for r, g, b in re.findall(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", text):
        colours[rgb_to_hex(r, g, b)] += 1
    for name, hx in NAMED.items():
        k = len(re.findall(r"(?<![\w-])%s(?![\w-])" % name, text))
        if k:
            colours[hx] += k
    print("\n== colours (most used first; grays listed separately) ==")
    chroma = [(c, n) for c, n in colours.most_common() if c not in BORING]
    grays = [(c, n) for c, n in colours.most_common() if c in BORING]
    for c, n in chroma[:10]:
        print(f"  {c}  ×{n}")
    if grays:
        print("  neutrals: " + ", ".join(f"{c}×{n}" for c, n in grays[:6]))
    if not chroma:
        print("  (no chromatic colours found — the icon will have to supply the personality)")

    vars_ = re.findall(r"(--[\w-]*(?:color|colour|primary|accent|brand|bg|background)[\w-]*)\s*:\s*([^;]+);", text, re.I)
    if vars_:
        print("\n== css variables that look like brand tokens ==")
        seen = set()
        for k, val in vars_:
            if k not in seen:
                seen.add(k)
                print(f"  {k}: {val.strip()}")

    fonts = Counter()
    for fam in re.findall(r"font-family\s*:\s*([^;}]+)", text, re.I):
        first = fam.split(",")[0].strip().strip("'\"")
        if first and not first.startswith("var("):
            fonts[first] += 1
    gf = re.findall(r"fonts\.googleapis\.com/css2?\?family=([^&\"']+)", text)
    print("\n== typography ==")
    for f, n in fonts.most_common(5):
        print(f"  {f}  ×{n}")
    for g in gf:
        print(f"  google fonts: {g.replace('+', ' ')}")
    if not fonts and not gf:
        print("  (no explicit font-family)")

    print("\n== existing icon wiring ==")
    for label, pat in [("apple-touch-icon", r'rel=["\']apple-touch-icon'), ("manifest", r'rel=["\']manifest'),
                       ("favicon", r'rel=["\'](?:shortcut )?icon'), ("standalone meta", r'apple-mobile-web-app-capable'),
                       ("viewport", r'name=["\']viewport')]:
        print(f"  {label:18} {'yes' if re.search(pat, text, re.I) else 'no'}")

    words = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", text, flags=re.S | re.I)
    words = re.findall(r"[A-Za-z\u4e00-\u9fff]{3,}", words)
    stop = {"the", "and", "for", "with", "that", "this", "you", "your", "are", "from", "have", "not", "but", "all", "can"}
    top = [w for w, _ in Counter(w.lower() for w in words if w.lower() not in stop).most_common(12)]
    print("\n== frequent words in the copy (what the app is about) ==")
    print("  " + ", ".join(top) if top else "  (no visible copy)")

    # The app's own words: headings and tagline-like elements. Ideas drawn from these (the name
    # taken literally, a motto, a thesis) are the most ownable — see design-process §1a.
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S | re.I)
    own = []
    # taglines and notes first (most ownable), then headings
    pats = [r"<(?:p|div|span|small|strong|em|a)[^>]*class=[\"'][^\"']*(?:tagline|subtitle|slogan|motto|lead|hero|eyebrow|brand|kicker|thesis|note|claim|quote)[^\"']*[\"'][^>]*>(.*?)</(?:p|div|span|small|strong|em|a)>",
            r"<h[1-3][^>]*>(.*?)</h[1-3]>"]
    for pat in pats:
        for m in re.findall(pat, body, re.I | re.S):
            t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m)).strip()
            if 2 <= len(t) <= 80 and t not in own:
                own.append(t)
    print("\n== own words (headings, taglines — mine these for the idea) ==")
    print("\n".join(f"  {t}" for t in own[:14]) if own else "  (none found — read the README's first paragraph and the UI copy)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
