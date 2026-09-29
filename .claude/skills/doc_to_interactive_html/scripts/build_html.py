#!/usr/bin/env python3
"""Build an interactive lesson as ONE self-contained HTML file.

Usage:
  python build_html.py SOURCE.html --out OUTPUT.html [--ds PATH/TO/design-system]
         [--lang en|es] [--brand TEXT] [--credit TEXT | --lesson-credit]
         [--ratio 19:9|16:9|16:10|4:3 …] [--width N --height N]
         [--fit auto|on|off] [--fit-max K] [--no-posters] [--no-closing]
         [--mathjax inline|cdn]

What it produces (see references/standalone.md):
  · a responsive stage (19:9 by default; --ratio 16:9 …) with the navigation chrome: top bar (brand,
    auto-generated section menu, ⛶ full screen), ‹ › slide arrows, ↑ ↓ step
    arrows (only on slides with steps), a slide counter that opens a
    go-to-slide field, a progress line with section ticks, a rotate notice,
    idle dimming and pinch zoom; an optional credit line (none by default);
  · a fixed canvas (--width × --height, derived from --ratio: 2280×1080 for 19:9,
    2288×1287 for 16:9) holding the slides plus an
    accent-field poster before each new section and a closing poster;
  · on canvases taller than 19:9, an auto-fit (--fit, see scripts/fit.py) that
    scales each slide's type and figures to use the extra height;
  · the design system applied through the role bridge (ds-layer.css);
  · local images (<img src="img/…">, relative to the source) inlined as
    data: URIs;
  · MathJax (tex-svg-full, no autoload) inlined, so the file works from
    file:// and offline (--mathjax cdn links it instead, ~2.3 MB smaller).

Input: any HTML whose <body> has <section class="diapositiva"
data-seccion="…"> elements and its own scripts (the minimal source form is in
references/standalone.md), or a clase-slides lesson (its core is replaced).
"""
import argparse, base64, html, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, '..', 'assets')
sys.path.insert(0, HERE)
import common as c
import fit as fitmod

read = lambda p: open(p, encoding='utf-8').read()

# Interface text of the chrome, by language
UI = {
    'en': {
        'SECTIONS': 'Lesson sections', 'FULLSCREEN': 'Full screen',
        'PREV_SLIDE': 'Previous slide', 'NEXT_SLIDE': 'Next slide',
        'PREV_STEP': 'Previous step', 'NEXT_STEP': 'Next step',
        'PREV_STEP_LONG': 'Previous step within the slide', 'NEXT_STEP_LONG': 'Next step within the slide',
        'ROTATE': 'Rotate your device to view the presentation full screen',
        'GOTO': 'Go to a slide: tap and type its number', 'SLIDE_NUMBER': 'Slide number',
        'END': 'End', 'QUESTIONS': 'Questions?',
        'DIVIDER': 'Section divider: %s. %d slides.',
    },
    'es': {
        'SECTIONS': 'Secciones de la lección', 'FULLSCREEN': 'Pantalla completa',
        'PREV_SLIDE': 'Diapositiva anterior', 'NEXT_SLIDE': 'Diapositiva siguiente',
        'PREV_STEP': 'Paso anterior', 'NEXT_STEP': 'Paso siguiente',
        'PREV_STEP_LONG': 'Paso anterior dentro de la diapositiva', 'NEXT_STEP_LONG': 'Paso siguiente dentro de la diapositiva',
        'ROTATE': 'Gira el dispositivo para ver la presentación a pantalla completa',
        'GOTO': 'Ir a una diapositiva: toca y escribe el número', 'SLIDE_NUMBER': 'Número de diapositiva',
        'END': 'Fin', 'QUESTIONS': '¿Preguntas?',
        'DIVIDER': 'Separador: %s. %d diapositivas.',
    },
}

# Markers that identify engine scripts inside a clase-slides source lesson
CORE_MARKERS = ('NÚCLEO clase-slides', 'CORE clase-slides')
UTIL_MARKERS = ('UTILIDADES', 'UTILITIES')
COUNTER_MARKERS = ('Contador → ir a diapositiva', 'Counter → go to slide')


def roles_for(ds_hex):
    """"Mono" profile from common.ROLES; if the system has role accents
    (--color-accent-2 / -3) or an error colour, use them for the case roles."""
    r = dict(c.ROLES)
    tex = dict(c.TEX_COLOR)
    if '--color-accent-3' in ds_hex:
        r.update({'--caso1': 'var(--color-accent-3)', '--caso1-50': 'var(--color-accent-3-100, var(--color-surface))'})
        tex['075985'] = ('casouno', '--color-accent-3')
    if '--color-accent-2' in ds_hex:
        r.update({'--caso2': 'var(--color-accent-2)', '--caso2-50': 'var(--color-accent-2-100, var(--color-surface))',
                  '--caso2-tx': 'var(--color-accent-2-700, var(--color-accent-2))'})
        tex['B45309'] = ('casodos', '--color-accent-2')
    if '--color-error' in ds_hex:
        r.update({'--mal': 'var(--color-error)', '--mal-50': 'var(--color-error-100, var(--color-surface))'})
    if '--color-accent-2' in ds_hex or '--color-accent-3' in ds_hex:
        r.update({'--ok': 'var(--color-accent)', '--ok-tx': 'var(--color-accent-700)', '--ok-50': 'var(--color-accent-100)'})
    return r, tex


def markup(s):
    """TeX clean-up, hex colours → roles in style="" and SVG presentation
    attributes. Form controls keep their value/selected."""
    s = c.tex(s)
    s = re.sub(r'(\sstyle=")([^"]*)(")', c.style_attr, s)
    s = re.sub(r'<(?:path|line|polyline|polygon|circle|rect|ellipse|text|tspan|g|stop|marker|use)\b[^>]*>',
               c.svg_tag, s)
    return s.replace('''font-family="'Inter',sans-serif"''', '''font-family="Archivo,sans-serif"''')


SUP = str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻')
SUB = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')
def plain_text(s):
    """Title with TeX → readable plain text (posters, data-label):
    Δt, v², m₂, (F)/(m)… instead of leftover macros."""
    def f(m):
        t = m.group(1) if m.group(1) is not None else m.group(2)
        for a_, z in (('\\Delta ', 'Δ'), ('\\Delta', 'Δ'), ('\\omega', 'ω'), ('\\pi', 'π'), ('\\theta', 'θ'),
                      ('\\approx', '≈'), ('\\cdot', '·'), ('\\times', '×'), ('\\leq', '≤'), ('\\geq', '≥'), ('\\le ', '≤ '), ('\\ge ', '≥ '), ('\\left', ''), ('\\right', ''), ('{,}', ','),
                      ('\\alpha', 'α'), ('\\beta', 'β'), ('\\gamma', 'γ'), ('\\varepsilon', 'ε'), ('\\epsilon', 'ε'), ('\\lambda', 'λ'),
                      ('\\mu', 'μ'), ('\\nu', 'ν'), ('\\rho', 'ρ'), ('\\sigma', 'σ'), ('\\tau', 'τ'), ('\\phi', 'φ'), ('\\hbar', 'ħ'), ('\\infty', '∞'), ('\\propto', '∝'), ('\\sim', '∼'),
                      ('\\delta', 'δ'), ('\\chi', 'χ')):
            t = t.replace(a_, z)
        for _ in range(4):
            t = re.sub(r'\\qty\{([^{}]*)\}\{([^{}]*)\}', lambda m: (m.group(1) + ' ' + m.group(2).replace(' ', '')) if m.group(1) else ' ' + m.group(2).replace(' ', ''), t)
            t = re.sub(r'\\(?:vect|mathrm|mathsf|text|boldsymbol|mathbf|mathcal)\{([^{}]*)\}', r'\1', t)
            t = re.sub(r'\\(?:abs)\{([^{}]*)\}', r'|\1|', t)
            t = re.sub(r'\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}', lambda m: (m.group(1) if len(m.group(1)) < 2 else '(' + m.group(1) + ')') + '/' + (m.group(2) if len(m.group(2)) < 2 else '(' + m.group(2) + ')'), t)
        t = re.sub(r'\^\{?(-?\d+)\}?', lambda m: m.group(1).translate(SUP), t)
        t = re.sub(r'_\{?(\d)\}?', lambda m: m.group(1).translate(SUB), t)
        t = re.sub(r'_\{?([A-Za-z]+)\}?', r'\1', t)
        t = t.replace('\\,', ' ').replace('\\;', ' ').replace('\\!', '')
        t = re.sub(r'\\[a-zA-Z]+', '', t).replace('{', '').replace('}', '')
        return t
    s = re.sub(r'\\\((.+?)\\\)|\\\[(.+?)\\\]', f, s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
        '.webp': 'image/webp', '.svg': 'image/svg+xml'}
def inline_images(s, base):
    """<img src="img/photo.webp"> relative to the source folder → data: URI, so
    the output stays ONE file. Absolute URLs (http:, data:) are left alone."""
    def f(m):
        src = html.unescape(m.group(2))
        if re.match(r'(?i)(data:|https?:|//)', src): return m.group(0)
        path = os.path.normpath(os.path.join(base, src))
        ext = os.path.splitext(path)[1].lower()
        if ext not in MIME or not os.path.isfile(path): raise SystemExit('image not found or unsupported type: ' + src)
        return m.group(1) + 'data:%s;base64,%s' % (MIME[ext], base64.b64encode(open(path, 'rb').read()).decode()) + m.group(3)
    return re.sub(r'(<img\b[^>]*?\ssrc=")([^"]+)(")', f, s)


def lesson_js(scripts, ui):
    """Keep the lesson's own modules; replace a clase-slides core with
    core.js, add the counter if missing, drop embedded MathJax and the
    source package's safety net."""
    core = read(os.path.join(ASSETS, 'core.js'))
    keep, has_core, has_counter = [], False, False
    for s in scripts:
        if '__webpack_modules__' in s or 'window.MathJax =' in s or 'window.MathJax=' in s: continue
        if 'RED DE SEGURIDAD' in s or 'SAFETY NET' in s: continue
        if any(m in s for m in CORE_MARKERS):
            k = max((s.find(m) for m in UTIL_MARKERS), default=-1)
            k = s.rfind('/*', 0, k) if k >= 0 else len(s)
            keep.append(core); keep.append(s[k:]); has_core = True
            continue
        if any(m in s for m in COUNTER_MARKERS): has_counter = True
        keep.append(s)
    if not has_core: keep.insert(0, core)
    if not has_counter:
        keep.append(read(os.path.join(ASSETS, 'counter.js'))
                    .replace('%%T_GOTO%%', ui['GOTO']).replace('%%T_SLIDE_NUMBER%%', ui['SLIDE_NUMBER']))
    js = '\n\n'.join(keep)
    js = re.sub(r"'#([0-9A-Fa-f]{6})'", lambda m: "tok('%s')" % c.HEX_TO_VAR.get(m.group(1).upper(), '--obj'), js)
    js = re.sub(r'(color:)#([0-9A-Fa-f]{6})', lambda m: m.group(1) + c.hex_var(m.group(2)), js)
    js = js.replace('fill="white"', "fill=\"' + tok('--panel') + '\"")
    js = js.replace("'Inter',sans-serif", 'Archivo,sans-serif')
    if '</script' in js.lower(): raise SystemExit('the JS contains </script>')
    return js


def canvas_size(ratio, width, height):
    """Canvas (w, h) in px from --ratio / --width / --height. Default 19:9 → 2280 × 1080;
    the stage takes the canvas's own aspect ratio, so canvas and stage always agree."""
    if width and height:
        if ratio: print('WARNING: --width and --height given: --ratio %s ignored' % ratio)
        return width, height
    try:
        rw, rh = (int(x) for x in (ratio or '19:9').split(':'))
        assert rw > 0 and rh > 0
    except Exception:
        raise SystemExit('--ratio must look like 16:9')
    g = math.gcd(rw, rh); rw, rh = rw // g, rh // g
    if width: return width, round(width * rh / rw)
    if height: return round(height * rw / rh), height
    w = math.ceil(2280 / rw) * rw          # smallest width ≥ 2280 with an integer height (19:9 → 2280, 16:9 → 2288)
    return w, w * rh // rw


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('source', help='lesson source HTML')
    ap.add_argument('--out', required=True, help='output HTML file')
    ap.add_argument('--ds', default=os.path.join(ASSETS, 'default-ds'),
                    help='design-system folder with styles.css (default: assets/default-ds)')
    ap.add_argument('--lang', choices=sorted(UI), default='en', help='interface language (default: en)')
    ap.add_argument('--ratio', default=None, metavar='W:H',
                    help='aspect ratio of the stage, e.g. 16:9 (default 19:9); sets the canvas size unless --width/--height are given')
    ap.add_argument('--width', type=int, default=None, help='canvas width in px (default: 2280, adjusted to the ratio)')
    ap.add_argument('--height', type=int, default=None, help='canvas height in px (default: from the ratio)')
    ap.add_argument('--fit', choices=['auto', 'on', 'off'], default='auto',
                    help='per-slide auto-fit of type and figures to the canvas height (auto: on when the canvas is taller than 19:9)')
    ap.add_argument('--fit-max', type=float, default=None, metavar='K', help='largest auto-fit scale (default: from the canvas)')
    ap.add_argument('--no-posters', action='store_true', help='no section divider slides')
    ap.add_argument('--no-closing', action='store_true', help='no closing slide')
    ap.add_argument('--mathjax', choices=['inline', 'cdn'], default='inline')
    ap.add_argument('--brand', help='text at the top left (default: the source\'s .marca, or its title)')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--credit', default='', help='credit line at the bottom left (default: none)')
    g.add_argument('--lesson-credit', action='store_true', help='use the <p class="credito"> of the source')
    a = ap.parse_args()
    ui = UI[a.lang]
    a.width, a.height = canvas_size(a.ratio, a.width, a.height)
    fit_on = a.fit == 'on' or (a.fit == 'auto' and fitmod.growth(a.width, a.height) > 1.05)
    kmax, hk = fitmod.defaults(a.width, a.height)
    if a.fit_max: kmax = a.fit_max

    src = read(a.source)
    ds_css = read(os.path.join(a.ds, 'styles.css'))
    ds_hex = c.ds_values(ds_css)
    roles, tex_color = roles_for(ds_hex)
    c.TEX_COLOR.clear(); c.TEX_COLOR.update(tex_color)

    title = re.search(r'<title>([\s\S]*?)</title>', src).group(1).strip()
    src_credit = (lambda m: m.group(1).strip() if m else '')(re.search(r'<p class="credito">([\s\S]*?)</p>', src))
    credit = src_credit if a.lesson_credit else a.credit
    credit = html.unescape(re.sub(r'<[^>]+>', '', credit)).strip()
    brand = a.brand or (lambda m: m.group(1).strip() if m else title.split('·')[0].strip())(re.search(r'<span class="marca">([\s\S]*?)</span>', src))

    # lesson CSS without :root, chrome or visibility rules
    css = [m.group(1) for m in re.finditer(r'<style>([\s\S]*?)</style>', src)][-1]
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    for sel in (r':root', r'\*', r'html,body', r'body', r'#escenario', r'\.barra', r'\.marca', r'\.menu[^{]*', r'\.btn-fs[^{]*',
                r'\.flecha[^{]*', r'#escenario[^{]*', r'\.pie[^{]*', r'\.recta[^{]*', r'\.credito', r'\.giro',
                r'\.diapositiva', r'\.diapositiva\.activa', r'\.diapositiva\.compacta', r'\.portada',
                r'\.portada h1', r'\.portada \.regla', r'\.ayuda'):
        css = re.sub(r'(^|\n)\s*%s\s*\{[^{}]*\}' % sel, r'\1', css)
    m = re.search(r'--t-rotulo:[^;]+;[^\n]*', src)
    if not m: raise SystemExit('the source does not define the type-size tokens (--t-rotulo…)')
    t_tokens = m.group(0).split('}')[0]
    css = re.sub(r'@media\s*print\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', css)
    css = re.sub(r'@media\s*\(orientation[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', css)
    css = re.sub(r'@page\{[^}]*\}', '', css)
    css = css.replace("'Inter',sans-serif", 'var(--font-body)').replace("'Inter',system-ui,sans-serif", 'var(--font-body)')
    css = css.replace("'Lora',serif", 'var(--font-heading)')
    css = re.sub(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b', lambda m: c.hex_var(m.group(1)), css)
    css = re.sub(r'rgba\(20,26,36,([.\d]+)\)', lambda m: 'color-mix(in srgb, var(--color-text) %g%%, transparent)' % (float(m.group(1)) * 100), css)
    css = re.sub(r'rgba\(0,0,0,([.\d]+)\)', lambda m: 'color-mix(in srgb, var(--color-text) %g%%, transparent)' % (float(m.group(1)) * 100), css)
    css = re.sub(r'\n\s*\n+', '\n', css).strip()
    if fit_on: css = fitmod.scale_css(css) + '\n' + fitmod.token_css(t_tokens)

    root = ':root{\n  %s\n%s\n}' % (t_tokens, '\n'.join('  %s:%s;' % kv for kv in roles.items()))
    padx = round(a.width * 0.0253); pad = '%dpx %dpx %dpx' % (round(a.height * .06), padx, round(a.height * .07))
    layer = (read(os.path.join(ASSETS, 'ds-layer.css')).replace('%%ROLES%%', root).replace('%%PAD%%', pad)
             .replace('%%PADX%%', '%dpx' % padx).replace('%%COLS%%', '4'))
    chrome = read(os.path.join(ASSETS, 'chrome.css')).replace('%%WIDTH%%', str(a.width)).replace('%%HEIGHT%%', str(a.height))
    css_all = ds_css + '\n\n' + css + '\n\n' + layer + '\n\n' + chrome

    # body: slides, pop-up sources and scripts
    body = src[src.find('<body'):]
    scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', re.sub(r'<!--[\s\S]*?-->', '', body))
    body = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', body)
    secs = [body[i:j] for i, j in c.blocks(body, 'section', r'<section class="diapositiva')]
    if not secs: raise SystemExit('no <section class="diapositiva"> found')
    pops = [body[i:j] for i, j in c.blocks(body, 'div', r'<div class="pop-src"')]

    groups = []
    for s in secs:
        name = (re.search(r'data-seccion="([^"]*)"', s) or [0, '—'])[1]
        if not groups or groups[-1][0] != name: groups.append([name, []])
        groups[-1][1].append(s)
    out, n = [], 0
    for k, (name, lst) in enumerate(groups):
        if not a.no_posters and k > 0:
            titles = [plain_text((re.search(r'<h2[^>]*>([\s\S]*?)</h2>', x) or [0, ''])[1]) for x in lst]
            titles = [t for t in titles if t][:4]
            p = c.poster(name, '§ %d' % (k + 1), titles, ui['DIVIDER'] % (name, len(lst)))
            out.append(p.replace('<section class="poster"', '<section class="poster" data-seccion="%s"' % html.escape(name, quote=True), 1))
        for s in lst:
            n += 1
            if 'data-label=' not in s[:300]:
                h = re.search(r'<h[12][^>]*>([\s\S]*?)</h[12]>', s)
                s = s.replace('<section ', '<section data-label="%s" ' % html.escape(plain_text(h.group(1)) if h else name, quote=True), 1)
            out.append(s)
    if not a.no_closing:
        foot = ['<span>%s</span>' % html.escape(ui['QUESTIONS'])] + (['<span>%s</span>' % html.escape(credit)] if credit else [])
        out.append(('<section class="poster" data-seccion="%s" data-label="%s">\n  <div class="p-num">%s</div>\n  <h2 class="p-tit">%s</h2>\n'
                    '  <div class="p-pie" style="grid-template-columns:repeat(%d,1fr)">%s</div>\n</section>\n')
                   % (html.escape(groups[-1][0], quote=True), html.escape(ui['END']), html.escape(ui['END']),
                      html.escape(title.split('·')[0].strip()), len(foot), ''.join(foot)))
    slides = markup('\n\n'.join(out))
    if fit_on: slides = fitmod.scale_html(slides)
    pops_html = markup('\n'.join(pops))
    base = os.path.dirname(os.path.abspath(a.source))
    slides, pops_html = inline_images(slides, base), inline_images(pops_html, base)

    # MathJax: semantic preamble + full bundle inline (no autoload)
    macros = {'abs': ['\\lvert #1\\rvert', 1], 'norm': ['\\lVert #1\\rVert', 1], 'R': '\\mathbb{R}',
              'vect': ['\\boldsymbol{#1}', 1], 'qty': ['#1\\,\\mathrm{#2}', 2]}
    for hx, (mac, tok) in c.TEX_COLOR.items():
        col = ds_hex.get(tok, '#000000').lstrip('#').upper()
        macros[mac] = ['{\\color[RGB]{%s}{#1}}' % ','.join(str(int(col[k:k + 2], 16)) for k in (0, 2, 4)), 1]
    mj_cfg = read(os.path.join(ASSETS, 'mathjax-config.js')).replace('%%MACROS%%', json.dumps(macros))
    if a.mathjax == 'inline':
        mj = read(os.path.join(ASSETS, 'mathjax-tex-svg-full.js'))
        if '</script' in mj.lower(): raise SystemExit('MathJax contains </script>')
        mj_tag = '<script>\n' + mj + '\n</script>'
    else:
        mj_tag = '<script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg-full.js" id="MathJax-script"></script>'

    tok_js = ("function tok(name) {\n  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();\n"
              "  return v || '#201e1d';\n}")
    scale = read(os.path.join(ASSETS, 'scale.js')).replace('%%WIDTH%%', str(a.width))
    les = lesson_js(scripts, ui)
    parts = [tok_js, scale]
    if fit_on:
        les = fitmod.patch_ejes(les)
        parts += ['window.__HK = %s;   // taller explorer plots on the taller canvas' % hk, les, fitmod.fit_js(ASSETS, kmax)]
    else:
        parts += [les]
    js = '\n\n'.join(parts + ['window.__leccionTypeset();'])
    if fit_on: print('auto-fit on: canvas %d × %d, slide scale up to %g, explorer plots ×%g' % (a.width, a.height, kmax, hk))
    for t in (css_all, slides, pops_html, mj_cfg):
        if '</script' in t.lower(): raise SystemExit('content contains </script>')

    credit_html = '  <p class="credito">%s</p>' % html.escape(credit) if credit else ''
    doc = read(os.path.join(ASSETS, 'template.html'))
    reps = [('%%LANG%%', a.lang), ('%%TITLE%%', html.escape(title)),
            ('%%BRAND%%', html.escape(html.unescape(re.sub(r'<[^>]+>', '', brand)))),
            ('%%CREDIT%%', credit_html)]
    reps += [('%%T_' + k + '%%', html.escape(v)) for k, v in ui.items()]
    reps += [('%%CSS%%', css_all), ('%%MATHJAX_CFG%%', mj_cfg), ('%%MATHJAX%%', mj_tag),
             ('%%SLIDES%%', slides), ('%%POPS%%', pops_html), ('%%JS%%', js)]
    for k, v in reps:   # bulky content last, so its text is never re-scanned for placeholders
        doc = doc.replace(k, v)
    open(a.out, 'w', encoding='utf-8').write(doc)
    print('OK: %s · %d content slides · %d in total · %.2f MB'
          % (a.out, n, slides.count('<section '), len(doc.encode()) / 1e6))
    for w in c.warnings: print('WARNING:', w[:200])


if __name__ == '__main__':
    main()
