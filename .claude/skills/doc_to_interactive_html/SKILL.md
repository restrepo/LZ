---
name: doc_to_interactive_html
description: 'Turns a document (a LaTeX paper or notes with main.tex and its \input files, a compiled PDF, slides, or an existing clase-slides lesson) into ONE self-contained interactive HTML lesson: 19:9 slides with step-by-step reveals (↓ ↑), a section menu, full screen, slide counter and progress line, MathJax maths that works offline, pop-up definitions, interactive SVG explorers with sliders, a practice slide with scoring and a glossary, styled by a design system. English interface and no credit line by default. Use it WHENEVER the user asks to make an "interactive HTML", "interactive lesson", "interactive slides", "slides from this paper/LaTeX/PDF", a "single self-contained HTML" or something to publish on GitHub Pages from a document, even without naming the format.'
---

# Document → interactive single-file HTML lesson

The output is **one self-contained `.html` file** that opens with a
double-click, needs no server or network (MathJax and images are inlined), and
can be published as-is on GitHub Pages. It carries its own navigation chrome:

- top bar: brand text, a **section menu** generated from `data-seccion`
  (underlines the current section, jumps to its start) and ⛶ full screen;
- ‹ › slide arrows; ↑ ↓ **step** arrows on both sides, only on slides with steps;
- a counter showing the current slide number; tapping it opens a go-to-slide field;
- a progress line with a tick per section; `#/n` in the URL opens slide *n*;
- idle dimming, a rotate notice on portrait phones, pinch zoom in full screen;
- an accent-field **poster** before each section and a closing slide.

Defaults: **English interface** (`--lang es` switches the chrome to Spanish)
and **no credit line** (`--credit "…"` adds one at the bottom left and on the
closing slide).

## Workflow

1. **Read the whole source.** For LaTeX, follow `main.tex` through every
   `\input`/`\include`, tables and the supplemental material; if a compiled
   PDF exists, use it for resolved figure/table numbers (they often differ from
   the order of the sources). Extract the story, key numbers and figures.
2. **Convert figures** to WebP (≤ 1400 px on the long side) in `img/` next to
   the source, e.g. PDF figures with PyMuPDF (`page.get_pixmap`). See
   `references/images.md`.
3. **Write the lesson source** starting from `assets/source-template.html`
   (form and conventions in `references/standalone.md`). Plan 15–30 slides in
   5–8 sections: cover, motivation, method, results, discussion, conclusion,
   practice, glossary. Put secondary information in steps (`class="frag"`) and
   definitions in pop-ups. **Create new figures** where an idea is easier to
   see than to read — preferably interactive SVG explorers with sliders driven
   by the real equations and numbers of the document. Say which figures are new
   when delivering. Follow `references/latex.md` for the maths.
4. **Build:**
   ```bash
   python <skill>/scripts/build_html.py lesson/source.html --out docs/index.html \
       [--ds path/to/design-system] [--lang en|es] [--credit "…"] [--brand "…"]
   ```
   Other options: `--width/--height` (canvas, default 2280×1080), `--no-posters`,
   `--no-closing`, `--mathjax cdn` (link MathJax instead of inlining it, −2.3 MB,
   needs network), `--lesson-credit` (use the source's `<p class="credito">`).
   Read and fix any `WARNING:` lines.
5. **Verify** (needs `playwright` and Chromium):
   ```bash
   python <skill>/scripts/verify_html.py docs/index.html /tmp/shots
   ```
   It must print `PASS`: no page errors, no MathJax errors, full chrome, no
   leftover placeholders, the walk reaches the last slide. Then **look at the
   contact sheets** (`sheetN.png`, all steps revealed) for overflow, clipped
   text or collisions, and exercise each explorer (sliders, buttons, pop-ups,
   practice). See `references/verification.md`.
6. **Deliver** the HTML file. For GitHub Pages, build to `docs/index.html`, add
   an empty `docs/.nojekyll`, and set *Settings → Pages → Deploy from a branch →
   main → /docs*.

## Design system

`--ds` points to a folder with `styles.css` defining the tokens the layer
uses: `--color-bg`, `--color-surface`, `--color-text`, `--color-divider`,
`--color-neutral-100…900`, `--color-accent` and `-100/-200/-300/-600/-700/-800`,
optionally `--color-accent-2`, `--color-accent-3` (role accents for the two
"case" colours) and `--color-error`, plus `--font-heading`,
`--font-heading-weight`, `--font-body`, `--radius-md`, `--shadow-lg`. Without
`--ds` the bundled `assets/default-ds/` is used (warm paper, near-black ink,
blue accent, green and amber role accents).

Lesson markup never uses hex colours: it uses the **role variables**
(`--res` highlight, `--caso1`/`--caso2` case colours, `--tinta`/`--tinta2`
ink, `--panel`, `--linea`, `--rejilla`, `--proy`, `--ok`/`--mal`…); in JS,
`tok('--res')` resolves a role to its current colour.

## Steps within a slide

Pending steps are shown **dimmed** (25 % opacity) and go to full opacity on
their turn (↓ ↑, the step buttons, or space). Use `class="frag aparece"` for
content that must stay hidden until its turn (answers, results of a question).

## Files

| Path | Role |
|---|---|
| `scripts/build_html.py` | Build the single-file lesson |
| `scripts/common.py` | Colour roles, TeX clean-up, markup helpers |
| `scripts/verify_html.py` | Headless check + screenshots/contact sheets |
| `assets/source-template.html` | Starting point for a lesson source |
| `assets/template.html`, `chrome.css`, `ds-layer.css`, `core.js`, `scale.js`, `counter.js`, `mathjax-config.js` | Page skeleton, navigation chrome and engine |
| `assets/mathjax-tex-svg-full.js` | MathJax 3.2.2 (Apache-2.0), inlined in every build |
| `assets/default-ds/` | Default design system |
| `references/*.md` | Source format, images, LaTeX conventions, verification |
