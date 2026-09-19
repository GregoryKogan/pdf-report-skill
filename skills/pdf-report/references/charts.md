# Charts in a PDF

**Load the `dataviz` skill first** (it ships with Claude Code; skip it if your runtime has no
such skill). What follows are only the corrections for print.

## API of assets/charts.py
```python
import sys; sys.path.insert(0, "<path to assets>")
from charts import *
area_line(labels, vals, ymax, unit="", label_idx=[6,11])   # area + line, selective labels
stacked_cols(labels, [s1,s2,s3], [C1,C2,C3], ymax)          # stack, total above the column
heatmap(rows, months)          # rows: 0=empty, 1..4=ramp, None=no cell at all
polar(vals24)                  # rose by hour
share_bar(items, colors)       # 100% bar; draw the legend in HTML!
spark(vals)                    # sparkline for a table cell
scatter([(name,pts),…], colors)
multi_line(xs, [(name,vals),…], colors, ymax=, xlabel=)   # continuous axis, ≤4 series
treemap([(group,[(child,value),…]),…])                    # nested, area == value
hbars([(label,value),…], unit="", lw=150, nd=1)           # horizontal bars, value at the end
threshold(x_frac, "ceiling 750")                          # hairline threshold; insert
                                                          # AFTER the grid, BEFORE the marks
```

**The shape you need is missing?** Write it in **your own** generator on top of the module's
primitives and leave the skill's files alone — otherwise the next report inherits an edit made
for somebody else's task. If the shape earns its keep twice, then move it into `charts.py`.

**The viewBox is 420 wide, not 520.** Both formats are built from the same HTML, and the
physical size of a label depends on the format: one viewBox unit on A5 is almost half of what
it is on A4.

| viewBox | 9.5-unit label on A4 | on A5 |
|---|---|---|
| 520 | 8.0 pt | **5.9 pt — unreadable** |
| 420 | 9.9 pt | 7.3 pt |

Do not go below 6.5 pt in print. At 420 the gap inside a stack is 2.0 units and the mark
thickness limit is 23 units (the same 24 px). The defaults in `charts.py` are already those.

## Corrections for print
- **Style SVG with presentation attributes only** (`font-family=`, `fill=`, `stroke=`): CSS
  does not cascade into inline SVG and the text falls back to black defaults.
- **There is no hover.** A value has to be readable off the mark, off an axis, or out of the
  summary table in the appendix. A table with every number is not optional — it replaces the
  tooltip.
- **The legend goes in HTML** (`.legend`), not in the SVG: you cannot measure text width in
  SVG, so labels run off the edge.
- A legend is mandatory from 2 series up; with a single series leave it out — the card title
  already says what is drawn.
- Mark thickness ≤ 27 viewBox units (that is 24 px), 2 px gap inside a stack in the surface
  colour, round only the outer end.
- The grid is a solid hairline one step off the surface, never a dashed line.
- Labels are clipped with an ellipsis (`clip()`), never cut mid-word in silence.

## Numbers
**Numbers look the same in every language** — a period for the decimal separator and no space
before `%` — including the languages that write a comma and a space in running text. A chart
is read next to code, tables and other languages, and one notation is one ambiguity less.
There is nothing to configure: `num()` writes them that way and never switches.

That covers everything the module prints itself: axis labels, values at the end of bars,
percentages in the 100% bar. Numbers you format in your own generator are your own
responsibility — write them the same way, or one document will show two notations.

## Palette on dark
Nord as shipped does not pass `validate_palette.js`: chroma below the floor, worst pair at
ΔE 9.1 against a threshold of 15. The working set (Nord hues, chroma raised exactly to the
0.10 floor) is already in `nord-dark.css`:
`#60c4de #d4af62 #b77bad #9ec27e #c9785f` — ΔE 18.8 normal vision / 11.7 CVD.
The first three also pass `--pairs all` — do not take more than three series for a scatter.

The "strictly inside the lightness band" variant was tested and turned out **worse**: ΔE under
CVD dropped to 2.8. The formal checkmark and real distinguishability diverge here — choose
distinguishability.
