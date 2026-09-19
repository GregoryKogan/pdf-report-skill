#!/bin/bash
# build.sh <report.html> [outdir] [flags]
#
# DEFAULT: Nord dark theme + "scroll" format (ONE page, no breaks) + one file.
# Flags exist only to depart from the default:
#   --light   light theme instead of Nord
#   --a5      paginated A5 (when you need running heads and page numbers)
#   --a4      paginated A4, for print
#   --both    A4 and A5 as two files
#   --book    book layout (A5, chapter running head, table breaking)
# A scroll longer than the PDF limit falls back to book layout automatically.
set -euo pipefail
export PATH=/opt/homebrew/bin:$PATH        # macOS: a GUI context does not see brew
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; A="$(cd "$HERE/../assets" && pwd)"
# A python that can import weasyprint. Name your own in PDFREPORT_PYTHON.
pick_python(){
  for p in "${PDFREPORT_PYTHON:-}" python3 /opt/homebrew/opt/weasyprint/libexec/bin/python; do
    [ -n "$p" ] && command -v "$p" >/dev/null 2>&1 &&
      "$p" -c "import weasyprint" 2>/dev/null && { echo "$p"; return; }
  done
  echo "no python with weasyprint; install it or set PDFREPORT_PYTHON" >&2; exit 4
}
SRC=""; OUT=""; THEME="nord-dark.css"; MODE="scroll"
for arg in "$@"; do case "$arg" in
  --light) THEME="light.css" ;;  --dark) THEME="nord-dark.css" ;;
  --a5) MODE="a5" ;;  --a4) MODE="a4" ;;  --both) MODE="both" ;;
  --scroll) MODE="scroll" ;;  --book) MODE="book" ;;
  --*) echo "unknown flag: $arg" >&2; exit 2 ;;
  *) if [ -z "$SRC" ]; then SRC="$arg"; else OUT="$arg"; fi ;;
esac; done
[ -n "$SRC" ] || { sed -n '2,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' >&2; exit 2; }
OUT="${OUT:-$(dirname "$SRC")}"; NAME="$(basename "${SRC%.*}")"
paged(){ weasyprint "$SRC" "$2" -s "$A/base.css" -s "$A/$THEME" -s "$A/$1"; }
report(){ printf '%-40s %s pages, %s KB%s\n' "$(basename "$1")" \
  "$(pdfinfo "$1" | awk '/^Pages/{print $2}')" \
  "$(( $(stat -f%z "$1" 2>/dev/null || stat -c%s "$1")/1024 ))" "${2:-}"; }
echo "theme: ${THEME%.css}"
case "$MODE" in
  scroll)
    if H=$("$(pick_python)" "$HERE/fit-scroll.py" "$SRC" "$OUT/$NAME.pdf" \
             --css "$A/base.css" "$A/$THEME" "$A/scroll.css" --width 136mm 2>/dev/null); then
      report "$OUT/$NAME.pdf" " — scroll $H mm, no breaks"
    else
      echo "document longer than the scroll limit (5080 mm) — switching to book layout" >&2
      paged book.css "$OUT/$NAME.pdf"; report "$OUT/$NAME.pdf" " — book"
    fi ;;
  a5)   paged mobile.css "$OUT/$NAME.pdf"; report "$OUT/$NAME.pdf" ;;
  book) paged book.css   "$OUT/$NAME.pdf"; report "$OUT/$NAME.pdf" " — book" ;;
  a4)   paged a4.css     "$OUT/$NAME.pdf"; report "$OUT/$NAME.pdf" ;;
  both) paged a4.css "$OUT/$NAME.pdf"; paged mobile.css "$OUT/$NAME-mobile.pdf"
        report "$OUT/$NAME.pdf"; report "$OUT/$NAME-mobile.pdf" ;;
esac
