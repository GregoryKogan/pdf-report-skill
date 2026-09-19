#!/usr/bin/env python3
"""Finds the height of a single page such that the whole document fits without breaks.

Binary search over the height: the width is fixed, so the layout does not depend on the
height — only the number of pages does. We look for the smallest height that still gives
one page. The PDF limit is 14400 pt (5080 mm); past that we return exit code 3.
"""
import sys, argparse
from weasyprint import HTML, CSS

ap = argparse.ArgumentParser()
ap.add_argument("html"); ap.add_argument("out")
ap.add_argument("--css", nargs="*", default=[])
ap.add_argument("--width", default="148mm")
ap.add_argument("--tol", type=float, default=2.0, help="fitting tolerance, mm")
a = ap.parse_args()

doc_html = HTML(filename=a.html)
sheets = [CSS(filename=c) for c in a.css]
LIMIT = 5080.0

def pages(h_mm):
    css = CSS(string=f"@page{{ size:{a.width} {h_mm:.1f}mm }}")
    return len(doc_html.render(stylesheets=sheets + [css]).pages)

if pages(LIMIT) > 1:
    print("TOO LONG: the content does not fit in 5080 mm — build it paginated", file=sys.stderr)
    sys.exit(3)

lo, hi = 60.0, LIMIT
while hi - lo > a.tol:
    mid = (lo + hi) / 2
    if pages(mid) == 1: hi = mid
    else:               lo = mid

css = CSS(string=f"@page{{ size:{a.width} {hi:.1f}mm }}")
doc_html.render(stylesheets=sheets + [css]).write_pdf(a.out)
print(f"{hi:.0f}")
