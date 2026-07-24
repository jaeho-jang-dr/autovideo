# -*- coding: utf-8 -*-
"""걷기 8컷(+왼쪽 8) 정수리 복원: 평평하게 잘린 머리 위에 머리색 돔(둥근 정수리)을 덧대고,
   talk 포즈와 같은 머리~발 키(770)로 재정합. ★재생성 없이 있는 컷 살림.
사용: python fix_walk_head.py test   (walk_r_0만 시험, 비교시트)
      python fix_walk_head.py apply  (16컷 전부 복원+정합)
"""
import sys, glob, os
import numpy as np
from PIL import Image

CW, CH, FEET_Y, TARGET = 1024, 1280, 1210, 770


def crown_pad(a):
    """a: RGBA (임의 캔버스). figure bbox로 크롭 후, 최상단이 평평(넓은폭)하면 머리 돔 덧댐. 크롭본 반환."""
    al = a[:, :, 3] > 0
    ys, xs = np.where(al)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    al = a[:, :, 3] > 0
    H, W = al.shape
    top_cols = np.where(al[0])[0]
    if len(top_cols) < W * 0.10:          # 최상단이 좁으면(둥근 정수리) 이미 정상 → 그대로
        return a
    x0, x1 = int(top_cols.min()), int(top_cols.max())
    span = x1 - x0
    dome_h = int(span * 0.55)             # 정수리 높이(측면 머리 비율)
    # 머리색 = 최상단 12행 중 알파 픽셀의 중앙값(갈색), 외곽선 = 가장 어두운 픽셀
    reg = a[0:12, x0:x1 + 1]
    m = reg[:, :, 3] > 0
    px = reg[m][:, :3].astype(int)
    fill = np.median(px, axis=0).astype(np.uint8)
    dark = px[(px.sum(1)).argmin()].astype(np.uint8) if len(px) else np.array([35, 30, 28], np.uint8)
    nb = np.zeros((H + dome_h, W, 4), np.uint8)
    nb[dome_h:] = a
    cx = (x0 + x1) / 2.0; rx = span / 2.0 + 2; ry = float(dome_h)
    yy, xx = np.mgrid[0:dome_h, 0:W]
    d2 = ((xx - cx) / rx) ** 2 + ((yy - dome_h) / ry) ** 2
    fillmask = d2 <= 1.0
    nb[:dome_h][fillmask] = [int(fill[0]), int(fill[1]), int(fill[2]), 255]
    outline = (d2 <= 1.0) & (d2 >= 0.80)   # 돔 테두리 = 외곽선
    nb[:dome_h][outline] = [int(dark[0]), int(dark[1]), int(dark[2]), 255]
    return nb


def normalize(a):
    """머리~발 bbox 높이를 TARGET로 스케일, 발끝 y=FEET_Y, 중앙 배치, 캔버스 CWxCH."""
    ys, xs = np.where(a[:, :, 3] > 0)
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = crop.shape[:2]
    sc = TARGET / h
    nw, nh = max(1, round(w * sc)), max(1, round(h * sc))
    im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)
    cv = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    cv.paste(im, (CW // 2 - nw // 2, FEET_Y - nh), im)
    return cv


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    if mode == "test":
        p = "assets/graphics/poses/jieun_w19_walk_r_0.png"
        a = np.array(Image.open(p).convert("RGBA"))
        before = a[:, :, 3] > 0
        ys, xs = np.where(before); bc = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        padded = crown_pad(a.copy())
        # 비교시트: 원본머리 vs 복원머리 (상단 40%)
        H = 320
        def topcrop(arr):
            im = Image.fromarray(arr); hh = int(im.height * 0.40)
            im = im.crop((0, 0, im.width, hh)); r = H / im.height
            return im.resize((int(im.width * r), H))
        ta = topcrop(bc); tb = topcrop(padded)
        conf = Image.open("scratch/w19_walk/diag/head_confident.png").convert("RGBA"); rc = H / conf.height
        tc = conf.resize((int(conf.width * rc), H))
        sh = Image.new("RGB", (ta.width + tb.width + tc.width + 40, H + 24), (240, 240, 240))
        from PIL import ImageDraw; d = ImageDraw.Draw(sh)
        x = 5
        for lbl, im in [("잘린 원본", ta), ("정수리 복원", tb), ("talk(참고)", tc)]:
            sh.paste(im, (x, 20), im); d.text((x, 3), lbl, fill=(180, 0, 0)); x += im.width + 15
        sh.save("scratch/w19_walk/diag/crown_test.png")
        print("시험 저장 → crown_test.png")
        return
    # apply: 16컷 전부
    n = 0
    for p in sorted(glob.glob("assets/graphics/poses/jieun_w19_walk_*.png")):
        a = np.array(Image.open(p).convert("RGBA"))
        padded = crown_pad(a)
        normalize(padded).save(p)
        n += 1
    print(f"정수리 복원 + 정합 완료: {n}컷 (머리~발 {TARGET}·발끝 y{FEET_Y})")


if __name__ == "__main__":
    main()
