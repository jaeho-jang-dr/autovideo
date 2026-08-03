# -*- coding: utf-8 -*-
"""컷아웃 프레임의 운동화를 양쪽 다 흰색으로 통일한다 (2026-07-27, 사장님 지시).

Veo 클립을 프레임컷으로 뜨면 공중 동작 구간에서 운동화가 회색(RGB 120~200)으로 렌더돼
지상 컷의 흰 운동화(RGB 240+)와 색이 어긋난다. 여기서 하는 일:

  1. 무채색(채도<0.16) + 외곽선보다 밝은(V>0.30) 픽셀을 후보로 잡는다
  2. 연결요소 중 **몸(바지/살색 등 유채색 픽셀)에 붙어 있는 것만** 운동화로 인정한다
     → 공중에 떠 있는 모션 스트리크(속도선)는 건드리지 않는다
  3. 운동화 픽셀의 명도를 흰색 쪽으로 리매핑(V -> 0.88~1.0)하고 채도를 죽인다
     → 음영 계조는 남기고 색만 흰색으로

사용:
  python whiten_shoes.py "W23/poses/injun_w23_windmill_up_*.png"          # 실제 적용(원본은 _orig_backup/)
  python whiten_shoes.py "<glob>" --preview scratch/shoe_preview          # 적용 전 비교 이미지만
"""
import argparse
import glob
import os
import shutil

import numpy as np
from PIL import Image
from scipy import ndimage

SAT_MAX = 0.16      # 무채색 판정
V_MIN = 0.30        # 검정 외곽선은 건드리지 않는다
BODY_SAT = 0.20     # 몸(유채색) 판정
V_LO, V_HI = 0.88, 1.0   # 흰색 리매핑 목표 명도대


def hsv_parts(rgb):
    mx = rgb.max(2).astype(np.float32)
    mn = rgb.min(2).astype(np.float32)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    return sat, mx / 255.0


def whiten(path):
    """운동화 픽셀을 흰색으로. (수정된 RGBA 배열, 바뀐 픽셀 수) 반환."""
    im = np.array(Image.open(path).convert("RGBA"))
    rgb = im[..., :3].astype(np.float32)
    solid = im[..., 3] > 128
    sat, v = hsv_parts(rgb)

    # ★알파 경계의 반투명 안티에일리어싱 픽셀은 채도가 낮아 회색으로 잡힌다 → 바지 테두리가
    #   갉히는 사고가 난다(2026-07-27 실측). 경계에서 3px 안쪽만 후보로 본다.
    inner = ndimage.binary_erosion(solid, iterations=3)
    gray = inner & (sat < SAT_MAX) & (v > V_MIN)
    body = solid & (sat >= BODY_SAT) & (v > 0.25)
    if not gray.any() or not body.any():
        return im, 0

    lab, n = ndimage.label(gray)
    # 몸에 붙은(=1px 팽창 시 겹치는) 연결요소만 운동화로 인정
    touch = ndimage.binary_dilation(body, iterations=2) & gray
    ids = np.unique(lab[touch])
    ids = ids[ids > 0]
    if len(ids) == 0:
        return im, 0
    shoe = np.isin(lab, ids) & gray
    # 아주 작은 파편(안티에일리어싱 잔여)은 제외
    lab2, n2 = ndimage.label(shoe)
    if n2:
        sizes = ndimage.sum(shoe, lab2, range(1, n2 + 1))
        keep = np.isin(lab2, np.where(sizes >= 120)[0] + 1)
        shoe &= keep
    if not shoe.any():
        return im, 0

    sv = v[shoe]
    lo, hi = np.percentile(sv, 3), np.percentile(sv, 97)
    if hi - lo < 0.02:
        newv = np.full_like(sv, V_HI)
    else:
        newv = V_LO + (np.clip(sv, lo, hi) - lo) / (hi - lo) * (V_HI - V_LO)
    val = np.clip(newv * 255.0, 0, 255)
    for c in range(3):
        ch = im[..., c].astype(np.float32)
        ch[shoe] = val                      # 채도 제거 = 3채널 동일값 → 순백 계열
        im[..., c] = np.clip(ch, 0, 255).astype(np.uint8)
    return im, int(shoe.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern")
    ap.add_argument("--preview", help="적용 대신 before/after 비교 PNG를 이 폴더에 쓴다")
    ap.add_argument("--backup", default="_orig_backup")
    a = ap.parse_args()

    files = sorted(glob.glob(a.pattern), key=lambda p: (len(p), p))
    if not files:
        raise SystemExit(f"대상 없음: {a.pattern}")
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)

    total = 0
    for p in files:
        out, cnt = whiten(p)
        total += 1 if cnt else 0
        if a.preview:
            before = Image.open(p).convert("RGBA")
            bb = Image.new("RGBA", before.size, (255, 255, 255, 255)); bb.alpha_composite(before)
            aa = Image.new("RGBA", before.size, (255, 255, 255, 255)); aa.alpha_composite(Image.fromarray(out))
            cmp = Image.new("RGB", (before.width * 2, before.height), (255, 255, 255))
            cmp.paste(bb.convert("RGB"), (0, 0)); cmp.paste(aa.convert("RGB"), (before.width, 0))
            cmp.save(os.path.join(a.preview, os.path.basename(p)))
        else:
            bdir = os.path.join(os.path.dirname(p), a.backup)
            os.makedirs(bdir, exist_ok=True)
            bpath = os.path.join(bdir, os.path.basename(p))
            if not os.path.exists(bpath):
                shutil.copy2(p, bpath)
            Image.fromarray(out).save(p)
        print(f"  {os.path.basename(p):40s} 운동화픽셀 {cnt:6d}")
    print(f"\n{'미리보기' if a.preview else '적용'} 완료 — {len(files)}개 중 {total}개에서 운동화 검출")


if __name__ == "__main__":
    main()
