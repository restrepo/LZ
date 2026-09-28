# Verification

`scripts/verify_html.py LESSON.html SHOT_DIR` opens the file from `file://`
with the network blocked (proving it is self-contained), waits for
`document.documentElement.dataset.mathjax === 'ok'`, walks every slide with
all steps revealed, and prints a JSON report followed by `PASS` or `FAIL`:

- `tex_errors`: must be empty (no `[data-mjx-error]`);
- `missing_chrome`: must be empty;
- `placeholders`: must be empty (no `%%NAME%%` left);
- `page_errors`: must be empty;
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
