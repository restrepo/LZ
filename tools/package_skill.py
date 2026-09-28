#!/usr/bin/env python3
"""Package .claude/skills/doc_to_interactive_html as a zip that can be
uploaded to a Claude account (Settings → Capabilities → Skills → Upload).

Claude account skill names allow only lowercase letters, digits and hyphens,
so the packaged skill is named `doc-to-interactive-html` (folder and
frontmatter); the repository copy keeps its original name.

Usage: python tools/package_skill.py [--out dist/doc-to-interactive-html.zip]
"""
import argparse, os, re, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '.claude', 'skills', 'doc_to_interactive_html')
NAME = 'doc-to-interactive-html'
SKIP_DIRS = {'__pycache__', '.git'}
SKIP_FILES = {'.DS_Store'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'dist', NAME + '.zip'))
    a = ap.parse_args()

    skill_md = open(os.path.join(SRC, 'SKILL.md'), encoding='utf-8').read()
    fm = re.match(r'---\n([\s\S]*?)\n---\n', skill_md)
    if not fm: raise SystemExit('SKILL.md has no YAML frontmatter')
    front = re.sub(r'^name: .*$', 'name: ' + NAME, fm.group(1), count=1, flags=re.M)
    desc = re.search(r'^description: (.*)$', front, re.M).group(1)
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', NAME) or len(NAME) > 64:
        raise SystemExit('invalid skill name: ' + NAME)
    if len(desc) > 1024: raise SystemExit('description longer than 1024 characters')
    skill_md = '---\n' + front + '\n---\n' + skill_md[fm.end():]

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    n = 0
    with zipfile.ZipFile(a.out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(NAME + '/SKILL.md', skill_md); n += 1
        for d, dirs, files in os.walk(SRC):
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
            for f in sorted(files):
                if f in SKIP_FILES or f.endswith('.pyc'): continue
                rel = os.path.relpath(os.path.join(d, f), SRC)
                if rel == 'SKILL.md': continue
                z.write(os.path.join(d, f), NAME + '/' + rel.replace(os.sep, '/')); n += 1
    print('OK: %s · %d files · %.2f MB' % (a.out, n, os.path.getsize(a.out) / 1e6))


if __name__ == '__main__':
    main()
