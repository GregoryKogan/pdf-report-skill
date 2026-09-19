#!/bin/bash
# check.sh <file.pdf> [page] — the mandatory check before handing the file over.
# Exports the pages as PNG next to the PDF: you MUST open them and look.
set -euo pipefail
export PATH=/opt/homebrew/bin:$PATH        # macOS: a GUI context does not see brew
F="$1"; D="$(dirname "$F")/$(basename "${F%.*}")-pages"
echo "── metadata ──"; pdfinfo "$F" | grep -E "^(Title|Pages|Page size)"
echo "── fonts (emb=yes sub=yes on all of ours; foreign names are inert WeasyPrint ballast, nothing to fix) ──"
pdffonts "$F" | tail -n +3 | awk '{printf "  %-30s emb=%s sub=%s\n",$1,$(NF-4),$(NF-3)}'
echo "── bookmarks ──"
qpdf --json --json-key=outlines "$F" | python3 -c "
import json,sys
o=json.load(sys.stdin)['outlines']
def total(i): return 1+sum(total(k) for k in i.get('kids',[]))
top=', '.join(f\"{i['title']}→{i['destpageposfrom1']}\" for i in o)
print(f'  {sum(total(i) for i in o)} on all levels · top level: {top}' if o
      else '  NONE — check h1/h2')"
# head closes the pipe early: without the guard, SIGPIPE + pipefail kills the script
# here, and the PNG export below never runs — silently skipping the mandatory look.
echo "── text outside the column ──"; python3 "$(dirname "${BASH_SOURCE[0]}")/overflow.py" "$F" || true
echo "── text extracts ──"; { pdftotext "$F" - | tr -s '\n' ' ' | head -c 120; } || true; echo
mkdir -p "$D"; pdftoppm -png -r 110 "$F" "$D/p"
# `[ … ] && P=…` returns 1 whenever the test is false, which set -e treats as failure
N=$(pdfinfo "$F" | awk '/^Pages/{print $2}'); P="${2:-3}"; if [ "$P" -gt "$N" ]; then P="$N"; fi
pdftoppm -png -scale-to-x 390 -scale-to-y -1 -f "$P" -l "$P" "$F" "$D/phone"
echo "── pages exported to $D/ (looking at them is MANDATORY, phone-*.png included) ──"
