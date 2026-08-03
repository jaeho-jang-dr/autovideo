# -*- coding: utf-8 -*-
"""W24 시나리오 + 캐릭터별 동작 트랙 검수 페이지 생성 (2026-08-03).

두 원본 문서를 **파싱해서** 만든다 — 문서를 고치면 다시 돌리기만 하면 화면이 따라온다.
  W24/W24_scenario.md  : - **S<n>** 제목 | `글리프` | "KO" → (EN) | `bg`[TYPE] | 모션 | 태그
  W24_motion.md        : ### S<n> `bg` | 구도  /  - **캐릭터** Z.. | `포즈`(방향) — 설명

사용: python make_w24_review_page.py   → W24/review_w24.html
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
SCEN = "W24/W24_scenario.md"
MOTION = "W24_motion.md"
OUT = "W24/review_w24.html"

# 캐릭터 → (그룹, 색)
CHARS = {
    "졸라맨":   ("A", "#5ec8f0"), "졸라걸": ("A", "#f0a85e"), "스틱맨": ("A", "#b48cf0"),
    "인준":     ("B", "#5e8cf0"), "지은":   ("B", "#f0d05e"),
    "티쳐제이": ("C", "#6fd39b"), "마담제이": ("C", "#f07e9b"),
}
GROUP_OF_SCENE = {}


def parse_scenario(path):
    out = {}
    for ln in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^- \*\*S(\d+)\*\*\s*(.*)$", ln)
        if not m:
            continue
        parts = [p.strip() for p in m.group(2).split("|")]
        if len(parts) < 4:
            continue
        seq = int(m.group(1))
        title = parts[0]
        glyph = parts[1].strip().strip("`").strip()
        narr = parts[2]
        ka = re.split(r"\s*→\s*(?=\()", narr, maxsplit=1)
        kside, eside = (ka if len(ka) == 2 else (narr, ""))
        km = re.search(r'"([^"]*)"', kside)
        ko = km.group(1).strip() if km else kside.strip().strip('"')
        eside = eside.strip()
        if eside.startswith("(") and eside.endswith(")"):
            eside = eside[1:-1].strip()
        bm = re.search(r"`?([a-z_]+)`?\s*\[(\w+)\]", parts[3])
        out[seq] = dict(title=title, glyph=glyph, ko=ko, en=eside,
                        bg=bm.group(1) if bm else "?", bgtype=bm.group(2) if bm else "?",
                        tag=parts[5] if len(parts) > 5 else "")
    return out


def parse_motion(path):
    """### S<n> ... 아래에 달린 `- **캐릭터** ...` 줄과 `※` 줄을 모은다."""
    scenes, cur = {}, None
    for ln in open(path, encoding="utf-8").read().splitlines():
        h = re.match(r"^### S(\d+)\s*(.*)$", ln)
        if h:
            cur = int(h.group(1))
            scenes[cur] = dict(head=h.group(2).strip(), tracks=[], notes=[])
            continue
        if cur is None:
            continue
        if ln.startswith("### ") or ln.startswith("## "):
            cur = None
            continue
        body = ln.strip()
        if body.startswith("- "):
            body = body[2:].strip()
        # ★메모(※)를 트랙보다 **먼저** 걸러낸다 — '- ※상호작용: **A** ↔ B' 가 트랙으로 잡히던 버그
        if body.startswith("※"):
            scenes[cur]["notes"].append(body.lstrip("※").strip())
            continue
        t = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", body)
        if t:
            scenes[cur]["tracks"].append((t.group(1).strip(), t.group(2).strip()))
        elif body.startswith("(인물 없음)"):
            scenes[cur]["tracks"].append(("(인물 없음)", body))
    return scenes


def deco(s):
    """`코드` → <code>, **굵게** → <b>, ★ 강조."""
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = s.replace("★", '<span class="star">★</span>')
    return s


def scene_group(tracks):
    gs = {CHARS[n][0] for n, _ in tracks if n in CHARS}
    if not gs:
        return "-"
    if len(gs) >= 3:
        return "전원"
    return "+".join(sorted(gs))


def main():
    sc = parse_scenario(SCEN)
    mo = parse_motion(MOTION)
    rows = []
    for n in sorted(sc):
        s = sc[n]
        m = mo.get(n, dict(head="", tracks=[], notes=[]))
        grp = scene_group(m["tracks"])
        tr = []
        for name, body in m["tracks"]:
            col = CHARS.get(name, ("", "#8b96a8"))[1]
            g = CHARS.get(name, ("-",))[0]
            tr.append(
                f'<div class="tk"><span class="nm" style="border-color:{col};color:{col}">'
                f'{html.escape(name)}</span><span class="gp">{g}</span>'
                f'<span class="bd">{deco(body)}</span></div>')
        notes = "".join(f'<div class="note">※ {deco(x)}</div>' for x in m["notes"])
        if not tr:
            tr = ['<div class="tk"><span class="bd" style="color:#ff7b72">'
                  '★동작 트랙 없음 — W24_motion.md 확인</span></div>']
        rows.append(f"""
<div class="scene" data-g="{grp}">
  <div class="hd">
    <span class="sn">S{n}</span>
    <span class="ti">{html.escape(s['title'])}</span>
    <span class="bg">{html.escape(s['bg'])}<i>{s['bgtype']}</i></span>
    <span class="grp g{grp.replace('+','').replace('전원','ALL')}">{grp}</span>
    <span class="tag">{html.escape(s['tag'])}</span>
  </div>
  <div class="gl">{html.escape(s['glyph'])}</div>
  <div class="ko">{html.escape(s['ko'])}</div>
  <div class="en">{html.escape(s['en'])}</div>
  <div class="mo">{''.join(tr)}{notes}</div>
</div>""")

    n_video = sum(1 for s in sc.values() if s["bgtype"] == "VIDEO")
    body = f"""<!doctype html>
<meta charset="utf-8">
<title>W24 검수 — 시나리오 + 캐릭터별 동작</title>
<style>
 body{{margin:0;background:#0b0d12;color:#e8ecf4;font-family:"Malgun Gothic",sans-serif;font-size:14px}}
 .wrap{{max-width:1120px;margin:0 auto;padding:22px 22px 60px}}
 h1{{font-size:20px;margin:0 0 4px}}
 .sub{{font-size:13px;color:#8b96a8;margin-bottom:14px;line-height:1.7}}
 .bar{{position:sticky;top:0;background:#0b0d12;padding:10px 0;z-index:5;
      border-bottom:1px solid #1e2532;margin-bottom:14px;display:flex;gap:7px;flex-wrap:wrap}}
 button{{background:#1b2130;color:#dfe6f2;border:1px solid #2c3549;border-radius:7px;
        padding:7px 13px;font-size:13px;cursor:pointer}}
 button:hover{{background:#252d40}} button.on{{background:#2f6df6;border-color:#2f6df6;color:#fff}}
 .scene{{border:1px solid #1e2532;border-radius:10px;padding:13px 15px;margin-bottom:11px;background:#10141c}}
 .hd{{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-bottom:7px}}
 .sn{{font-weight:bold;color:#63d2a4;font-variant-numeric:tabular-nums}}
 .ti{{font-weight:bold}}
 .bg{{font-size:11px;color:#8b96a8;border:1px solid #2c3549;border-radius:5px;padding:2px 7px}}
 .bg i{{font-style:normal;color:#e3b341;margin-left:5px}}
 .grp{{font-size:11px;border-radius:5px;padding:2px 8px;font-weight:bold}}
 .gA{{background:#1d3546;color:#5ec8f0}} .gB{{background:#1d2a46;color:#5e8cf0}}
 .gC{{background:#1d3a2c;color:#6fd39b}} .gAB{{background:#243046;color:#9ec0f0}}
 .gBC{{background:#20362f;color:#8fd0b0}} .gALL{{background:#3a2f1d;color:#f0c85e}}
 .g-{{background:#22262e;color:#8b96a8}}
 .tag{{font-size:11px;color:#6b7686;margin-left:auto}}
 .gl{{color:#f0c85e;font-size:15px;margin:2px 0 6px}}
 .ko{{line-height:1.75;margin-bottom:3px}}
 .en{{line-height:1.7;color:#93a0b4;font-size:13px;margin-bottom:9px}}
 .mo{{border-top:1px dashed #222b39;padding-top:8px}}
 .tk{{display:flex;gap:8px;margin:4px 0;align-items:baseline;line-height:1.65}}
 .nm{{flex:0 0 74px;font-size:12px;border-left:3px solid;padding-left:7px;font-weight:bold}}
 .gp{{flex:0 0 14px;font-size:10px;color:#5b6575}}
 .bd{{flex:1}}
 code{{background:#1a2130;padding:1px 5px;border-radius:4px;font-size:12px;color:#9fd0ff}}
 .note{{margin:6px 0 0 82px;font-size:12px;color:#8b96a8;line-height:1.6}}
 .star{{color:#ff7b72;font-weight:bold}}
 b{{color:#fff}}
</style>
<div class="wrap">
 <h1>W24 검수 — 전체 시나리오 + 캐릭터별 동작 트랙</h1>
 <div class="sub">
  씬 {len(sc)}개 · 배경 동영상 {n_video} / 정지 {len(sc)-n_video} ·
  <b>A</b> 졸라맨·졸라걸·스틱맨 / <b>B</b> 인준·지은 / <b>C</b> 마담제이·티쳐제이 ·
  피날레 50초는 S34 뒤에 붙이며 <b>이번 렌더에서는 제외</b><br>
  원본: <code>W24/W24_scenario.md</code> · <code>W24_motion.md</code>
  (문서를 고치고 <code>python make_w24_review_page.py</code> 를 다시 돌리면 이 화면이 따라옵니다)
 </div>
 <div class="bar">
  <button class="on" data-f="all">전체</button>
  <button data-f="A">A 글자·수</button>
  <button data-f="B">B 거리의 말</button>
  <button data-f="C">C 마음의 말</button>
  <button data-f="전원">전원(수료식)</button>
 </div>
 {''.join(rows)}
</div>
<script>
 const bs=[...document.querySelectorAll('.bar button')], ss=[...document.querySelectorAll('.scene')];
 bs.forEach(b=>b.onclick=()=>{{
   bs.forEach(x=>x.classList.remove('on')); b.classList.add('on');
   const f=b.dataset.f;
   ss.forEach(s=>{{ const g=s.dataset.g;
     s.style.display=(f==='all'||g===f||(f!=='전원'&&g.includes(f)))?'':'none'; }});
 }});
</script>
"""
    open(OUT, "w", encoding="utf-8").write(body)
    miss = [n for n in sorted(sc) if not mo.get(n, {}).get("tracks")]
    print(f"씬 {len(sc)} · 동작 트랙 있는 씬 {len(sc)-len(miss)}")
    if miss:
        print(f"★동작 트랙 없는 씬: {miss}")
    print(f"✅ {OUT}")


if __name__ == "__main__":
    main()
