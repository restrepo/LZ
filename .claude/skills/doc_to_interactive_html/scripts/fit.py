"""Auto-fit for canvases taller than 19:9 (16:9, 16:10, 4:3 …).

Lessons are authored in px for a 2280 × 1080 canvas. On a taller canvas every
slide would end with an empty band, so the build makes type sizes, card
padding, gaps and figure heights scale with a per-slide factor `--k`, and
`assets/fit.js` picks `--k` at run time: the largest value (≤ KMAX) at which
the slide still fits above the key-idea line. Nothing here changes a 19:9 build.

The transformations are regex-based and line-oriented, which matches the
one-rule-per-line style of assets/source-template.html:

  · `font-size:Npx`, the size in the `font:` shorthand, `padding*`, `margin*`,
    `gap`, `grid-template-columns` (px values ≥ 3) → `calc(Npx*var(--k,1))`;
  · `max-height:var(--fh,Npx)` → multiplied by `--k`;
  · the tokens `--t-peq` and `--t-cuerpo` are redefined per slide;
  · rules on lines containing `.clave`, `.popover`, `.ayuda`, `.marca`,
    `.portada`, `@media` or the marker `--nofit` are left alone (put `--nofit:1;`
    inside any rule whose sizes must stay fixed, e.g. big statistics that would
    wrap).
"""
import os, re

SKIP = ('.clave', '.popover', '.ayuda', '.marca', '.portada', '@media', '--nofit')
_PX = r'(-?\d+(?:\.\d+)?)px'
_PROPS = re.compile(r'(?<![\w-])((?:padding|margin)(?:-(?:top|right|bottom|left))?|gap|row-gap|column-gap|grid-template-columns):([^;}"]*)')
BASE_RATIO_H = 9 / 19          # the design baseline: 2280 × 1080


def _k(v):
    return 'calc(%spx*var(--k,1))' % v


def scale_decls(text):
    """Scale the size-bearing declarations found in a run of CSS declarations."""
    text = re.sub(r'(?<![\w-])font-size:\s*' + _PX, lambda m: 'font-size:' + _k(m.group(1)), text)
    text = re.sub(r'(?<![\w-])font:[^;}"]*',
                  lambda m: re.sub(_PX, lambda q: _k(q.group(1)), m.group(0), count=1), text)
    text = _PROPS.sub(lambda m: m.group(1) + ':' + re.sub(
        _PX, lambda q: _k(q.group(1)) if abs(float(q.group(1))) >= 3 else q.group(0), m.group(2)), text)
    return re.sub(r'max-height:\s*var\(--fh,\s*(\d+)px\)', r'max-height:calc(var(--fh,\1px)*var(--k,1))', text)


def scale_css(css):
    return '\n'.join(l if any(s in l for s in SKIP) else scale_decls(l) for l in css.split('\n'))


def scale_html(html):
    """Same for inline style="…" attributes of the slides (in SVG use the font-size attribute)."""
    return re.sub(r'style="([^"]*)"', lambda m: 'style="%s"' % scale_decls(m.group(1)), html)


def token_css(t_tokens):
    """Per-slide redefinition of the body-type tokens so --k reaches everything sized by them."""
    tok = dict(re.findall(r'(--t-[a-z]+):\s*([\d.]+)px', t_tokens))
    d = ';'.join('%s:calc(%spx*var(--k,1))' % (n, tok[n]) for n in ('--t-peq', '--t-cuerpo') if n in tok)
    return 'section.diapositiva{%s}' % d if d else ''


def patch_ejes(js):
    """Make the explorers' plots taller too: `H = o.H` in ejes() → `H = round(o.H * window.__HK)`."""
    return re.sub(r'(const\s+W\s*=\s*o\.W\s*,\s*H\s*=\s*)o\.H\b', r'\1Math.round(o.H * (window.__HK || 1))', js)


def growth(width, height):
    """How much taller the canvas is than the 19:9 baseline at this width."""
    return height / (width * BASE_RATIO_H)


def defaults(width, height):
    """(KMAX, HK) for a canvas: scale ≈ the extra height, capped; plots grow a bit less."""
    g = growth(width, height)
    return round(max(1.0, min(1.5, 1 + 1.05 * (g - 1))), 2), round(max(1.0, min(1.3, 1 + 0.6 * (g - 1))), 2)


def fit_js(assets, kmax):
    return open(os.path.join(assets, 'fit.js'), encoding='utf-8').read().replace('%%KMAX%%', str(kmax))
