# LZ: dark matter search in an extended nuclear-recoil window

LaTeX sources (`main.tex` and its included files) and the compiled `main.pdf` of the LZ Collaboration paper
*Search for dark matter particle interactions in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ) experiment*,
plus an interactive lesson built from it.

## Interactive lesson

**Live:** <https://restrepo.github.io/LZ/>

A single self-contained HTML file (`docs/index.html`, about 3.5 MB) with 33 slides and interactive explorers: recoil
spectra, collision kinematics, S1/S2 energy, NEST response, backgrounds, MSSI, look-elsewhere effect and the
local-significance map. Navigation: `→`/`←` slides, `↓`/`↑` steps, `space` everything in order, `F` full screen;
`#/n` in the URL opens slide *n*. It also works offline: download `docs/index.html` and open it in a browser.

| Path | Contents |
|---|---|
| `docs/index.html` | Built lesson, published by GitHub Pages |
| `docs/.nojekyll` | Serve files as-is (no Jekyll processing) |
| `lesson/source.html` | Editable lesson source (clase-slides format) |
| `lesson/img/` | Paper figures converted to WebP |
| `lesson/_ds/fundamentacion/` | Design system |
| `lesson/build.py` | Build script |

### Rebuild

Requires the `leccion-a-deck` skill:

```bash
python lesson/build.py            # or: python lesson/build.py --skill /path/to/leccion-a-deck
```

This rewrites `docs/index.html`; commit and push it to `main` to update the site.

### GitHub Pages setup (one time)

*Settings → Pages → Build and deployment*: **Source** = *Deploy from a branch*, **Branch** = `main`, folder **`/docs`** → *Save*.
The site appears at <https://restrepo.github.io/LZ/> a minute or two after each push to `main`.
