# WeasyPrint gotchas (verified on version 69)

| Symptom | Cause and what to do |
|---|---|
| An SVG shape with `fill="url(#grad)"` is invisible | **`<linearGradient>` does not render at all.** CSS `linear-gradient` works. For a gradient inside SVG, stack layers with falling opacity |
| Moiré / grid pattern on semi-transparent graphics | Overlapping shapes double the alpha. Place them **edge to edge**: step width == shape width, no overlap on either axis |
| Text inside an SVG comes out black in the default font, CSS does not touch it | **CSS does not cascade into inline SVG.** Set everything with presentation attributes: `font-family=`, `font-size=`, `fill=`, `stroke=`. `charts.py` does exactly that; the rule `svg.chart{width:100%}` only applies to the element itself |
| Legend labels are cut off on the right | The legend was built inside the SVG. Move it to HTML, where line wrapping works on its own |
| `pdffonts` lists foreign fonts (Helvetica, Hiragino, Arial — the set varies) | **Inert ballast.** With a PT-only stack they still show up in the resources, and the pages are byte-identical. Nothing to fix |
| Numbers in adjacent tiles sit at different heights | One label wrapped to two lines and the others did not. `min-height` on `.kpi .lbl` is already there; after a font-size change, check it is still enough |
| Chart labels are smaller than the body text | The body size went up and `charts.py` did not. They are not linked automatically: when you edit `--body-pt`, edit the sizes in the module too |
| Cover text sits on top of the artwork | The art was absolutely positioned under the whole block with the text on top. The art zone (`--aur-h`) and the text block must not overlap — `base.css` separates them itself, do not set `padding-top` by hand |
| A horizontal "step" shows under the artwork, especially above cards | A semi-transparent fill with a hard bottom edge. Never cut a fill off: build the fade from layers and end the drawing above the bottom of its zone |
| In scroll mode all the text is pinned to the left edge | The cover was declared as a named `@page cover` with zero margins, and since there is only one page those margins stretched across the whole document. In `scroll.css` the cover gets `page:auto` and bleeds out with negative margins |
| Empty running head on the left | `string-set` does not escape `position:absolute`. Fill it through the `--doctitle` token |
| The running head broke through onto the cover | The document redefined `@page` and overrode `@page cover{content:none}` from base.css. Do not touch `@page` in the document — only the tokens |
| Fonts vanished in the dark build, `font-family:` is "no value" | The typography tokens ended up only in the light theme. Keep `--sans/--serif/--mono/--fs-chrome` in `base.css`; a theme carries **colour only** |
| Legend swatches turned into sticks | Flex squeezed them: `flex:0 0 9px` |
| The dark theme goes light in the margins | The background belongs on `@page{background:#…}` — that fills the whole sheet, margins included. `body{background}` does not paint the margins |
| The table header does not repeat on the next page | `thead{display:table-header-group}` |
| Words ran together in a PDF bookmark ("onboarding:results") | A `<br>` inside `h1`: the line break does not reach the bookmark. Avoid `<br>` in the cover heading, or put a space before it |
| Short labels break with a hyphen ("ONBOAR-DING") | `hyphens:auto` with a `lang` that has a dictionary. In base.css hyphenation is off for tile labels, legends and table headers; for your own class add `hyphens:none` |
| CJK text renders as boxes | No CJK font on the machine. `brew install --cask font-noto-sans-cjk-sc` or `apt install fonts-noto-cjk`; the fallback tail is already in `base.css` |
| A CJK line breaks in the middle of a Latin word or a number | `word-break` was set to `break-all` somewhere. `base.css` uses `line-break:strict; word-break:normal` for `:lang(zh)` — that breaks between Han characters but keeps Latin runs whole |
| The number in the table of contents sticks to the text | Hang the counter on `li::after` with `attr(data-t)`, not on `a::after` — otherwise it lands before the dot leader |
| A **highlighted** code line runs off the page, the same line wraps fine unhighlighted | **`overflow-wrap` and `word-break` do not break between adjacent inline boxes.** Syntax highlighting splits the line into `<span>`s, and each one becomes unbreakable, so the whole run overflows. Measured: the same 74-character line wraps at 206 pt as plain text and reaches 595 pt once wrapped in spans, with either `overflow-wrap:anywhere` or `word-break:break-all`. There is no CSS that fixes this — **wrap the line in the source**, the way you would in the code it came from. `build.sh` reports it, so you find out at build time rather than from a reader |
| Inline `<code>` in a table splits mid-word ("pre_cal" + "l") | `overflow-wrap:anywhere` on inline code. `anywhere` also shrinks min-content to a single character, so the table gives the column almost no width and then breaks the word to fit. Inline code wants `break-word` (break only a word that would not fit a line of its own); `anywhere` is right for `pre`, which owns its line |

## Measuring page fill — carefully

A short **last page of a chapter** is normal book layout, not a defect: the next chapter's
`break-before:page` follows it. Treat it as a fault and you will "fix" something that is not
broken and ruin a working layout.

What to measure is **how far the content reaches**, excluding the first and last pages of
chapters: `last inked line / page height`. The norm is 0.95 and up. The "share of lines with
ink" metric is useless here: for normal text it sits around 0.5 simply because of leading.

That share is still worth computing for a different job — not judging a page, but **choosing
which pages to open first** on a long document, where "look at every PNG" is 60+ images.
Compare each page's inked share against the document's own median and open the outliers.
On a 67-page book the median was 7.9 %; the page that turned out to hold a heading and
nothing else measured 0.33 %, two orders below its neighbours, and a long `<pre>` that had
jumped whole to the next page was the cause. Cover, contents and chapter-end pages come up
in the same list and are fine — the number picks the candidates, you still look.

One more: `h2,h3{break-before:avoid}` **makes it worse**. Combined with `break-after:avoid` on
the heading itself it glues the heading to both the previous and the following block, which
produces unbreakable slabs and real holes. Verified: the share of short pages doubled. Keep a
heading with the text that follows it, and nothing else.

## What WeasyPrint can do that Chrome cannot
`target-counter` (page numbers in the table of contents), named `@page` (a cover with no
running heads), running heads through margin boxes. Chrome loses all of it and additionally
eats the space in a bookmark title at a line break.

## Environment check
```bash
brew install weasyprint poppler qpdf     # required (macOS)
pip install weasyprint                   # required (Linux) + apt install poppler-utils qpdf
brew install typst pandoc                # optional, for the other route
```
Fonts come from the system: PT Serif / PT Sans / Menlo cover Latin and Cyrillic and are
embedded as a subset (≈110 KB for 4 pages). Han characters fall back to the CJK tail of the
stack in `base.css`, which adds roughly 300–700 KB to a Chinese document — that is the subset
of a CJK font and it is normal.
