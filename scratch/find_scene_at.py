# -*- coding: utf-8 -*-
"""compile_main_hybrid 의 타임라인 로직을 그대로 재현해 특정 시각의 씬을 찾는다."""
import os, re, sys
from moviepy import AudioFileClip

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SF = os.path.join(ROOT, "sejong_film")
MAIN = os.path.join(SF, "main")
AUD = os.path.join(MAIN, "audio_free")
LANG = "ko"
XF = 0.6
DISSOLVE = ("디졸브", "모프", "페이드", "입자와이프", "슬라이드")

shots = []
cur = None
for line in open(os.path.join(SF, "sejong_master_shotscript_48.md"), encoding="utf-8"):
    mh = re.match(r"^\*\*S(\d+)\s*·\s*([🎬✏️].*?)\s*·.*?(?:→(\S+))?\*\*", line)
    if mh:
        n = int(mh.group(1)); mode = "real" if "🎬" in mh.group(2) else "anim"
        trans = (mh.group(3) or "컷")
        cur = {"n": n, "mode": mode, "trans": trans, "ko": "", "en": ""}; shots.append(cur); continue
    mk = re.match(r"^-\s*KO:\s*(.*)$", line); me = re.match(r"^-\s*EN:\s*(.*)$", line)
    if mk and cur: cur["ko"] = mk.group(1).strip()
    if me and cur: cur["en"] = me.group(1).strip()

def is_music(t): return ("음악" in t and "없음" in t) or t.lower().startswith("(music")
def aud(n):
    p = os.path.join(AUD, f"{LANG}_S{n:02d}.mp3")
    return AudioFileClip(p) if os.path.exists(p) else None

rows = []
t = 0.0; prev_trans = "컷"
for s in shots:
    n = s["n"]; a = aud(n); music = is_music(s["ko"])
    dur = (a.duration + 0.55) if (a and not music) else (2.6 if music else 3.4)
    inxf = XF if prev_trans in DISSOLVE else 0.0
    start = max(0.0, t - inxf)
    end = start + dur
    rows.append((n, s["mode"], s["trans"], start, end))
    t = end; prev_trans = s["trans"]
    if a: a.close()

targets = [float(x) for x in sys.argv[1:]] or [25.0, 340.0]
for tt in targets:
    hit = [r for r in rows if r[3] <= tt < r[4]]
    print(f"\n=== t={tt:.0f}s ({int(tt//60)}:{int(tt%60):02d}) ===")
    for r in hit:
        print(f"  S{r[0]:02d} {r[1]} trans={r[2]}  [{r[3]:.1f}s ~ {r[4]:.1f}s]")
    # 주변 씬도 표시
    for r in rows:
        if abs(r[3]-tt) < 12 or (r[3] <= tt < r[4]):
            print(f"     · S{r[0]:02d} {r[1]:4s} {r[3]:6.1f}~{r[4]:6.1f}")
print(f"\n총 길이 {rows[-1][4]:.1f}s")
