# -*- coding: utf-8 -*-
"""W14 마담제이 포즈 정규화 — 사장님 원칙:
   ① 전체 키(발바닥~머리끝) 통일 — 서기 STAND_H / 앉기 SIT_H (앉기는 의자 포함이라 별도 그룹)
   ② 얼굴·머리·옷·신발·체형은 원본 그대로, 크기만 맞춤
   ③ 걷기는 좌/우 둘 다 유지
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
BOTTOM = CANVAS_H - 16
STAND_H = 660          # 서기: 머리끝~발바닥
SIT_H   = 560          # ★앉기(의자 포함): 머리끝~의자바닥. 서기의 85%

# 앉기/누움 포즈 (의자·침대 포함 → 별도 키 그룹)
SIT_POSES = {"eat_sit", "drink_sit", "sit_desk", "work_laptop", "work_laptop_a",
             "study_book", "study_book_a", "read_book", "write_note", "write_note_a",
             "rest_sit", "watch_tv", "write_diary", "wake_sit", "sit_stargaze"}   # ★sleep(누움)은 가로라 키 정규화 제외
FLIP = set()           # 리버스 대상 없음(전부 오른쪽/정면 향함)


def cutout(im):
    im = im.convert("RGBA"); a = np.array(im)
    rgb = a[:, :, :3].astype(int); al = a[:, :, 3]
    white = (rgb[:, :, 0] > 238) & (rgb[:, :, 1] > 238) & (rgb[:, :, 2] > 238) & (al > 10)
    lbl, n = ndimage.label(white)
    border = set(np.unique(np.concatenate([lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]]))) - {0}
    a[np.isin(lbl, list(border)), 3] = 0
    return a


def head_top(al):
    """머리끝 행. 든 손·뻗은 팔에 흔들리지 않게 낮은 임계 + 연속 3행(W12/W13 검증 방식)."""
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
    name = os.path.basename(path).replace("mj_w14_", "").replace(".png", "")
    a = cutout(Image.open(path))
    al = a[:, :, 3]
    ys, xs = np.where(al > 20)
    if len(ys) == 0:
        return None
    top, bot, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    crop = a[top:bot + 1, left:right + 1]
    ht = head_top(crop[:, :, 3])
    feet = crop.shape[0] - 1
    char_h = feet - ht
    if char_h <= 0:
        return None
    is_sit = name in SIT_POSES
    target = SIT_H if is_sit else STAND_H
    scale = target / char_h
    cim = Image.fromarray(crop)
    if name in FLIP:
        cim = cim.transpose(Image.FLIP_LEFT_RIGHT)
    nw, nh = max(1, round(cim.width * scale)), max(1, round(cim.height * scale))
    cim = cim.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    canvas.alpha_composite(cim, ((CANVAS_W - nw) // 2, max(0, BOTTOM - nh)))
    out = os.path.join(PD, f"mj_w14_{name}.png")
    canvas.save(out)
    a2 = np.array(canvas)[:, :, 3]
    ht2 = head_top(a2); yy = np.where(a2 > 20)[0]; feet2 = yy.max() if len(yy) else 0
    return {"name": name, "h": int(feet2 - ht2), "head": int(ht2), "feet": int(feet2), "sit": is_sit}


def process_lying(path, target_len=520, canvas_w=CANVAS_W, canvas_h=CANVAS_H, bottom=BOTTOM):
    """누움 포즈: 컷아웃 후 머리~발끝 '길이'(가로 bbox)를 target_len 으로 맞추고
       ★표준 560 캔버스에 바닥정렬(다른 포즈와 동일 규격 → 렌더러 get_tile과 호환).
       흰배경 제거 + 크롭 없음(크게 만들어 화면맞춤 크롭 금지)."""
    a = cutout(Image.open(path))
    al = a[:, :, 3]
    ys, xs = np.where(al > 20)
    if len(ys) == 0:
        return None
    top, bot, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    crop = a[top:bot + 1, left:right + 1]
    fig_len = crop.shape[1]                     # 가로 = 머리~발끝 길이
    scale = target_len / fig_len
    cim = Image.fromarray(crop)
    nw, nh = max(1, round(cim.width * scale)), max(1, round(cim.height * scale))
    cim = cim.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    canvas.alpha_composite(cim, ((canvas_w - nw) // 2, max(0, bottom - nh)))
    out = os.path.join(PD, os.path.basename(path))
    canvas.save(out)
    return {"name": "sleep(lying)", "w": nw, "h": nh, "canvas": (canvas_w, canvas_h)}


def sheet(rows):
    rows = sorted([r for r in rows if r], key=lambda x: (x["sit"], x["name"]))
    cols = 8
    rws = (len(rows) + cols - 1) // cols
    tw, th = 210, 350
    sh = Image.new("RGB", (cols * tw, rws * th + 50), (250, 249, 245))
    d = ImageDraw.Draw(sh)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 13)
        fb = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 21)
    except Exception:
        f = fb = ImageFont.load_default()
    d.text((14, 13), f"W14 마담제이 포즈 {len(rows)}종 — 서기 {STAND_H}px / 앉기 {SIT_H}px 통일 "
                     f"(초록=머리끝, 빨강=바닥). _a=중간동작", font=fb, fill=(28, 28, 28))
    for i, r in enumerate(rows):
        cx = (i % cols) * tw; cy = (i // cols) * th + 50
        im = Image.open(os.path.join(PD, f"mj_w14_{r['name']}.png")).convert("RGBA")
        sc = min(tw / im.width, (th - 24) / im.height)
        iw, ih = int(im.width * sc), int(im.height * sc)
        bgc = Image.new("RGBA", (tw, th), (255, 255, 255, 255))
        bgc.alpha_composite(im.resize((iw, ih), Image.LANCZOS), ((tw - iw) // 2, 0))
        sh.paste(bgc.convert("RGB"), (cx, cy))
        gy = cy + int(r["head"] * sc); fy = cy + int(r["feet"] * sc)
        col = (0, 175, 0) if not r["sit"] else (0, 130, 200)
        d.line((cx, gy, cx + tw, gy), fill=col, width=2)
        d.line((cx, fy, cx + tw, fy), fill=(220, 40, 40), width=2)
        tag = f"{r['name']} H={r['h']}" + (" [앉]" if r["sit"] else "")
        d.text((cx + 5, cy + th - 20), tag[:26], font=f, fill=(20, 20, 20))
    out = os.path.join(ROOT, "scratch", "w14_uniformity.png")
    sh.save(out)
    return out


if __name__ == "__main__":
    files = [f for f in sorted(glob.glob(os.path.join(SRC, "mj_w14_*.png")))
             if "sleep" not in os.path.basename(f)]   # 누움 포즈는 원본 그대로 복사
    rows = [process(p) for p in files]
    ok = [r for r in rows if r]
    st = [r["h"] for r in ok if not r["sit"]]
    si = [r["h"] for r in ok if r["sit"]]
    print(f"처리 {len(ok)}/{len(files)}종")
    if st: print(f"  서기 키: min={min(st)} max={max(st)} (목표 {STAND_H}) 편차 {max(st)-min(st)}px  [{len(st)}종]")
    if si: print(f"  앉기 키: min={min(si)} max={max(si)} (목표 {SIT_H}) 편차 {max(si)-min(si)}px  [{len(si)}종]")
    # ★누움 포즈: 컷아웃 + 머리~발끝 '길이'를 서기 키(STAND_H)로 정규화 + 바닥정렬(흰배경/크롭 금지)
    for f in glob.glob(os.path.join(SRC, "mj_w14_sleep*.png")):
        r = process_lying(f)
        print(f"  누움 정규화: {os.path.basename(f)} -> 길이 {r['w']}px, 캔버스 {r['canvas']}" if r
              else f"  누움 실패: {f}")
    print("증명시트:", sheet(ok))
