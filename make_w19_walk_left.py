# -*- coding: utf-8 -*-
"""W19 지은 왼쪽(리버스) 걷기 8컷 = 오른쪽 정규화 컷 좌우반전(flip).
   flip은 캔버스 중심 대칭이라 키(770px)·발끝(y1210)·중심 그대로 유지.
   → jieun_w19_walk_l_0..7.png + DB 왼걷기 등록 + 왼쪽 걷기 데모.
사용: python make_w19_walk_left.py
"""
import os, glob, subprocess, sqlite3
from PIL import Image

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
POSE = "assets/graphics/poses"
DEMO = "scratch/w19_walk/demo"
BG = "home_vocab/w19/bg/w19_bg_entrance.png"
CANVAS_W, CANVAS_H, FEET_Y = 1024, 1280, 1210

# ── 1) 좌우반전으로 왼쪽 8컷 ──
print("1) 리버스(왼쪽) 8컷 생성 (오른쪽 컷 좌우반전):")
lefts = []
for i in range(8):
    rp = f"{POSE}/jieun_w19_walk_r_{i}.png"
    lp = f"{POSE}/jieun_w19_walk_l_{i}.png"
    Image.open(rp).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT).save(lp)
    lefts.append(lp)
    print(f"   l_{i} <- r_{i} (flip)")

# ── 2) DB 등록 (왼걷기) ──
con = sqlite3.connect("channel/content.db"); cur = con.cursor()
cur.execute("DELETE FROM asset_catalog WHERE project='W19' AND category='캐릭터걷기컷' AND name LIKE '%왼쪽 걷기%'")
tot = sum(os.path.getsize(p) for p in lefts)
cur.execute("""INSERT INTO asset_catalog (project,category,name,location,kind,storage,count,bytes,db_table,note,updated_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
    ('W19', '캐릭터걷기컷', '지은 왼쪽 걷기 투명컷 8(오른쪽컷 리버스)',
     f"{POSE}/jieun_w19_walk_l_0..7.png", 'png', 'local', 8, tot, None,
     '오른쪽 걷기 8컷 좌우반전(돌아오기/왼쪽 이동). 키770px·발끝y1210·발사이 투명 그대로. 순환+좌측이동=왼걷기.'))
con.commit(); con.close()
print("2) DB 등록 완료 (asset_catalog W19/캐릭터걷기컷 · 왼걷기)")

# ── 3) 왼쪽 걷기 데모 (오른쪽→왼쪽 이동) ──
print("3) 왼쪽 걷기 데모 렌더:")
BW, BH = 1280, 720
bg = Image.open(BG).convert("RGB")
r = max(BW / bg.width, BH / bg.height)
bg = bg.resize((int(bg.width * r), int(bg.height * r)), Image.LANCZOS)
bg = bg.crop(((bg.width - BW) // 2, (bg.height - BH) // 2,
              (bg.width - BW) // 2 + BW, (bg.height - BH) // 2 + BH))

SCALE = 0.60
sw, sh = int(CANVAS_W * SCALE), int(CANVAS_H * SCALE)
SCENE_FEET_Y = 662
paste_y = int(SCENE_FEET_Y - FEET_Y * SCALE)
ref = Image.open(f"{POSE}/jieun_w19_smile_bright.png").convert("RGBA").resize((sw, sh), Image.LANCZOS)
cuts = [Image.open(p).convert("RGBA").resize((sw, sh), Image.LANCZOS) for p in lefts]

ref_cx = 1030                     # 왼걷기: 기준은 오른쪽 고정
walk_x0, walk_x1 = 810, 100       # 오른쪽에서 시작 → 왼쪽으로
FPS, HOLD, CYCLES = 12, 3, 3
nframes = len(cuts) * HOLD * CYCLES
tmp = f"{DEMO}/_seql"; os.makedirs(tmp, exist_ok=True)
for f in glob.glob(f"{tmp}/*.png"): os.remove(f)
for k in range(nframes):
    fr = bg.copy()
    fr.paste(ref, (ref_cx - sw // 2, paste_y), ref)
    wx = int(walk_x0 + (walk_x1 - walk_x0) * (k / max(1, nframes - 1)))
    fr.paste(cuts[(k // HOLD) % len(cuts)], (wx - sw // 2, paste_y), cuts[(k // HOLD) % len(cuts)])
    fr.save(f"{tmp}/f{k:04d}.png")
demo_l = f"{DEMO}/walk_demo_left.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", demo_l],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"   {demo_l} ({nframes/FPS:.1f}초)")

# ── 4) index.html 갱신(오른쪽+왼쪽+키시트) ──
html = """<!doctype html><meta charset=utf-8><title>W19 지은 걷기 확인</title>
<style>body{background:#161616;color:#eee;font-family:'Malgun Gothic',system-ui;margin:0;padding:18px}
h2{font-size:16px;margin:14px 0 6px} img,video{max-width:100%;border-radius:8px;background:#000}
.row{display:flex;gap:14px;flex-wrap:wrap}</style>
<h2>① 오른쪽 걷기 (기준 왼쪽 고정)</h2>
<video src="walk_demo.mp4" autoplay loop muted controls width="820"></video>
<h2>② 왼쪽 걷기 = 리버스 (기준 오른쪽 고정)</h2>
<video src="walk_demo_left.mp4" autoplay loop muted controls width="820"></video>
<h2>③ 같은 키 확인 시트 — 초록=머리선, 빨강=발끝선</h2>
<img src="height_check.png">"""
open(f"{DEMO}/index.html", "w", encoding="utf-8").write(html)
print(f"완료 → {DEMO}/index.html (오른쪽+왼쪽 데모)")
