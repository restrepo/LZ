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
| `lesson/source.html` | Editable lesson source |
| `lesson/img/` | Paper figures converted to WebP |
| `lesson/build.py` | Build script (uses the skill below) |
| `.claude/skills/doc_to_interactive_html/` | Claude Code skill that turns a document into a single-file interactive HTML lesson |

### Rebuild

```bash
pip install playwright pillow      # only needed for the verification step
python lesson/build.py             # rewrites docs/index.html
python .claude/skills/doc_to_interactive_html/scripts/verify_html.py docs/index.html /tmp/shots   # must print PASS
```

Commit and push `docs/index.html` to `main` to update the site.

> **Note:** the published `docs/index.html` (16:9, 39 slides, "Journal Club" version) was built from a revised lesson
> source that is not yet in the repository. Running `lesson/build.py` now rebuilds the older 33-slide lesson from
> `lesson/source.html` and would overwrite it; add the revised source to `lesson/source.html` first (and build with
> `--ratio 16:9`).

## The `doc_to_interactive_html` skill

Claude Code loads the skill automatically when working in this repository (ask, for example, *"turn main.tex into an
interactive HTML lesson"*). It can also be run by hand:

```bash
python .claude/skills/doc_to_interactive_html/scripts/build_html.py SOURCE.html --out OUTPUT.html \
    [--ratio 16:9] [--ds DESIGN_SYSTEM_DIR] [--lang en|es] [--credit "…"] [--brand "…"]
```

English interface and no credit line by default. `SKILL.md` describes the workflow; `assets/source-template.html` is a
starting point for a new lesson.

### Install in a Claude account

```bash
python tools/package_skill.py      # → dist/doc-to-interactive-html.zip
```

Upload the zip in claude.ai under *Settings → Capabilities → Skills → Upload skill* (code execution must be on).
Account skill names allow only lowercase letters, digits and hyphens, so the packaged skill is named
`doc-to-interactive-html`.

### GitHub Pages setup (one time)

*Settings → Pages → Build and deployment*: **Source** = *Deploy from a branch*, **Branch** = `main`, folder **`/docs`** → *Save*.
The site appears at <https://restrepo.github.io/LZ/> a minute or two after each push to `main`.
