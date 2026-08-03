# -*- coding: utf-8 -*-
"""W24 전체 자산 뷰어 — 배경·전환·동작·포즈·피날레를 한 화면에 (2026-08-03).

디스크를 훑어서 만든다. 자산이 늘면 다시 돌리기만 하면 화면이 따라온다.

  배경 정지    assets/graphics/bg/bg_w24_*.png
  배경 동영상  assets/graphics/bg/bg_w24_*.mp4      (기본 / ★전환 to_* 구분)
  그룹 동작    W24/cut_preview/*.mp4  (64컷 스틸 동영상)
  개별 포즈    assets/graphics/poses/w24_*.png
  피날레       W24/_final/W24_finale_50s_MASTER.mp4

사용: python make_w24_asset_viewer.py   → W24/assets.html
      (W24 를 문서 루트로 서빙하므로 바깥 파일은 W24/_view/ 로 복사해 링크한다)
"""
import glob
import html
import os
import shutil
import subprocess

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

BG_DIR = "assets/graphics/bg"
POSE_DIR = "assets/graphics/poses"
CUTPREV = "W24/cut_preview"
VIEW = "W24/_view"
PAGE = "W24/assets.html"

TRANS = {"to_hall": "휩 팬 — 로비→전시장", "to_path": "유리 통과 — 전시장→둘레길",
         "to_ruins": "크레인 다운 — 둘레길→지하", "to_grass": "틸트 업 — 지하→잔디",
         "to_rose": "시간경과+푸시인 — 잔디→장미정원", "to_gallery": "매치 컷 — 장미정원→전시실"}
BGV = {"ddp_arrive": "도착 — 외부→로비", "board_time": "벽에서 자모가 떠오름",
       "gallery_wake": "★액자가 깨어난다", "gallery_out": "★액자가 비고 밖으로",
       "classroom_sejong": "★세종대왕이 웃는다", "plaza_gather": "광장에 원이 생긴다"}
ACT = {
    "a_write_jamo": ("A", "자모 획을 긋는다"), "a_stack_block": ("A", "블록이 손에서 손으로"),
    "a_count_up": ("A", "하나·둘·셋이 넘어간다"), "a_jump": ("A", "★전환 점프"),
    "a_sit_class": ("A", "앉기 3박자 — 듣기·박수·정면"),
    "b_ask_price": ("B", "묻는 손 ↔ 답하는 손"), "b_hold_strap": ("B", "같은 리듬으로 흔들림"),
    "b_point_way": ("B", "손끝을 시선이 따라간다"), "b_highfive": ("B", "손바닥이 마주친다"),
    "b_jump": ("B", "★전환 점프"), "b_sit_class": ("B", "앉기 3박자"),
    "c_talk_sit": ("C", "마주 앉아 날짜를 짚는다"), "c_weather_look": ("C", "시선이 하늘 한 점에서"),
    "c_emotion_face": ("C", "웃음이 옮는다"), "c_nod_agree": ("C", "끄덕임이 반사된다"),
    "c_jump": ("C", "★의자에서 일어나 폴짝"), "c_sit_class": ("C", "앉기 3박자"),
    "flower_give": ("C", "★꽃다발을 주고받는다"),
}
CHAR_KO = {"injun": "인준", "jieun": "지은", "madam_jay": "마담제이", "teacher_jay": "티쳐제이",
           "zolla_man": "졸라맨", "zolla_girl": "졸라걸", "stickman": "스틱맨"}
CHAR_COL = {"injun": "#5e8cf0", "jieun": "#f0d05e", "madam_jay": "#f07e9b",
            "teacher_jay": "#6fd39b", "zolla_man": "#5ec8f0", "zolla_girl": "#f0a85e",
            "stickman": "#b48cf0"}


def stage(src, sub):
    """W24 바깥 파일을 W24/_view/<sub>/ 로 복사해 서빙 가능하게 만든다."""
    d = f"{VIEW}/{sub}"
    os.makedirs(d, exist_ok=True)
    dst = f"{d}/{os.path.basename(src)}"
    if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
        shutil.copyfile(src, dst)
    return f"/_view/{sub}/{os.path.basename(src)}"


def poster(mp4, sub):
    """동영상 첫 프레임을 포스터로 뽑아 둔다(자동재생 실패해도 보이게)."""
    d = f"{VIEW}/{sub}"
    os.makedirs(d, exist_ok=True)
    out = f"{d}/{os.path.splitext(os.path.basename(mp4))[0]}.jpg"
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-y", "-ss", "0.1", "-i", mp4, "-frames:v", "1",
                        "-vf", "scale=480:-1", "-q:v", "4", out], capture_output=True)
    return f"/_view/{sub}/{os.path.basename(out)}"


def card_video(src, title, sub, tag=""):
    return f"""<div class="card">
  <div class="hd"><b>{html.escape(title)}</b><span class="tag">{html.escape(tag)}</span></div>
  <video src="{src}" loop muted playsinline controls preload="none"></video></div>"""


def main():
    os.makedirs(VIEW, exist_ok=True)
    sec = []

    # ── 배경 정지 ──
    stills = sorted(glob.glob(f"{BG_DIR}/bg_w24_*.png"))
    cards = []
    for p in stills:
        k = os.path.basename(p)[7:-4]
        sz = Image.open(p).size
        cards.append(f"""<div class="card"><div class="hd"><b>{k}</b>
          <span class="tag">{sz[0]}×{sz[1]}</span></div>
          <img src="{stage(p,'bg')}" loading="lazy"></div>""")
    sec.append(("배경 정지", f"{len(stills)}키", "".join(cards)))

    # ── 배경 동영상: 기본 / 전환 ──
    vids = sorted(glob.glob(f"{BG_DIR}/bg_w24_*.mp4"))
    base, trans = [], []
    for p in vids:
        k = os.path.basename(p)[7:-4]
        (trans if k in TRANS else base).append(
            card_video(stage(p, "bgv"), k, "bgv", TRANS.get(k, BGV.get(k, ""))))
    sec.append(("배경 동영상", f"{len(base)}키", "".join(base)))
    sec.append(("★장소 전환", f"{len(trans)}키 · 기법 전부 다름", "".join(trans)))

    # ── 그룹 동작 64컷 ──
    prevs = sorted(glob.glob(f"{CUTPREV}/*.mp4"))
    cards = []
    for p in prevs:
        k = os.path.splitext(os.path.basename(p))[0]
        g, what = ACT.get(k, ("-", ""))
        n = len(glob.glob(f"W24/group_cuts/{k}/*.png"))
        cards.append(f"""<div class="card"><div class="hd">
          <span class="g">{g}</span><b>{k}</b><span class="tag">{n}컷 · {what}</span></div>
          <video src="/cut_preview/{os.path.basename(p)}" loop muted playsinline controls
                 preload="none"></video></div>""")
    sec.append(("그룹 동작 — 64컷 스틸 동영상", f"{len(prevs)}종", "".join(cards)))

    # ── 개별 포즈 ──
    poses = sorted(glob.glob(f"{POSE_DIR}/w24_*.png"))
    bych = {}
    for p in poses:
        stem = os.path.basename(p)[4:-4]
        ch = next((c for c in CHAR_KO if stem.startswith(c)), None)
        if ch:
            bych.setdefault(ch, []).append((stem[len(ch) + 1:], p))
    blocks = []
    for ch in sorted(bych, key=lambda c: -len(bych[c])):
        items = "".join(
            f"""<div class="pose"><img src="{stage(p,'pose')}" loading="lazy">
                <span>{html.escape(nm)}</span></div>""" for nm, p in sorted(bych[ch]))
        blocks.append(f"""<div class="chblock">
          <div class="chhd" style="border-color:{CHAR_COL[ch]};color:{CHAR_COL[ch]}">
            {CHAR_KO[ch]} <i>{ch}</i> <b>{len(bych[ch])}종</b></div>
          <div class="poses">{items}</div></div>""")
    sec.append(("개별 정지 포즈", f"{len(poses)}장 · 그룹컷에서 추출", "".join(blocks)))

    # ── 피날레 ──
    fin = "W24/_final/W24_finale_50s_MASTER.mp4"
    if os.path.exists(fin):
        sec.append(("피날레", "50초 · 확정",
                    card_video("/_final/W24_finale_50s_MASTER.mp4", "플래시몹 피날레",
                               "fin", "폭죽 → 완전 정지 타블로")))

    body = "".join(
        f"""<section><h2>{html.escape(t)}<span class="cnt">{html.escape(c)}</span></h2>
        <div class="grid">{inner}</div></section>""" for t, c, inner in sec)

    open(PAGE, "w", encoding="utf-8").write(f"""<!doctype html>
<meta charset="utf-8"><title>W24 전체 자산</title>
<style>
 body{{margin:0;background:#0b0d12;color:#e8ecf4;font-family:"Malgun Gothic",sans-serif;font-size:14px}}
 .wrap{{max-width:1600px;margin:0 auto;padding:20px 20px 60px}}
 h1{{font-size:21px;margin:0 0 6px}}
 .sub{{font-size:13px;color:#8b96a8;margin-bottom:18px;line-height:1.7}}
 h2{{font-size:16px;margin:26px 0 10px;padding-bottom:6px;border-bottom:1px solid #1e2532;
    display:flex;align-items:baseline;gap:10px}}
 .cnt{{font-size:12px;color:#6b7686;font-weight:normal}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}}
 .card{{border:1px solid #1e2532;border-radius:9px;background:#10141c;padding:9px}}
 .hd{{display:flex;gap:7px;align-items:baseline;font-size:12px;margin-bottom:6px;flex-wrap:wrap}}
 .hd b{{color:#fff}} .tag{{color:#8b96a8;font-size:11px;margin-left:auto;text-align:right}}
 .g{{background:#1d3546;color:#5ec8f0;border-radius:4px;padding:1px 6px;font-size:10px;font-weight:bold}}
 video,.card img{{width:100%;border-radius:6px;background:#000;display:block}}
 .chblock{{grid-column:1/-1;border:1px solid #1e2532;border-radius:9px;background:#10141c;padding:11px}}
 .chhd{{font-size:14px;border-left:4px solid;padding-left:9px;margin-bottom:9px;font-weight:bold}}
 .chhd i{{font-style:normal;color:#6b7686;font-size:11px;margin-left:5px}}
 .chhd b{{color:#8b96a8;font-weight:normal;font-size:12px;margin-left:6px}}
 .poses{{display:flex;gap:9px;flex-wrap:wrap}}
 .pose{{width:118px;text-align:center;background:#1a2130;border-radius:7px;padding:6px 4px}}
 .pose img{{width:100%;height:130px;object-fit:contain}}
 .pose span{{display:block;font-size:10px;color:#9fd0ff;margin-top:3px;word-break:break-all}}
</style>
<div class="wrap">
 <h1>W24 전체 자산</h1>
 <div class="sub">
  배경 정지 · 배경 동영상 · <b>장소 전환</b> · 그룹 동작 64컷 · 개별 포즈 · 피날레<br>
  그룹 동작은 8초 영상 → 192프레임 → <b>3장 중 1장 = 64컷</b>, 체커보드가 비치는 곳이 투명입니다.
  개별 포즈는 <b>그룹컷에서 덩어리별로 추출</b>해 Flow 크레딧 없이 뽑았습니다.
 </div>
 {body}
</div>
<script>
 // 화면에 들어온 동영상만 재생 — 전부 동시에 틀면 버벅인다
 const io=new IntersectionObserver(es=>es.forEach(e=>{{
   const v=e.target; if(e.isIntersecting) v.play().catch(()=>{{}}); else v.pause();
 }}),{{threshold:0.25}});
 document.querySelectorAll('video').forEach(v=>io.observe(v));
</script>""")
    tot = len(stills) + len(vids) + len(prevs) + len(poses)
    print(f"배경정지 {len(stills)} · 배경동영상 {len(base)} · 전환 {len(trans)} · "
          f"그룹동작 {len(prevs)} · 개별포즈 {len(poses)}  (합 {tot})")
    print(f"✅ {PAGE}")


if __name__ == "__main__":
    main()
