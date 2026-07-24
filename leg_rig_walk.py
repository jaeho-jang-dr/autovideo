# -*- coding: utf-8 -*-
"""걷기1의 실제 다리 그림을 힙 기준으로 회전(스윙)시켜 진짜 걷기 프레임 생성.
 - 다리 = 힙에서 [앞(오른쪽) → 중간(수직) → 뒤(왼쪽)] 왕복, 두 다리는 반대 위상
 - 상체(머리·몸통·배낭·팔)는 원본 유지, 다리만 회전
프레임 시트 + 걷기 mp4 생성. 판단은 사용자.
사용: python leg_rig_walk.py
"""
import os, subprocess, math
import numpy as np
from PIL import Image
from scipy import ndimage
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
OUT = "scratch/w19_walk"

# 1) 걷기1 컷아웃
a = np.array(Image.open(f"{OUT}/step_1.png").convert("RGBA"))
rgb = a[:, :, :3].astype(int); lo = rgb.min(2); hi = rgb.max(2)
white = (lo > 210) & ((hi - lo) < 26)
lbl, _ = ndimage.label(white)
b = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1]); b.discard(0)
a[np.isin(lbl, list(b)), 3] = 0
ys, xs = np.where(a[:, :, 3] > 0)
a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
H, W = a.shape[:2]
alpha = a[:, :, 3]

# 2) 힙 y(다리 시작=허리) 와 힙 x
hip_y = int(H * 0.56)
row = alpha[hip_y - 3:hip_y + 3]
_, hx = np.where(row > 0)
hip_x = int(hx.mean())

# 3) 사타구니 아래에서 두 다리 분리(연결요소). 안되면 y를 내려가며 재시도
def split_legs(cut_y):
    region = np.zeros_like(alpha); region[cut_y:] = alpha[cut_y:] > 0
    lb, n = ndimage.label(region)
    comps = [(lb == i) for i in range(1, n + 1)]
    comps = [c for c in comps if c.sum() > (H * W) * 0.004]
    comps.sort(key=lambda c: np.where(c)[1].mean())   # x 평균순(왼→오른)
    return comps

legs = []
for cy in (int(H * 0.62), int(H * 0.66), int(H * 0.70)):
    legs = split_legs(cy)
    if len(legs) >= 2:
        cut_y = cy; break
if len(legs) < 2:
    raise SystemExit(f"다리 분리 실패({len(legs)}개)")
# 위쪽(사타구니~힙)은 두 다리 공통 → 각 다리 마스크에 힙까지 기둥 추가(회전 중심 연결)
far_mask, near_mask = legs[0], legs[-1]   # 왼(뒤)=far, 오른(앞)=near

def leg_piece(mask):
    pc = np.zeros_like(a); pc[mask] = a[mask]
    # 힙까지 채우기: hip_y~cut_y 구간에서 그 다리 x대역만 원본 픽셀 포함
    return pc

near = leg_piece(near_mask); far = leg_piece(far_mask)

# 상체 = 원본에서 두 다리 제거
upper = a.copy()
upper[near_mask] = 0; upper[far_mask] = 0
# 다리 제거로 생긴 힙 아래 빈 곳 없게: 상체는 hip 위주로 남김(다리는 따로 얹음)

def rotate_about(img_arr, cx, cy, deg):
    """img_arr(RGBA)를 (cx,cy) 기준 deg 회전. 캔버스 동일 크기 유지."""
    im = Image.fromarray(img_arr)
    # 회전중심을 캔버스 중앙으로 옮겼다 회전 후 복원
    big = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    big.paste(im, (W - cx, H - cy), im)
    big = big.rotate(deg, resample=Image.BICUBIC, center=(W, H))
    out = big.crop((W - cx, H - cy, W - cx + W, H - cy + H))
    return np.array(out)

# 4) 스윙 각도: near 다리 앞(+)→중간(0)→뒤(-)→중간, far 반대
NF = 8
AMP = 26.0
frames = []
for k in range(NF):
    ph = 2 * math.pi * k / NF
    dnear = AMP * math.cos(ph)          # +앞 … -뒤
    dfar = -AMP * math.cos(ph)
    # 걷기1의 near는 이미 '앞'이므로, 목표각-현재각 만큼 회전. 현재 near≈+AMP, far≈-AMP로 가정.
    rn = rotate_about(near, hip_x, hip_y, -(AMP - dnear))   # 앞(+AMP)에서 dnear로
    rf = rotate_about(far, hip_x, hip_y, -(-AMP - dfar))
    canvas = Image.fromarray(upper).convert("RGBA")
    # far(뒤 다리) 먼저, near(앞 다리) 위에
    canvas.alpha_composite(Image.fromarray(rf))
    canvas.alpha_composite(Image.fromarray(rn))
    frames.append(np.array(canvas))
    Image.fromarray(frames[-1]).save(f"{OUT}/rig_{k}.png")

# 컨택트시트
cs = Image.new("RGB", (W * NF, H), (245, 245, 245))
for i, f in enumerate(frames): cs.paste(Image.fromarray(f), (i * W, 0), Image.fromarray(f))
cs.save(f"{OUT}/rig_contact.png")
print(f"리그 {NF}프레임 + 컨택트시트 저장")

# 걷기 mp4(좌→우)
BW, BH = 1280, 720
bg = Image.new("RGB", (BW, BH), (234, 228, 214))
scale = int(BH * 0.55) / H
cw2, ch2 = int(W * scale), int(H * scale)
regr = [Image.fromarray(f).resize((cw2, ch2)) for f in frames]
FPS = 12; HOLD = 3
cycle = NF * HOLD
stride_per_cycle = cw2 * 0.7
x_start, x_end = -cw2, BW
nframes = int((x_end - x_start) / stride_per_cycle * cycle)
foot_y = int(BH * 0.965) - ch2
tmp = f"{OUT}/_seqrig"; os.makedirs(tmp, exist_ok=True)
for fn in os.listdir(tmp): os.remove(os.path.join(tmp, fn))
for k in range(nframes):
    fr = bg.copy()
    x = int(x_start + (x_end - x_start) * (k / max(1, nframes - 1)))
    fr.paste(regr[(k // HOLD) % NF], (x, foot_y), regr[(k // HOLD) % NF])
    fr.save(f"{tmp}/f{k:04d}.png")
out = f"{OUT}/walk_rig.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"★ 리그 걷기: {out} ({nframes/FPS:.1f}초)")
