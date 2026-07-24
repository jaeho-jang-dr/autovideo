# -*- coding: utf-8 -*-
"""W12 인준 포즈 정규화 — 사장님 지시 반영:
   ① 전체 키(머리끝~발끝)를 STAND_H로 딱 통일 (옷·신발·얼굴·체형은 원본 그대로, 크기만 맞춤)
   ② **왼쪽 보고 동작하는 제스처는 좌우 리버스**해서 오른쪽 향하게 저장 (콘텐츠가 오른쪽)
   ③ **단, 걷기(walk)는 예외 — 좌/우 둘 다 유지** (여정물이라 양방향 필요)
   출력: assets/graphics/poses/injun_w12_*.png  +  증명시트 scratch/w12_uniformity.png
"""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
PD = os.path.join(ROOT, "assets", "graphics", "poses")     # 출력
SRC_W10 = PD                                                # 기존 W10 인준(재사용)
SRC_W12 = os.path.join(ROOT, "home_vocab", "w12")           # 신규 생성(agy)
CANVAS_W, CANVAS_H = 560, 860
BOTTOM = CANVAS_H - 16
# ★키 = 발바닥(또는 엉덩이 바닥)~머리끝 기준으로 측정해 그룹별로 통일
STAND_H = 660          # 서기: 머리끝~발바닥
SIT_H   = 560          # 앉기: 앉은 상태 감안(웅크려 낮아지므로) — 너무 작지 않게 서기의 85%
SIT_POSES = set()      # W12는 전부 서기. 앉는 포즈가 생기면 여기에 이름 추가

# W12에서 쓰는 포즈 (build_w12.py 사용 목록)
# (name, 원본소스, flip여부)  flip=True → 왼쪽 보는 것을 오른쪽으로 리버스
POSES = [
    # 기존 W10 재사용 (오른쪽 향함 — flip 불필요)
    ("presenting",    "w10", False),
    ("speak",         "w10", False),
    ("thinking",      "w10", False),
    ("nod",           "w10", False),
    ("listen",        "w10", False),
    ("look_around",   "w10", False),
    ("point_right",   "w10", False),
    ("point_up",      "w10", False),
    ("point_center",  "w10", False),
    ("count_fingers", "w10", False),
    ("hold_cash",     "w10", False),
    ("cheering",      "w10", False),
    ("thumbs_up",     "w10", False),
    ("bow",           "w10", False),
    ("surprise",      "w10", False),
    ("tap_card",      "w10", False),
    # ★ 왼쪽 보는 제스처 → 리버스해서 오른쪽 향하게 (사장님 지시)
    ("point_left",    "w10", True),    # → 리버스하면 오른쪽 가리킴(예비 보관)
    # ★ 걷기 = 좌/우 둘 다 유지 (사장님 지시, 리버스 안 함)
    ("walk_right",    "w10", False),
    ("walk_left",     "w10", False),   # 왼쪽 걷기는 그대로 둔다(되돌아가는 씬용)
    # 신규 생성(agy, home_vocab/w12) — 없으면 스킵
    ("hold_strap",    "w12", False),
    ("pull_suitcase", "w12", False),
    ("look_up_sign",  "w12", False),
    ("walk_stairs",   "w12", False),
]

def cutout(im):
    im = im.convert("RGBA"); a = np.array(im)
    rgb = a[:, :, :3].astype(int); al = a[:, :, 3]
    white = (rgb[:, :, 0] > 238) & (rgb[:, :, 1] > 238) & (rgb[:, :, 2] > 238) & (al > 10)
    lbl, n = ndimage.label(white)
    border = set(np.unique(np.concatenate([lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]]))) - {0}
    a[np.isin(lbl, list(border)), 3] = 0
    return a

def head_top(al):
    """머리끝 행. 든 손·뻗은 팔·캐리어에 흔들리지 않도록 **연결성분(머리 덩어리)**으로 찾는다.

    ⚠️ 기존 '행 픽셀수 >= 30% 최대행' 방식은 point_right처럼 팔을 옆으로 뻗으면
    팔+몸통 행이 넓어져 머리를 건너뛰고 아래를 머리끝으로 잡는 버그가 있었다(H=759).
    → 최상단 성분(머리)의 첫 행을 쓰되, 그 성분이 너무 가늘면(손가락 등) 다음 성분으로.
    """
    mask = al > 30
    if not mask.any():
        return 0
    rowc = mask.sum(axis=1)
    ys = np.where(rowc > 0)[0]
    top = int(ys.min())
    H = al.shape[0]
    # ⚠️ 최대 행폭(rowc.max())을 기준으로 삼으면 안 된다: point_right처럼 팔을 옆으로
    #    뻗으면 그 행이 머리 폭의 3배가 되어, 머리를 통째로 건너뛴다(H=759 버그).
    # → 머리는 '내용이 시작되는 맨 위'에 있다. 가는 삐침(손가락 끝·안테나)만 배제하도록
    #    절대적으로 낮은 임계(이미지 폭의 3% 또는 5px)를 쓰고, 그 상태가 몇 행 이어지는지 확인.
    thr = max(5, int(al.shape[1] * 0.03))
    need = 3                                  # 연속 3행 이상이어야 진짜 덩어리(노이즈 배제)
    run = 0
    for y in range(top, H):
        if rowc[y] >= thr:
            run += 1
            if run >= need:
                return int(y - need + 1)
        else:
            run = 0
    return top

# W12 포즈명 → W10 원본 파일명이 다른 경우 매핑
ALIAS = {"look_around": "browse"}   # 둘러보기 = W10 browse

def src_path(name, src):
    if src == "w10":
        return os.path.join(SRC_W10, f"injun_w10_{ALIAS.get(name, name)}.png")
    return os.path.join(SRC_W12, f"injun_w12_{name}.png")

def process(name, src, flip):
    p = src_path(name, src)
    if not os.path.exists(p):
        return None
    a = cutout(Image.open(p))
    al = a[:, :, 3]
    ys, xs = np.where(al > 20)
    if len(ys) == 0: return None
    top, bot, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    crop = a[top:bot + 1, left:right + 1]
    ht = head_top(crop[:, :, 3])
    feet = crop.shape[0] - 1                       # 크롭 맨 아래 = 발바닥(앉기면 엉덩이/의자 바닥)
    char_h = feet - ht                             # ★발바닥~머리끝
    if char_h <= 0: return None
    target = SIT_H if name in SIT_POSES else STAND_H   # 앉기는 앉은 상태 감안한 별도 기준
    scale = target / char_h                        # ★키 통일(옷·얼굴·체형·비율은 원본 그대로)
    cim = Image.fromarray(crop)
    if flip:
        cim = cim.transpose(Image.FLIP_LEFT_RIGHT)  # ★왼쪽 보는 제스처 → 오른쪽으로
    nw, nh = max(1, round(cim.width * scale)), max(1, round(cim.height * scale))
    cim = cim.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    px = (CANVAS_W - nw) // 2
    py = BOTTOM - nh
    canvas.alpha_composite(cim, (px, max(0, py)))
    out = os.path.join(PD, f"injun_w12_{name}.png")
    canvas.save(out)
    a2 = np.array(canvas)[:, :, 3]
    ht2 = head_top(a2); yy = np.where(a2 > 20)[0]; feet2 = yy.max() if len(yy) else 0
    return {"name": name, "src": src, "char_h_src": int(char_h), "scale": round(scale, 3),
            "height_after": int(feet2 - ht2), "head_top": int(ht2), "feet": int(feet2), "flip": flip}

def sheet(rows):
    rows = [r for r in rows if r]
    cols = 6; rws = (len(rows) + cols - 1) // cols
    tw, th = 260, 420
    sh = Image.new("RGB", (cols * tw, rws * th + 46), (250, 248, 244))
    d = ImageDraw.Draw(sh)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 16)
        fb = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 21)
    except Exception:
        f = fb = ImageFont.load_default()
    d.text((14, 11), f"W12 인준 — 전체 키 통일 {STAND_H}px (초록=머리끝, 빨강=발). ↔=왼쪽보던 것 리버스. walk는 좌우 둘 다 유지",
           font=fb, fill=(30, 30, 30))
    for i, r in enumerate(rows):
        cx = (i % cols) * tw; cy = (i // cols) * th + 46
        im = Image.open(os.path.join(PD, f"injun_w12_{r['name']}.png")).convert("RGBA")
        sc = min(tw / im.width, (th - 28) / im.height)
        iw, ih = int(im.width * sc), int(im.height * sc)
        bgc = Image.new("RGBA", (tw, th), (255, 255, 255, 255))
        bgc.alpha_composite(im.resize((iw, ih), Image.LANCZOS), ((tw - iw) // 2, 0))
        sh.paste(bgc.convert("RGB"), (cx, cy))
        gy = cy + int(r['head_top'] * sc); fy = cy + int(r['feet'] * sc)
        d.line((cx, gy, cx + tw, gy), fill=(0, 175, 0), width=2)
        d.line((cx, fy, cx + tw, fy), fill=(220, 40, 40), width=2)
        tag = f"{r['name']} H={r['height_after']}" + (" ↔" if r['flip'] else "")
        d.text((cx + 6, cy + th - 24), tag, font=f, fill=(20, 20, 20))
    out = os.path.join(ROOT, "scratch", "w12_uniformity.png")
    sh.save(out); return out

if __name__ == "__main__":
    rows = [process(n, s, fl) for (n, s, fl) in POSES]
    ok = [r for r in rows if r]
    missing = [n for (n, s, fl), r in zip(POSES, rows) if r is None]
    hs = [r["height_after"] for r in ok if r["name"] not in SIT_POSES]
    print(f"처리 {len(ok)}/{len(POSES)}종")
    print(f"키 after: min={min(hs)} max={max(hs)} (목표 {STAND_H}) → 편차 {max(hs)-min(hs)}px")
    print("리버스(왼→오):", [r['name'] for r in ok if r['flip']])
    print("걷기 유지:", [r['name'] for r in ok if r['name'].startswith('walk')])
    if missing: print("★미생성(agy 대기):", missing)
    print("증명시트:", sheet(ok))
