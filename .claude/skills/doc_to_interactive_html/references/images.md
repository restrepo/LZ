# Images: reuse the document's, create what is missing

A lesson is not limited to the figures of its source (LaTeX repository,
PowerPoint, PDF, notes). When an idea is easier to understand with a figure the
source does not have, **create it** without waiting to be asked, and say which
figures are new when delivering.

## When to create a new figure

- The text describes a geometry, a process or an order of magnitude the reader
  would have to imagine.
- A source figure has text in another language, low resolution or notation that
  clashes with the lesson: redraw it (or translate its labels in the caption).
- A table or list reads better as bars, a scale or a diagram.
- There is something to **explore**: then it is an explorer (slider, buttons,
  dragging), not a static image — driven by the document's real equations and
  numbers, and checked against them (e.g. reproduce a published curve or value).
- A slide is text-only and the idea admits a diagram.

Never create decorative figures or images that imitate real photographs of
experiments, people or places: use the source's, with its credit.

## How (in order of preference)

1. **SVG generated in the lesson JS** with `nodo()`, `ejes()`, `polilinea()`,
   `rotulo()`: sharp at any scale, uses the role colours (`var(--res)`,
   `tok('--caso1')`). Maths labels in STIX Two Text (`FMATH`), other text in
   the body font (`FTXT`).
2. **Interactive figure** when there is a parameter to vary or a choice to make.
3. **Generated bitmap** (Python + Pillow/matplotlib) only when SVG will not do;
   save as WebP (≤ 1400 px) in `img/` and link with `<img class="foto">`.

## Source images

- **PDF / LaTeX figures:** render each page with PyMuPDF:
  ```python
  import pymupdf
  d = pymupdf.open('Fig1.pdf'); p = d[0]; z = 1400 / max(p.rect.width, p.rect.height)
  pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)   # then save via Pillow as WebP
  ```
  TikZ/PGFPlots figures are better redrawn as SVG.
- **PowerPoint (.pptx):** images are in `ppt/media/` of the zip; `python-pptx`
  gives placement, crop and notes.
- Give files descriptive names and keep a "Source" link in the caption when the
  original has one.
- `build_html.py` inlines every local `<img src>` as a `data:` URI; `http(s):`
  URLs are left as links (they need network).

## Verification

New figures go through the same checks as the rest of the lesson: no page
errors, no overflow or collisions, and an eye review on the contact sheets.
