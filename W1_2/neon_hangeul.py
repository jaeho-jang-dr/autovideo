# -*- coding: utf-8 -*-
"""파라메트릭 획을 **네온으로** 밝힌다.

★사장님 물음(2026-08-14) "우리 파라메트릭 엔진에도 네온이 되나?"

된다. `hangeul_write.render_syllable(글자, 크기, progress)` 가 내주는 것은
**획 모양이 담긴 알파**다. 색이 아니라 모양이므로, 그 알파만 가지고 이렇게 쌓으면
네온이 된다.

  ① 바깥 번짐  — 알파를 크게 흐려서 색을 진하게      (halo)
  ② 중간 번짐  — 조금 흐려서 밝게                    (glow)
  ③ 심지       — 흐리지 않은 알파를 거의 흰색으로     (core)

진짜 네온관도 유리관 속 흰 빛 + 바깥으로 퍼지는 색이라, 이 세 겹이면 그대로 읽힌다.
획순(progress)은 그대로 살아 있어서 **획이 하나씩 켜지듯** 그릴 수 있다.

    python W1_2/neon_hangeul.py            # 견본 시트
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import hangeul_write as HW                                  # noqa: E402

# (심지, 안쪽 번짐, 바깥 번짐) — 물빛
WATER = ((255, 255, 255), (150, 235, 255), (30, 130, 255))
PINK = ((255, 255, 255), (255, 190, 235), (230, 40, 170))


def neon(alpha, color=WATER, r1=6, r2=22, gain=1.0):
    """획 알파 한 장 → 네온 RGBA."""
    a = Image.fromarray(alpha, "L")
    core = np.asarray(a, np.float32) / 255.0
    mid = np.asarray(a.filter(ImageFilter.GaussianBlur(r1)), np.float32) / 255.0
    out = np.asarray(a.filter(ImageFilter.GaussianBlur(r2)), np.float32) / 255.0
    c0, c1, c2 = (np.array(c, np.float32) for c in color)

    rgb = np.zeros(core.shape + (3,), np.float32)
    acc = np.zeros_like(core)
    for m, c, w in ((out, c2, 1.35), (mid, c1, 1.5), (core, c0, 1.0)):
        v = np.clip(m * w * gain, 0, 1)[:, :, None]
        rgb = rgb * (1 - v) + c[None, None, :] * v          # 위로 갈수록 밝게 덮는다
        acc = np.maximum(acc, np.clip(m * w * gain, 0, 1))
    return Image.fromarray(
        np.dstack([rgb.astype(np.uint8), (acc * 255).astype(np.uint8)]), "RGBA")


def neon_syllable(syl, size_px, progress=1.0, color=WATER, gain=1.0):
    im = HW.render_syllable(syl, size_px, progress)
    return neon(np.asarray(im)[:, :, 3], color, max(3, size_px // 60),
                max(10, size_px // 18), gain)


def main():
    S = 300
    cols = [("ㄱ", 1.0), ("ㅏ", 1.0), ("ㅇ", 1.0), ("가", 0.34), ("가", 0.7), ("가", 1.0)]
    W = S * len(cols)
    sheet = Image.new("RGB", (W, S + 46), (10, 12, 20))
    from PIL import ImageDraw, ImageFont
    F = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 22)
    d = ImageDraw.Draw(sheet)
    for i, (ch, pr) in enumerate(cols):
        n = neon_syllable(ch, S, pr, WATER if i < 3 else PINK)
        sheet.paste(n, (i * S, 40), n)
        d.text((i * S + S // 2, 10), "%s  획 %d%%" % (ch, round(pr * 100)),
               fill=(210, 220, 235), font=F, anchor="ma")
    out = "W1_2/_check/neon_try.png"
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
