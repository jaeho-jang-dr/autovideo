# -*- coding: utf-8 -*-
"""W1-2 자산 검수 — **양방향 대조**.

★[[precheck-asset-fidelity-before-render]] : 빌드는 누락을 조용히 삼킨다(포즈가 없으면
  캐릭터가 사라지고, mp4 가 없으면 정지로 강등된다). 그래서 렌더 전에 두 방향으로 센다.

  ① 씬이 요구하는 자산이 **실제로 있는가**      (없으면 그 씬이 깨진다)
  ② 만들어 둔 자산이 **어느 씬엔가 쓰이는가**   (안 쓰이면 씬 설계가 틀린 것)

    python W1_2/precheck_w12.py
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

import w12_manifest as M                                 # noqa: E402

BG_DIR = "W1_2/bg"
CUT_DIR = "W1_2/motion6_cuts"
POSE_DIR = "W1_2/pose_cuts"
SPOSE_DIR = "W1_2/_poses"
CARD_DIR = "W1_2/cards"
ANCHOR_DIR = "assets/anchors"
DB_POSE_DIR = "assets/graphics/poses"


def has_bg(k):
    return any(os.path.exists(os.path.join(BG_DIR, "%s.%s" % (k, e))) for e in ("mp4", "png"))


STRIDE_DIR = "W1_2/motion6_stride"


def has_cut(k):
    # ★컷은 두 곳에 나뉘어 있다 — 1회 동작은 motion6_cuts, 순환 동작은 motion6_stride
    for base in (CUT_DIR, STRIDE_DIR):
        d = os.path.join(base, k)
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*.png")):
            return True
    # m6_* 는 DB 포즈 폴더에 낱장으로 있다
    return bool(glob.glob(os.path.join(DB_POSE_DIR, k + "_*.png")))


def has_pose(k):
    return (os.path.exists(os.path.join(POSE_DIR, k + ".png"))
            or os.path.exists(os.path.join(SPOSE_DIR, k + ".png"))
            or os.path.exists(os.path.join(DB_POSE_DIR, k + ".png")))


def has_card(k):
    return os.path.exists(os.path.join(CARD_DIR, "card_%s.png" % k))


def main():
    print("=" * 74)
    print("W1-2 자산 검수 — %d씬 · %d초 (%d분 %d초)"
          % (len(M.SCENES), M.total_sec(), M.total_sec() // 60, M.total_sec() % 60))
    print("=" * 74)

    miss = {"배경": set(), "동작컷": set(), "정지포즈": set(), "카드": set(), "앵커": set()}
    used = {"배경": set(), "동작컷": set(), "정지포즈": set(), "카드": set()}
    bad_scenes = []

    for sc, sec, bg, cuts, poses, cards, anchors in M.SCENES:
        bad = []
        used["배경"].add(bg)
        if not has_bg(bg):
            miss["배경"].add(bg); bad.append("배경 " + bg)
        for k in cuts:
            used["동작컷"].add(k)
            if not has_cut(k):
                miss["동작컷"].add(k); bad.append("컷 " + k)
        for k in poses:
            used["정지포즈"].add(k)
            if not has_pose(k):
                miss["정지포즈"].add(k); bad.append("포즈 " + k)
        for k in cards:
            used["카드"].add(k)
            if not has_card(k):
                miss["카드"].add(k); bad.append("카드 " + k)
        if anchors:
            p = os.path.join(ANCHOR_DIR, bg + ".json")
            if not os.path.exists(p):
                miss["앵커"].add(bg); bad.append("앵커 " + bg)
        if bad:
            bad_scenes.append((sc, bad))

    print("\n① 씬이 요구하는데 **없는** 것")
    if not bad_scenes:
        print("   없음 — 26씬 전부 자산이 갖춰졌다")
    for sc, bad in bad_scenes:
        print("   S%-2d  %s" % (sc, " · ".join(bad)))

    print("\n② 만들어 뒀는데 **안 쓰이는** 것")
    made_bg = [os.path.splitext(os.path.basename(p))[0]
               for p in glob.glob(os.path.join(BG_DIR, "*.*"))
               if not os.path.basename(p).startswith("_")]
    made_cut = [os.path.basename(d) for base in (CUT_DIR, STRIDE_DIR)
                for d in glob.glob(os.path.join(base, "*")) if os.path.isdir(d)]
    made_pose = [os.path.splitext(os.path.basename(p))[0]
                 for p in glob.glob(os.path.join(POSE_DIR, "*.png"))]
    made_card = [os.path.basename(p)[5:-4] for p in glob.glob(os.path.join(CARD_DIR, "card_*.png"))]
    for label, made, key in (("배경", made_bg, "배경"), ("동작컷", made_cut, "동작컷"),
                             ("졸라포즈", made_pose, "정지포즈"), ("카드", made_card, "카드")):
        idle = sorted(set(made) - used[key])
        print("   %-8s %2d개 중 안 쓰임 %d개%s"
              % (label, len(made), len(idle), ("  → " + ", ".join(idle)) if idle else ""))

    print("\n③ 배경 사건 시각 (실측)")
    for k, (what, t) in M.BG_EVENTS.items():
        print("   %-16s %-16s %.2fs%s" % (k, what, t, "" if has_bg(k) else "  ★배경없음"))

    n_miss = sum(len(v) for v in miss.values())
    print("\n" + "=" * 74)
    print("빠진 자산 %d종 · 깨지는 씬 %d개" % (n_miss, len(bad_scenes)))
    for kind, v in miss.items():
        if v:
            print("  %-8s %s" % (kind, ", ".join(sorted(v))))
    return 1 if n_miss else 0


if __name__ == "__main__":
    raise SystemExit(main())
