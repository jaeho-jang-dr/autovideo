# -*- coding: utf-8 -*-
"""W19 지은 걷기 최종화:
  1) 사용자가 고른 한 스트라이드(프레임 2~33) 8등분 = 프레임 2,6,10,14,18,22,26,30
     → 컷아웃 + 비율유지 리사이즈로 키 통일(770px) → jieun_w19_walk_r_0..7.png
  2) asset_catalog(DB) 등록
  3) 배경에 기준 이미지 하나 + 그 옆에서 걷기 데모(mp4) + 같은키 확인 시트
사용: python build_w19_walk_final.py
"""
import os, glob, subprocess, sqlite3
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
SEQ = "scratch/w19_walk/seq5"          # 0000..0119 원본 프레임 (t=0.4s부터 24fps)
POSE = "assets/graphics/poses"
DEMO = "scratch/w19_walk/demo"
os.makedirs(DEMO, exist_ok=True)
PICK = [2, 6, 10, 14, 18, 22, 26, 30]  # ★사용자 선택: 스트라이드 2~33 균등 8등분
REF_STAND = f"{POSE}/jieun_w19_smile_bright.png"   # 기준(서 있는 포즈, 같은 770px 규격)
BG = "home_vocab/w19/bg/w19_bg_entrance.png"

# 동일 규격 (cutout_jieun_w19.py)
CANVAS_W, CANVAS_H, FEET_Y, TARGET_BODY = 1024, 1280, 1210, 770


def cutout_largest(arr):
    """배경색(밝고 무채색=흰배경+바닥 그림자+발 사이 흰영역)이 아닌 것 = 캐릭터.
    → 그림자·발사이 흰색 완전 제거. 얼굴 하이라이트 같은 작은 내부구멍만 메우고
      발 사이 큰 열린영역은 투명 유지. Veo 워터마크는 최대덩어리 남기기로 제거."""
    arr = arr.copy()
    rgb = arr[:, :, :3].astype(int)
    lo = rgb.min(axis=2); hi = rgb.max(axis=2)
    bg = (lo > 168) & ((hi - lo) < 45)              # 밝고 채도낮음 = 배경/그림자/발사이
    fg = ~bg
    lbl, n = ndimage.label(fg)
    if n == 0:
        return None
    sizes = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    char = lbl == (int(np.argmax(sizes)) + 1)       # 최대덩어리 = 캐릭터(워터마크 제외)
    # 작은 내부구멍만 메움(얼굴/머리 하이라이트). 발 사이 큰 구멍은 투명 유지.
    filled = ndimage.binary_fill_holes(char)
    holes = filled & ~char
    hl, hn = ndimage.label(holes)
    if hn:
        hsz = ndimage.sum(np.ones_like(hl), hl, range(1, hn + 1))
        small = {i + 1 for i, a in enumerate(hsz) if a < 1500}
        if small:
            char |= np.isin(hl, list(small))
    arr[~char, 3] = 0
    arr[char, 3] = 255
    ys, xs = np.where(char)
    if len(ys) == 0:
        return None
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def body_metrics(crop):
    alpha = crop[:, :, 3] > 0
    w = alpha.sum(axis=1).astype(float); H = len(w)
    torso = np.median(w[int(H * 0.42):int(H * 0.72)]) or w.max()
    thr = max(0.5 * torso, 0.12 * w.max())
    head_top = 0
    for y in range(H):
        if w[y] >= thr and np.mean(w[y:y + 22] >= thr * 0.6) > 0.6:
            head_top = y; break
    span = (H - 1) - head_top
    band = alpha[int(H * 0.42):int(H * 0.72)]
    bx = np.where(band.any(axis=0))[0]
    cx = int(bx.mean()) if len(bx) else crop.shape[1] // 2
    return span, cx


def normalize(crop):
    span, cx = body_metrics(crop)
    h, w = crop.shape[:2]
    s = TARGET_BODY / span
    nw, nh = max(1, round(w * s)), max(1, round(h * s))
    im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)   # 비율유지(크롭X)
    cv = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    cv.paste(im, (CANVAS_W // 2 - round(cx * s), FEET_Y - nh), im)
    return cv, span

# ── 1) 8컷 생성 ──
print("1) 선택 프레임 8컷 생성 (키 통일 770px):")
cut_paths = []
for i, fno in enumerate(PICK):
    src = f"{SEQ}/{fno:04d}.png"
    crop = cutout_largest(np.array(Image.open(src).convert("RGBA")))
    cv, span = normalize(crop)
    op = f"{POSE}/jieun_w19_walk_r_{i}.png"
    cv.save(op); cut_paths.append(op)
    print(f"   r_{i}  <- 프레임 {fno:>2d}  원본몸높이 {span}px → 770px")

# ── 2) DB 등록 ──
con = sqlite3.connect("channel/content.db"); cur = con.cursor()
cur.execute("DELETE FROM asset_catalog WHERE project='W19' AND category='캐릭터걷기컷' AND name LIKE '%오른쪽 걷기%'")
tot = sum(os.path.getsize(p) for p in cut_paths)
cur.execute("""INSERT INTO asset_catalog (project,category,name,location,kind,storage,count,bytes,db_table,note,updated_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
    ('W19', '캐릭터걷기컷', '지은 오른쪽 걷기 투명컷 8(스트라이드 2~33 8등분)',
     f"{POSE}/jieun_w19_walk_r_0..7.png", 'png', 'local', 8, tot, None,
     'Veo걷기영상→프레임 2,6,10,14,18,22,26,30 컷아웃·비율유지 리사이즈로 머리~발끝 770px 통일. 발끝 y1210, 1024x1280.'))
con.commit(); con.close()
print("2) DB 등록 완료 (asset_catalog W19/캐릭터걷기컷)")

# ── 3) 배경 + 기준 + 옆에서 걷기 데모 ──
print("3) 배경 걷기 데모 렌더:")
BW, BH = 1280, 720
bg = Image.open(BG).convert("RGB")
# cover-fit 1280x720
r = max(BW / bg.width, BH / bg.height)
bg = bg.resize((int(bg.width * r), int(bg.height * r)), Image.LANCZOS)
bg = bg.crop(((bg.width - BW) // 2, (bg.height - BH) // 2,
              (bg.width - BW) // 2 + BW, (bg.height - BH) // 2 + BH))

SCALE = 0.60                                   # 서기 몸높이 770*0.6≈462px
sw, sh = int(CANVAS_W * SCALE), int(CANVAS_H * SCALE)
scaled_feet = FEET_Y * SCALE                   # 캔버스 내 발끝의 스케일 후 y
SCENE_FEET_Y = 662                             # 화면 발끝선(기준·걷기 공통 → 같은 키 보장)
paste_y = int(SCENE_FEET_Y - scaled_feet)

ref = Image.open(REF_STAND).convert("RGBA").resize((sw, sh), Image.LANCZOS)
cuts = [Image.open(p).convert("RGBA").resize((sw, sh), Image.LANCZOS) for p in cut_paths]

ref_cx = 250                                   # 기준은 왼쪽 고정
walk_x0, walk_x1 = 470, 1180                   # 기준 옆에서 시작해 오른쪽으로
FPS, HOLD = 12, 3
CYCLES = 3
nframes = len(cuts) * HOLD * CYCLES
tmp = f"{DEMO}/_seq"; os.makedirs(tmp, exist_ok=True)
for f in glob.glob(f"{tmp}/*.png"): os.remove(f)
for k in range(nframes):
    fr = bg.copy()
    fr.paste(ref, (ref_cx - sw // 2, paste_y), ref)                       # 기준(고정)
    wx = int(walk_x0 + (walk_x1 - walk_x0) * (k / max(1, nframes - 1)))
    fr.paste(cuts[(k // HOLD) % len(cuts)], (wx - sw // 2, paste_y), cuts[(k // HOLD) % len(cuts)])
    fr.save(f"{tmp}/f{k:04d}.png")
demo_mp4 = f"{DEMO}/walk_demo.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", demo_mp4],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"   {demo_mp4} ({nframes/FPS:.1f}초)")

# ── 같은 키 확인 시트: 기준 + 8컷, 머리선/발끝선 ──
TW = 200; sv = TW / CANVAS_W; TH = int(CANVAS_H * sv)
tiles = [("기준", ref)] + [(f"r_{i}", c) for i, c in enumerate(cuts)]
sheet = Image.new("RGB", (TW * len(tiles) + 8, TH + 40), (28, 28, 28))
chk = Image.new("RGB", (TW, TH))
px = chk.load()
for yy in range(TH):
    for xx in range(TW):
        px[xx, yy] = (110, 110, 110) if ((xx // 12 + yy // 12) % 2 == 0) else (88, 88, 88)
d = ImageDraw.Draw(sheet)
try: fnt = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 20)
except Exception: fnt = ImageFont.load_default()
head_y = int((FEET_Y - TARGET_BODY) * sv) + 28
feet_y = int(FEET_Y * sv) + 28
for i, (name, im) in enumerate(tiles):
    x = i * TW + 4
    base = chk.copy()
    t = im.resize((TW, TH))
    base.paste(t, (0, 0), t)
    sheet.paste(base, (x, 28))
    d.text((x + 4, 4), name, fill=(255, 220, 90), font=fnt)
d.line([(0, head_y), (sheet.width, head_y)], fill=(0, 230, 0), width=1)
d.line([(0, feet_y), (sheet.width, feet_y)], fill=(255, 70, 70), width=1)
compare = f"{DEMO}/height_check.png"
sheet.save(compare)
print(f"   같은키 확인 시트: {compare}")

# ── 미리보기 HTML ──
html = f"""<!doctype html><meta charset=utf-8><title>W19 지은 걷기 확인</title>
<style>body{{background:#161616;color:#eee;font-family:'Malgun Gothic',system-ui;margin:0;padding:18px}}
h2{{font-size:16px;margin:14px 0 6px}} img,video{{max-width:100%;border-radius:8px;background:#000}}</style>
<h2>① 배경 걷기 데모 — 왼쪽 기준(고정) 옆에서 걷기 (같은 키 확인)</h2>
<video src="walk_demo.mp4" autoplay loop muted controls width="900"></video>
<h2>② 같은 키 확인 시트 — 초록=머리선, 빨강=발끝선 (기준 + 8컷 모두 정렬)</h2>
<img src="height_check.png">"""
open(f"{DEMO}/index.html", "w", encoding="utf-8").write(html)
print(f"완료 → {DEMO}/index.html")
