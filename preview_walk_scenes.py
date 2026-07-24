# -*- coding: utf-8 -*-
"""W19 걷기 확인용 부분 프리뷰(EN판).
걷기 씬 S1·S4·S23 각각 '앞뒤 한 씬' 포함 → S1,S2 / S3,S4,S5 / S22,S23,S24 = 8씬 이어붙임.
저장된 타임라인(길이·오디오)을 그대로 써서 최종 렌더와 동일. compile_np render_lang 본뜸.
사용: python preview_walk_scenes.py
"""
import sys, os, re, json, subprocess
sys.path.insert(0, os.path.join(os.getcwd(), "hangeul_birth_vowels"))
import numpy as np
from PIL import ImageDraw
import compile_stickman as cs
from moviepy import VideoClip, concatenate_videoclips

EP, PREFIX, PDIR = "KO-W19", "hangeul_w19_jieun", "hangeul_birth_vowels"
cs.EP = EP; cs.OUT_PREFIX = PREFIX
try: cs.PROJECT_NAME = PREFIX
except Exception: pass
LEAD, TAIL, FF = 0.0, 0.45, "ffmpeg"
SEQS = [1, 2, 3, 4, 5, 22, 23, 24]        # 걷기 S1/S4/S23 + 앞뒤 한 씬
OUT_MP4 = os.path.join(PDIR, "w19_walk_preview_en.mp4")
OUT_SILENT = os.path.join(PDIR, "w19_walk_preview_en_silent.mp4")
OUT_SRT = os.path.join(PDIR, "w19_walk_preview.en.srt")


def log(m): print(m, flush=True)


def draw_note_box(fr, cap):                 # compile_np 복사(직접 import 금지 — import시 전체 렌더됨)
    if not cap: return
    d = ImageDraw.Draw(fr); f = cs.get_font(cs.FONT_BD, 30); x, y = 26, 56
    rows = cs.wrap(d, cap, f, int(cs.W * 0.44))
    if not rows: return
    boxw = max(d.textlength(t, font=f) for t in rows)
    asc, desc = f.getmetrics(); lh = asc + desc + 4; padx, pady = 12, 7
    d.rounded_rectangle([x - padx, y - pady, x + boxw + padx, y + lh * len(rows) + pady - 4],
                        radius=12, fill=(255, 255, 255, 235))
    yy = y
    for t in rows:
        d.text((x, yy), t, font=f, fill=(28, 28, 40)); yy += lh


def srt_ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


# 타임라인(최종 렌더 길이·오디오) + 씬(비주얼/박스)
tl = json.load(open(os.path.join(PDIR, f"{PREFIX}_np_timeline.json"), encoding="utf-8"))
tlmap = {s["seq"]: s for s in tl["scenes"]}
ko_scenes = cs.load_scenes("ko"); en_scenes = cs.load_scenes("en")
komap = {k["seq"]: k for k in ko_scenes}; enmap = {e["seq"]: e for e in en_scenes}
seqs = [q for q in SEQS if q in tlmap and q in komap]
log(f"프리뷰 씬: {seqs}  (걷기 S1/S4/S23 + 앞뒤)")

# ---------- 무음 비디오 ----------
clips = []
for q in seqs:
    sc = komap[q]; t = tlmap[q]; dur = t["dur"]
    sc["sound_sched"] = [(j, LEAD + t0, LEAD + t1) for (j, t0, t1) in t["ko_js"]]
    cap = enmap[q]["cap"]

    def mk(tt, scene=sc, cam=sc.get("cam"), sdur=dur, cp=cap):
        fr = cs.compose(scene, t=tt, lang="ko", overlay=False)
        fr = cs.apply_camera(fr, tt, sdur, cam).convert("RGBA")
        draw_note_box(fr, cp)
        cs.draw_logo(fr); cs.draw_place(fr, scene.get("place_en"))
        return np.asarray(fr.convert("RGB"))
    clips.append(VideoClip(frame_function=mk, duration=dur))
    log(f"  S{q:>2}: {dur:4.1f}s")

video = concatenate_videoclips(clips, method="compose")
video.write_videofile(OUT_SILENT, fps=cs.FPS, codec="libx264", audio=False, threads=4, preset="medium", logger="bar")

# ---------- EN 오디오 트랙(최종과 동일 en_a) ----------
segs = []
for i, q in enumerate(seqs):
    t = tlmap[q]; seg = os.path.join(cs.TTS_DIR, f"_wpre_en_{i}.wav")
    subprocess.run([FF, "-y", "-i", t["en_a"], "-af",
        f"adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{t['dur']:.3f}", "-ar", "24000", "-ac", "1", seg],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    segs.append(seg)
lst = os.path.join(cs.TTS_DIR, "_wpre_list.txt")
open(lst, "w", encoding="utf-8").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))
track = os.path.join(PDIR, "w19_walk_preview_en.m4a")
subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "aac", "-b:a", "160k", track],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# ---------- EN 자막(이어붙인 타임라인) ----------
entries = []; start = 0.0
for q in seqs:
    sc = enmap[q]; t = tlmap[q]; narr = t["en_dur"]
    chunks = sc.get("chunks") or [sc["script"]]
    lens = [max(1, len(c)) for c in chunks]; tot = sum(lens); acc = LEAD
    for c, l in zip(chunks, lens):
        w = narr * l / tot; entries.append((start + acc, start + acc + w, c)); acc += w
    start += t["dur"]
with open(OUT_SRT, "w", encoding="utf-8") as f:
    for i, (t0, t1, txt) in enumerate([e for e in entries if e[2].strip()], 1):
        f.write(f"{i}\n{srt_ts(t0)} --> {srt_ts(t1)}\n{txt.strip()}\n\n")

# ---------- mux ----------
subprocess.run([FF, "-y", "-i", OUT_SILENT, "-i", track,
    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT_MP4],
    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
log(f"### 프리뷰 완료 -> {OUT_MP4}  (자막 {OUT_SRT})")
log(f"총 길이 ~{sum(tlmap[q]['dur'] for q in seqs):.1f}s")
