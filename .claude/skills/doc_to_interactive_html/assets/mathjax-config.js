window.MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']],
    /* Semantic preamble: \abs{·} (≈ mathtools' \DeclarePairedDelimiter),
       \R, and one colour macro per teaching ROLE, not per hue. */
    macros: %%MACROS%%
  },
  /* no glyph cache: every formula is self-contained (cloned pop-ups) */
  svg: { fontCache: 'none' },
  options: { enableAssistiveMml: false, menuOptions: { settings: { assistiveMml: false } } },
  /* Typesetting is started by __leccionTypeset() once the markup is in the DOM. */
  startup: { typeset: false }
};
/* Typesets the lesson: invisibly un-hides hidden boxes (hints, solutions)
   so MathJax measures with real fonts, and flattens compound transforms
   that some mobile viewers render badly. Sets data-mathjax="ok" when done. */
window.__leccionTypeset = function () {
  const listo = () => window.MathJax && MathJax.startup && MathJax.startup.promise && MathJax.typesetPromise;
  if (!listo()) { setTimeout(window.__leccionTypeset, 150); return; }
  const aplanar = () => {
    document.querySelectorAll('mjx-container svg [transform]').forEach(el => {
      const m = el.getAttribute('transform').match(/^translate\((-?[\d.eE+]+)(?:\s*,\s*(-?[\d.eE+]+))?\)\s+scale\((-?[\d.eE+]+)(?:\s*,\s*(-?[\d.eE+]+))?\)$/);
      if (m) {
        const tx = +m[1], ty = +(m[2] || 0), sx = +m[3], sy = m[4] !== undefined ? +m[4] : +m[3];
        el.setAttribute('transform', `matrix(${sx},0,0,${sy},${tx},${ty})`);
      }
    });
  };
  window.__mjAplanar = aplanar;
  let lote = [];
  const midiendo = si => {
    if (si) {
      lote = Array.from(document.querySelectorAll('section [style*="display:none"], section [style*="display: none"], .pr-pista:not(.on), .pr-sol:not(.on)'))
        .filter(el => /\\[(\[]/.test(el.textContent));
      lote.forEach(el => { el.__disp = el.style.display; el.style.display = 'block'; el.style.position = 'absolute'; el.style.visibility = 'hidden'; });
    } else {
      lote.forEach(el => { el.style.display = el.__disp || ''; el.style.position = ''; el.style.visibility = ''; });
      lote = [];
    }
  };
  MathJax.startup.promise
    .then(() => document.fonts.ready)
    .then(() => { midiendo(true); return MathJax.typesetPromise(); })
    .catch(e => console.error(e))
    .then(() => { aplanar(); midiendo(false); document.documentElement.dataset.mathjax = 'ok'; });
};
