# -*- coding: utf-8 -*-
"""W23 키 통일 증명시트 — 정지 포즈(정규화본)와 동영상 프레임컷을 같은 기준선 위에 올린다.

빨강 = 발끝 바닥선(y=1208) · 초록 = 서기 키 기준선(발끝-770).
정지 포즈 16 + 프레임컷 대표 8종을 한 장에. 출력: scratch/injun_w23_uniformity.png
"""
import glob
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
STILL = "W23/poses_still_norm"
CUTS = "W23/poses"
BOTTOM, STAND_H = 1208, 770
OUT = "scratch/injun_w23_uniformity.png"

CUT_REFS = ["walk_r_0", "walk_l_0", "board_write_0", "greet_wave_0", "check_ok_0",
            "spin_phone_0", "catch_petal_0", "point_far_follow_0"]


def cells():
    out = []
    for p in sorted(glob.glob(f"{STILL}/injun_w23_*.png")):
        out.append((os.path.basename(p).replace("injun_w23_", "")[:-4], p, "정지"))
    for k in CUT_REFS:
        p = f"{CUTS}/injun_w23_{k}.png"
        if os.path.exists(p):
            out.append((k, p, "컷"))
    return out


def main():
    rows = cells()
    cols, tw, th = 8, 230, 300
    rws = (len(rows) + cols - 1) // cols
    sh = Image.new("RGB", (cols * tw, rws * th + 56), (250, 249, 245))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 13)
    fb = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 20)
    d.text((14, 16), f"W23 인준 키 통일 증명 — 정지 {sum(1 for r in rows if r[2]=='정지')}종 + "
                     f"프레임컷 {sum(1 for r in rows if r[2]=='컷')}종 · 키 {STAND_H}px · 발끝 y{BOTTOM} "
                     f"(빨강=바닥선, 초록=키 기준선)", font=fb, fill=(28, 28, 28))
    for i, (key, path, kind) in enumerate(rows):
        cx, cy = (i % cols) * tw, (i // cols) * th + 56
        im = Image.open(path).convert("RGBA")
        sc = min(tw / im.width, (th - 22) / im.height)
        iw, ih = int(im.width * sc), int(im.height * sc)
        cell = Image.new("RGBA", (tw, th), (255, 255, 255, 255))
        cell.alpha_composite(im.resize((iw, ih), Image.LANCZOS), ((tw - iw) // 2, 0))
        sh.paste(cell.convert("RGB"), (cx, cy))
        by = cy + int(BOTTOM * sc)
        ty = cy + int((BOTTOM - STAND_H) * sc)
        d.line((cx, by, cx + tw, by), fill=(220, 40, 40), width=2)
        d.line((cx, ty, cx + tw, ty), fill=(40, 170, 90), width=1)
        col = (20, 20, 20) if kind == "정지" else (30, 90, 190)
        d.text((cx + 4, cy + th - 18), f"[{kind}] {key}"[:32], font=f, fill=col)
    os.makedirs("scratch", exist_ok=True)
    sh.save(OUT)
    print("증명시트:", OUT, sh.size)


if __name__ == "__main__":
    main()
