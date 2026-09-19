#!/usr/bin/env python3
"""highlight.py <in.html> [out.html] — syntax highlighting for the document's code blocks.

Rewrites every <pre><code class="language-XXX"> … </code></pre> into the same block with
Pygments token spans inside, prefixed `tok-` so they cannot collide with the document's
own classes. The colours live in the theme (see base.css); this script only marks up.

Highlighting is opt-in per block, by design. Guessing the lexer would mangle exactly the
blocks a teaching report leans on — console transcripts, pseudo-output, before/after
sketches — and a wrong guess is worse than no colour at all, because it reads as meaning.
A block with no language class is passed through untouched.

Without Pygments installed, or on a lexer it does not know, the block is left as it was and
the build carries on: colour is a nicety, the report is not.

build.sh runs this automatically; run it by hand only to inspect the intermediate HTML.
"""
import html
import re
import sys

BLOCK = re.compile(
    r'(<pre[^>]*>\s*<code[^>]*\bclass="(?:language|lang)-([\w+#-]+)"[^>]*>)(.*?)(</code>\s*</pre>)',
    re.S,
)


def highlight(doc: str) -> tuple[str, int, set[str]]:
    """Returns (rewritten html, blocks highlighted, languages that had no lexer)."""
    try:
        from pygments import highlight as pyg_highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import get_lexer_by_name
        from pygments.util import ClassNotFound
    except ImportError:
        return doc, 0, {"<pygments not installed>"}

    formatter = HtmlFormatter(nowrap=True, classprefix="tok-")
    done, unknown = 0, set()

    def one(m: re.Match) -> str:
        nonlocal done
        open_tag, lang, body, close_tag = m.groups()
        try:
            lexer = get_lexer_by_name(lang, stripnl=False, ensurenl=False)
        except ClassNotFound:
            unknown.add(lang)
            return m.group(0)
        # The source in the file is HTML-escaped; the lexer needs the real characters,
        # and Pygments escapes them again on the way out.
        marked = pyg_highlight(html.unescape(body), lexer, formatter)
        done += 1
        return f"{open_tag}{marked.rstrip(chr(10))}{close_tag}"

    return BLOCK.sub(one, doc), done, unknown


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        return 2
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src
    with open(src, encoding="utf-8") as fh:
        doc = fh.read()
    out, done, unknown = highlight(doc)
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(out)
    if unknown:
        print(f"highlight: no lexer for {', '.join(sorted(unknown))} — left plain", file=sys.stderr)
    print(f"highlight: {done} block(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
