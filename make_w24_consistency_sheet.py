# -*- coding: utf-8 -*-
"""W24 에셋 일관성 증명시트 — ①크기 ②머리·얼굴·옷·신발·손.
   ★사장님 지시(2026-08-04): "함부로 크롭하거나 키우지 마라" → 이 스크립트는 **읽기 전용**이다.
     에셋을 고치지 않는다. 보기용 시트만 만든다. 어긋난 것은 맞추는 게 아니라 **안 쓴다.**

   같은 바닥선에 세우고 규격 키(SPEC) 선을 그어 크기 어긋남이 눈에 들어오게 한다.
   출력: W24/_check/<캐릭터>.png · W24/_check/_groups.png   (로컬 전용 — 깃에 안 올린다)
   사용: python make_w24_consistency_sheet.py
"""
import glob
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

POSE_DIR = "assets/graphics/poses"
CUT_DIR = "W24/group_cuts"
OUT_DIR = "W24/_check"

# 사장님이 미리 정해 준 규격 키 — 이게 기준선이다 (build_w24.SPEC 과 동일)
SPEC = {"injun": 770, "zolla_man": 761, "teacher_jay": 749, "stickman": 749,
        "jieun": 706, "zolla_girl": 697, "madam_jay": 693}
KO = {"injun": "인준", "zolla_man": "졸라맨", "teacher_jay": "티쳐제이", "stickman": "스틱맨",
      "jieun": "지은", "zolla_girl": "졸라걸", "madam_jay": "마담제이"}

DISP = 300.0 / 770.0          # 보기 배율(규격 770 → 300px). 표시만 줄인다.
PAD, LBL, COLS = 26, 46, 8
FONT = "C:/Windows/Fonts/malgun.ttf"


def font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except Exception:
        return ImageFont.load_default()


def bbox_hw(im):
    """알파 내용의 실제 높이·너비 — 캔버스 여백이 아니라 그림 자체를 잰다."""
    b = im.getbbox() if im.mode == "RGBA" else None
    if not b:
        return im.height, im.width
    return b[3] - b[1], b[2] - b[0]


def head_feet(im):
    """★사장님 지시(2026-08-04): 키는 **머리끝~발끝**이다.
    의자·소품·들어 올린 물건은 키에 넣지 않는다.
    몸통이 서 있는 x 띠(하반신 무게중심 ±18%) 안에서만 위에서 아래로 훑어
    '머리'가 시작되는 줄을 찾는다 — 옆으로 뻗은 팔·들어 올린 물건은 이 띠 밖이라 걸리지 않는다.
    반환: (머리끝y, 발끝y) — 원본 이미지 좌표. 못 재면 None."""
    import numpy as np
    a = np.array(im.convert("RGBA"))[:, :, 3] > 40
    ys, xs = np.where(a)
    if len(ys) == 0:
        return None
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    h = y1 - y0 + 1
    low = a[y0 + int(h * 0.60):y1 + 1, :]              # 하반신 = 다리·발 (가장 안정적)
    lx = np.where(low.any(axis=0))[0]
    cx = int(lx.mean()) if len(lx) else (x0 + x1) // 2
    half = max(8, int((x1 - x0 + 1) * 0.18))           # 몸통 띠 반폭
    band = a[:, max(0, cx - half):cx + half + 1]
    rows = np.where(band.sum(axis=1) >= 3)[0]
    if len(rows) == 0:
        return int(y0), int(y1)
    # 머리 위 안테나(졸라맨 곱슬 한 올)에 걸리지 않게 8줄 연속으로 이어지는 첫 줄을 머리끝으로
    run, head = 0, rows[0]
    for r in rows:
        run = run + 1 if (r - head) <= run + 1 else 1
        head = r if run == 1 else head
        if run >= 8:
            break
    return int(head), int(y1)


def cell(im, name, spec_h, target=100.0):
    """포즈 한 칸 — ★키는 머리끝~발끝만. 의자·소품·들어 올린 물건은 안 센다.
    검출한 머리끝·발끝을 파란 선으로 그려 **측정 자체를 눈으로 검증**할 수 있게 한다.
    빨간선=규격 키(서기 100%) · 주황선=앉기 기준(60%)."""
    hf = head_feet(im)
    bb = im.getbbox() or (0, 0, im.width, im.height)
    ih = (hf[1] - hf[0] + 1) if hf else (bb[3] - bb[1])   # ★사람 키
    iw = bb[2] - bb[0]
    full_h = bb[3] - bb[1]                               # 그림 전체(소품 포함) — 표시용
    dh, dw = int(full_h * DISP), int(iw * DISP)
    cw = max(dw + PAD * 2, 165)
    chh = int(spec_h * DISP) + LBL + 46
    c = Image.new("RGBA", (cw, chh + LBL), (255, 255, 255, 255))
    d = ImageDraw.Draw(c)
    base_y = chh - 20                                    # 바닥선
    d.line([(0, base_y), (cw, base_y)], fill=(120, 120, 120), width=2)
    d.line([(0, base_y - int(spec_h * DISP)), (cw, base_y - int(spec_h * DISP))],
           fill=(220, 40, 40), width=2)                  # 서기 규격
    y60 = base_y - int(spec_h * (target / 100.0) * DISP)
    for x in range(0, cw, 12):                           # 앉기 기준 60% (점선)
        d.line([(x, y60), (x + 6, y60)], fill=(235, 140, 20), width=2)
    src = im.crop(bb)
    top_y = base_y - dh
    c.alpha_composite(src.resize((max(dw, 1), max(dh, 1))).convert("RGBA"),
                      ((cw - dw) // 2, top_y))
    if hf:                                               # 검출 결과를 그려서 검증 가능하게
        hy = top_y + int((hf[0] - bb[1]) * DISP)
        fy = top_y + int((hf[1] - bb[1]) * DISP)
        d.line([(0, hy), (cw, hy)], fill=(30, 90, 220), width=2)
        d.line([(0, fy), (cw, fy)], fill=(30, 90, 220), width=1)
    ratio = ih / spec_h * 100
    tgt = target
    off = ratio - tgt
    col = (200, 30, 30) if abs(off) >= 6 else (40, 120, 40)
    d.text((6, chh + 2), name[:24], font=font(13), fill=(20, 20, 20))
    d.text((6, chh + 20), f"{ih}px = 규격의 {ratio:.0f}% (목표 {tgt:.0f}%)",
           font=font(13), fill=col)
    return c, 0


def grid(cells, title, path):
    if not cells:
        return
    cw = max(c.width for c, _ in cells)
    chh = max(c.height for c, _ in cells)
    rows = (len(cells) + COLS - 1) // COLS
    W, H = cw * min(COLS, len(cells)), 54 + chh * rows
    sheet = Image.new("RGB", (W, H), (255, 255, 255))
    ImageDraw.Draw(sheet).text((14, 16), title, font=font(24), fill=(10, 10, 10))
    for i, (c, _t) in enumerate(cells):
        sheet.paste(c.convert("RGB"), ((i % COLS) * cw, 54 + (i // COLS) * chh))
    sheet.save(path)
    print(f"  {path}  ({W}x{H}, {len(cells)}칸)")


def pose_target(name):
    """★자세별 키 기준 (사장님 확정 2026-08-04) — 선 키 100% 대비 머리끝~발끝 목표 비율.
    서기 100 · 서서 약간 구부림 80 · 의자에 앉기 75 · 바닥에 웅크리고 앉기 50.
    (의자앉기는 60 으로 잡았다가 실제로 그려 보니 아이처럼 작아 보여 2026-08-04 사장님이 75 로 확정)
    물건을 높이 들고 서 있어도 키는 머리~발끝만 재므로 100 이다."""
    n = name.lower()
    if any(k in n for k in ("crouch", "squat", "floor_sit", "kneel", "웅크")):
        return 50.0
    if "sit" in n:
        return 75.0
    if any(k in n for k in ("bend", "lean", "bow", "stoop")):
        return 80.0
    return 100.0


def split_chars(im):
    """그룹 컷 한 장에 2~3명이 들어있다 → 세로로 빈 열(간격)에서 갈라 인물별로 나눈다.
    자르는 게 아니라 **재기 위해** 나누는 것이다(원본 파일은 건드리지 않는다)."""
    import numpy as np
    a = np.array(im)[:, :, 3] > 40
    colw = a.sum(axis=0)
    gap = colw == 0
    parts, s = [], None
    for x in range(len(colw)):
        if not gap[x] and s is None:
            s = x
        elif gap[x] and s is not None:
            if x - s > 40:                              # 너무 좁은 조각(그림자·소품)은 버린다
                parts.append(im.crop((s, 0, x, im.height)))
            s = None
    if s is not None and len(colw) - s > 40:
        parts.append(im.crop((s, 0, len(colw), im.height)))
    return [p for p in parts if p.getbbox() and head_feet(p)] or [im]


def char_of(stem):
    """w24_<charkey>_<pose> → 가장 긴 캐릭터 키로 가른다(zolla_man 등 밑줄 포함)."""
    for k in sorted(SPEC, key=len, reverse=True):
        if stem.startswith(k + "_"):
            return k, stem[len(k) + 1:]
    return None, stem


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=== W24 에셋 일관성 증명시트 (읽기 전용) ===")
    byc = {}
    for p in sorted(glob.glob(f"{POSE_DIR}/w24_*.png")):
        ch, pose = char_of(os.path.basename(p)[4:-4])
        if ch:
            byc.setdefault(ch, []).append((pose, p))
    for ch in sorted(byc, key=lambda c: -SPEC[c]):
        cells = [cell(Image.open(p).convert("RGBA"), pose, SPEC[ch], target=pose_target(pose))
                 for pose, p in byc[ch]]
        grid(cells, f"{KO[ch]} ({ch}) — 규격 {SPEC[ch]}px · 키=머리끝~발끝(파란선) · "
                    f"빨강=서기100% · 주황점선=이 자세의 목표", f"{OUT_DIR}/{ch}.png")

    # 그룹 통짜 컷 — 인물별로 갈라서 각각 잰다(한 장에 2~3명이 들어있다)
    cells = []
    for d in sorted(os.listdir(CUT_DIR)):
        fs = sorted(glob.glob(f"{CUT_DIR}/{d}/*.png"))
        if not fs:
            continue
        im = Image.open(fs[0]).convert("RGBA")
        parts = split_chars(im)
        base = max((head_feet(p)[1] - head_feet(p)[0] + 1) for p in parts) if parts else 1
        for i, p in enumerate(parts):
            cells.append(cell(p, f"{d} #{i + 1}", base, target=pose_target(d)))
    grid(cells, "그룹 통짜 컷 — 인물별 키(머리끝~발끝) · 규격=그 컷에서 가장 큰 인물 · "
                "빨강=100% · 주황점선=이 자세의 목표", f"{OUT_DIR}/_groups.png")


if __name__ == "__main__":
    main()
