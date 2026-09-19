# Markup: the classes base.css understands

The HTML carries **content and classes only**. Do not write your own CSS — if the class you
need is missing, add it to `assets/base.css` rather than a `<style>` block in the document.

## Style layers
`base.css` (structure) → theme (`nord-dark.css` by default | `light.css`; **text colour and
typeface**, but not the definitions of the font stacks — those live in base.css) → format
(`a4.css` | `mobile.css`, geometry and font size only). `scripts/build.sh` assembles them.

The only things that live in the document itself are the language and the tokens:
```html
<html lang="ru">      <!-- hyphenation, CJK line breaking, font fallback -->
<style>:root{ --doctitle:"Title";     /* left running head */
              --docdate:"Q3 2025" }   /* right running head */
</style>
```
The theme sets the text typeface (`--body-font`: grotesque in Nord, antiqua in light) — do not
override it in the document.
**Do not redefine `@page` in the document** — the rule will override
`@page cover{@top-left{content:none}}` from base.css and the running head will break through
onto the cover. That is what `--doctitle` is for.

| Block | Markup |
|---|---|
| Cover | `<section class="cover">` + `.kicker`, `<h1>`, `.bar`, `.meta`, `.foot` |
| Cover with artwork | `<section class="cover art" style="--aur-h:62mm">` + `<svg class="aur">`; see the zone rule below |
| Table of contents | `<nav class="toc">` → `<li data-t="#s1"><a href="#s1">…</a><span class="dots"></span></li>`; `target-counter` computes the page number |
| Hero number | `.hero` → `.v` (number), `.l` (caption). **One per document** |
| Tiles | `.kpis` → `.kpi` → `.lbl`, `.val` (+`.u` for the unit), `.dlt` + `.up`/`.down`/`.flat` |
| Callout | `.callout` (+`.warn`, `.crit`), inside it `<span class="h">Heading.</span>` |
| Chart card | `.card` → `.ttl`, `.cap`, then the SVG |
| Legend | `.legend` → `.lg` → `<i style="background:…">` + text |
| Table | a plain `table` (+`.dense`, `.wide`), number cells get `.num` |
| Timeline | `.tl` → `.e` with `style="--dot:colour"` → `.d`, `.h`, `.b`. **Strictly in ascending date order** |
| Meter | `.goal` → `.r` (label + values), `.track` → `<i style="width:…">` + `<u style="left:…">` (plan tick) |
| Code | `<pre><code class="language-python">` — see below; without the class the block stays plain |
| Breaks | `.sec` — section on a new page; `.pagebreak`, `.keep` |

## Code blocks: tag the language, and wrap the long lines yourself

`build.sh` runs `scripts/highlight.py` over the document before rendering: every
`<pre><code class="language-XXX">` comes out with Pygments token spans, coloured from the
theme. Any name Pygments knows works — `python`, `yaml`, `json`, `bash`, `sql`, `go`, `diff`.
The palette is Nord in both themes, with each hue moved until it clears 4.5:1 on the code
background; the stock Pygments `nord` style assumes a darker background and its comment
colour measures 1.96:1 on ours, which is why the colours live in the theme files instead.

**Highlighting is opt-in per block, deliberately.** A guessed lexer mangles exactly the
blocks a report leans on — console transcripts, pseudo-output, before/after sketches — and a
wrong guess reads as meaning. Leave those blocks untagged and they render as plain text.

**A highlighted line will not wrap.** WeasyPrint does not break between inline boxes, and
highlighting turns the line into a row of them, so a line too long for the column runs off
the page instead of folding (see `gotchas.md`). Wrap long lines in the source the way the
language would:

```
tasks.append(asyncio.create_task(          ← not one 74-character line
    proxy_logging_obj.during_call_hook(...)))
```

What has to fit is not the line but its **longest run without a space** — spaces still break
normally, so an 78-character line full of spaces is fine while a 74-character identifier is
not. Measured on a book column (120 mm): about 70 characters of unbroken run fit, ~80 on a
scroll (136 mm). You do not have to count: `build.sh` measures the rendered PDF and names any
line that ended up outside the column, with how far out it went.

## Cover with artwork: two zones that never overlap

`--aur-h` sets the height of the artwork zone. `base.css` pushes the text down by
`--aur-h + 12mm` on its own, so **do not touch the cover's `padding-top` by hand** — the text
will ride onto the artwork.

Two rules for the SVG itself:
- **No fills with a hard bottom edge.** A semi-transparent rectangle that stops in the middle
  of the cover reads as a seam, especially with cards right underneath. Build the fade from
  butted layers with falling opacity (see `gotchas.md` on moiré).
- **The drawing must end before its zone does.** Leave the bottom 20–30 % of the SVG height
  empty: then the transition into the text smooths itself out.

Check it with your eyes on a crop:
`pdftoppm -png -r 100 -x 0 -y 0 -W 583 -H 780 x.pdf top`

## `.sec` — dose it, do not hang it on every section
On A5 the page is short: `.sec` on each of 10 sections gives you **five nearly empty pages**.
Force a break only before major parts (an appendix, a new chapter); let short sections flow,
separated by an `<hr>` or a heading. Verify on the exported PNGs: a page filled less than a
third of the way is a defect.

## Long tables
Breaking between rows is on by default and the header repeats itself. Nothing to do. The
opposite case is the one to mark: pin a short table you do not want broken with
`<table class="keep">`.

## What breaks silently
- **Flex squeezes legend swatches into sticks.** They need `flex:0 0 9px`, already in base.css.
- Text in `.lg` wraps mid-word without `white-space:nowrap` — also already there.
- A meter without a plan tick lies: overshoot and shortfall both look like a full bar. Scale to
  `max(actual, plan)` and put the tick on `plan`.
- A missing `lang` on `<html>` costs you hyphenation in Latin and Cyrillic, and correct line
  breaking in CJK. It is one attribute and it is not optional.
- Long unbroken strings (paths, IDs) push a table past the page edge. Insert soft breaks
  (`​`) after `/` and `_`, or the column will bleed off the sheet.
