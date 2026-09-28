# Lesson source format and the single-file output

## Minimal source

`assets/source-template.html` is a working example. The builder needs:

```html
<title>Topic · Course</title>
<style>:root{--t-rotulo:25px; --t-peq:30px; --t-cuerpo:37px; --t-titulo:70px; --t-portada:132px}
  /* lesson CSS: px of the 2280 × 1080 canvas or cqh/cqw of the slide;
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
<div id="escenario">                   ← responsive 19:9 stage, size container
  header.barra  .marca · nav#menu · #btn-fs ⛶
  #btn-ant ‹  #btn-sig ›  · .flecha.vert.arr/.aba (↑ ↓ steps)
  #contador · #recta (progress + section ticks) · [p.credito] · .giro
  <div id="lienzo">                    ← fixed WIDTH × HEIGHT canvas, scaled by scale.js
     section.diapositiva … · section.poster …
  </div>
  div.pop-src …
</div>
<script> tok() · scale.js · core.js · lesson JS · counter.js · __leccionTypeset()
```

`core.js` handles the keyboard (← → slides; ↓ ↑ steps; space everything in
order; Home/End; F full screen), the `#/n` hash, idle dimming and pinch zoom.

## Converting an existing clase-slides lesson

Pass the lesson file directly: its `NÚCLEO clase-slides` core script is
replaced by `core.js` (the part from its `UTILIDADES` block on is kept), its
embedded MathJax and packaging safety net are dropped, and its palette hex
colours are mapped to roles.
