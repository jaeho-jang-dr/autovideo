# -*- coding: utf-8 -*-
"""W24 클립 **간** 캐릭터 키 일관성 — 같은 인물이 씬마다 다른 크기로 나오는지 본다. 읽기 전용.

   ★사장님 지시(2026-08-04): "그냥 보기에는 오케이라도 다른 키와 같이 사용하면 편차가 커서
     억 하고 놀라게 보일 수 있다."
   클립 하나 안의 상대 비율(verify_w24_group_clip)만으로는 못 잡는다 — 클립 전체가 10% 크게
   그려져도 내부 비율은 맞기 때문이다. 크기를 리사이즈하지 않기로 했으니 클립의 절대 픽셀이
   그대로 화면 크기가 된다. 그래서 **캐릭터별로 모든 클립의 실측 키를 모아** 편차를 낸다.

   누가 누군지는 순위로 맞춘다 — 그 클립 참조 인물을 규격 키 내림차순으로 세우고,
   실측 키도 내림차순으로 세워 짝짓는다(클립별 비율 검사를 통과했다면 순위는 믿을 수 있다).

   사용: python check_w24_cross_clip.py [--tol 3.0]
"""
import argparse
import collections
import glob
import os
import shutil
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

import verify_w24_group_clip as V
import recut_w24_groups as R
from gen_w24_group_prompts import ACTS, CM

CLIPS = "W24/group_clips"
KO = {"injun": "인준", "zollaman": "졸라맨", "teacherjay": "티쳐제이", "stickman": "스틱맨",
      "jieun": "지은", "zollagirl": "졸라걸", "madamjay": "마담제이"}


def log(m):
    print(m, flush=True)


def clip_heights(key):
    """클립 중간 프레임 여러 장의 **평균** 키를 인물별로 낸다(한 장은 자세 때문에 흔들린다)."""
    mp4 = f"{CLIPS}/{key}.mp4"
    if not os.path.exists(mp4):
        return None
    tmp = tempfile.mkdtemp(prefix=f"cc_{key}_")
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4,
                        "-vf", f"fps={R.FPS}", f"{tmp}/%03d.png"], check=True)
        frames = sorted(glob.glob(f"{tmp}/*.png"))[::8]        # 8프레임마다 = 24장
        rows = []
        for f in frames:
            hs = [h for h, _y in V.heights_of(f)]
            if hs:
                rows.append(sorted(hs, reverse=True))
        if not rows:
            return None
        n = collections.Counter(len(r) for r in rows).most_common(1)[0][0]
        rows = [r for r in rows if len(r) == n]
        return [sum(r[i] for r in rows) / len(rows) for i in range(n)]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(tol):
    per = collections.defaultdict(list)          # 캐릭터 → [(동작, 실측px)]
    log("=== 클립 간 캐릭터 키 일관성 (리사이즈 안 하므로 절대 픽셀이 곧 화면 크기) ===")
    for key, _g, refs, _s, _a in ACTS:
        hs = clip_heights(key)
        if not hs:
            continue
        order = sorted(refs, key=lambda r: -CM[r])           # 규격 키 큰 순
        if len(order) != len(hs):
            log(f"  {key:<16} 인물 {len(hs)}명 ≠ 참조 {len(order)}명 — 건너뜀")
            continue
        for r, h in zip(order, hs):
            per[r].append((key, h))
        log(f"  {key:<16} " + " · ".join(f"{KO[r]} {h:.0f}px" for r, h in zip(order, hs)))

    log(f"\n=== 캐릭터별 편차 (허용 {tol:.0f}%) ===")
    bad = []
    for r in sorted(per, key=lambda x: -CM[x]):
        v = [h for _k, h in per[r]]
        lo, hi, mean = min(v), max(v), sum(v) / len(v)
        d = (hi - lo) / mean * 100
        mark = "" if d <= tol else "  ★편차 큼"
        log(f"  {KO[r]:<6} {len(v):>2}클립 · {lo:.0f}~{hi:.0f}px 평균{mean:.0f} · 편차 {d:.1f}%{mark}")
        if d > tol:
            bad.append(r)
            for k, h in sorted(per[r], key=lambda x: -x[1])[:3]:
                log(f"           최대 {k} {h:.0f}px")
            for k, h in sorted(per[r], key=lambda x: x[1])[:1]:
                log(f"           최소 {k} {h:.0f}px")
    log("\n" + ("✅ 전 캐릭터 클립 간 일관" if not bad
                else f"★편차 초과: {', '.join(KO[r] for r in bad)} — 해당 클립 재생성 필요"))
    return 0 if not bad else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tol", type=float, default=3.0)
    raise SystemExit(main(ap.parse_args().tol))
