#!/usr/bin/env python3
"""
ribbon.py — strokes that SVG cannot draw: width and colour changing along the path.

Comet trails, rising orbits, brush strokes, swooshes, tapering waves — anything whose
energy should *grow* or *fade* along its length. Plain SVG strokes have one width and
no gradient along the path; this script samples the centreline and emits a ribbon of
small opaque polygons (overlapping by one sample, so no seams) to paste into an icon.

Centreline sources (pick one):
  --path "M x y C x1 y1 x2 y2 x y ..."   absolute M/L/C/Q/Z commands (what you would draw by hand)
  --spiral cx,cy,r0,r1,turns[,squash[,tilt_deg[,start_deg]]]
                                          an orbit seen in perspective that widens as it turns;
                                          squash 0.3–0.45 looks like a tilted plane, tilt rotates it

Shape and colour:
  --width A:B[:power]      width at start:end (px at 1024); power >1 keeps it thin longer (default 1)
  --colors "#hex@0,#hex@0.6,#hex@1"   colour stops along the path (opaque; fade by colour, not alpha)
  --taper A:B              round-ish taper: fraction of length over which the start/end narrow to 0
  --side front|back|all    spiral only: front = the half nearer the viewer (draw after the body it
                           orbits), back = the far half (draw before it). Default all
  --samples N              resolution (default 360)
  --id NAME                id of the emitted <g> (default ribbon)
  --core "#hex:width:from" also emit a centreline <path> (e.g. a hot white core) from t=from to 1

Example — the rising orbit used for the Orbit app (draw back, then the sphere, then front):
  python3 ribbon.py --spiral 486,584,196,380,1.75,0.4,-24,90 --width 7:56:1.15 \\
      --colors "#4e28aa@0,#7c54e2@0.3,#ba96ff@0.55,#ecd2ff@0.84,#ffd68a@0.92,#ffc454@1" --side back
Prints SVG to stdout. Pure stdlib.
"""
import math
import re
import sys


def die(msg):
    print(f"ribbon.py: {msg}", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------- centrelines
def parse_path(d):
    toks = re.findall(r"[MLCQZmlcqz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    if any(t.islower() for t in toks if t.isalpha()):
        die("--path supports absolute commands only (M L C Q Z)")
    segs, i, cur, start, cmd = [], 0, None, None, None
    num = lambda: float(toks[i])  # noqa: E731
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]; i += 1
            if cmd == "Z" and cur and start:
                segs.append(("L", cur, start)); cur = start
            continue
        if cmd == "M":
            cur = start = (float(toks[i]), float(toks[i + 1])); i += 2; cmd = "L"
        elif cmd == "L":
            p = (float(toks[i]), float(toks[i + 1])); segs.append(("L", cur, p)); cur = p; i += 2
        elif cmd == "Q":
            c, p = (float(toks[i]), float(toks[i + 1])), (float(toks[i + 2]), float(toks[i + 3]))
            segs.append(("Q", cur, c, p)); cur = p; i += 4
        elif cmd == "C":
            c1 = (float(toks[i]), float(toks[i + 1])); c2 = (float(toks[i + 2]), float(toks[i + 3]))
            p = (float(toks[i + 4]), float(toks[i + 5])); segs.append(("C", cur, c1, c2, p)); cur = p; i += 6
        else:
            die(f"unexpected token {toks[i]!r}")
    if not segs:
        die("--path has no drawable segments")
    return segs


def seg_point(s, t):
    u = 1 - t
    if s[0] == "L":
        (a, b) = s[1], s[2]
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    if s[0] == "Q":
        a, c, b = s[1], s[2], s[3]
        return (u * u * a[0] + 2 * u * t * c[0] + t * t * b[0], u * u * a[1] + 2 * u * t * c[1] + t * t * b[1])
    a, c1, c2, b = s[1], s[2], s[3], s[4]
    return (u ** 3 * a[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * b[0],
            u ** 3 * a[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * b[1])


def path_samples(segs, n):
    dense = []
    for s in segs:
        for k in range(64):
            dense.append(seg_point(s, k / 64))
    dense.append(seg_point(segs[-1], 1.0))
    acc = [0.0]
    for a, b in zip(dense, dense[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    total = acc[-1] or 1.0
    out, j = [], 0
    for i in range(n + 1):
        target = total * i / n
        while j < len(acc) - 2 and acc[j + 1] < target:
            j += 1
        span = (acc[j + 1] - acc[j]) or 1.0
        f = (target - acc[j]) / span
        a, b = dense[j], dense[j + 1]
        out.append(((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), i / n, None))
    return out


def spiral_samples(spec, n):
    v = [float(x) for x in spec.split(",")]
    if len(v) < 5:
        die("--spiral needs cx,cy,r0,r1,turns[,squash[,tilt_deg[,start_deg]]]")
    cx, cy, r0, r1, turns = v[:5]
    squash = v[5] if len(v) > 5 else 0.38
    tilt = math.radians(v[6] if len(v) > 6 else -20)
    start = math.radians(v[7] if len(v) > 7 else 90)
    ct, st = math.cos(tilt), math.sin(tilt)
    out = []
    for i in range(n + 1):
        t = i / n
        th = start + t * turns * 2 * math.pi
        r = r0 + (r1 - r0) * t
        x, y = r * math.cos(th), r * math.sin(th) * squash
        out.append(((cx + x * ct - y * st, cy + x * st + y * ct), t, math.sin(th) > 0))
    return out


# ---------------------------------------------------------------- styling
def parse_colors(spec):
    stops = []
    for part in spec.split(","):
        part = part.strip()
        if "@" not in part:
            die(f"colour stop {part!r} needs @position, e.g. #ffcc00@0.8")
        c, pos = part.split("@")
        c = c.lstrip("#")
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        if not re.fullmatch(r"[0-9a-fA-F]{6}", c):
            die(f"bad colour {part!r}")
        stops.append((float(pos), tuple(int(c[k:k + 2], 16) for k in (0, 2, 4))))
    return sorted(stops)


def colour_at(stops, t):
    if t <= stops[0][0]:
        return stops[0][1]
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            f = (t - t0) / ((t1 - t0) or 1)
            return tuple(round(a + (b - a) * f) for a, b in zip(c0, c1))
    return stops[-1][1]


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    o = {"path": None, "spiral": None, "width": "8:40", "colors": "#ffffff@0,#ffffff@1", "taper": None,
         "side": "all", "samples": 360, "id": "ribbon", "core": None}
    i = 0
    while i < len(argv):
        k = argv[i]
        if not k.startswith("--") or k[2:] not in o:
            die(f"unknown option {k}")
        if i + 1 >= len(argv):
            die(f"{k} needs a value")
        o[k[2:]] = argv[i + 1]; i += 2
    if bool(o["path"]) == bool(o["spiral"]):
        die("give exactly one of --path or --spiral")
    n = int(o["samples"])
    samples = path_samples(parse_path(o["path"]), n) if o["path"] else spiral_samples(o["spiral"], n)

    w = o["width"].split(":")
    w0, w1 = float(w[0]), float(w[1])
    pw = float(w[2]) if len(w) > 2 else 1.0
    ta, tb = (float(x) for x in o["taper"].split(":")) if o["taper"] else (0.0, 0.0)

    def width(t):
        base = w0 + (w1 - w0) * (t ** pw)
        if ta and t < ta:
            base *= math.sin(math.pi / 2 * t / ta) ** 0.6
        if tb and t > 1 - tb:
            base *= math.sin(math.pi / 2 * (1 - t) / tb) ** 0.6
        return max(base, 0.4)

    stops = parse_colors(o["colors"])

    def normal(k):
        a = samples[max(0, k - 1)][0]
        b = samples[min(n, k + 1)][0]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        return (-dy / L, dx / L)

    out = [f'<g id="{o["id"]}">']
    step = 2
    for k0 in range(0, n, step):
        k1 = min(n, k0 + step + 1)
        mid = samples[(k0 + k1) // 2]
        if o["side"] != "all":
            if mid[2] is None:
                die("--side only applies to --spiral")
            if (o["side"] == "front") != mid[2]:
                continue
        left, right = [], []
        for k in range(k0, k1 + 1):
            (x, y), t, _ = samples[k]
            nx, ny = normal(k)
            h = width(t) / 2
            left.append((x + nx * h, y + ny * h))
            right.append((x - nx * h, y - ny * h))
        pts = left + right[::-1]
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"
        out.append(f'  <path d="{d}" fill="#%02x%02x%02x"/>' % colour_at(stops, mid[1]))
    out.append("</g>")

    if o["core"]:
        col, cw, frm = o["core"].split(":")
        keep = [t >= float(frm) and (o["side"] == "all" or front == (o["side"] == "front")) for _, t, front in samples]
        runs, cur = [], []
        for (p, _, _), k in zip(samples, keep):   # contiguous runs only — never bridge a gap
            if k:
                cur.append(p)
            elif cur:
                runs.append(cur); cur = []
        if cur:
            runs.append(cur)
        d = " ".join("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in r) for r in runs if len(r) > 1)
        if d:
            out.append(f'<path id="{o["id"]}-core" d="{d}" fill="none" stroke="{col}" stroke-width="{cw}" stroke-linecap="round"/>')
    end = samples[-1][0]
    out.append(f"<!-- ribbon end at ({end[0]:.1f}, {end[1]:.1f}) — put the head/body there -->")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
