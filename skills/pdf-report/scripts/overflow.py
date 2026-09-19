#!/usr/bin/env python3
"""overflow.py <file.pdf> [tolerance-pt] — finds content that runs outside the text column.

The defect this catches is invisible to every other check: a long unbreakable token — a
dotted identifier, a URL, a file path, an id in a table cell — pushes its line past the
column and into the margin. The PDF still renders, the text still extracts, and the page
looks fine in a thumbnail. Only a reader at full size sees the line hanging off the edge.

It is measured, not guessed. The column edges come from the document itself: the 2nd and
98th percentile of every word's x-coordinates, so the script needs no idea which layout,
page size or margins were used. Anything sticking out past that by more than the tolerance
(5 pt by default, about a character) is reported with its page and its text.

Those two numbers are tuned, not picked: at the 95th percentile the hyphenated words that
legitimately end at the right edge of a justified column sit ~4 pt outside the estimate and
drown the real defect in false positives. At the 98th, a 67-page report produced exactly one
hit — the real one, 15.6 pt out.

Word boxes come from `pdftotext -bbox`, so this needs poppler and nothing else.

Exit status: 0 when clean, 1 when something overflows — so a build script can gate on it.
"""
import re
import subprocess
import sys

WORD = re.compile(
    r'<word xMin="([\d.]+)" yMin="[\d.]+" xMax="([\d.]+)" yMax="[\d.]+">([^<]*)</word>'
)


def words(pdf: str) -> list[tuple[int, float, float, str]]:
    out = subprocess.run(
        ["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True
    ).stdout
    found = []
    for page_no, page in enumerate(re.split(r"<page ", out)[1:], 1):
        for x_min, x_max, text in WORD.findall(page):
            found.append((page_no, float(x_min), float(x_max), text))
    return found


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        return 2
    tol = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    found = words(sys.argv[1])
    if len(found) < 50:  # too little text to infer a column from
        print("  not enough text to measure a column — skipped")
        return 0

    def pct(values: list[float], p: float) -> float:
        ordered = sorted(values)
        return ordered[min(len(ordered) - 1, int(len(ordered) * p))]

    right = pct([w[2] for w in found], 0.98)
    left = pct([w[1] for w in found], 0.02)
    bad = [w for w in found if w[2] > right + tol or w[1] < left - tol]
    if not bad:
        print(f"  none — column {left:.0f}..{right:.0f} pt, {len(found)} words checked")
        return 0

    print(f"  {len(bad)} past the column ({left:.0f}..{right:.0f} pt):")
    for page_no, x_min, x_max, text in bad[:20]:
        over = x_max - right if x_max > right + tol else left - x_min
        print(f"    p.{page_no:<4} {over:+6.1f} pt  {text[:64]}")
    if len(bad) > 20:
        print(f"    … and {len(bad) - 20} more")
    print("  fix the source, not the symptom — rewrap the long line or shorten the token.")
    print("  base.css already wraps plain code and prose, so a hit here is usually one of:")
    print("  a highlighted code line (WeasyPrint will not break inside Pygments' spans),")
    print("  an SVG drawn wider than its box, or an image.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
