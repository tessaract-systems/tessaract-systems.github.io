# Tessaract Systems — brand assets

Generated from the site's own layer-stack graphic. The SVGs are the
masters; the PNGs are exports. All files have transparent backgrounds.

## Which file to use

| Use | File |
|---|---|
| Anything printed or displayed large | `tessaract-logo.svg` |
| Dark backgrounds | `*-light.svg` / `*-light@*.png` |
| Mark alone (social avatar, app icon) | `tessaract-mark.svg` |
| Favicon, avatars, anything under ~48px | `tessaract-mark-simple.svg` |

**Use the simplified mark below about 48px.** The detailed mark's interior
motifs collapse into noise at small sizes; the simplified one keeps the four
planes and the signal diamond and stays readable down to 16px.

## Files

```
tessaract-logo.svg                mark + wordmark, dark ink      2000 x 993
tessaract-logo-light.svg          same, for dark backgrounds
tessaract-mark.svg                mark only, full detail          368 x 270
tessaract-mark-light.svg          same, for dark backgrounds
tessaract-mark-simple.svg         simplified, for small sizes     368 x 298
tessaract-mark-simple-light.svg   same, for dark backgrounds
png/                              exports at several widths
```

## Notes

- **The type is outlined.** TESSARACT and SYSTEMS are paths, not live text,
  so nothing depends on Traceform being installed. To change the wording you
  need the font and the generator, not a text editor.
- **Occlusion is done with SVG masks**, not a background-coloured knockout,
  which is why the transparency is real and the logo sits correctly on any
  colour.
- **Colours**: ink `#2A373D`, signal red `#DB5461`, paper `#FAFAFA`.
- Clear space: keep at least the height of one plane edge clear on all sides.
