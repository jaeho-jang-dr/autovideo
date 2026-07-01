#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기존 에피소드 일괄 CC 토글 전환기.

각 프로젝트를 make_video.py 로 다시 렌더하되 --no-burn-subs --embed-subs 를 적용해
영어 자막을 굽지 않고 ko/en 소프트 CC 트랙(기본 OFF) + 사이드카 SRT 를 만든 뒤,
결과 mp4 와 .en.srt/.ko.srt 를 Google Drive(AutoVideo)로 복사한다.

★ autoveo_flow.py(브라우저 자동화)는 절대 호출하지 않는다. 클립은 이미 전부 존재.
"""
import os
import sys
import shutil
import subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVE_DST = r"G:\내 드라이브\AutoVideo"

# (이름, scenario, output(절대), intro, outro, annotations)
PROJECTS = [
    {
        "name": "workout_injury_science",
        "scenario": r"workout_injury_science\scenario.txt",
        "output": os.path.join(ROOT, r"workout_injury_science\workout_injury.mp4"),
        "outro": "assets/outro.mp4",
        "annotations": r"workout_injury_science\annotations.json",
    },
    {
        "name": "child_growth_science",
        "scenario": r"child_growth_science\scenario.txt",
        "output": os.path.join(ROOT, r"child_growth_science\child_growth.mp4"),
        "outro": os.path.join(ROOT, r"child_growth_science\scene_0_thumbnail.png"),
        "annotations": r"child_growth_science\annotations.json",
    },
    {
        "name": "binge_watching",
        "scenario": r"binge_watching\scenario.txt",
        "output": os.path.join(ROOT, r"binge_watching\binge_watching.mp4"),
        "outro": "assets/outro.mp4",
        "annotations": r"binge_watching\annotations.json",
    },
]


def copy_to_drive(path):
    if not os.path.exists(path):
        return f"MISSING {os.path.basename(path)}"
    dst = os.path.join(DRIVE_DST, os.path.basename(path))
    shutil.copy2(path, dst)
    ok = os.path.getsize(path) == os.path.getsize(dst)
    return f"{'OK' if ok else 'SIZE-MISMATCH'} {os.path.basename(path)} ({os.path.getsize(path)} bytes)"


def main():
    results = []
    for p in PROJECTS:
        name = p["name"]
        print("=" * 70, flush=True)
        print(f"[{name}] CC 토글 재렌더 시작...", flush=True)
        log_path = os.path.join(ROOT, name, "_build_cc.log")
        cmd = [
            sys.executable, "make_video.py",
            "--scenario", p["scenario"],
            "--output", p["output"],
            "--intro", "assets/intro.mp4",
            "--outro", p["outro"],
            "--annotations", p["annotations"],
            "--no-burn-subs", "--embed-subs",
        ]
        print(f"  cmd: {' '.join(cmd)}", flush=True)
        with open(log_path, "w", encoding="utf-8") as lf:
            rc = subprocess.run(cmd, cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT).returncode

        if rc != 0 or not os.path.exists(p["output"]):
            print(f"[{name}] 렌더 실패 (rc={rc}). 로그: {log_path}", flush=True)
            results.append((name, f"RENDER FAILED rc={rc}"))
            continue

        base = os.path.splitext(p["output"])[0]
        uploads = [p["output"], base + ".en.srt", base + ".ko.srt"]
        msgs = [copy_to_drive(u) for u in uploads]
        print(f"[{name}] 렌더 OK → 드라이브 업로드:", flush=True)
        for m in msgs:
            print(f"    {m}", flush=True)
        results.append((name, "DONE -> " + "; ".join(msgs)))

    print("=" * 70, flush=True)
    print("일괄 전환 요약:", flush=True)
    for name, status in results:
        print(f"  - {name}: {status}", flush=True)


if __name__ == "__main__":
    main()
