# -*- coding: utf-8 -*-
"""
졸라맨 + 졸라녀 베이스 2장을 '변형 없이 그대로' 한 장에 나란히 합성.
- AI(Flow) 재생성은 캐릭터를 재해석/변형하므로 사용하지 않는다.
- 각 원본 PNG에서 인물 영역만 흰배경 기준으로 자동 크롭(trim) → 같은 키(높이)로 비율유지 스케일
  → 바닥 맞춰 적당한 간격으로 흰 캔버스에 paste. 픽셀은 원본 그대로(스케일만, 재그림 없음).

사용: python scratch/compose_zolla_pair.py
출력: home_vocab/zolla_pair_base.png  (표준 페어)
"""
import os
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, "home_vocab", "zollaman_base.png")
WOMAN = os.path.join(ROOT, "home_vocab", "zollanyeo_base.png")
OUT = os.path.join(ROOT, "home_vocab", "zolla_pair_base.png")


def trim(path, thr=20):
    """흰 배경과 다른 영역(인물)만 잘라낸다. 픽셀 변형 없음(crop만)."""
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg).convert("L").point(lambda x: 255 if x > thr else 0)
    bbox = diff.getbbox()
    return im.crop(bbox) if bbox else im


def main():
    a = trim(MAN)
    b = trim(WOMAN)
    print(f"crop  man={a.size}  woman={b.size}")

    # ★ 리사이즈 금지: 각 원본 픽셀을 100% 그대로 보존(crop만). 키 차이도 원본대로 유지.
    H = max(a.height, b.height)
    gap = round(H * 0.15)   # 두 사람 사이 간격
    pad = round(H * 0.12)   # 바깥 여백
    W = pad * 2 + a.width + gap + b.width
    Hc = H + pad * 2
    canvas = Image.new("RGB", (W, Hc), (255, 255, 255))
    # 바닥(발끝)을 같은 라인에 맞춰 paste — 보간/스케일 없음 = 무변형
    canvas.paste(a, (pad, pad + (H - a.height)))                  # 좌: 졸라맨
    canvas.paste(b, (pad + a.width + gap, pad + (H - b.height)))  # 우: 졸라녀
    canvas.save(OUT)
    print(f"[OK] 무변형 페어(리사이즈 없음) 저장: {canvas.size} -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
