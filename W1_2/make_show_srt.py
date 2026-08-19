# -*- coding: utf-8 -*-
"""쇼케이스 **설명 자막** — 구간마다 누가 무슨 동작을 하는지 적어 교정앱에 띄운다.

★사장님 지시(2026-08-12): "렌더 다 하면 내가 고칠 수 있게 교정앱에 띄우고
  **이름과 동작 설명도 추가해서** 보여 줘."

교정앱(`review_lesson.py`)은 SRT 를 타임라인으로 쓴다. 이 쇼케이스는 나레이션이 없으므로
**배치 내용을 SRT 로 만들어** 넣는다. 그러면 구간마다 "여기 이 동작이 이상하다"를
바로 짚을 수 있다.

    python W1_2/make_show_srt.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import render_show as R                                  # noqa: E402

OUT = "W1_2/_show/w1d2_show.ko.srt"

# 동작 키 → 사람이 읽을 이름
NAME = {
    "back_flip": "백플립", "butt_fall": "엉덩방아", "forward_roll": "앞구르기",
    "high_five": "하이파이브", "hop_down": "계단 뛰어내리기", "pick_up": "쭈그려 집기",
    "reach_catch": "손 뻗어 받기", "shoulder_arm": "어깨동무", "sit_stand": "앉기↔기립",
    "skid_stop": "급정지", "tiptoe": "살금살금", "run_front": "정면 달리기",
    "run_back": "후면 달리기", "run_side": "측면 달리기", "run_turn": "달리며 돌기",
    "run_exit": "달려 나가기", "walk_side": "측면 걷기", "walk_turn": "걸으며 돌기",
    "walk_exit": "걸어 나가기", "run_exit_back": "뒤돌아 달려 나가기",
    "walk_exit_back": "뒤돌아 걸어 나가기",
    "zman_run_side": "졸라맨 달리기", "zman_run_side_l": "졸라맨 달리기(좌)",
    "zman_sit_stand": "졸라맨 앉기↔기립", "zman_head_tilt": "졸라맨 고개 갸웃",
    "zgirl_run_side": "졸라걸 달리기", "zgirl_run_side_l": "졸라걸 달리기(좌)",
    "zgirl_high_five": "졸라걸 하이파이브",
}
PATH_NAME = {
    "run_in": "★앞으로 달려 들어오기 (90→600)",
    "run_out": "★뒤로 달려 나가기 (600→90)",
    "diag_away_r": "★사선으로 달려 멀어지기 (오른쪽 위로)",
    "diag_near_l": "★사선으로 달려 다가오기 (왼쪽 아래로)",
    "diag_walk_r": "★사선으로 걸어 멀어지기",
    "deep_in": "★아주 멀리서 달려 들어오기",
    "deep_away_r": "★아주 멀리로 달려 멀어지기",
}
LAY_NAME = {"front": "앞", "mid": "중간", "back": "뒤", "far": "아주 뒤"}


def nice(k):
    if k.startswith("m6:"):
        k = k[3:]
        base = k.rsplit("_", 1)[0] if k[-1] in "rl" and k[-2] == "_" else k
        d = "우" if k.endswith("_r") else ("좌" if k.endswith("_l") else "")
        return NAME.get(base, base) + (("(%s)" % d) if d else "")
    return NAME.get(k, k)


def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return "%02d:%02d:%06.3f" % (h, m, s)


def main():
    cuts, poses = R.load_cuts(), R.load_poses()
    import glob
    cards = sorted(glob.glob(os.path.join(R.CARD_DIR, "*.png")))
    bgs = sorted(os.path.splitext(os.path.basename(p))[0]
                 for p in glob.glob(os.path.join(R.BG_DIR, "*.mp4")) +
                 glob.glob(os.path.join(R.BG_DIR, "*.png")))
    bgs = [b for b in bgs if not b.startswith("_")]

    import random
    rnd = random.Random(12)
    mkeys, pkeys = sorted(cuts), sorted(poses)
    rnd.shuffle(mkeys); rnd.shuffle(pkeys)
    nbg = len(bgs)
    per_m = -(-len(mkeys) // nbg); per_p = -(-len(pkeys) // nbg)
    LAY_CYCLE = ["back", "mid", "front", "far"]
    SEC = 480.0 / nbg

    lines, t0 = [], 0.0
    for i, bg in enumerate(bgs):
        ms = mkeys[i * per_m:(i + 1) * per_m]
        ps = pkeys[i * per_p:(i + 1) * per_p]
        pth = R.PATHS[i % len(R.PATHS)]
        parts = []
        if pth[1] in cuts:
            parts.append(PATH_NAME.get(pth[0], pth[0]))
        for j, k in enumerate(ms):
            parts.append("%s에서 %s" % (LAY_NAME[LAY_CYCLE[j % 4]], nice(k)))
        pose_txt = ", ".join(nice(k) for k in ps[:4])
        head = "[%d/%d] %s" % (i + 1, nbg, bg)
        body = " · ".join(parts)
        tail = ("정지 포즈: " + pose_txt) if pose_txt else ""
        card = os.path.basename(cards[i % len(cards)])[5:-4] if cards else ""
        txt = "%s\n%s\n%s%s" % (head, body, tail, ("  |  카드: " + card) if card else "")
        lines.append((t0, t0 + SEC, txt))
        t0 += SEC

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(lines, 1):
            f.write("%d\n%s --> %s\n%s\n\n"
                    % (i, ts(a).replace(".", ","), ts(b).replace(".", ","), txt))
    print("설명 자막 %d구간 → %s (%.0f초)" % (len(lines), OUT, t0))
    for a, b, txt in lines[:3]:
        print("  %5.1f~%5.1f  %s" % (a, b, txt.replace("\n", " / ")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
