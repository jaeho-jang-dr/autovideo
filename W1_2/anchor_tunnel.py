# -*- coding: utf-8 -*-
"""터널분수 무대를 **2.5D 엔진 규격**으로 적어 둔다 (`assets/anchors/perf_tunnel.json`).

★사장님 지시(2026-08-14) "2.5D 캐릭터 모션 엔진을 사용한다."

`stage2d.Stage` 는 배경 이름으로 이 파일을 읽어 원근과 걸을 수 있는 땅을 가져간다.
씬 스크립트가 제 나름의 상수를 들고 있으면 그때뿐이고 다음 씬에서 또 재야 한다.
무대는 **한 번 재서 여기 적어 두고**, 씬은 엔진에게 물어보기만 한다.

## 실측 (`W1_2/_check/tn4_191.png`)
  키 = 0.45 × (발y − 321)   ← 배경 실루엣으로 맞춤(잔차 5.5px)
  ※젖은 돌의 반사가 발밑에서 사람과 붙어 키가 두 배로 잡히길래, 마스크를 깎아
    목을 끊고 다시 쟀다.

## 걸을 수 있는 땅
물이 떨어지는 좌우 수로는 못 밟는다. 가운데 **마른 통로**만 밟는다.
소실점(640, 321)으로 모이는 사다리꼴로 잡았다 —
  발y 715 에서 x 300~980, 발y 430 에서 x 560~720.

    python W1_2/anchor_tunnel.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ANCHOR_DIR = "assets/anchors"
BG = "perf_tunnel"
W, H = 1280, 720
STEP = 16

# ★전면 재측정 (2026-08-14). 앞의 값(지평선 321·k 0.45~0.62)은 **틀렸다.**
#   자동 검출기가 나무·물보라·건물을 사람으로 잡아 그 위에 회귀를 돌렸다.
#   그래서 지평선을 138px 이나 위로 잡았고, 캐릭터가 **허공을 걷고 크기도 거의
#   안 변했다**(사장님 지적 "하늘로 날라 올라가고 원근법도 없고").
#
#   사람이 있는 자리를 눈으로 짚어 그 안에서만 위·아래 끝을 재니 이렇게 나온다:
#     큰 커플   발y 565·562 · 키 185·182
#     좌우 사람 발y 559·544 · 키 159·138
#     가운데 무리 발y 501 · 키 59
#     문 앞 사람 발y 478 · 키 42
#   → 키 = 1.681 × (발y − 459) · 잔차 8.6px
#     발y 700 → 405 (우리 나레이터 기준 400 과 맞는다)
#     발y 485 → 44  (문 앞 사람들과 같은 키)
HORIZON = 459.0
K = 1.681
Y_NEAR, Y_FAR = 720.0, 480.0
X_NEAR = (250.0, 1030.0)
X_FAR = (520.0, 760.0)


def band(y):
    """그 줄에서 밟을 수 있는 x 범위 — 소실점으로 모이는 사다리꼴."""
    if y < Y_FAR or y > H:
        return None
    u = (y - Y_FAR) / (Y_NEAR - Y_FAR)
    return (X_FAR[0] + (X_NEAR[0] - X_FAR[0]) * u,
            X_FAR[1] + (X_NEAR[1] - X_FAR[1]) * u)


def main():
    os.makedirs(ANCHOR_DIR, exist_ok=True)
    top, bot = [], []
    for x in range(0, W, STEP):
        lo, hi = None, None
        for y in range(int(Y_FAR), H, 2):
            b = band(y)
            if b and b[0] <= x <= b[1]:
                if lo is None:
                    lo = y
                hi = y
        top.append(lo if lo is not None else 0)
        bot.append(hi if hi is not None else 0)

    doc = {
        "bg": BG,
        "stage": {"horizon": HORIZON, "k": K,
                  "front_h": round(K * (H - HORIZON), 1),
                  "note": "배경 실루엣으로 맞춤 · 잔차 5.5px · 반사 끊고 잼"},
        "ground": {"step": STEP, "top": top, "bot": bot,
                   "note": "가운데 마른 통로만. 좌우 수로는 물이 떨어져 못 밟는다"},
        "anchors": {},
    }
    p = os.path.join(ANCHOR_DIR, BG + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    n = sum(1 for a, b in zip(top, bot) if b > a)
    print("%s · 밟을 수 있는 세로줄 %d/%d · 키 %.0f(발y 720) ~ %.0f(발y %d)"
          % (p, n, len(top), K * (H - HORIZON), K * (Y_FAR - HORIZON), Y_FAR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
