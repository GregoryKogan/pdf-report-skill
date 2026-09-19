#!/bin/bash
# prose-check.sh <file.pdf|file.html> [--lang ru|en|zh] — candidates for traces of
# machine writing. The language is detected from the text unless given explicitly.
#
# This is NOT a verdict: the humanizer explicitly warns against mechanical matches.
# The script points at places to look at; the decision is always a human's.
set -uo pipefail
export PATH=/opt/homebrew/bin:$PATH        # macOS: a GUI context does not see brew
F="${1:?usage: prose-check.sh <file.pdf|file.html> [--lang ru|en|zh]}"
LANG_OPT=""
[ "${2:-}" = "--lang" ] && LANG_OPT="${3:-}"
case "$F" in
  *.pdf)  TXT="$(pdftotext "$F" - 2>/dev/null)" ;;
  *)      TXT="$(sed -e 's/<[^>]*>/ /g' "$F")" ;;
esac
TXT="$(printf '%s' "$TXT" | tr -s ' \n' ' ')"

# Language by dominant script: Cyrillic -> ru, Han -> zh, otherwise en.
if [ -z "$LANG_OPT" ]; then
  LANG_OPT=$(printf '%s' "$TXT" | python3 -c '
import sys, unicodedata as u
t = sys.stdin.read()
c = sum(1 for ch in t if "Ѐ" <= ch <= "ӿ")
j = sum(1 for ch in t if "一" <= ch <= "鿿")
print("zh" if j > 40 else "ru" if c > 40 else "en")')
fi
echo "language: $LANG_OPT"

hit(){ # $1 — label, $2 — regex
  local n; n=$(printf '%s' "$TXT" | grep -oiE "$2" | wc -l | tr -d ' ')
  [ "$n" -gt 0 ] && { printf '  %-34s %2d  ' "$1" "$n"
    printf '%s' "$TXT" | grep -oiE ".{0,26}(${2}).{0,26}" | head -2 | tr '\n' '|' ; echo; }
  return 0
}

echo "── candidates (§ humanizer) ──"
case "$LANG_OPT" in
ru)
  hit "filler §23"            "в рамках (проведённ|данн)|следует отметить|важно (отметить|подчеркнуть)|стоит отметить|в конечном (счёте|итоге)|в связи с тем"
  hit "inflated claims §1,§4"  "впечатляющ|кардинальн|прорыв|открывает нов|играет (ключевую|важную) роль|поистине|беспрецедент"
  hit "stock phrases §7"              "ключев(ым|ой) драйвер|синерги|экосистем[ае] (решений|продуктов)|в сфере|ландшафт"
  hit "\"not just X, but Y\" §9"  "не просто [^.,]{2,30}, а |не только [^.,]{2,40}, но и"
  hit "participial tail §3"        "позволяя|обеспечивая|подчёркивая|демонстрируя|отражая|способствуя"
  hit "stock ending §25"  "говорят сами за себя|время покажет|в правильном направлении|светло|многообещающ"
  hit "deep truth §27"    "по сути|на самом деле|в действительности|главный вопрос в том"
  hit "next-section trailer §28"   "давайте (разберём|рассмотрим)|рассмотрим подробнее|стоит начать с|перейдём к"
  hit "corporate voice §13"         "было принято решение|осуществля(ется|ются)|производится|имеет место"
  ;;
en)
  hit "filler §23"             "it('s| is) worth noting|it should be noted|in order to|due to the fact that|at the end of the day"
  hit "inflated claims §1,§4"  "groundbreaking|revolutioniz|game.chang|cutting.edge|unprecedented|pivotal|profound|transformative"
  hit "stock words §7"         "delve|leverag|robust|seamless|meticulous|underscore|tapestry|realm|landscape of|testament to"
  hit "\"not just X, but Y\" §9" "not (just|only) [^.,]{2,40}, (but|it)"
  hit "participial tail §3"    "allowing (it|them|you) to|ensuring that|highlighting the|showcasing|reflecting the|underscoring"
  hit "stock ending §25"       "speaks for itself|time will tell|in the right direction|the future looks|exciting times"
  hit "deep truth §27"         "at its core|in essence|the real question is|fundamentally, "
  hit "next-section trailer §28" "let('s| us) (explore|dive|take a look)|we will explore|stay tuned|but first"
  hit "corporate voice §13"    "a decision was made|is being (carried|performed)|plays a (key|vital) role"
  ;;
zh)
  hit "cliche 套话 §23"               "值得注意的是|需要指出的是|众所周知|综上所述|总而言之|在当今|随着.{0,6}的(不断)?发展"
  hit "inflated 夸大 §1,§4"             "颠覆性|革命性|前所未有|极大地提升|显著改善|全方位|深度赋能|里程碑"
  hit "jargon 黑话 §7"                "赋能|抓手|闭环|生态(体系|圈)|打法|沉淀|链路|心智|对齐颗粒度"
  hit "not-just 不仅…而且 §9"        "不仅[^。，]{2,30}(而且|还)|不只是[^。，]{2,30}(而是|更是)"
  hit "rule of three 排比三连 §26"           "(首先|一方面)[^。]{2,40}(其次|另一方面)[^。]{2,40}(最后|再者)"
  hit "stock ending 结尾套话 §25"           "让我们(一起)?(期待|拭目以待)|未来可期|不言而喻|道阻且长"
  hit "empty verbs 空洞动词 §13"           "打造|助力|聚焦|发力|布局|持续(优化|迭代)"
  ;;
esac
hit "emoji §18"      "[😀-🿿🚀-🛿☀-➿]"

echo "── typography (here an error IS an error) ──"
case "$LANG_OPT" in
ru)
  # a decimal period is intentional here — see "Typography by language" in SKILL.md
  hit "decimal comma (a period is the house style)"   "[0-9],[0-9]([^0-9]|$)"
  hit "straight quotes (ru wants guillemets)"         "\"[А-Яа-я]"
  ;;
en)
  hit "decimal comma"          "[0-9],[0-9]([^0-9]|$)"
  hit "em-dash density"        " — "
  ;;
zh)
  hit "half-width punctuation 半角标点"                "[一-龥][,;:!?]|[,;:!?][一-龥]"
  hit "half-width brackets 半角括号"                "[一-龥]\(|\)[一-龥]"
  hit "straight quotes 直角引号缺失"            "\"[一-龥]"
  ;;
esac
echo "(nothing above = clean)"
