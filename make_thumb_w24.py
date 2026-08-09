# -*- coding: utf-8 -*-
"""W24 썸네일 — 종합 진단과 수료(DDP). 24주 총화판.

★매회 다른 디자인 원칙:
   W21 상단 타이틀+하단 3알약 / W22 좌캐릭터+우 2단카드 / W23 중앙 캐릭터+좌 제목+3버튼
   → W24 는 **완성 영상의 실제 씬**(7명 전원 착석)을 배경으로 쓰고,
     상단에 리본 배지("24주 수료"), 하단에 24주를 상징하는 진행 바를 얹는다.

  python make_thumb_w24.py            # 시안 4개 → hangeul_birth_vowels/_thumb_w24/
  python make_thumb_w24.py --pick 2   # 2번 시안을 확정본으로 저장(ko/en)
"""
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"
VIDEO = "hangeul_birth_vowels/hangeul_w24r_full_ko.mp4"
OUTDIR = "hangeul_birth_vowels/_thumb_w24"
# ★7명 전원이 **정면으로 기립**한 수료식 장면(본편 끝머리). 총화판 썸네일로 가장 맞다.
#   (교실 착석 씬은 전원 옆모습이라 밋밋했다 — 후보 프레임 비교 후 이걸로 정함)
FRAME_AT = 332.0

TITLE = {"ko": ("24주 한글 수료", "다 배운 것을 한자리에서"),
         "en": ("24 Weeks Complete", "Everything you learned, in one place")}
BADGE = {"ko": "총 · 정 · 리", "en": "FINAL REVIEW"}


def F(p, s):
    return ImageFont.truetype(p, s)


def outline(d, xy, txt, font, fill, oc=(20, 17, 14), ow=6):
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            d.text((x + dx, y + dy), txt, font=font, fill=oc)
    d.text((x, y), txt, font=font, fill=fill)


def fit(d, txt, path, maxw, start, floor=24):
    s = start
    while s > floor and d.textlength(txt, font=F(path, s)) > maxw:
        s -= 2
    return F(path, s)


def grab(at=FRAME_AT):
    os.makedirs(OUTDIR, exist_ok=True)
    p = os.path.join(OUTDIR, "_frame.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{at:.2f}", "-i", VIDEO,
                    "-frames:v", "1", "-vf", f"scale={W}:{H}", p], check=True)
    return Image.open(p).convert("RGBA")


def bar(base, lang, y, done=24, total=24):
    """24주 진행 바 — 다 채워진 상태."""
    d = ImageDraw.Draw(base)
    x0, x1 = 64, W - 64
    seg = (x1 - x0) / total
    for i in range(total):
        x = x0 + seg * i
        col = (74, 190, 140, 255) if i < done else (120, 120, 120, 160)
        d.rounded_rectangle([x + 3, y, x + seg - 3, y + 16], radius=6, fill=col)
    f = F(MALGUN, 24)
    t = "1주 → 24주 완주" if lang == "ko" else "Week 1 → 24  Complete"
    outline(d, (x0, y - 38), t, f, (255, 255, 255), ow=4)


def badge(base, lang, cx, cy):
    d = ImageDraw.Draw(base)
    f = F(MALGUN, 30)
    t = BADGE[lang]
    tw = d.textlength(t, font=f)
    pad = 22
    d.rounded_rectangle([cx - tw / 2 - pad, cy - 30, cx + tw / 2 + pad, cy + 30],
                        radius=30, fill=(228, 74, 58, 255))
    d.text((cx - tw / 2, cy - 19), t, font=f, fill=(255, 255, 255))


def scrim(base, mode):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    if mode == "top":
        # ★배경 프레임에 파라메트릭 한글('앞으로 계속')이 좌상단에 그려져 있다 → 확실히 덮는다
        d.rectangle([0, 0, W, 196], fill=(16, 14, 26, 226))
        for y in range(196, 330):
            d.rectangle([0, y, W, y + 1], fill=(16, 14, 26, int(226 * (1 - (y - 196) / 134))))
        for y in range(170):
            d.rectangle([0, H - y, W, H - y + 1], fill=(16, 14, 26, int(165 * (1 - y / 170))))
    else:                                              # 왼쪽 세로 + 좌상단 글자 가림
        for x in range(620):
            d.rectangle([x, 0, x + 1, H], fill=(16, 14, 26, int(185 * (1 - x / 620))))
        d.rectangle([0, 0, 700, 180], fill=(16, 14, 26, 200))
    base.alpha_composite(ov)


def build(lang, variant, frame):
    base = frame.copy()
    ko, sub = TITLE[lang]
    d = ImageDraw.Draw(base)

    if variant == 1:                                   # 상단 제목 + 하단 24주 바
        scrim(base, "top")
        d = ImageDraw.Draw(base)
        f1 = fit(d, ko, DONG, W - 130, 104)
        outline(d, (64, 40), ko, f1, (255, 226, 120), ow=7)
        f2 = fit(d, sub, MALGUN, W - 140, 40)
        outline(d, (68, 40 + f1.size + 14), sub, f2, (255, 255, 255), ow=5)
        badge(base, lang, W - 150, 62)
        bar(base, lang, H - 78)

    elif variant == 2:                                 # 왼쪽 세로 제목 + 하단 바
        scrim(base, "left")
        d = ImageDraw.Draw(base)
        f1 = fit(d, ko, DONG, 540, 96)
        outline(d, (56, 150), ko, f1, (255, 226, 120), ow=7)
        f2 = fit(d, sub, MALGUN, 520, 36)
        outline(d, (60, 150 + f1.size + 16), sub, f2, (255, 255, 255), ow=5)
        badge(base, lang, 190, 90)
        bar(base, lang, H - 78)

    elif variant == 3:                                 # 가운데 큰 제목(배지 없음)
        scrim(base, "top")
        d = ImageDraw.Draw(base)
        f1 = fit(d, ko, DONG, W - 120, 120)
        tw = d.textlength(ko, font=f1)
        outline(d, ((W - tw) / 2, 46), ko, f1, (255, 226, 120), ow=8)
        f2 = fit(d, sub, MALGUN, W - 200, 42)
        tw2 = d.textlength(sub, font=f2)
        outline(d, ((W - tw2) / 2, 46 + f1.size + 16), sub, f2, (255, 255, 255), ow=5)
        bar(base, lang, H - 70)

    else:                                              # 4: 카드형 — 제목 판때기
        scrim(base, "top")
        d = ImageDraw.Draw(base)
        card = Image.new("RGBA", (W - 120, 190), (250, 248, 242, 238))
        base.alpha_composite(card, (60, 44))
        d = ImageDraw.Draw(base)
        f1 = fit(d, ko, DONG, W - 200, 96)
        d.text((92, 62), ko, font=f1, fill=(32, 28, 24))
        f2 = fit(d, sub, MALGUN, W - 220, 38)
        d.text((96, 62 + f1.size + 12), sub, font=f2, fill=(120, 96, 40))
        badge(base, lang, W - 190, 268)
        bar(base, lang, H - 78)
    return base.convert("RGB")


def save(im, path):
    q = 92
    while q >= 60:
        im.save(path, quality=q, optimize=True)
        if os.path.getsize(path) < 2_000_000:
            return
        q -= 6


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    frame = grab()
    if "--pick" in sys.argv:
        v = int(sys.argv[sys.argv.index("--pick") + 1])
        for lang in ("ko", "en"):
            p = f"hangeul_birth_vowels/thumb_w24_{lang}_1280x720.jpg"
            save(build(lang, v, frame), p)
            print("확정 ->", p, f"{os.path.getsize(p)/1e6:.2f}MB")
        return
    for v in (1, 2, 3, 4):
        for lang in ("ko", "en"):
            p = os.path.join(OUTDIR, f"v{v}_{lang}.jpg")
            save(build(lang, v, frame), p)
            print("시안 ->", p)


if __name__ == "__main__":
    main()
