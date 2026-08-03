# -*- coding: utf-8 -*-
"""W24 Flow 작업 큐 — 배경 12개가 끝나면 그룹 7편을 이어서 만든다 (2026-08-03).

★Flow 세션은 하나뿐이라 두 작업이 동시에 돌면 서로 화면을 뺏는다.
  그래서 앞 작업이 **완전히 끝난 것을 확인한 뒤** 다음 작업을 시작한다.

순서:
  1) (이미 돌고 있으면) 배경 동영상 12개가 끝날 때까지 기다린다
  2) 그룹 7편 = 점프 3 + 앉기 3 + 꽃다발 1
  3) 새로 나온 7편을 64컷 투명컷으로 자른다
  4) 개별 포즈 추출 계획을 다시 돌린다(신규분 포함)

사용: python run_w24_queue.py
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

GROUP_KEYS = ["a_jump", "b_jump", "c_jump",
              "a_sit_class", "b_sit_class", "c_sit_class", "flower_give"]
MAX_WAIT = 60 * 60      # 앞 작업 대기 상한 1시간


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def bg_running():
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
         "Where-Object { $_.CommandLine -match 'flow_make_bg_w24' } | Measure-Object).Count"],
        capture_output=True, text=True)
    try:
        return int(r.stdout.strip() or 0) > 0
    except ValueError:
        return False


def run(cmd):
    log(f"$ {' '.join(cmd)}")
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONUTF8="1")
    p = subprocess.run([sys.executable] + cmd, env=env)
    return p.returncode == 0


def main():
    t0 = time.time()
    if bg_running():
        log("배경 동영상 작업이 돌고 있다 — 끝날 때까지 기다린다")
        while bg_running():
            if time.time() - t0 > MAX_WAIT:
                log("★대기 상한 초과 — 그래도 이어서 진행한다")
                break
            time.sleep(20)
        log(f"배경 작업 종료 확인 ({time.time()-t0:.0f}초 대기)")
    else:
        log("돌고 있는 배경 작업 없음 — 바로 시작")

    log("[1b] 남은 배경 동영상 11개")
    run(["flow_make_bg_w24.py", "board_time", "classroom_sejong", "gallery_wake",
         "gallery_out", "plaza_gather", "to_hall", "to_path", "to_ruins",
         "to_grass", "to_rose", "to_gallery"])

    log(f"[2] 그룹 7편 생성: {', '.join(GROUP_KEYS)}")
    run(["flow_make_group_w24.py"] + GROUP_KEYS)

    log("[3] 신규 7편 64컷 투명컷")
    run(["cut_w24_group.py"] + GROUP_KEYS)

    log("[4] 개별 포즈 추출(전체 계획 재실행)")
    run(["split_w24_group_poses.py", "--plan"])

    log("큐 완료")


if __name__ == "__main__":
    main()
