# -*- coding: utf-8 -*-
"""W1-2 **씬 → 자산** 대조표. 검수와 DB 배선의 원천.

`W1_2_scenario.md`(26씬)와 `W1_2_motion.md`(씬별 트랙)를 읽어 손으로 옮긴 것이다.
문서가 바뀌면 여기도 같이 고친다. `precheck_w12.py` 가 이 표와 **실제 파일**을
양방향으로 대조한다([[precheck-asset-fidelity-before-render]]).

용어
  bg    : W1_2/bg/<키>.mp4|png
  cut   : W1_2/motion6_cuts/<키>/       (동작 프레임컷)
  pose  : W1_2/pose_cuts/<키>.png       (졸라 정지 포즈 · 투명컷)
  spose : W1_2/_poses/<키>.png          (스틱맨 정지 포즈 · 기존)
  card  : W1_2/cards/card_<키>.png      (삽화 카드)
  anchor: assets/anchors/<배경키>.json
"""

# (씬, 초, 배경, [동작컷], [정지포즈], [카드], [앵커])
SCENES = [
    (1,  20, "plaza_arrive",   ["run_front", "skid_stop"], ["sm_greeting_wave"], [], []),
    (2,  16, "plaza_arrive",   ["zman_run_side2"], ["sm_presenting"], [], []),
    (3,  14, "plaza_gate",     ["m6_run_side_r", "m6_run_turn_r"], ["sm_pointing_left"], [], []),
    (4,  12, "plaza_gate",     ["forward_roll2"], ["sm_presenting"], [], []),

    (5,  22, "steps_seat",     ["m6_walk_side_r", "m6_walk_turn_r", "sit_stand"],
             ["stickman_w1d2_card_hold"], ["ai"], ["step_seat"]),
    (6,  18, "steps_seat",     ["sit_stand", "hop_down"],
             ["stickman_w1d2_mouth_a", "stickman_w1d2_mouth_i"], [], ["step_seat"]),
    (7,  18, "steps_rail",     ["m6_run_side_r"],
             ["stickman_w1d2_grab_rail_r"], ["i"], ["rail_grip"]),

    (8,  22, "stall_cuke",     ["m6_run_side_r", "m6_run_turn_r", "pick_up"], [], ["oi"],
             ["cuke_rest"]),
    (9,  18, "stall_cuke",     [], ["stickman_w1d2_mouth_o", "stickman_w1d2_mouth_i"], [], []),
    (10, 20, "stall_milk",     ["reach_catch"], [], ["uyu"], ["milk_fall"]),
    (11, 18, "stall_milk",     [], ["stickman_w1d2_mouth_u"], [], []),
    (12, 18, "stall_rail",     ["m6_run_side_r"], ["stickman_w1d2_lean_rail_r"], [], ["stall_rail"]),

    (13, 22, "fountain_burst", ["skid_stop", "run_front", "m6_run_turn_l"],
             [], ["o"], []),
    (14, 18, "fountain_burst", [], ["sm_counting_five"], ["o5"], []),

    (15, 22, "bench_pair",     ["m6_run_side_r", "sit_stand", "shoulder_arm"],
             ["zman_shoulder_recv"], ["au"], ["bench_seat_l", "bench_seat_r"]),
    # ★S16 은 스틱맨이 입 모양을 보이고 **졸라맨이 한 박자 늦게 따라 한다** — 둘 다 필요
    (16, 18, "bench_pair",     ["zman_head_tilt"],
             ["stickman_w1d2_mouth_a", "stickman_w1d2_mouth_u",
              "zman_mouth_a", "zman_mouth_u"], [], []),
    (17, 16, "bench_open",     ["zgirl_run_side", "high_five", "zgirl_high_five", "sit_stand"],
             [], [], []),
    (18, 16, "bench_open",     [], ["zman_attention", "zgirl_attention"], [], []),

    (19, 22, "path_fox",       ["m6_walk_side_l", "tiptoe"],
             ["stickman_w1d2_crouch_ground_r"], ["yeou"], ["path_ground"]),
    (20, 18, "path_fox",       ["butt_fall"],
             ["stickman_w1d2_mouth_yeo", "stickman_w1d2_mouth_u"], [], []),
    (21, 18, "path_leaves",    [], ["sm_arms_out_wide"], [], []),
    (22, 18, "path_leaves",    ["reach_catch"], [], [], []),

    # ★S23 방향 — 졸라맨은 **왼쪽에서** 오른쪽으로(원본, 오른쪽 향함),
    #   졸라걸은 **오른쪽에서** 왼쪽으로(반전본). 뒤집어 적었던 것을 바로잡음
    (23, 20, "dusk_lanterns",  ["zman_run_side", "zgirl_run_side_l"],
             ["stickman_w1d2_card_fan", "zman_card_hold", "zgirl_card_hold"],
             ["oi", "uyu", "yeou"], []),
    (24, 22, "dusk_lanterns",  [], ["zman_hands_up", "zgirl_hands_up",
                                    "zman_arms_wide", "zgirl_arms_wide"], [], []),
    (25, 14, "dusk_calm",      [], ["sm_holding_mirror", "zman_mirror", "zgirl_mirror"], [], []),
    (26, 18, "dusk_calm",      ["m6_run_turn_r", "m6_run_exit_r"], [], [], []),
]

# 배경 실측 사건 시각 (measure_bg_events.py · 2026-08-12)
BG_EVENTS = {
    "plaza_arrive":   ("분수 정점", 5.75),
    "plaza_gate":     ("비둘기 날아오름", 2.46),
    "stall_cuke":     ("오이 멈춤", 3.79),
    "stall_milk":     ("우유팩 낙하", 5.21),
    "fountain_burst": ("물기둥", 2.25),
    "path_fox":       ("여우 나옴/숨음", 1.92),
    "path_leaves":    ("잎 도달", 6.20),
    "dusk_lanterns":  ("마지막 등", 5.42),
}

# 실측으로 확정된 앵커 좌표 (1280x720)
ANCHORS_MEASURED = {
    "stall_cuke": {"cuke_rest": (610, 509)},
    "stall_milk": {"milk_fall": (958, 607)},
}


def total_sec():
    return sum(s[1] for s in SCENES)


if __name__ == "__main__":
    print("W1-2 %d씬 · %d초 (%d분 %d초)"
          % (len(SCENES), total_sec(), total_sec() // 60, total_sec() % 60))
