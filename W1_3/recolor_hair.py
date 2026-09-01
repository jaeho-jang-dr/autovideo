# -*- coding: utf-8 -*-
"""임시 보정 — 신규 졸라걸 동작 10종(zgirl_walk_side 등)이 검은 머리로 잘못
생성됐다(기존 확정 캐릭터는 주황 머리, `w12_zgirl_attention.png` 등 참고).
캐릭터 원본 재생성은 캐릭터랑/컷랑 몫이지만, 오늘 초안 렌더가 장면마다 머리색이
바뀌어 보이는 걸 막기 위해 **되돌릴 수 있는 렌더용 보정 사본**만 만든다
(DB의 file_path·원본 PNG는 건드리지 않는다 — 새 폴더에 사본만 저장).

방법: 머리 부위(이미지 상단)에서 "두꺼운 검은 덩어리"(칠 영역)만 골라 주황으로
바꾸고, 얇은 선(윤곽선)은 검은 채로 남긴다 — 기존 주황머리 자산의 그림체(주황
채우기 + 검은 윤곽선)를 그대로 흉내낸다. 몸통·팔다리의 검은 윤곽선은 상단 크롭
밖이라 건드리지 않는다.

사용법:
    python W1_3/recolor_hair.py --preview   # 프레임 1장만 보정해서 미리보기 저장
    python W1_3/recolor_hair.py             # 385장 전체 보정 사본 생성
"""
import os
import sys
import glob
import numpy as np
from PIL import Image
from scipy import ndimage

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HAIR_RGB = (237, 135, 63)   # 기존 확정 주황 머리색 실측값(w12_zgirl_attention.png)
DARK_THRESH = 70            # 이 값 미만이면 "검다"
ERODE_PX = 4                # 이만큼 깎아내야 "선"이 아니라 "칠"로 본다(눈과 맞닿은 머리술도 끊어낸다)
HAIR_ZONE_FRAC = 0.30       # 인물 bbox 세로 30% 안쪽만 머리 취급 대상

SRC_DIRS = [
    "W1_2/motion6_stride/zgirl_walk_side",
    "W1_2/motion6_stride/zgirl_walk_front",
    "W1_2/motion6_stride/zgirl_run_front",
    "W1_2/motion6_stride/zgirl_walk_back",
    "W1_2/motion6_stride/zgirl_run_back",
    "W1_2/motion6_stride/zgirl_stone_hop",
    "W1_2/motion6_cuts/zgirl_block_touch",
    "W1_2/motion6_cuts/zgirl_stumble_bounce",
    "W1_2/motion6_cuts/zgirl_cold_flinch",
    "W1_2/motion6_cuts/zgirl_clap_together",
]


MIN_BLOB_FRAC = 0.035  # 그 프레임 "머리존" 잉크 총량의 이 비율보다 작은 덩어리는 눈동자/입선
MIN_BLOB_FLOOR = 40    # 절대 하한(px) — 캔버스가 작아도 이보다 작게는 안 잡는다


def recolor(im):
    """im: PIL RGBA. 반환: 머리 보정된 RGBA 사본.

    눈동자·입선도 "두꺼운 검은 덩어리"라 침식만으로는 못 가른다 — 머리 타래는
    수천 px, 눈동자·입선은 수십 px이므로 **연결 성분 면적**으로 가른다.
    """
    a = np.array(im.convert("RGBA")).astype(np.uint8)
    alpha = a[:, :, 3]
    ys, xs = np.where(alpha > 20)
    if len(ys) == 0:
        return im
    y0, y1 = int(ys.min()), int(ys.max())
    zone_y1 = y0 + int((y1 - y0) * HAIR_ZONE_FRAC)

    rgb = a[:, :, :3].astype(int)
    dark = (rgb.max(axis=2) < DARK_THRESH) & (alpha > 20)
    zone_mask = np.zeros_like(dark)
    zone_mask[y0:zone_y1 + 1, :] = True
    dark_in_zone = dark & zone_mask

    total_ink = int(dark_in_zone.sum())
    min_area = max(MIN_BLOB_FLOOR, MIN_BLOB_FRAC * total_ink)

    # 눈동자·입선 보호 — 침식 전 원본 덩어리 기준으로 "원래도 작았던" 자리는
    # 나중에 머리 덩어리와 이어 붙어도 절대 칠하지 않는다(벨트 앤 서스펜더즈).
    orig_labels, n_orig = ndimage.label(dark_in_zone)
    protect = np.zeros_like(dark_in_zone)
    if n_orig:
        orig_areas = ndimage.sum(np.ones_like(orig_labels), orig_labels, index=np.arange(1, n_orig + 1))
        small_ids = [i for i, ar in enumerate(orig_areas, start=1) if ar < min_area]
        if small_ids:
            protect = np.isin(orig_labels, small_ids)

    # 얇은 윤곽선(머리 가장자리 선)까지 칠하면 경계가 사라지므로 살짝 침식해
    # "칠 영역"만 골라내되, 눈동자·입선처럼 원래 작은 덩어리는 면적으로 제외한다.
    eroded = ndimage.binary_erosion(dark_in_zone, iterations=ERODE_PX)
    labels, n = ndimage.label(eroded)
    if n:
        areas = ndimage.sum(np.ones_like(labels), labels, index=np.arange(1, n + 1))
        big_ids = set(int(i) for i, ar in enumerate(areas, start=1) if ar >= min_area)
        big_mask = np.isin(labels, list(big_ids)) if big_ids else np.zeros_like(eroded)
    else:
        big_mask = eroded

    fill = ndimage.binary_dilation(big_mask, iterations=ERODE_PX) & ~protect
    # 원래 눈동자/입선 자리는 큰 덩어리가 아니므로(또는 protect 로) 검은 채로 남는다.

    out = a.copy()
    out[fill, 0] = HAIR_RGB[0]
    out[fill, 1] = HAIR_RGB[1]
    out[fill, 2] = HAIR_RGB[2]
    return Image.fromarray(out, "RGBA")


def out_path(src_path):
    rel = os.path.relpath(src_path, REPO_ROOT).replace("\\", "/")
    parts = rel.split("/")
    # W1_2/motion6_stride/zgirl_walk_side/xxx.png -> W1_2/motion6_stride_recolored/zgirl_walk_side/xxx.png
    parts[1] = parts[1] + "_recolored"
    return os.path.join(REPO_ROOT, *parts)


def main():
    preview = "--preview" in sys.argv
    total = 0
    for rel_dir in SRC_DIRS:
        abs_dir = os.path.join(REPO_ROOT, rel_dir.replace("/", os.sep))
        pngs = sorted(glob.glob(os.path.join(abs_dir, "*.png")))
        if preview:
            pngs = pngs[:1]
        for p in pngs:
            im = Image.open(p)
            fixed = recolor(im)
            op = out_path(p)
            if preview:
                op = os.path.join(REPO_ROOT, "W1_3", "_preview", "recolor_" + os.path.basename(p))
            os.makedirs(os.path.dirname(op), exist_ok=True)
            fixed.save(op)
            total += 1
            if preview:
                print("preview ->", op)
        if not preview:
            print("%-45s %3d장 보정 완료" % (rel_dir, len(pngs)))
    print("\n총", total, "장", ("(미리보기)" if preview else "(전체 보정 사본 완료)"))


if __name__ == "__main__":
    main()
