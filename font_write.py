#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
font_write.py — 전용 폰트(검은고딕/나눔고딕/나눔손글씨/카페24동동 …)의 글자꼴로
'매직펜으로 쓰듯' 파라메트릭 드로잉하는 렌더러.

방식: 폰트로 문장을 고해상도 알파로 렌더 → 글자 획을 '쓰는 순서'(위→아래 우선, 왼→오)
로 진행 마스크를 만들어 progress(0..1)까지만 드러냄 + 진행 앞단에 펜촉(밝은 점).
손코딩 획이 아니라 실제 폰트 글자꼴이라 훨씬 예쁘고 정확하다.

DB: channel/content.db hangeul_fonts(key,file_path,...) 에서 폰트를 찾음.
render_text_writing(text, key, size_px, progress) -> RGBA 이미지
검증: python font_write.py     # 6개 폰트 × 한 문장 파라메트릭 드로잉 시트
"""
import os, sys, sqlite3
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")
SS = 2                    # supersample
INK = (34, 30, 26, 255)   # 잉크색

_FCACHE = {}
def font_path(key):
    if key not in _FCACHE:
        con = sqlite3.connect(DB)
        r = con.execute("SELECT file_path FROM hangeul_fonts WHERE key=?", (key,)).fetchone()
        con.close()
        _FCACHE[key] = os.path.join(ROOT, r[0]) if r else None
    return _FCACHE[key]

def list_fonts():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    rows = list(con.execute("SELECT key,korean_name,file_path,use_for FROM hangeul_fonts ORDER BY id"))
    con.close(); return rows


def _render_alpha(text, fp, size_px, pad=0.22):
    """폰트로 text를 렌더한 알파(L) + 잉크색 RGBA 반환 (SS 배율)."""
    fnt = ImageFont.truetype(fp, int(size_px * SS))
    tmp = Image.new("L", (10, 10), 0)
    bb = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=fnt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    px = int(size_px * SS * pad)
    W, H = tw + 2 * px, th + 2 * px
    a = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(a)
    d.text((px - bb[0], px - bb[1]), text, font=fnt, fill=255)
    return a


def render_text_writing(text, key, size_px, progress=1.0, ink=INK, pen=True):
    """text를 전용 폰트꼴로 progress(0..1)까지 '써지는' 상태로 그린 RGBA."""
    fp = font_path(key)
    if not fp or not os.path.exists(fp):
        raise FileNotFoundError(key)
    alpha = _render_alpha(text, fp, size_px)
    W, H = alpha.size
    arr = np.asarray(alpha, dtype=np.float32) / 255.0   # (H,W) 잉크 강도
    ys, xs = np.nonzero(arr > 0.35)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if len(xs) == 0 or progress <= 0:
        return out.resize((W // SS, H // SS), Image.LANCZOS)
    if progress >= 1.0:
        col = Image.new("RGBA", (W, H), ink)
        out = Image.composite(col, out, alpha)
        return out.resize((W // SS, H // SS), Image.LANCZOS)
    # '쓰는 순서' 스칼라 t(픽셀) = 주로 왼→오(x), 약간 위→아래(y) 가중.
    x0, x1 = xs.min(), xs.max()
    order = arr.copy()
    xx = np.linspace(0, 1, W)[None, :]
    yy = np.linspace(0, 1, H)[:, None]
    torder = xx * 0.86 + yy * 0.14                       # 손글씨 진행 방향
    thr = progress
    # feather: 진행 경계 근처는 부드럽게
    reveal = np.clip((thr - torder) / 0.05 + 1.0, 0.0, 1.0)
    mask = (arr * reveal * 255).astype(np.uint8)
    col = Image.new("RGBA", (W, H), ink)
    out = Image.composite(col, out, Image.fromarray(mask, "L"))
    # 펜촉: 현재 경계(torder≈thr)에서 잉크가 있는 지점에 밝은 점
    if pen:
        band = (np.abs(torder - thr) < 0.02) & (arr > 0.4)
        pys, pxs = np.nonzero(band)
        if len(pxs):
            cx, cy = int(pxs.mean()), int(pys[np.argmax(pxs)] if len(pys) else 0)
            pd = ImageDraw.Draw(out)
            r = int(6 * SS)
            pd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 90, 40, 230))
    return out.resize((W // SS, H // SS), Image.LANCZOS)


def _sheet():
    sent = "한글 받침 대표 7음"
    steps = [0.25, 0.5, 0.75, 1.0]
    fonts = list_fonts()
    cell_h = 150
    rowfont = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 24)
    imgs = []
    for r in fonts:
        row = Image.new("RGBA", (1500, cell_h), (248, 247, 243, 255))
        d = ImageDraw.Draw(row)
        d.text((12, 10), f"{r['korean_name']}", fill=(30, 30, 30), font=rowfont)
        d.text((12, 44), r['key'], fill=(140, 140, 140), font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 16))
        x = 300
        for p in steps:
            im = render_text_writing(sent, r["key"], 78, progress=p)
            row.alpha_composite(im, (x, (cell_h - im.height) // 2))
            x += 300
        imgs.append(row)
    sheet = Image.new("RGBA", (1500, cell_h * len(imgs)), (248, 247, 243, 255))
    for i, im in enumerate(imgs):
        sheet.alpha_composite(im, (0, i * cell_h))
    out = os.path.join(ROOT, "scratch", "_font_write_sheet.png")
    sheet.convert("RGB").save(out)
    print("font-write sheet ->", out)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "scratch"), exist_ok=True)
    _sheet()
