#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_zolla_write_poses.py — 졸라걸(머리묶음) 파라메트릭 동작 포즈 세트 생성.
stickman_factory render_pose(style=zolla) + 머리묶음(bun) + 연필로,
'왼→중앙 이동/글쓰기/설명/복귀/앉아생각/책읽기/일어서기' 애니메이션용 포즈들을 만든다.
출력: assets/graphics/poses/stickman_zg_<name>.png (투명 트림 안 함 — 좌표계 공유로 정렬 유지)
검증: python make_zolla_write_poses.py  → scratch/_zg_poses_sheet.png
"""
import os, sys, math
from PIL import Image, ImageDraw
import stickman_factory as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
POSES = os.path.join(ROOT, "assets", "graphics", "poses")
S, SS = sf.S, sf.SS
P = sf.P

# facing="right" → 글자(오른쪽)를 향해 글씨 쓰기. 오른팔에 연필.
PEN = {"hand": "right", "len": 15}

# 동작 포즈 정의 (60x80 좌표계). 오른손이 오른쪽-아래로 뻗어 글쓰기.
DEFS = {
    # 걷기 2프레임 (옆모습, 오른쪽 글자 향해 성큼) — facing right
    "walk1": dict(style="zolla", facing="right", expr="happy",
                  pts=P(head=(31, 11), chest=(30, 20), body=(30, 30), pelvis=(30, 41),
                        kneeLeft=(27, 51), feetLeft=(23, 64), kneeRight=(34, 52), feetRight=(39, 63),
                        elbowLeft=(28, 30), handLeft=(25, 37), elbowRight=(33, 28), handRight=(36, 34))),
    "walk2": dict(style="zolla", facing="right", expr="happy",
                  pts=P(head=(31, 11), chest=(30, 20), body=(30, 30), pelvis=(30, 41),
                        kneeLeft=(31, 52), feetLeft=(35, 63), kneeRight=(30, 51), feetRight=(27, 64),
                        elbowLeft=(32, 30), handLeft=(35, 36), elbowRight=(29, 29), handRight=(26, 35))),
    # 글쓰기 3프레임 (오른팔+연필이 위→중→아래로, 필기 동작) — 오른쪽 향함
    "write_up": dict(style="zolla", facing="right", expr="talk", pencil=PEN,
                     pts=P(head=(31, 11), elbowRight=(37, 22), handRight=(45, 22))),
    "write_mid": dict(style="zolla", facing="right", expr="talk", pencil=PEN,
                      pts=P(head=(31, 11), elbowRight=(38, 26), handRight=(47, 29))),
    "write_dn": dict(style="zolla", facing="right", expr="talk", pencil=PEN,
                     pts=P(head=(31, 11), elbowRight=(38, 30), handRight=(46, 35))),
    # 설명 (옆모습, 글자 쪽 향해 한 손 들어 강조) — facing right
    "explain": dict(style="zolla", facing="right", expr="talk",
                    pts=P(head=(31, 11), elbowRight=(36, 20), handRight=(43, 14), elbowLeft=(29, 30), handLeft=(31, 38))),
    # 서서 글자 쳐다봄 — 오른쪽 향함
    "look": dict(style="zolla", facing="right", expr="neutral",
                 pts=P(head=(31, 11), elbowRight=(34, 28), handRight=(31.5, 19))),
    # 앞을 봄(정면 기본, 청중 바라보기)
    "look_front": dict(style="zolla", facing="front", expr="happy",
                       pts=P(elbowLeft=(26, 30), handLeft=(25, 38), elbowRight=(34, 30), handRight=(35, 38))),
    # 오른쪽(글자) 손으로 가리키기
    "point_right": dict(style="zolla", facing="right", expr="talk",
                        pts=P(head=(31, 11), elbowRight=(38, 21), handRight=(48, 18))),
    # 앉기(정면) — 시작/끝 인사·차분
    "sit_front": dict(style="zolla", facing="front", expr="happy",
                      pts=P(head=(30, 13), chest=(30, 22), body=(30, 31), pelvis=(30, 42),
                            kneeLeft=(27, 44), feetLeft=(26, 56), kneeRight=(33, 44), feetRight=(34, 56),
                            elbowLeft=(26, 30), handLeft=(27, 40), elbowRight=(34, 30), handRight=(33, 40))),
    # 앉아서 생각 (턱에 손) — 옆모습
    "sit_think": dict(style="zolla", facing="right", expr="neutral",
                      pts=P(head=(31, 13), chest=(30, 22), body=(29.5, 31), pelvis=(28, 42),
                            kneeLeft=(33, 43), feetLeft=(34, 56), kneeRight=(34, 42), feetRight=(35, 55),
                            elbowLeft=(31, 30), handLeft=(34, 40), elbowRight=(33, 24), handRight=(31.5, 18))),
    # 앉아서 책 폄 (두 손 앞으로 책 든 자세) — 옆모습
    "sit_read": dict(style="zolla", facing="right", expr="happy",
                     pts=P(head=(31, 14), chest=(30, 22), body=(29.5, 31), pelvis=(28, 42),
                           kneeLeft=(33, 43), feetLeft=(34, 56), kneeRight=(34, 42), feetRight=(35, 55),
                           elbowLeft=(31, 29), handLeft=(35, 33), elbowRight=(33, 29), handRight=(37, 33))),
    # ── 시그니처(캐릭터 고유 마무리) ──
    # 졸라걸: 점프(신남) — 두 팔 위로, 다리 벌림
    "sig_jump": dict(style="zolla", facing="front", expr="happy",
                     pts=P(head=(30, 9), chest=(30, 18), body=(30, 27), pelvis=(30, 37),
                           elbowLeft=(25, 12), handLeft=(22, 4), elbowRight=(35, 12), handRight=(38, 4),
                           kneeLeft=(26, 47), feetLeft=(22, 58), kneeRight=(34, 47), feetRight=(38, 58))),
    # 스틱맨: 로댕 '생각하는 사람' — 앉아 팔꿈치 무릎, 턱에 주먹(옆모습)
    "sig_thinker": dict(style="zolla", facing="right", expr="neutral",
                        pts=P(head=(32, 15), chest=(31, 23), body=(30, 31), pelvis=(28, 42),
                              kneeLeft=(34, 44), feetLeft=(36, 57), kneeRight=(33, 44), feetRight=(34, 57),
                              elbowLeft=(30, 32), handLeft=(32, 40), elbowRight=(34, 40), handRight=(33, 20))),
}


def add_bun(img, headpt):
    """머리 위-뒤에 묶음(bun) 하나 그려 졸라'걸' 정체성 부여."""
    d = ImageDraw.Draw(img)
    hx, hy = headpt[0] * S, headpt[1] * S     # 최종 해상도 좌표(render_pose가 /SS 리사이즈 후)
    hr = 7.0 * S
    br = 3.9 * S                              # 묶음 반지름
    facing = _CUR_FACING.get("f", "front")
    off = {"front": 0.0, "right": -0.45, "left": 0.45}.get(facing, 0.0)
    cx, cy = hx + off * hr, hy - hr * 0.55    # 머리 위(뒤쪽)에 붙임
    d.ellipse([cx - br, cy - br, cx + br, cy + br], fill=sf.INK)
    return img


_CUR_FACING = {"f": "front"}


ORANGE = (232, 126, 58, 255)   # 졸라걸 주황 머리
WHITE = (252, 250, 247, 255)   # 흰 얼굴

def gen(name, spec):
    spec = dict(spec)
    spec.pop("style", None)
    img = sf.render_girl(spec, seed=hash(name) % 1000)   # 원본 졸라걸 룩(통통 튜브+손발+주황머리)
    out = os.path.join(POSES, f"stickman_zg_{name}.png")
    img.save(out)
    return out, img


def main():
    os.makedirs(POSES, exist_ok=True)
    made = []
    for name, spec in DEFS.items():
        out, img = gen(name, spec)
        made.append((name, img))
    # 공통 박스로 정렬 크롭(모든 포즈 동일 크기·발 위치 정렬 → 애니메이션 시 크기/위치 튐 방지)
    import numpy as np
    boxes = [im.split()[3].getbbox() for _, im in made]
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    pad = 16
    x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(made[0][1].width, x1 + pad); y1 = min(made[0][1].height, y1 + pad)
    cropped = []
    for name, im in made:
        ci = im.crop((x0, y0, x1, y1))
        ci.save(os.path.join(POSES, f"stickman_zg_{name}.png"))
        cropped.append((name, ci))
        print(f"  OK stickman_zg_{name:10} {ci.size} (정렬크롭)")
    made = cropped
    # 미리보기 시트
    cols = 3
    rows = (len(made) + cols - 1) // cols
    cw = made[0][1].width // 2
    ch = made[0][1].height // 2
    sheet = Image.new("RGB", (cw * cols, ch * rows), (245, 244, 240))
    d = ImageDraw.Draw(sheet)
    from PIL import ImageFont
    f = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 26)
    for i, (name, img) in enumerate(made):
        r, c = divmod(i, cols)
        thumb = img.resize((cw, ch), Image.LANCZOS)
        bg = Image.new("RGB", (cw, ch), (245, 244, 240))
        bg.paste(thumb.convert("RGB"), (0, 0), thumb)
        sheet.paste(bg, (c * cw, r * ch))
        d.text((c * cw + 10, r * ch + 8), name, font=f, fill=(30, 30, 40))
    sheet.save(os.path.join(ROOT, "scratch", "_zg_poses_sheet.png"))
    print(f"\n{len(made)} poses -> scratch/_zg_poses_sheet.png")


if __name__ == "__main__":
    main()
