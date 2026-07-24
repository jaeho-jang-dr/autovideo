# -*- coding: utf-8 -*-
"""★인준 포즈 크기 정규화 — 크기 통일 최우선(사장님 지시, W16 준비).

문제: 인준 포즈가 세대별로 스케일 제각각(base 1024 흰배경 / 활동 1376×768 투명 / w10 varied).
      알파 실체 높이 599~1115px, 편차 큼 → 합성 시 크기 들쭉날쭉.

규칙(W15 방법 확장):
  · 흰 배경이면 4모서리 flood-fill 컷아웃, 이미 투명이면 그대로.
  · 머리끝~바닥(최하 알파=지면접촉) 높이를 그룹별 목표로 통일.
      - 서기/활동(기본) = STAND_H
      - 앉기(자전거·의자앉기·독서벤치·피아노) = STAND_H×0.80
      - 웅크림(캠핑·정원) = STAND_H×0.72
  · 인준 활동 포즈는 가로가 넓다(축구+공 등) → 캔버스 1376×880, 바닥 y=800.
  · 발끝(최하 알파) = y800 앵커 → 렌더 좌표 하나로 일관.
출력: assets/graphics/poses/injun_w16_*.png + 증명시트 scratch/injun_w16_uniformity.png
"""
import os, glob, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
PD = os.path.join(ROOT, "assets", "graphics", "poses")
# 소스 검색 우선순위
SRC_DIRS = [os.path.join(ROOT, "home_vocab"),
            os.path.join(ROOT, "assets", "characters", "cutouts"),
            os.path.join(ROOT, "assets", "graphics", "poses")]

CANVAS_W, CANVAS_H = 1376, 880
BOTTOM = 800
STAND_H = 640
SEAT_H = round(STAND_H * 0.76)     # 앉기(피아노·벤치독서·소파·돗자리) = 서기의 76%(check_char_fit과 일치)
CROUCH_H = round(STAND_H * 0.72)

SEAT = {"piano", "reading_bench", "gaming", "watching_movie", "picnic_sit"}
CROUCH = set()

# W16 신규 생성 포즈(home_vocab/w16/injun_w16_<key>.png)
_NEW = [
    "cycling", "cycling_b", "jogging", "jogging_b", "taking_photo", "picnic_sit", "kite",
    "frisbee", "frisbee_b", "badminton", "badminton_b", "fishing", "walking_dog", "animal_watch",
    "zipwire", "jump_rope", "jump_rope_b", "camping", "reading_bench", "painting", "skateboard",
    "skateboard_b", "piano", "cooking", "watching_movie", "singing", "gaming", "suitcase",
    "stretching", "walk_r1", "walk_r2",
]
# W16 재사용 제스처(injun_w10 표준을 동일 규격으로 재정규화). out_key -> injun_w10 파일 key
_REUSE = {
    "cheering": "cheering", "clapping": "clapping", "greeting": "greeting",
    "point_left": "point_left", "point_right": "point_right", "point_self": "point_self",
    "point_up": "point_up", "presenting": "presenting", "raising_hand": "raising_hand",
    "thinking": "thinking", "waving": "wave_right",
}
SRCMAP = {}
for _k in _NEW:
    SRCMAP[_k] = os.path.join(ROOT, "home_vocab", "w16", f"injun_w16_{_k}.png")
for _outk, _w10k in _REUSE.items():
    SRCMAP[_outk] = os.path.join(ROOT, "assets", "graphics", "poses", f"injun_w10_{_w10k}.png")
POSES = list(SRCMAP.keys())


def find_src(key):
    p = SRCMAP.get(key)
    return p if p and os.path.exists(p) else None


def cutout(im):
    """4모서리에서 이어진 흰 배경만 투명화(내부 흰색 보존). 이미 투명이면 사실상 그대로."""
    im = im.convert("RGBA")
    a = np.array(im)
    rgb = a[:, :, :3].astype(int)
    al = a[:, :, 3]
    white = (rgb[:, :, 0] > 238) & (rgb[:, :, 1] > 238) & (rgb[:, :, 2] > 238) & (al > 10)
    if white.any():
        lbl, n = ndimage.label(white)
        border = set(np.unique(np.concatenate([lbl[0, :], lbl[-1, :], lbl[:, 0], lbl[:, -1]]))) - {0}
        a[np.isin(lbl, list(border)), 3] = 0
    return a


def head_top(al):
    """머리끝 행 — 연속 3행 임계로 든 손/뻗은 팔 무시(W12~15 검증)."""
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


def group_of(key):
    if key in SEAT:
        return "앉기", SEAT_H
    if key in CROUCH:
        return "웅크림", CROUCH_H
    return "서기", STAND_H


def process(key):
    src = find_src(key)
    if not src:
        return None
    a = cutout(Image.open(src))
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
    kind, target = group_of(key)
    scale = target / char_h
    cim = Image.fromarray(crop)
    nw, nh = max(1, round(cim.width * scale)), max(1, round(cim.height * scale))
    cim = cim.resize((nw, nh), Image.LANCZOS)
    # 가로가 캔버스보다 넓으면 캔버스 폭 확장 방지 위해 중앙 배치(넘치면 잘림 경고)
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    ox = (CANVAS_W - nw) // 2
    canvas.alpha_composite(cim, (ox, BOTTOM - nh))
    out = os.path.join(PD, f"injun_w16_{key}.png")
    canvas.save(out)
    a2 = np.array(canvas)[:, :, 3]
    yy, xx = np.where(a2 > 20)
    over = (nw > CANVAS_W)
    return {"key": key, "kind": kind, "h": int(char_h * scale), "w": nw,
            "over": over, "target": target}


def sheet(rows):
    rows = sorted([r for r in rows if r], key=lambda x: (x["kind"], x["key"]))
    cols = 7
    rws = (len(rows) + cols - 1) // cols
    tw, th = 240, 300
    sh = Image.new("RGB", (cols * tw, rws * th + 56), (250, 249, 245))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 13)
    fb = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 20)
    d.text((14, 16), f"인준 포즈 {len(rows)}종 정규화 — 서기 {STAND_H}/앉기 {SEAT_H}/웅크림 {CROUCH_H} · 발끝 y{BOTTOM} (빨강=바닥선, 초록=서기키)",
           font=fb, fill=(28, 28, 28))
    for i, r in enumerate(rows):
        cx = (i % cols) * tw
        cy = (i // cols) * th + 56
        im = Image.open(os.path.join(PD, f"injun_w16_{r['key']}.png")).convert("RGBA")
        sc = min(tw / im.width, (th - 24) / im.height)
        iw, ih = int(im.width * sc), int(im.height * sc)
        bgc = Image.new("RGBA", (tw, th), (255, 255, 255, 255))
        bgc.alpha_composite(im.resize((iw, ih), Image.LANCZOS), ((tw - iw) // 2, 0))
        sh.paste(bgc.convert("RGB"), (cx, cy))
        by = cy + int(BOTTOM * sc)
        d.line((cx, by, cx + tw, by), fill=(220, 40, 40), width=2)       # 바닥선
        ty = cy + int((BOTTOM - STAND_H) * sc)
        d.line((cx, ty, cx + tw, ty), fill=(40, 170, 90), width=1)        # 서기 머리높이 기준선
        flag = " ⚠넘침" if r["over"] else ""
        d.text((cx + 4, cy + th - 18), f"{r['key']} {r['kind']}{flag}"[:30], font=f, fill=(20, 20, 20))
    out = os.path.join(ROOT, "scratch", "injun_w16_uniformity.png")
    sh.save(out)
    return out


if __name__ == "__main__":
    from PIL import ImageOps
    rows = [process(k) for k in POSES]
    # 왼쪽 걷기 = 오른쪽 걷기 좌우반전(정규화 규격 그대로 유지)
    for r_key, l_key in [("walk_r1", "walk_l1"), ("walk_r2", "walk_l2")]:
        rp = os.path.join(PD, f"injun_w16_{r_key}.png")
        if os.path.exists(rp):
            ImageOps.mirror(Image.open(rp).convert("RGBA")).save(
                os.path.join(PD, f"injun_w16_{l_key}.png"))
            print(f"  플립: {l_key} <- {r_key}")
    ok = [r for r in rows if r]
    miss = [POSES[i] for i, r in enumerate(rows) if r is None]
    st = [r["h"] for r in ok if r["kind"] == "서기"]
    print(f"처리 {len(ok)}/{len(POSES)}종  (소스없음: {miss})")
    if st:
        print(f"  서기 {len(st)}종: 키 {min(st)}~{max(st)}px (목표 {STAND_H}) 편차 {max(st)-min(st)}px")
    over = [r["key"] for r in ok if r["over"]]
    if over:
        print(f"  ⚠ 캔버스 폭({CANVAS_W}) 넘침: {over}")
    print("증명시트:", sheet(ok))
