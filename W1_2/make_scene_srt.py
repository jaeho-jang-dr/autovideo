# -*- coding: utf-8 -*-
"""씬 동선 **설명 자막** — 교정앱에서 구간마다 무슨 동작인지 보이게.

★사장님 지시: "이름과 동작 설명도 추가해서 보여 줘."
비트 하나가 자막 한 줄이 된다. 배경 사건과 맞물리는 대목은 ★로 표시한다.

    python W1_2/make_scene_srt.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import scene_defs as S                                   # noqa: E402

OUT = "W1_2/_scenes/w1d2_scenes.ko.srt"

NAME = {
    "back_flip": "백플립", "butt_fall": "엉덩방아", "forward_roll": "앞구르기",
    "high_five": "하이파이브", "hop_down": "계단 뛰어내리기", "pick_up": "쭈그려 집기",
    "reach_catch": "손 뻗어 받기", "shoulder_arm": "어깨동무", "sit_stand": "앉기↔기립",
    "skid_stop": "급정지", "tiptoe": "살금살금", "run_front": "정면 달리기(3배속)",
    "run_back": "후면 달리기(3배속)", "zgirl_run_side": "졸라걸 달리기",
    "sm_greeting_wave": "손 흔들기", "sm_presenting": "두 손 펴 설명",
    "sm_pointing_left": "가리키기", "sm_counting_five": "손가락 다섯 세기",
    "sm_arms_out_wide": "두 팔 벌리기", "sm_holding_mirror": "거울 들기",
    "stickman_w1d2_card_hold": "카드 들기", "stickman_w1d2_card_fan": "카드 부채",
    "stickman_w1d2_surprise": "놀람", "stickman_w1d2_grab_rail_r": "난간 잡고 걸터앉기",
    "stickman_w1d2_lean_rail_r": "난간에 기대기",
    "stickman_w1d2_crouch_ground_r": "쭈그려 살피기",
    "stickman_w1d2_mouth_o": "입 모양 오", "stickman_w1d2_mouth_a": "입 모양 아",
    "zman_shoulder_recv": "졸라맨 앉아 있기", "zman_attention": "졸라맨 차렷",
    "zman_hands_up": "졸라맨 두 손 번쩍", "zgirl_hands_up": "졸라걸 두 손 번쩍",
    "zman_mirror": "졸라맨 거울", "zgirl_mirror": "졸라걸 거울",
    "zgirl_high_five": "졸라걸 하이파이브",
}


def nice(k):
    if k.startswith("POSE:"):
        k = k[5:]
    if k.startswith("m6:"):
        k = k[3:]
        d = "우" if k.endswith("_r") else ("좌" if k.endswith("_l") else "")
        base = k[:-2] if d else k
        n = {"walk_side": "옆으로 걷기", "run_side": "옆으로 달리기(2배속)",
             "walk_turn": "걸으며 돌기", "run_turn": "달리며 돌기",
             "walk_exit": "걸어 나가기", "run_exit": "달려 나가기(2배속)"}.get(base, base)
        return n + (("(%s)" % d) if d else "")
    return NAME.get(k, k)


def ts(t):
    return "%02d:%02d:%06.3f" % (int(t // 3600), int((t % 3600) // 60), t % 60)


def main():
    lines, base = [], 0.0
    for n, bg, sec, ein, eout, beats, extra in S.SCENES:
        ev = S.EVENT.get(bg)
        for b in beats:
            t0, t1, key, x0, x1, h0, h1 = b[:7]
            hit = ""
            if ev and abs(t0 - ev[1]) < 0.6:
                hit = "  ★%s" % ev[0]
            move = ""
            if abs(x1 - x0) > 40:
                move = " · %s로 이동" % ("오른쪽" if x1 > x0 else "왼쪽")
            if abs(h1 - h0) > 30:
                move += " · %s" % ("다가옴 %d→%d" % (h0, h1) if h1 > h0
                                   else "멀어짐 %d→%d" % (h0, h1))
            txt = "S%d %s\n%s%s%s" % (n, bg, nice(key), move, hit)
            lines.append((base + t0, base + t1, txt))
        base += sec

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(lines, 1):
            f.write("%d\n%s --> %s\n%s\n\n"
                    % (i, ts(a).replace(".", ","), ts(b).replace(".", ","), txt))
    print("설명 자막 %d줄 → %s (%.0f초)" % (len(lines), OUT, base))
    for a, b, t in lines[:5]:
        print("  %5.1f~%5.1f  %s" % (a, b, t.replace("\n", " / ")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
