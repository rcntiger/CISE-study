#!/usr/bin/env python3
"""study-plan/*.md → sanan-notes HTML 페이지 생성 (한능검 노트와 같은 종이 노트 스타일)."""
import html, re, sys, json, os, base64, secrets
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

SUBJECTS = {
    1: ("산업재해 예방 및 안전보건교육", "var(--c1)"),
    2: ("인간공학 및 위험성 평가·관리", "var(--c2)"),
    3: ("기계·기구 및 설비 안전관리", "var(--c3)"),
    4: ("전기설비 안전관리", "var(--c4)"),
    5: ("화학설비 안전관리", "var(--c5)"),
    6: ("건설공사 안전관리", "var(--c6)"),
}
BLURB = {
    1: "재해 이론·통계 계산, 안전보건관리체제, 보호구·표지, 산업심리, 안전보건교육",
    2: "인간-기계 체계, 신뢰도·FTA 계산, HAZOP, 인체측정, 근골격계, 위험성 평가",
    3: "위험점·방호장치, 프레스·롤러·연삭기 수치, 양중기·지게차, 보일러, 비파괴검사",
    4: "감전·심실세동 계산, 누전차단기, KEC 접지, 정전기, 방폭·온도등급 — 과락 위험 1순위",
    5: "인화점·폭발범위·위험도 계산, 위험물질 분류, 안전밸브·파열판, 소화, PSM·MSDS",
    6: "산업안전보건관리비, 굴착 기울기, 흙막이, 추락방지·비계, 거푸집·철골, 해체공사",
}

CSS = """
:root{
  --bg:#F3F5F8;--surface:#FFFFFF;--surface2:#F7F8FA;--ink:#121A24;--ink-soft:#5A6573;--line:#E3E7EC;
  --hero:#1C2733;--hero-ink:#F4F6F8;--hero-soft:#AEB8C4;
  --yellow:#FFC21A;--yellow-soft:#FFF3C9;--mark:#FFE58A;
  --c1:#1F9D6B;--c2:#2F6FDE;--c3:#5B6B7E;--c4:#E0482E;--c5:#8A4FD8;--c6:#E07B12;--c7:#0E8A9A;--c8:#C2416B;
  --shadow:0 1px 2px rgba(16,24,40,.06),0 4px 14px rgba(16,24,40,.06);
  --cf:#6D3FD1;--cf-soft:#F1EBFF;--exp:#16865F;--exp-soft:#E7F6EF;
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0F151C;--surface:#18212B;--surface2:#1E2833;--ink:#E8EDF2;--ink-soft:#9AA6B4;--line:#2A3541;
    --hero:#141C25;--yellow-soft:#3A3115;--mark:#5C4A12;--shadow:none;
    --cf:#B79CFF;--cf-soft:#2A2340;--exp:#5EC2A0;--exp-soft:#16302A;
  }
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--ink);font-family:'IBM Plex Sans KR','Noto Sans KR',sans-serif;font-size:15px;line-height:1.7;font-variant-numeric:tabular-nums}
.wrap{max-width:720px;margin:0 auto;padding:0 16px 72px}
header{margin:0 -16px;padding:18px 20px 22px;background:var(--hero);color:var(--hero-ink);border-radius:0 0 22px 22px;position:relative;overflow:hidden}
header::before{content:"";position:absolute;left:0;right:0;top:0;height:6px;background:repeating-linear-gradient(-45deg,var(--yellow) 0 12px,#111 12px 24px)}
.back{display:inline-block;margin:6px 0 14px;font-size:12.5px;color:var(--hero-ink);text-decoration:none;background:rgba(255,255,255,.1);padding:4px 12px;border-radius:999px}
.tab{display:inline-block;margin-left:6px;font-size:11.5px;font-weight:700;color:#111;background:var(--accent,var(--yellow));padding:3px 10px;border-radius:999px;vertical-align:1px}
.eyebrow{font-size:12px;font-weight:600;color:var(--yellow);letter-spacing:.06em;margin:0 0 6px}
h1{font-weight:700;font-size:clamp(24px,6.6vw,34px);margin:0 0 10px;line-height:1.3;letter-spacing:-.02em}
.sub{font-size:13px;color:var(--hero-soft);margin:0;padding-left:18px}
.sub li{margin-bottom:2px}
.sub b{color:var(--hero-ink)}
.toc{display:flex;gap:6px;overflow-x:auto;margin:16px -20px -4px;padding:2px 20px 6px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.toc::-webkit-scrollbar{display:none}
.toc a{flex:0 0 auto;font-size:12.5px;text-decoration:none;color:var(--hero-ink);background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:999px;padding:5px 12px;white-space:nowrap}
.toc a .n{font-weight:700;color:var(--yellow);margin-right:5px}
.toc a.ch{color:#111;background:var(--yellow);border-color:var(--yellow);font-weight:700}
.chapter{margin:38px 0 -12px;scroll-margin-top:64px;padding:12px 14px 12px 16px;border-radius:14px;background:var(--hero);color:var(--hero-ink);border-left:6px solid var(--yellow)}
.chapter .k{display:block;font-size:11.5px;font-weight:700;letter-spacing:.08em;color:var(--yellow)}
.chapter .t{font-size:17px;font-weight:700}
.section{margin-top:30px;scroll-margin-top:64px}
.section-head{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.duality{display:flex;align-items:center;gap:10px;font-weight:700;font-size:18px;letter-spacing:-.01em}
.duality .n{flex:0 0 auto;min-width:30px;height:30px;padding:0 8px;border-radius:9px;background:var(--accent,var(--c1));color:#fff;font-size:13.5px;display:inline-flex;align-items:center;justify-content:center}
.duality .n:empty{display:none}
.section-line{display:none}
.card{background:var(--surface);border-radius:16px;padding:16px 16px 10px;margin-bottom:12px;box-shadow:var(--shadow);border:1px solid var(--line)}
.card h4{margin:0 0 10px;font-size:15.5px;font-weight:700;display:flex;align-items:center;gap:8px}
.card h4::before{content:"";width:4px;height:16px;border-radius:2px;background:var(--accent,var(--c1))}
.card p{margin:0 0 10px;font-size:14px}
.card b{font-weight:700;background:linear-gradient(transparent 60%,var(--mark) 60%);padding:0 1px}
.card code{font-size:13px}
ul.chk{list-style:none;margin:0 0 10px;padding:0}
ul.chk>li{position:relative;padding:9px 0 9px 18px;font-size:14px;border-top:1px solid var(--line)}
ul.chk>li:first-child{border-top:0;padding-top:2px}
ul.chk>li::before{content:"";position:absolute;left:2px;top:19px;width:6px;height:6px;border-radius:50%;background:var(--accent,var(--c1))}
ul.chk>li:first-child::before{top:12px}
ul.chk>li.star{background:var(--yellow-soft);margin:0 -10px;padding-left:28px;padding-right:10px;border-radius:10px;border-top-color:transparent}
ul.chk>li.star::before{display:none}
ul.chk>li.star::after{content:"★";position:absolute;left:10px;top:9px;color:#E0A200;font-size:13px}
ul.chk>li.cf{background:var(--cf-soft);margin:4px -10px;padding:8px 10px 8px 12px;border-radius:10px;border:0;border-left:3px solid var(--cf)}
ul.chk>li.cf::before{display:none}
.exp{margin:4px 0 12px;padding:9px 12px;background:var(--exp-soft);border-radius:10px;font-size:13.6px;line-height:1.65}
.exp-tag{display:block;margin-bottom:2px;font-size:12px;font-weight:700;color:var(--exp)}
ul.chk>li.cf .cf-tag{display:inline-block;margin-right:6px;font-size:12px;font-weight:700;color:var(--cf)}
ul.sub2{margin:6px 0 0;padding-left:14px;font-size:13.5px;color:var(--ink-soft)}
ul.sub2 li{margin-bottom:3px}
.subnote{margin:0 0 12px;padding:9px 12px;background:var(--surface2);border-radius:10px;font-size:12.5px;color:var(--ink-soft);line-height:1.6}
.subnote::before{content:"ⓘ ";color:var(--accent,var(--c1));font-weight:700}
.subnote.std{background:transparent;border:1px dashed var(--line,#ccc);padding:7px 11px;font-size:12px}
.subnote.std::before{content:""}
footer{margin-top:40px;padding:16px;background:var(--surface);border-radius:14px;border:1px solid var(--line);font-size:12px;color:var(--ink-soft);line-height:1.75}
footer a{color:var(--accent,var(--c1));font-weight:600}
/* 문제은행 */
.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;position:sticky;top:0;z-index:5;margin:0 -16px;padding:10px 16px;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.btn{font:inherit;font-size:13px;font-weight:600;background:var(--surface);color:var(--ink);border:1px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer}
.btn.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.tools .count{font-size:12px;color:var(--ink-soft);margin-left:auto}
.q-head{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.q-num{font-weight:700;font-size:12.5px;color:var(--accent,var(--c1));background:color-mix(in srgb,var(--accent,var(--c1)) 12%,transparent);border-radius:8px;padding:2px 10px}
.q-ch{font-size:11.5px;color:var(--ink-soft);background:var(--surface2);border:1px solid var(--line);border-radius:8px;padding:1px 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
select.btn{max-width:100%;appearance:auto}
.q-star{margin-left:auto;background:none;border:0;font-size:22px;cursor:pointer;color:var(--line);padding:0 2px;line-height:1}
.q.marked .q-star{color:#E0A200}
.q.marked{border-color:#F2C94C}
.q-body{font-size:15px;font-weight:500;margin:0 0 10px}
.opts{list-style:none;margin:0 0 6px;padding:0;display:grid;gap:6px}
.opts li{font-size:14px;padding:8px 12px;background:var(--surface2);border:1px solid var(--line);border-radius:10px}
details.ans{margin:8px 0 6px}
details.ans summary{cursor:pointer;list-style:none;text-align:center;font-size:13.5px;font-weight:700;color:#111;background:var(--yellow);border-radius:10px;padding:9px}
details.ans summary::-webkit-details-marker{display:none}
details.ans[open] summary{background:var(--surface2);color:var(--ink-soft)}
details.ans .c,details.ans[open] .o{display:none}details.ans[open] .c{display:inline}
.ans-body{margin-top:10px;padding:12px 12px 4px;background:var(--surface2);border-radius:12px}
.ans-body p,.ans-body li{font-size:13.8px}
.hidden{display:none !important}
/* PC: 넓은 화면에서는 본문을 넓히고 전체를 키움 */
@media (min-width:1000px){body{zoom:1.2;font-size:16px}.wrap{max-width:1160px;padding:0 24px 80px}body[data-subject] .wrap{max-width:920px}.cards{columns:2;column-gap:14px}.cards .card{break-inside:avoid;display:inline-block;width:100%}.card p,ul.chk>li,.opts li{font-size:15px}.card h4{font-size:16.5px}.q-body{font-size:16px}.opts{grid-template-columns:1fr 1fr}header{margin:0 -24px;padding:22px 32px 26px}.toc{margin-left:-32px;margin-right:-32px;padding-left:32px;padding-right:32px;flex-wrap:wrap;overflow:visible}.tools{margin:0 -24px;padding:10px 24px}}
@media (min-width:1600px){body{zoom:1.38}}
@media print{header{background:none;color:#000}.tools,.q-star{display:none}}
"""

HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1C2733">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body style="--accent:{accent}">
<div class="wrap">
"""

FOOT = """
<footer>{extra}</footer>
</div>
{script}
</body>
</html>
"""


def inline(s):
    s = html.escape(s.strip(), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def indent(l):
    return len(l) - len(l.lstrip(" "))


BULLET = re.compile(r"^(-|\d+\.)\s+")
CF_LABEL = "헷갈리는 선지:"  # 시험 보기에서 정답처럼 나오는 틀린 선지 줄
EXP_LABEL = "💡 해설:"  # 정리본에 덧붙인 해설 문단


def render_item(lines):
    """lines: 들여쓰기를 걷어 낸 항목 줄들 (첫 줄은 기호 제거됨)."""
    text, kids = [], []
    i = 0
    while i < len(lines):
        l = lines[i]
        if l.startswith("- "):
            kid = [l[2:]]
            i += 1
            while i < len(lines) and indent(lines[i]) >= 2:
                kid.append(lines[i][2:])
                i += 1
            kids.append(kid)
            continue
        text.append(inline(l))
        i += 1
    out = "<br>".join(t for t in text if t)
    if kids:
        out += '<ul class="sub2">' + "".join("<li>" + "<br>".join(inline(k) for k in kid) + "</li>" for kid in kids) + "</ul>"
    return out


def render_blocks(lines):
    """마크다운 조각 → HTML (목록·문단·인용만 쓰는 단순한 형식)."""
    out, i = [], 0
    lines = [l.rstrip("\n") for l in lines]
    while i < len(lines):
        l = lines[i]
        if not l.strip() or l.strip() == "---":
            i += 1
            continue
        if l.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(inline(lines[i].lstrip("> ")))
                i += 1
            cls = "subnote std" if buf and buf[0].startswith("📋") else "subnote"
            out.append(f'<div class="{cls}">' + "<br>".join(buf) + "</div>")
            continue
        m = BULLET.match(l)
        if m and indent(l) == 0:
            items = []
            while i < len(lines):
                l = lines[i]
                m = BULLET.match(l)
                if m and indent(l) == 0:
                    num = m.group(1)
                    first = l[m.end():]
                    if num != "-":
                        first = num + " " + first
                    items.append([first])
                    i += 1
                elif l.strip() and indent(l) >= 2 and items:
                    items[-1].append(l[2:] if indent(l) >= 2 else l)
                    i += 1
                else:
                    break
            lis = []
            for it in items:
                star = "⭐" in it[0]
                cf = it[0].startswith(CF_LABEL)
                first = it[0].replace("⭐", "").strip()
                if cf:
                    first = first[len(CF_LABEL):].strip()
                body = render_item([first] + it[1:])
                if cf:
                    body = '<span class="cf-tag">🔀 헷갈리는 선지</span>' + body
                cls = " class=\"cf\"" if cf else " class=\"star\"" if star else ""
                lis.append(f'<li{cls}>{body}</li>')
            out.append('<ul class="chk">' + "".join(lis) + "</ul>")
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(">") \
                and not (BULLET.match(lines[i]) and indent(lines[i]) == 0) and lines[i].strip() != "---":
            buf.append(inline(lines[i]))
            i += 1
        if buf and buf[0].startswith(EXP_LABEL):
            buf[0] = buf[0][len(EXP_LABEL):].strip()
            out.append('<div class="exp"><span class="exp-tag">💡 해설</span>' + "<br>".join(buf) + "</div>")
            continue
        out.append("<p>" + "<br>".join(buf) + "</p>")
    return "\n".join(out)


def split_doc(path):
    """# 제목, 머리말 목록, [(## 제목, [(### 제목|None, 줄들)])] 로 나눔."""
    title, intro, sections = "", [], []
    cur_sec = None
    for l in path.read_text(encoding="utf-8").splitlines():
        if l.startswith("# "):
            title = l[2:].strip()
        elif l.startswith("## "):
            cur_sec = [l[3:].strip(), [[None, []]]]
            sections.append(cur_sec)
        elif l.startswith("### ") and cur_sec:
            cur_sec[1].append([l[4:].strip(), []])
        elif cur_sec:
            cur_sec[1][-1][1].append(l)
        else:
            intro.append(l)
    for s in sections:
        s[1] = [c for c in s[1] if c[0] or any(x.strip() and x.strip() != "---" for x in c[1])]
    return title, intro, sections


def intro_list(lines):
    items = [inline(l[2:]) for l in lines if l.startswith("- ")]
    return '<ul class="sub">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>" if items else ""


def sec_title(t):
    m = re.match(r"^((?:기초 )?[0-9A-Z]+)\.\s*(.*)$", t)
    if m:
        return m.group(1), m.group(2)
    return "", t


def points_page(n, src):
    name, accent = SUBJECTS[n]
    _, intro, sections = split_doc(src)
    toc, body, topics = [], [], 0
    for si, (st, cards) in enumerate(sections, 1):
        ch = re.match(r"^CHAPTER (\d+)\s*·\s*(.*)$", st)
        if ch:
            toc.append(f'<a class="ch" href="#c{ch.group(1)}">CH{ch.group(1)} {html.escape(ch.group(2))}</a>')
            body.append(f'<div class="chapter" id="c{ch.group(1)}"><span class="k">CHAPTER {ch.group(1)}</span><span class="t">{html.escape(ch.group(2))}</span></div>')
            continue
        if st.startswith("출제기준"):
            toc.append(f'<a class="ch" href="#std">{html.escape(st)}</a>')
            body.append(f'<section class="section" id="std"><div class="section-head"><div class="duality">{html.escape(st)}</div><div class="section-line"></div></div>\n<div class="cards">' + "\n".join(f'<div class="card" data-title="{html.escape(st)}">{render_blocks(cl)}</div>' for _, cl in cards) + "</div></section>")
            continue
        topics += 1
        num, t = sec_title(st)
        sid = f"t{si}"
        star = "⭐" in t
        t_clean = t.replace("⭐", "").strip()
        toc.append(f'<a href="#{sid}"><span class="n">{num}</span>{html.escape(t_clean)}{" ★" if star else ""}</a>')
        parts = []
        for ct, cl in cards:
            h = f"<h4>{inline(ct)}</h4>" if ct else ""
            parts.append(f'<div class="card" data-title="{html.escape(t_clean)}{" · " + html.escape(ct) if ct else ""}">{h}{render_blocks(cl)}</div>')
        body.append(f'<section class="section" id="{sid}"><div class="section-head"><div class="duality"><span class="n">{num}</span>{html.escape(t_clean)}</div><div class="section-line"></div></div>\n' + '<div class="cards">' + "\n".join(parts) + "</div></section>")
    header = f"""<header>
  <a class="back" href="index.html">← 목록으로</a>
  <span class="tab">{n}과목 · 기출포인트</span>
  <div class="eyebrow">산업안전기사 필기 · {n}과목</div>
  <h1>{name}</h1>
  {intro_list(intro)}
  <nav class="toc">{''.join(toc)}</nav>
</header>"""
    bank = f'<a href="s{n}-bank.html">{n}과목 문제은행</a>에서 바로 문제로 확인해 보세요. ' if n in BANKS else ""
    doc = HEAD.format(title=f"{n}과목 기출포인트 · {name}", css=CSS, accent=accent) + header + "\n".join(body) + FOOT.format(extra=bank, script="")
    (OUT / f"s{n}-points.html").write_text(doc, encoding="utf-8")
    return topics


BANK_JS = """<script>
(function(){
  var key='sanan-star-'+document.body.dataset.subject;
  var marked={};
  try{marked=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){}
  function save(){try{localStorage.setItem(key,JSON.stringify(marked))}catch(e){}}
  var qs=[].slice.call(document.querySelectorAll('.q'));
  var cnt=document.getElementById('starCount');
  function upd(){cnt.textContent='★ 다시 볼 문제 '+Object.keys(marked).length+'개'}
  var ids={};qs.forEach(function(q){ids[q.dataset.q]=1});
  Object.keys(marked).forEach(function(id){if(!ids[id])delete marked[id]});
  qs.forEach(function(q){
    var id=q.dataset.q;
    if(marked[id])q.classList.add('marked');
    q.querySelector('.q-star').addEventListener('click',function(){
      if(marked[id]){delete marked[id];q.classList.remove('marked')}else{marked[id]=1;q.classList.add('marked')}
      save();upd();
    });
  });
  upd();
  var openAll=document.getElementById('openAll'),onlyStar=document.getElementById('onlyStar');
  openAll.addEventListener('click',function(){
    var on=!openAll.classList.contains('on');openAll.classList.toggle('on',on);
    openAll.textContent=on?'정답 모두 접기':'정답 모두 펼치기';
    document.querySelectorAll('details.ans').forEach(function(d){d.open=on});
  });
  var chSel=document.getElementById('chSel');
  function filter(){
    var star=onlyStar.classList.contains('on'),ch=chSel?chSel.value:'';
    qs.forEach(function(q){q.classList.toggle('hidden',(star&&!q.classList.contains('marked'))||(ch&&q.dataset.ch!==ch))});
    document.querySelectorAll('.section').forEach(function(s){
      s.classList.toggle('hidden',!s.querySelector('.q:not(.hidden)'));
    });
  }
  onlyStar.addEventListener('click',function(){onlyStar.classList.toggle('on');filter()});
  if(chSel){
    try{chSel.value=sessionStorage.getItem(key+'-ch')||''}catch(e){}
    chSel.addEventListener('change',function(){try{sessionStorage.setItem(key+'-ch',chSel.value)}catch(e){}filter()});
    filter();
  }
})();
</script>"""


LOCK_ITER = 600000
LOCK_CSS = """<style>
.lock{max-width:340px;margin:28px auto;text-align:center;padding:22px 18px 18px}
.lock b{background:none;display:block;font-size:16px;margin-bottom:6px}
.lock p{font-size:13px;color:var(--ink-soft);margin:0 0 14px}
.lock input{width:100%;box-sizing:border-box;font:inherit;font-size:22px;letter-spacing:.4em;text-align:center;padding:10px;border:1px solid var(--line);border-radius:12px;background:var(--surface2);color:var(--ink);margin-bottom:10px}
.lock input:focus{outline:2px solid var(--yellow);outline-offset:1px}
.lock .err{color:#E0482E;min-height:18px;margin:8px 0 0}
</style>"""
LOCK_JS = """<script>
(function(){
  var data=JSON.parse(document.getElementById('locked').textContent),key='sanan-pw-'+document.body.dataset.subject;
  var form=document.getElementById('lock'),pw=document.getElementById('pw'),err=form.querySelector('.err'),btn=form.querySelector('button');
  function b64(s){return Uint8Array.from(atob(s),function(c){return c.charCodeAt(0)})}
  function open(code){
    var enc=new TextEncoder();
    return crypto.subtle.importKey('raw',enc.encode(code),'PBKDF2',false,['deriveKey']).then(function(k){
      return crypto.subtle.deriveKey({name:'PBKDF2',salt:b64(data.s),iterations:data.i,hash:'SHA-256'},k,{name:'AES-GCM',length:256},false,['decrypt']);
    }).then(function(k){return crypto.subtle.decrypt({name:'AES-GCM',iv:b64(data.iv)},k,b64(data.c))}).then(function(buf){
      var box=document.createElement('div');box.innerHTML=new TextDecoder().decode(buf);
      var toc=box.querySelector('nav.toc');if(toc)document.querySelector('header').appendChild(toc);
      while(box.firstChild)form.parentNode.insertBefore(box.firstChild,form);
      form.remove();
      var sc=document.createElement('script');sc.textContent=document.getElementById('bankjs').textContent;document.body.appendChild(sc);
    });
  }
  form.addEventListener('submit',function(e){
    e.preventDefault();
    if(!/^\\d{6}$/.test(pw.value)){err.textContent='숫자 6자리를 입력하세요.';return}
    btn.disabled=true;err.textContent='확인 중…';
    open(pw.value).catch(function(){err.textContent='암호가 맞지 않습니다.';pw.value='';pw.focus()}).then(function(){btn.disabled=false});
  });
  try{sessionStorage.removeItem(key)}catch(e){}
  pw.focus();
})();
</script>"""


def page_password():
    """잠금 페이지 암호: study-plan/.page-password 파일 또는 CISE_PAGE_PW 환경변수 (저장소에 두지 않음)."""
    f = SRC / ".page-password"
    pw = f.read_text(encoding="utf-8").strip() if f.exists() else os.environ.get("CISE_PAGE_PW", "").strip()
    return pw if re.fullmatch(r"\d{6}", pw) else None


def lock_html(secret_html, pw):
    """secret_html을 pw로 암호화해 잠금 화면 + 암호문으로 바꿈 (PBKDF2-SHA256 → AES-GCM)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    salt, iv = secrets.token_bytes(16), secrets.token_bytes(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=LOCK_ITER).derive(pw.encode())
    ct = AESGCM(key).encrypt(iv, secret_html.encode("utf-8"), None)
    b = lambda x: base64.b64encode(x).decode()
    data = json.dumps({"s": b(salt), "iv": b(iv), "i": LOCK_ITER, "c": b(ct)})
    return f"""{LOCK_CSS}
<form class="card lock" id="lock" autocomplete="off"><b>🔒 암호를 입력하세요</b><p>숫자 6자리</p>
<input id="pw" type="password" inputmode="numeric" pattern="[0-9]*" maxlength="6" aria-label="암호 숫자 6자리">
<button class="btn" type="submit">열기</button><p class="err"></p></form>
<script type="application/json" id="locked">{data}</script>"""


def bank_page(n, src, *, slug=None, tab=None, eyebrow=None, h1=None, title=None, extra=None, accent=None, notes=True, locked=False, per_section=False):
    """과목 문제은행. 실기처럼 과목이 아닌 문제집은 slug 등 키워드로 넘김.
    per_section=True면 번호가 묶음마다 1번부터라 ★ 저장 키를 "묶음-번호"로 씀."""
    if n in SUBJECTS:
        name, accent = SUBJECTS[n]
    _, intro, sections = split_doc(src)
    # 교재 챕터별 문항: "- CHAPTER 01 이름 (n문항): 1~3, 7"
    chapters, q_ch = [], {}
    for l in intro:
        m = re.match(r"^- CHAPTER (\d+) (.+?) \((\d+)문항\): (.*)$", l)
        if not m:
            continue
        chapters.append((m.group(1), m.group(2), int(m.group(3))))
        for part in re.findall(r"\d+(?:~\d+)?", m.group(4)):
            a, _, b = part.partition("~")
            for q in range(int(a), int(b or a) + 1):
                q_ch[q] = m.group(1)
    if "**목차**" in intro:
        intro = intro[:intro.index("**목차**")]
    intro = [l for l in intro if l.startswith("- ")]
    toc, body, total = [], [], 0
    for si, (st, cards) in enumerate(sections, 1):
        if "틀린 문제" in st:
            continue
        if not any(ct for ct, _ in cards):
            continue
        sid = f"g{si}"
        num, t = sec_title(st)
        toc.append(f'<a href="#{sid}"><span class="n">{html.escape(num)}</span>{html.escape(t)}</a>')
        parts = []
        for ct, cl in cards:
            if not ct:
                continue
            qn = re.sub(r"\D", "", ct)
            qid = f"{num}-{qn}" if per_section else qn
            total += 1
            text = "\n".join(cl)
            q_part, _, rest = text.partition("<details>")
            ans_part = rest.split("</details>")[0]
            ans_part = re.sub(r"<summary>.*?</summary>", "", ans_part)
            q_lines = [l for l in q_part.splitlines() if l.strip() and l.strip() != "---"]
            opts = [l for l in q_lines if l.strip()[:1] in "①②③④⑤"]
            stem = [l for l in q_lines if l not in opts]
            stem_html = "<br>".join("· " + inline(l[2:]) if l.startswith("- ") else inline(l) for l in stem)
            opts_html = "".join(f"<li>{inline(o)}</li>" for o in opts)
            cid = q_ch.get(int(qn), "")
            chip = f'<span class="q-ch">CH{cid} {html.escape(dict((c[0], c[1]) for c in chapters)[cid])}</span>' if cid else ""
            parts.append(f"""<div class="card q" data-q="{qid}" data-ch="{cid}" data-title="{qn}번">
<div class="q-head"><span class="q-num">{qn}번</span>{chip}<button class="q-star" title="다시 볼 문제로 표시" aria-label="다시 볼 문제로 표시">★</button></div>
<p class="q-body">{stem_html}</p>
<ul class="opts">{opts_html}</ul>
<details class="ans"><summary><span class="o">정답 보기</span><span class="c">정답 닫기</span></summary><div class="ans-body">{render_blocks(ans_part.splitlines())}</div></details>
</div>""")
        body.append(f'<section class="section" id="{sid}"><div class="section-head"><div class="duality"><span class="n">{html.escape(num)}</span>{html.escape(t)}</div><div class="section-line"></div></div>\n' + "\n".join(parts) + "</section>")
    opts = "".join(f'<option value="{c}">CH{c} {html.escape(t)} ({k})</option>' for c, t, k in chapters if k)
    ch_sel = f'<select class="btn" id="chSel" aria-label="교재 챕터별 보기"><option value="">교재 챕터: 전체</option>{opts}</select>' if chapters else ""
    if chapters:
        intro = intro + ["- 아래 **교재 챕터** 선택으로 에듀윌 교재 챕터별 문제만 골라 볼 수 있습니다. 문제 번호는 그대로입니다."]
    slug = slug or f"s{n}-bank"
    tab = tab or f"{n}과목 · 문제은행"
    eyebrow = eyebrow or f"산업안전기사 필기 · {n}과목"
    h1 = h1 or f"{name}<br>문제은행"
    title = title or f"{n}과목 문제은행 · {name}"
    if extra is None:
        extra = f'개념이 막히면 <a href="s{n}-points.html">{n}과목 기출포인트</a>를 먼저 보세요. '
    header = f"""<header>
  <a class="back" href="index.html">← 목록으로</a>
  <span class="tab">{tab}</span>
  <div class="eyebrow">{eyebrow} · {total}문항</div>
  <h1>{h1}</h1>
  {intro_list(intro + ['- 헷갈린 문제는 오른쪽 위 **★**을 눌러 두면 이 기기에 저장되고, "★만 보기"로 모아 풀 수 있습니다.']) if notes else ""}
  {"" if locked else f'<nav class="toc">{"".join(toc)}</nav>'}
</header>"""
    content = (f'<nav class="toc">{"".join(toc)}</nav>' if locked else "\n") + f"""<div class="tools">{ch_sel}<button class="btn" id="openAll">정답 모두 펼치기</button><button class="btn" id="onlyStar">★만 보기</button><span class="count" id="starCount"></span></div>""" + "\n".join(body)
    script = BANK_JS
    if locked:
        pw = page_password()
        if not pw:
            print(f"{slug}: 암호(study-plan/.page-password 또는 CISE_PAGE_PW)가 없어 건너뜀", file=sys.stderr)
            return total
        content = lock_html(content, pw)
        script = BANK_JS.replace("<script>", '<script type="text/plain" id="bankjs">', 1) + LOCK_JS
    doc = HEAD.format(title=title, css=CSS, accent=accent).replace(
        f'<body style="--accent:{accent}">', f'<body style="--accent:{accent}" data-subject="{slug.replace("-bank", "")}">') + header + content + FOOT.format(extra=extra, script=script)
    (OUT / f"{slug}.html").write_text(doc, encoding="utf-8")
    return total


def roadmap_page(src):
    title, intro, sections = split_doc(src)
    toc, body = [], []
    for si, (st, cards) in enumerate(sections, 1):
        num, t = sec_title(st)
        toc.append(f'<a href="#r{si}"><span class="n">{num}</span>{html.escape(t)}</a>')
        parts = [f'<div class="card" data-title="{html.escape(t)}">' + (f"<h4>{inline(ct)}</h4>" if ct else "") + render_blocks(cl) + "</div>" for ct, cl in cards]
        body.append(f'<section class="section" id="r{si}"><div class="section-head"><div class="duality"><span class="n">{num}</span>{html.escape(t)}</div><div class="section-line"></div></div>\n' + '<div class="cards">' + "\n".join(parts) + "</div></section>")
    header = f"""<header>
  <a class="back" href="index.html">← 목록으로</a>
  <span class="tab">로드맵</span>
  <div class="eyebrow">산업안전기사 · 학습 계획</div>
  <h1>{html.escape(title)}</h1>
  <nav class="toc">{''.join(toc)}</nav>
</header>"""
    doc = HEAD.format(title=title, css=CSS, accent="var(--c1)") + header + "\n".join(body) + FOOT.format(extra="", script="")
    (OUT / "roadmap.html").write_text(doc, encoding="utf-8")


BANKS = {n: SRC / f"{n}과목_문제은행_1-100.md" for n in SUBJECTS if (SRC / f"{n}과목_문제은행_1-100.md").exists()}
counts = {n: points_page(n, SRC / f"{n}과목_기출포인트.md") for n in SUBJECTS}
bank_counts = {n: bank_page(n, p) for n, p in BANKS.items()}
roadmap_page(SRC / "산업안전기사_12주_로드맵.md")
PRACTICAL = SRC / "실기_필답형_핵심.md"
practical_count = bank_page("practical", PRACTICAL, slug="practical", tab="실기 · 필답형",
    eyebrow="산업안전기사 실기 · 필답형 2016~2026", h1="실기 필답형<br>핵심",
    title="실기 필답형 핵심", accent="var(--c7)", notes=False, locked=True, per_section=True,
    extra="번호는 주제마다 1번부터입니다. 🔧(용어·수치 바로잡음)·⚠️(법령·교재 확인 필요) 표시 문항은 교재로 한 번 더 확인하세요. 개념은 과목별 기출포인트에서 찾아볼 수 있습니다. ") if PRACTICAL.exists() else 0
CORE = SRC / "필기_핵심요약.md"
core_count = bank_page("core", CORE, slug="core226", tab="필기 · 핵심요약",
    eyebrow="산업안전기사 필기 · 2018~2025 기출 분석", h1="필기<br>핵심요약",
    title="필기 핵심요약", accent="var(--c8)", notes=False, locked=True, per_section=True,
    extra="번호는 과목마다 1번부터입니다. 🔧(용어·수치 바로잡음)·⚠️(법령·교재 확인 필요) 표시 문항은 교재로 한 번 더 확인하세요. 더 자세한 개념은 과목별 기출포인트에 있습니다. ") if CORE.exists() else 0
print(counts, bank_counts, practical_count, core_count)


INDEX_CSS = CSS + """
.hero-meta{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
.hero-meta span{font-size:12px;color:var(--hero-ink);background:rgba(255,255,255,.08);border-radius:999px;padding:3px 11px}
.hero-meta b{color:var(--yellow)}
.search-wrap{margin:-20px 4px 0;position:relative;z-index:2}
.search-input{width:100%;padding:14px 16px;border:1px solid var(--line);border-radius:14px;background:var(--surface);color:var(--ink);font:inherit;font-size:15px;box-shadow:var(--shadow)}
.search-input:focus{outline:2px solid var(--yellow);outline-offset:1px}
.search-status{font-size:12px;color:var(--ink-soft);margin:8px 4px 0;min-height:14px}
.search-result{display:block;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-bottom:8px;text-decoration:none;color:inherit}
.search-result h4{margin:0 0 4px;font-size:14.5px;font-weight:700}
.search-result p{margin:0;font-size:13px;color:var(--ink-soft);line-height:1.6}
.search-result mark{background:var(--mark);color:inherit;border-radius:3px;padding:0 1px}
.grid{display:grid;grid-template-columns:1fr;gap:12px}
@media (min-width:560px){.grid{grid-template-columns:1fr 1fr}}
@media (min-width:1000px){.grid{grid-template-columns:1fr 1fr 1fr}}
.subj{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:16px;box-shadow:var(--shadow);display:flex;flex-direction:column}
.subj-top{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.subj-no{width:40px;height:40px;border-radius:12px;background:var(--c);color:#fff;font-weight:700;font-size:17px;display:flex;align-items:center;justify-content:center;flex:0 0 auto}
.subj h3{margin:0;font-size:16px;line-height:1.35;letter-spacing:-.01em}
.subj p{margin:0 0 12px;font-size:12.8px;color:var(--ink-soft);line-height:1.6;flex:1}
.subj-btns{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.subj-btns a{display:block;text-align:center;text-decoration:none;border-radius:11px;padding:9px 6px;font-size:13px;font-weight:700;line-height:1.35}
.subj-btns a small{display:block;font-weight:500;font-size:11.5px;opacity:.8}
.subj-btns .pt{background:color-mix(in srgb,var(--c) 13%,transparent);color:var(--c)}
.subj-btns .bk{background:var(--c);color:#fff}
.subj-btns .off{background:var(--surface2);color:var(--ink-soft);pointer-events:none}
.plan{display:flex;align-items:center;gap:12px;text-decoration:none;color:inherit;background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:14px 16px;box-shadow:var(--shadow)}
.plan .ic{width:40px;height:40px;border-radius:12px;background:var(--yellow);color:#111;display:flex;align-items:center;justify-content:center;font-size:19px;flex:0 0 auto}
.plan b{display:block;font-size:15px}
.plan span{font-size:12.8px;color:var(--ink-soft)}
.plan .go{margin-left:auto;color:var(--ink-soft);font-size:18px}
"""

INDEX_JS = """<script>
(function(){
  var pages=PAGES,input=document.getElementById('siteSearch'),status=document.getElementById('searchStatus'),
      box=document.getElementById('searchResults'),all=document.getElementById('allSections'),index=null,loading=null;
  function load(){
    if(loading)return loading;
    status.textContent='노트 불러오는 중…';
    loading=Promise.all(pages.map(function(p){
      return fetch(p.href).then(function(r){return r.text()}).then(function(t){
        var doc=new DOMParser().parseFromString(t,'text/html');
        return [].slice.call(doc.querySelectorAll('.card')).map(function(c,i){
          var sec=c.closest('.section');
          if(!c.id)c.id='c'+i;
          return {page:p.name,href:p.href+(sec&&sec.id?'#'+sec.id:''),title:c.dataset.title||'',text:txt(c)};
        });
      }).catch(function(){return []});
    })).then(function(a){index=[].concat.apply([],a);status.textContent='';return index});
    return loading;
  }
  function txt(el){var w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),a=[],n;while(n=w.nextNode())a.push(n.nodeValue);return a.join(' ').replace(/\\s+/g,' ').trim()}
  function esc(s){return s.replace(/[&<>]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
  function run(){
    var q=input.value.trim();
    if(!q){box.classList.add('hidden');all.classList.remove('hidden');status.textContent='';return}
    load().then(function(idx){
      if(input.value.trim()!==q)return;
      var ql=q.toLowerCase(),hits=idx.filter(function(e){return e.text.toLowerCase().indexOf(ql)>=0});
      status.textContent=hits.length+'개 카드에서 찾음';
      box.innerHTML=hits.slice(0,60).map(function(h){
        var i=h.text.toLowerCase().indexOf(ql),s=Math.max(0,i-40),snip=(s>0?'…':'')+h.text.slice(s,i+q.length+70)+'…';
        var re=new RegExp(q.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&'),'gi');
        return '<a class="search-result" href="'+h.href+'"><h4>'+esc(h.page)+' · '+esc(h.title)+'</h4><p>'+esc(snip).replace(re,function(m){return '<mark>'+m+'</mark>'})+'</p></a>';
      }).join('')||'<p class="search-status">검색 결과가 없습니다.</p>';
      box.classList.remove('hidden');all.classList.add('hidden');
    });
  }
  var t;input.addEventListener('input',function(){clearTimeout(t);t=setTimeout(run,200)});
})();
</script>"""


def index_page():
    tiles, pages = [], [{"name": "12주 로드맵", "href": "roadmap.html"}]
    for n, (name, color) in SUBJECTS.items():
        pages.append({"name": f"{n}과목 기출포인트", "href": f"s{n}-points.html"})
        if n in bank_counts:
            pages.append({"name": f"{n}과목 문제은행", "href": f"s{n}-bank.html"})
            bank = f'<a class="bk" href="s{n}-bank.html">문제은행<small>{bank_counts[n]}문항</small></a>'
        else:
            bank = '<a class="off" href="#" aria-disabled="true">문제은행<small>준비 중</small></a>'
        tiles.append(f"""<div class="subj" style="--c:{color}">
    <div class="subj-top"><div class="subj-no">{n}</div><h3>{name}</h3></div>
    <p>{BLURB[n]}</p>
    <div class="subj-btns"><a class="pt" href="s{n}-points.html">기출포인트<small>{counts[n]}주제</small></a>{bank}</div>
  </div>""")
    core = f"""<section class="section">
  <div class="section-head"><div class="duality">필기 요약</div></div>
  <a class="plan" href="core226.html"><div class="ic" style="background:var(--c8);color:#fff">★</div><div><b>필기 핵심요약</b><span>2018~2025 기출 2,880문항 분석 · 6과목 · {core_count}문항</span></div><div class="go">›</div></a>
</section>""" if core_count else ""
    practical = f"""<section class="section">
  <div class="section-head"><div class="duality">실기</div></div>
  <a class="plan" href="practical.html"><div class="ic" style="background:var(--c7);color:#fff">✍</div><div><b>필답형 핵심</b><span>2016~2026 기출 · 14개 주제 · {practical_count}문항</span></div><div class="go">›</div></a>
</section>""" if practical_count else ""
    body = f"""<header>
  <div class="eyebrow" style="margin-top:14px">CISE · 산업안전기사 필기</div>
  <h1>과목별 기출포인트와<br>문제은행</h1>
  <p class="sub" style="padding:0">기출포인트로 핵심을 잡고, 문제은행으로 바로 확인하세요.</p>
  <div class="hero-meta"><span>6과목 × <b>20문항</b></span><span>과목별 <b>40점↑</b></span><span>평균 <b>60점↑</b> 합격</span></div>
  <div style="height:22px"></div>
</header>

<div class="search-wrap">
  <input type="search" id="siteSearch" class="search-input" placeholder="🔍 전체 검색 — 도수율, 파열판, 접지, 비계" autocomplete="off">
  <div class="search-status" id="searchStatus"></div>
</div>
<div class="search-results hidden" id="searchResults"></div>

<div id="allSections">
<section class="section" style="margin-top:14px">
  <a class="plan" href="roadmap.html"><div class="ic">🗓</div><div><b>12주 로드맵</b><span>시험 구조 · 과목별 난이도 · 주차별 계획</span></div><div class="go">›</div></a>
</section>
{core}
{practical}

<section class="section">
  <div class="section-head"><div class="duality">과목</div></div>
  <div class="grid">
  {''.join(tiles)}
  </div>
</section>
</div>
"""
    doc = HEAD.format(title="산업안전기사 학습 노트", css=INDEX_CSS, accent="var(--c1)") + body + FOOT.format(extra="", script=INDEX_JS.replace("PAGES", json.dumps(pages, ensure_ascii=False)))
    (OUT / "index.html").write_text(doc, encoding="utf-8")


index_page()
