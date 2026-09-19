#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One report, three languages — the language check for the skill.

    python3 examples/demo.py en | ru | zh  > demo-en.html
    ./scripts/build.sh demo-en.html docs/examples

Same numbers, same markup, same build. What changes is the language of the text,
`<html lang>`, the locale of the chart numbers and the typography of the prose.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "pdf-report", "assets"))
import charts as ch

NB = " "
MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"],
    "ru": ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен"],
    "zh": ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月"],
}
VISITS = [4.1, 3.8, 5.2, 6.0, 5.4, 4.9, 3.2, 3.6, 6.8]
SHELVES = [("fiction", 31.4), ("children", 22.8), ("science", 14.2),
           ("history", 9.6), ("art", 7.1), ("reference", 4.3)]

T = {
"en": dict(
  lang="en", sp=" ", title="City Library: nine months", kicker="QUARTERLY REVIEW",
  doctitle="City Library", docdate="Q1–Q3 2026",
  meta="Central branch and four reading rooms<br>January–September 2026 · 43,100 visits · 89,400 loans",
  foot="Demonstration document. The numbers are synthetic.",
  toc_h="Contents",
  toc=["What the numbers say", "Visits", "What people borrow", "Appendix"],
  s1="What the numbers say", sub1="Nine months against the same period last year",
  hero_l="of registered readers came in at least once",
  kpi=[("Visits", "43.1", "k"), ("Loans per visit", "2.07", ""), ("New cards", "1,940", "")],
  lead="September brought the busiest month of the year: 6,800 visits, a third of them on the "
       "three Saturdays after the school year started. The reading rooms ran at capacity twice.",
  p2="Growth did not come from events. Attendance at readings and workshops stayed flat at "
     "roughly 400 people a month, while ordinary weekday visits rose by a fifth.",
  call_h="What this costs.", call="Two of the four reading rooms have no free seats after "
     "16:00 on weekdays. Until that changes, further growth in visits turns into queueing, "
     "not into loans.",
  s2="Visits", sub2="Thousands of visits per month",
  c1t="Visits by month", c1c="One series, so no legend. The peak and the last value are labelled.",
  s3="What people borrow", sub3="Share of loans by shelf",
  c2t="Loans by shelf", c2c="Thousands of loans, January to September.",
  p3="Fiction and children's books make up 62% of everything borrowed. The science shelf grew "
     "fastest — up 40% — from the smallest base of the three.",
  s4="Appendix", sub4="Every number in the report",
  th=["Month", "Visits, k", "Loans, k"],
  note="Built with the pdf-report skill. Text in English, decimal point, no space before the "
       "percent sign: the typography follows the language of the report."),
"ru": dict(
  lang="ru", sp=" ", title="Городская библиотека — девять месяцев", kicker="КВАРТАЛЬНЫЙ ОБЗОР",
  doctitle="Городская библиотека", docdate="I–III кв. 2026",
  meta="Центральный филиал и четыре читальных зала<br>Январь—сентябрь 2026 · 43<span>&#8239;</span>100 посещений · 89<span>&#8239;</span>400 выдач",
  foot="Демонстрационный документ. Данные синтетические.",
  toc_h="Содержание",
  toc=["Что говорят цифры", "Посещения", "Что берут читать", "Приложение"],
  s1="Что говорят цифры", sub1="Девять месяцев против того же периода год назад",
  hero_l="записанных читателей пришли хотя бы раз",
  kpi=[("Посещений", "43.1", "тыс."), ("Выдач за визит", "2.07", ""), ("Новых билетов", "1940", "")],
  lead="Сентябрь стал самым людным месяцем года: 6800 посещений, треть из них — в три субботы "
       "после начала учебного года. Читальные залы дважды заполнялись до последнего места.",
  p2="Рост дали не мероприятия. На чтения и мастер-классы по-прежнему приходит около 400 человек "
     "в месяц, а обычные будние посещения выросли на пятую часть.",
  call_h="Чем это оборачивается.", call="В двух залах из четырёх после 16:00 в будни нет "
     "свободных мест. Пока это так, дальнейший рост посещений превращается в очередь, а не в выдачи.",
  s2="Посещения", sub2="Тысячи посещений в месяц",
  c1t="Посещения по месяцам", c1c="Одна серия — легенда не нужна. Подписаны пик и последнее значение.",
  s3="Что берут читать", sub3="Доля выдач по разделам",
  c2t="Выдачи по разделам", c2c="Тысячи выдач, январь—сентябрь.",
  p3="Проза и детские книги дают 62 % всех выдач. Быстрее всех вырос научный раздел — на 40 %, "
     "и при этом он стартовал с самой маленькой базы из трёх.",
  s4="Приложение", sub4="Все числа отчёта",
  th=["Месяц", "Посещений, тыс.", "Выдач, тыс."],
  note="Собрано скилом pdf-report. Текст по-русски, десятичная запятая, неразрывный пробел "
       "перед знаком процента — типографика следует языку отчёта."),
"zh": dict(
  lang="zh", sp="", title="市图书馆——九个月", kicker="季度回顾",
  doctitle="市图书馆", docdate="2026年第一至三季度",
  meta="中心馆与四个阅览室<br>2026年1月至9月 · 43,100人次 · 89,400册次",
  foot="演示文档，数据为虚构。",
  toc_h="目录",
  toc=["数字说明了什么", "到馆人次", "读者借什么", "附录"],
  s1="数字说明了什么", sub1="九个月，与去年同期相比",
  hero_l="的注册读者至少到馆一次",
  kpi=[("到馆人次", "43.1", "千"), ("每次借阅量", "2.07", ""), ("新办证", "1,940", "")],
  lead="九月是全年最忙的一个月：6,800人次，其中三分之一集中在开学后的三个周六。阅览室两次坐满。",
  p2="增长并非来自活动。讲座和工作坊的参与人数仍在每月400人左右，而平日的普通到馆量上升了五分之一。",
  call_h="代价在哪里。", call="四个阅览室中有两个，工作日16:00之后已无空位。这一点不改，"
     "到馆人次继续上涨只会变成排队，而不是借阅。",
  s2="到馆人次", sub2="每月到馆人次（千）",
  c1t="各月到馆人次", c1c="只有一条序列，无需图例。已标注峰值与末值。",
  s3="读者借什么", sub3="各类别借阅占比",
  c2t="各类别借阅量", c2c="1月至9月借阅量（千册次）。",
  p3="文学与少儿图书占全部借阅的62%。增长最快的是科学类，上升40%，而它的基数在三者中最小。",
  s4="附录", sub4="报告中的全部数字",
  th=["月份", "到馆（千）", "借阅（千）"],
  note="由 pdf-report 技能生成。正文为中文，小数点、百分号前不加空格，全角标点——"
       "排版规则跟随报告的语言。"),
}


def build(lang):
    t = T[lang]
    ch.set_locale(lang)
    m = MONTHS[lang]
    shelf_names = {
        "en": ["fiction", "children", "science", "history", "art", "reference"],
        "ru": ["проза", "детские", "научные", "история", "искусство", "справочники"],
        "zh": ["文学", "少儿", "科学", "历史", "艺术", "工具书"],
    }[lang]
    loans = [(n, v) for n, (_, v) in zip(shelf_names, SHELVES)]
    rows = "".join(
        f"<tr><td>{mm}</td><td class='num'>{ch.num(v, 1)}</td>"
        f"<td class='num'>{ch.num(v * 2.07, 1)}</td></tr>"
        for mm, v in zip(m, VISITS))
    kpis = "".join(
        f'<div class="kpi"><div class="lbl">{k}</div>'
        f'<div class="val">{v}<span class="u">{u}</span></div></div>'
        for k, v, u in t["kpi"])
    toc = "".join(
        f'<li data-t="#s{i+1}"><span class="n">0{i+1}</span>'
        f'<span class="t">{s}</span><span class="dots"></span></li>'
        for i, s in enumerate(t["toc"]))

    return f"""<!doctype html><html lang="{t['lang']}"><head><meta charset="utf-8">
<title>{t['title']}</title>
<style>:root{{ --doctitle:"{t['doctitle']}"; --docdate:"{t['docdate']}" }}</style>
</head><body>
<section class="cover">
<div class="txt">
  <div class="kicker">{t['kicker']}</div>
  <h1>{t['title']}</h1>
  <div class="bar"></div>
  <div class="meta">{t['meta']}</div>
</div>
<div class="foot">{t['foot']}</div>
</section>

<section class="toc"><h3>{t['toc_h']}</h3><ol>{toc}</ol></section>

<section class="sec"><div class="num-lbl">01</div><h1 id="s1">{t['s1']}</h1>
<div class="sub">{t['sub1']}</div>
<div class="hero"><div class="v">68{ch.PCT_SP}%</div><div class="l">{t['hero_l']}</div></div>
<div class="kpis">{kpis}</div>
<p class="lead">{t['lead']}</p>
<p>{t['p2']}</p>
<div class="callout warn"><p><span class="h">{t['call_h']}</span>{t['sp']}{t['call']}</p></div>
</section>

<section class="sec"><div class="num-lbl">02</div><h1 id="s2">{t['s2']}</h1>
<div class="sub">{t['sub2']}</div>
<div class="card"><div class="ttl">{t['c1t']}</div>
<div class="cap">{t['c1c']}</div>
{ch.area_line(m, VISITS, 8, label_idx=[8])}
</div>
</section>

<section class="sec"><div class="num-lbl">03</div><h1 id="s3">{t['s3']}</h1>
<div class="sub">{t['sub3']}</div>
<div class="card"><div class="ttl">{t['c2t']}</div>
<div class="cap">{t['c2c']}</div>
{ch.hbars(loans, unit="", lw=110, nd=1)}
</div>
<p>{t['p3']}</p>
</section>

<section class="sec"><div class="num-lbl">04</div><h1 id="s4">{t['s4']}</h1>
<div class="sub">{t['sub4']}</div>
<table class="dense"><thead><tr><th>{t['th'][0]}</th><th class="num">{t['th'][1]}</th>
<th class="num">{t['th'][2]}</th></tr></thead><tbody>{rows}</tbody></table>
<p class="sub">{t['note']}</p>
</section>
</body></html>"""


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    if lang not in T:
        sys.exit(f"languages: {', '.join(T)}")
    sys.stdout.write(build(lang))
