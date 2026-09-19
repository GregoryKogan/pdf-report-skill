---
name: pdf-report
description: >
  Use whenever the user wants ANY document rendered as a PDF file — a report, memo, summary,
  analysis, guide, checklist, one-pager, handout, leaflet, or a redo/restyle of an existing
  one. Triggers: «make a PDF», «export to PDF», «one-pager», «handout», «write this up as a
  report», «сделай отчёт в pdf», «собери pdf», «памятка», «инструкция», «методичка»,
  «одностраничник», «оформи документ», «свёрстай», «под мобильные», «тёмная тема»,
  «做成 PDF», «出一份报告», «排版», «单页», «深色主题».
  Works in any language: the PDF is written in the language the user wrote in.
  Applies even when the user names no format: if the deliverable is a PDF, this skill owns it.
  Do NOT use for HTML artifacts published to claude.ai (that is the Artifact tool), for
  .docx/.pptx, or for reading an existing PDF.
---

# PDF reports

Engine — **WeasyPrint** (HTML + CSS Paged Media). Ready-made styles, a chart module and the
scripts live next to this file. Never start the layout from scratch.

## Procedure

1. **Check the tools.** `command -v weasyprint pdfinfo qpdf` — if missing,
   `brew install weasyprint poppler qpdf` (macOS) or
   `pip install weasyprint && apt install poppler-utils qpdf` (Linux). Also check for the
   humanizer skill that matches the report's language (table below); install it if absent.
2. **Write the text in the user's language and run it through the humanizer.** Mandatory,
   see the humanizer section.
3. **Mark it up.** HTML with the classes from `references/markup.md`, no custom CSS.
   Starting point — `assets/example-dark.html`; the light sample is `assets/example.html`.
   Set `<html lang="…">`: hyphenation, CJK line breaking and font fallback hang off it.
4. **Build.** `scripts/build.sh report.html [outdir]` → **one file** `report.pdf`:
   Nord dark theme, "scroll" format — ONE page of whatever length it needs, no page breaks
   at all. `scripts/fit-scroll.py` finds the height by binary search. A long document
   (over 5080 mm of scroll) **switches itself** to book layout — see below. Flags are only
   for departing from the default: `--light`, `--a5`, `--a4`, `--book`, `--both`.
5. **Check.** `scripts/check.sh report.pdf` — and **look at the exported PNGs with your own
   eyes, every single one.** This is not a formality: on the demo report that pass found
   13 defects no automated test catches — timeline events out of order, a legend spilling
   outside its SVG, "empty" calendar cells that were invisible.
6. **Ship one file.** That is the default, not a simplification — see the section below.

## Language: the report speaks the language of the request

**The PDF is written in the language the user used.** A request in Russian yields a Russian
report, in English an English one, in Chinese a Chinese one. Never translate the user's
subject matter into your own default language, and never ask which language to use — the
request already answered it. Mixed input: follow the language of the instructions, not the
language of the quoted data.

Two things depend on that language, and both are set explicitly (numbers do not: they are
written identically in every language — see "Typography by language"):

| What | How |
|---|---|
| Line breaking and fonts | `<html lang="ru">` / `"en"` / `"zh"` — `base.css` keys hyphenation, CJK rules and the font fallback off it |
| Typography in the text | the table in "Typography by language" below |

The font stacks in `base.css` end with a CJK tail, so Latin and Cyrillic come from PT Sans /
PT Serif while Han characters fall back to PingFang / Noto Sans CJK / Source Han. Nothing to
configure — but if the glyphs come out as boxes, the machine has no CJK font installed:
`brew install --cask font-noto-sans-cjk-sc` or `apt install fonts-noto-cjk`.

## Long documents: book layout

From about 20 pages the scroll stops working (the PDF limit is 5080 mm), and `build.sh`
switches to `book.css` on its own. Verified on a 169-page book: 4.4 s to build, 99 bookmarks
on two levels, the page numbers in the table of contents agree with the bookmarks, and **not
one short page inside a chapter** (the median page fills 96 % of the height).

What `book.css` adds over the mobile preset:

| | why |
|---|---|
| running head with the **current chapter title** (`string-set:chapter`) | on page 169 the reader still knows where they are |
| `orphans:3; widows:3` | not a single widow line — verified across 56 consecutive pages |
| justified text + hyphenation | the column is 120 mm wide, so no rivers open up |
| `.sec{break-before:page}` | a chapter starts on a fresh page; its short final page is **normal for a book, not a defect** |

**Breaking long tables is enabled in `base.css` for every format.** Without it a 45-row table
moves to the next page whole and leaves an almost empty one behind — verified, the difference
is a full page. Rows are not split, the header repeats. A short table can be pinned:
`<table class="keep">`.

## Text: the humanizer is required

**REQUIRED SUB-SKILL: a humanizer.** Every piece of text in the report — the summary,
paragraphs, callouts, chart captions, conclusions — goes through it **before** layout. Not
"if it comes out odd", but always: a human reads the report, and traces of machine writing
cost the numbers their credibility.

Do not talk yourself out of it because there is little text, because it is "technical",
because time is short, or because it already sounds fine. Three paragraphs of summary are
exactly the text that will be read most closely.

Pick the one that matches the report's language:

| Language | Skill | Install |
|---|---|---|
| English | `humanizer` | `git clone --depth 1 https://github.com/blader/humanizer ~/.claude/skills/humanizer` |
| Russian | `humanizer-ru` | `git clone --depth 1 https://github.com/ilyautov/humanizer-ru ~/.claude/skills/humanizer-ru` |
| Chinese | `humanizer-zh` | `git clone --depth 1 https://github.com/op7418/Humanizer-zh ~/.claude/skills/humanizer-zh` |
| anything else | `humanizer` | as above — its structural rules carry across languages |

Delete the `.git` directory after cloning (`rm -rf ~/.claude/skills/<name>/.git`).

After the pass, an objective cross-check: `scripts/prose-check.sh report.pdf` detects the
language itself and prints candidates for clichés, corporate voice and stock endings, plus
the typographic errors of that language. This is **not a verdict**: the humanizer explicitly
warns against mechanical matches, and every hit needs a human look. But an empty list on text
that knowingly has not been through the pass means the script ran on the wrong file.

### Per-language carve-outs

The humanizer itself says that a writing sample beats its style rules. For reports that sample
is the "Typography by language" section below, so its rules win where they collide:

- **Russian** — §14 (no dashes) and §19 (straight quotes) are cancelled. In Russian the em
  dash `—` is the norm rather than a machine tell, and the quotes are «guillemets».
- **Chinese** — the rules on sentence length and paragraph rhythm apply; the ones on articles
  and Latin punctuation do not. Full-width punctuation is correct, not a defect.
- **English** — every rule applies as written, and `prose-check.sh` additionally flags em-dash
  density, which in English *is* a tell.

The word lists in §7 and §26 are English; in other languages they rarely fire, and §17 (title
case) does not apply outside English. The structural rules carry over one to one — and those
are the ones that do the work: more often than not the humanizer reveals that a paragraph
holds no facts, only judgements.

## Default: Nord dark, scroll, one file

The reader reads reports on a phone, in dark mode. So **when the request names no format,
theme or number of files**, build with no flags: Nord + scroll + a single `report.pdf`.

**There must be no page breaks.** That is a direct requirement, not a preference: in a scroll
the document is one long page and the reader simply scrolls. If the content runs past the PDF
limit (5080 mm), `build.sh` falls back to paginated A5 by itself — and then the breaks have to
be clean: `break-inside:avoid` on cards and tables, `.sec` only before major parts, and a page
filled less than a third of the way is a defect.

Depart from the default only on a cue named in the request:

| The request said | Flag |
|---|---|
| "for print", "to print out", "A4", "for the print shop" | `--a4` |
| "with page numbers", "paginated", "with running heads" | `--a5` |
| "light theme", "on white", "like a normal document" | `--light` |
| "and one for print too", "both versions", "a desktop version" | `--both` |

None of that was said — do not ask and do not build extras: hand over the default in silence.

Why not A4: a PDF does not reflow, and A4 on a phone is unreadable without zoom. The scroll is
136 mm wide at 13.5 pt: on screen that is the equivalent of ~13.7 px on the web at 48
characters per line. Tuned by rendering into a real phone width (390 px), not by eye: at
11.5 pt it was too small, at 14.5 pt the line starts breaking with hyphens.

Size changes through **one knob** — `--body-pt` in `scroll.css`; the other sizes are in em and
follow it. If you change it, raise the font sizes in `charts.py` too, or the chart labels fall
behind the text. And check the tiles — a label that wraps to two lines drops its number below
its neighbours' (`base.css` has a `min-height` on `.kpi .lbl` for exactly that).

## Charts

**Load the `dataviz` skill before the first line of chart code** (it ships with Claude Code;
skip this step if your runtime has no such skill) and run the palette through its
`scripts/validate_palette.js`. Do not draw geometry by hand — `assets/charts.py` already
has area+line, stacked columns, a calendar heatmap, a polar rose, a 100 % bar, a sparkline,
a scatter, a multi-line, a treemap and horizontal bars. Details and print rules —
`references/charts.md`.

Numbers in charts need no configuration: `num()` writes a period for the decimal separator
and no space before `%` in every language, exactly as the rest of the report does.

A PDF has no hover and no tooltips, so **every value must be reachable some other way**:
labels on the marks, axes, and a summary table with all the numbers in an appendix.

## WeasyPrint gotchas

Read `references/gotchas.md` before layout. In short: SVG gradients do not render; overlapping
semi-transparent shapes moiré; build legends in HTML, not in SVG; `Helvetica`/`Hiragino` in
`pdffonts` are inert ballast, nothing to fix.

## Typography by language

**The same in every language**, deliberately, even where running text in that language would
do otherwise. A report is read next to code, tables and other languages, and one notation is
one ambiguity less:

- decimal separator — a period: `4.6`
- before `%`, `°C` and units — no space: `45%`, `20°C`
- minus — `−`, never a hyphen

`charts.py` writes numbers this way on its own; in your own generator, match it.

**Follows the language of the text**, not the language of whoever builds the report:

| | Russian | English | Chinese |
|---|---|---|---|
| Thousands | thin space `12 345` | comma `12,345` | comma `12,345` |
| Quotes | «guillemets» | "straight" or "curly", consistently | 「」 or “”, full-width |
| Dash | `—` with spaces | `—` unspaced, sparingly | `——` full-width |
| Space after punctuation | one | one | none — the full-width glyph carries its own |
| Alignment in a narrow column | left (`mobile.css` does it) | left | justified (`base.css` does it for `:lang(zh)`) |

For a language that is not in the table, follow its own convention.

## When WeasyPrint is not the right tool

A chart that has to be computed in JS → headless Chrome (you lose the page numbers in the
table of contents). Formulas, standards-style layout → `typst`. A quick draft from existing
Markdown → `pandoc --pdf-engine=typst`. In every other case — WeasyPrint.
