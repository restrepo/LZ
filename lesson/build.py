#!/usr/bin/env python3
"""Build docs/index.html (published by GitHub Pages) from lesson/source.html
with the repository's doc_to_interactive_html skill.

Usage: python lesson/build.py
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL = os.path.join(ROOT, '.claude', 'skills', 'doc_to_interactive_html')

subprocess.run([sys.executable, os.path.join(SKILL, 'scripts', 'build_html.py'),
                os.path.join(HERE, 'source.html'),
                '--out', os.path.join(ROOT, 'docs', 'index.html')], check=True)
