/* Per-slide auto-fit for canvases taller than 19:9 (built in with --fit).
   Each content slide gets --k (1 … KMAX): the largest scale of its type, card
   padding, gaps and figure heights (see scripts/fit.py) that still fits above the
   key-idea line and inside the canvas width, with formulas and boxes unclipped.
   Measured in layout pixels (offsetTop / offsetHeight), so it is independent of
   the canvas scaling; runs once per slide, after MathJax and web fonts. */
(function () {
  const lz = document.getElementById('lienzo'); if (!lz) return;
  const KMAX = %%KMAX%%, MARGEN = 30;
  const cabe = sec => {
    const H = lz.offsetHeight, W = lz.offsetWidth, limite = H - 52 - MARGEN;   // the key-idea line sits ~52 px above the bottom
    let b = 0, r = 0;
    for (const e of sec.children) {
      if (e.classList.contains('clave') || e.classList.contains('ayuda') || e.classList.contains('lightbox')) continue;
      if (getComputedStyle(e).position === 'absolute') continue;
      b = Math.max(b, e.offsetTop + e.offsetHeight); r = Math.max(r, e.offsetLeft + e.offsetWidth);
    }
    if (b > limite || r > W - 30) return false;
    for (const e of sec.querySelectorAll('.kf, .caja, .lectura div, td, th, mjx-container[display="true"]'))
      if (e.scrollWidth > e.clientWidth + 2) return false;                     // a formula or box spilling sideways
    return true;
  };
  const ajusta = sec => {
    if (!sec || sec.classList.contains('portada') || sec.classList.contains('poster') || sec.dataset.kOk === '1') return;
    sec.dataset.kOk = '1';
    sec.style.setProperty('--k', KMAX);
    if (cabe(sec)) return;                                                     // the largest scale fits
    sec.style.setProperty('--k', 1);
    if (!cabe(sec)) return;                                                    // already tight at the base scale: leave it
    let lo = 1, hi = KMAX;
    for (let i = 0; i < 7; i++) { const m = (lo + hi) / 2; sec.style.setProperty('--k', m); if (cabe(sec)) lo = m; else hi = m; }
    sec.style.setProperty('--k', lo.toFixed(3));
  };
  const listo = () => document.documentElement.dataset.mathjax === 'ok';
  const activa = () => ajusta(lz.querySelector('section.activa'));
  if (listo()) activa();
  else new MutationObserver((m, o) => { if (listo()) { o.disconnect(); activa(); } })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['data-mathjax'] });
  document.addEventListener('diapositiva', () => { if (listo()) activa(); });
  if (document.fonts && document.fonts.ready)
    document.fonts.ready.then(() => { lz.querySelectorAll(':scope > section').forEach(s => delete s.dataset.kOk); if (listo()) activa(); });
})();
