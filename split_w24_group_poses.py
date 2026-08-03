# -*- coding: utf-8 -*-
"""★W24 그룹 64컷 → 캐릭터 개별 포즈 추출 (2026-08-03).

사장님 승인(2026-08-03): "그룹컷에서 뽑아쓰고 없는 것만 새로 만들자."

그룹 컷은 이미 투명컷이고 인물별로 **덩어리(blob)가 분리**돼 있다. 덩어리를 쪼개면
개별 정지 포즈가 공짜로 나온다. 같은 영상에서 나왔으니 캐릭터 일관성도 자동으로 맞는다.

★누가 누구인지는 **색으로 판별**한다(같은 그룹 안에서는 색이 겹치지 않는다):
  A그룹  졸라맨=머리가 새까맣다 / 졸라걸=주황 머리 / 스틱맨=시안 발광 또는 무채색
  B그룹  인준=남색 티셔츠 / 지은=노란 원피스
  C그룹  마담제이=코랄 조끼 / 티쳐제이=파란 체크 셔츠 + 베이지 바지
※손을 맞잡은 프레임은 두 사람이 한 덩어리가 된다 → 덩어리 수가 모자라면 그 프레임은 건너뛴다.

키 통일: 캐릭터별 규격 px(W24_concept.md)에 맞춘다.

사용:
  python split_w24_group_poses.py --list
  python split_w24_group_poses.py a_write_jamo:12=write_jamo
  python split_w24_group_poses.py --plan          # 계획표대로 일괄 추출
"""
import argparse
import os

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

CUTS = "W24/group_cuts"
OUT_DIR = "assets/graphics/poses"
PREFIX = "w24"

SPEC = {"zolla_man": 761, "stickman": 749, "zolla_girl": 697,
        "injun": 770, "jieun": 706, "teacher_jay": 749, "madam_jay": 693}
MEMBERS = {
    "a": ["zolla_man", "zolla_girl", "stickman"],
    "b": ["injun", "jieun"],
    "c": ["madam_jay", "teacher_jay"],
}
# ★그룹 접두어(a/b/c)로 안 풀리는 영상은 여기에 따로 적는다.
#   `flower_give` 는 티쳐제이(C)+인준(B) 이 섞여 있어 접두어 규칙이 안 통했다 →
#   그래서 꽃다발 포즈 2장이 계속 빠졌다(2026-08-03).
MEMBERS_BY_KEY = {
    "flower_give": ["teacher_jay", "injun"],
}


def members_of(key):
    return MEMBERS_BY_KEY.get(key) or MEMBERS[key[0]]

# ★추출 계획 — 그룹컷 <키>:<컷번호> 에서 뽑을 포즈 이름
#   컷번호는 64컷(00~63) 중 그 포즈가 가장 또렷한 지점.
PLAN = [
    # A그룹 — 글자·수
    ("a_write_jamo", 12, {"zolla_man": "write_jamo", "zolla_girl": "write_jamo",
                          "stickman": "write_jamo"}),
    ("a_write_jamo", 34, {"zolla_girl": "touch_lips"}),
    ("a_stack_block", 20, {"zolla_man": "lift_block_up"}),
    ("a_stack_block", 40, {"zolla_girl": "stack_block", "stickman": "point_up"}),
    ("a_count_up", 10, {"zolla_man": "count_one"}),
    ("a_count_up", 32, {"zolla_girl": "count_two"}),
    ("a_count_up", 56, {"stickman": "count_three"}),
    ("a_count_up", 62, {"zolla_man": "look_r", "zolla_girl": "nod_to_l", "stickman": "look_l"}),
    # B그룹 — 거리의 말
    ("b_ask_price", 16, {"injun": "ask_price"}),
    ("b_ask_price", 40, {"jieun": "show_price"}),
    ("b_ask_price", 62, {"injun": "present_right", "jieun": "listen_l"}),
    ("b_hold_strap", 30, {"injun": "hold_strap", "jieun": "hold_strap"}),
    ("b_point_way", 20, {"jieun": "point_way_r"}),
    ("b_point_way", 44, {"injun": "follow_gaze_r"}),
    ("b_highfive", 18, {"injun": "highfive_r", "jieun": "highfive_l"}),
    ("b_highfive", 60, {"injun": "listen_r", "jieun": "tilt_smile"}),
    # C그룹 — 마음의 말
    ("c_talk_sit", 8, {"teacher_jay": "sit_talk_r", "madam_jay": "sit_listen_l"}),
    ("c_talk_sit", 26, {"teacher_jay": "count_routine_r", "madam_jay": "sit_nod_l"}),
    ("c_talk_sit", 54, {"teacher_jay": "tap_date_r", "madam_jay": "tap_date_l"}),
    ("c_weather_look", 30, {"teacher_jay": "look_up_r", "madam_jay": "look_up_l"}),
    ("c_emotion_face", 14, {"teacher_jay": "face_upset_r"}),
    ("c_emotion_face", 44, {"madam_jay": "face_glad_l"}),
    ("c_nod_agree", 20, {"teacher_jay": "nod_to_r"}),
    ("c_nod_agree", 44, {"madam_jay": "nod_to_l"}),
    # ★교실 앉기 3박자 — 한 편에서 포즈 3종씩 (듣기 08 / 박수 34 / 정면 56)
    ("a_sit_class", 8, {"zolla_man": "sit_listen", "zolla_girl": "sit_listen",
                        "stickman": "sit_listen"}),
    ("a_sit_class", 34, {"zolla_man": "sit_clap", "zolla_girl": "sit_clap",
                         "stickman": "sit_clap"}),
    ("a_sit_class", 56, {"zolla_man": "sit_look_front", "zolla_girl": "sit_look_front",
                         "stickman": "sit_look_front"}),
    ("b_sit_class", 8, {"injun": "sit_listen", "jieun": "sit_listen"}),
    ("b_sit_class", 34, {"injun": "sit_clap", "jieun": "sit_clap"}),
    ("b_sit_class", 56, {"injun": "sit_look_front", "jieun": "sit_look_front"}),
    ("c_sit_class", 8, {"teacher_jay": "sit_listen", "madam_jay": "sit_listen"}),
    ("c_sit_class", 34, {"teacher_jay": "sit_clap", "madam_jay": "sit_clap"}),
    ("c_sit_class", 56, {"teacher_jay": "sit_look_front", "madam_jay": "sit_look_front"}),
    # ★수료식 꽃다발 — 주는 순간(20) / 받고 인사(58)
    ("flower_give", 20, {"teacher_jay": "give_flower"}),
    ("flower_give", 58, {"injun": "receive_flower"}),
    # ★점프 전환 — 공중 정점(28)도 한 장씩 뽑아 둔다
    ("a_jump", 28, {"zolla_man": "jump_up", "zolla_girl": "jump_up", "stickman": "jump_up"}),
    ("b_jump", 28, {"injun": "jump_up", "jieun": "jump_up"}),
    ("c_jump", 40, {"teacher_jay": "stand_up", "madam_jay": "stand_up"}),
]


def log(m):
    print(m, flush=True)


def blobs_of(rgba, want):
    """알파에서 덩어리를 뽑아 왼→오른쪽 순으로 돌려준다."""
    al = rgba[:, :, 3]
    lbl, n = ndimage.label(al > 40)
    if n == 0:
        return []
    sizes = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    big = [i + 1 for i, s in enumerate(sizes) if s >= sizes.max() * 0.05]
    out = []
    for i in big:
        ys, xs = np.where(lbl == i)
        out.append(dict(idx=i, cx=xs.mean(), x0=xs.min(), x1=xs.max() + 1,
                        y0=ys.min(), y1=ys.max() + 1, mask=(lbl == i)))
    out.sort(key=lambda b: b["cx"])
    return out


def classify(rgba, b, members):
    """색으로 누구인지 고른다. members 안에서만 고르면 되므로 색이 겹치지 않는다."""
    m = b["mask"]
    px = rgba[:, :, :3][m].astype(int)
    r, g, bl = px[:, 0], px[:, 1], px[:, 2]
    lo = px.min(1); hi = px.max(1); sat = hi - lo
    n = max(1, len(px))
    orange = ((r > 170) & (g > 80) & (g < 190) & (bl < 110) & (sat > 60)).sum() / n
    cyan = ((bl > 170) & (g > 150) & (r < 170) & (sat > 40)).sum() / n
    navy = ((bl > 80) & (bl < 190) & (r < 110) & (g < 130) & (sat > 40)).sum() / n
    yellow = ((r > 200) & (g > 180) & (bl < 165) & (sat > 45)).sum() / n
    coral = ((r > 195) & (g > 70) & (g < 165) & (bl < 140) & (sat > 75)).sum() / n
    # 머리(위 22%)가 새까만가 — 졸라맨의 표식
    hy = b["y0"] + int((b["y1"] - b["y0"]) * 0.22)
    head = m.copy(); head[hy:, :] = False
    hpx = rgba[:, :, :3][head].astype(int)
    black_head = ((hpx.max(1) < 90).sum() / max(1, len(hpx))) if len(hpx) else 0.0

    score = {}
    for c in members:
        if c == "zolla_man":
            score[c] = black_head * 3 - orange * 5 - cyan * 5
        elif c == "zolla_girl":
            score[c] = orange * 8
        elif c == "stickman":
            score[c] = cyan * 8 + (0.4 if (orange < 0.01 and black_head < 0.25) else 0)
        elif c == "injun":
            score[c] = navy * 6
        elif c == "jieun":
            score[c] = yellow * 6
        elif c == "madam_jay":
            score[c] = coral * 6
        elif c == "teacher_jay":
            score[c] = navy * 2 + (0.5 if coral < 0.02 else 0)
    return max(score, key=score.get), score


def extract(key, cut, mapping, dry=False):
    src = f"{CUTS}/{key}/{cut:02d}.png"
    if not os.path.exists(src):
        log(f"  ★컷 없음: {src}")
        return 0
    members = members_of(key)
    rgba = np.array(Image.open(src).convert("RGBA"))
    bs = blobs_of(rgba, len(members))
    if len(bs) < len(mapping):
        log(f"  ※{key}:{cut:02d} 덩어리 {len(bs)}개 < 필요 {len(mapping)}개 — 붙어 있는 프레임, 건너뜀")
        return 0

    # ★한 사람당 덩어리 하나씩 **최적 배정**한다.
    #   그냥 최고점만 고르면 두 덩어리가 같은 사람으로 몰려 나머지가 '못 찾음'이 된다.
    from scipy.optimize import linear_sum_assignment
    cand = members
    cost = np.zeros((len(bs), len(cand)))
    for i, b in enumerate(bs):
        _, sc = classify(rgba, b, cand)
        for j, c in enumerate(cand):
            cost[i, j] = -sc.get(c, 0.0)
    ri, ci = linear_sum_assignment(cost)
    named = {cand[j]: bs[i] for i, j in zip(ri, ci)}

    # ★두 사람이 손을 잡아 한 덩어리가 된 컷은 폭이 비정상으로 넓다 → 그 컷은 버린다
    canvas_w = rgba.shape[1]
    for c, b in list(named.items()):
        if len(members) > 1 and (b["x1"] - b["x0"]) > canvas_w * 0.62:
            log(f"  ※{key}:{cut:02d} {c} 덩어리 폭 {(b['x1']-b['x0'])}px — 두 사람이 붙었다, 건너뜀")
            named.pop(c)

    made = 0
    for char, pose in mapping.items():
        b = named.get(char)
        if b is None:
            log(f"  ★{key}:{cut:02d} 에서 {char} 못 찾음")
            continue
        pad = 6
        y0 = max(0, b["y0"] - pad); y1 = min(rgba.shape[0], b["y1"] + pad)
        x0 = max(0, b["x0"] - pad); x1 = min(rgba.shape[1], b["x1"] + pad)
        sub = rgba[y0:y1, x0:x1].copy()
        # 다른 사람 픽셀은 지운다(겹친 경우 대비)
        sub[:, :, 3] = np.where(b["mask"][y0:y1, x0:x1], sub[:, :, 3], 0)
        im = Image.fromarray(sub)
        h = b["y1"] - b["y0"]
        scale = SPEC[char] / h if h else 1.0
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                       Image.LANCZOS)
        out = f"{OUT_DIR}/{PREFIX}_{char}_{pose}.png"
        if not dry:
            os.makedirs(OUT_DIR, exist_ok=True)
            im.save(out)
        log(f"  {char:12s} {pose:16s} {im.width}x{im.height}  ← {key}:{cut:02d}")
        made += 1
    return made


def main(a):
    if a.list:
        for k, c, mp in PLAN:
            log(f"  {k:16s} 컷{c:02d}  {', '.join(f'{ch}={ps}' for ch, ps in mp.items())}")
        return
    if a.plan:
        total = 0
        for k, c, mp in PLAN:
            total += extract(k, c, mp, a.dry)
        log(f"\n✅ 개별 포즈 {total}장 추출 → {OUT_DIR}/{PREFIX}_*.png")
        return
    for spec in a.specs:
        key_cut, pose = spec.split("=")
        key, cut = key_cut.split(":")
        extract(key, int(cut), {c: pose for c in members_of(key)}, a.dry)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="*")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry", action="store_true")
    main(ap.parse_args())
