# -*- coding: utf-8 -*-
"""W13 지은 포즈 정규화 — 사장님 원칙 그대로:
   ① 전체 키(발바닥~머리끝)를 STAND_H로 통일 (얼굴·머리·옷·신발·체형은 원본 그대로, 크기만 맞춤)
   ② 왼쪽 보고 동작하는 제스처는 좌우 리버스 → 오른쪽 향하게 (콘텐츠가 오른쪽)
      단, **point_left는 '왼쪽을 가리키는' 의미가 있어 리버스하지 않는다**(내용상 왼쪽이어야 함)
   ③ 걷기(walk)는 좌/우 둘 다 유지
   출력: assets/graphics/poses/jieun_w13_*.png + 증명시트 scratch/w13_uniformity.png
"""
import os, sys, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
PD = os.path.join(ROOT, "assets", "graphics", "poses")
SRC = os.path.join(ROOT, "home_vocab", "w13")
CANVAS_W, CANVAS_H = 560, 860
BOTTOM = CANVAS_H - 16
STAND_H = 660              # 서기 키(발바닥~머리끝) — W12와 동일 규격
SIT_H = 560                # 앉기(있으면)
SIT_POSES = set()          # W13은 전부 서기

# 리버스 대상: 왼쪽을 향해 '동작'하는 것 중 내용상 오른쪽이어야 하는 것.
# ※ point_left / walk_left* 는 의미상 왼쪽이어야 하므로 리버스하지 않는다.
FLIP = set()


def cutout(im):
    im = im.convert("RGBA"); a = np.array(im)
    rgb = a[:, :, :3].astype(int); al = a[:, :, 3]
    white = (rgb[:, :, 0] > 238) & (rgb[:, :, 1] > 238) & (rgb[:, :, 2] > 238) & (al > 10)
    lbl, n = ndimage.label(white)
    border = set(np.unique(np.concatenate([lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]]))) - {0}
    a[np.isin(lbl, list(border)), 3] = 0
    return a


def head_top(al):
    """머리끝 행. 뻗은 팔·든 손에 흔들리지 않게 '내용이 시작되는 맨 위'에서
    가는 삐침만 배제(폭 3% 임계 + 연속 3행). W12에서 검증된 방식."""
    mask = al > 30
    if not mask.any():
        return 0
    rowc = mask.sum(axis=1)
    ys = np.where(rowc > 0)[0]
    top = int(ys.min())
    thr = max(5, int(al.shape[1] * 0.03))
    need, run = 3, 0
    for y in range(top, al.shape[0]):
        if rowc[y] >= thr:
            run += 1
            if run >= need:
                return int(y - need + 1)
        else:
            run = 0
    return top


def process(path):
    name = os.path.basename(path).replace("jieun_w13_", "").replace(".png", "")
    a = cutout(Image.open(path))
    al = a[:, :, 3]
    ys, xs = np.where(al > 20)
    if len(ys) == 0:
        return None
    top, bot, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    crop = a[top:bot + 1, left:right + 1]
    ht = head_top(crop[:, :, 3])
    feet = crop.shape[0] - 1                  # 발바닥
    char_h = feet - ht
    if char_h <= 0:
        return None
    target = SIT_H if name in SIT_POSES else STAND_H
    scale = target / char_h
    cim = Image.fromarray(crop)
    flip = name in FLIP
    if flip:
        cim = cim.transpose(Image.FLIP_LEFT_RIGHT)
    nw, nh = max(1, round(cim.width * scale)), max(1, round(cim.height * scale))
    cim = cim.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.alpha_composite(cim, ((CANVAS_W - nw) // 2, max(0, BOTTOM - nh)))
    out = os.path.join(PD, f"jieun_w13_{name}.png")
    canvas.save(out)
    a2 = np.array(canvas)[:, :, 3]
    ht2 = head_top(a2); yy = np.where(a2 > 20)[0]; feet2 = yy.max() if len(yy) else 0
    return {"name": name, "height_after": int(feet2 - ht2), "head_top": int(ht2),
            "feet": int(feet2), "flip": flip}


def sheet(rows):
    rows = sorted([r for r in rows if r], key=lambda x: x["name"])
    cols = 7
    rws = (len(rows) + cols - 1) // cols
    tw, th = 240, 400
    sh = Image.new("RGB", (cols * tw, rws * th + 48), (250, 249, 245))
    d = ImageDraw.Draw(sh)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 15)
        fb = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 22)
    except Exception:
        f = fb = ImageFont.load_default()
    d.text((14, 12), f"W13 지은 포즈 {len(rows)}종 — 전체 키 통일 {STAND_H}px (초록=머리끝, 빨강=발바닥). _a=중간포즈, walk 1/2=걷기 교대",
           font=fb, fill=(28, 28, 28))
    for i, r in enumerate(rows):
        cx = (i % cols) * tw; cy = (i // cols) * th + 48
        im = Image.open(os.path.join(PD, f"jieun_w13_{r['name']}.png")).convert("RGBA")
        sc = min(tw / im.width, (th - 26) / im.height)
        iw, ih = int(im.width * sc), int(im.height * sc)
        bgc = Image.new("RGBA", (tw, th), (255, 255, 255, 255))
        bgc.alpha_composite(im.resize((iw, ih), Image.LANCZOS), ((tw - iw) // 2, 0))
        sh.paste(bgc.convert("RGB"), (cx, cy))
        gy = cy + int(r["head_top"] * sc); fy = cy + int(r["feet"] * sc)
        d.line((cx, gy, cx + tw, gy), fill=(0, 175, 0), width=2)
        d.line((cx, fy, cx + tw, fy), fill=(220, 40, 40), width=2)
        d.text((cx + 6, cy + th - 22), f"{r['name']} H={r['height_after']}", font=f, fill=(20, 20, 20))
    out = os.path.join(ROOT, "scratch", "w13_uniformity.png")
    sh.save(out)
    return out


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(SRC, "jieun_w13_*.png")))
    rows = [process(p) for p in files]
    ok = [r for r in rows if r]
    hs = [r["height_after"] for r in ok if r["name"] not in SIT_POSES]
    print(f"처리 {len(ok)}/{len(files)}종")
    if hs:
        print(f"키 after: min={min(hs)} max={max(hs)} (목표 {STAND_H}) → 편차 {max(hs)-min(hs)}px")
    print("증명시트:", sheet(ok))
