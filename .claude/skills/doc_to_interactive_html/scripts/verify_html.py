#!/usr/bin/env python3
"""Check a built lesson by opening it from file:// with the network blocked.

Reports page and MathJax errors, missing chrome (menu, ⛶, ‹ ›, ↑ ↓, counter,
progress line), leftover %%PLACEHOLDERS%%, walks every slide with the ›
button and saves one screenshot per slide (all steps revealed) plus contact
sheets of six slides each (sheetN.png) to review by eye. The browser window
takes the stage's aspect ratio (read from the file: 19:9, 16:9 …), and on every
slide a layout check looks for content crossing the key-idea line or the canvas
edge and for boxes or formulas spilling sideways ("layout" in the report).

Usage: python verify_html.py LESSON.html SCREENSHOT_DIR [--chrome PATH] [--network] [--no-layout]
Needs: pip install playwright pillow (and a Chromium; --chrome points to it).
"""
import asyncio, glob, json, os, re, sys
from playwright.async_api import async_playwright

CHROME = ['#menu', '#btn-fs', '#btn-ant', '#btn-sig', '.flecha.vert.arr', '.flecha.vert.aba', '#contador', '#recta']

# Layout of the active slide (all steps revealed), in canvas pixels.
LAYOUT_JS = """() => {
  const lz = document.getElementById('lienzo'), d = lz.querySelector('section.activa'); if (!d) return null;
  const L = lz.getBoundingClientRect(), s = L.width / lz.offsetWidth, W = lz.offsetWidth, H = lz.offsetHeight;
  const cl = d.querySelector(':scope > .clave');
  const limit = cl ? (cl.getBoundingClientRect().top - L.top) / s : H - 20;
  let mb = 0, mr = 0, who = ''; const clip = [];
  d.querySelectorAll('*').forEach(e => {
    if (e.closest('.clave,.ayuda,.popover,.pop-src,.barra,.pasos-ctrl,.lightbox') || (e.closest('svg') && e.tagName !== 'svg')) return;
    const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = e.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return;
    const b = (r.bottom - L.top) / s; if (b > mb) { mb = b; who = e.tagName.toLowerCase() + '.' + (e.className.baseVal !== undefined ? e.className.baseVal : e.className); }
    mr = Math.max(mr, (r.right - L.left) / s);
    if (e.scrollWidth > e.clientWidth + 2 && e.clientWidth > 0 && cs.display !== 'inline' && cs.overflowX === 'visible' && !/^(input|button|img|svg)$/i.test(e.tagName))
      clip.push(e.tagName.toLowerCase() + '.' + (e.className.baseVal !== undefined ? e.className.baseVal : e.className) + ' ' + e.scrollWidth + '>' + e.clientWidth);
  });
  return { id: d.id || d.dataset.label || '', k: d.style.getPropertyValue('--k') || '', below: Math.round(mb - limit), who,
           right: Math.round(mr - W), clip: clip.slice(0, 2) };
}"""


def stage_ratio(path):
    """(w, h) of the stage aspect ratio, read from the built CSS (default 19:9)."""
    m = re.search(r'calc\(100vh \* ([\d.]+) / ([\d.]+)\)', open(path, encoding='utf-8').read())
    return (float(m.group(1)), float(m.group(2))) if m else (19.0, 9.0)


async def main(path, out, chrome, network, layout_check):
    os.makedirs(out, exist_ok=True)
    rw, rh = stage_ratio(path); vh = 720; vw = round(vh * rw / rh)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=chrome) if chrome else await p.chromium.launch()
        pg = await b.new_page(viewport={'width': vw, 'height': vh})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text))
        if not network:   # proves the file is self-contained (web fonts fall back)
            await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto('file://' + os.path.abspath(path))
        await pg.wait_for_function("document.documentElement.dataset.mathjax==='ok'", timeout=120000)
        q = pg.evaluate
        info = await q("""(sel)=>({
          formulas: document.querySelectorAll('mjx-container').length,
          tex_errors: [...document.querySelectorAll('[data-mjx-error]')].map(e=>e.getAttribute('data-mjx-error')),
          missing_chrome: sel.filter(s=>!document.querySelector(s)),
          placeholders: (document.documentElement.outerHTML.match(/%%[A-Z_]+%%/g)||[]),
          lang: document.documentElement.lang,
          menu: [...document.querySelectorAll('#menu button')].map(b=>b.textContent),
          credit: (document.querySelector('.credito')||{}).textContent || null,
          total: document.getElementById('contador').dataset.total})""", CHROME)
        from math import gcd
        g = gcd(int(rw), int(rh)) if float(rw).is_integer() and float(rh).is_integer() else 1
        info['stage_ratio'] = '%g:%g' % (rw / g, rh / g)
        n = int(info['total'])
        shots, layout, ks = [], [], []
        for i in range(n):
            for _ in range(15): await pg.keyboard.press('ArrowDown')
            await pg.wait_for_timeout(450)
            f = os.path.join(out, 's%02d.png' % (i + 1)); await pg.screenshot(path=f); shots.append(f)
            if layout_check:
                r = await q(LAYOUT_JS)
                if r:
                    if r['k']: ks.append(float(r['k']))
                    if r['below'] > 2: layout.append('slide %d (%s): content %d px below the key-idea line (%s)' % (i + 1, r['id'], r['below'], r['who']))
                    if r['right'] > 2: layout.append('slide %d (%s): content %d px beyond the canvas width' % (i + 1, r['id'], r['right']))
                    if r['clip']: layout.append('slide %d (%s): spills sideways: %s' % (i + 1, r['id'], '; '.join(r['clip'])))
            await pg.click('#btn-sig')
        info['after_walk'] = await q("document.getElementById('contador').textContent")
        await pg.click('#btn-ant'); await pg.wait_for_timeout(300)
        info['after_prev_button'] = await q("document.getElementById('contador').textContent")
        info['page_errors'] = errs
        if layout_check:
            info['layout'] = layout
            if ks: info['auto_fit'] = {'slides_scaled': len(ks), 'k_min': min(ks), 'k_max': max(ks)}
        print(json.dumps(info, ensure_ascii=False, indent=1))
        await b.close()
    from PIL import Image
    cw, ch = round(360 * rw / rh), 360
    ims = [Image.open(f).resize((cw, ch)) for f in shots]
    for k in range(0, len(ims), 6):
        g = ims[k:k + 6]; W = Image.new('RGB', (2 * cw, ch * ((len(g) + 1) // 2)), 'white')
        for j, im in enumerate(g): W.paste(im, ((j % 2) * cw, (j // 2) * ch))
        W.save(os.path.join(out, 'sheet%d.png' % (k // 6)))
    ok = not (info['tex_errors'] or info['missing_chrome'] or info['placeholders'] or info['page_errors'] or info.get('layout')) \
        and info['after_walk'] == str(n)
    print('PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    args = [x for x in sys.argv[1:]]
    chrome = None
    if '--chrome' in args:
        k = args.index('--chrome'); chrome = args[k + 1]; del args[k:k + 2]
    else:
        chrome = (glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome') or [None])[0]
    network = '--network' in args
    layout_check = '--no-layout' not in args
    args = [x for x in args if x not in ('--network', '--no-layout')]
    if len(args) != 2: sys.exit(__doc__)
    asyncio.run(main(args[0], args[1], chrome, network, layout_check))
