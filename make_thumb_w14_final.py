# -*- coding: utf-8 -*-
"""W14 썸네일 — 하루 일과 / 협재해수욕장 / 마담제이.
★매회 디자인 다르게(메모리 지침): W13은 왼쪽 세로 텍스트 블록이었으니
   W14는 '아침→밤' 하루의 흐름을 보여주는 **상단 가로 배너 + 중앙 큰 훅 + 하단 표현 스트립** 구성.
KO/EN 두 판. 1280x720 <2MB.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"


def outline(d, xy, txt, font, fill, oc=(20, 20, 20, 255), ow=8):
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            d.text((x + dx, y + dy), txt, font=font, fill=oc)
    d.text((x, y), txt, font=font, fill=fill)


def taegukgi(d, cx, cy, R):
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=3)
    d.pieslice([cx-R, cy-R, cx+R, cy+R], 180, 360, fill=(205, 40, 50, 255))
    d.pieslice([cx-R, cy-R, cx+R, cy+R], 0, 180, fill=(30, 80, 170, 255))
    rr = R / 2
    d.ellipse([cx-R, cy-rr, cx, cy+rr], fill=(205, 40, 50, 255))
    d.ellipse([cx, cy-rr, cx+R, cy+rr], fill=(30, 80, 170, 255))


def build(lang):
    # 배경: 협재 해변(야자수가 캐릭터를 가리지 않는 컷)
    bg = Image.open("assets/graphics/bg/bg_w14_sunset_beach.png").convert("RGBA")
    r = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * r), int(bg.height * r)))
    bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H))
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(bg, (0, 0))

    # 중앙~왼쪽 밝은 베일(글자 가독성)
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    for x in range(880):
        vd.line([(x, 0), (x, H)], fill=(255, 255, 255, int(120 * (1 - x / 880))))
    canvas = Image.alpha_composite(canvas, veil)

    # 캐릭터: 마담제이 인사(오른쪽) — 하루를 소개하는 느낌
    mj = Image.open("assets/graphics/poses/mj_w14_smile_big.png").convert("RGBA")
    a = np.array(mj)
    ys, xs = np.where(a[:, :, 3] > 25)
    mj = mj.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    mh = 660
    mw = int(mj.width * mh / mj.height)
    mj = mj.resize((mw, mh))
    canvas.alpha_composite(mj, (W - mw - 40, H - mh + 4))

    d = ImageDraw.Draw(canvas)

    # ① LEARN KOREAN 배너(상단 좌)
    f_ban = ImageFont.truetype(MALGUN, 58)
    bx, by = 38, 30
    btxt = "LEARN KOREAN"
    tw = d.textbbox((0, 0), btxt, font=f_ban)[2]
    d.rounded_rectangle([bx, by, bx + tw + 142, by + 86], radius=18,
                        fill=(211, 47, 47, 255), outline=(255, 255, 255, 255), width=5)
    taegukgi(d, bx + 54, by + 43, 32)
    d.text((bx + 100, by + 11), btxt, font=f_ban, fill=(255, 255, 255, 255))

    # ② 토픽 칩
    topic = "나의 하루 일과 · DAILY ROUTINE" if lang == "ko" else "MY DAILY ROUTINE IN KOREAN"
    outline(d, (44, 140), topic, ImageFont.truetype(MALGUN, 42), (255, 255, 255, 255), ow=5)

    # ③ 큰 한글 훅 — 하루의 시작과 끝 (2줄, W13의 1줄과 다르게)
    f_hook = ImageFont.truetype(MALGUN, 118)
    outline(d, (42, 198), "일어나요", f_hook, (255, 224, 66, 255), ow=10)
    outline(d, (42, 322), "자요", f_hook, (130, 220, 255, 255), ow=10)
    # 아침→밤 화살표: '자요' 글자 오른쪽 여백에(겹치지 않게). 도형이라 폰트 무관.
    ax, ay = 300, 388
    d.line([(ax, ay), (ax + 84, ay)], fill=(20, 20, 20, 255), width=16)
    d.line([(ax, ay), (ax + 84, ay)], fill=(255, 255, 255, 255), width=8)
    d.polygon([(ax + 120, ay), (ax + 80, ay - 26), (ax + 80, ay + 26)],
              fill=(255, 255, 255, 255), outline=(20, 20, 20, 255))
    # 화살표 끝에 달/별(밤) 아이콘 — '자요'가 밤이라는 뜻 전달
    mx, my = ax + 168, ay
    d.ellipse([mx - 30, my - 30, mx + 30, my + 30], fill=(255, 236, 140, 255), outline=(20, 20, 20, 255), width=4)
    d.ellipse([mx - 12, my - 34, mx + 34, my + 22], fill=(255, 255, 255, 0))

    # ④ 뜻
    mean = '= "Wake up → Sleep"' if lang == "en" else '= 아침부터 밤까지'
    outline(d, (48, 462), mean, ImageFont.truetype(MALGUN, 48), (255, 255, 255, 255), ow=6)

    # ⑤ 표현 스트립 — 하루 동작들 (·이 안 나오는 동동체 대신 맑은고딕 사용)
    strip = "세수 · 밥 · 일 · 공부 · 산책 · 잠" if lang == "ko" else "wash · eat · work · study · sleep"
    outline(d, (48, 552), strip, ImageFont.truetype(MALGUN, 42), (255, 255, 255, 255), ow=5)

    # 장소(우하단)
    place = "협재해수욕장 · 제주" if lang == "ko" else "Hyeopjae Beach · Jeju"
    outline(d, (W - 430, H - 46), place, ImageFont.truetype(MALGUN, 30), (255, 255, 255, 255), ow=4)

    out = f"hangeul_birth_vowels/thumb_w14_{lang}_1280x720.jpg"
    canvas.convert("RGB").save(out, quality=90)
    print(f"썸네일({lang}): {out}  {os.path.getsize(out)//1024}KB")
    return out


if __name__ == "__main__":
    build("ko")
    build("en")
