#!/usr/bin/env python3
"""study-plan/*.md → sanan-notes HTML 페이지 생성 (한능검 노트와 같은 종이 노트 스타일)."""
import html, re, sys, json, os, base64, secrets
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

# 2027년 개편 5과목 체계 (옛 4과목 전기설비 + 5과목 화학설비 → 4과목, 옛 6과목 건설 → 5과목)
SUBJECTS = {
    1: ("산업재해 예방 및 안전보건교육", "var(--c1)"),
    2: ("인간공학 및 위험성 평가·관리", "var(--c2)"),
    3: ("기계·기구 및 설비 안전관리", "var(--c3)"),
    4: ("전기 및 화학설비 안전관리", "var(--c4)"),
    5: ("건설공사 안전관리", "var(--c6)"),
}
BLURB = {
    1: "안전관리조직, 안전보건관리체제, 보호구·표지, 산업심리·리더십, 안전보건교육·TWI",
    2: "FTA·신뢰도 계산, 휴먼에러, 소음·조명·온열 작업환경, 표시장치, 인체측정, 위험성 평가",
    3: "프레스·연삭기·공작기계 방호, 양중기·지게차, 보일러·가스용접, 재해통계·안전점검",
    4: "전기(감전·누전차단기·정전기·방폭·피뢰) + 화학(폭발범위·위험물·소화·화학설비) — 2027 통합 과목",
    5: "유해위험방지계획서, 비계·거푸집, 흙막이, 차량계 건설기계, 산업안전보건관리비, 추락방지",
}
# 첫 화면 '내 학습 현황'에 쓰는 짧은 과목 이름
SHORT = {1: "산업재해 예방·안전보건교육", 2: "인간공학·위험성 평가", 3: "기계·기구·설비 안전", 4: "전기·화학설비 안전", 5: "건설공사 안전"}
# 원본 md: study-plan/2027_5과목/ (tools/gen27로 만든 5과목 기출포인트·문제은행)
SRC27 = SRC / "2027_5과목"

CSS = """
:root{
  --bg:#F3F5F8;--surface:#FFFFFF;--surface2:#F7F8FA;--ink:#121A24;--ink-soft:#5A6573;--line:#E3E7EC;
  --hero:#1C2733;--hero-ink:#F4F6F8;--hero-soft:#AEB8C4;
  --yellow:#FFC21A;--yellow-soft:#FFF3C9;--mark:#FFE58A;
  --c1:#1F9D6B;--c2:#2F6FDE;--c3:#5B6B7E;--c4:#E0482E;--c5:#8A4FD8;--c6:#E07B12;--c7:#0E8A9A;--c8:#C2416B;
  --shadow:0 1px 2px rgba(16,24,40,.06),0 4px 14px rgba(16,24,40,.06);
  --cf:#6D3FD1;--cf-soft:#F1EBFF;--exp:#16865F;--exp-soft:#E7F6EF;
  --ok:#16865F;--ok-soft:#E3F5EC;--memo:#C25E00;--memo-soft:#FFF1E2;--ng:#D63B25;--ng-soft:#FDE9E5;
  --add:#0B7F8C;--add-soft:#E4F5F7;
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0F151C;--surface:#18212B;--surface2:#1E2833;--ink:#E8EDF2;--ink-soft:#9AA6B4;--line:#2A3541;
    --hero:#141C25;--yellow-soft:#3A3115;--mark:#5C4A12;--shadow:none;
    --cf:#B79CFF;--cf-soft:#2A2340;--exp:#5EC2A0;--exp-soft:#16302A;
    --ok:#5EC2A0;--ok-soft:#16302A;--memo:#FFB066;--memo-soft:#33251A;--ng:#FF7A63;--ng-soft:#3A1E1A;
    --add:#5CCAD6;--add-soft:#13302F;
  }
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{zoom:var(--fz,1)}
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
.exp{margin:4px 0 12px;padding:9px 12px;background:var(--exp-soft);border-radius:10px;font-size:14.6px;line-height:1.65}
.memo{margin:4px 0 12px;padding:9px 12px;background:var(--memo-soft);border-left:3px solid var(--memo);border-radius:10px;font-size:14px;line-height:1.65}
.memo-tag{display:block;margin-bottom:2px;font-size:12px;font-weight:700;color:var(--memo)}
.card .memo b{background:none;color:var(--memo);padding:0}
.exp-tag{display:block;margin-bottom:2px;font-size:12px;font-weight:700;color:var(--exp)}
ul.chk>li.cf .cf-tag{display:inline-block;margin-right:6px;font-size:12px;font-weight:700;color:var(--cf)}
ul.sub2{margin:6px 0 0;padding-left:14px;font-size:13.5px;color:var(--ink-soft)}
ul.sub2 li{margin-bottom:3px}
/* 기출포인트 보강 카드: 제목이 🆕로 시작하는 ### 카드 (기존 내용과 구분) */
.card.add{border:1.5px dashed var(--add);background:linear-gradient(var(--add-soft),var(--surface) 48px)}
.card.add h4{color:var(--add)}
.card.add h4::before{background:var(--add)}
.subnote{margin:0 0 12px;padding:9px 12px;background:var(--surface2);border-radius:10px;font-size:12.5px;color:var(--ink-soft);line-height:1.6}
.subnote::before{content:"ⓘ ";color:var(--accent,var(--c1));font-weight:700}
.subnote.std{background:transparent;border:1px dashed var(--line,#ccc);padding:7px 11px;font-size:12px}
.subnote.std::before{content:""}
/* 기출포인트·과목 문제은행: 줄이 꺾이지 않게 글자·여백을 줄임 (아래 미디어쿼리에서 휴대폰 +2px, PC 14px로 덮어씀) */
:is(body[data-page=points],body[data-subject^=s]) .card{padding:14px 12px 8px;letter-spacing:-.015em}
body[data-page=points] .card p,body[data-page=points] ul.chk>li{font-size:13px}
body[data-page=points] ul.chk>li:not(.star):not(.cf){padding-left:16px}
body[data-page=points] .card h4{font-size:15.5px}
body[data-page=points] ul.sub2{font-size:12.5px}
body[data-page=points] .card code{font-size:12.5px}
body[data-page=points] .exp{font-size:13px}
body[data-page=points] .memo{font-size:12.5px;padding:8px 10px}
body[data-page=points] .subnote{font-size:12.5px;padding:8px 10px}
body[data-page=points] .subnote.std{font-size:12px}
body[data-subject^=s] .q-body{font-size:14px}
body[data-subject^=s] .opts li{font-size:13px;padding:7px 10px}
body[data-subject^=s] .ans-body{padding:10px 10px 2px}
body[data-subject^=s] .ans-body p,body[data-subject^=s] .ans-body li{font-size:13px}
footer{margin-top:40px;padding:16px;background:var(--surface);border-radius:14px;border:1px solid var(--line);font-size:12px;color:var(--ink-soft);line-height:1.75}
footer a{color:var(--accent,var(--c1));font-weight:600}
/* 문제은행 */
.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;position:sticky;top:0;z-index:5;margin:0 -16px;padding:10px 16px;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.btn{font:inherit;font-size:13px;font-weight:600;background:var(--surface);color:var(--ink);border:1px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer}
.btn.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.tools .count{font-size:12px;color:var(--ink-soft);margin-left:auto}
.q-head{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.q-num{flex:0 0 auto;white-space:nowrap;font-weight:700;font-size:12.5px;color:var(--accent,var(--c1));background:color-mix(in srgb,var(--accent,var(--c1)) 12%,transparent);border-radius:8px;padding:2px 10px}
.q-ch{font-size:11.5px;color:var(--ink-soft);background:var(--surface2);border:1px solid var(--line);border-radius:8px;padding:1px 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
select.btn{max-width:100%;appearance:auto}
.q-meta{flex:0 0 auto;font-size:11.5px;font-weight:700;color:var(--memo);background:var(--memo-soft);border-radius:8px;padding:1px 7px;white-space:nowrap}
.q-meta+.q-meta{color:var(--ink-soft);background:var(--surface2);font-weight:600}
.q-meta.warn{color:var(--ng);background:var(--ng-soft)}
@media (max-width:420px){.q-head .q-ch{display:none}}
.tbl{overflow-x:auto;margin:0 0 10px}
.tbl table{border-collapse:collapse;font-size:12.5px;min-width:100%}
.tbl th,.tbl td{border:1px solid var(--line);padding:4px 7px;text-align:center;white-space:nowrap}
.tbl th{background:var(--surface2)}
/* 기출포인트: 🔁 기출 반복 출제 카드, 🔑 필수 암기 카드 */
.card.rep{border-left:4px solid var(--memo)}
.card.rep h4{color:var(--memo)}
.card.rep h4::before{background:var(--memo)}
.card.key{border-left:4px solid var(--yellow)}
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
.opts.pick li{cursor:pointer;-webkit-tap-highlight-color:transparent}
.opts.pick li:hover{border-color:var(--accent,var(--c1))}
.q.done .opts li{cursor:default}
.opts li.right{background:var(--ok-soft);border-color:var(--ok);color:var(--ink);font-weight:600}
.opts li.wrong{background:var(--ng-soft);border-color:var(--ng)}
.opts li.right::after{content:" ✓";color:var(--ok);font-weight:700}
.opts li.wrong::after{content:" ✗";color:var(--ng);font-weight:700}
.q-res{flex:0 0 auto;font-size:12px;font-weight:700;border-radius:8px;padding:2px 8px;white-space:nowrap}
.q-res:empty{display:none}
.q.ok{border-color:var(--ok)}.q.ok .q-res{color:var(--ok);background:var(--ok-soft)}
.q.ng{border-color:var(--ng)}.q.ng .q-res{color:var(--ng);background:var(--ng-soft)}
.q.marked.ok,.q.marked.ng{box-shadow:inset 0 0 0 1px #F2C94C,var(--shadow)}
.q-self{display:flex;gap:8px;justify-content:center;margin:2px 0 10px}
.q-self .btn{padding:6px 16px}
.q-self .ok-b{color:var(--ok);border-color:var(--ok)}.q-self .ng-b{color:var(--ng);border-color:var(--ng)}
.q-redo{display:none;margin:0 0 4px auto;font:inherit;font-size:12px;color:var(--ink-soft);background:none;border:0;padding:2px 4px;cursor:pointer;text-decoration:underline}
.q.done .q-redo{display:block}
.score{flex:1 1 100%;display:flex;flex-wrap:wrap;align-items:center;gap:4px 12px;font-size:12.5px;color:var(--ink-soft)}
.score>span:first-child{display:flex;flex-wrap:wrap;gap:4px 12px}
.score b{color:var(--ink)}.score .o b{color:var(--ok)}.score .x b{color:var(--ng)}
.score .count{margin-left:auto}
footer #gReset{display:block;margin-top:10px;font-size:12px;padding:4px 12px}
.brief{margin:0;font-size:12px;color:var(--hero-soft)}
details.howto{margin-top:4px}
details.howto summary{display:inline-block;cursor:pointer;font-size:12px;color:var(--hero-soft);text-decoration:underline;list-style:none}
details.howto summary::-webkit-details-marker{display:none}
details.howto .sub{margin-top:6px}
.hidden{display:none !important}
/* PC: 넓은 화면에서는 본문을 넓히고 전체를 키움 */
@media (min-width:1000px){body[data-page=points] .card p,body[data-page=points] ul.chk>li{font-size:14px}body[data-page=points] .exp{font-size:13px}body[data-page=points] .memo,body[data-page=points] ul.sub2,body[data-page=points] .card code{font-size:12.5px}body[data-page=points] .card h4{font-size:16.5px}body{zoom:calc(1.2*var(--fz,1));font-size:16px}.wrap{max-width:1160px;padding:0 24px 80px}body[data-subject] .wrap{max-width:920px}.cards{columns:2;column-gap:14px}.cards .card{break-inside:avoid;display:inline-block;width:100%}.card p,ul.chk>li,.opts li{font-size:15px}.card h4{font-size:16.5px}.q-body{font-size:16px}.opts{grid-template-columns:1fr 1fr}header{margin:0 -24px;padding:22px 32px 26px}.toc{margin-left:-32px;margin-right:-32px;padding-left:32px;padding-right:32px;flex-wrap:wrap;overflow:visible}.tools{margin:0 -24px;padding:10px 24px}}
/* 모바일(999px 이하) 본문 글자: 기존보다 2px 크게 (2026-11-04) */
@media (max-width:999px){.card p,ul.chk>li{font-size:16px}.card code{font-size:15px}.exp{font-size:16.6px}.memo{font-size:16px}ul.sub2{font-size:15.5px}.subnote{font-size:14.5px}.subnote.std{font-size:14px}.q-body{font-size:17px}.opts li{font-size:16px}.ans-body p,.ans-body li{font-size:15.8px}.tbl table{font-size:14.5px}body[data-page=points] .card p,body[data-page=points] ul.chk>li{font-size:15px}body[data-page=points] ul.sub2{font-size:14.5px}body[data-page=points] .card code{font-size:14.5px}body[data-page=points] .exp{font-size:15px}body[data-page=points] .memo{font-size:14.5px}body[data-page=points] .subnote{font-size:14.5px}body[data-page=points] .subnote.std{font-size:14px}body[data-subject^=s] .q-body{font-size:16px}body[data-subject^=s] .opts li{font-size:15px}body[data-subject^=s] .ans-body p,body[data-subject^=s] .ans-body li{font-size:15px}body[data-subject=core226] .q-body{font-size:17px}body[data-subject=core226] .ans-body p{font-size:16.8px}body[data-subject=core226] ul.chk>li{font-size:17px}body[data-subject=core226] .exp{font-size:17.6px}}
@media (min-width:1000px){:is(body[data-subject=core226],body[data-subject=practical]) .q-body,:is(body[data-subject=core226],body[data-subject=practical]) .ans-body p,:is(body[data-subject=core226],body[data-subject=practical]) ul.chk>li,:is(body[data-subject=core226],body[data-subject=practical]) .opts li{font-size:13px}:is(body[data-subject=core226],body[data-subject=practical]) .exp{font-size:12.6px}}
.section.off{display:none}#secSel{flex:1 1 calc(100% - 72px);min-width:0;font-weight:700;text-overflow:ellipsis}@media (min-width:1000px){#secSel{flex:0 1 auto;max-width:360px}}#qJump{width:64px;flex:0 0 auto;text-align:center}body[data-subject] .tools .count{font-size:11.5px}#qJump::-webkit-inner-spin-button{display:none}.sec-nav{display:flex;gap:8px;justify-content:space-between;margin:18px 0 6px}.sec-nav .btn{flex:1 1 0;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sec-nav .next{text-align:right}.to-top{position:fixed;right:16px;bottom:18px;z-index:6;width:44px;height:44px;border-radius:50%;border:1px solid var(--line);background:var(--surface);color:var(--ink);font-size:18px;box-shadow:0 2px 10px rgba(0,0,0,.15);cursor:pointer;opacity:0;pointer-events:none;transition:opacity .2s}.to-top.show{opacity:1;pointer-events:auto}.toc a.cur{color:#111;background:var(--yellow);border-color:var(--yellow)}.toc a.cur .n{color:#111}.card.flash{outline:3px solid var(--yellow);outline-offset:2px}
:is(body[data-subject=core226],body[data-subject=practical]) h1{font-size:clamp(20px,6vw,28px);white-space:nowrap}:is(body[data-subject=core226],body[data-subject=practical]) .eyebrow{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.02em}
@media (min-width:1600px){body{zoom:calc(1.38*var(--fz,1))}}
/* 글자 크기 조절: PC(1000px 이상)·모바일 따로 저장(localStorage sanan-fz-pc / sanan-fz-m) */
.fsz{display:inline-flex;align-items:center;gap:2px;margin:6px 0 14px 6px;vertical-align:top;background:rgba(255,255,255,.1);border-radius:999px;padding:1px 4px;font-size:12px;color:var(--hero-ink)}
.fsz button{font:inherit;font-weight:700;background:none;border:0;color:inherit;cursor:pointer;padding:3px 8px;line-height:1.2}
.fsz b{min-width:38px;text-align:center;font-weight:600;cursor:pointer}
/* 검색 결과로 들어온 카드: 위치·강조 (2026-11-22) */
.card[id]{scroll-margin-top:80px}
mark.hl{background:var(--mark);color:inherit;border-radius:3px;padding:0 1px}
/* 오답노트 */
#wrongSel{flex:0 1 auto;min-width:0;max-width:150px;text-overflow:ellipsis}
#wrongSel.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.q.rep .q-res{outline:1.5px solid var(--ng)}
.q.retry{border-style:dashed}
@media print{.fsz{display:none}}
@media print{header{background:none;color:#000}.tools,.q-star,.q-redo,.q-self{display:none}}
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
<script>try{{var z=localStorage.getItem(matchMedia("(min-width:1000px)").matches?"sanan-fz-pc":"sanan-fz-m");if(z)document.documentElement.style.setProperty("--fz",z)}}catch(e){{}}</script>
</head>
<body style="--accent:{accent}">
<div class="wrap">
"""

FOOT = """
<footer>{extra}</footer>
</div>
{script}
<script>
(function(){{
  var mq=matchMedia("(min-width:1000px)"),root=document.documentElement;
  function key(){{return mq.matches?"sanan-fz-pc":"sanan-fz-m"}}
  function get(){{var v=1;try{{v=parseFloat(localStorage.getItem(key()))||1}}catch(e){{}}return v}}
  var box=document.createElement("span");box.className="fsz";
  box.innerHTML='<button type="button" data-d="-1" aria-label="글자 작게">가−</button><b title="기본 크기로"></b><button type="button" data-d="1" aria-label="글자 크게">가+</button>';
  var lab=box.querySelector("b");
  function apply(v){{root.style.setProperty("--fz",v);lab.textContent=(mq.matches?"PC ":"폰 ")+Math.round(v*100)+"%"}}
  function set(v){{v=Math.min(1.5,Math.max(0.8,Math.round(v*20)/20));try{{v===1?localStorage.removeItem(key()):localStorage.setItem(key(),v)}}catch(e){{}}apply(v)}}
  box.addEventListener("click",function(e){{var b=e.target.closest("button");if(b)set(get()+0.05*b.dataset.d);else if(e.target===lab)set(1)}});
  (mq.addEventListener?mq.addEventListener("change",function(){{apply(get())}}):mq.addListener(function(){{apply(get())}}));
  var h=document.querySelector("header"),bk=h&&h.querySelector(".back");
  if(bk)bk.after(box);else if(h)h.prepend(box);
  apply(get());
}})();
</script>
</body>
</html>
"""


# 전체 검색 결과로 들어온 카드(주소 #카드id, ?hl=검색어): 필터를 풀고 카드로 이동, 검색어 강조, 잠깐 테두리 표시 (2026-11-22)
HIT_JS = """<script>
(function(){
  function mark(el,q){
    var ql=q.toLowerCase(),w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),ns=[],n,hitAns=false,hitTop=false;
    while(n=w.nextNode())if(n.nodeValue.toLowerCase().indexOf(ql)>=0&&!n.parentNode.closest('mark,script,button'))ns.push(n);
    ns.forEach(function(n){
      var t=n.nodeValue,tl=t.toLowerCase(),f=document.createDocumentFragment(),i=0,j;
      while((j=tl.indexOf(ql,i))>=0){f.appendChild(document.createTextNode(t.slice(i,j)));var m=document.createElement('mark');m.className='hl';m.textContent=t.slice(j,j+q.length);f.appendChild(m);i=j+q.length}
      f.appendChild(document.createTextNode(t.slice(i)));
      if(n.parentNode.closest('details.ans'))hitAns=true;else hitTop=true;
      n.parentNode.replaceChild(f,n);
    });
    return hitAns&&!hitTop;
  }
  function go(){
    var id;try{id=decodeURIComponent(location.hash.slice(1))}catch(e){return}
    var el=id&&document.getElementById(id);
    if(!el||!el.classList.contains('card'))return;
    if(el.classList.contains('hidden')){
      var cs=document.getElementById('chSel');if(cs&&cs.value){cs.value='';cs.dispatchEvent(new Event('change'))}
      ['onlyStar'].forEach(function(b){b=document.getElementById(b);if(b&&b.classList.contains('on'))b.click()});
      var ws=document.getElementById('wrongSel');if(ws&&ws.value){ws.value='';ws.dispatchEvent(new Event('change'))}
    }
    var q=null;try{q=new URLSearchParams(location.search).get('hl')}catch(e){}
    if(q&&q.trim()&&!el.dataset.hl){el.dataset.hl=1;var d=el.querySelector('details.ans');if(mark(el,q.trim())&&d)d.open=true}
    var tl=document.querySelector('.tools'),off=tl&&getComputedStyle(tl).position==='sticky'?tl.getBoundingClientRect().height+10:12;
    window.scrollTo({top:Math.max(0,el.getBoundingClientRect().top+window.pageYOffset-off),behavior:'instant'});
    el.classList.add('flash');setTimeout(function(){el.classList.remove('flash')},2600);
  }
  if(location.hash)setTimeout(go,60);
  window.addEventListener('hashchange',go);
})();
</script>"""

FOOT = FOOT.replace("</body>", HIT_JS.replace("{", "{{").replace("}", "}}") + "\n</body>")


def inline(s):
    s = html.escape(s.strip(), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def indent(l):
    return len(l) - len(l.lstrip(" "))


BULLET = re.compile(r"^(-|\d+\.)\s+")
CF_LABELS = ("바꿔치기 주의:", "헷갈리는 선지:")  # 시험 보기에서 정답처럼 나오는 틀린 선지 줄 (옛 이름도 인식)
EXP_LABEL = "💡 해설:"  # 정리본에 덧붙인 해설 문단
MEMO_LABEL = "🧠 암기법:"  # 기출포인트에 덧붙인 연상 암기법 문단


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


def table_html(rows):
    if not rows:
        return ""
    head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
    body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
    return f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def render_blocks(lines):
    """마크다운 조각 → HTML (목록·문단·인용만 쓰는 단순한 형식)."""
    out, i = [], 0
    lines = [l.rstrip("\n") for l in lines]
    while i < len(lines):
        l = lines[i]
        if not l.strip() or l.strip() == "---":
            i += 1
            continue
        if l.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            out.append(table_html(rows))
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
                cf = next((l for l in CF_LABELS if it[0].startswith(l)), None)
                first = it[0].replace("⭐", "").strip()
                if cf:
                    first = first[len(cf):].strip()
                body = render_item([first] + it[1:])
                if cf:
                    body = '<span class="cf-tag">🔀 바꿔치기 주의</span>' + body
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
        if buf and buf[0].startswith(MEMO_LABEL):
            buf[0] = buf[0][len(MEMO_LABEL):].strip()
            out.append('<div class="memo"><span class="memo-tag">💡 이렇게 외워보자</span>' + "<br>".join(buf) + "</div>")
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
        if st.startswith("📊"):
            toc.insert(0, f'<a class="ch" href="#freq">📊 출제 분석</a>')
            body.append(f'<section class="section" id="freq"><div class="section-head"><div class="duality">{html.escape(st)}</div><div class="section-line"></div></div>\n<div class="cards">' + "\n".join(f'<div class="card{" key" if ct and ct.startswith("🔑") else ""}" id="p{si}-{k}" data-title="{html.escape(ct or st)}">' + (f"<h4>{inline(ct)}</h4>" if ct else "") + f'{render_blocks(cl)}</div>' for k, (ct, cl) in enumerate(cards, 1)) + "</div></section>")
            continue
        if st.startswith("출제기준"):
            toc.append(f'<a class="ch" href="#std">{html.escape(st)}</a>')
            body.append(f'<section class="section" id="std"><div class="section-head"><div class="duality">{html.escape(st)}</div><div class="section-line"></div></div>\n<div class="cards">' + "\n".join(f'<div class="card" id="p{si}-{k}" data-title="{html.escape(st)}">{render_blocks(cl)}</div>' for k, (_, cl) in enumerate(cards, 1)) + "</div></section>")
            continue
        topics += 1
        num, t = sec_title(st)
        sid = f"t{si}"
        star = "⭐" in t
        t_clean = t.replace("⭐", "").strip()
        toc.append(f'<a href="#{sid}"><span class="n">{num}</span>{html.escape(t_clean)}{" ★" if star else ""}</a>')
        parts = []
        # 🔁 반복 출제 카드를 주제 맨 위에 먼저 보여 줌
        cards = sorted(cards, key=lambda c: 0 if c[0] and c[0].startswith("🔁") else 1)
        for k, (ct, cl) in enumerate(cards, 1):
            h = f"<h4>{inline(ct)}</h4>" if ct else ""
            cls = "card add" if ct and ct.startswith("🆕") else "card rep" if ct and ct.startswith("🔁") else "card"
            parts.append(f'<div class="{cls}" id="p{si}-{k}" data-title="{html.escape(t_clean)}{" · " + html.escape(ct) if ct else ""}">{h}{render_blocks(cl)}</div>')
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
    doc = HEAD.format(title=f"{n}과목 기출포인트 · {name}", css=CSS, accent=accent).replace(
        f'<body style="--accent:{accent}">', f'<body style="--accent:{accent}" data-page="points">') + header + "\n".join(body) + FOOT.format(extra=bank, script="")
    (OUT / f"s{n}-points.html").write_text(doc, encoding="utf-8")
    return topics


BANK_JS = """<script>
(function(){
  (function(){var B=document.body.dataset;if(!B.remap||!B.oldstore)return;
    ['sanan-star-','sanan-grade-'].forEach(function(p){try{
      if(localStorage.getItem(p+B.store)!==null)return;
      var o=JSON.parse(localStorage.getItem(p+B.oldstore)||'null');if(!o)return;
      var m=JSON.parse(B.remap),r={};Object.keys(o).forEach(function(k){if(m[k])r[m[k]]=o[k]});
      localStorage.setItem(p+B.store,JSON.stringify(r));
    }catch(e){}});
  })();
  var key='sanan-star-'+(document.body.dataset.store||document.body.dataset.subject);
  var marked={};
  try{marked=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){}
  function save(){try{localStorage.setItem(key,JSON.stringify(marked))}catch(e){}}
  var qs=[].slice.call(document.querySelectorAll('.q'));
  var cnt=document.getElementById('starCount');
  function upd(){cnt.textContent='★ '+(document.getElementById('score')?'':'다시 볼 문제 ')+Object.keys(marked).length+'개'}
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
  // 채점: 보기를 누르면 data-a(정답 번호)와 비교, 보기·정답 키가 없으면 정답 안의 맞음/틀림 버튼
  var store=document.body.dataset.store||document.body.dataset.subject;
  var gkey='sanan-grade-'+store,graded={},score=document.getElementById('score'),wrongSel=document.getElementById('wrongSel');
  try{graded=JSON.parse(localStorage.getItem(gkey)||'{}')}catch(e){}
  Object.keys(graded).forEach(function(id){if(!ids[id])delete graded[id]});
  function gsave(){try{localStorage.setItem(gkey,JSON.stringify(graded))}catch(e){}}
  // 오답 기록(sanan-hist-*): 문제별 {w:틀린 횟수,o:맞힌 횟수,s:틀린 뒤 연속으로 맞힌 횟수,d:다음 복습 시각(ms),m:졸업}
  // 틀리면 바로 복습 대상, 다시 맞힐 때마다 복습 간격을 1→3→7→14→30일로 늘리고 그 뒤 맞히면 졸업
  var hkey='sanan-hist-'+store,hist={},DAY=864e5,IV=[1,3,7,14,30];
  try{hist=JSON.parse(localStorage.getItem(hkey)||'{}')}catch(e){}
  Object.keys(hist).forEach(function(id){if(!ids[id])delete hist[id]});
  function hsave(){try{localStorage.setItem(hkey,JSON.stringify(hist))}catch(e){}}
  (function(){var ch=0;Object.keys(graded).forEach(function(id){if(graded[id].r==='x'&&!hist[id]){hist[id]={w:1,o:0,s:0,d:0};ch=1}});if(ch)hsave()})();
  function record(id,r){
    var h=hist[id],now=Date.now();
    if(r==='x'){h=hist[id]=h||{w:0,o:0,s:0,d:0};h.w++;h.s=0;h.d=now;delete h.m}
    else if(h){h.o++;h.s++;if(h.s>IV.length){h.m=1;h.d=0}else h.d=now+IV[h.s-1]*DAY}
    hsave();
  }
  function due(id){var h=hist[id];return !!h&&h.w>0&&!h.m&&(h.d||0)<=Date.now()}
  function rep(id){var h=hist[id];return !!h&&h.w>=2&&!h.m}
  var retry={},resetArm=0,gReset=document.getElementById('gReset');
  function g(id){return retry[id]===1?null:graded[id]}
  function gupd(){
    if(!score)return;
    var o=0,x=0;Object.keys(graded).forEach(function(id){graded[id].r==='o'?o++:x++});
    score.innerHTML='<span class="o">✅ 맞음 <b>'+o+'</b></span><span class="x">❌ 틀림 <b>'+x+'</b></span><span>미풀이 <b>'+(qs.length-o-x)+'</b></span>'+
      (o+x?'<span>정답률 <b>'+Math.round(o*100/(o+x))+'%</b></span>':'');
    gReset.classList.toggle('hidden',!(o+x));
    gReset.textContent=resetArm?'한 번 더 누르면 모두 지워져요':'채점 기록 지우기';
    if(wrongSel){
      var nx=0,nr=0,nd=0;qs.forEach(function(q){var id=q.dataset.q;if(graded[id]&&graded[id].r==='x')nx++;if(rep(id))nr++;if(due(id)||retry[id])nd++});
      var lab={'':'❌ 오답노트',x:'❌ 틀린 문제 '+nx,rep:'🔁 반복 오답 '+nr,due:'📅 다시 풀기 '+nd};
      [].forEach.call(wrongSel.options,function(op){op.textContent=lab[op.value]});
    }
  }
  if(gReset)gReset.addEventListener('click',function(){
    if(!resetArm){resetArm=1;gupd();setTimeout(function(){resetArm=0;gupd()},4000);return}
    resetArm=0;graded={};hist={};retry={};gsave();hsave();qs.forEach(show);gupd();filter();
  });
  function show(q){
    var id=q.dataset.q,gr=g(id),h=hist[id],res=q.querySelector('.q-res');
    q.classList.toggle('done',!!gr);q.classList.toggle('ok',!!gr&&gr.r==='o');q.classList.toggle('ng',!!gr&&gr.r==='x');
    q.classList.toggle('rep',!!gr&&gr.r==='x'&&rep(id));q.classList.toggle('retry',retry[id]===1);
    if(res)res.textContent=gr?(gr.r==='o'?'✅ 맞음':(h&&h.w>=2?'❌ '+h.w+'회 틀림':'❌ 틀림')):'';
    var a=q.dataset.a;
    q.querySelectorAll('.opts li').forEach(function(li){
      li.classList.toggle('right',!!gr&&!!a&&li.dataset.o===a);
      li.classList.toggle('wrong',!!gr&&!!gr.c&&li.dataset.o===String(gr.c)&&gr.c!=a);
    });
  }
  function set(q,r,c){
    var id=q.dataset.q;graded[id]={r:r};if(c)graded[id].c=c;if(retry[id])retry[id]=2;gsave();record(id,r);show(q);gupd();
    q.querySelector('details.ans').open=true;
  }
  if(score)qs.forEach(function(q){
    var a=q.dataset.a;
    show(q);
    if(a)q.querySelectorAll('.opts li').forEach(function(li){
      li.setAttribute('role','button');li.tabIndex=0;
      function pick(){if(g(q.dataset.q))return;set(q,li.dataset.o===a?'o':'x',+li.dataset.o)}
      li.addEventListener('click',pick);
      li.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();pick()}});
    });
    q.querySelectorAll('.q-self .btn').forEach(function(b){b.addEventListener('click',function(){if(!g(q.dataset.q))set(q,b.dataset.r)})});
    var redo=q.querySelector('.q-redo');
    if(redo)redo.addEventListener('click',function(){delete graded[q.dataset.q];gsave();show(q);gupd();q.querySelector('details.ans').open=false;filter()});
  });
  gupd();
  var chSel=document.getElementById('chSel');
  function filter(){
    var star=onlyStar.classList.contains('on'),w=wrongSel?wrongSel.value:'',ch=chSel?chSel.value:'';
    qs.forEach(function(q){var id=q.dataset.q;q.classList.toggle('hidden',(star&&!q.classList.contains('marked'))||(w==='x'&&!(graded[id]&&graded[id].r==='x'))||(w==='rep'&&!rep(id))||(w==='due'&&!retry[id])||(ch&&q.dataset.ch!==ch))});
    document.querySelectorAll('.section').forEach(function(s){
      s.classList.toggle('hidden',!s.querySelector('.q:not(.hidden)'));
    });
  }
  onlyStar.addEventListener('click',function(){onlyStar.classList.toggle('on');filter()});
  // 📅 오답 다시 풀기: 복습할 때가 된 오답을 골라 답을 가리고 새로 풀게 함(고른 목록은 끌 때까지 유지)
  function startRetry(){
    retry={};qs.forEach(function(q){var id=q.dataset.q;if(due(id))retry[id]=1});
    qs.forEach(function(q){show(q);if(retry[q.dataset.q])q.querySelector('details.ans').open=false});
  }
  function stopRetry(){retry={};qs.forEach(show)}
  if(wrongSel){
    wrongSel.addEventListener('change',function(){
      if(wrongSel.value==='due')startRetry();else if(Object.keys(retry).length)stopRetry();
      wrongSel.classList.toggle('on',!!wrongSel.value);gupd();filter();
      if(wrongSel.value)window.scrollTo({top:document.querySelector('.tools').getBoundingClientRect().top+window.pageYOffset-1});
    });
    if(/[?&]review=1/.test(location.search)){wrongSel.value='due';wrongSel.dispatchEvent(new Event('change'))}
  }
  if(chSel){
    try{chSel.value=sessionStorage.getItem(key+'-ch')||''}catch(e){}
    chSel.addEventListener('change',function(){try{sessionStorage.setItem(key+'-ch',chSel.value)}catch(e){}filter()});
    filter();
  }
})();
</script>"""


# 묶음(과목·주제)이 많은 문제집: 한 묶음씩 보기, 번호로 이동, 맨 위로, 마지막 위치 기억
PAGED_JS = """<script>
(function(){
  var pk='sanan-pos-'+document.body.dataset.subject,st={};
  try{st=JSON.parse(localStorage.getItem(pk)||'{}')}catch(e){}
  if(!st.y)st.y={};
  function save(){try{localStorage.setItem(pk,JSON.stringify(st))}catch(e){}}
  var secs=[].slice.call(document.querySelectorAll('section.section[id]')),ids=secs.map(function(s){return s.id});
  var sel=document.getElementById('secSel'),jump=document.getElementById('qJump'),toTop=document.getElementById('toTop'),
      tools=document.querySelector('.tools'),onlyStar=document.getElementById('onlyStar'),onlyWrong=document.getElementById('onlyWrong');
  function cur(){return sel.value}
  function apply(){
    var c=cur(),all=!c||onlyStar.classList.contains('on')||(onlyWrong&&onlyWrong.classList.contains('on'));
    secs.forEach(function(s){s.classList.toggle('off',!all&&s.id!==c)});
    document.querySelectorAll('nav.toc a').forEach(function(a){a.classList.toggle('cur',!!c&&a.getAttribute('href')==='#'+c)});
  }
  function listTop(){return document.querySelector('header').getBoundingClientRect().bottom+window.pageYOffset}
  function to(y,smooth){window.scrollTo({top:y,behavior:smooth?'smooth':'instant'})}
  function go(id,y){
    sel.value=id;st.sec=id;save();apply();
    if(y!=null)to(y);
  }
  secs.forEach(function(s,i){
    var nav=document.createElement('div');nav.className='sec-nav';
    function btn(j,cls,label){
      var b=document.createElement('button');b.type='button';b.className='btn '+cls;
      b.textContent=label;b.addEventListener('click',function(){go(ids[j],listTop())});nav.appendChild(b);
    }
    var name=function(j){return sel.querySelector('option[value="'+ids[j]+'"]').textContent};
    if(i>0)btn(i-1,'prev','‹ '+name(i-1));
    if(i<secs.length-1)btn(i+1,'next',name(i+1)+' ›');
    s.appendChild(nav);
  });
  sel.addEventListener('change',function(){go(sel.value,listTop())});
  document.querySelectorAll('nav.toc a').forEach(function(a){
    a.addEventListener('click',function(e){var id=a.getAttribute('href').slice(1);if(ids.indexOf(id)<0)return;e.preventDefault();go(id,listTop())});
  });
  onlyStar.addEventListener('click',apply);
  if(onlyWrong)onlyWrong.addEventListener('click',apply);
  function doJump(){
    var n=parseInt(jump.value,10);if(!n)return;
    var q=[].slice.call(document.querySelectorAll('.section:not(.off):not(.hidden) .q:not(.hidden)')).filter(function(q){return q.dataset.title===n+'번'})[0];
    if(!q){jump.value='';jump.placeholder='없음';setTimeout(function(){jump.placeholder='번호'},1500);return}
    to(q.getBoundingClientRect().top+window.pageYOffset-tools.offsetHeight-8,1);
    q.classList.add('flash');setTimeout(function(){q.classList.remove('flash')},1400);
    jump.blur();
  }
  jump.addEventListener('change',doJump);
  jump.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();doJump()}});
  toTop.addEventListener('click',function(){to(0,1)});
  var t=0;
  window.addEventListener('scroll',function(){
    toTop.classList.toggle('show',window.pageYOffset>600);
    clearTimeout(t);t=setTimeout(function(){st.y[cur()]=Math.round(window.pageYOffset);save()},250);
  },{passive:true});
  if('scrollRestoration' in history)history.scrollRestoration='manual';
  var h=location.hash.slice(1);
  function secOf(h){var el=null;try{el=document.getElementById(decodeURIComponent(h))}catch(e){}var s=el&&el.closest('section.section[id]');return s&&ids.indexOf(s.id)>=0&&s!==el?s.id:null}
  if(secOf(h)){go(secOf(h),null)}
  else if(ids.indexOf(h)>=0){go(h,null);secs[ids.indexOf(h)].scrollIntoView()}
  else{var s0=st.sec!=null&&(st.sec===''||ids.indexOf(st.sec)>=0)?st.sec:ids[0];sel.value=s0;apply();if(st.y[s0])to(st.y[s0])}
  window.addEventListener('hashchange',function(){var h=location.hash.slice(1);if(secOf(h))go(secOf(h),null);else if(ids.indexOf(h)>=0){go(h,null);secs[ids.indexOf(h)].scrollIntoView()}});
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


# 2026-11-05 문제은행에 2회 출제 문항을 더하면서 번호가 바뀜 → 저장 키를 -2027b로 바꾸고,
# 옛 키(-2027)의 ★·채점 기록을 remap_2027b.json(옛 번호 → 새 번호)으로 한 번 옮김
REMAP_FILE = SRC27 / "tools" / "remap_2027b.json"
REMAP = json.loads(REMAP_FILE.read_text(encoding="utf-8")) if REMAP_FILE.exists() else {}


def store_attrs(n, slug):
    base = slug.replace("-bank", "")
    rm = REMAP.get(str(n))
    if not rm:
        return f' data-store="{base}-2027"'
    return (f' data-store="{base}-2027b" data-oldstore="{base}-2027"'
            f' data-remap="{html.escape(json.dumps(rm, separators=(",", ":")))}"')


def bank_page(n, src, *, slug=None, tab=None, eyebrow=None, h1=None, title=None, extra=None, accent=None, notes=True, locked=False, per_section=False, grade=False, paged=False, store=""):
    """과목 문제은행. 실기처럼 과목이 아닌 문제집은 slug 등 키워드로 넘김.
    per_section=True면 번호가 묶음마다 1번부터라 ★ 저장 키를 "묶음-번호"로 씀.
    grade=True면 보기를 눌러 채점(정답 줄 "✅ **②"에서 정답을 읽음, 없으면 맞음/틀림 자가 채점)."""
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
    toc, body, total, sec_opts = [], [], 0, []
    for si, (st, cards) in enumerate(sections, 1):
        if "틀린 문제" in st:
            continue
        if not any(ct for ct, _ in cards):
            continue
        sid = f"g{si}"
        num, t = sec_title(st)
        toc.append(f'<a href="#{sid}"><span class="n">{html.escape(num)}</span>{html.escape(t)}</a>')
        sec_opts.append(f'<option value="{sid}">{html.escape(num)}. {html.escape(t)}</option>')
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
            meta = ""
            if stem and stem[0].startswith(("🔁", "🏷️")):
                meta = "".join(f'<span class="q-meta{" warn" if "⚠️" in p else ""}">{html.escape(p.strip())}</span>' for p in stem[0].removeprefix("🏷️").split(" · "))
                stem = stem[1:]
            tbl = [l for l in stem if l.lstrip().startswith("|")]
            stem = [l for l in stem if l not in tbl]
            stem_html = "<br>".join("· " + inline(l[2:]) if l.startswith("- ") else inline(l) for l in stem)
            a = re.search(r"✅\s*\**\s*([①②③④⑤])", ans_part) if grade else None
            marks = [o.strip()[:1] for o in opts]
            a_idx = marks.index(a.group(1)) + 1 if a and a.group(1) in marks else 0
            opts_html = "".join(f'<li data-o="{i}">{inline(o)}</li>' if a_idx else f"<li>{inline(o)}</li>" for i, o in enumerate(opts, 1))
            g_attr = f' data-a="{a_idx}"' if a_idx else ""
            res = '<span class="q-res"></span>' if grade else ""
            redo = '<button class="q-redo" type="button">다시 풀기</button>' if grade else ""
            self_g = '<div class="q-self"><button class="btn ok-b" type="button" data-r="o">⭕ 맞았어요</button><button class="btn ng-b" type="button" data-r="x">❌ 틀렸어요</button></div>' if grade and not a_idx else ""
            cid = q_ch.get(int(qn), "")
            chip = f'<span class="q-ch">CH{cid} {html.escape(dict((c[0], c[1]) for c in chapters)[cid])}</span>' if cid else ""
            parts.append(f"""<div class="card q" id="q{re.sub(r'\W', '-', qid)}" data-q="{qid}" data-ch="{cid}" data-title="{qn}번"{g_attr}>
<div class="q-head"><span class="q-num">{qn}번</span>{meta}{chip}{res}<button class="q-star" title="다시 볼 문제로 표시" aria-label="다시 볼 문제로 표시">★</button></div>
<p class="q-body">{stem_html}</p>{table_html([[c.strip() for c in l.strip().strip("|").split("|")] for l in tbl if not re.fullmatch(r"[\s|:-]+", l)]) if tbl else ""}
<ul class="opts{" pick" if a_idx else ""}">{opts_html}</ul>{redo}
<details class="ans"><summary><span class="o">정답 보기</span><span class="c">정답 닫기</span></summary><div class="ans-body">{self_g}{render_blocks(ans_part.splitlines())}</div></details>
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
    howto_list = intro_list(intro + (['- **보기를 누르면 바로 채점**됩니다. 맞으면 ✅, 틀리면 ❌가 문제에 붙고 이 기기에 저장됩니다.', '- **❌ 오답노트**에서 틀린 문제, 두 번 이상 틀린 🔁 반복 오답만 모아 보거나, 📅 **다시 풀기**로 답을 가리고 새로 풀 수 있습니다. 다시 맞힐 때마다 복습 간격이 1·3·7·14·30일로 늘어납니다.', '- 학습 기록은 이 기기 브라우저에 저장됩니다. 첫 화면 **내 학습 현황**에서 백업 파일로 내보내고 가져올 수 있습니다.'] if grade else []) + ['- 헷갈린 문제는 오른쪽 위 **★**을 눌러 두면 이 기기에 저장되고, "★만 보기"로 모아 풀 수 있습니다.'])
    # 과목 문제은행은 한 줄 요약만 보이고 자세한 안내는 접어 둠
    howto = f'<p class="brief">{"보기 누르면 채점 · " if grade else ""}★ 다시 볼 문제 · 법령 수치는 시험 전 확인</p><details class="howto"><summary>ⓘ 사용법</summary>{howto_list}</details>' if grade else howto_list
    header = f"""<header>
  <a class="back" href="index.html">← 목록으로</a>
  <span class="tab">{tab}</span>
  <div class="eyebrow">{eyebrow} · {total}문항</div>
  <h1>{h1}</h1>
  {howto if notes else ""}
  {"" if locked else f'<nav class="toc">{"".join(toc)}</nav>'}
</header>"""
    sec_sel = ('<select class="btn" id="secSel" aria-label="볼 묶음 고르기"><option value="">전체 보기</option>' + "".join(sec_opts) + '</select><input class="btn" id="qJump" type="number" inputmode="numeric" min="1" placeholder="번호" aria-label="번호로 이동">') if paged else ""
    content = (f'<nav class="toc">{"".join(toc)}</nav>' if locked else "\n") + f"""<div class="tools">{sec_sel}{ch_sel}<button class="btn" id="openAll">정답 모두 펼치기</button><button class="btn" id="onlyStar">★만 보기</button>{'<select class="btn" id="wrongSel" aria-label="오답노트"><option value="">❌ 오답노트</option><option value="x"></option><option value="rep"></option><option value="due"></option></select><div class="score"><span id="score"></span><span class="count" id="starCount"></span></div>' if grade else '<span class="count" id="starCount"></span>'}</div>""" + "\n".join(body)
    if grade:
        extra += '<button class="btn hidden" type="button" id="gReset">채점 기록 지우기</button>'
    script = BANK_JS
    if paged:
        content += '<button class="to-top" id="toTop" type="button" aria-label="맨 위로">▲</button>'
        script += PAGED_JS
    if locked:
        pw = page_password()
        if not pw:
            print(f"{slug}: 암호(study-plan/.page-password 또는 CISE_PAGE_PW)가 없어 건너뜀", file=sys.stderr)
            return total
        content = lock_html(content, pw)
        script = BANK_JS.replace("<script>", '<script type="text/plain" id="bankjs">', 1) + LOCK_JS
    doc = HEAD.format(title=title, css=CSS, accent=accent).replace(
        f'<body style="--accent:{accent}">', f'<body style="--accent:{accent}" data-subject="{slug.replace("-bank", "")}"' + (store_attrs(n, slug) if n in SUBJECTS else store) + '>') + header + content + FOOT.format(extra=extra, script=script)
    (OUT / f"{slug}.html").write_text(doc, encoding="utf-8")
    return total


def roadmap_page(src):
    title, intro, sections = split_doc(src)
    toc, body = [], []
    for si, (st, cards) in enumerate(sections, 1):
        num, t = sec_title(st)
        toc.append(f'<a href="#r{si}"><span class="n">{num}</span>{html.escape(t)}</a>')
        parts = [f'<div class="card" id="r{si}-{k}" data-title="{html.escape(t)}">' + (f"<h4>{inline(ct)}</h4>" if ct else "") + render_blocks(cl) + "</div>" for k, (ct, cl) in enumerate(cards, 1)]
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


BANKS = {n: SRC27 / f"{n}과목_문제은행.md" for n in SUBJECTS if (SRC27 / f"{n}과목_문제은행.md").exists()}
counts = {n: points_page(n, SRC27 / f"{n}과목_기출포인트.md") for n in SUBJECTS}
bank_counts = {n: bank_page(n, p, grade=True) for n, p in BANKS.items()}
roadmap_page(SRC / "산업안전기사_12주_로드맵.md")
PRACTICAL = SRC / "실기_필답형_핵심.md"
practical_count = bank_page("practical", PRACTICAL, slug="practical", tab="실기 · 필답형",
    eyebrow="산업안전기사 실기 · 필답형 2016~2026", h1="실기 필답형 핵심",
    title="실기 필답형 핵심", accent="var(--c7)", notes=False, per_section=True, paged=True,
    extra="번호는 주제마다 1번부터입니다. 🔧(용어·수치 바로잡음)·⚠️(법령·교재 확인 필요) 표시 문항은 교재로 한 번 더 확인하세요. 개념은 과목별 기출포인트에서 찾아볼 수 있습니다. ") if PRACTICAL.exists() else 0
CORE = SRC / "필기_핵심요약.md"
# 2026-11-09 핵심요약을 2027 5과목으로 재배치(옛 4·5과목 → 4과목 1~68번, 옛 6과목 → 5과목)
# → ★ 저장 키를 core226-2027로 바꾸고 옛 키(core226)의 ★를 remap_core2027.json으로 한 번 옮김
CORE_REMAP = SRC27 / "tools" / "remap_core2027.json"
core_store = (' data-store="core226-2027" data-oldstore="core226" data-remap="'
              + html.escape(json.dumps(json.loads(CORE_REMAP.read_text(encoding="utf-8")), separators=(",", ":"))) + '"') if CORE_REMAP.exists() else ""
core_count = bank_page("core", CORE, slug="core226", tab="필기 · 핵심요약",
    eyebrow="산업안전기사 필기 · 2027 개편 5과목", h1="필기 핵심요약",
    title="필기 핵심요약", accent="var(--c8)", notes=False, per_section=True, paged=True, store=core_store,
    extra="2027 개편 5과목 기준입니다. 번호는 과목마다 1번부터이고, 4과목은 1~33번 전기, 34~68번 화학입니다. 🔧(용어·수치 바로잡음)·⚠️(법령·교재 확인 필요) 표시 문항은 교재로 한 번 더 확인하세요. 더 자세한 개념은 과목별 기출포인트에 있습니다. ") if CORE.exists() else 0
print(counts, bank_counts, practical_count, core_count)

# 옛 6과목(건설) 주소는 새 5과목으로 보냄
for kind in ("points", "bank"):
    (OUT / f"s6-{kind}.html").write_text(f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>5과목으로 옮겼습니다</title><meta http-equiv="refresh" content="0; url=s5-{kind}.html">
<style>body{{font-family:sans-serif;padding:24px;background:#F3F5F8;color:#121A24}}@media (prefers-color-scheme:dark){{body{{background:#0F151C;color:#E8EDF2}}}}a{{color:#E07B12}}</style></head>
<body><p>2027년 개편으로 건설공사 안전관리는 5과목이 됐습니다. <a href="s5-{kind}.html">5과목으로 가기</a></p></body></html>
""", encoding="utf-8")


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

INDEX_CSS += """
.search-cats{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px}
.search-cats button{font:inherit;font-size:12px;font-weight:600;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:4px 10px;cursor:pointer}
.search-cats button b{color:var(--ink-soft);font-weight:600;margin-left:3px}
.search-cats button.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.search-cats button.on b{color:inherit}
.search-err{color:var(--ng)}
.search-err button{font:inherit;font-size:12px;margin-left:6px;padding:2px 10px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
.search-more{font-size:12px;color:var(--ink-soft);margin:4px 4px 0}
/* 내 학습 현황 (2026-11-22) */
.dash{padding:14px 14px 12px}
.dash-sum{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:12px}
@media (min-width:560px){.dash-sum{grid-template-columns:repeat(4,1fr)}}
.dash-sum div{background:var(--surface2);border-radius:12px;padding:9px 10px;min-width:0}
.dash-sum span{display:block;font-size:11.5px;color:var(--ink-soft);white-space:nowrap}
.dash-sum b{display:block;font-size:20px;line-height:1.3;background:none;padding:0;white-space:nowrap}
.dash-sum small{font-size:11.5px;color:var(--ink-soft);font-weight:500;margin-left:3px}
.dash-row{display:block;text-decoration:none;color:inherit;padding:9px 2px;border-top:1px solid var(--line)}
.dash-row .top{display:flex;align-items:center;gap:8px;font-size:13.5px;font-weight:700;min-width:0}
.dash-row .no{flex:0 0 auto;width:22px;height:22px;border-radius:7px;background:var(--c);color:#fff;font-size:12px;display:inline-flex;align-items:center;justify-content:center}
.dash-row .nm{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dash-row .weak{flex:0 0 auto;font-size:11px;color:var(--ng);background:var(--ng-soft);border-radius:6px;padding:0 6px}
.dash-row .rate{margin-left:auto;flex:0 0 auto;font-size:13.5px}
.dash-row .rate.lo{color:var(--ng)}.dash-row .rate.mid{color:var(--memo)}.dash-row .rate.hi{color:var(--ok)}.dash-row .rate.none{color:var(--ink-soft);font-weight:500;font-size:12px}
.dash-bar{height:6px;border-radius:3px;background:var(--surface2);margin:6px 0 4px;overflow:hidden}
.dash-bar i{display:block;height:100%;background:var(--c);border-radius:3px}
.dash-row .meta{display:flex;flex-wrap:wrap;gap:2px 10px;font-size:11.5px;color:var(--ink-soft)}
.dash-row .meta .rv{color:var(--ng);font-weight:700}
.dash .dash-note{font-size:12.5px;color:var(--ink-soft);margin:8px 2px 0}
.dash-bak{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:10px;padding-top:10px;border-top:1px dashed var(--line)}
.dash-bak .btn{font-size:12.5px;padding:6px 12px}
.dash-bak .msg{flex:1 1 100%;font-size:12px;color:var(--ink-soft)}
.dash-bak .msg button{font:inherit;font-size:12px;color:var(--ink);background:none;border:0;text-decoration:underline;cursor:pointer;padding:0 2px}
.dash-bak .msg.err{color:var(--ng)}
"""

INDEX_JS = """<script>
(function(){
  var pages=PAGES,input=document.getElementById('siteSearch'),status=document.getElementById('searchStatus'),
      box=document.getElementById('searchResults'),all=document.getElementById('allSections'),index=null,loading=null,failed=[],cat='';
  function load(){
    if(loading)return loading;
    status.textContent='노트 불러오는 중…';
    loading=Promise.all(pages.map(function(p){
      return fetch(p.href).then(function(r){if(!r.ok)throw new Error(r.status);return r.text()}).then(function(t){
        var doc=new DOMParser().parseFromString(t,'text/html'),out=[];
        [].forEach.call(doc.querySelectorAll('.card'),function(c){
          var sec=c.closest('.section'),sd=sec&&sec.querySelector('.duality'),sn=sd?txt(sd):'',ti=c.dataset.title||'';
          if(sn&&ti.indexOf(sn.replace(/^\\S+\\s/,''))<0&&/^\\d+번$/.test(ti))ti=sn+' · '+ti;
          out.push({page:p.name,href:p.href,id:c.id||(sec&&sec.id)||'',title:ti,text:txt(c)});
        });
        if(!out.length)throw new Error('empty');
        return out;
      }).catch(function(){failed.push(p.name);return []});
    })).then(function(a){
      index=[].concat.apply([],a);
      if(failed.length===pages.length){loading=null;index=null;failed=[];throw new Error('all')}
      return index;
    });
    return loading;
  }
  function txt(el){var w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),a=[],n;while(n=w.nextNode())if(!n.parentNode.closest('button,summary,.q-self'))a.push(n.nodeValue);return a.join(' ').replace(/\\s+/g,' ').trim()}
  function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function retryBtn(msg){
    status.innerHTML='<span class="search-err">'+msg+'<button type="button" id="searchRetry">다시 시도</button></span>';
    document.getElementById('searchRetry').addEventListener('click',function(){loading=null;index=null;failed=[];run()});
  }
  function run(){
    var q=input.value.trim();
    if(!q){box.classList.add('hidden');all.classList.remove('hidden');status.textContent='';return}
    load().then(function(idx){
      if(input.value.trim()!==q)return;
      var ql=q.toLowerCase(),hits=idx.filter(function(e){return e.text.toLowerCase().indexOf(ql)>=0}),by={},order=[];
      hits.forEach(function(h){if(!by[h.page]){by[h.page]=0;order.push(h.page)}by[h.page]++});
      if(cat&&!by[cat])cat='';
      var shown=cat?hits.filter(function(h){return h.page===cat}):hits;
      status.textContent=hits.length?hits.length+'개 카드에서 찾음'+(order.length>1?' · '+order.length+'곳':''):'';
      if(failed.length)retryBtn((hits.length?hits.length+'개 찾음 · ':'')+'못 불러온 노트가 있어 결과가 빠졌을 수 있어요: '+failed.join(', '));
      var re=new RegExp(q.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&'),'gi');
      var cats=order.length>1?'<div class="search-cats">'+['<button type="button" data-c=""'+(cat?'':' class="on"')+'>전체<b>'+hits.length+'</b></button>'].concat(order.map(function(p){return '<button type="button" data-c="'+esc(p)+'"'+(cat===p?' class="on"':'')+'>'+esc(p)+'<b>'+by[p]+'</b></button>'})).join('')+'</div>':'';
      box.innerHTML=cats+(shown.slice(0,80).map(function(h){
        var i=h.text.toLowerCase().indexOf(ql),s=Math.max(0,i-40),snip=(s>0?'…':'')+h.text.slice(s,i+q.length+70)+'…';
        var url=h.href+'?hl='+encodeURIComponent(q)+(h.id?'#'+encodeURIComponent(h.id):'');
        return '<a class="search-result" href="'+esc(url)+'"><h4>'+esc(h.page)+' · '+esc(h.title)+'</h4><p>'+esc(snip).replace(re,function(m){return '<mark>'+m+'</mark>'})+'</p></a>';
      }).join('')||'<p class="search-status">검색 결과가 없습니다.</p>')+(shown.length>80?'<p class="search-more">처음 80개만 보여요. 위에서 노트를 고르거나 검색어를 더 길게 써 보세요.</p>':'');
      box.classList.remove('hidden');all.classList.add('hidden');
    }).catch(function(){
      if(input.value.trim()!==q)return;
      box.classList.add('hidden');all.classList.remove('hidden');
      retryBtn(location.protocol==='file:'?'파일로 연 페이지에서는 검색할 수 없어요. 사이트 주소로 열어 주세요.':'노트를 불러오지 못해 검색할 수 없어요. 인터넷 연결을 확인해 주세요.');
    });
  }
  box.addEventListener('click',function(e){var b=e.target.closest('.search-cats button');if(!b)return;cat=b.dataset.c;run()});
  var t;input.addEventListener('input',function(){clearTimeout(t);cat='';t=setTimeout(run,200)});
})();
</script>
<script>
// 내 학습 현황 + 학습 기록 백업·복원 (기록은 이 기기 localStorage의 sanan-* 키)
(function(){
  var SUBJ=DASH,el=function(id){return document.getElementById(id)},DAY=864e5;
  function get(k){try{return JSON.parse(localStorage.getItem(k)||'null')}catch(e){return null}}
  function migrate(s){
    if(!s.old||!s.remap)return;
    ['sanan-star-','sanan-grade-'].forEach(function(p){try{
      if(localStorage.getItem(p+s.store)!==null)return;
      var o=get(p+s.old);if(!o)return;var r={};Object.keys(o).forEach(function(k){if(s.remap[k])r[s.remap[k]]=o[k]});
      localStorage.setItem(p+s.store,JSON.stringify(r));
    }catch(e){}});
  }
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function stat(s){
    if(s.total)migrate(s);
    var g=get('sanan-grade-'+s.store)||{},h=get('sanan-hist-'+s.store)||{},st=get('sanan-star-'+s.store)||{},now=Date.now();
    var ok=function(id){return !s.total||(+id>=1&&+id<=s.total)};
    var r={o:0,x:0,rep:0,due:0,star:Object.keys(st).filter(ok).length};
    Object.keys(g).filter(ok).forEach(function(id){g[id]&&g[id].r==='o'?r.o++:r.x++;if(g[id]&&g[id].r==='x'&&!h[id])r.due++});
    Object.keys(h).filter(ok).forEach(function(id){var e=h[id];if(!e||!e.w||e.m)return;if(e.w>=2)r.rep++;if((e.d||0)<=now)r.due++});
    return r;
  }
  function rateCls(p){return p<40?'lo':p<60?'mid':'hi'}
  function render(){
    var T={tot:0,o:0,x:0,rep:0,due:0,star:0},rows=[],st=[];
    SUBJ.forEach(function(s){var r=stat(s);st.push(r);T.star+=r.star;if(!s.total)return;T.tot+=s.total;T.o+=r.o;T.x+=r.x;T.rep+=r.rep;T.due+=r.due});
    var weak=-1,wr=101;
    SUBJ.forEach(function(s,i){var r=st[i],n=r.o+r.x;if(s.total&&n>=10){var p=r.o*100/n;if(p<wr){wr=p;weak=i}}});
    if(SUBJ.filter(function(s,i){return s.total&&st[i].o+st[i].x>=10}).length<2)weak=-1;
    SUBJ.forEach(function(s,i){
      if(!s.total)return;var r=st[i],n=r.o+r.x,p=n?Math.round(r.o*100/n):0;
      rows.push('<a class="dash-row" style="--c:'+s.color+'" href="'+s.href+(r.due?'?review=1':'')+'"><div class="top"><span class="no">'+s.n+'</span><span class="nm">'+esc(s.name)+'</span>'+(i===weak?'<span class="weak">취약</span>':'')+
        '<span class="rate '+(n?rateCls(p):'none')+'">'+(n?'정답률 '+p+'%':'시작 전')+'</span></div>'+
        '<div class="dash-bar"><i style="width:'+(n*100/s.total).toFixed(1)+'%"></i></div>'+
        '<div class="meta"><span>풀이 '+n+'/'+s.total+'</span>'+(r.x?'<span>❌ '+r.x+'</span>':'')+(r.rep?'<span>🔁 반복 '+r.rep+'</span>':'')+(r.star?'<span>★ '+r.star+'</span>':'')+(r.due?'<span class="rv">📅 다시 풀 오답 '+r.due+' ›</span>':'')+'</div></a>');
    });
    var n=T.o+T.x,p=n?Math.round(T.o*100/n):0;
    el('dashSum').innerHTML='<div><span>학습률 (풀이 문제)</span><b>'+(function(v){return v>0&&v<10?v.toFixed(1):Math.round(v)})(T.tot?n*100/T.tot:0)+'%<small>'+n+'/'+T.tot+'</small></b></div>'+
      '<div><span>정답률</span><b'+(n?' style="color:var(--'+(p<40?'ng':p<60?'memo':'ok')+')"':'')+'>'+(n?p+'%':'–')+'</b></div>'+
      '<div><span>오답 · 반복 오답</span><b>'+T.x+'<small>🔁 '+T.rep+'</small></b></div>'+
      '<div><span>★ 다시 볼 문제</span><b>'+T.star+'</b></div>';
    el('dashRows').innerHTML=rows.join('');
    el('dashNote').textContent=n?(T.due?'📅 오늘 다시 풀 오답이 '+T.due+'개 있어요. 과목을 누르면 바로 시작해요.':'다시 풀 오답이 없어요. 과목을 누르면 문제은행으로 가요.')+(weak>=0?' 취약은 10문제 이상 푼 과목 중 정답률이 가장 낮은 과목이에요.':''):'문제은행에서 보기를 누르면 여기에 과목별 진도와 정답률이 쌓여요.';
    bakInfo();
  }
  // 백업·복원
  var msg=el('bakMsg');
  function keys(){var a=[];for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k&&k.indexOf('sanan-')===0&&k.indexOf('sanan-pw-')!==0)a.push(k)}return a.sort()}
  function snap(){var d={};keys().forEach(function(k){d[k]=localStorage.getItem(k)});return d}
  function ago(t){var d=Math.floor((Date.now()-t)/DAY);return d<1?'오늘':d+'일 전'}
  function bakInfo(extra,err){
    var last=0;try{last=+localStorage.getItem('cise-lastexport')||0}catch(e){}
    msg.className='msg'+(err?' err':'');
    msg.innerHTML=extra||(keys().length?(last?'마지막 내보내기: '+ago(last)+'. ':'아직 내보낸 적이 없어요. ')+'기록은 이 브라우저에만 있으니 가끔 파일로 내보내 두세요.':'기록은 이 브라우저에만 저장돼요. 다른 기기 기록은 파일로 가져올 수 있어요.');
  }
  el('bakOut').addEventListener('click',function(){
    try{
      var d=snap(),now=new Date(),blob=new Blob([JSON.stringify({app:'cise-study',v:1,at:now.toISOString(),data:d},null,1)],{type:'application/json'});
      var a=document.createElement('a'),ymd=now.getFullYear()+String(now.getMonth()+1).padStart(2,'0')+String(now.getDate()).padStart(2,'0');
      a.href=URL.createObjectURL(blob);a.download='cise-study-backup-'+ymd+'.json';document.body.appendChild(a);a.click();a.remove();
      setTimeout(function(){URL.revokeObjectURL(a.href)},4000);
      try{localStorage.setItem('cise-lastexport',Date.now())}catch(e){}
      bakInfo('📤 기록 '+Object.keys(d).length+'개 항목을 파일로 내보냈어요. 다운로드 폴더를 확인하세요.');
    }catch(e){bakInfo('내보내기에 실패했어요: '+esc(e.message),1)}
  });
  el('bakIn').addEventListener('change',function(){
    var f=this.files&&this.files[0];this.value='';if(!f)return;
    var rd=new FileReader();
    rd.onload=function(){
      var o;try{o=JSON.parse(rd.result)}catch(e){return bakInfo('JSON 파일이 아니에요. 이 사이트에서 내보낸 파일을 골라 주세요.',1)}
      if(!o||o.app!=='cise-study'||!o.data||typeof o.data!=='object')return bakInfo('이 사이트의 학습 기록 파일이 아니에요.',1);
      var ks=Object.keys(o.data).filter(function(k){return k.indexOf('sanan-')===0&&k.indexOf('sanan-pw-')!==0&&typeof o.data[k]==='string'});
      if(!ks.length)return bakInfo('파일에 가져올 기록이 없어요.',1);
      try{
        localStorage.setItem('cise-undo',JSON.stringify(snap()));
        ks.forEach(function(k){localStorage.setItem(k,o.data[k])});
      }catch(e){return bakInfo('저장하지 못했어요(브라우저 저장 공간을 확인하세요).',1)}
      render();
      bakInfo('📥 '+(o.at?o.at.slice(0,10)+' ':'')+'백업에서 '+ks.length+'개 항목을 가져왔어요. <button type="button" id="bakUndo">가져오기 전으로 되돌리기</button>');
      el('bakUndo').addEventListener('click',function(){
        try{var u=JSON.parse(localStorage.getItem('cise-undo')||'null');if(!u)return;keys().forEach(function(k){localStorage.removeItem(k)});Object.keys(u).forEach(function(k){localStorage.setItem(k,u[k])});localStorage.removeItem('cise-undo')}catch(e){}
        render();bakInfo('가져오기 전 기록으로 되돌렸어요.');
      });
    };
    rd.onerror=function(){bakInfo('파일을 읽지 못했어요.',1)};
    rd.readAsText(f);
  });
  try{render()}catch(e){el('dashNote').textContent='학습 기록을 읽지 못했어요(브라우저 저장소가 꺼져 있을 수 있어요).'}
  window.addEventListener('pageshow',function(e){if(e.persisted)try{render()}catch(x){}});
  window.addEventListener('storage',function(){try{render()}catch(x){}});
})();
</script>"""

def index_page():
    tiles, pages, dash = [], [{"name": "12주 로드맵", "href": "roadmap.html"}], []
    for n, (name, color) in SUBJECTS.items():
        pages.append({"name": f"{n}과목 기출포인트", "href": f"s{n}-points.html"})
        if n in bank_counts:
            pages.append({"name": f"{n}과목 문제은행", "href": f"s{n}-bank.html"})
            bank = f'<a class="bk" href="s{n}-bank.html">문제은행<small>{bank_counts[n]}문항</small></a>'
        else:
            bank = '<a class="off" href="#" aria-disabled="true">문제은행<small>준비 중</small></a>'
        if n in bank_counts:
            st = store_attrs(n, f"s{n}-bank")
            m = re.search(r'data-store="([^"]+)"', st)
            rm = REMAP.get(str(n))
            dash.append({"n": n, "name": SHORT[n], "color": color, "href": f"s{n}-bank.html", "total": bank_counts[n],
                         "store": m.group(1), **({"old": f"s{n}-2027", "remap": rm} if rm else {})})
        tiles.append(f"""<div class="subj" style="--c:{color}">
    <div class="subj-top"><div class="subj-no">{n}</div><h3>{name}</h3></div>
    <p>{BLURB[n]}</p>
    <div class="subj-btns"><a class="pt" href="s{n}-points.html">기출포인트<small>{counts[n]}주제</small></a>{bank}</div>
  </div>""")
    if core_count:
        pages.append({"name": "필기 핵심요약", "href": "core226.html"})
        dash.append({"n": "★", "name": "필기 핵심요약", "store": "core226-2027" if core_store else "core226"})
    if practical_count:
        pages.append({"name": "실기 필답형", "href": "practical.html"})
        dash.append({"n": "✍", "name": "실기 필답형", "store": "practical"})
    core = f"""<section class="section">
  <div class="section-head"><div class="duality">필기 요약</div></div>
  <a class="plan" href="core226.html"><div class="ic" style="background:var(--c8);color:#fff">★</div><div><b>필기 핵심 정리({core_count}문항)</b></div><div class="go">›</div></a>
</section>""" if core_count else ""
    practical = f"""<section class="section">
  <div class="section-head"><div class="duality">실기</div></div>
  <a class="plan" href="practical.html"><div class="ic" style="background:var(--c7);color:#fff">✍</div><div><b>실기 필답형 핵심({practical_count}문항)</b></div><div class="go">›</div></a>
</section>""" if practical_count else ""
    body = f"""<header>
  <div class="eyebrow" style="margin-top:14px">CISE · 산업안전기사 필기 · 2027 개편 5과목</div>
  <h1>과목별 기출포인트와<br>문제은행</h1>
  <div class="hero-meta"><span><b>5과목</b> (전기·화학 통합)</span><span>과목별 <b>40점↑</b></span><span>평균 <b>60점↑</b> 합격</span></div>
  <div style="height:22px"></div>
</header>

<div class="search-wrap">
  <input type="search" id="siteSearch" class="search-input" placeholder="🔍 전체 검색 — 도수율, 파열판, 접지, 비계" autocomplete="off">
  <div class="search-status" id="searchStatus"></div>
</div>
<div class="search-results hidden" id="searchResults"></div>

<div id="allSections">
<section class="section" id="dash" style="margin-top:14px">
  <div class="section-head"><div class="duality">내 학습 현황</div></div>
  <div class="card dash">
    <div class="dash-sum" id="dashSum"></div>
    <div id="dashRows"></div>
    <p class="dash-note" id="dashNote"></p>
    <div class="dash-bak"><button class="btn" type="button" id="bakOut">📤 기록 내보내기</button><label class="btn" for="bakIn">📥 기록 가져오기</label><input type="file" id="bakIn" accept=".json,application/json" hidden><span class="msg" id="bakMsg"></span></div>
  </div>
</section>
<section class="section">
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
    doc = HEAD.format(title="산업안전기사 학습 노트", css=INDEX_CSS, accent="var(--c1)") + body + FOOT.format(extra="", script=INDEX_JS.replace("PAGES", json.dumps(pages, ensure_ascii=False)).replace("DASH", json.dumps(dash, ensure_ascii=False, separators=(",", ":"))))
    (OUT / "index.html").write_text(doc, encoding="utf-8")


index_page()
