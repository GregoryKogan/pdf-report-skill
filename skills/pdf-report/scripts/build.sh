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
# pick_python <module> — prints a python that can import it. Name your own in PDFREPORT_PYTHON.
pick_python(){
  local m="$1" p
  for p in "${PDFREPORT_PYTHON:-}" python3 /opt/homebrew/opt/weasyprint/libexec/bin/python; do
    [ -n "$p" ] && command -v "$p" >/dev/null 2>&1 &&
      "$p" -c "import $m" 2>/dev/null && { echo "$p"; return 0; }
  done
  return 1
}
need_weasyprint(){
  pick_python weasyprint ||
    { echo "no python with weasyprint; install it or set PDFREPORT_PYTHON" >&2; exit 4; }
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
# Syntax highlighting, if the document asked for it. The intermediate file is written next
# to the source so that relative URLs (images, fonts) still resolve, and removed on exit.
if grep -q 'class="\(language\|lang\)-' "$SRC" 2>/dev/null; then
  if HL="$(pick_python pygments)"; then
    TMP="$(dirname "$SRC")/.$NAME.highlighted.html"
    trap 'rm -f "$TMP"' EXIT
    "$HL" "$HERE/highlight.py" "$SRC" "$TMP"; SRC="$TMP"
  else
    echo "code blocks are tagged with a language but pygments is missing:" >&2
    echo "  pip install pygments   — building without highlighting" >&2
  fi
fi
paged(){ weasyprint "$SRC" "$2" -s "$A/base.css" -s "$A/$THEME" -s "$A/$1"; }
report(){ printf '%-40s %s pages, %s KB%s\n' "$(basename "$1")" \
  "$(pdfinfo "$1" | awk '/^Pages/{print $2}')" \
  "$(( $(stat -f%z "$1" 2>/dev/null || stat -c%s "$1")/1024 ))" "${2:-}"
  # Overflow is silent in a PDF — nothing errors, the text still extracts, and it does not
  # show at thumbnail size. Reporting it here means you cannot ship it without having read
  # it: the build is the one output nobody skips.
  python3 "$HERE/overflow.py" "$1" >/tmp/ow.$$ 2>/dev/null || {
    echo "!! content runs outside the text column:" >&2; cat /tmp/ow.$$ >&2; }
  rm -f /tmp/ow.$$; }
echo "theme: ${THEME%.css}"
case "$MODE" in
  scroll)
    if H=$("$(need_weasyprint)" "$HERE/fit-scroll.py" "$SRC" "$OUT/$NAME.pdf" \
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
