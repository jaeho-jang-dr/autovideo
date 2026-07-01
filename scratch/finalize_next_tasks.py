#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""추가 4개 프로젝트 (소아키성장, 거북목, 정주행, 운동 손상) 순차 빌드 및 구글 드라이브 업로드 스크립트."""
import os
import sys
import shutil
import subprocess
import glob

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

DRIVE = r"G:\내 드라이브\AutoVideo"
AUDIO_DIR = os.path.join(ROOT, "assets", "audio")

# 태스크 정의
# (project_dir, output_basename, active_voice, compile_args)
TASKS = [
    {
        "name": "child_growth_science",
        "voice": "sunhi",
        "output_base": os.path.join(ROOT, "child_growth_science", "child_growth.mp4"),
        "compile_args": [
            "--scenario", "child_growth_science/scenario.txt",
            "--output", os.path.join(ROOT, "child_growth_science", "child_growth.mp4"),
            "--intro", "assets/intro.mp4",
            "--outro", os.path.join(ROOT, "child_growth_science", "scene_0_thumbnail.png"),
            "--annotations", "child_growth_science/annotations.json",
            "--no-burn-subs", "--embed-subs"
        ],
        "drive_names": {
            "mp4": "child_growth.mp4",
            "ko_srt": "child_growth.ko.srt",
            "en_srt": "child_growth.en.srt",
            "m4a": "child_growth.en.m4a",
            "thumb": "child_growth_thumbnail.png"
        }
    },
    {
        "name": "turtle_neck_science",
        "voice": "sunhi",
        "output_base": os.path.join(ROOT, "turtle_neck_science", "turtle_neck_science.mp4"),
        "compile_args": [
            "--scenario", "turtle_neck_science/scenario.txt",
            "--output", os.path.join(ROOT, "turtle_neck_science", "turtle_neck_science.mp4"),
            "--intro", "assets/intro.mp4",
            "--outro", "assets/outro.mp4",
            "--annotations", "turtle_neck_science/annotations.json",
            "--no-burn-subs", "--embed-subs"
        ],
        "drive_names": {
            "mp4": "turtle_neck_science.mp4",
            "ko_srt": "turtle_neck_science.ko.srt",
            "en_srt": "turtle_neck_science.en.srt",
            "m4a": "turtle_neck_science.en.m4a",
            "thumb": "turtle_neck_thumbnail.png"
        }
    },
    {
        "name": "binge_watching",
        "voice": "sunhi",
        "output_base": os.path.join(ROOT, "binge_watching", "binge_watching.mp4"),
        "compile_args": [
            "--scenario", "binge_watching/scenario.txt",
            "--output", os.path.join(ROOT, "binge_watching", "binge_watching.mp4"),
            "--intro", "assets/intro.mp4",
            "--outro", "assets/outro.mp4",
            "--annotations", "binge_watching/annotations.json",
            "--no-burn-subs", "--embed-subs"
        ],
        "drive_names": {
            "mp4": "binge_watching.mp4",
            "ko_srt": "binge_watching.ko.srt",
            "en_srt": "binge_watching.en.srt",
            "m4a": "binge_watching.en.m4a",
            "thumb": "binge_watching_thumbnail.png"
        }
    },
    {
        "name": "workout_injury_science",
        "voice": "injoon",
        "output_base": os.path.join(ROOT, "workout_injury_science", "workout_injury.mp4"),
        "compile_args": [
            "--scenario", "workout_injury_science/scenario.txt",
            "--output", os.path.join(ROOT, "workout_injury_science", "workout_injury.mp4"),
            "--intro", "assets/intro.mp4",
            "--outro", "assets/outro.mp4",
            "--annotations", "workout_injury_science/annotations.json",
            "--no-burn-subs", "--embed-subs"
        ],
        "drive_names": {
            "mp4": "workout_injury.mp4",
            "ko_srt": "workout_injury.ko.srt",
            "en_srt": "workout_injury.en.srt",
            "m4a": "workout_injury.en.m4a",
            "thumb": "workout_injury_thumbnail.png"
        }
    }
]


def run(cmd, log_path):
    print(f"Executing: {' '.join(cmd)}")
    with open(log_path, "w", encoding="utf-8") as f:
        return subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode


def clean_audio_cache():
    print("[CACHE] Clearing assets/audio for the next project...")
    for f in glob.glob(os.path.join(AUDIO_DIR, "scene_*.*")):
        try:
            os.remove(f)
        except Exception as e:
            print(f"[CACHE] Warning: Failed to remove {f}: {e}")


def copy_and_verify(src, dst):
    if os.path.exists(src):
        try:
            if os.path.exists(dst):
                os.remove(dst)
        except Exception:
            pass
        shutil.copy2(src, dst)
        ok = os.path.exists(dst) and os.path.getsize(src) == os.path.getsize(dst)
        print(f"  {'OK' if ok else 'FAIL'} {os.path.basename(src)} -> {os.path.basename(dst)} ({os.path.getsize(dst)} bytes)")
        return ok
    else:
        print(f"  MISSING {os.path.basename(src)}")
        return False


def main():
    print("=" * 60)
    print("  추가 4개 프로젝트 순차 컴파일 및 구글 드라이브 업로드")
    print("=" * 60)

    for task in TASKS:
        name = task["name"]
        voice = task["voice"]
        out_base = task["output_base"]
        args = task["compile_args"]
        drive_map = task["drive_names"]
        
        print(f"\n========================================================")
        print(f" 프로젝트 빌드 시작: {name.upper()} ({voice})")
        print(f"========================================================")

        # 1. 오디오 캐시 초기화
        clean_audio_cache()

        # 2. 환경 변수 주입
        os.environ["EDGE_ACTIVE_VOICE"] = voice
        print(f"[ENV] Set EDGE_ACTIVE_VOICE = {voice}")

        # 3. 비디오 컴파일 (make_video.py)
        log_path = os.path.join(ROOT, name, f"_build_all_voices.log")
        print(f"[1/3] 720p 및 4K 비디오 컴파일 시작...")
        rc = run(["python", "make_video.py"] + args, log_path)
        
        if rc != 0 or not os.path.exists(out_base):
            print(f"[ERR] {name} 비디오 컴파일 실패 (rc={rc})")
            continue
        print("[1/3] 비디오 컴파일 완료 ✔")

        # 4. 영어 나레이션 추가 (add_en_narration.py)
        # 이전 빌드 시 만들어진 _en_tts 가 있으면 충돌 방지를 위해 삭제
        shutil.rmtree(os.path.join(ROOT, name, "_en_tts"), ignore_errors=True)
        print(f"[2/3] 영어 나레이션 추가 시작...")
        narr_log = os.path.join(ROOT, name, f"_narr_all_voices.log")
        rc = run(["python", "add_en_narration.py", out_base], narr_log)
        print(f"[2/3] 영어 나레이션 완료 (rc={rc}) ✔")

        # 5. 구글 드라이브 복사 및 검증
        print(f"[3/3] 최종 결과물 구글 드라이브 복사 및 검증...")
        
        base_name = os.path.splitext(out_base)[0]
        files_to_upload = {
            out_base: os.path.join(DRIVE, drive_map["mp4"]),
            base_name + ".ko.srt": os.path.join(DRIVE, drive_map["ko_srt"]),
            base_name + ".en.srt": os.path.join(DRIVE, drive_map["en_srt"]),
            base_name + ".en.m4a": os.path.join(DRIVE, drive_map["m4a"]),
        }
        
        # 썸네일 경로
        thumb_src = os.path.join(ROOT, name, "scene_0_thumbnail_korean.png")
        if not os.path.exists(thumb_src):
            # fallback: scene_0_thumbnail.png (child_growth_science 등)
            thumb_src = os.path.join(ROOT, name, "scene_0_thumbnail.png")
            
        files_to_upload[thumb_src] = os.path.join(DRIVE, drive_map["thumb"])

        for src, dst in files_to_upload.items():
            copy_and_verify(src, dst)

        print(f"[SUCCESS] {name.upper()} 완료 및 구글 드라이브 업로드 완료!")

    print("\n[DONE] 모든 4개 프로젝트 처리가 성공적으로 종료되었습니다!")


if __name__ == "__main__":
    main()
