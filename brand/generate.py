# -*- coding: utf-8 -*-
"""Tessaract Systems brand generator.

Everything in the mark is one isometric construction, so the whole thing is
driven by two numbers:

    RATIO  plane width : height. This IS the camera elevation.
           2.000  = 30.0 deg   "game isometric" / 2:1 dimetric
           1.732  = 35.264 deg TRUE isometric -- a square tile reads as square
           1.000  = 45 deg     flat-on diamond

    GAP    vertical distance between plane centres, in user units.

The art was originally cut at RATIO 2.0, which made each plane read as a
rectangle rather than a square -- the planes looked squashed. Everything
below is expressed as a fraction of the plane half-height, so changing RATIO
rescales the motifs with it and nothing drifts.

Usage:  python3 brand/generate.py [--ratio R] [--gap G] [--out DIR]
"""
import argparse, io, math, os, re

INK, SIGNAL, PAPER = "#2A373D", "#DB5461", "#FAFAFA"
CX = 200.0          # horizontal centre of the stack
HW = 170.0          # plane half-width -- fixed, the mark's width never changes
OLD_HH = 85.0       # half-height the original motifs were cut against
PAD = 14.0          # clear space inside the viewBox


def n(v):
    """Trim float noise so the SVG stays readable."""
    return ("%.2f" % v).rstrip("0").rstrip(".")


class Geo(object):
    def __init__(self, ratio, gap, planes=4):
        self.ratio = float(ratio)
        self.hh = HW / self.ratio
        self.k = self.hh / OLD_HH          # motif rescale factor
        self.gap = float(gap)
        # Plane centres, bottom first, centred on y=305 like the original.
        span = self.gap * (planes - 1)
        self.cys = [305.0 + span / 2.0 - self.gap * i for i in range(planes)]

    # -- primitives ---------------------------------------------------
    def dia(self, cx, cy, hw):
        """A diamond: the isometric projection of a square."""
        hh = hw / self.ratio
        return "%s,%s %s,%s %s,%s %s,%s" % (
            n(cx), n(cy - hh), n(cx + hw), n(cy),
            n(cx), n(cy + hh), n(cx - hw), n(cy))

    def plane(self, cy):
        return self.dia(CX, cy, HW)

    def ly(self, cy, dy_old):
        """A motif's y, given its offset in the original 2:1 artwork."""
        return cy + dy_old * self.k

    def ell(self, cx, cy, rx, extra=""):
        return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s"%s/>' % (
            n(cx), n(cy), n(rx), n(rx / self.ratio), extra)

    # -- occlusion ----------------------------------------------------
    def masks(self, prefix, bleed):
        """One mask per plane, knocking out every plane above it.

        The bleed is a fat stroke on the knockout so layers stay visibly
        separate instead of butting together.
        """
        out = []
        for i in range(len(self.cys) - 1):
            cuts = "".join(
                '\n        <polygon points="%s" fill="#000" stroke="#000" '
                'stroke-width="%s" stroke-linejoin="round"/>'
                % (self.plane(c), n(bleed)) for c in self.cys[i + 1:])
            out.append(
                '    <mask id="%s%d" maskUnits="userSpaceOnUse" x="0" y="0" '
                'width="760" height="610">\n'
                '        <rect x="0" y="0" width="760" height="610" fill="#fff"/>%s\n'
                '    </mask>' % (prefix, i, cuts))
        return "\n".join(out)

    def viewbox(self, stroke):
        half = stroke / 2.0
        top = self.cys[-1] - self.hh - half - PAD
        bot = self.cys[0] + self.hh + half + PAD
        return (CX - HW - PAD, top, 2 * (HW + PAD), bot - top)


def svg(geo, body, defs, stroke, vb=None):
    x, y, w, h = vb or geo.viewbox(stroke)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s" '
            'width="%s" height="%s" role="img" aria-label="Tessaract Systems">\n'
            '  <title>Tessaract Systems</title>\n'
            '  <defs>\n%s\n  </defs>\n%s\n</svg>\n'
            % (n(x), n(y), n(w), n(h), n(w), n(h), defs, body))


# ---------------------------------------------------------------- marks
def mark_detailed(geo, ink, paper, stroke=4.0, bleed=22.0):
    """The full mark: four planes, each carrying its own motif.

    bottom -> top:  raw grid, network, focus rings, resolved nodes.
    """
    p = geo.cys
    g = []

    # 0: raw data -- a cross-hatch, lines running with both plane edges.
    hatch = []
    for a in (-0.5, 0.0, 0.5):
        x1, y1 = CX + (a - 1) / 2 * HW, geo.ly(p[0], (a + 1) / 2 * OLD_HH)
        x2, y2 = CX + (a + 1) / 2 * HW, geo.ly(p[0], (a - 1) / 2 * OLD_HH)
        hatch.append("M%s,%s L%s,%s" % (n(x1), n(y1), n(x2), n(y2)))
    for b in (0.5, 0.0, -0.5):
        x1, y1 = CX + (-1 + b) / 2 * HW, geo.ly(p[0], (-1 - b) / 2 * OLD_HH)
        x2, y2 = CX + (1 + b) / 2 * HW, geo.ly(p[0], (1 - b) / 2 * OLD_HH)
        hatch.append("M%s,%s L%s,%s" % (n(x1), n(y1), n(x2), n(y2)))
    g.append('    <g mask="url(#m0)">\n'
             '      <polygon points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>\n'
             '      <path d="%s" fill="none" stroke="%s" stroke-width="1.5" stroke-linecap="round" opacity=".5"/>\n'
             '    </g>' % (geo.plane(p[0]), ink, n(stroke), " ".join(hatch), ink))

    # 1: the network -- deliberately irregular, this is messy real data.
    hub = (195.8, 2.1)
    nodes = [(191.5, -42.5), (289.2, -2.1), (106.5, 4.2), (204.2, 44.6)]
    hx, hy = hub[0], geo.ly(p[1], hub[1])
    nd = [(x, geo.ly(p[1], dy)) for x, dy in nodes]
    lines = ["".join('      <path d="M%s,%s L%s,%s" fill="none" stroke="%s" '
                     'stroke-width="2" opacity=".75"/>\n'
                     % (n(hx), n(hy), n(x), n(y), ink)) for x, y in nd]
    lines.append('      <path d="M%s,%s L%s,%s M%s,%s L%s,%s" fill="none" '
                 'stroke="%s" stroke-width="2" opacity=".75"/>\n'
                 % (n(nd[0][0]), n(nd[0][1]), n(nd[1][0]), n(nd[1][1]),
                    n(nd[3][0]), n(nd[3][1]), n(nd[2][0]), n(nd[2][1]), ink))
    for x, y in nd:
        lines.append("      %s\n" % geo.ell(
            x, y, 10.8, ' fill="%s" stroke="%s" stroke-width="2"' % (paper, ink)))
    lines.append("      %s\n" % geo.ell(
        hx, hy, 15.6, ' fill="%s" stroke="%s" stroke-width="2"' % (ink, ink)))
    g.append('    <g mask="url(#m1)">\n'
             '      <polygon points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>\n'
             '%s    </g>' % (geo.plane(p[1]), ink, n(stroke), "".join(lines)))

    # 2: focus -- concentric rings closing on one point.
    g.append('    <g mask="url(#m2)">\n'
             '      <polygon points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>\n'
             '      <polygon points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="7 8" opacity=".75"/>\n'
             '      <polygon points="%s" fill="none" stroke="%s" stroke-width="2" opacity=".75"/>\n'
             '      %s\n'
             '    </g>' % (geo.plane(p[2]), ink, n(stroke),
                           geo.dia(CX, p[2], 115.6), ink,
                           geo.dia(CX, p[2], 54.4), ink,
                           geo.ell(CX, p[2], 9.6, ' fill="%s"' % SIGNAL)))

    # 3: resolved -- three clean nodes and the signal.
    top = p[3]
    g.append('    <g>\n'
             '      <polygon points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>\n'
             '      <polygon points="%s" fill="none" stroke="%s" stroke-width="1.5" opacity=".5"/>\n'
             '      <polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>\n'
             '      <polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>\n'
             '      <polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>\n'
             '      <polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>\n'
             '    </g>' % (
                 geo.plane(top), ink, n(stroke),
                 geo.dia(CX, top, 76.5), ink,
                 geo.dia(CX, geo.ly(top, -38.25), 28.9), paper, ink,
                 geo.dia(CX + 76.5, top, 28.9), paper, ink,
                 geo.dia(CX - 76.5, top, 28.9), paper, ink,
                 geo.dia(CX, geo.ly(top, 38.25), 28.9), SIGNAL, SIGNAL))

    return svg(geo, "\n".join(g), geo.masks("m", bleed), stroke)


def mark_ui(geo, ink, paper, stroke=9.0, bleed=30.0):
    """UI weight: same composition, strokes that land on whole pixels at 50px."""
    p = geo.cys
    b = []
    for i, cy in enumerate(p):
        att = ' mask="url(#um%d)"' % i if i < len(p) - 1 else ""
        b.append('  <polygon%s points="%s" fill="none" stroke="%s" '
                 'stroke-width="%s" stroke-linejoin="round"/>'
                 % (att, geo.plane(cy), ink, n(stroke)))
    top = p[-1]
    b.append('  <polygon points="%s" fill="none" stroke="%s" stroke-width="4" opacity=".55"/>'
             % (geo.dia(CX, top, 76.5), ink))
    for cx, dy in [(CX, -38.2), (CX + 76.5, 0.0), (CX - 76.5, 0.0)]:
        b.append('  <polygon points="%s" fill="%s" stroke="%s" stroke-width="6" '
                 'stroke-linejoin="round"/>'
                 % (geo.dia(cx, geo.ly(top, dy), 34.0), paper, ink))
    b.append('  <polygon points="%s" fill="%s"/>'
             % (geo.dia(CX, geo.ly(top, 38.2), 36.0), SIGNAL))
    return svg(geo, "\n".join(b), geo.masks("um", bleed), stroke)


def mark_simple(geo, ink, stroke=9.0, bleed=26.0):
    """For favicons and anything under ~48px: planes and the signal, nothing else."""
    p = geo.cys
    b = []
    for i, cy in enumerate(p):
        att = ' mask="url(#s%d)"' % i if i < len(p) - 1 else ""
        b.append('  <polygon%s points="%s" fill="none" stroke="%s" '
                 'stroke-width="%s" stroke-linejoin="round"/>'
                 % (att, geo.plane(cy), ink, n(stroke)))
    b.append('  <polygon points="%s" fill="%s"/>' % (geo.dia(CX, p[-1], 48.0), SIGNAL))
    return svg(geo, "\n".join(b), geo.masks("s", bleed), stroke)


# ---------------------------------------------------------------- lockup
WORDMARK_BASE_H = 993.288      # height of the original lockup
MARK_SCALE      = 2.03804      # mark width 750 inside a 2000-wide lockup
MARK_X          = 625.0
OLD_MARK_H      = 550.264      # 270 * MARK_SCALE, what the wordmark was set to


def _wordmark(ink):
    """The outlined TESSARACT / SYSTEMS paths, recoloured."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_wordmark.svg")
    s = io.open(path, encoding="utf-8").read()
    s = s[s.index(">", s.index("<svg")) + 1:s.rindex("</svg>")]
    s = "\n".join(l for l in s.split("\n") if "<!--" not in l and "-->" not in l)
    return s.replace("#2A373D", ink).strip()


def logo(geo, ink, paper, stroke=4.0, bleed=22.0):
    """Mark over wordmark. The wordmark shifts down by however much taller
    the mark got, so the optical gap between them is unchanged."""
    m = mark_detailed(geo, ink, paper, stroke, bleed)
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', m).group(1).split()]
    defs = re.search(r"<defs>(.*?)</defs>", m, re.S).group(1)
    inner = m[m.index("</defs>") + 7:m.rindex("</svg>")]
    shift = vb[3] * MARK_SCALE - OLD_MARK_H
    h = WORDMARK_BASE_H + shift
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 %s" '
            'width="2000" height="%s" role="img" aria-label="Tessaract Systems">\n'
            '  <title>Tessaract Systems</title>\n'
            '  <defs>%s</defs>\n'
            '  <g transform="translate(%s,0) scale(%s) translate(%s,%s)">%s</g>\n'
            '  <g transform="translate(0,%s)">\n%s\n  </g>\n</svg>\n'
            % (n(h), n(h), defs, n(MARK_X), MARK_SCALE, n(-vb[0]), n(-vb[1]),
               inner, n(shift), _wordmark(ink)))


# ---------------------------------------------------------------- social
def _place(art, box_w, box_h, target_w, cx, cy, uid):
    """Drop a generated mark into a canvas, scaled to target_w and centred."""
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', art).group(1).split()]
    defs = re.search(r"<defs>(.*?)</defs>", art, re.S).group(1)
    inner = art[art.index("</defs>") + 7:art.rindex("</svg>")]
    for mid in sorted(set(re.findall(r'id="(\w+)"', defs)), key=len, reverse=True):
        inner = inner.replace("url(#%s)" % mid, "url(#%s_%s)" % (uid, mid))
        defs = defs.replace('id="%s"' % mid, 'id="%s_%s"' % (uid, mid))
    s = target_w / vb[2]
    return defs, ('<g transform="translate(%s,%s) scale(%s) translate(%s,%s)">%s</g>'
                  % (n(cx - target_w / 2.0), n(cy - vb[3] * s / 2.0), s,
                     n(-vb[0]), n(-vb[1]), inner))


def avatar(geo, size, ink, bg, frac=0.62, simple=False, uid="av"):
    """Square profile picture or app icon.

    Platforms crop avatars to a circle and show them small, so this uses a
    knockout-free weight and leaves room inside the inscribed circle. bg=None
    gives a transparent icon; the mark's own knockouts then need a colour to
    knock out to, which is what `plate` carries.
    """
    plate = bg or PAPER
    art = mark_simple(geo, ink) if simple else mark_ui(geo, ink, plate)
    defs, g = _place(art, size, size, size * frac, size / 2.0, size / 2.0, uid)
    rect = ('  <rect width="%d" height="%d" fill="%s"/>\n' % (size, size, bg)) if bg else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
            'height="%d" role="img" aria-label="Tessaract Systems">\n'
            '  <title>Tessaract Systems</title>\n  <defs>%s</defs>\n%s%s\n</svg>\n'
            % (size, size, size, size, defs, rect, g))


# Measured bbox of the outlined wordmark, in the 2000-wide lockup's own space.
WM = {"w": 2000.0, "top": 699.26, "bot": 990.92}
WM_H = WM["bot"] - WM["top"]          # 291.66
WM_ASPECT = WM["w"] / WM_H            # 6.858


def wordmark_block(ink, x, y, h):
    """TESSARACT over SYSTEMS with its rules -- the real outlined lockup
    wordmark, its bounding box placed top-left at (x, y) and scaled to height h."""
    k = h / WM_H
    return ('<g transform="translate(%s,%s) scale(%s) translate(%s,%s)">%s</g>'
            % (n(x), n(y), n(k), n(-WM["w"] / 2.0 * 0), n(-WM["top"]), _wordmark(ink)))


def banner(geo, w, h, ink, bg, sub=None, align="center", uid="bn", shrink=1.0):
    """A horizontal cover: mark, then the wordmark lockup beside it.

    Laid out in abstract units (wordmark height = 1) and then scaled to fit,
    so the same code gives a 1128x191 LinkedIn strip and a 1500x500 header
    without either one overflowing.
    """
    art = mark_detailed(geo, ink, bg)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', art).group(1).split()]
    U_MARK_H = 1.55
    U_MARK_W = U_MARK_H * vb[2] / vb[3]
    U_GAP = 0.45
    U_SUB = 0.62 if sub else 0.0            # tagline band under the wordmark
    U_W = U_MARK_W + U_GAP + WM_ASPECT
    U_H = max(U_MARK_H, 1.0 + U_SUB)

    pad = h * 0.11
    s = min((w - 2 * pad) / U_W, (h - 2 * pad) / U_H) * shrink

    bw, bh = U_W * s, U_H * s
    bx = {"center": (w - bw) / 2.0, "left": pad,
          "right": w - pad - bw}[align]
    cy = h / 2.0

    mark_h = U_MARK_H * s
    mark_w = U_MARK_W * s
    defs, g = _place(art, w, h, mark_w, bx + mark_w / 2.0, cy, uid)

    wm_h = 1.0 * s
    wm_x = bx + mark_w + U_GAP * s
    wm_y = cy - (wm_h + U_SUB * s) / 2.0
    parts = [g, wordmark_block(ink, wm_x, wm_y, wm_h)]

    if sub:
        fs = 0.30 * s
        parts.append('<text x="%s" y="%s" font-family="Instrument Sans, Helvetica Neue, '
                     'Helvetica, Arial, sans-serif" font-size="%s" letter-spacing="%s" '
                     'fill="%s" opacity=".8">%s</text>'
                     % (n(wm_x + 2), n(wm_y + wm_h + U_SUB * s * 0.78), n(fs),
                        n(fs * 0.04), ink, sub))

    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
            'height="%d" role="img" aria-label="Tessaract Systems">\n'
            '  <title>Tessaract Systems</title>\n  <defs>%s</defs>\n'
            '  <rect width="%d" height="%d" fill="%s"/>\n  %s\n</svg>\n'
            % (w, h, w, h, defs, w, h, bg, "\n  ".join(parts)))

# ---------------------------------------------------------------- site art
HF_OPEN_GAP = 130.0     # plane spacing while the hero stack is open
HF_PAD = 34.0           # viewBox padding around the CLOSED stack


def markfold(geo_open, geo_closed):
    """The animated hero stack. Drawn open; CSS translates each layer closed.

    The translateY values in the stylesheet are closed_centre - open_centre,
    so as long as both gaps are unchanged the animation needs no edits --
    only the bloom's transform-origin, which this returns alongside.
    """
    op, cl = geo_open.cys, geo_closed.cys
    hh = geo_open.hh
    mid_top, mid_bot = op[-1] - hh, op[0] + hh
    side_top, side_bot = op[-1], op[0]

    def motifs(i):
        cy = op[i]
        if i == 0:
            d = []
            for a in (-0.5, 0.0, 0.5):
                d.append("M%s,%s L%s,%s" % (
                    n(CX + (a - 1) / 2 * HW), n(geo_open.ly(cy, (a + 1) / 2 * OLD_HH)),
                    n(CX + (a + 1) / 2 * HW), n(geo_open.ly(cy, (a - 1) / 2 * OLD_HH))))
            for b in (0.5, 0.0, -0.5):
                d.append("M%s,%s L%s,%s" % (
                    n(CX + (-1 + b) / 2 * HW), n(geo_open.ly(cy, (-1 - b) / 2 * OLD_HH)),
                    n(CX + (1 + b) / 2 * HW), n(geo_open.ly(cy, (1 - b) / 2 * OLD_HH))))
            return ('              <path d="%s" fill="none" stroke="currentColor" '
                    'stroke-width="1.5" stroke-linecap="round" opacity=".5"/>' % " ".join(d))
        if i == 1:
            hx, hy = 195.8, geo_open.ly(cy, 2.1)
            nd = [(191.5, geo_open.ly(cy, -42.5)), (289.2, geo_open.ly(cy, -2.1)),
                  (106.5, geo_open.ly(cy, 4.2)), (204.2, geo_open.ly(cy, 44.6))]
            o = ['              <path d="M%s,%s L%s,%s" fill="none" stroke="currentColor" '
                 'stroke-width="2" opacity=".75"/>' % (n(hx), n(hy), n(x), n(y)) for x, y in nd]
            o.append('              <path d="M%s,%s L%s,%s M%s,%s L%s,%s" fill="none" '
                     'stroke="currentColor" stroke-width="2" opacity=".75"/>'
                     % (n(nd[0][0]), n(nd[0][1]), n(nd[1][0]), n(nd[1][1]),
                        n(nd[3][0]), n(nd[3][1]), n(nd[2][0]), n(nd[2][1])))
            for x, y in nd:
                o.append("              " + geo_open.ell(
                    x, y, 10.8, ' fill="%s" stroke="currentColor" stroke-width="2"' % PAPER))
            o.append("              " + geo_open.ell(
                hx, hy, 15.6, ' fill="currentColor" stroke="currentColor" stroke-width="2"'))
            return "\n".join(o)
        if i == 2:
            return ('              <polygon points="%s" fill="none" stroke="currentColor" '
                    'stroke-width="2" stroke-dasharray="7 8" opacity=".75"/>\n'
                    '              <polygon points="%s" fill="none" stroke="currentColor" '
                    'stroke-width="2" opacity=".75"/>\n              %s'
                    % (geo_open.dia(CX, cy, 115.6), geo_open.dia(CX, cy, 54.4),
                       geo_open.ell(CX, cy, 9.6, ' fill="%s"' % SIGNAL)))
        bloom_y = geo_open.ly(cy, 38.2)
        return ('              <polygon points="%s" fill="none" stroke="currentColor" '
                'stroke-width="1.5" opacity=".5"/>\n'
                '              <polygon points="%s" fill="%s" stroke="currentColor" stroke-width="2"/>\n'
                '              <polygon points="%s" fill="%s" stroke="currentColor" stroke-width="2"/>\n'
                '              <polygon points="%s" fill="%s" stroke="currentColor" stroke-width="2"/>\n'
                '              <ellipse class="hf-bloom" cx="%s" cy="%s" rx="40" ry="%s" fill="%s" filter="url(#hf-bloom)"/>\n'
                '              <polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>'
                % (geo_open.dia(CX, cy, 76.5),
                   geo_open.dia(CX, geo_open.ly(cy, -38.25), 28.9), PAPER,
                   geo_open.dia(CX + 76.5, cy, 28.9), PAPER,
                   geo_open.dia(CX - 76.5, cy, 28.9), PAPER,
                   n(CX), n(bloom_y), n(40.0 / geo_open.ratio), SIGNAL,
                   geo_open.dia(CX, bloom_y, 28.9), SIGNAL, SIGNAL))

    layers = []
    for i in range(4):
        layers.append('            <g class="hf-layer hf-%d">\n'
                      '              <polygon class="plane-halo" points="%s"/>\n'
                      '              <polygon class="plane" points="%s"/>\n%s\n'
                      '            </g>' % (i, geo_open.plane(op[i]), geo_open.plane(op[i]), motifs(i)))

    vb_top = cl[-1] - geo_closed.hh - HF_PAD
    vb_h = (cl[0] + geo_closed.hh + HF_PAD) - vb_top
    svg = ('<svg class="markfold" viewBox="%s %s 368 %s" role="presentation">\n'
           '            <g class="hf-scale">\n'
           '            <defs>\n'
           '              <linearGradient id="hf-edge" gradientUnits="userSpaceOnUse" x1="0" y1="%s" x2="0" y2="%s">\n'
           '                <stop offset="0" stop-color="%s" stop-opacity="0"/>\n'
           '                <stop offset=".22" stop-color="%s" stop-opacity=".45"/>\n'
           '                <stop offset=".78" stop-color="%s" stop-opacity=".45"/>\n'
           '                <stop offset="1" stop-color="%s" stop-opacity="0"/>\n'
           '              </linearGradient>\n'
           '              <linearGradient id="hf-edge-mid" gradientUnits="userSpaceOnUse" x1="0" y1="%s" x2="0" y2="%s">\n'
           '                <stop offset="0" stop-color="%s" stop-opacity="0"/>\n'
           '                <stop offset=".26" stop-color="%s" stop-opacity=".4"/>\n'
           '                <stop offset=".74" stop-color="%s" stop-opacity=".4"/>\n'
           '                <stop offset="1" stop-color="%s" stop-opacity="0"/>\n'
           '              </linearGradient>\n'
           '              <filter id="hf-bloom" x="-120%%" y="-300%%" width="340%%" height="700%%">\n'
           '                <feGaussianBlur stdDeviation="11"/>\n'
           '              </filter>\n'
           '            </defs>\n'
           '            <g class="hf-edges">\n'
           '              <line x1="30" y1="%s" x2="30" y2="%s" stroke="url(#hf-edge)" stroke-width="2"/>\n'
           '              <line x1="370" y1="%s" x2="370" y2="%s" stroke="url(#hf-edge)" stroke-width="2"/>\n'
           '              <line x1="200" y1="%s" x2="200" y2="%s" stroke="url(#hf-edge-mid)" stroke-width="2"/>\n'
           '            </g>\n%s\n            </g>\n          </svg>'
           % (n(CX - HW - HF_PAD), n(vb_top), n(vb_h),
              n(side_top), n(side_bot), SIGNAL, SIGNAL, SIGNAL, SIGNAL,
              n(mid_top), n(mid_bot), SIGNAL, SIGNAL, SIGNAL, SIGNAL,
              n(side_top), n(side_bot), n(side_top), n(side_bot),
              n(mid_top), n(mid_bot), "\n".join(layers)))
    return svg, geo_open.ly(op[-1], 38.2)


def svc_glyph(geo, kind):
    """A single plane carrying one division's motif, for the service cards."""
    cx, hw = 55.0, 50.0
    hh = hw / geo.ratio
    k = 1.0 / geo.ratio * 2.0          # old art was cut at 2:1
    cy = hh + 1.2 + 10.8               # keep the original optical padding
    box_h = 2 * cy
    out = ['<polygon points="%s" fill="none" stroke="currentColor" stroke-width="2.4" '
           'stroke-linejoin="round"/>' % geo.dia(cx, cy, hw)]
    if kind == "ai":
        out.append('<polygon points="%s" fill="none" stroke="currentColor" '
                   'stroke-width="1.2" opacity=".5"/>' % geo.dia(cx, cy, 22.0))
        for nx, dy in [(cx, -11.0), (cx + 22, 0.0), (cx - 22, 0.0)]:
            out.append('<polygon points="%s" fill="%s" stroke="currentColor" '
                       'stroke-width="1.6"/>' % (geo.dia(nx, cy + dy * k, 8.0), PAPER))
        out.append('<polygon points="%s" fill="%s"/>' % (geo.dia(cx, cy + 11 * k, 9.0), SIGNAL))
    elif kind == "data":
        for t in (-0.5, 0.0, 0.5):
            x = cx + hw * t * 0.62
            y = cy + hh * t * 0.62
            out.append('<path d="M%s,%s L%s,%s" stroke="currentColor" stroke-width="1.2" '
                       'opacity=".55" fill="none"/>'
                       % (n(x - hw * 0.4), n(y - hh * 0.4), n(x + hw * 0.4), n(y + hh * 0.4)))
            out.append('<path d="M%s,%s L%s,%s" stroke="currentColor" stroke-width="1.2" '
                       'opacity=".55" fill="none"/>'
                       % (n(x - hw * 0.4), n(y + hh * 0.4), n(x + hw * 0.4), n(y - hh * 0.4)))
    else:
        pts = [(cx, -13.0), (cx + 26, 1.0), (cx - 26, 1.0), (cx + 2, 13.0)]
        for px, dy in pts:
            out.append('<path d="M%s,%s L%s,%s" stroke="currentColor" stroke-width="1.3" '
                       'opacity=".6" fill="none"/>' % (n(cx), n(cy), n(px), n(cy + dy * k)))
        for px, dy in pts:
            out.append(geo.ell(px, cy + dy * k, 4.6,
                               ' fill="%s" stroke="currentColor" stroke-width="1.4"' % PAPER))
        out.append(geo.ell(cx, cy, 6.0, ' fill="%s"' % SIGNAL))
    return ('<svg class="svc-glyph" viewBox="0 0 110 %s" aria-hidden="true">%s</svg>'
            % (n(box_h), "".join(out)))


def header_mark(geo, stroke=9.0, bleed=30.0):
    """The inline header mark: UI weight, strokes inheriting colour."""
    art = mark_ui(geo, "currentColor", PAPER, stroke, bleed)
    vb = re.search(r'viewBox="([^"]+)"', art).group(1)
    defs = re.search(r"<defs>(.*?)</defs>", art, re.S).group(1)
    inner = art[art.index("</defs>") + 7:art.rindex("</svg>")]
    inner = re.sub(r"\s*\n\s*", "", inner)
    return ('<svg class="brand-mark" viewBox="%s" aria-hidden="true"><defs>%s</defs>%s</svg>'
            % (vb, re.sub(r"\s*\n\s*", "", defs), inner))



def build(ratio, gap, gap_simple):
    geo = Geo(ratio, gap)
    geo_s = Geo(ratio, gap_simple)
    out = {
        "tessaract-mark.svg":              mark_detailed(geo, INK, PAPER),
        "tessaract-mark-light.svg":        mark_detailed(geo, PAPER, INK),
        "tessaract-mark-ui.svg":           mark_ui(geo, INK, PAPER),
        "tessaract-mark-ui-light.svg":     mark_ui(geo, PAPER, INK),
        "tessaract-mark-simple.svg":       mark_simple(geo_s, INK),
        "tessaract-mark-simple-light.svg": mark_simple(geo_s, PAPER),
        "tessaract-logo.svg":              logo(geo, INK, PAPER),
        "tessaract-logo-light.svg":        logo(geo, PAPER, INK),
    }
    # Social. Avatars use the UI weight: profile pictures are shown small and
    # often cropped to a circle, so the detailed interior would turn to mush.
    tag = "Data &amp; AI engineering"
    out["social/avatar-light.svg"]  = avatar(geo, 1000, INK, PAPER, uid="a1")
    out["social/avatar-dark.svg"]   = avatar(geo, 1000, PAPER, INK, uid="a2")
    # Favicons: the simplified mark, transparent, a touch larger in frame
    # because at 16px every spare pixel of stroke counts.
    out["icon.svg"]       = avatar(geo_s, 512, INK, None, frac=.80, simple=True, uid="ic")
    out["icon-light.svg"] = avatar(geo_s, 512, PAPER, None, frac=.80, simple=True, uid="icl")
    out["apple-touch.svg"] = avatar(geo_s, 512, INK, PAPER, frac=.70, simple=True, uid="at")
    # LinkedIn drops the company logo badge over the cover's lower left, so
    # that corner is kept clear and the lockup sits right.
    out["social/linkedin-cover.svg"] = banner(geo, 1128, 191, INK, PAPER, tag,
                                              align="right", uid="li", shrink=.92)
    out["social/linkedin-cover-dark.svg"] = banner(geo, 1128, 191, PAPER, INK, tag,
                                                   align="right", uid="lid", shrink=.92)
    out["social/x-header.svg"] = banner(geo, 1500, 500, PAPER, INK, tag, uid="xh", shrink=.86)
    out["social/og-image.svg"] = banner(geo, 1200, 630, INK, PAPER, tag, uid="og", shrink=.88)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratio", type=float, default=math.sqrt(3))
    ap.add_argument("--gap", type=float, default=24.0)
    ap.add_argument("--gap-simple", type=float, default=36.0)
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    g = Geo(a.ratio, a.gap)
    print("ratio %.4f:1  elevation %.3f deg  half-height %.2f  gap %.1f"
          % (a.ratio, math.degrees(math.asin(1.0 / a.ratio)), g.hh, a.gap))
    for name, text in sorted(build(a.ratio, a.gap, a.gap_simple).items()):
        dest = os.path.join(a.out, name)
        d = os.path.dirname(dest)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        io.open(dest, "w", encoding="utf-8").write(text)
        print("  %-38s %7d bytes" % (name, len(text)))
