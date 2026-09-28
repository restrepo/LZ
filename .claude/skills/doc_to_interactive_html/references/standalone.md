# Lesson source format and the single-file output

## Minimal source

`assets/source-template.html` is a working example. The builder needs:

```html
<title>Topic · Course</title>
<style>:root{--t-rotulo:25px; --t-peq:30px; --t-cuerpo:37px; --t-titulo:70px; --t-portada:132px}
  /* lesson CSS: px of the 2280 × 1080 canvas (design baseline) or cqh/cqw of the slide;
     colours only through role variables: var(--res), var(--caso1)… */</style>
<body><div id="escenario">
  <span class="marca">Brand text · top left</span>
  <section class="diapositiva portada" data-seccion="Section 1">…</section>
  <section class="diapositiva" data-seccion="Section 1" id="dp-x">
    <p class="ceja">§ 1 · eyebrow</p><h2 class="titulo">Title</h2> … <li class="frag">…</li>
    <p class="clave">One-line key idea (shown at the bottom).</p>
  </section>
  <div class="pop-src" id="pop-a" style="display:none"><h4>Term</h4><p>…</p></div>
</div><script>/* the lesson's own modules */</script></body>
```

- `section.diapositiva` = a slide; `data-seccion` groups consecutive slides
  into a section (menu entry + poster). `data-label` (optional) names the slide;
  otherwise the `h1`/`h2` text is used. Add `compacta` for denser slides.
- The type tokens `--t-rotulo … --t-portada` are required.
- `.frag` = a step; `.frag.aparece` = hidden until its step.
- `<span class="prop" data-pop="pop-a">` opens the pop-up whose source is
  `div.pop-src#pop-a` (handled by the template's pop-up module).
- Practice: `.pr-item` with `data-ok="b"` + `.pr-opc[data-o]` buttons, or
  `data-ok-num` + `data-tol` + an `input.pr-in`; `.pr-score` counts hits.
- Class names (`diapositiva`, `frag`, `ceja`, `titulo`, `caja`…) and role
  variables are the engine's API, inherited from the clase-slides engine;
  they are never shown to the reader.

## JavaScript contract

- Colours through `tok('--role')`.
- A slide is active when it has `data-deck-active`; `activa(el)` tests it
  (pause animations when inactive).
- Events on `document`: `diapositiva` (any slide or step change) and
  `slidechange` (slide change, `detail.index`).
- Do not navigate or capture ← → ↑ ↓ outside your own fields.
- Figures drawn at load must not depend on being visible (the canvas exists
  from the start).
- Template helpers: `nodo(tag, attrs, parent)` (SVG node), `ejes(host, opts)`
  (axes with grid; `logx/logy`), `polilinea(A, pts, style)`, `rotulo(g, x, y,
  "*italic* _sub ^sup")`, `rango(id, fn)` (slider), `filaBotones(host, fn)`
  (toggle row), `num(x, d)` (formatted number), `cient(v)` (scientific).

## Output anatomy

```
<style>  design system · lesson CSS · ds-layer.css · chrome.css
<script> mathjax-config.js (role macros)   <script> MathJax tex-svg-full (inline)
<div id="escenario">                   ← responsive stage (canvas's aspect ratio; default 19:9), size container
  header.barra  .marca · nav#menu · #btn-fs ⛶
  #btn-ant ‹  #btn-sig ›  · .flecha.vert.arr/.aba (↑ ↓ steps)
  #contador · #recta (progress + section ticks) · [p.credito] · .giro
  <div id="lienzo">                    ← fixed WIDTH × HEIGHT canvas, scaled by scale.js (+ fit.js on tall canvases)
     section.diapositiva … · section.poster …
  </div>
  div.pop-src …
</div>
<script> tok() · scale.js · core.js · lesson JS · [fit.js] · counter.js · __leccionTypeset()
```

`core.js` handles the keyboard (← → slides; ↓ ↑ steps; space everything in
order; Home/End; F full screen), the `#/n` hash, idle dimming and pinch zoom.

## Converting an existing clase-slides lesson

Pass the lesson file directly: its `NÚCLEO clase-slides` core script is
replaced by `core.js` (the part from its `UTILIDADES` block on is kept), its
embedded MathJax and packaging safety net are dropped, and its palette hex
colours are mapped to roles.

## Aspect ratio and auto-fit

`--ratio W:H` (default 19:9) picks the canvas: width 2280 (rounded up to a
multiple of the reduced numerator so the height is an integer) and the height
from the ratio — 19:9 → 2280 × 1080, 16:9 → 2288 × 1287, 16:10 → 2280 × 1425,
4:3 → 2280 × 1710. The stage CSS uses `%%WIDTH%% / %%HEIGHT%%` (chrome.css), so
stage and canvas always share one ratio and scale.js never letterboxes.

Lessons are authored for 2280 × 1080. With `--fit auto` (on when the canvas is
> 5 % taller than that) the build:

1. rewrites the lesson CSS (`scripts/fit.py`): `font-size`, the size in the
   `font:` shorthand, `padding*`, `margin*`, `gap`, `grid-template-columns`
   (px ≥ 3) become `calc(Npx*var(--k,1))`; `max-height:var(--fh,Npx)` is
   multiplied by `--k`; `--t-peq` and `--t-cuerpo` are redefined per slide;
   inline `style="…"` of the slides get the same treatment; rules on lines with
   `.clave`, `.popover`, `.ayuda`, `.marca`, `.portada`, `@media` or `--nofit` are
   skipped (titles, eyebrows and the key-idea line keep their size);
2. patches `ejes()` (`H = o.H` → `Math.round(o.H*window.__HK)`), so explorer
   plots are taller (`__HK` ≈ 1 + 0.6 × extra height);
3. appends `assets/fit.js`: when a slide is first shown (after MathJax and the
   web fonts) it sets `--k` on the slide to the largest value in [1, KMAX]
   (bisection, 7 steps) at which the content ends above the key-idea line
   (30 px margin), stays inside the canvas width, and no `.kf`, `.caja`,
   `.lectura div`, table cell or display formula spills sideways. If the slide
   is already tight at `--k` 1 it is left alone.

Authoring rules that make this work: write sizes as plain `Npx` (not `em` or
`calc`); keep each CSS rule on one line; put `--nofit:1;` inside any rule that
must not grow (e.g. `.cifra b{…;--nofit:1}` for big numbers that would wrap);
in SVG use the `font-size` *attribute* (SVG is scaled by its `viewBox`, not by
`--k`); don't rely on fixed heights for content columns. Text-light slides keep
some empty space (the scale is capped); that is deliberate — the scale is the
same idea as a narrower canvas, so a larger cap would make slides differ in
type size.
