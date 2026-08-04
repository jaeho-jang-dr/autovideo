# -*- coding: utf-8 -*-
"""W24 그룹 클립: 만들고 → 검사하고 → 떨어진 것만 다시. (사장님 확정 2026-08-04)

   Veo 는 매번 다르게 나오는 확률 기계라 완벽한 프롬프트는 없다. 대신 **자동 검사**로 거른다.
     생성  flow_make_group_w24.py <동작>
     검사  verify_w24_group_clip.check  — 64컷 전부에서 인원수·키 편차·규격 비율·발끝
     실패  _reject_<동작>_a<n>.mp4 로 밀어 두고 재시도. **동작당 최대 3회.**
   3회로도 안 되면 그 동작은 '보류'로 남기고 다음으로 넘어간다 — 무한정 늘어나지 않게.

   사용: python run_w24_groups.py [동작 ...] [--all] [--tries 3]
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

import verify_w24_group_clip as V
from gen_w24_group_prompts import ACTS

CLIPS = "W24/group_clips"


def log(m):
    print(m, flush=True)


def one(key, tries):
    for n in range(1, tries + 1):
        log(f"\n######## {key}  시도 {n}/{tries} ########")
        r = subprocess.run([sys.executable, "flow_make_group_w24.py", key],
                           env={**os.environ, "PYTHONUTF8": "1"})
        mp4 = f"{CLIPS}/{key}.mp4"
        if r.returncode != 0 or not os.path.exists(mp4):
            log(f"  생성 실패 — 재시도")
            continue
        if V.check(key):
            log(f"  ✅ {key} 합격 (시도 {n}회)")
            return True
        rej = f"{CLIPS}/_reject_{key}_a{n}.mp4"
        shutil.move(mp4, rej)
        log(f"  불합격 → {os.path.basename(rej)} 로 밀어 둠")
    log(f"  ★{key} 는 {tries}회로 통과 못 함 — 보류")
    return False


def main(keys, tries):
    done, hold = [], []
    for k in keys:
        (done if one(k, tries) else hold).append(k)
        log(f"\n----- 진행 {len(done) + len(hold)}/{len(keys)} · 합격 {len(done)} · 보류 {len(hold)} -----")
    log("\n" + "=" * 60)
    log(f"합격 {len(done)}/{len(keys)}: {', '.join(done)}")
    if hold:
        log(f"보류 {len(hold)}: {', '.join(hold)}")
    return 0 if not hold else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--tries", type=int, default=3)
    a = ap.parse_args()
    allk = [k for k, *_ in ACTS]
    raise SystemExit(main(allk if a.all else (a.keys or allk), a.tries))
