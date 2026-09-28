"""Shared helpers for build_html.py: colour roles, TeX clean-up, markup
rewriting and section posters.

The lesson markup keeps the clase-slides engine's class names and role
variables (section.diapositiva, .frag, --res, --caso1, --tinta…); these are
the engine's API, not display text.
"""
import html, re

# ── Hex colours of the clase-slides palette → lesson role variable
HEX_TO_VAR = {
    '141A24': '--obj', '5B6472': '--tinta2', '6D28D9': '--res', '0D9488': '--aux',
    'B45309': '--caso2', '075985': '--caso1', 'E8EAF0': '--rejilla', 'A9B1BF': '--proy',
    'FFFFFF': '--panel', 'FFF': '--panel', 'F5F3FF': '--res-50', 'FFFBEB': '--caso2-50',
    'F0F9FF': '--caso1-50', 'F0FDFA': '--aux-50', 'EDE9FE': '--res-100', 'C9BAEE': '--res-borde',
    '92400E': '--caso2-tx', '0F766E': '--aux-tx', 'D5DAE3': '--linea', '7E8899': '--borde',
    '334155': '--primario', 'EEF1F6': '--primario-tinte', '15803D': '--ok', 'F0FDF4': '--ok-50',
    '166534': '--ok-tx', 'B91C1C': '--mal', 'FEF2F2': '--mal-50', 'F1F5F9': '--pista-50',
    'F7F8FA': '--papel', '1F2A3A': '--color-accent-700', '0E1116': '--lienzo',
}

# ── Lesson roles → design-system tokens ("mono" profile: a single accent).
#    build_html.roles_for() upgrades it when the system has role accents.
#    --papel paper · --panel card · --tinta ink · --tinta2 secondary ink ·
#    --linea rule · --borde border · --res highlight/result · --caso1/--caso2
#    case colours · --rejilla grid · --proy projection · --ok/--mal feedback.
ROLES = {
    '--papel': 'var(--color-bg)', '--panel': 'var(--color-neutral-100)',
    '--tinta': 'var(--color-text)', '--tinta2': 'var(--color-neutral-700)',
    '--lienzo': 'var(--color-neutral-900)', '--linea': 'var(--color-neutral-300)',
    '--borde': 'var(--color-neutral-600)', '--halo': 'var(--color-neutral-100)',
    '--primario': 'var(--color-text)', '--primario-tinte': 'var(--color-neutral-200)',
    '--res': 'var(--color-accent)', '--res-50': 'var(--color-accent-100)',
    '--res-100': 'var(--color-accent-200)', '--res-borde': 'var(--color-accent-300)',
    '--obj': 'var(--color-text)',
    '--caso1': 'var(--color-neutral-800)', '--caso1-50': 'var(--color-neutral-200)',
    '--caso2': 'var(--color-accent-700)', '--caso2-50': 'var(--color-accent-100)',
    '--caso2-tx': 'var(--color-accent-800)',
    '--aux': 'var(--color-neutral-600)', '--aux-50': 'var(--color-surface)',
    '--aux-tx': 'var(--color-neutral-800)',
    '--rejilla': 'var(--color-neutral-200)', '--proy': 'var(--color-neutral-400)',
    '--ok': 'var(--color-text)', '--ok-50': 'var(--color-neutral-200)', '--ok-tx': 'var(--color-text)',
    '--mal': 'var(--color-accent-700)', '--mal-50': 'var(--color-accent-100)',
    '--pista-50': 'var(--color-surface)',
}
# ── TeX colours: \color{#hex} → semantic macro (defined in the MathJax config)
TEX_COLOR = {'075985': ('casouno', '--color-neutral-800'), 'B45309': ('casodos', '--color-accent-700'),
             '6D28D9': ('resalta', '--color-accent'), '0D9488': ('dato', '--color-neutral-600')}

warnings = []
def warn(m): warnings.append(m)


# ───────────────────────────── HTML utilities
def blocks(s, tag, open_re):
    """(start, end) of every balanced element whose opening tag matches open_re."""
    out, pos = [], 0
    tag_re = re.compile(r'<(/?)%s\b[^>]*>' % tag)
    while True:
        m = re.compile(open_re).search(s, pos)
        if not m: return out
        depth = 0
        for t in tag_re.finditer(s, m.start()):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                out.append((m.start(), t.end())); pos = t.end(); break
        else:
            raise SystemExit('unclosed <%s> element' % tag)


def ds_values(ds_css):
    return dict(re.findall(r'(--color-[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})', ds_css))


# ───────────────────────────── TeX
TEX_SPAN = re.compile(r'\\\((.+?)\\\)|\\\[(.+?)\\\]', re.S)

def abs_to_macro(t):
    """|…| → \\abs{…}. Pairs bars: opens when there is no operand before it or
    the stack is empty; closes when an operand precedes it. Leaves the formula
    untouched if anything is ambiguous."""
    if '|' not in t or '\\left|' in t or '\\mid' in t or '\\|' in t: return t
    idx = [k for k, c in enumerate(t) if c == '|']
    if len(idx) % 2: warn('odd number of bars, not converted: ' + t); return t
    stack, pairs = [], []
    for k in idx:
        before = t[:k].rstrip()
        before = re.sub(r'(\\[,;:! ]|\\quad|\\qquad)+$', '', before).rstrip()
        operand = bool(before) and (before[-1].isalnum() or before[-1] in ')]}\'' or
                                    (before[-1] == '|' and (len(before) - 1) in [p[1] for p in pairs]))
        if stack and operand:
            pairs.append((stack.pop(), k))
        else:
            stack.append(k)
    if stack: warn('ambiguous bar pairing, not converted: ' + t); return t
    out = list(t)
    for a, b in pairs:
        out[a] = '\\abs{'; out[b] = '}'
    return ''.join(out)


def color_to_macro(t):
    """{\\color{#hex}BODY} → \\macro{BODY}."""
    def close(s, k):
        p = 0
        for j in range(k, len(s)):
            p += (s[j] == '{') - (s[j] == '}')
            if p == 0: return j
        return -1
    for _ in range(50):
        m = re.search(r'\{\\color\{#([0-9A-Fa-f]{6})\}', t)
        if not m: break
        end = close(t, m.start())
        mac = TEX_COLOR.get(m.group(1).upper(), (None,))[0]
        if end < 0 or not mac: warn('TeX colour without macro: ' + m.group(0)); break
        t = t[:m.start()] + '\\' + mac + '{' + t[m.end():end].strip() + '}' + t[end + 1:]
    return t


def tex(s):
    def f(m):
        o, c = ('\\(', '\\)') if m.group(1) is not None else ('\\[', '\\]')
        body = m.group(1) if m.group(1) is not None else m.group(2)
        return o + color_to_macro(abs_to_macro(body)) + c
    return TEX_SPAN.sub(f, s)


# ───────────────────────────── markup
def hex_var(h):
    v = HEX_TO_VAR.get(h.upper().lstrip('#'))
    if not v: warn('colour without a role: #' + h); return '#' + h
    return 'var(%s)' % v


def style_attr(m):
    v = re.sub(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b', lambda h: hex_var(h.group(1)), m.group(2))
    v = v.replace("'Inter',sans-serif", 'var(--font-body)').replace("'Inter'", 'var(--font-body)')
    return m.group(1) + v + m.group(3)


PRES = re.compile(r'\s(fill|stroke|stop-color)="(#[0-9A-Fa-f]{3,6}|white)"')
def svg_tag(m):
    """SVG presentation colours → role variables inside style=""."""
    tag = m.group(0)
    props = []
    def take(p):
        val = p.group(2)
        props.append('%s:%s' % (p.group(1), 'var(--panel)' if val == 'white' else hex_var(val[1:])))
        return ''
    tag = PRES.sub(take, tag)
    if not props: return tag
    if ' style="' in tag:
        return tag.replace(' style="', ' style="' + ';'.join(props) + ';', 1)
    end = '/>' if tag.endswith('/>') else '>'
    return tag[:-len(end)] + ' style="' + ';'.join(props) + '"' + end


def poster(name, num, titles, notes):
    """Accent-field section divider: § n, section name and up to four slide titles."""
    cols = max(1, min(4, len(titles)))
    foot = ''.join('<span>%s</span>' % html.escape(t) for t in titles[:4])
    return ('<section class="poster" data-label="%s" data-speaker-notes="%s">\n'
            '  <div class="p-num">%s</div>\n  <h2 class="p-tit">%s</h2>\n  <div class="p-pie" style="grid-template-columns:repeat(%d,1fr)">%s</div>\n'
            '</section>\n') % (html.escape(num + ' · ' + name), html.escape(notes),
                               html.escape(num), html.escape(name), cols, foot)
