# -*- coding: utf-8 -*-
"""W23 썸네일 — 정문 광장 배경 + 인준 + 오늘의 표현 큰 글씨 (2026-07-28).

★사장님 원칙: 썸네일은 매회 다르게. W22(전망대 야경·세로 2단)와 겹치지 않게
  이번엔 **가로 2단 + 달력 칸 모티프**로 간다. 1280x720, 2MB 미만.
출력: hangeul_birth_vowels/w23pkg/w23_thumb_ko.png / _en.png
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PKG = "hangeul_birth_vowels/w23pkg"
os.makedirs(PKG, exist_ok=True)
W, H = 1280, 720
BG = "assets/graphics/bg/bg_w23_gate_plaza.png"
POSE = "assets/graphics/poses/injun_w23_present_right.png"
FB = r"C:\Windows\Fonts\malgunbd.ttf"


def build(out, line1, line2, badge, sub):
    bg = Image.open(BG).convert("RGB")
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2,
                  (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    # 왼쪽에 글자가 앉을 자리를 밝게 눌러 준다(배경과 싸우지 않게).
    # ★세로 직선 경계가 보이면 싸구려로 보인다 → 오른쪽 200px 을 그라데이션으로 흘린다.
    import numpy as np
    a = np.zeros((H, W), dtype=float)
    a[:, :560] = 1.0
    a[:, 560:760] = np.linspace(1.0, 0.0, 200)[None, :]
    veil = Image.fromarray(
        np.dstack([np.full((H, W), 255), np.full((H, W), 252), np.full((H, W), 244),
                   (a * 208)]).astype("uint8"), "RGBA")
    bg = Image.alpha_composite(bg.convert("RGBA"), veil)

    # 캐릭터 — 오른쪽, 글자 쪽(왼쪽=중앙)을 향하도록 present_right 그대로
    ch = Image.open(POSE).convert("RGBA")
    k = 690 / 770                                     # 몸높이 770 → 690px
    ch = ch.resize((round(ch.width * k), round(ch.height * k)), Image.LANCZOS)
    bg.alpha_composite(ch, (W - 470 - round(512 * k), H - round(1209 * k) - 8))

    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(FB, 118)
    f2 = ImageFont.truetype(FB, 92)
    f3 = ImageFont.truetype(FB, 40)
    f4 = ImageFont.truetype(FB, 34)

    def shadow(xy, txt, font, fill, off=5):
        d.text((xy[0] + off, xy[1] + off), txt, font=font, fill=(0, 0, 0, 70))
        d.text(xy, txt, font=font, fill=fill)

    shadow((56, 150), line1, f1, (28, 40, 90))
    shadow((56, 292), line2, f2, (206, 74, 40))
    # 달력 칸 모티프 — 표현 아래 3칸(약속 → 조율 → 확정)
    x0, y0 = 60, 440
    for i, t in enumerate(badge):
        bx = x0 + i * 214
        d.rounded_rectangle((bx, y0, bx + 196, y0 + 92), radius=16,
                            fill=(255, 255, 255, 235), outline=(60, 80, 140), width=4)
        tw = d.textlength(t, font=f4)
        d.text((bx + (196 - tw) / 2, y0 + 26), t, font=f4, fill=(40, 55, 110))
    shadow((60, 566), sub, f3, (70, 80, 100), 3)
    d.text((W - 168, 26), "W23", font=ImageFont.truetype(FB, 46), fill=(255, 255, 255))

    bg.convert("RGB").save(out, quality=92)
    print(f"{out}  {os.path.getsize(out)//1024}KB  {Image.open(out).size}")


build(f"{PKG}/w23_thumb_ko.png", "약속을 잡다", "시간 조율",
      ["약속", "조율", "확정"], "여러 사람과 만날 날 정하기")
build(f"{PKG}/w23_thumb_en.png", "약속을 잡다", "Making Plans",
      ["Ask", "Adjust", "Confirm"], "Set up a meetup in Korean")
