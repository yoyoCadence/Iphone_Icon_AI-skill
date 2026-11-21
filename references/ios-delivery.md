# iOS delivery — what the phone actually reads, and how to test it

## The one tag that matters on iPhone

```html
<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png?v=3f2a9c1e">
```

- iOS Safari uses **this** for "Add to Home Screen". Manifest `icons` are *not* a reliable
  substitute on iOS — ship both, but never only the manifest.
- 180×180 covers every current iPhone (60pt @3x). iPad uses 167/152; iOS downsamples the 180 if
  those are absent, so extra sizes are optional. One tag, one file, no `-precomposed` (obsolete).
- The PNG must be **opaque** and **square with square corners**. iOS applies the squircle mask and
  composites over black: transparency becomes black corners, baked-in rounding becomes a double
  border.
- Without any tag, iOS requests `/apple-touch-icon.png` at the site root — a safe fallback to also
  place there if the site has multiple pages.

## Caching: the most common "it didn't change" report

iOS caches home-screen icons by URL. After re-rendering, change the URL (`?v=<hash>`, which
`inject.py` does automatically) **and** remove + re-add the web clip on the phone. An existing
home-screen shortcut never refreshes its icon on its own.

**Service workers.** A PWA whose worker serves images cache-first (very common: "images, icons,
manifests → cache-first") keeps returning the *old* PNG at the same URL, in the browser and in the
manifest, until the worker's cache name changes. If the project has a worker, bump its cache version
(or run the project's version/bump script) in the same change, and say so in the hand-off. If the
worker precaches an explicit list of icon URLs, a `?v=` query makes those entries miss — update the
list or rely on the version bump instead of the query.

## URLs: choose by how the site is served

iOS reads the `apple-touch-icon` from whatever page the user is on when they tap *Add to Home Screen*,
so the href must resolve from every page:

| Site | Use | Breaks if you use the other |
|---|---|---|
| all pages in one folder (plain HTML, GitHub Pages project site `user.github.io/<repo>/`) | relative `icons/…` (inject.py default) | `/icons/…` 404s under `/<repo>/` |
| single-page app with nested routes (`/spot/123`) served at the domain root (Vite, Next, CRA `public/`) | `--web-path /icons` | `icons/…` resolves to `/spot/icons/…` |
| single-page app with nested routes under a sub-path | `--web-path /<base>/icons` | both of the above |

When there is no code yet, pick the most likely row, say which one you assumed, and give the one-line
change for the other case.

## The name under the icon

`<meta name="apple-mobile-web-app-title" content="Tidewatch">` — otherwise `<title>` is used, and
titles are usually too long. iOS truncates at roughly 11–13 characters with an ellipsis. Prefer the
short brand name; never a slogan.

## Standalone mode (app-like) — a trade-off, say so

```html
<meta name="apple-mobile-web-app-capable" content="yes">   <!-- iOS -->
<meta name="mobile-web-app-capable" content="yes">         <!-- Android/Chromium -->
<meta name="apple-mobile-web-app-status-bar-style" content="default">  <!-- default | black | black-translucent -->
```
Launching from the home screen hides Safari's address bar and navigation. Consequences:
- the page must provide its own back/close affordances; no browser back button;
- links to other origins open in an in-app browser sheet; same-origin navigation stays inside;
- `default` is a light status bar with dark text — wrong above a dark UI; dark apps use `black`;
- the status bar overlays the page with `black-translucent`; use
  `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`
  and `padding-top: env(safe-area-inset-top)` on the header;
- `theme-color` tints Safari's chrome and, in standalone, the status-bar area.

If the page is a plain content site, pass `--no-standalone` to `inject.py` and keep the browser UI.

## Manifest (Android, Chrome, desktop PWAs)

```json
{ "name": "Tidewatch", "short_name": "Tidewatch", "start_url": "./", "scope": "./",
  "display": "standalone", "background_color": "#0B47B8", "theme_color": "#0B47B8",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" } ] }
```
`maskable` means Android may crop the image to a circle, squircle or rounded square — the glyph
must sit inside the central 80% circle (`validate.py` checks this). Because the exported icon is
full-bleed with the glyph centred, the *same* 512 serves both purposes; a separate padded file is
unnecessary. `background_color` is used for the splash/launch surface while the app loads — pick
the tile's bottom colour so the icon appears to grow out of it. `theme_color` / `<meta name="theme-color">`
colours the browser chrome beside the page, so it should match the page header (usually the brand
colour) — keep a page's existing value; it is not the icon's colour.

## Favicon / tabs

`<link rel="icon" type="image/png" sizes="192x192" href="/icons/icon-192.png">` plus the SVG
(`type="image/svg+xml"`) is enough for modern browsers. A dedicated 32px favicon is optional; if
the glyph is intricate, simplify it for 32px rather than shrinking the full tile.

## Testing on a real iPhone (2 minutes)

1. Serve the folder over HTTP (`npx serve .` or `python3 -m http.server`), open it in **Safari**
   (not Chrome — only Safari can add web clips on iOS) on the phone via the LAN address.
2. Share → **Add to Home Screen**. Check: icon, name length, no black corners.
3. Change something, re-render, reload, remove the clip, add again. Verify the `?v=` changed.
4. Switch wallpaper dark/light; glance at the icon next to real apps. If it disappears on one
   of them, deepen the tile's bottom stop or add the rim/edge treatment.

## Checklist before saying "done"

- [ ] `apple-touch-icon.png` is 180×180, opaque, square corners, < 100 KB
- [ ] `icon-192.png`, `icon-512.png`, `manifest.webmanifest` present and linked
- [ ] `?v=` cache-buster in every icon URL (inject.py)
- [ ] `apple-mobile-web-app-title` ≤ 11 characters
- [ ] viewport meta present; if standalone, safe-area padding exists
- [ ] icons folder actually deployed at the referenced path (the #2 "it doesn't show" cause)
