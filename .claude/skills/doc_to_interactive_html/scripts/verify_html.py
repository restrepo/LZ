#!/usr/bin/env python3
"""Check a built lesson by opening it from file:// with the network blocked.

Reports page and MathJax errors, missing chrome (menu, ⛶, ‹ ›, ↑ ↓, counter,
progress line), leftover %%PLACEHOLDERS%%, walks every slide with the ›
button and saves one screenshot per slide (all steps revealed) plus contact
sheets of six slides each (sheetN.png) to review by eye.

Usage: python verify_html.py LESSON.html SCREENSHOT_DIR [--chrome PATH] [--network]
Needs: pip install playwright pillow (and a Chromium; --chrome points to it).
"""
import asyncio, glob, json, os, sys
from playwright.async_api import async_playwright

CHROME = ['#menu', '#btn-fs', '#btn-ant', '#btn-sig', '.flecha.vert.arr', '.flecha.vert.aba', '#contador', '#recta']


async def main(path, out, chrome, network):
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=chrome) if chrome else await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1520, 'height': 720})
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
        n = int(info['total'])
        shots = []
        for i in range(n):
            for _ in range(15): await pg.keyboard.press('ArrowDown')
            await pg.wait_for_timeout(450)
            f = os.path.join(out, 's%02d.png' % (i + 1)); await pg.screenshot(path=f); shots.append(f)
            await pg.click('#btn-sig')
        info['after_walk'] = await q("document.getElementById('contador').textContent")
        await pg.click('#btn-ant'); await pg.wait_for_timeout(300)
        info['after_prev_button'] = await q("document.getElementById('contador').textContent")
        info['page_errors'] = errs
        print(json.dumps(info, ensure_ascii=False, indent=1))
        await b.close()
    from PIL import Image
    ims = [Image.open(f).resize((760, 360)) for f in shots]
    for k in range(0, len(ims), 6):
        g = ims[k:k + 6]; W = Image.new('RGB', (1520, 360 * ((len(g) + 1) // 2)), 'white')
        for j, im in enumerate(g): W.paste(im, ((j % 2) * 760, (j // 2) * 360))
        W.save(os.path.join(out, 'sheet%d.png' % (k // 6)))
    ok = not (info['tex_errors'] or info['missing_chrome'] or info['placeholders'] or info['page_errors']) \
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
    args = [x for x in args if x != '--network']
    if len(args) != 2: sys.exit(__doc__)
    asyncio.run(main(args[0], args[1], chrome, network))
