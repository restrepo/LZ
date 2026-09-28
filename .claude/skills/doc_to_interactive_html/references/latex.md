# LaTeX conventions for MathJax in the lesson

Delimiters: `\( … \)` inline and `\[ … \]` display; never `$`.

The MathJax preamble (`assets/mathjax-config.js`, completed by the builder)
defines:

| Macro | Meaning |
|---|---|
| `\abs{x}` | `\lvert x\rvert` (like mathtools' `\DeclarePairedDelimiter`) |
| `\norm{x}` | `\lVert x\rVert` |
| `\R` | `\mathbb{R}` |
| `\vect{p}` | bold italic vector, `\boldsymbol{p}` |
| `\qty{9.8}{m/s^2}` | number, thin space, upright unit (like siunitx) |
| `\resalta{…}`, `\casouno{…}`, `\casodos{…}`, `\dato{…}` | colour by teaching role (highlight, case 1, case 2, datum), taken from the design system |

## Rules

| Do | Avoid | Why |
|---|---|---|
| `\abs{x-1}` | `\|x-1\|` | `\|` is an ordinary symbol: bad spacing, ambiguous when nested (the builder converts simple cases) |
| `\casodos{-x}` | `{\color{#B45309}-x}` | colour is a ROLE; changing the theme must not touch formulas |
| `\operatorname{dom}(f)` | `dom(f)` | upright operator names with correct spacing |
| `0.5`, `2.84` | `0,5` | English lessons use a decimal point (group thousands in running text, not in formulas) |
| `\text{ if } x\ge 0` | bare words in maths | words must not be italic |
| `\tfrac13` inline, `\dfrac` in display | cramped `\frac` in lines | legibility at projection distance |
| `v = 3\ \mathrm{m/s}` or `\qty{3}{m/s}` | `3 m/s` in italics | units upright and separated |
| `\ge`, `\le`, `\neq`, `\iff`, `\Rightarrow` | `>=`, `<=>`, `->` | proper relation symbols |

- Maths labels inside SVG use STIX Two Text so they match typeset maths.
- After changing TeX, re-verify: 0 `[data-mjx-error]` elements.
- For Spanish lessons (`--lang es`) use the decimal comma as `0{,}5`.
