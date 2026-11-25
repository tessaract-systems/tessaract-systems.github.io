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

`RATIO` is **1.4142136** (√2) — the camera sits at exactly **45°**, halfway
between flat-on and straight down.

It was originally 2.0 (a 30° camera), which made every plane read as a
rectangle. Textbook true isometric is 1.7320508 (√3, 35.264°) and that is
the projection in which a square tile is *geometrically* square — but both
that and 1.600 still read as stretched horizontally, because the eye judges
the whole stack, not one tile. Any ratio is a square tile viewed from
`asin(1/RATIO)` elevation, so a higher camera is not a distortion.

`GAP` scales with the plane height so four layers keep reading as four.
Below about **1.3** the stack stops reading as stacked planes and starts
reading as concentric diamonds — that is the floor.

**Changing `RATIO` also moves the hero animation.** Each layer's travel is
`closed_centre - open_centre`, so `@keyframes hf-0..hf-3`, the
`prefers-reduced-motion` fallback and `.hf-bloom`'s `transform-origin` in
`css/styles.css` all have to be recomputed with it.

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

tessaract-logo.svg                mark + wordmark, dark ink     2000 x 1164
tessaract-logo-light.svg          same, for dark backgrounds
tessaract-mark.svg                mark only, full detail          368 x 354
tessaract-mark-light.svg          same, for dark backgrounds
tessaract-mark-ui.svg             heavier strokes, for 40-80px    368 x 359
tessaract-mark-ui-light.svg       same, for dark backgrounds
tessaract-mark-simple.svg         simplified, for small sizes     368 x 400
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
