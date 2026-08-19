# -*- coding: utf-8 -*-
"""W1-2 **모션 쇼케이스** 배치표 — 8분을 동작으로 빼곡히.

★사장님 지시(2026-08-12):
  "8분 꽉 채워서 캐릭터 모션, 배경과 협동 작업, 다양한 연출, 놀랄 만한 포즈와 동작."
  "동작으로 빈 곳 없이, 있는 모든 애셋 다 집어넣어라."
  "한 캐릭터가 중복해서 둘이 나와도 좋다."
  "**자르지 말고 확대하지 마라. 원근법을 쓰라.**"
  "동시에 두 개의 캐릭터, 셋 캐릭터가 화면에 나오게."
  "앞구르기·백플립은 정상 속도대로 하되 여러 번 반복해도 된다."

## 규칙
· **크롭·확대 금지** — 배경은 1280×720 원본 그대로, 캐릭터는 원본 컷을 **축소만** 한다
· **원근 3층** — 뒤로 갈수록 작고 화면 위쪽(발 y가 높다)
· 한 화면에 **2~3명**. 같은 스틱맨이 겹쳐 나와도 된다
· 1회 동작(백플립·앞구르기)도 **원속 그대로 반복**해서 빈 시간을 없앤다
· 배경 사건과 맞물리는 동작은 그 시각에 맞춘다

## 원근 3층 (발이 각자 지면선에 닿는다)
| 층 | 화면 키 | 발 y | 성격 |
|---|---:|---:|---|
| `front` | 480 | 670 | 큰 동작 — 받기·엉덩방아·급정지 |
| `mid`   | 420 | 646 | 이동·설명 |
| `back`  | 250 | 567 | 아크로바틱 — 백플립·앞구르기 |
| `far`   | 190 | 540 | 아주 멀리 — 걷기·달리기 실루엣 |
"""

# 층 → (화면 키, 발 y)
LAYER = {"front": (480, 670), "mid": (420, 646), "back": (250, 567), "far": (190, 540)}

# 동작 컷의 원속 길이(초) = 컷수 / 8fps  — 반복 횟수를 정할 때 쓴다
CUT_SEC = {
    "back_flip": 8.0, "butt_fall": 8.0, "forward_roll": 8.0, "high_five": 8.0,
    "hop_down": 8.0, "pick_up": 8.0, "reach_catch": 8.0, "shoulder_arm": 8.0,
    "sit_stand": 8.0, "skid_stop": 8.0, "tiptoe": 8.0, "zman_head_tilt": 8.0,
    "zman_sit_stand": 8.0, "zgirl_high_five": 8.0,
    "run_front": 5.5, "run_back": 5.5,
    "zman_run_side": 2.4, "zman_run_side_l": 2.4,
    "zgirl_run_side": 1.2, "zgirl_run_side_l": 1.2,
}

# ── 쇼 구성 ──────────────────────────────────────────────────────────
# (배경, 초, [ (캐릭터, 동작, 층, x시작, x끝, 반복) ... ])
#   캐릭터 : stick / zman / zgirl        층 : LAYER 키
#   x시작→x끝 : 화면을 가로지르면 다르게, 제자리면 같게
#   반복 : 그 동작을 원속으로 몇 번 되풀이할지 (0 = 씬 길이에 맞춰 자동)
SHOW = [
 # ── 1막 광장 — 등장과 아크로바틱 ─────────────────────────────────
 ("plaza_arrive", 34, [
   ("stick", "run_front",    "far",   640,  640, 0),   # 소실점에서 다가온다
   ("stick", "back_flip",    "back",  300,  300, 0),   # 뒤에서 계속 백플립
   ("stick", "skid_stop",    "front", 980,  980, 0),   # 앞에서 급정지
 ]),
 ("plaza_gate", 34, [
   ("stick", "forward_roll", "back",  200, 1080, 0),   # 뒤에서 굴러 가로지른다
   ("stick", "tiptoe",       "mid",   900,  420, 0),   # 살금살금 반대로
   ("zman",  "zman_run_side","front", -80, 1360, 0),   # 앞을 가로질러 달린다
 ]),

 # ── 2막 계단 — 앉고 뛰어내리기 ──────────────────────────────────
 ("steps_seat", 32, [
   ("stick", "sit_stand",    "mid",   640,  640, 0),
   ("stick", "back_flip",    "back",  300,  300, 0),
   ("zgirl", "zgirl_run_side_l", "front", 1360, -80, 0),
 ]),
 ("steps_rail", 30, [
   ("stick", "hop_down",     "mid",   560,  560, 0),
   ("stick", "forward_roll", "back",  980,  240, 0),
   ("zman",  "zman_head_tilt","front", 980,  980, 0),
 ]),

 # ── 3막 좌판 — 물건과 맞물리기 ──────────────────────────────────
 ("stall_cuke", 34, [
   ("stick", "pick_up",      "front", 610,  610, 0),   # 오이가 멈추는 자리
   ("stick", "run_front",    "far",   700,  700, 0),
   ("stick", "back_flip",    "back",  260,  260, 0),
 ]),
 ("stall_milk", 32, [
   ("stick", "reach_catch",  "front", 958,  958, 0),   # 우유팩 떨어지는 자리
   ("stick", "tiptoe",       "mid",   200,  700, 0),
   ("zgirl", "zgirl_high_five","back", 420,  420, 0),
 ]),
 ("stall_rail", 30, [
   ("stick", "butt_fall",    "front", 700,  700, 0),
   ("stick", "hop_down",     "mid",   300,  300, 0),
   ("zman",  "zman_sit_stand","back", 1000, 1000, 0),
 ]),

 # ── 4막 분수 — 물기둥에 놀라기 ──────────────────────────────────
 ("fountain_burst", 34, [
   ("stick", "butt_fall",    "front", 690,  690, 0),   # 물기둥 자리에서 뒤로 넘어진다
   ("stick", "back_flip",    "back",  260,  260, 0),
   ("stick", "run_front",    "far",   980,  980, 0),
 ]),

 # ── 5막 벤치 — 셋이 어울리기 ────────────────────────────────────
 ("bench_pair", 32, [
   ("stick", "sit_stand",    "mid",   620,  620, 0),
   ("zman",  "zman_sit_stand","mid",  880,  880, 0),
   ("stick", "forward_roll", "back",  200, 1080, 0),
 ]),
 ("bench_open", 34, [
   ("stick", "high_five",    "mid",   560,  560, 0),
   ("zgirl", "zgirl_high_five","mid",  760,  760, 0),
   ("stick", "back_flip",    "back",  300,  300, 0),
   ("zman",  "zman_run_side","far",  -80, 1360, 0),
 ]),

 # ── 6막 산책로 — 여우와 낙엽 ────────────────────────────────────
 ("path_fox", 34, [
   ("stick", "tiptoe",       "mid",   200,  900, 0),   # 살금살금 다가간다
   ("stick", "butt_fall",    "front", 900,  900, 0),   # 놀라 엉덩방아
   ("stick", "forward_roll", "back",  980,  240, 0),
 ]),
 ("path_leaves", 32, [
   ("stick", "reach_catch",  "front", 640,  640, 0),   # 잎을 잡는다
   ("stick", "back_flip",    "back",  260,  260, 0),
   ("zgirl", "zgirl_run_side","mid",  -80, 1360, 0),
 ]),

 # ── 7막 해질녘 — 다 모여 마무리 ─────────────────────────────────
 ("dusk_lanterns", 34, [
   ("stick", "high_five",    "mid",   640,  640, 0),
   ("zman",  "zman_head_tilt","front", 320,  320, 0),
   ("zgirl", "zgirl_high_five","front", 960, 960, 0),
   ("stick", "forward_roll", "back",  200, 1080, 0),
 ]),
 ("dusk_calm", 36, [
   ("stick", "run_back",     "far",   640,  640, 0),   # 멀어져 간다
   ("stick", "shoulder_arm", "mid",   340,  340, 0),
   ("stick", "back_flip",    "back",  940,  940, 0),
   ("zman",  "zman_run_side_l", "front", 1360, -80, 0),
 ]),
]

# ★m6 스틱맨 이동컷 라이브러리(572컷) — 걷기·달리기·회전·나가기 순환.
#   `gseq:m6_stick:...` 으로 붙는다. 씬마다 한 층을 이걸로 채워 화면이 늘 살아 있게 한다.
M6_FILL = [
 ("plaza_arrive",  "walk_side_r",  "mid",   -80, 1360),
 ("plaza_gate",    "run_side_r",   "far",   -80, 1360),
 ("steps_seat",    "walk_turn_r",  "far",   900,  900),
 ("steps_rail",    "run_turn_l",   "far",   300,  300),
 ("stall_cuke",    "walk_side_l",  "mid",  1360,  -80),
 ("stall_milk",    "run_side_l",   "far",  1360,  -80),
 ("stall_rail",    "walk_exit_r",  "far",   500,  980),
 ("fountain_burst","run_exit_r",   "mid",   300, 1200),
 ("bench_pair",    "walk_side_r",  "far",   -80, 1360),
 ("bench_open",    "run_side_l",   "far",  1360,  -80),
 ("path_fox",      "walk_turn_l",  "far",   500,  500),
 ("path_leaves",   "run_turn_r",   "far",   900,  900),
 ("dusk_lanterns", "walk_exit_l",  "far",   800,  320),
 ("dusk_calm",     "run_exit_l",   "far",   980,  200),
]

# ★정지 포즈 — 배경마다 두 장씩 세워 화면을 채운다(53장을 골고루 쓴다).
#   (배경, [(캐릭터, 포즈이름, 층, x) ...])
POSE_FILL = [
 ("plaza_arrive",  [("stick", "sm_greeting_wave", "mid", 1100),
                    ("stick", "stickman_w1d2_mouth_a", "back", 900)]),
 ("plaza_gate",    [("stick", "sm_presenting", "mid", 180),
                    ("stick", "stickman_w1d2_mouth_i", "back", 700)]),
 ("steps_seat",    [("stick", "sm_pointing_left", "front", 200),
                    ("stick", "stickman_w1d2_card_hold", "back", 1050)]),
 ("steps_rail",    [("stick", "stickman_w1d2_grab_rail_r", "front", 200),
                    ("stick", "stickman_w1d2_mouth_o", "back", 620)]),
 ("stall_cuke",    [("stick", "sm_counting_five", "mid", 240),
                    ("stick", "stickman_w1d2_surprise", "back", 900)]),
 ("stall_milk",    [("stick", "stickman_w1d2_card_fan", "mid", 1080),
                    ("stick", "stickman_w1d2_mouth_u", "back", 760)]),
 ("stall_rail",    [("stick", "stickman_w1d2_lean_rail_r", "mid", 1120),
                    ("stick", "sm_arms_out_wide", "back", 600)]),
 ("fountain_burst",[("stick", "sm_holding_mirror", "mid", 260),
                    ("stick", "stickman_w1d2_mouth_yeo", "back", 1000)]),
 ("bench_pair",    [("zgirl", "zgirl_card_hold", "front", 300),
                    ("stick", "stickman_w1d2_sit_bench", "back", 1080)]),
 ("bench_open",    [("zman", "zman_attention", "front", 200),
                    ("zgirl", "zgirl_attention", "front", 1080)]),
 ("path_fox",      [("stick", "stickman_w1d2_crouch_ground_r", "front", 320),
                    ("zman", "zman_mirror", "back", 1020)]),
 ("path_leaves",   [("zman", "zman_arms_wide", "front", 260),
                    ("zgirl", "zgirl_arms_wide", "back", 1000)]),
 ("dusk_lanterns", [("zman", "zman_hands_up", "back", 200),
                    ("zgirl", "zgirl_hands_up", "back", 1080)]),
 ("dusk_calm",     [("zman", "zman_card_hold", "front", 200),
                    ("zgirl", "zgirl_mirror", "front", 1080)]),
]

# ★삽화 카드 8장 — 배경마다 하나씩 화면 위쪽에 띄운다(자산을 다 쓴다)
CARD_FILL = [
 ("stall_cuke", "oi"), ("stall_milk", "uyu"), ("fountain_burst", "o"),
 ("path_fox", "yeou"), ("bench_pair", "au"), ("steps_seat", "ai"),
 ("steps_rail", "i"), ("dusk_lanterns", "o5"),
]


def total_sec():
    return sum(s[1] for s in SHOW)


if __name__ == "__main__":
    n_obj = sum(len(s[2]) for s in SHOW)
    used = set()
    for _, _, acts in SHOW:
        for a in acts:
            used.add(a[1])
    print("배경 %d개 · %d초 (%d분 %d초) · 오브젝트 %d개 · 쓰는 동작 %d종"
          % (len(SHOW), total_sec(), total_sec() // 60, total_sec() % 60, n_obj, len(used)))
    print("\n씬별")
    for bg, sec, acts in SHOW:
        print("  %-16s %2d초  %s" % (bg, sec, " · ".join(
            "%s/%s@%s" % (c, k, L) for c, k, L, _, _, _ in acts)))
    print("\n쓰는 동작:", ", ".join(sorted(used)))
    unused = sorted(set(CUT_SEC) - used)
    if unused:
        print("★안 쓰는 동작:", ", ".join(unused))
