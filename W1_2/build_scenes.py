# -*- coding: utf-8 -*-
"""W1-2 씬 동선을 **규격대로 자동 생성**한다 — `W1_2_RULES.md` 가 원천.

★손으로 짠 `scene_defs.py` 는 자산을 40종 중 17종밖에 못 썼다.
  규격 §5 "있는 자산을 다 쓴다" · §5 "한 화면에 둘·셋" · §2 "원근 90~600" 을
  지키려면 **배분을 계산으로** 해야 한다.

## 짜는 법
1. 배경 사건 시각(실측)이 씬의 **축**이다 — 그 순간에 맞물릴 동작을 고른다
2. 남은 동작·포즈를 배경들에 **고르게 나눠** 전량 소비한다
3. 씬마다 **주인공 1 + 동시 캐릭터 2~3** 을 세운다(같은 캐릭터 중복 허용)
4. 진입·퇴장을 **앞 씬과 물린다**(§7)
5. 원근은 **90~600** 안에서 씬마다 다르게(§2)

    python W1_2/build_scenes.py          # 동선 계산 결과를 보여준다
    python W1_2/build_scenes.py --write  # scene_plan.py 로 저장
"""
import glob
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import render_show as R                                  # noqa: E402
import scene_defs as S                                   # noqa: E402

# 배경 사건에 맞물릴 동작 — 그 순간 무엇을 하는가
HOOK = {
    "plaza_arrive":   ("skid_stop",   "분수가 다 솟을 때 급정지"),
    "plaza_gate":     ("forward_roll", "비둘기가 날 때 굴러 나간다"),
    "stall_cuke":     ("pick_up",     "오이가 멈출 때 집는다"),
    "stall_milk":     ("reach_catch", "우유팩이 떨어질 때 받는다"),
    "fountain_burst": ("back_flip",   "물기둥에 놀라 백플립"),
    "path_fox":       ("butt_fall",   "여우가 숨자 엉덩방아"),
    "path_leaves":    ("reach_catch", "잎이 내려올 때 잡는다"),
    "dusk_lanterns":  ("high_five",   "마지막 등이 켜질 때 하이파이브"),
}

# 진입·퇴장 어휘 (§7) — 돌려 쓰며 지루하지 않게
ENTER = ["in_front", "in_diag_l", "in_walk_l", "in_diag_r", "stay", "in_walk_r"]
EXIT = ["out_run_r", "out_back", "out_roll", "out_run_l", "hold", "out_tip"]

FAR, NEAR = 90, 600


def enter_beat(kind, t0, t1, x_end, h_end):
    """진입 — 규격 §2 원근(90~600)을 살려 들어온다."""
    if kind == "in_front":
        return (t0, t1, "run_front", x_end, x_end, FAR, h_end)
    if kind == "in_diag_l":
        return (t0, t1, "m6:run_side_l", 1340, x_end, FAR, h_end)
    if kind == "in_diag_r":
        return (t0, t1, "m6:run_side_r", -60, x_end, FAR, h_end)
    if kind == "in_walk_l":
        return (t0, t1, "m6:walk_side_r", -60, x_end, h_end, h_end)
    if kind == "in_walk_r":
        return (t0, t1, "m6:walk_side_l", 1340, x_end, h_end, h_end)
    return None                                          # stay


def exit_beat(kind, t0, t1, x0, h0):
    if kind == "out_run_r":
        return (t0, t1, "m6:run_side_r", x0, 1360, h0, 240)
    if kind == "out_run_l":
        return (t0, t1, "m6:run_side_l", x0, -80, h0, 240)
    if kind == "out_back":
        return (t0, t1, "run_back", x0, x0, h0, FAR)
    if kind == "out_roll":
        return (t0, t1, "forward_roll", x0, 180, h0, 260)
    if kind == "out_tip":
        return (t0, t1, "tiptoe", x0, 200, h0, 360)
    return None                                          # hold


def main():
    cuts, poses = R.load_cuts(), R.load_poses()
    bgs = [b for b in sorted(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(R.BG_DIR, "*.mp4")) +
        glob.glob(os.path.join(R.BG_DIR, "*.png"))) if not b.startswith("_")]

    # ★이야기 순서를 지킨다 — 광장 → 계단 → 좌판 → 분수 → 벤치 → 산책로 → 해질녘
    STORY = ["plaza_arrive", "plaza_gate", "steps_seat", "steps_rail",
             "stall_cuke", "stall_milk", "stall_rail", "fountain_burst",
             "bench_pair", "bench_open", "path_fox", "path_leaves",
             "dusk_lanterns", "dusk_calm"]
    bgs.sort(key=lambda b: STORY.index(b) if b in STORY else 99)

    hooked = {HOOK[b][0] for b in bgs if b in HOOK}
    rest = [k for k in sorted(cuts) if k not in hooked]
    pkeys = sorted(poses)
    rnd = random.Random(7)
    rnd.shuffle(rest)
    rnd.shuffle(pkeys)

    n = len(bgs)
    per_c = -(-len(rest) // n)
    per_p = -(-len(pkeys) // n)

    print("배경 %d · 동작 %d종(사건용 %d + 나머지 %d) · 포즈 %d장"
          % (n, len(cuts), len(hooked), len(rest), len(pkeys)))
    print("배경마다 동작 %d + 포즈 %d 를 얹는다 → 전량 소비\n" % (per_c, per_p))

    plan, prev_exit = [], "hold"
    for i, bg in enumerate(bgs):
        ev = S.EVENT.get(bg)
        # 앞 씬이 나갔으면 반대편에서 들어온다(§7)
        if prev_exit in ("out_run_r",):
            ein = "in_diag_l"
        elif prev_exit in ("out_run_l", "out_roll", "out_tip"):
            ein = "in_diag_r"
        elif prev_exit == "out_back":
            ein = "in_front"
        else:
            ein = ENTER[i % len(ENTER)]
        eout = EXIT[i % len(EXIT)]
        prev_exit = eout

        sec = 26 if ev else 22
        cs = rest[i * per_c:(i + 1) * per_c]
        ps = pkeys[i * per_p:(i + 1) * per_p]
        hook = HOOK.get(bg)
        plan.append(dict(bg=bg, sec=sec, ein=ein, eout=eout, ev=ev,
                         hook=hook, cuts=cs, poses=ps))

        print("S%-2d %-15s %2d초 %-10s→%-10s%s" % (i + 1, bg, sec, ein, eout,
              ("  ★%s %.2fs — %s" % (ev[0], ev[1], hook[1])) if (ev and hook) else ""))
        print("      동작 %s" % ", ".join(cs))
        print("      포즈 %s" % ", ".join(ps[:5]))

    tot = sum(p["sec"] for p in plan)
    print("\n합계 %d씬 · %d초 (%d분 %d초)" % (len(plan), tot, tot // 60, tot % 60))
    return plan


if __name__ == "__main__":
    main()
