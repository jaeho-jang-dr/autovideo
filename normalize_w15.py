# -*- coding: utf-8 -*-
"""★W15 지은 포즈 정규화 — 크기 통일 최우선 (사장님 지시).

규칙:
  · 투명 컷아웃(흰 배경 제거)
  · 서기(대부분) = 전부 같은 키로 통일 (머리끝~발끝 = STAND_H)
  · 쪼그린 자세(snowman) = 서기 키의 50% 높이
  · 캔버스 560x860, 인물 맨아래(발끝) = y 700 정렬 → 렌더 좌표 하나로 안 잘림 (W11/W14 규격)
출력: assets/graphics/poses/jieun_w15_*.png + 증명시트 scratch/w15_uniformity.png
"""
import os, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
PD = os.path.join(ROOT, "assets", "graphics", "poses")
SRC = os.path.join(ROOT, "home_vocab", "w15")
CANVAS_W, CANVAS_H = 560, 860
BOTTOM = 700
STAND_H = 660                       # 서기 키(캔버스 기준) → 렌더 ×0.655 ≈ 432px
CROUCH_H = round(STAND_H * 0.50)    # ★쪼그림 = 서기의 50%

CROUCH_POSES = {"winter_snowman"}   # 쪼그려/허리 굽혀 눈사람 만드는 자세
FLIP = set()


def cutout(im):
    """4모서리 흰 배경만 flood-fill 로 투명화(내부 흰색은 보존)."""
    im = im.convert("RGBA")
    a = np.array(im)
    rgb = a[:, :, :3].astype(int)
    al = a[:, :, 3]
    white = (rgb[:, :, 0] > 238) & (rgb[:, :, 1] > 238) & (rgb[:, :, 2] > 238) & (al > 10)
    lbl, n = ndimage.label(white)
    border = set(np.unique(np.concatenate([lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]]))) - {0}
    a[np.isin(lbl, list(border)), 3] = 0
    return a


def head_top(al):
    """머리끝 행 — 든 손·뻗은 팔에 안 흔들리게 연속 3행 임계(W12/W13/W14 검증)."""
    mask = al > 30
    if not mask.any():
        return 0
    rowc = mask.sum(axis=1)
    top = int(np.where(rowc > 0)[0].min())
    thr = max(5, int(al.shape[1] * 0.03))
    run = 0
    for y in range(top, al.shape[0]):
        if rowc[y] >= thr:
            run += 1
            if run >= 3:
                return int(y - 2)
        else:
            run = 0
    return top


def process(path):
    name = os.path.basename(path).replace("jieun_", "").replace(".png", "")
    a = cutout(Image.open(path))
    al = a[:, :, 3]
    ys, xs = np.where(al > 20)
    if len(ys) == 0:
        return None
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

    ht = head_top(crop[:, :, 3])
    feet = crop.shape[0] - 1
    char_h = feet - ht
    if char_h <= 0:
        return None
    target = CROUCH_H if name in CROUCH_POSES else STAND_H
    scale = target / char_h

    cim = Image.fromarray(crop)
    if name in FLIP:
        cim = cim.transpose(Image.FLIP_LEFT_RIGHT)
    nw, nh = max(1, round(cim.width * scale)), max(1, round(cim.height * scale))
    cim = cim.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.alpha_composite(cim, ((CANVAS_W - nw) // 2, BOTTOM - nh))   # 발끝 = y700
    out = os.path.join(PD, f"jieun_w15_{name}.png")
    canvas.save(out)

    a2 = np.array(canvas)[:, :, 3]
    yy = np.where(a2 > 20)[0]
    ht2 = head_top(a2)
    bot2 = int(yy.max()) if len(yy) else 0
    kind = "쪼그림" if name in CROUCH_POSES else "서기"
    return {"name": name, "h": int(bot2 - ht2), "head": int(ht2), "bot": bot2, "kind": kind}


def sheet(rows):
    rows = sorted([r for r in rows if r], key=lambda x: (x["kind"], x["name"]))
    cols = 8
    rws = (len(rows) + cols - 1) // cols
    tw, th = 200, 340
    sh = Image.new("RGB", (cols * tw, rws * th + 52), (250, 249, 245))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 12)
    fb = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 20)
    d.text((14, 14), f"W15 지은 포즈 {len(rows)}종 — 서기 통일 {STAND_H} / 쪼그림 {CROUCH_H}(50%) · 발끝 y{BOTTOM} (빨강=바닥)",
           font=fb, fill=(28, 28, 28))
    for i, r in enumerate(rows):
        cx = (i % cols) * tw
        cy = (i // cols) * th + 52
        im = Image.open(os.path.join(PD, f"jieun_w15_{r['name']}.png")).convert("RGBA")
        sc = min(tw / im.width, (th - 24) / im.height)
        iw, ih = int(im.width * sc), int(im.height * sc)
        bgc = Image.new("RGBA", (tw, th), (255, 255, 255, 255))
        bgc.alpha_composite(im.resize((iw, ih), Image.LANCZOS), ((tw - iw) // 2, 0))
        sh.paste(bgc.convert("RGB"), (cx, cy))
        by = cy + int(BOTTOM * sc)
        d.line((cx, by, cx + tw, by), fill=(220, 40, 40), width=2)
        d.text((cx + 4, cy + th - 18), f"{r['name']} H={r['h']}"[:24], font=f, fill=(20, 20, 20))
    out = os.path.join(ROOT, "scratch", "w15_uniformity.png")
    sh.save(out)
    return out


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(SRC, "jieun_*.png")))
    rows = [process(p) for p in files]
    ok = [r for r in rows if r]
    st = [r["h"] for r in ok if r["kind"] == "서기"]
    cr = [r["h"] for r in ok if r["kind"] == "쪼그림"]
    print(f"처리 {len(ok)}/{len(files)}종")
    if st:
        print(f"  서기 {len(st)}종: 키 {min(st)}~{max(st)}px (목표 {STAND_H}) 편차 {max(st)-min(st)}px, 발끝 통일")
    if cr:
        print(f"  쪼그림 {len(cr)}종: 키 {cr} (목표 {CROUCH_H} = 서기 50%)")
    print("증명시트:", sheet(ok))
