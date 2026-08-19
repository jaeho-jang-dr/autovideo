# -*- coding: utf-8 -*-
"""W1-2 앵커 JSON — 배경에서 **캐릭터가 몸을 걸 지점**의 좌표.

앉을 단·잡을 난간·기댈 난간·물건이 멈춘 자리. 인터액트랑이 이 좌표에 캐릭터의
엉덩이·손·등을 맞춘다.

## 어디서 나온 값인가
- `stall_cuke` · `stall_milk` → **동영상 프레임 실측**(`measure_bg_events.py`).
  물체가 실제로 멈춘 자리다
- 나머지 정지 배경 → 그림 위에 100px 격자를 얹어 읽은 값

## ★깊이 검산
`sit` 앵커는 **발 y − 0.45 × 그 깊이의 키** 와 맞아야 한다.
거꾸로 풀면 **그 자리에 앉을 수 있는 캐릭터의 키**가 나온다 —
배경이 그려진 크기가 캐릭터 깊이를 정한다(캐릭터를 배경에 맞춘다).

    python W1_2/make_anchors.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = "assets/anchors"

# 배경키 → {앵커이름: (type, x, y, 메모)}
ANCHORS = {
    "steps_seat": {
        "step_seat":   ("sit",   640, 243, "가운데 특히 넓은 빈 단 — 걸터앉는 자리"),
        "step_top":    ("stand", 640, 205, "계단 위 (동상 앞)"),
        "step_bottom": ("stand", 640, 600, "계단 아래 포장"),
        "rail_grip_l": ("grab",  155, 250, "왼쪽 난간 윗대"),
        "rail_grip_r": ("grab", 1105, 250, "오른쪽 난간 윗대"),
    },
    "steps_rail": {
        "rail_grip":   ("grab",  565, 390, "두 기둥 사이 윗대 — 잡고 기울인다"),
        "rail_post_l": ("stand", 360, 430, "왼쪽 기둥"),
        "rail_post_r": ("stand", 770, 430, "오른쪽 기둥"),
    },
    "stall_rail": {
        "stall_rail":  ("lean",  700, 492, "난간 윗대 — 등을 기댄다"),
        "stall_front": ("stand", 300, 600, "좌판 앞 포장"),
    },
    "bench_pair": {
        "bench_seat_l": ("sit",  620, 505, "벤치 왼쪽 — 스틱맨"),
        "bench_seat_r": ("sit",  880, 505, "벤치 오른쪽 — 졸라맨"),
        "bench_back":   ("lean", 750, 428, "등받이 윗대"),
    },
    "bench_open": {
        "stand_l": ("stand", 380, 640, "셋이 나란히 설 자리 왼쪽"),
        "stand_c": ("stand", 620, 640, "가운데"),
        "stand_r": ("stand", 860, 640, "오른쪽"),
    },
    # ★동영상 프레임 실측값 (measure_bg_events.py)
    "stall_cuke": {
        "cuke_rest": ("ground", 610, 509, "오이가 3.79초에 멈춘 자리 — 프레임 실측"),
    },
    "stall_milk": {
        "milk_fall": ("grab", 958, 607, "우유팩이 5.21초에 안착한 자리 — 프레임 실측"),
    },
    "path_fox": {
        "bush_peek":   ("touch",  877, 549, "여우가 나오는 덤불 — 프레임 실측"),
        "path_ground": ("ground", 700, 640, "쭈그려 살피는 자리"),
    },
}

# 깊이표 (W1_2_motion.md §0-B) — 발 y 기준
DEPTHS = [("F0", 573, 706), ("F1", 480, 670), ("M", 420, 646),
          ("M2", 322, 607), ("D1", 220, 567), ("D2", 149, 539)]


def implied_height(y_hip, foot_y):
    """앉기 앵커에서 거꾸로 푼 **그 자리에 맞는 서기 키**."""
    return (foot_y - y_hip) / 0.45


def main():
    os.makedirs(OUT, exist_ok=True)
    for bg, items in ANCHORS.items():
        doc = {"bg": bg, "canvas": [1280, 720], "anchors": {}}
        for name, (typ, x, y, note) in items.items():
            doc["anchors"][name] = {"type": typ, "x": x, "y": y, "note": note}
        p = os.path.join(OUT, bg + ".json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        print("  %-16s %d개 → %s" % (bg, len(items), p))
        for name, (typ, x, y, _) in items.items():
            if typ != "sit":
                continue
            # 그 앵커 아래 지면을 발끝으로 보고 키를 역산한다
            foot = 600 if bg == "bench_pair" else 620
            h = implied_height(y, foot)
            best = min(DEPTHS, key=lambda d: abs(d[1] - h))
            print("     ★%s(sit) 발끝 y%d 가정 → 맞는 서기 키 **%.0f** ≈ 깊이 %s(%d)"
                  % (name, foot, h, best[0], best[1]))
    print("\n%d개 배경 → %s" % (len(ANCHORS), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
