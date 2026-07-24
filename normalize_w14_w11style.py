# -*- coding: utf-8 -*-
"""★W14 포즈 정규화 — W11(감천 식당, 성공작) 규격 그대로.

W11이 왜 완벽했나 (실측):
  · 좌표는 전 씬 **(300, 452, scale 0.6) 하나**뿐 — 앉기/서기 구분 없음
  · 비결: 포즈 PNG를 **560x860 캔버스에 "인물 맨아래(발끝/엉덩이) = y 700"** 로 정규화
    → 같은 좌표로 얹어도 서기(403~420px)든 앉기(302~318px)든 바닥이 딱 맞고 안 잘린다
  · 앉기 높이 = 서기의 약 76% (자연스럽게 나온 값. 억지로 정한 비율이 아니다)

W14도 동일 규격으로 맞춘다:
  · 캔버스 560x860, 인물 맨아래 = y 700 (BOTTOM)
  · 서기 = STAND_H(660px, 캔버스 기준) 로 키 통일   → 렌더 시 ×0.655 ≈ 432px
  · 앉기 = 캔버스에서 서기의 76% → 렌더 시 ≈ 328px (W11과 같은 비율)
  · 누움 = 머리~발끝 '길이'를 서기 키와 같게(가로)
출력: assets/graphics/poses/mj_w14_*.png + 증명시트 scratch/w14_uniformity.png
"""
import os, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
PD = os.path.join(ROOT, "assets", "graphics", "poses")
SRC = os.path.join(ROOT, "home_vocab", "w14")
CANVAS_W, CANVAS_H = 560, 860
BOTTOM = 700            # ★W11 규격: 인물 맨아래가 항상 여기 (렌더 좌표 (300,452,0.655)와 맞물림)
STAND_H = 660           # 서기 키(캔버스 기준) → 렌더 432px
SIT_H = round(STAND_H * 0.76)   # ★W11 실측 비율 76% → 캔버스 502px, 렌더 ≈328px

SIT_POSES = {"eat_sit", "drink_sit", "sit_desk", "work_laptop", "work_laptop_a",
             "study_book", "study_book_a", "read_book", "write_note", "write_note_a",
             "rest_sit", "watch_tv", "write_diary", "wake_sit", "sit_stargaze"}
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
    """머리끝 행 — 든 손·뻗은 팔에 안 흔들리게 연속 3행 임계(W12/W13 검증 방식)."""
    mask = al > 30
    if not mask.any():
        return 0
    rowc = mask.sum(axis=1)
    ys = np.where(rowc > 0)[0]
    top = int(ys.min())
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
    name = os.path.basename(path).replace("mj_w14_", "").replace(".png", "")
    a = cutout(Image.open(path))
    al = a[:, :, 3]
    ys, xs = np.where(al > 20)
    if len(ys) == 0:
        return None
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

    if name == "sleep":                       # 누움: 가로 '길이'를 서기 키에 맞춤
        fig = crop.shape[1]
        scale = STAND_H / fig
    else:
        ht = head_top(crop[:, :, 3])
        feet = crop.shape[0] - 1
        char_h = feet - ht
        if char_h <= 0:
            return None
        target = SIT_H if name in SIT_POSES else STAND_H
        scale = target / char_h

    cim = Image.fromarray(crop)
    if name in FLIP:
        cim = cim.transpose(Image.FLIP_LEFT_RIGHT)
    nw, nh = max(1, round(cim.width * scale)), max(1, round(cim.height * scale))
    cim = cim.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    # ★W11 규격: 인물 맨아래를 항상 BOTTOM(700)에. 가로는 중앙.
    canvas.alpha_composite(cim, ((CANVAS_W - nw) // 2, BOTTOM - nh))
    out = os.path.join(PD, f"mj_w14_{name}.png")
    canvas.save(out)

    a2 = np.array(canvas)[:, :, 3]
    yy = np.where(a2 > 20)[0]
    ht2 = head_top(a2); bot2 = int(yy.max()) if len(yy) else 0
    kind = "누움" if name == "sleep" else ("앉기" if name in SIT_POSES else "서기")
    return {"name": name, "h": int(bot2 - ht2), "head": int(ht2), "bot": bot2, "kind": kind}


def sheet(rows):
    rows = sorted([r for r in rows if r], key=lambda x: (x["kind"], x["name"]))
    cols = 8
    rws = (len(rows) + cols - 1) // cols
    tw, th = 210, 350
    sh = Image.new("RGB", (cols * tw, rws * th + 52), (250, 249, 245))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 13)
    fb = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 20)
    d.text((14, 14), f"W14 포즈 {len(rows)}종 — W11(감천식당) 규격: 인물 맨아래=y{BOTTOM} 통일 / "
                     f"서기 {STAND_H} · 앉기 {SIT_H}(76%) (빨강=바닥선)", font=fb, fill=(28, 28, 28))
    for i, r in enumerate(rows):
        cx = (i % cols) * tw; cy = (i // cols) * th + 52
        im = Image.open(os.path.join(PD, f"mj_w14_{r['name']}.png")).convert("RGBA")
        sc = min(tw / im.width, (th - 24) / im.height)
        iw, ih = int(im.width * sc), int(im.height * sc)
        bgc = Image.new("RGBA", (tw, th), (255, 255, 255, 255))
        bgc.alpha_composite(im.resize((iw, ih), Image.LANCZOS), ((tw - iw) // 2, 0))
        sh.paste(bgc.convert("RGB"), (cx, cy))
        by = cy + int(BOTTOM * sc)
        d.line((cx, by, cx + tw, by), fill=(220, 40, 40), width=2)
        d.text((cx + 5, cy + th - 20), f"{r['name']} H={r['h']} [{r['kind']}]"[:26], font=f, fill=(20, 20, 20))
    out = os.path.join(ROOT, "scratch", "w14_uniformity.png")
    sh.save(out)
    return out


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(SRC, "mj_w14_*.png")))
    rows = [process(p) for p in files]
    ok = [r for r in rows if r]
    for kind in ("서기", "앉기", "누움"):
        hs = [r["h"] for r in ok if r["kind"] == kind]
        bt = [r["bot"] for r in ok if r["kind"] == kind]
        if hs:
            print(f"  {kind}: {len(hs)}종  키 {min(hs)}~{max(hs)}px (편차 {max(hs)-min(hs)})  "
                  f"바닥 y {min(bt)}~{max(bt)} (목표 {BOTTOM})")
    print("증명시트:", sheet(ok))
