# -*- coding: utf-8 -*-
"""W1-3 청계천 애셋 일괄 생성 — 10단계를 **이 프로세스 하나 안에서** 전부 돈다.

★왜 이 파일이 필요한가(2026-08-31) — 에이전트에게 "10개 명령을 순서대로 실행해,
하나 실패해도 계속해"라고 시키면 **에이전트 턴(turn) 경계에서 매번 멈췄다**(실행 속도
문제가 아니라 오케스트레이션을 에이전트 판단에 맡긴 게 문제였다). 그래서 오케스트레이션
자체를 코드로 내려서, 실행자(제미나이)는 **이 스크립트 하나만 켜면** 끝까지 자동으로
돈다 — 중간에 판단할 지점이 없다.

각 단계는 subprocess로 돌리고, 실패해도(0이 아닌 종료코드) 예외를 삼키고 다음 단계로
넘어간다. 끝나면 전체 결과 요약을 찍는다.

사용:
  python W1_3/run_all_assets.py
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PY = sys.executable

if sys.platform == "win32":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


STEPS = [
    ("zgirl_walk_side",     [PY, "W1_2/flow_make_motion6.py", "zgirl_walk_side"]),
    ("zgirl_walk_front",    [PY, "W1_2/flow_make_motion6.py", "zgirl_walk_front"]),
    ("zgirl_run_front",     [PY, "W1_2/flow_make_motion6.py", "zgirl_run_front"]),
    ("zgirl_walk_back",     [PY, "W1_2/flow_make_motion6.py", "zgirl_walk_back"]),
    ("zgirl_run_back",      [PY, "W1_2/flow_make_motion6.py", "zgirl_run_back"]),
    ("zgirl_block_touch",   [PY, "W1_2/flow_make_motion6.py", "zgirl_block_touch"]),
    ("zgirl_stumble_bounce", [PY, "W1_2/flow_make_motion6.py", "zgirl_stumble_bounce"]),
    ("stride(순환5종)",      [PY, "W1_2/stride_motion6.py", "zgirl_walk_side", "zgirl_walk_front",
                              "zgirl_run_front", "zgirl_walk_back", "zgirl_run_back"]),
    ("cut(1회성2종)",        [PY, "W1_2/cut_motion6.py", "zgirl_block_touch", "zgirl_stumble_bounce"]),
    ("배경7종",              [PY, "W1_3/flow_make_bg_cheonggye.py", "--all"]),
]

LOG = "W1_3/_run_all_assets.log"


def log(m):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), m)
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    open(LOG, "w", encoding="utf-8").write("")
    results = []
    t_all = time.time()
    for i, (name, cmd) in enumerate(STEPS, 1):
        log("=" * 60)
        log("[%d/%d] %s 시작 — %s" % (i, len(STEPS), name, " ".join(cmd)))
        t0 = time.time()
        try:
            r = subprocess.run(cmd, cwd=ROOT, timeout=600)
            ok = r.returncode == 0
            log("[%d/%d] %s %s (%.0f초, 종료코드 %d)"
                % (i, len(STEPS), name, "성공" if ok else "실패(계속 진행)", time.time() - t0, r.returncode))
            results.append((name, ok, r.returncode))
        except subprocess.TimeoutExpired:
            log("[%d/%d] %s 타임아웃(600초) — 계속 진행" % (i, len(STEPS), name))
            results.append((name, False, "timeout"))
        except Exception as e:
            log("[%d/%d] %s 예외: %s — 계속 진행" % (i, len(STEPS), name, str(e)[:200]))
            results.append((name, False, str(e)[:80]))

    log("=" * 60)
    log("전체 완료 (%.0f분)" % ((time.time() - t_all) / 60))
    for name, ok, code in results:
        log("  %-24s %s (%s)" % (name, "OK" if ok else "FAIL", code))


if __name__ == "__main__":
    main()
