# -*- coding: utf-8 -*-
"""Favicons: purpose-built art plus a dependency-free rasteriser.

The site icon cannot simply be the mark shrunk down. Two things break:

  * The mark is a thin-stroked line drawing. Below about 48px the stroke
    falls under one pixel and antialiases away to almost nothing -- the
    16px favicon this replaces had four distinct byte values in the whole
    image, i.e. it was blank.
  * It is drawn in ink on a transparent ground, so on a dark browser tab
    bar there is nothing to see even when the strokes do survive.

So the favicon gets a solid ink tile (legible against light and dark
chrome alike), paper-coloured planes at a weight chosen per size, and the
signal diamond. Plane count drops with the canvas: four planes cannot
resolve in sixteen pixels, so small sizes show fewer, heavier ones.

Rasterising is done here rather than by qlmanage, which pads non-square
input and silently produced a tiny off-centre mark last time. Everything
below is scanline coverage with supersampling and a hand-rolled PNG
writer, so the output is exact and reproducible on any machine.
"""

import io, os, struct, zlib

RATIO  = 1.4142136          # matches brand/generate.py
INK    = (0x2A, 0x37, 0x3D)
PAPER  = (0xFA, 0xFA, 0xFA)
SIGNAL = (0xDB, 0x54, 0x61)

# size -> (plane count, stroke as a fraction of the icon, art width fraction)
PLAN = {
    16:  (2, 0.070, 0.78),   # two planes is the most that resolves here
    32:  (2, 0.075, 0.82),
    48:  (3, 0.060, 0.80),
    64:  (4, 0.050, 0.80),
    180: (4, 0.040, 0.74),   # apple-touch
    512: (4, 0.038, 0.74),
}


def geometry(size, planes, stroke_frac, art_frac):
    """Plane centres and radii, in pixels, centred in a `size` square."""
    hw = size * art_frac / 2.0
    hh = hw / RATIO
    # The mark's own spacing, but never tighter than the stroke can survive:
    # below about twice the stroke width the dark line between two planes
    # closes up and the stack reads as one solid lozenge.
    gap = max(0.2259 * hh, size * stroke_frac * 2.0)
    span = gap * (planes - 1)
    cx, cy = size / 2.0, size / 2.0
    # cys[0] is the bottom plane (drawn first, furthest back).
    cys = [cy + span / 2.0 - gap * i for i in range(planes)]
    return cx, cys, hw, hh, size * stroke_frac


def _ring(hw, hh, w):
    """A diamond outline of width w, as (outer, inner) half-extents.

    Offsetting the edge x/hw + y/hh = 1 outward by d scales the diamond,
    because the offset of a diamond is a similar diamond. The perpendicular
    distance from the centre to that edge is hw*hh/hypot(hw,hh).
    """
    d = (hw * hh) / ((hw * hw + hh * hh) ** 0.5)
    s_out = (d + w / 2.0) / d
    s_in = max(0.0, (d - w / 2.0) / d)
    return (hw * s_out, hh * s_out), (hw * s_in, hh * s_in)


def render(size, ss=8):
    """Returns `size`x`size` RGB rows. Drawn at ss x then box-filtered."""
    planes, stroke_frac, art_frac = PLAN[size]
    S = size * ss
    cx, cys, hw, hh, sw = geometry(S, planes, stroke_frac, art_frac)
    (ohw, ohh), (ihw, ihh) = _ring(hw, hh, sw)

    buf = bytearray()
    for c in INK:
        buf.append(c)
    px = bytearray(INK * (S * S))

    def diamond(x, y, cyy, a, b):
        if b <= 0:
            return False
        return abs(x - cx) / a + abs(y - cyy) / b <= 1.0

    def fill(cyy, a, b, colour):
        if b <= 0:
            return
        y0, y1 = max(0, int(cyy - b)), min(S - 1, int(cyy + b) + 1)
        for y in range(y0, y1 + 1):
            t = 1.0 - abs(y + 0.5 - cyy) / b
            if t <= 0:
                continue
            half = a * t
            x0, x1 = max(0, int(cx - half)), min(S - 1, int(cx + half) + 1)
            for x in range(x0, x1 + 1):
                if abs(x + 0.5 - cx) / a + abs(y + 0.5 - cyy) / b <= 1.0:
                    o = (y * S + x) * 3
                    px[o:o + 3] = bytes(bytearray(colour))

    # Back to front: the plane nearest the viewer sits highest and is drawn
    # last, so it occludes the ones behind it.
    for cyy in cys:
        fill(cyy, ohw, ohh, PAPER)     # the outline
        fill(cyy, ihw, ihh, INK)       # knock its middle back out
    # The signal sits on the top plane.
    fill(cys[-1], hw * 0.282, hh * 0.282, SIGNAL)

    # Box downsample.
    out = []
    n = float(ss * ss)
    for y in range(size):
        row = bytearray()
        for x in range(size):
            r = g = b = 0
            for dy in range(ss):
                base = ((y * ss + dy) * S + x * ss) * 3
                for dx in range(ss):
                    o = base + dx * 3
                    r += px[o]; g += px[o + 1]; b += px[o + 2]
            row += bytes(bytearray((int(r / n + .5), int(g / n + .5), int(b / n + .5))))
        out.append(bytes(row))
    return out


def write_png(path, rows):
    raw = b''.join(b'\x00' + r for r in rows)
    w = len(rows[0]) // 3
    h = len(rows)

    def chunk(typ, body):
        return (struct.pack('>I', len(body)) + typ + body
                + struct.pack('>I', zlib.crc32(typ + body) & 0xffffffff))

    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    io.open(path, 'wb').write(png)
    return len(png)


def svg(size=512):
    """The same art as a vector, for anything that wants to scale it."""
    planes, stroke_frac, art_frac = PLAN[size]
    cx, cys, hw, hh, sw = geometry(float(size), planes, stroke_frac, art_frac)

    def pts(cyy, a, b):
        return "%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" % (
            cx, cyy - b, cx + a, cyy, cx, cyy + b, cx - a, cyy)

    hexs = lambda c: "#%02X%02X%02X" % c
    body = ['  <rect width="%d" height="%d" fill="%s"/>' % (size, size, hexs(INK))]
    for cyy in cys:
        body.append('  <polygon points="%s" fill="none" stroke="%s" stroke-width="%.2f" '
                    'stroke-linejoin="round"/>' % (pts(cyy, hw, hh), hexs(PAPER), sw))
    body.append('  <polygon points="%s" fill="%s"/>'
                % (pts(cys[-1], hw * .282, hh * .282), hexs(SIGNAL)))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
            'height="%d" role="img" aria-label="Tessaract Systems">\n  <title>Tessaract '
            'Systems</title>\n%s\n</svg>\n' % (size, size, size, size, "\n".join(body)))


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    targets = [(16, 'assets/favicon-16.png'), (32, 'assets/favicon-32.png'),
               (48, 'assets/favicon-48.png'), (64, 'assets/favicon-64.png'),
               (180, 'assets/apple-touch-icon.png')]
    for size, rel in targets:
        p = os.path.join(root, rel)
        n = write_png(p, render(size))
        print("%-32s %3dpx  %5d bytes" % (rel, size, n))
    p = os.path.join(here, 'favicon.svg')
    io.open(p, 'w', encoding='utf-8').write(svg(512))
    print("%-32s vector" % 'brand/favicon.svg')
