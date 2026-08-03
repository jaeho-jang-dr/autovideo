# -*- coding: utf-8 -*-
"""W24 그룹 64컷 → 스틸 동영상 + 뷰어 (2026-08-03).

64컷을 **8fps** 로 이어 붙이면 원본 8초와 길이가 같다(192프레임 ÷ 3 = 64컷, 24fps ÷ 3 = 8fps).
투명이 제대로 뚫렸는지 보이도록 **체커보드 위**에 얹어 렌더한다.

사용: python make_w24_cut_preview.py
  → W24/cut_preview/<키>.mp4 11개 + W24/cuts.html
"""
import glob
import os
import subprocess

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

CUTS = "W24/group_cuts"
OUT = "W24/cut_preview"
PAGE = "W24/cuts.html"
W, H = 1280, 720
FPS = 8          # 64컷 ÷ 8fps = 8초 (원본과 동일)

META = {
    "a_write_jamo":  ("A", "졸라맨·졸라걸·스틱맨", "S5 S6", "허공에 자모 획을 긋는다"),
    "a_stack_block": ("A", "졸라맨·졸라걸·스틱맨", "S7", "블록이 손에서 손으로 넘어가며 쌓인다"),
    "a_count_up":    ("A", "졸라맨·졸라걸·스틱맨", "S9", "하나·둘·셋이 왼→오른쪽으로 넘어간다"),
    "b_ask_price":   ("B", "인준·지은", "S13", "묻는 손과 답하는 손이 가운데서 마주 놓인다"),
    "b_hold_strap":  ("B", "인준·지은", "S15", "둘이 같은 리듬으로 흔들린다"),
    "b_point_way":   ("B", "인준·지은", "S16", "지은의 손끝을 인준의 시선이 따라간다"),
    "b_highfive":    ("B", "인준·지은", "S18", "손바닥이 같은 높이에서 마주친다"),
    "c_talk_sit":    ("C", "마담제이·티쳐제이", "S20 S21 S27", "마주 앉아 손가락으로 꼽고 날짜를 짚는다"),
    "c_weather_look":("C", "마담제이·티쳐제이", "S22", "둘의 시선이 화면 위 같은 점에서 만난다"),
    "c_emotion_face":("C", "마담제이·티쳐제이", "S23", "웃음이 상대에게 옮는다"),
    "c_nod_agree":   ("C", "마담제이·티쳐제이", "S25", "끄덕임이 서로를 향해 반사된다"),
    # ★씬 전환용 점프 — 같은 캐릭터가 이어질 때
    "a_jump":        ("A", "졸라맨·졸라걸·스틱맨", "전환", "셋이 동시에 점프 → 착지 → 정면"),
    "b_jump":        ("B", "인준·지은", "전환", "둘이 동시에 점프 → 착지 → 정면"),
    "c_jump":        ("C", "마담제이·티쳐제이", "전환", "의자에서 일어나 한 번 폴짝"),
    # ★교실(전시실) 앉기 3박자 + 수료식 꽃다발
    "a_sit_class":   ("A", "졸라맨·졸라걸·스틱맨", "S30~S32", "듣기 → 박수 → 정면"),
    "b_sit_class":   ("B", "인준·지은", "S30~S32", "듣기 → 박수 → 정면"),
    "c_sit_class":   ("C", "마담제이·티쳐제이", "S30~S32", "듣기 → 박수 → 정면"),
    "flower_give":   ("C", "티쳐제이·인준", "S32", "★꽃다발이 네 손 사이에서 건네진다"),
}
COLOR = {"A": "#5ec8f0", "B": "#5e8cf0", "C": "#6fd39b"}


def checker(w, h, sq=24):
    im = Image.new("RGB", (w, h), (208, 208, 208))
    px = im.load()
    for y in range(0, h, sq):
        for x in range(0, w, sq):
            if (x // sq + y // sq) % 2:
                for yy in range(y, min(y + sq, h)):
                    for xx in range(x, min(x + sq, w)):
                        px[xx, yy] = (170, 170, 170)
    return im


def build(key, bg):
    src = sorted(glob.glob(f"{CUTS}/{key}/*.png"))
    if not src:
        print(f"  ★컷 없음: {key}")
        return False
    tmp = f"{OUT}/_t"
    os.makedirs(tmp, exist_ok=True)
    for old in glob.glob(f"{tmp}/*.png"):
        os.remove(old)
    for i, p in enumerate(src):
        im = Image.open(p).convert("RGBA")
        s = min((W - 80) / im.width, (H - 60) / im.height, 1.0)
        if s < 1.0:
            im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        c = bg.copy()
        c.paste(im, ((W - im.width) // 2, H - im.height - 20), im)
        c.save(f"{tmp}/{i:03d}.png")
    out = f"{OUT}/{key}.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/%03d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-vf", "fps=24", out], capture_output=True)
    for old in glob.glob(f"{tmp}/*.png"):
        os.remove(old)
    os.rmdir(tmp)
    return os.path.exists(out)


def page(keys):
    cards = []
    for k in keys:
        g, who, sc, what = META[k]
        n = len(glob.glob(f"{CUTS}/{k}/*.png"))
        sz = Image.open(f"{CUTS}/{k}/00.png").size
        cards.append(f"""
<div class="card" data-g="{g}">
  <div class="hd"><span class="g" style="background:{COLOR[g]}22;color:{COLOR[g]}">{g}</span>
    <b>{k}</b><span class="who">{who}</span><span class="sc">{sc}</span></div>
  <video src="/cut_preview/{k}.mp4" loop muted playsinline controls></video>
  <div class="ft">{what}<span class="n">{n}컷 · {sz[0]}×{sz[1]}</span></div>
</div>""")
    html = f"""<!doctype html>
<meta charset="utf-8"><title>W24 그룹 동작 64컷</title>
<style>
 body{{margin:0;background:#0b0d12;color:#e8ecf4;font-family:"Malgun Gothic",sans-serif}}
 .wrap{{max-width:1500px;margin:0 auto;padding:20px}}
 h1{{font-size:19px;margin:0 0 4px}}
 .sub{{font-size:13px;color:#8b96a8;margin-bottom:14px;line-height:1.7}}
 .bar{{display:flex;gap:7px;margin-bottom:14px;flex-wrap:wrap}}
 button{{background:#1b2130;color:#dfe6f2;border:1px solid #2c3549;border-radius:7px;
        padding:7px 13px;font-size:13px;cursor:pointer}}
 button.on{{background:#2f6df6;border-color:#2f6df6;color:#fff}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(460px,1fr));gap:14px}}
 .card{{border:1px solid #1e2532;border-radius:10px;background:#10141c;padding:10px}}
 .hd{{display:flex;gap:8px;align-items:center;font-size:13px;margin-bottom:7px;flex-wrap:wrap}}
 .g{{border-radius:5px;padding:2px 8px;font-weight:bold;font-size:11px}}
 .who{{color:#8b96a8;font-size:12px}} .sc{{color:#63d2a4;font-size:12px;margin-left:auto}}
 video{{width:100%;border-radius:8px;background:#000;display:block}}
 .ft{{font-size:12px;color:#93a0b4;margin-top:7px;display:flex;gap:8px;line-height:1.6}}
 .n{{margin-left:auto;color:#6b7686;white-space:nowrap}}
</style>
<div class="wrap">
 <h1>W24 그룹 동작 — 64컷 투명컷 스틸 동영상</h1>
 <div class="sub">
  8초 영상 → 24fps 192프레임 → <b>3장 중 1장 = 64컷</b> → 8fps 재생(원본과 같은 8초)<br>
  <b>체커보드가 비치는 곳이 투명입니다</b> — 의자 살 사이·팔과 몸 사이·의자와 몸 사이가 뚫렸는지 보세요.
  키는 규격표대로 통일(인준770·졸라맨761·티쳐제이749·스틱맨749·지은706·졸라걸697·마담제이693).
 </div>
 <div class="bar">
  <button class="on" data-f="all">전체 11</button>
  <button data-f="A">A 3인</button><button data-f="B">B 2인</button><button data-f="C">C 2인</button>
  <button onclick="document.querySelectorAll('video').forEach(v=>v.play())">전부 재생</button>
  <button onclick="document.querySelectorAll('video').forEach(v=>{{v.pause();v.currentTime=0}})">전부 정지</button>
 </div>
 <div class="grid">{''.join(cards)}</div>
</div>
<script>
 const bs=[...document.querySelectorAll('.bar button[data-f]')], cs=[...document.querySelectorAll('.card')];
 bs.forEach(b=>b.onclick=()=>{{bs.forEach(x=>x.classList.remove('on'));b.classList.add('on');
   cs.forEach(c=>c.style.display=(b.dataset.f==='all'||c.dataset.g===b.dataset.f)?'':'none');}});
 document.querySelectorAll('video').forEach(v=>v.play().catch(()=>{{}}));
</script>"""
    open(PAGE, "w", encoding="utf-8").write(html)


def main():
    os.makedirs(OUT, exist_ok=True)
    bg = checker(W, H)
    keys = [k for k in META if os.path.isdir(f"{CUTS}/{k}")]
    ok = []
    for k in keys:
        if build(k, bg):
            ok.append(k)
            print(f"  ✅ {k}")
    page(ok)
    print(f"\n스틸 동영상 {len(ok)}/{len(keys)} → {OUT}/")
    print(f"✅ {PAGE}")


if __name__ == "__main__":
    main()
