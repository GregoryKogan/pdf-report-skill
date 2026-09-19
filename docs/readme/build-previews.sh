#!/bin/bash
# Rebuilds the README images from the example PDFs in docs/examples.
#   bash docs/readme/build-previews.sh
set -euo pipefail
export PATH=/opt/homebrew/bin:$PATH
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT"

for l in en ru zh; do
  python3 examples/demo.py "$l" > "/tmp/demo-$l.html"
  skills/pdf-report/scripts/build.sh "/tmp/demo-$l.html" docs/examples >/dev/null
done
skills/pdf-report/scripts/build.sh skills/pdf-report/assets/example-dark.html docs/examples >/dev/null

python3 "$HERE/compose.py"
echo "docs/readme/*.png rebuilt"
