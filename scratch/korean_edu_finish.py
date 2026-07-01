#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
korean_education 미완 씬 이어서 생성 (프롬프트 입력=클립보드 붙여넣기 fix 반영).

- autoveo_flow.py 를 --scene N 으로 한 씬씩(SKILL 권장) 순차 실행.
- 씬당 타임아웃(기본 420s)으로 행 방지, 실패해도 다음 씬 진행.
- 각 실행 전 chrome_profile 잔류 chrome 종료 + SingletonLock 제거 (깨끗한 새 프로젝트).
- 결과 클립은 prompts_for_veo/ 에 저장됨 → 끝나고 korean_education/ 로 동기화.
"""
import os
import sys
import time
import shutil
import subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS = r"korean_education/prompts_for_veo.txt"
OUT_DIR = os.path.join(ROOT, "prompts_for_veo")          # autoveo 가 실제로 저장하는 폴더
DEST_DIR = os.path.join(ROOT, "korean_education")         # 최종 프로젝트 폴더
LOCK = os.path.join(ROOT, "assets", "chrome_profile", "SingletonLock")
PER_SCENE_TIMEOUT = 420

MISSING = [46] + list(range(48, 90))   # 20 은 이미 완료


def is_real_mp4(path):
    try:
        with open(path, "rb") as f:
            return b"ftyp" in f.read(16)
    except Exception:
        return False


def kill_profile_chrome():
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | "
                    "Where-Object { $_.CommandLine -match 'chrome_profile' } | "
                    "ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force } catch {} }"],
                   check=False)
    time.sleep(1.0)
    try:
        if os.path.exists(LOCK):
            os.remove(LOCK)
    except Exception:
        pass


def main():
    todo = [n for n in MISSING if not is_real_mp4(os.path.join(OUT_DIR, f"scene_{n}.mp4"))]
    print(f"[START] 미완 {len(todo)}개: {todo}", flush=True)
    ok, fail = [], []

    for i, n in enumerate(todo, 1):
        print("=" * 60, flush=True)
        print(f"[{i}/{len(todo)}] Scene {n} 생성 시작...", flush=True)
        kill_profile_chrome()
        log_path = os.path.join(ROOT, "debug", f"_keu_s{n}.log")
        cmd = [sys.executable, "autoveo_flow.py", "--prompts", PROMPTS, "--scene", str(n)]
        try:
            with open(log_path, "w", encoding="utf-8") as lf:
                subprocess.run(cmd, cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
                               timeout=PER_SCENE_TIMEOUT)
        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] Scene {n} {PER_SCENE_TIMEOUT}s 초과 → 강제 종료, 다음 진행", flush=True)
            kill_profile_chrome()
        except Exception as e:
            print(f"  [ERR] Scene {n}: {e}", flush=True)

        if is_real_mp4(os.path.join(OUT_DIR, f"scene_{n}.mp4")):
            ok.append(n)
            print(f"  [OK] Scene {n} 완료 ✔ ({len(ok)} done)", flush=True)
        else:
            fail.append(n)
            print(f"  [FAIL] Scene {n} 미생성", flush=True)

    # 결과 클립을 korean_education/ 로 동기화
    copied = 0
    for f in os.listdir(OUT_DIR):
        if f.startswith("scene_") and f.endswith(".mp4") and is_real_mp4(os.path.join(OUT_DIR, f)):
            shutil.copy2(os.path.join(OUT_DIR, f), os.path.join(DEST_DIR, f))
            copied += 1

    print("=" * 60, flush=True)
    print(f"[DONE] 성공 {len(ok)} / 실패 {len(fail)}", flush=True)
    print(f"  성공: {ok}", flush=True)
    print(f"  실패: {fail}", flush=True)
    print(f"  korean_education/ 로 복사한 클립: {copied}개", flush=True)
    # 최종 누락 확인
    final_missing = [n for n in range(90)
                     if not is_real_mp4(os.path.join(DEST_DIR, f"scene_{n}.mp4"))]
    print(f"  korean_education 최종 누락: {final_missing}", flush=True)


if __name__ == "__main__":
    main()
