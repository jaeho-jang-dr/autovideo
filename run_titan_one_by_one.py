#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""run_titan_one_by_one.py — Flow 클립을 **하나 만들 때마다 크롬을 껐다 켜서** 생성한다.

★사장님 지시(2026-08-10)
   "계속 실패 난다. 이제부터는 하나 만들고 다시 크롬아웃 → 다시 로그인 →
    프로젝트 찾아서 다시 생성 → 다운로드 → 다시 크롬아웃, 그렇게 해야 할 거야."

실측: 같은 크롬 세션에서 3~4개를 이어 만들면 그 뒤로 생성이 멈춘다.
      (Flow 쪽 세션/레이트 문제로 보인다 — 프롬프트는 들어가는데 새 미디어가 안 뜬다)
      그래서 **클립 1개 = 크롬 1회 기동**으로 못박는다. 느리지만 끝까지 간다.

  python run_titan_one_by_one.py s05_femur s06_tank ...
  python run_titan_one_by_one.py --rest        # 아직 안 만든 것 전부
"""
import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from gen_titan_prompts import SCENES            # noqa: E402

OUT_DIR = "titan_science/keyframes"
COOL = 12          # 크롬 내린 뒤 쉬는 시간(초) — 세션이 완전히 정리되도록


def log(m):
    print(m, flush=True)


def kill_chrome():
    """크롬을 전부 내린다. 프로필 락까지 풀리도록 조금 기다린다."""
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"],
                   capture_output=True, text=True)
    time.sleep(3)
    n = subprocess.run(["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
                       capture_output=True, text=True).stdout.count("chrome.exe")
    log(f"  [크롬] 종료 (남은 프로세스 {n})")


def done(key):
    ext = "mp4" if dict((k, t) for k, t, _ in SCENES)[key] == "VIDEO" else "png"
    p = os.path.join(OUT_DIR, f"{key}.{ext}")
    return os.path.exists(p) and os.path.getsize(p) > 100_000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--rest", action="store_true", help="아직 안 만든 것 전부")
    a = ap.parse_args()

    keys = [k for k, _t, _p in SCENES if not done(k)] if a.rest else a.keys
    if not keys:
        log("만들 것이 없다."); return 0

    log(f"대상 {len(keys)}개: {', '.join(keys)}\n")
    ok, fail = [], []
    for i, k in enumerate(keys, 1):
        log(f"{'='*54}\n[{i}/{len(keys)}] {k}\n{'='*54}")
        kill_chrome()                       # ①크롬 아웃
        time.sleep(COOL)
        r = subprocess.run([sys.executable, "-u", "flow_make_titan.py", k],
                           env={**os.environ, "PYTHONUTF8": "1"})
        # ②flow_make_titan 이 크롬을 새로 띄우고(프로필에 로그인 유지) 프로젝트를 새로 잡는다
        if r.returncode == 0 and done(k):
            ok.append(k); log(f"  ✅ {k}")
        else:
            fail.append(k); log(f"  ★{k} 실패 (rc={r.returncode})")
        kill_chrome()                       # ③다시 크롬 아웃
        time.sleep(COOL)

    log(f"\n{'='*54}")
    log(f"완료 {len(ok)}/{len(keys)}")
    if fail:
        log(f"실패: {', '.join(fail)}")
        log(f"재시도: python run_titan_one_by_one.py {' '.join(fail)}")
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
