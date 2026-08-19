# -*- coding: utf-8 -*-
"""걸을 수 있는 땅을 **감독이 칠해서** 넣는다 — 자동 측정이 못 잡는 곳.

★사장님 지시(2026-08-13)
  "내가 붓으로 계단 평상을 칠하거나 지우는 것은 못 해. 그것을 네가 해라."

## 왜 손으로 칠하나
`measure_ground.py` 는 **색이 이어지는 바닥**만 잡는다. 그래서 계단처럼 단마다 색이
끊기는 곳은 통째로 "못 가는 곳"이 된다. 실제로 계단 배경은 화면 아래 좁은 띠만 잡혔고,
캐릭터가 계단을 못 올라갔다.

AGS·SLUDGE 같은 어드벤처 엔진도 **사람이 칠한 마스크**를 쓴다. 자동으로 뽑지 않는다.
다만 사장님이 칠하실 일이 아니므로, **실측한 좌표로 감독이 코드로 칠한다.**

## 칠하는 법 — 배경마다 한 벌
`PAINT` 에 그 배경에서 밟을 수 있는 도형을 적어 둔다.

  ("band",  y0, y1, x0, x1)          가로 띠 — 평지·포장
  ("tread", y,  x0, x1, 두께)        계단 디딤판 한 칸
  ("road",  [(y, x0, x1), …])        ★사다리꼴 길 — 소실점으로 좁아지는 길
  ("erase", y0, y1, x0, x1)          지우기 — 물·화단처럼 못 가는 곳

나온 마스크는 앵커 파일의 `ground.top/bot` 을 **덮어쓴다**. 세로줄마다 위·아래 끝을
다시 계산해 넣으므로, `stage2d.Stage` 가 그대로 읽어 쓴다.

    python W1_2/paint_walk.py                 # 칠해 보고 확인 그림만
    python W1_2/paint_walk.py --write         # 앵커에 기록
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ANCHOR_DIR = "assets/anchors"
BG_DIR = "W1_2/bg"
OUT = "W1_2/_walk"
FONT = r"C:\Windows\Fonts\malgun.ttf"
W, H = 1280, 720
STEP = 16

# 계단 디딤판 실측 (steps_measure.py · 아래 0칸 → 위 17칸)
TREAD = [682, 640, 607, 591, 569, 544, 525, 509, 486, 463,
         439, 423, 404, 381, 360, 341, 323, 306]

# ★배경마다 밟을 수 있는 곳 — 감독이 실측해 칠한다
PAINT = {
    # 계단 — 아래 포장 + 디딤판 18칸. 위로 갈수록 계단 폭이 좁아진다(원근).
    "steps_seat": (
        [("band", 682, 720, 0, 1280)] +
        [("tread", TREAD[i], 210 + i * 22, 1075 - i * 22, 14) for i in range(18)]
    ),
    # 난간 계단 — 아래 포장만. 난간 너머는 못 간다
    "steps_rail": [("band", 640, 720, 0, 1280)],
    # 광장 — 포장이 지평선(544)까지 트여 있다
    "plaza_arrive": [("band", 560, 720, 0, 1280)],
    "plaza_gate": [("band", 590, 720, 0, 1280)],
    # 좌판 — 좌판 앞 포장. 좌판 뒤로는 못 간다
    "stall_cuke": [("band", 590, 720, 0, 1280)],
    "stall_milk": [("band", 600, 720, 0, 1280)],
    "stall_rail": [("band", 600, 720, 0, 1280)],
    # 분수 — 분수 둘레만. 물 안은 못 간다
    "fountain_burst": [("band", 610, 720, 0, 1280),
                       ("erase", 610, 660, 330, 950)],
    # 벤치 — 벤치 앞뒤 포장
    "bench_open": [("band", 530, 720, 0, 1280)],
    "bench_pair": [("band", 545, 720, 0, 1280)],
    # ★은행나무길 — **사다리꼴 길**. 소실점으로 좁아진다 (사장님 지시 2026-08-13
    #   "은행나무길도 그 길을 갈 수 있는 구역으로 만들어서 달려갔다 달려올 수 있게")
    #   가로 띠로 칠하면 나무 사이 풀밭까지 밟게 되어 길이 안 산다.
    #   좌우 폭은 배경을 보고 잰 값이다 — 낙엽 깔린 데까지 넉넉히 잡았다.
    "path_leaves": [("road", [(445, 600, 660), (480, 570, 690), (520, 545, 720),
                              (560, 510, 760), (600, 470, 800), (650, 410, 870),
                              (720, 330, 950)])],
    "path_fox": [("road", [(455, 600, 665), (500, 560, 705), (550, 515, 755),
                           (600, 465, 810), (660, 400, 880), (720, 330, 960)])],
    # 해질녘 광화문 — 포장이 광화문 밑단(435)까지
    "dusk_calm": [("band", 470, 720, 0, 1280)],
    "dusk_lanterns": [("band", 460, 720, 0, 1280)],
}


def paint(bg):
    m = np.zeros((H, W), bool)
    for shape in PAINT.get(bg, []):
        kind = shape[0]
        if kind == "band":
            _, y0, y1, x0, x1 = shape
            m[max(0, y0):min(H, y1), max(0, x0):min(W, x1)] = True
        elif kind == "tread":
            _, y, x0, x1, th = shape
            m[max(0, y - th // 2):min(H, y + th // 2 + 1),
              max(0, x0):min(W, x1)] = True
        elif kind == "road":
            # ★사다리꼴 길 — 잰 지점 사이를 줄마다 이어 채운다
            pts = shape[1]
            for i in range(len(pts) - 1):
                (ya, la, ra), (yb, lb, rb) = pts[i], pts[i + 1]
                for y in range(max(0, ya), min(H, yb + 1)):
                    u = (y - ya) / max(1.0, float(yb - ya))
                    l = int(round(la + (lb - la) * u))
                    r = int(round(ra + (rb - ra) * u))
                    m[y, max(0, l):min(W, r)] = True
        elif kind == "erase":
            _, y0, y1, x0, x1 = shape
            m[max(0, y0):min(H, y1), max(0, x0):min(W, x1)] = False
    return m


def to_cols(m):
    """마스크 → 세로줄마다 (위 끝, 아래 끝). 앵커가 쓰는 꼴."""
    top, bot = [], []
    for i in range(W // STEP):
        col = m[:, i * STEP:(i + 1) * STEP].any(axis=1)
        ys = np.nonzero(col)[0]
        if len(ys):
            top.append(int(ys[0]))
            bot.append(int(ys[-1]) + 1)
        else:
            top.append(H)
            bot.append(H)
    return top, bot


def first_frame(bg):
    png = os.path.join(BG_DIR, bg + ".png")
    if os.path.exists(png):
        return Image.open(png).convert("RGB").resize((W, H), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_f.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i",
                    os.path.join(BG_DIR, bg + ".mp4"), "-frames:v", "1", tmp],
                   check=True)
    return Image.open(tmp).convert("RGB").resize((W, H), Image.LANCZOS)


def check(bg, m):
    cv = first_frame(bg).convert("RGBA")
    a = np.array(cv).astype(np.int16)
    a[..., 1][m] = np.minimum(255, a[..., 1][m] + 60)
    a[..., 0][m] = np.maximum(0, a[..., 0][m] - 25)
    cv = Image.fromarray(a.astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(cv)
    d.text((10, 8), "%s — 초록 = 감독이 칠한 '갈 수 있는 땅' (%.1f%%)"
           % (bg, 100.0 * m.mean()), font=ImageFont.truetype(FONT, 21),
           fill=(255, 235, 0))
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "%s.png" % bg)
    cv.convert("RGB").save(p)
    return p


def main():
    write = "--write" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    print("%-17s %8s %8s  %s" % ("배경", "밟을수있는", "가장먼발", "확인 그림"))
    for bg in (args or sorted(PAINT)):
        m = paint(bg)
        if not m.any():
            print("  %-15s ★칠한 것이 없다" % bg)
            continue
        top, bot = to_cols(m)
        far = min(t for t in top if t < H)
        p = check(bg, m)
        print("  %-15s %7.1f%% %8d  %s" % (bg, 100.0 * m.mean(), far, p))

        if write:
            fp = os.path.join(ANCHOR_DIR, bg + ".json")
            doc = {}
            if os.path.exists(fp):
                with open(fp, encoding="utf-8") as f:
                    doc = json.load(f)
            doc.setdefault("bg", bg)
            doc.setdefault("canvas", [W, H])
            g = doc.get("ground") or {}
            # ★`horizon` 은 **바닥 평면의 것**을 지킨다 — 칠한 땅의 맨 위가 아니다.
            #   계단처럼 높아진 땅을 칠하면 맨 위가 y299 까지 올라가는데, 그걸 지평선으로
            #   쓰면 원근이 깨진다(계단 꼭대기가 '무한히 멀다'가 되어 62초짜리 길이 나왔다).
            #   계단은 오를수록 멀어지지만 **올라간 만큼 화면에서 도로 내려온다.**
            g.update({"step": STEP, "top": top, "bot": bot,
                      "walk_top": far,               # 칠한 땅의 맨 위 (참고용)
                      "painted": True,
                      "note": "paint_walk.py — 감독이 실측 좌표로 칠한 walkable area. "
                              "자동 측정(measure_ground)은 색이 끊기는 계단을 못 잡는다. "
                              "horizon 은 바닥 평면 값을 그대로 둔다."})
            g.setdefault("horizon", far)             # 없을 때만 채운다
            doc["ground"] = g
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
    print("\n확인 그림 → %s%s" % (OUT, "  · 앵커에 기록함" if write else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
