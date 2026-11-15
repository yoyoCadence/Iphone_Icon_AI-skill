#!/usr/bin/env python3
"""
inject.py — wire the rendered icons into a web page so "Add to Home Screen" uses them.

    python3 inject.py index.html --name "Tide" --theme "#0b3d91" [options]

What it does
  1. Writes manifest.webmanifest (name, short_name, icons, display, colours) next to the HTML.
  2. Inserts a managed <!-- iphone-icon:start/end --> block into <head> with:
       apple-touch-icon (180×180, the tag iOS actually uses), manifest link, theme-color,
       apple-mobile-web-app-title, and (unless --no-standalone) the standalone-mode metas.
  3. Replaces any previous block, and removes stray apple-touch-icon / manifest / theme-color
     tags so there is exactly one source of truth. Re-running is safe.
  4. Cache-busts every icon URL with ?v=<content hash>; iOS caches home-screen icons hard.

Options
  --icons-dir <dir>     where render.js wrote the PNGs       (default: icons, next to the HTML)
  --web-path <path>     URL prefix the PNGs are served from  (default: derived, e.g. /icons)
  --name <text>         app name under the icon (short_name, apple-mobile-web-app-title)
  --long-name <text>    full name for the manifest           (default: --name)
  --theme <#hex>        theme-color + manifest theme_color   (default: #000000)
  --bg <#hex>           manifest background_color (splash)    (default: --theme)
  --start-url <url>     manifest start_url                   (default: ./)
  --status-bar <mode>   default | black | black-translucent  (default: default)
  --no-standalone       keep Safari chrome when launched from the home screen
  --manifest <file>     manifest filename                    (default: manifest.webmanifest)
  --print               print the <head> block instead of editing the file
"""
import hashlib
import json
import re
import sys
from pathlib import Path

START = "<!-- iphone-icon:start -->"
END = "<!-- iphone-icon:end -->"


def parse(argv):
    opts = {"html": None, "icons_dir": None, "web_path": None, "name": None, "long_name": None,
            "theme": "#000000", "bg": None, "start_url": "./", "status_bar": "default",
            "standalone": True, "manifest": "manifest.webmanifest", "print": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        nxt = lambda: argv[i + 1] if i + 1 < len(argv) else sys.exit(f"inject.py: {a} needs a value")  # noqa: E731
        if a in ("-h", "--help"):
            print(__doc__); sys.exit(0)
        elif a == "--icons-dir": opts["icons_dir"] = nxt(); i += 1
        elif a == "--web-path": opts["web_path"] = nxt(); i += 1
        elif a == "--name": opts["name"] = nxt(); i += 1
        elif a == "--long-name": opts["long_name"] = nxt(); i += 1
        elif a == "--theme": opts["theme"] = nxt(); i += 1
        elif a == "--bg": opts["bg"] = nxt(); i += 1
        elif a == "--start-url": opts["start_url"] = nxt(); i += 1
        elif a == "--status-bar": opts["status_bar"] = nxt(); i += 1
        elif a == "--manifest": opts["manifest"] = nxt(); i += 1
        elif a == "--no-standalone": opts["standalone"] = False
        elif a == "--print": opts["print"] = True
        elif a.startswith("-"): sys.exit(f"inject.py: unknown option {a}\n{__doc__}")
        elif opts["html"] is None: opts["html"] = a
        else: sys.exit(f"inject.py: unexpected argument {a}")
        i += 1
    if opts["html"] is None and not opts["print"]:
        sys.exit(f"inject.py: missing index.html\n{__doc__}")
    return opts


def file_hash(p: Path):
    return hashlib.sha1(p.read_bytes()).hexdigest()[:8] if p.exists() else "1"


def esc(s):
    return str(s).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def main(argv):
    o = parse(argv)
    html_path = Path(o["html"]).resolve() if o["html"] else Path("index.html").resolve()
    base_dir = html_path.parent
    icons_dir = Path(o["icons_dir"]).resolve() if o["icons_dir"] else base_dir / "icons"
    if o["web_path"]:
        web = o["web_path"].rstrip("/")
    else:
        try:
            web = "/" + icons_dir.relative_to(base_dir).as_posix()
        except ValueError:
            web = "/icons"
    name = o["name"] or (re.search(r"<title[^>]*>(.*?)</title>", html_path.read_text(encoding="utf-8", errors="ignore"), re.I | re.S).group(1).strip()
                         if html_path.exists() else "App")
    long_name = o["long_name"] or name
    theme = o["theme"]
    bg = o["bg"] or theme

    required = ["apple-touch-icon.png", "icon-192.png", "icon-512.png"]
    missing = [f for f in required if not (icons_dir / f).exists()]
    if missing and not o["print"]:
        print(f"inject.py: warning — missing in {icons_dir}: {', '.join(missing)} (run render.js first)", file=sys.stderr)

    v = lambda f: f"{web}/{f}?v={file_hash(icons_dir / f)}"  # noqa: E731

    manifest = {
        "name": long_name,
        "short_name": name,
        "start_url": o["start_url"],
        "scope": "./",
        "display": "standalone" if o["standalone"] else "browser",
        "background_color": bg,
        "theme_color": theme,
        "icons": [
            {"src": v("icon-192.png"), "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": v("icon-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": v("icon-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }

    lines = [
        START,
        f'<link rel="apple-touch-icon" sizes="180x180" href="{esc(v("apple-touch-icon.png"))}">',
        f'<link rel="icon" type="image/png" sizes="192x192" href="{esc(v("icon-192.png"))}">',
    ]
    if (icons_dir / "icon.svg").exists():
        lines.append(f'<link rel="icon" type="image/svg+xml" href="{esc(web + "/icon.svg?v=" + file_hash(icons_dir / "icon.svg"))}">')
    lines += [
        f'<link rel="manifest" href="{esc(o["manifest"])}">',
        f'<meta name="theme-color" content="{esc(theme)}">',
        f'<meta name="apple-mobile-web-app-title" content="{esc(name)}">',
    ]
    if o["standalone"]:
        lines += [
            '<meta name="apple-mobile-web-app-capable" content="yes">',
            '<meta name="mobile-web-app-capable" content="yes">',
            f'<meta name="apple-mobile-web-app-status-bar-style" content="{esc(o["status_bar"])}">',
        ]
    lines.append(END)
    block = "\n".join(lines)

    if o["print"]:
        print(block)
        print("\n" + json.dumps(manifest, indent=2, ensure_ascii=False))
        return 0

    if not html_path.exists():
        sys.exit(f"inject.py: {html_path} does not exist")
    src = html_path.read_text(encoding="utf-8")

    # remove a previous managed block and any stray competing tags
    src = re.sub(r"[ \t]*" + re.escape(START) + r".*?" + re.escape(END) + r"[ \t]*\n?", "", src, flags=re.S)
    strays = [
        r'<link[^>]*rel=["\']apple-touch-icon(?:-precomposed)?["\'][^>]*>\s*',
        r'<link[^>]*rel=["\']manifest["\'][^>]*>\s*',
        r'<meta[^>]*name=["\']theme-color["\'][^>]*>\s*',
        r'<meta[^>]*name=["\'](?:apple-)?mobile-web-app-capable["\'][^>]*>\s*',
        r'<meta[^>]*name=["\']apple-mobile-web-app-title["\'][^>]*>\s*',
        r'<meta[^>]*name=["\']apple-mobile-web-app-status-bar-style["\'][^>]*>\s*',
    ]
    removed = 0
    for pat in strays:
        src, k = re.subn(pat, "", src, flags=re.I)
        removed += k

    # viewport is what makes the page phone-friendly in the first place; add it if absent
    to_insert = list(lines)
    if not re.search(r'<meta[^>]*name=["\']viewport["\']', src, re.I):
        to_insert.insert(0, '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
        print("inject.py: added a viewport meta (page had none)", file=sys.stderr)

    head = re.search(r"<head[^>]*>", src, re.I)
    if head:
        # keep <meta charset> first (browsers want it within the first 1024 bytes): insert after it
        charset = re.search(r"<meta[^>]*charset[^>]*>", src[head.end():], re.I)
        pos = head.end() + charset.end() if charset else head.end()
        im = re.match(r"\n([ \t]*)", src[head.end():])
        indent = im.group(1) if im else ""
        insert = "\n" + "\n".join(indent + l for l in to_insert)
        src = src[:pos] + insert + src[pos:]
    else:
        src = "<head>\n" + "\n".join(to_insert) + "\n</head>\n" + src
        print("inject.py: no <head> found — prepended one", file=sys.stderr)

    html_path.write_text(src, encoding="utf-8")
    (base_dir / o["manifest"]).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"inject.py: updated {html_path.name} (+{len(lines)-2} tags, removed {removed} stray tag(s)), wrote {o['manifest']}")
    print(f"           icons served from {web}/ — make sure that path is reachable on the deployed site")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
