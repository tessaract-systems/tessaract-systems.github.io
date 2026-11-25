# Tessaract Systems — brand assets

Generated from the site's own layer-stack graphic by `generate.py`. The SVGs
are the masters; the PNGs in `png/` are exports.

## Geometry

The whole mark is one isometric construction driven by two numbers in
`generate.py`:

| | |
|---|---|
| `RATIO` | plane width : height — this *is* the camera elevation |
| `GAP` | vertical distance between plane centres |

`RATIO` is **1.7320508** (√3), true isometric, a 35.264° camera. That is the
projection in which a square tile reads as a square. It was previously 2.0
(a 30° camera), which made every plane ~15% too flat, so the planes read as
rectangles rather than squares.

Regenerate everything after changing either number:

```
python3 brand/generate.py                 # writes into brand/
python3 brand/generate.py --ratio 2 --out /tmp/old   # compare against anything
```

`generate.py` also emits the artwork that is inlined into the site (the
header mark, the three service-card glyphs and the animated hero stack), so
if you change the geometry those have to be re-inlined too — they are not
read from this folder at runtime.

## Which file to use

| Use | File |
|---|---|
| Anything printed or displayed large | `tessaract-logo.svg` |
| Dark backgrounds | `*-light.svg` / `*-light@*.png` |
| Mark alone (app icon, large avatar) | `tessaract-mark.svg` |
| Favicon, anything under ~48px | `tessaract-mark-simple.svg` |
| LinkedIn / X profile picture | `social/avatar-light.svg` (or `-dark`) |
| LinkedIn company cover | `social/linkedin-cover.svg` |
| X / Twitter header | `social/x-header.svg` |
| Link previews (Open Graph) | `social/og-image.svg` |

**Use the simplified mark below about 48px.** The detailed mark's interior
motifs collapse into noise at small sizes; the simplified one keeps the four
planes and the signal diamond and stays readable down to 16px.

## Files

```
generate.py                       the generator -- the source of truth
_wordmark.svg                     TESSARACT / SYSTEMS as outlines

tessaract-logo.svg                mark + wordmark, dark ink     2000 x 1055
tessaract-logo-light.svg          same, for dark backgrounds
tessaract-mark.svg                mark only, full detail          368 x 300
tessaract-mark-light.svg          same, for dark backgrounds
tessaract-mark-ui.svg             heavier strokes, for 40-80px    368 x 305
tessaract-mark-ui-light.svg       same, for dark backgrounds
tessaract-mark-simple.svg         simplified, for small sizes     368 x 341
tessaract-mark-simple-light.svg   same, for dark backgrounds
icon.svg / icon-light.svg         square, transparent, favicons
apple-touch.svg                   square, paper ground, iOS

social/avatar-light.svg           square profile picture         1000 x 1000
social/avatar-dark.svg            same, ink ground
social/linkedin-cover.svg         LinkedIn company cover         1128 x 191
social/linkedin-cover-dark.svg    same, ink ground
social/x-header.svg               X / Twitter header             1500 x 500
social/og-image.svg               link preview                   1200 x 630

png/                              exports at several widths
png/social/                       the social set as PNG
```

## Social sizing notes

- **Avatars are cropped to a circle** by several platforms, so the mark is
  sized to sit inside the inscribed circle with room to spare. Both the
  square and the circle crop are correct.
- **LinkedIn drops the company logo badge over the cover's lower left**, so
  `linkedin-cover.svg` keeps that corner empty and sets the lockup right.
- Upload the **PNG** versions. LinkedIn and X do not accept SVG.

## Notes

- **The type is outlined.** TESSARACT and SYSTEMS are paths, not live text,
  so nothing depends on Traceform being installed. `_wordmark.svg` holds
  them; to change the wording you need the font, not a text editor.
- **Occlusion is done with SVG masks**, not a background-coloured knockout,
  which is why the transparency is real and the logo sits correctly on any
  colour.
- **Colours**: ink `#2A373D`, signal red `#DB5461`, paper `#FAFAFA`.
- Clear space: keep at least the height of one plane edge clear on all sides.
