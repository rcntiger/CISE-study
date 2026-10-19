#!/usr/bin/env python3
"""study-plan/*.md → sanan-notes HTML 페이지 생성 (한능검 노트와 같은 종이 노트 스타일)."""
import html, re, sys, json
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

SUBJECTS = {
    1: ("산업재해 예방 및 안전보건교육", "var(--green)"),
    2: ("인간공학 및 위험성 평가·관리", "var(--blue)"),
    3: ("기계·기구 및 설비 안전관리", "var(--heuk)"),
    4: ("전기설비 안전관리", "var(--red)"),
    5: ("화학설비 안전관리", "var(--purple)"),
    6: ("건설공사 안전관리", "var(--orange)"),
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
  --paper:#EFE8D6;--paper2:#E6DFC9;--ink:#232A35;--ink-soft:#4B5563;--rule:#C9BFA0;
  --red:#B4362C;--green:#3F6D4E;--hl:#EFC94C;--blue:#3E5C86;--purple:#6E5482;
  --heuk:#7C848F;--orange:#B8661F;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--paper);color:var(--ink);font-family:'Noto Sans KR',sans-serif;
  font-weight:400;line-height:1.7;font-size:15px;
  background-image:repeating-linear-gradient(0deg, rgba(0,0,0,0.015) 0px, rgba(0,0,0,0.015) 1px, transparent 1px, transparent 34px);
}
.wrap{max-width:760px;margin:0 auto;padding:0 20px 80px}
header{padding:40px 0 20px;border-bottom:3px double var(--ink);position:relative}
.back{position:absolute;left:0;top:14px;font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--ink-soft);text-decoration:none}
.tab{position:absolute;top:0;right:0;background:var(--accent,var(--red));color:var(--paper);font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.14em;padding:5px 10px;border-radius:0 0 2px 2px}
.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.2em;color:var(--ink-soft);text-transform:uppercase;margin-bottom:10px}
h1{font-family:'Gowun Batang',serif;font-weight:700;font-size:clamp(26px,7vw,38px);margin:0 0 10px;letter-spacing:-.01em;line-height:1.3}
.sub{font-size:13.5px;color:var(--ink-soft);margin:0;padding-left:18px}
.sub li{margin-bottom:2px}
.sub b{color:var(--ink)}
.toc{display:flex;flex-wrap:wrap;gap:6px;margin:20px 0 4px}
.toc a{font-size:12.5px;text-decoration:none;color:var(--ink);background:var(--paper2);border:1px solid var(--rule);border-radius:3px;padding:4px 9px;line-height:1.4}
.toc a:hover{border-color:var(--ink)}
.toc a .n{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--ink-soft);margin-right:4px}
.section{margin-top:38px;scroll-margin-top:12px}
.section-head{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.duality{font-family:'Gowun Batang',serif;font-weight:700;font-size:19px;color:var(--ink)}
.duality .n{color:var(--accent,var(--red));margin-right:6px}
.section-line{flex:1;height:1px;background:repeating-linear-gradient(90deg, var(--rule) 0 4px, transparent 4px 8px)}
.card{background:var(--paper2);border:1px solid var(--rule);border-radius:4px;padding:14px 16px 12px;margin-bottom:10px}
.card h4{margin:0 0 8px;font-family:'Gowun Batang',serif;font-size:16px;font-weight:700}
.card p{margin:0 0 8px;font-size:14px}
.card b{font-weight:700;background:linear-gradient(transparent 62%, var(--hl) 62%);padding:0 1px}
.card code{font-family:'IBM Plex Mono',monospace;font-size:13px}
ul.chk{list-style:none;margin:0 0 8px;padding:0}
ul.chk>li{position:relative;padding-left:22px;margin-bottom:7px;font-size:14px}
ul.chk>li::before{content:"☐";position:absolute;left:0;top:0;color:var(--ink-soft);font-size:13px}
ul.chk>li.star::before{content:"★";color:var(--red)}
ul.sub2{margin:4px 0 0;padding-left:16px;font-size:13.5px;color:var(--ink-soft)}
ul.sub2 li{margin-bottom:3px}
.subnote{margin:0 0 10px;padding:8px 10px;background:var(--paper);border-left:3px solid var(--red);font-size:12.5px;color:var(--ink-soft);line-height:1.6;border-radius:0 2px 2px 0}
footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--rule);font-size:11.5px;color:var(--ink-soft);line-height:1.75}
footer a{color:var(--ink)}
/* 문제은행 */
.tools{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0;position:sticky;top:0;z-index:5;background:var(--paper);padding:8px 0;border-bottom:1px solid var(--rule)}
.btn{font-family:'Noto Sans KR',sans-serif;font-size:12.5px;background:var(--paper2);color:var(--ink);border:1px solid var(--rule);border-radius:3px;padding:6px 10px;cursor:pointer}
.btn.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.tools .count{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--ink-soft);align-self:center;margin-left:auto}
.q{position:relative}
.q-head{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.q-num{font-family:'IBM Plex Mono',monospace;font-weight:700;font-size:12px;color:var(--paper);background:var(--accent,var(--red));border-radius:12px;padding:1px 9px}
.q-star{margin-left:auto;background:none;border:0;font-size:19px;cursor:pointer;color:var(--ink-soft);padding:0 2px;line-height:1}
.q.marked .q-star{color:var(--red)}
.q.marked{border-color:var(--red)}
.q-body{font-size:14.5px;margin:0 0 8px}
.opts{list-style:none;margin:0 0 6px;padding:0}
.opts li{font-size:14px;padding:3px 0}
details.ans{margin-top:6px;border-top:1px dashed var(--rule);padding-top:8px}
details.ans summary{cursor:pointer;font-size:12.5px;color:var(--accent,var(--red));font-weight:500;list-style:none}
details.ans summary::-webkit-details-marker{display:none}
details.ans summary::before{content:"▸ "}
details.ans[open] summary::before{content:"▾ "}
.ans-body{margin-top:8px;padding:8px 10px;background:var(--paper);border-left:3px solid var(--accent,var(--red));border-radius:0 2px 2px 0}
.ans-body p,.ans-body li{font-size:13.5px}
.hidden{display:none !important}
@media print{body{background:#fff;font-size:12px}.tools,.q-star{display:none}details.ans{display:block}}
"""

HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Noto+Sans+KR:wght@300;400;500;700;900&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body style="--accent:{accent}">
<div class="wrap">
"""

FOOT = """
<footer>{extra}출제 경향을 정리한 유형 노트이며 기출 원문이 아닙니다. 법령·KEC 수치는 시험 전에 최신 개정 사항으로 확인하세요.</footer>
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
            out.append('<div class="subnote">' + "<br>".join(buf) + "</div>")
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
                body = render_item([it[0].replace("⭐", "").strip()] + it[1:])
                lis.append(f'<li{" class=\"star\"" if star else ""}>{body}</li>')
            out.append('<ul class="chk">' + "".join(lis) + "</ul>")
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(">") \
                and not (BULLET.match(lines[i]) and indent(lines[i]) == 0) and lines[i].strip() != "---":
            buf.append(inline(lines[i]))
            i += 1
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
    toc, body = [], []
    for si, (st, cards) in enumerate(sections, 1):
        num, t = sec_title(st)
        sid = f"t{si}"
        star = "⭐" in t
        t_clean = t.replace("⭐", "").strip()
        toc.append(f'<a href="#{sid}"><span class="n">{num}</span>{html.escape(t_clean)}{" ★" if star else ""}</a>')
        parts = []
        for ct, cl in cards:
            h = f"<h4>{inline(ct)}</h4>" if ct else ""
            parts.append(f'<div class="card" data-title="{html.escape(t_clean)}{" · " + html.escape(ct) if ct else ""}">{h}{render_blocks(cl)}</div>')
        body.append(f'<section class="section" id="{sid}"><div class="section-head"><div class="duality"><span class="n">{num}</span>{html.escape(t_clean)}</div><div class="section-line"></div></div>\n' + "\n".join(parts) + "</section>")
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
    return len(sections)


BANK_JS = """<script>
(function(){
  var key='sanan-star-'+document.body.dataset.subject;
  var marked={};
  try{marked=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){}
  function save(){try{localStorage.setItem(key,JSON.stringify(marked))}catch(e){}}
  var qs=[].slice.call(document.querySelectorAll('.q'));
  var cnt=document.getElementById('starCount');
  function upd(){cnt.textContent='★ 다시 볼 문제 '+Object.keys(marked).length+'개'}
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
  onlyStar.addEventListener('click',function(){
    var on=!onlyStar.classList.contains('on');onlyStar.classList.toggle('on',on);
    qs.forEach(function(q){q.classList.toggle('hidden',on&&!q.classList.contains('marked'))});
    document.querySelectorAll('.section').forEach(function(s){
      s.classList.toggle('hidden',on&&!s.querySelector('.q.marked'));
    });
  });
})();
</script>"""


def bank_page(n, src):
    name, accent = SUBJECTS[n]
    _, intro, sections = split_doc(src)
    intro = [l for l in intro if l.startswith("- ")]
    toc, body, total = [], [], 0
    for si, (st, cards) in enumerate(sections, 1):
        if "틀린 문제" in st:
            continue
        sid = f"g{si}"
        num, t = sec_title(st)
        toc.append(f'<a href="#{sid}"><span class="n">{html.escape(num)}</span>{html.escape(t)}</a>')
        parts = []
        for ct, cl in cards:
            if not ct:
                continue
            qn = re.sub(r"\D", "", ct)
            total += 1
            text = "\n".join(cl)
            q_part, _, rest = text.partition("<details>")
            ans_part = rest.split("</details>")[0]
            ans_part = re.sub(r"<summary>.*?</summary>", "", ans_part)
            q_lines = [l for l in q_part.splitlines() if l.strip() and l.strip() != "---"]
            opts = [l for l in q_lines if l.strip()[:1] in "①②③④⑤"]
            stem = [l for l in q_lines if l not in opts]
            stem_html = "<br>".join(inline(l) for l in stem)
            opts_html = "".join(f"<li>{inline(o)}</li>" for o in opts)
            parts.append(f"""<div class="card q" data-q="{qn}" data-title="{qn}번">
<div class="q-head"><span class="q-num">{qn}번</span><button class="q-star" title="다시 볼 문제로 표시" aria-label="다시 볼 문제로 표시">★</button></div>
<p class="q-body">{stem_html}</p>
<ul class="opts">{opts_html}</ul>
<details class="ans"><summary>정답 보기</summary><div class="ans-body">{render_blocks(ans_part.splitlines())}</div></details>
</div>""")
        body.append(f'<section class="section" id="{sid}"><div class="section-head"><div class="duality"><span class="n">{html.escape(num)}</span>{html.escape(t)}</div><div class="section-line"></div></div>\n' + "\n".join(parts) + "</section>")
    header = f"""<header>
  <a class="back" href="index.html">← 목록으로</a>
  <span class="tab">{n}과목 · 문제은행</span>
  <div class="eyebrow">산업안전기사 필기 · {n}과목 · {total}문항</div>
  <h1>{name}<br>문제은행</h1>
  {intro_list(intro + ['- 헷갈린 문제는 오른쪽 위 **★**을 눌러 두면 이 기기에 저장되고, "★만 보기"로 모아 풀 수 있습니다.'])}
  <nav class="toc">{''.join(toc)}</nav>
</header>
<div class="tools"><button class="btn" id="openAll">정답 모두 펼치기</button><button class="btn" id="onlyStar">★만 보기</button><span class="count" id="starCount"></span></div>"""
    extra = f'개념이 막히면 <a href="s{n}-points.html">{n}과목 기출포인트</a>를 먼저 보세요. '
    doc = HEAD.format(title=f"{n}과목 문제은행 · {name}", css=CSS, accent=accent).replace(
        f'<body style="--accent:{accent}">', f'<body style="--accent:{accent}" data-subject="s{n}">') + header + "\n".join(body) + FOOT.format(extra=extra, script=BANK_JS)
    (OUT / f"s{n}-bank.html").write_text(doc, encoding="utf-8")
    return total


def roadmap_page(src):
    title, intro, sections = split_doc(src)
    toc, body = [], []
    for si, (st, cards) in enumerate(sections, 1):
        num, t = sec_title(st)
        toc.append(f'<a href="#r{si}"><span class="n">{num}</span>{html.escape(t)}</a>')
        parts = [f'<div class="card" data-title="{html.escape(t)}">' + (f"<h4>{inline(ct)}</h4>" if ct else "") + render_blocks(cl) + "</div>" for ct, cl in cards]
        body.append(f'<section class="section" id="r{si}"><div class="section-head"><div class="duality"><span class="n">{num}</span>{html.escape(t)}</div><div class="section-line"></div></div>\n' + "\n".join(parts) + "</section>")
    header = f"""<header>
  <a class="back" href="index.html">← 목록으로</a>
  <span class="tab">로드맵</span>
  <div class="eyebrow">산업안전기사 · 학습 계획</div>
  <h1>{html.escape(title)}</h1>
  <nav class="toc">{''.join(toc)}</nav>
</header>"""
    doc = HEAD.format(title=title, css=CSS, accent="var(--green)") + header + "\n".join(body) + FOOT.format(extra="", script="")
    (OUT / "roadmap.html").write_text(doc, encoding="utf-8")


BANKS = {1: SRC / "1과목_문제은행_1-100.md"}
counts = {n: points_page(n, SRC / f"{n}과목_기출포인트.md") for n in SUBJECTS}
bank_counts = {n: bank_page(n, p) for n, p in BANKS.items()}
roadmap_page(SRC / "산업안전기사_12주_로드맵.md")
pass
print(counts, bank_counts)


INDEX_CSS = CSS + """
.card-link{display:block;background:var(--paper2);border:1px solid var(--rule);border-radius:4px;padding:14px 16px;margin-bottom:10px;text-decoration:none;color:inherit;position:relative;transition:border-color .15s}
.card-link::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:currentColor;border-radius:4px 0 0 4px}
.card-link:hover{border-color:var(--ink)}
.card-link .idx{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--ink-soft);letter-spacing:.1em}
.card-link h3{font-family:'Gowun Batang',serif;font-weight:700;font-size:17px;margin:3px 0 5px;color:var(--ink);padding-right:44px}
.card-link p{margin:0;font-size:13px;color:var(--ink-soft);line-height:1.6;padding-right:44px}
.card-link .go{position:absolute;right:16px;top:50%;transform:translateY(-50%);font-family:'IBM Plex Mono',monospace;font-size:11px;color:currentColor;opacity:.7}
.card-link.disabled{opacity:.5;cursor:default;pointer-events:none}
.tl{display:flex;flex-wrap:wrap;border:1px solid var(--ink);border-radius:3px;overflow:hidden;margin-top:22px}
.tl-node{flex:1 1 15%;min-width:96px;padding:8px 4px 7px;text-align:center;border-right:1px solid var(--ink);border-bottom:1px solid var(--ink);background:var(--paper2);font-size:12px;color:var(--ink-soft);line-height:1.5}
.tl-node b{display:block;font-size:13px;color:var(--ink)}
.search-wrap{margin:24px 0 4px}
.search-input{width:100%;padding:12px 14px;border:1px solid var(--rule);border-radius:4px;background:var(--paper2);color:var(--ink);font-family:'Noto Sans KR',sans-serif;font-size:14.5px}
.search-input:focus{outline:none;border-color:var(--ink)}
.search-status{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--ink-soft);margin-top:7px;min-height:14px}
.search-result{display:block;background:var(--paper2);border:1px solid var(--rule);border-radius:4px;padding:12px 14px;margin-bottom:8px;text-decoration:none;color:inherit}
.search-result:hover{border-color:var(--ink)}
.search-result h4{margin:0 0 4px;font-family:'Gowun Batang',serif;font-weight:700;font-size:15px}
.search-result p{margin:0;font-size:12.8px;color:var(--ink-soft);line-height:1.65}
.search-result mark{background:var(--hl);color:var(--ink);padding:0 1px;border-radius:2px}
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
    pts, bks, pages = [], [], [{"name": "12주 로드맵", "href": "roadmap.html"}]
    for n, (name, color) in SUBJECTS.items():
        pts.append(f"""<a class="card-link" style="color:{color}" href="s{n}-points.html">
    <span class="idx">{n}과목 · {counts[n]}주제</span>
    <h3>{name}</h3>
    <p>{BLURB[n]}</p>
    <span class="go">열기 →</span>
  </a>""")
        pages.append({"name": f"{n}과목 기출포인트", "href": f"s{n}-points.html"})
        if n in bank_counts:
            bks.append(f"""<a class="card-link" style="color:{color}" href="s{n}-bank.html">
    <span class="idx">{n}과목 · {bank_counts[n]}문항</span>
    <h3>{name} 문제은행</h3>
    <p>문제 → 정답 → 핵심 정리(📌). 정답은 눌러야 펼쳐지고, 헷갈린 문제는 ★로 모아 다시 풀 수 있음</p>
    <span class="go">풀기 →</span>
  </a>""")
            pages.append({"name": f"{n}과목 문제은행", "href": f"s{n}-bank.html"})
        else:
            bks.append(f"""<a class="card-link disabled" style="color:{color}" href="#">
    <span class="idx">{n}과목 · 준비 중</span>
    <h3>{name} 문제은행</h3>
    <p>기출포인트 {counts[n]}주제 기준으로 100문항 준비 중</p>
    <span class="go">준비 중</span>
  </a>""")
    nodes = "".join(f'<div class="tl-node"><b>{n}과목</b>{SUBJECTS[n][0].split(" ")[0]}</div>' for n in SUBJECTS)
    body = f"""<header>
  <div class="eyebrow">산업안전기사 필기 · 학습 노트 모음</div>
  <h1>과목별 기출포인트 · 문제은행</h1>
  <p class="sub" style="padding:0">6과목 × 20문항, 과목별 40점 이상 · 평균 60점 이상이면 합격. 기출포인트로 핵심을 잡고 문제은행으로 바로 확인하세요.</p>
  <div class="tl">{nodes}</div>
</header>

<div class="search-wrap">
  <input type="search" id="siteSearch" class="search-input" placeholder="키워드로 전체 검색 — 예: 도수율, 파열판, 접지, 비계" autocomplete="off">
  <div class="search-status" id="searchStatus"></div>
</div>
<div class="search-results hidden" id="searchResults"></div>

<div id="allSections">
<section class="section">
  <div class="section-head"><div class="duality">빠른 참조</div><div class="section-line"></div></div>
  <a class="card-link" style="color:var(--green)" href="roadmap.html">
    <span class="idx">PLAN · 전체 과목</span>
    <h3>산업안전기사 12주 로드맵</h3>
    <p>필기·실기 시험 구조, 과목별 난이도와 공부 순서, 주차별 계획</p>
    <span class="go">열기 →</span>
  </a>
</section>

<section class="section">
  <div class="section-head"><div class="duality">과목별 기출포인트</div><div class="section-line"></div></div>
  <p style="font-size:12.5px;color:var(--ink-soft);margin:0 0 12px"><b style="color:var(--red)">★</b> 표시는 특히 자주 나오는 항목입니다.</p>
  {''.join(pts)}
</section>

<section class="section">
  <div class="section-head"><div class="duality">과목별 문제은행</div><div class="section-line"></div></div>
  {''.join(bks)}
</section>
</div>
"""
    doc = HEAD.format(title="산업안전기사 학습 노트", css=INDEX_CSS, accent="var(--green)") + body + FOOT.format(extra="", script=INDEX_JS.replace("PAGES", json.dumps(pages, ensure_ascii=False)))
    (OUT / "index.html").write_text(doc, encoding="utf-8")


index_page()
