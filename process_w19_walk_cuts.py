# -*- coding: utf-8 -*-
"""W19 지은 걷기영상(W19_package) → 8투명컷 추출 → 비율유지 리사이즈로 키 통일
   (크롭 아님, 같은 배율로 축소/확대) → 다른 W19 포즈와 동일 규격.
   규격: cutout_jieun_w19.py 와 동일 — 캔버스 1024x1280, 발끝 y=1210, 머리~발끝 770px.
   레퍼런스 측면 사진도 같은 규격으로 정규화해 나란히 비교시트 생성.
사용: python process_w19_walk_cuts.py
"""
import os, glob, subprocess
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
VID = "W19_package/Woman_walks_right_side_profile_202607221409.mp4"
POSE = "assets/graphics/poses"
TMP = "scratch/w19_walk/newproc"
os.makedirs(TMP, exist_ok=True)
for fn in glob.glob(f"{TMP}/*.png"):
    os.remove(fn)

# ── cutout_jieun_w19.py 와 동일 규격 ──
CANVAS_W, CANVAS_H = 1024, 1280
FEET_Y = 1210
TARGET_BODY = 770          # 머리끝~발끝 몸높이 통일값 (다른 포즈와 동일)


def grab(t):
    p = f"{TMP}/_g.png"
    subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", VID, "-frames:v", "1", p],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return np.array(Image.open(p).convert("RGBA"))


def cutout_largest(arr):
    """흰배경 테두리연결 플러드 투명(옷/신발 내부 흰색 보존) + 최대덩어리만(Veo 워터마크 제거)."""
    arr = arr.copy()
    rgb = arr[:, :, :3].astype(int)
    lo = rgb.min(axis=2); hi = rgb.max(axis=2)
    white = (lo > 200) & ((hi - lo) < 30)
    lbl, _ = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    arr[np.isin(lbl, list(border)), 3] = 0
    # 최대 연결덩어리(캐릭터)만 남기고 나머지(워터마크 등) 제거
    a = arr[:, :, 3] > 0
    l2, n = ndimage.label(a)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(l2), l2, range(1, n + 1))
        keep = int(np.argmax(sizes)) + 1
        arr[l2 != keep, 3] = 0
    ys, xs = np.where(arr[:, :, 3] > 0)
    if len(ys) == 0:
        return None, None
    box = (xs.min(), ys.min(), xs.max(), ys.max())
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1], box


def body_metrics(crop):
    """머리끝~발끝 몸높이(든 팔 제외) + 몸통중심 x — cutout_jieun_w19 와 동일 로직."""
    alpha = crop[:, :, 3] > 0
    w = alpha.sum(axis=1).astype(float)
    H = len(w)
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
    """비율유지 리사이즈(크롭X) → 몸높이 770px 통일, 발끝 y1210 정렬, 몸통중심 가로 정중앙."""
    span, cx = body_metrics(crop)
    h, w = crop.shape[:2]
    scale = TARGET_BODY / span
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)   # 같은 배율 = 비율 유지
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    x = CANVAS_W // 2 - round(cx * scale)
    y = FEET_Y - nh
    canvas.paste(im, (x, y), im)
    return canvas, span


# ── 1) 걷기 위상(phase) 측정으로 한 사이클 구간·주기 자동 검출 ──
print("걷기 사이클 측정 중...")
ts = np.arange(0.4, 6.0, 0.15)
samples = []   # (t, feet_offset, box, span)
for t in ts:
    crop, box = cutout_largest(grab(t))
    if crop is None:
        continue
    ch, cw = crop.shape[:2]
    # 발영역(하단 12%) 중심 x - 몸통중심 x = 스트라이드 위상(부호 있음)
    feet = crop[int(ch * 0.88):, :, 3] > 0
    fx = np.where(feet.any(axis=0))[0]
    _, cx = body_metrics(crop)
    off = (fx.mean() - cx) if len(fx) else 0.0
    fully_in = box[0] > 12 and box[2] < 1268   # 화면 안에 완전히 들어온 프레임만
    samples.append((t, off, fully_in, crop))

# 완전히 들어온 구간
in_idx = [i for i, s in enumerate(samples) if s[2]]
i0, i1 = in_idx[0], in_idx[-1]
sig = np.array([samples[i][1] for i in range(i0, i1 + 1)], float)
sig -= sig.mean()
ac = np.correlate(sig, sig, "full")[len(sig) - 1:]
# 최소 lag(0.6s=4샘플) 이후 첫 지역최대 = 한 스트라이드 주기
P = 8
for lag in range(4, len(ac) - 1):
    if ac[lag] > ac[lag - 1] and ac[lag] >= ac[lag + 1] and ac[lag] > 0:
        P = lag; break
period_s = P * 0.15
t_start = samples[i0][0]
# 시작+주기가 화면 안에 남도록 조정
if t_start + period_s > samples[i1][0]:
    t_start = max(samples[i0][0], samples[i1][0] - period_s)
print(f"  화면내 구간 {samples[i0][0]:.2f}~{samples[i1][0]:.2f}s / 검출 주기 {period_s:.2f}s / 시작 {t_start:.2f}s")

# ── 2) 한 사이클을 8등분해 8컷 추출·정규화·저장 ──
print("8컷 추출·정규화(비율유지):")
cut_paths = []
spans = []
for i in range(8):
    t = t_start + period_s * i / 8
    crop, _ = cutout_largest(grab(t))
    canvas, span = normalize(crop)
    op = f"{POSE}/jieun_w19_walk_r_{i}.png"
    canvas.save(op)
    cut_paths.append(op); spans.append(span)
    print(f"  r_{i}  t={t:.2f}s  원본몸높이 {span}px → 770px 통일")

# 레퍼런스 측면 사진도 동일 규격으로 정규화
ref_src = next((p for p in glob.glob("W19_package/*.png") if "옆" in p), None)
ref_norm = None
if ref_src:
    rcrop, _ = cutout_largest(np.array(Image.open(ref_src).convert("RGBA")))
    ref_norm, rspan = normalize(rcrop)
    ref_norm.save(f"{TMP}/ref_side_norm.png")
    print(f"  레퍼런스({os.path.basename(ref_src)})  원본몸높이 {rspan}px → 770px 통일")

# ── 3) 비교시트: 레퍼런스 + 8컷, 같은 발끝선/머리선 가이드로 키 일치 확인 ──
tiles = ([("REF", ref_norm)] if ref_norm else []) + [(f"r_{i}", Image.open(p)) for i, p in enumerate(cut_paths)]
TW = 210
scale_v = TW / CANVAS_W
TH = int(CANVAS_H * scale_v)
pad = 8
sheet = Image.new("RGB", (TW * len(tiles) + pad * (len(tiles) + 1), TH + 44), (30, 30, 30))
# 체크무늬(투명 확인용)
chk = Image.new("RGB", (TW, TH))
px = chk.load()
for yy in range(TH):
    for xx in range(TW):
        px[xx, yy] = (120, 120, 120) if ((xx // 12 + yy // 12) % 2 == 0) else (95, 95, 95)
d = ImageDraw.Draw(sheet)
head_y = int((FEET_Y - TARGET_BODY) * scale_v) + 30
feet_y = int(FEET_Y * scale_v) + 30
for i, (name, im) in enumerate(tiles):
    x = pad + i * (TW + pad)
    base = chk.copy()
    base.paste(im.resize((TW, TH)), (0, 0), im.resize((TW, TH)))
    sheet.paste(base, (x, 30))
    d.text((x + 4, 6), name, fill=(255, 230, 120))
# 같은 머리선(초록)·발끝선(빨강) — 전 컷 키 동일 증명
d.line([(0, head_y), (sheet.width, head_y)], fill=(0, 230, 0), width=1)
d.line([(0, feet_y), (sheet.width, feet_y)], fill=(255, 60, 60), width=1)
d.text((4, head_y - 12), "head", fill=(0, 230, 0))
d.text((4, feet_y + 2), "feet(same height)", fill=(255, 60, 60))
sheet_path = f"{TMP}/compare_sheet.png"
sheet.save(sheet_path)
print(f"\n비교시트 저장: {sheet_path}")
print(f"저장된 컷: {POSE}/jieun_w19_walk_r_0..7.png (8개)")
