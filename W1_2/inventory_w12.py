# -*- coding: utf-8 -*-
"""W1-2 **전체 에셋 인벤토리** — 무엇이 있고, 무엇이 쓰이고, 무엇이 남는가.

사장님 지시(2026-08-14): "새로 고치고 열심히 만든 모든 동작자산·배경자산·포즈에셋을
**하나도 빼지 않고 다 쓴다**. 필요하면 포즈를 더 만들고 배경을 더 만들어서라도 쓴다.
그 모든 에셋과 배경 동영상을 중심으로 시나리오·동작 시나리오를 다시 쓸 수 있어야 한다."

`precheck_w12.py` 는 **씬이 요구하는 것이 있는가**(빠짐)를 본다.
이 파일은 반대로 **가진 것이 다 쓰이는가**(남음)를 본다. 시나리오 재작성의 재료표다.

중간산출물은 빼고 센다 — 같은 동작의 판올림본(`_v1` `_v2` …)과 공정 찌꺼기
(`_pre_fit` `_prev` `_raw` `_half`)는 최종본 하나로 친다.

    python W1_2/inventory_w12.py            # 표
    python W1_2/inventory_w12.py --json     # 기계용
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

import scene_defs as S                                    # noqa: E402

CUTS = "W1_2/motion6_cuts"
POSES_Z = "W1_2/pose_cuts"          # 졸라맨·졸라걸 정지 포즈
POSES_S = "W1_2/_poses"             # 스틱맨 정지 포즈
BG = "W1_2/bg"
CARDS = "W1_2/cards"

# 판올림·공정 찌꺼기로 치는 꼬리표
SPARE = re.compile(r"_(v\d+|pre_fit|prev|raw|half|old|tmp|test)$")


def is_spare(name):
    return bool(SPARE.search(name))


def newest_of(names):
    """`walk_side` `walk_side_v1` `walk_side_v2` → 최종본 하나만 남긴다.

    판올림본이 있으면 **번호가 가장 큰 것**이 최신이다. 다만 렌더가 실제로 부르는
    이름은 꼬리표 없는 쪽이므로, 둘 다 있으면 **꼬리표 없는 이름**을 대표로 둔다.
    """
    fam = {}
    for n in names:
        base = SPARE.sub("", n)
        fam.setdefault(base, []).append(n)
    out = {}
    for base, members in fam.items():
        rep = base if base in members else sorted(members)[-1]
        out[rep] = sorted(m for m in members if m != rep)
    return out


def used_keys():
    """`scene_defs.SCENES` 가 실제로 부르는 컷·포즈 키."""
    cuts, poses = set(), set()

    def take(key):
        if key.startswith("POSE:"):
            poses.add(key[5:])
        else:
            cuts.add(key.split(":")[-1] if key.startswith("m6:") else key)

    for sc in S.SCENES:
        for b in sc[5]:
            take(b[2])
        for it in sc[6]:
            take(it[0] if len(it) == 3 else it[2])
    return cuts, poses


def scan():
    cut_dirs = [os.path.basename(p) for p in sorted(glob.glob(os.path.join(CUTS, "*")))
                if os.path.isdir(p)]
    zpose = [os.path.splitext(os.path.basename(p))[0]
             for p in sorted(glob.glob(os.path.join(POSES_Z, "*.png")))]
    spose = [os.path.splitext(os.path.basename(p))[0]
             for p in sorted(glob.glob(os.path.join(POSES_S, "*.png")))]
    bgs = [os.path.splitext(os.path.basename(p))[0]
           for p in sorted(glob.glob(os.path.join(BG, "*.mp4")) +
                           glob.glob(os.path.join(BG, "*.png")))]
    cards = [os.path.splitext(os.path.basename(p))[0]
             for p in sorted(glob.glob(os.path.join(CARDS, "*.png")))]
    return cut_dirs, zpose, spose, bgs, cards


def frames_in(key):
    return len(glob.glob(os.path.join(CUTS, key, "*.png")))


def report(as_json=False):
    cut_dirs, zpose, spose, bgs, cards = scan()
    used_c, used_p = used_keys()

    # m6_ 접두는 렌더에서 m6: 로 불린다 — 이름을 맞춰 준다
    def norm(k):
        return k[3:] if k.startswith("m6_") else k

    cut_fam = newest_of(cut_dirs)
    used_norm = {norm(k) for k in used_c}

    live_cuts, spare_cuts, unused_cuts = [], [], []
    for rep, extras in sorted(cut_fam.items()):
        n = frames_in(rep)
        row = {"key": rep, "frames": n, "versions": extras}
        if norm(rep) in used_norm:
            live_cuts.append(row)
        else:
            unused_cuts.append(row)
        spare_cuts += extras

    def split_poses(names):
        fam = newest_of([n for n in names])
        live, unused, sp = [], [], []
        for rep, extras in sorted(fam.items()):
            (live if rep in used_p else unused).append(rep)
            sp += extras
        return live, unused, sp

    zlive, zun, zsp = split_poses(zpose)
    slive, sun, ssp = split_poses(spose)

    bg_used = {sc[1] for sc in S.SCENES}
    bg_fam = newest_of(bgs)
    bg_live = [k for k in sorted(bg_fam) if k in bg_used]
    bg_un = [k for k in sorted(bg_fam) if k not in bg_used]
    bg_sp = [x for v in bg_fam.values() for x in v]

    data = {
        "cuts": {"live": live_cuts, "unused": unused_cuts, "spare": sorted(spare_cuts)},
        "pose_zolla": {"live": zlive, "unused": zun, "spare": sorted(zsp)},
        "pose_stick": {"live": slive, "unused": sun, "spare": sorted(ssp)},
        "bg": {"live": bg_live, "unused": bg_un, "spare": sorted(bg_sp)},
        "cards": cards,
        "scenes": len(S.SCENES),
        "sec": S.total_sec(),
    }
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=1))
        return data

    W = 76
    print("=" * W)
    print("W1-2 에셋 인벤토리 — 현재 동선 %d씬 · %d초 (%d분 %d초)"
          % (data["scenes"], data["sec"], data["sec"] // 60, data["sec"] % 60))
    print("=" * W)

    def block(title, live, unused, spare):
        print("\n▣ %s   최종본 %d종 (쓰는 중 %d · **노는 중 %d**) · 판올림 찌꺼기 %d"
              % (title, len(live) + len(unused), len(live), len(unused), len(spare)))
        if unused:
            names = [u["key"] if isinstance(u, dict) else u for u in unused]
            for i in range(0, len(names), 5):
                print("   놀고 있음: " + ", ".join(names[i:i + 5]))

    block("동작컷", live_cuts, unused_cuts, spare_cuts)
    block("졸라 포즈", zlive, zun, zsp)
    block("스틱맨 포즈", slive, sun, ssp)
    block("배경", bg_live, bg_un, bg_sp)
    print("\n▣ 카드   %d장  %s" % (len(cards), ", ".join(cards)))

    tot_un = len(unused_cuts) + len(zun) + len(sun) + len(bg_un)
    print("\n" + "=" * W)
    print("★놀고 있는 최종본 합계 %d종 — 시나리오를 다시 써서 **전부 태운다**" % tot_un)
    return data


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    report(a.json)
