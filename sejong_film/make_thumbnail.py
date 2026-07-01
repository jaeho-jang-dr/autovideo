# -*- coding: utf-8 -*-
"""세종대왕과 한글 — 유튜브 썸네일 합성 (애니 히어로 + 제목 텍스트 + 우하단 로고).
한글 폰트는 malgunbd(깨짐 방지), 로고는 우하단(Veo 워터마크 부위 덮기)."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
HERO = os.path.join(ROOT, "thumb_hero.png")
LOGO = os.path.abspath(os.path.join(ROOT, "..", "assets", "drjay_ed_logo_circle.png"))
MALGUN_BD = r"C:\Windows\Fonts\malgunbd.ttf"
MALGUN = r"C:\Windows\Fonts\malgun.ttf"

VARIANTS = {
    "ko": {"title": ["세종대왕과", "한글"], "accent": "한글",
            "hook": "스물여덟 자에 담긴 애민의 비밀", "out": "thumbnail_ko.png"},
    "en": {"title": ["KING SEJONG", "& HANGEUL"], "accent": "HANGEUL",
            "hook": "The Birth of an Alphabet for the People", "out": "thumbnail_en.png"},
}
GOLD = (245, 200, 75)
WHITE = (255, 255, 255)
OUTLINE = (20, 25, 45)

def draw_text_outlined(d, xy, text, font, fill, outline=OUTLINE, ow=6):
    x, y = xy
    d.text((x, y), text, font=font, fill=fill, stroke_width=ow, stroke_fill=outline)

def build(variant, cfg):
    img = Image.open(HERO).convert("RGBA")
    W, H = img.size
    d = ImageDraw.Draw(img)
    # left title block — keep within left ~50% so it never overlaps the letters/figure
    margin = int(W * 0.045)
    maxw = int(W * 0.50) - margin
    title_sz = int(H * 0.135)
    # shrink title until the WIDEST line fits maxw (prevents overlap, e.g. long EN words)
    while title_sz > int(H * 0.07):
        f_try = ImageFont.truetype(MALGUN_BD, title_sz)
        widest = max(d.textlength(ln, font=f_try) for ln in cfg["title"])
        if widest <= maxw:
            break
        title_sz -= 4
    hook_sz = int(title_sz * 0.40)
    f_title = ImageFont.truetype(MALGUN_BD, title_sz)
    f_hook = ImageFont.truetype(MALGUN_BD, hook_sz)
    y = int(H * 0.14)
    for line in cfg["title"]:
        fill = GOLD if line.strip() == cfg["accent"] else WHITE
        draw_text_outlined(d, (margin, y), line, f_title, fill, ow=max(6, title_sz // 16))
        y += int(title_sz * 1.06)
    # hook line under title
    y += int(H * 0.02)
    draw_text_outlined(d, (margin, y), cfg["hook"], f_hook, WHITE, ow=max(4, hook_sz // 12))
    # logo bottom-right (watermark area)
    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert("RGBA")
        ls = int(H * 0.17)
        logo = logo.resize((ls, ls), Image.LANCZOS)
        lx, ly = W - ls - int(W * 0.02), H - ls - int(H * 0.03)
        img.alpha_composite(logo, (lx, ly))
    out = os.path.join(ROOT, cfg["out"])
    img.convert("RGB").save(out, quality=92)
    print(f"[OK] {variant} -> {out} ({W}x{H})")

if __name__ == "__main__":
    if not os.path.exists(HERO):
        raise SystemExit("히어로 이미지 없음: " + HERO)
    for v, c in VARIANTS.items():
        build(v, c)
