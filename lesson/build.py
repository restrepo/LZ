#!/usr/bin/env python3
"""Build the single-file interactive lesson from lesson/source.html.

Runs the leccion-a-deck skill's build_html.py and then translates the
navigation chrome that the skill's template emits in Spanish.

Usage: python lesson/build.py [--skill PATH_TO_leccion-a-deck]
"""
import argparse, glob, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
OUT = os.path.join(RAIZ, 'docs', 'index.html')   # published by GitHub Pages from /docs

CHROME = [
    ('<html lang="es">', '<html lang="en">'),
    ('aria-label="Secciones de la lección"', 'aria-label="Lesson sections"'),
    ('aria-label="Pantalla completa" title="Pantalla completa (F)"', 'aria-label="Full screen" title="Full screen (F)"'),
    ('aria-label="Diapositiva anterior" title="Diapositiva anterior (←)"', 'aria-label="Previous slide" title="Previous slide (←)"'),
    ('aria-label="Diapositiva siguiente" title="Diapositiva siguiente (→)"', 'aria-label="Next slide" title="Next slide (→)"'),
    ('aria-label="Paso anterior dentro de la diapositiva" title="Paso anterior (↑)"', 'aria-label="Previous step within the slide" title="Previous step (↑)"'),
    ('aria-label="Paso siguiente dentro de la diapositiva" title="Paso siguiente (↓)"', 'aria-label="Next step within the slide" title="Next step (↓)"'),
    ('Gira el dispositivo para ver la presentación a pantalla completa', 'Rotate your device to view the presentation full screen'),
    ("'Ir a una diapositiva: toca y escribe el número'", "'Go to a slide: tap and type its number'"),
    ("'Número de diapositiva'", "'Slide number'"),
    ('data-label="Fin"', 'data-label="End"'),
    ('<div class="p-num">Fin</div>', '<div class="p-num">End</div>'),
    ('<span>¿Preguntas?</span>', '<span>Questions?</span>'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--skill', default=(glob.glob(os.path.expanduser('~/.claude/skills/**/leccion-a-deck'), recursive=True) or [''])[0])
    a = ap.parse_args()
    build = os.path.join(a.skill, 'scripts', 'build_html.py')
    if not os.path.isfile(build):
        sys.exit('leccion-a-deck skill not found; pass --skill PATH')
    subprocess.run([sys.executable, build, os.path.join(AQUI, 'source.html'),
                    '--ds', os.path.join(AQUI, '_ds', 'fundamentacion'), '--out', OUT,
                    '--credito', 'Study material design · W. Alexander Flórez'], check=True)
    s = open(OUT, encoding='utf-8').read()
    for es, en in CHROME:
        if es not in s:
            sys.exit('chrome string not found (template changed?): ' + es)
        s = s.replace(es, en)
    s = s.replace('data-speaker-notes="Separador: ', 'data-speaker-notes="Section divider: ').replace(' diapositivas."', ' slides."')
    open(OUT, 'w', encoding='utf-8').write(s)
    print('Translated navigation chrome →', OUT)


if __name__ == '__main__':
    main()
