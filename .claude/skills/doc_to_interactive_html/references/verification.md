# Verification

`scripts/verify_html.py LESSON.html SHOT_DIR` opens the file from `file://`
with the network blocked (proving it is self-contained), waits for
`document.documentElement.dataset.mathjax === 'ok'`, walks every slide with
all steps revealed, and prints a JSON report followed by `PASS` or `FAIL`. The
browser window takes the stage's aspect ratio, read from the built CSS (19:9,
16:9 …), and the contact sheets use the same ratio:

- `tex_errors`: must be empty (no `[data-mjx-error]`);
- `missing_chrome`: must be empty;
- `placeholders`: must be empty (no `%%NAME%%` left);
- `page_errors`: must be empty;
- `layout`: must be empty. Per slide, with all steps revealed: content ending
  below the key-idea line (or the canvas bottom if the slide has none), content
  beyond the canvas width, or an element whose content spills sideways out of its
  box (a formula wider than its `.kf`, say). Fix the slide, or for a rule that
  cannot grow add `--nofit:1;`. `--no-layout` skips this check;
- `auto_fit` (informational, tall canvases): how many slides were scaled and the
  range of `--k`;
- `after_walk` equals the total slide count.

Then, by hand or with a short Playwright script:

1. Review the contact sheets `sheetN.png` for overflow, clipped text,
   collisions with the key-idea line, and colours outside the roles.
2. On a slide with steps: ↓ twice ⇒ same slide, two more steps shown.
3. Pop-up (`.prop`): opens inside the active slide, maths rendered.
4. Practice: the right option or a correct number + Enter raises the score.
5. Sliders and buttons: changing a value redraws the figure; compare the
   readouts with numbers quoted in the document.
6. For GitHub Pages, also serve the folder (`python -m http.server`) and open
   `http://localhost:8000/#/n` to check deep links.

Blur a text field before navigating with the keyboard (the core ignores keys
typed into inputs).
