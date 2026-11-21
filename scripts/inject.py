#!/usr/bin/env python3
"""
inject.py — wire the rendered icons into a web page so "Add to Home Screen" uses them.

    python3 inject.py index.html --name "Tide" --theme "#0b3d91" [options]

What it does
  1. If the page ALREADY links an apple-touch-icon or a manifest (outside this script's own
     block), it changes nothing and prints the paths the page uses, so you can render the new
     icon to those paths instead. Pass --force to rewire anyway. Projects with their own icon
     build (an icon script, icon tests, a service worker) almost always want the first option.
  2. Otherwise inserts a managed <!-- iphone-icon:start/end --> block into <head>:
     apple-touch-icon (180×180), icon, manifest link, and only those of theme-color,
     apple-mobile-web-app-title and the standalone metas that the page does not already set
     (a value the page already chose is kept unless you pass the matching option).
  3. Writes or updates the manifest: an existing manifest keeps every field except "icons"
     (and the fields you pass explicitly); a new one gets name, short_name, colours, display.
  4. URLs are RELATIVE to the HTML (icons/apple-touch-icon.png?v=<hash>), so the site works
     under a sub-path such as GitHub Pages' /<repo>/. Re-running is safe.

Options
  --icons-dir <dir>     where render.js wrote the PNGs        (default: icons, next to the HTML)
  --web-path <path>     URL prefix for the PNGs, e.g. /static/icons (default: relative path)
  --name <text>         app name under the icon (short_name, apple-mobile-web-app-title)
  --long-name <text>    full name for the manifest            (default: --name)
  --theme <#hex>        theme-color + manifest theme_color
  --bg <#hex>           manifest background_color (splash)     (default: --theme)
  --start-url <url>     manifest start_url                    (default: ./ for new manifests)
  --status-bar <mode>   default | black | black-translucent   (only added if the page sets none)
  --no-standalone       do not add the standalone (app-like) metas
  --manifest <file>     manifest filename for a NEW manifest   (default: manifest.webmanifest)
  --force               rewire a page that already has icon/manifest links
  --print               no page to edit (or you only want the snippet): write the manifest into --out
                        (the folder served as the site root, e.g. public/) and head-snippet.html into the
                        current folder (never into the deployed folder), and print the snippet
  --out <dir>           with --print: where the manifest goes              (default: current folder)
  --snippet <file>      with --print: where head-snippet.html goes         (default: ./head-snippet.html)
Exit codes: 0 ok · 2 usage error · 3 page already wired (nothing changed; see message)
"""
import hashlib
import json
import os
import re
import struct
import sys
from pathlib import Path

START = "<!-- iphone-icon:start -->"
END = "<!-- iphone-icon:end -->"
BLOCK_RE = re.compile(r"[ \t]*" + re.escape(START) + r".*?" + re.escape(END) + r"[ \t]*\n?", re.S)


def parse(argv):
    o = {"html": None, "icons_dir": None, "web_path": None, "name": None, "long_name": None, "theme": None,
         "bg": None, "start_url": None, "status_bar": None, "standalone": True, "manifest": "manifest.webmanifest",
         "force": False, "print": False, "out": None, "snippet": None}
    flags = {"--no-standalone": ("standalone", False), "--force": ("force", True), "--print": ("print", True)}
    valued = {"--icons-dir": "icons_dir", "--web-path": "web_path", "--name": "name", "--long-name": "long_name",
              "--theme": "theme", "--bg": "bg", "--start-url": "start_url", "--status-bar": "status_bar",
              "--manifest": "manifest", "--out": "out", "--snippet": "snippet"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            print(__doc__); sys.exit(0)
        if a in flags:
            k, v = flags[a]; o[k] = v
        elif a in valued:
            if i + 1 >= len(argv):
                print(f"inject.py: {a} needs a value", file=sys.stderr); sys.exit(2)
            o[valued[a]] = argv[i + 1]; i += 1
        elif a.startswith("-"):
            print(f"inject.py: unknown option {a}\n{__doc__}", file=sys.stderr); sys.exit(2)
        elif o["html"] is None:
            o["html"] = a
        else:
            print(f"inject.py: unexpected argument {a}", file=sys.stderr); sys.exit(2)
        i += 1
    if o["html"] is None and not o["print"]:
        print(f"inject.py: missing index.html\n{__doc__}", file=sys.stderr); sys.exit(2)
    return o


def file_hash(p: Path):
    return hashlib.sha1(p.read_bytes()).hexdigest()[:8] if p.exists() else "1"


def esc(s):
    return str(s).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def png_size(p: Path):
    try:
        with open(p, "rb") as f:
            head = f.read(24)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", head[16:24])
    except OSError:
        pass
    return None


def tag_attr(tag, name):
    m = re.search(r'\b%s\s*=\s*["\']([^"\']*)["\']' % name, tag, re.I)
    return m.group(1) if m else None


def find_link(html, rel):
    for tag in re.findall(r"<link\b[^>]*>", html, re.I):
        rels = (tag_attr(tag, "rel") or "").lower().split()
        if rel in rels:
            return tag
    return None


def find_meta(html, name):
    for tag in re.findall(r"<meta\b[^>]*>", html, re.I):
        if (tag_attr(tag, "name") or "").lower() == name:
            return tag
    return None


def strip_query(u):
    return u.split("?", 1)[0].split("#", 1)[0]


def report_existing(html_path, outside):
    base = html_path.parent
    apple = find_link(outside, "apple-touch-icon")
    man = find_link(outside, "manifest")
    print("inject.py: this page already wires its home-screen icon — nothing changed.\n")
    targets = []
    if apple:
        href = tag_attr(apple, "href") or ""
        p = (base / strip_query(href)) if not re.match(r"^[a-z]+:|^/", href) else None
        sz = png_size(p) if p else None
        print(f"  apple-touch-icon  {href}" + (f"   ({sz[0]}×{sz[1]})" if sz else "   (not a local file I can read)"))
        if p:
            targets.append((str(p), 180))
    if man:
        href = tag_attr(man, "href") or ""
        p = (base / strip_query(href)) if not re.match(r"^[a-z]+:|^/", href) else None
        print(f"  manifest          {href}")
        if p and p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                for ic in data.get("icons", []):
                    src = ic.get("src", "")
                    ip = (p.parent / strip_query(src)) if not re.match(r"^[a-z]+:|^/", src) else None
                    sz = png_size(ip) if ip else None
                    print(f"    icon {ic.get('sizes', '?'):>9} {ic.get('purpose', 'any'):<9} {src}" + (f"   ({sz[0]}×{sz[1]})" if sz else ""))
                    if ip:
                        targets.append((str(ip), int(str(ic.get("sizes", "0x0")).split("x")[0] or 0)))
            except (ValueError, OSError) as e:
                print(f"    (could not read it: {e})")
    print("\nNext steps (recommended):")
    print("  1. Look for the project's own icon build first (an npm script like `icons`, a make-icons file,")
    print("     tests that open these PNGs). If one exists, edit ITS source SVG and run IT — its tests are the contract.")
    print("  2. Otherwise render straight to the paths above, e.g.:")
    dirs = sorted({str(Path(t).parent) for t, _ in targets})
    for d in dirs:
        print(f"       node scripts/render.js icon.svg --out {d}")
    print("     and rename/copy so each listed file gets the right size. A file listed as \"maskable\" needs the")
    print("     art inside the centre 80% circle (validate.py reports it).")
    print("  3. Bust caches: iOS keeps the icon it saw when the shortcut was added; a service worker that")
    print("     serves images cache-first keeps the OLD file at the same URL until its cache version changes.")
    print("\nRe-run with --force to replace the wiring instead.")
    return 3


def main(argv):
    o = parse(argv)
    if o["html"]:
        html_path = Path(o["html"]).resolve()
    else:
        html_path = (Path(o["out"]).resolve() if o["out"] else Path.cwd()) / "index.html"
    base_dir = html_path.parent
    src = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    had_block = START in src
    outside = BLOCK_RE.sub("", src)

    if not o["print"] and not had_block and not o["force"] and (find_link(outside, "apple-touch-icon") or find_link(outside, "manifest")):
        return report_existing(html_path, outside)

    icons_dir = Path(o["icons_dir"]).resolve() if o["icons_dir"] else base_dir / "icons"
    if o["web_path"]:
        web = o["web_path"].rstrip("/")
    else:
        web = os.path.relpath(icons_dir, base_dir).replace(os.sep, "/")
        web = "." if web == "." else web
    url = lambda f: f"{web}/{f}?v={file_hash(icons_dir / f)}"  # noqa: E731

    title = re.search(r"<title[^>]*>(.*?)</title>", src, re.I | re.S)
    page_title = re.sub(r"\s+", " ", title.group(1)).strip() if title else "App"
    existing_title = find_meta(outside, "apple-mobile-web-app-title")
    name = o["name"] or (tag_attr(existing_title, "content") if existing_title else None) or page_title
    long_name = o["long_name"] or name
    existing_theme = find_meta(outside, "theme-color")
    theme = o["theme"] or (tag_attr(existing_theme, "content") if existing_theme else None)

    required = ["apple-touch-icon.png", "icon-192.png", "icon-512.png"]
    missing = [f for f in required if not (icons_dir / f).exists()]
    if missing:
        print(f"inject.py: warning — missing in {icons_dir}: {', '.join(missing)} (run render.js first, or pass --icons-dir); "
              "cache-busters fall back to ?v=1", file=sys.stderr)
    maskable = "icon-maskable-512.png" if (icons_dir / "icon-maskable-512.png").exists() else "icon-512.png"

    # ---- decide which tags this block owns -------------------------------------------------
    lines = [START,
             f'<link rel="apple-touch-icon" sizes="180x180" href="{esc(url("apple-touch-icon.png"))}">',
             f'<link rel="icon" type="image/png" sizes="192x192" href="{esc(url("icon-192.png"))}">']
    if (icons_dir / "icon.svg").exists():
        lines.append(f'<link rel="icon" type="image/svg+xml" href="{esc(web + "/icon.svg?v=" + file_hash(icons_dir / "icon.svg"))}">')
    existing_manifest = find_link(outside, "manifest")
    if existing_manifest:
        manifest_href = strip_query(tag_attr(existing_manifest, "href"))
    elif web.startswith("/"):
        manifest_href = "/" + o["manifest"]          # absolute icon paths → absolute manifest (nested routes)
    else:
        manifest_href = o["manifest"]
    lines.append(f'<link rel="manifest" href="{esc(manifest_href)}">')
    replace = []   # (kind, name) of page tags this run replaces
    if o["theme"] or not existing_theme:
        lines.append(f'<meta name="theme-color" content="{esc(theme or "#000000")}">')
        if existing_theme:
            replace.append(("meta", "theme-color"))
    if o["name"] or not existing_title:
        lines.append(f'<meta name="apple-mobile-web-app-title" content="{esc(name)}">')
        if existing_title:
            replace.append(("meta", "apple-mobile-web-app-title"))
    if o["standalone"]:
        for meta, val in (("apple-mobile-web-app-capable", "yes"), ("mobile-web-app-capable", "yes")):
            if not find_meta(outside, meta):
                lines.append(f'<meta name="{meta}" content="{val}">')
    if o["standalone"] or o["status_bar"]:
        existing_sb = find_meta(outside, "apple-mobile-web-app-status-bar-style")
        if o["status_bar"] or not existing_sb:
            lines.append(f'<meta name="apple-mobile-web-app-status-bar-style" content="{esc(o["status_bar"] or "default")}">')
            if existing_sb:
                replace.append(("meta", "apple-mobile-web-app-status-bar-style"))
    lines.append(END)

    # ---- manifest: update in place, never drop fields we do not own ----------------------------
    man_path = base_dir / manifest_href.lstrip("/") if not re.match(r"^[a-z]+:", manifest_href) else base_dir / o["manifest"]
    man_rel = os.path.relpath(icons_dir, man_path.parent).replace(os.sep, "/")
    man_url = lambda f: (f"{web}/{f}" if o["web_path"] else f"{man_rel}/{f}") + f"?v={file_hash(icons_dir / f)}"  # noqa: E731
    manifest = {}
    if man_path.exists():
        try:
            manifest = json.loads(man_path.read_text(encoding="utf-8"))
        except ValueError:
            print(f"inject.py: {man_path.name} is not valid JSON — leaving it alone, writing nothing", file=sys.stderr)
            return 2
    kept = sorted(k for k in manifest if k != "icons")
    for key, val, explicit in (("name", long_name, o["long_name"] or o["name"]), ("short_name", name, o["name"]),
                               ("theme_color", theme, o["theme"]), ("background_color", o["bg"] or theme, o["bg"] or o["theme"]),
                               ("start_url", o["start_url"] or "./", o["start_url"]), ("display", "standalone" if o["standalone"] else "browser", None)):
        if val and (explicit or key not in manifest):
            manifest[key] = val
    manifest.setdefault("scope", "./")
    manifest["icons"] = [
        {"src": man_url("icon-192.png"), "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": man_url("icon-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": man_url(maskable), "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ]

    if o["print"]:
        snippet = ['<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'] + lines
        snippet_path = Path(o["snippet"]).resolve() if o["snippet"] else Path.cwd() / "head-snippet.html"
        snippet_path.parent.mkdir(parents=True, exist_ok=True)
        snippet_path.write_text("\n".join(snippet) + "\n", encoding="utf-8")
        man_path.parent.mkdir(parents=True, exist_ok=True)
        man_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("\n".join(snippet))
        print(f"\ninject.py: wrote {snippet_path} and {man_path} "
              f"(manifest href {manifest_href}; icons at {web}/)", file=sys.stderr)
        return 0
    if not html_path.exists():
        print(f"inject.py: {html_path} does not exist", file=sys.stderr); return 2

    # ---- edit the HTML ---------------------------------------------------------------------------
    src = BLOCK_RE.sub("", src)
    removed = 0
    for pat in (r'<link[^>]*rel=["\']apple-touch-icon(?:-precomposed)?["\'][^>]*>[ \t]*\n?',
                r'<link[^>]*rel=["\']manifest["\'][^>]*>[ \t]*\n?'):
        src, k = re.subn(pat, "", src, flags=re.I); removed += k
    for _, meta in replace:
        src, k = re.subn(r'<meta[^>]*name=["\']%s["\'][^>]*>[ \t]*\n?' % re.escape(meta), "", src, flags=re.I); removed += k

    to_insert = list(lines)
    if not re.search(r'<meta[^>]*name=["\']viewport["\']', src, re.I):
        to_insert.insert(0, '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">')
        print("inject.py: added a viewport meta (page had none)", file=sys.stderr)
    head = re.search(r"<head[^>]*>", src, re.I)
    if head:
        charset = re.search(r"<meta[^>]*charset[^>]*>", src[head.end():], re.I)
        pos = head.end() + charset.end() if charset else head.end()
        im = re.match(r"\n([ \t]*)", src[head.end():])
        indent = im.group(1) if im else ""
        src = src[:pos] + "\n" + "\n".join(indent + l for l in to_insert) + src[pos:]
    else:
        src = "<head>\n" + "\n".join(to_insert) + "\n</head>\n" + src
        print("inject.py: no <head> found — prepended one", file=sys.stderr)

    html_path.write_text(src, encoding="utf-8")
    man_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"inject.py: updated {html_path.name} ({len(lines) - 2} tags in the managed block, replaced {removed} page tag(s)); "
          f"{'updated' if kept else 'wrote'} {man_path.name}" + (f" (kept: {', '.join(kept)})" if kept else ""))
    print(f"           icon URLs are relative ({web}/…) — they resolve against the page, so sub-path hosting works")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
