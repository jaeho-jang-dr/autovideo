#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""최면술 및 팻패밀리 비디오 선희 목소리(UHD 4K + 720p SNS 사본) 재렌더링 마스터 스크립트."""
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

ROOT = r"d:\Entertainments\DevEnvironment\autovideo"
DRIVE = r"G:\내 드라이브\AutoVideo"
AUDIO_DIR = os.path.join(ROOT, "assets", "audio")

# 프로젝트 구성 정의
PROJECTS = {
    "hypnosis_science": {
        "output_dir": os.path.join(ROOT, "hypnosis_science"),
        "compile_args": [
            "--scenario", "hypnosis_science/scenario.txt",
            "--output", os.path.join(ROOT, "hypnosis_science", "hypnosis_science.mp4"),
            "--intro", "assets/intro.mp4",
            "--outro", "assets/outro.mp4",
            "--no-burn-subs", "--embed-subs"
        ],
        "output_base": os.path.join(ROOT, "hypnosis_science", "hypnosis_science.mp4"),
        "sns_output": os.path.join(ROOT, "hypnosis_science", "hypnosis_science_sns_720p.mp4"),
        "drive_names": {
            "mp4": "hypnosis_science.mp4",
            "sns_mp4": "hypnosis_science_sns_720p.mp4",
            "ko_srt": "hypnosis_science.ko.srt",
            "en_srt": "hypnosis_science.en.srt",
            "m4a": "hypnosis_science.en.m4a",
            "thumb": "hypnosis_science_thumbnail.png"
        }
    },
    "pet_family": {
        "output_dir": os.path.join(ROOT, "pet_family"),
        "compile_args": [
            "--scenario", "pet_family/scenario.txt",
            "--output", os.path.join(ROOT, "pet_family", "pet_family.mp4"),
            "--profile", "assets/profiles/dynamic_active.json",
            "--intro", "assets/intro.mp4",
            "--outro", "assets/outro.mp4",
            "--no-burn-subs", "--embed-subs"
        ],
        "output_base": os.path.join(ROOT, "pet_family", "pet_family.mp4"),
        "sns_output": os.path.join(ROOT, "pet_family", "pet_family_sns_720p.mp4"),
        "drive_names": {
            "mp4": "pet_family.mp4",
            "sns_mp4": "pet_family_sns_720p.mp4",
            "ko_srt": "pet_family.ko.srt",
            "en_srt": "pet_family.en.srt",
            "m4a": "pet_family.en.m4a",
            "thumb": "pet_family_thumbnail.png"
        }
    }
}


def run(cmd, log_path=None):
    print(f"Executing: {' '.join(cmd)}")
    if log_path:
        with open(log_path, "w", encoding="utf-8") as f:
            return subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode
    else:
        return subprocess.run(cmd, cwd=ROOT).returncode


def clean_audio_cache():
    print("[CACHE] Clearing assets/audio cache...")
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
    else:
        print(f"  MISSING {os.path.basename(src)}")
        return False
        
    shutil.copy2(src, dst)
    ok = os.path.exists(dst) and os.path.getsize(src) == os.path.getsize(dst)
    print(f"  {'OK' if ok else 'FAIL'} {os.path.basename(src)} -> {os.path.basename(dst)} ({os.path.getsize(dst)} bytes)")
    return ok


def setup_hypnosis():
    print("\n[SETUP] Setting up hypnosis_science directory & resources...")
    hdir = PROJECTS["hypnosis_science"]["output_dir"]
    os.makedirs(hdir, exist_ok=True)
    
    # 1. 복사: assets/videos_hypnosis/scene_[1~16].mp4 -> hypnosis_science/scene_[1~16].mp4
    src_video_dir = os.path.join(ROOT, "assets", "videos_hypnosis")
    for i in range(1, 17):
        src = os.path.join(src_video_dir, f"scene_{i}.mp4")
        dst = os.path.join(hdir, f"scene_{i}.mp4")
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            
    # 2. 복사: assets/images_hypnosis/scene_1.png -> hypnosis_science/scene_0.png (썸네일 베이스)
    src_thumb = os.path.join(ROOT, "assets", "images_hypnosis", "scene_1.png")
    dst_thumb = os.path.join(hdir, "scene_0.png")
    if os.path.exists(src_thumb) and not os.path.exists(dst_thumb):
        shutil.copy2(src_thumb, dst_thumb)
        
    print("[SETUP] hypnosis_science 준비 완료 ✔")


def setup_pet_family():
    print("\n[SETUP] Setting up pet_family directory & resources...")
    pdir = PROJECTS["pet_family"]["output_dir"]
    
    # scene_0.png 가 없는 경우 scene_0.mp4 에서 첫 프레임 추출
    scene0_png = os.path.join(pdir, "scene_0.png")
    scene0_mp4 = os.path.join(pdir, "scene_0.mp4")
    
    if not os.path.exists(scene0_png) and os.path.exists(scene0_mp4):
        print(f"[SETUP] Extracting thumbnail base from {os.path.basename(scene0_mp4)}...")
        cmd = [
            "ffmpeg", "-y",
            "-i", scene0_mp4,
            "-ss", "00:00:00",
            "-vframes", "1",
            scene0_png
        ]
        rc = run(cmd)
        print(f"[SETUP] Thumbnail frame extraction completed (rc={rc}) ✔")
    else:
        print("[SETUP] pet_family scene_0.png 이미 준비됨 ✔")


def transcode_to_sns(src, dst):
    print(f"\n[TRANSCODE] Start encoding SNS 720p: {os.path.basename(src)} -> {os.path.basename(dst)}")
    # H.264 720p 변환 및 용량 제한(300MB 미만) 적용
    cmd = [
        "ffmpeg", "-y",
        "-i", src,
        "-map", "0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "24",
        "-maxrate", "1.8M",
        "-bufsize", "3.6M",
        "-vf", "scale=1280:720",
        "-c:a", "aac",
        "-b:a", "128k",
        "-c:s", "mov_text",
        dst
    ]
    rc = run(cmd)
    if rc != 0:
        print(f"[ERR] Transcode failed for {os.path.basename(src)} (rc={rc})")
        return False
    
    size_mb = os.path.getsize(dst) / (1024 * 1024)
    print(f"[VERIFY] SNS Copy size: {size_mb:.2f} MB (OK)")
    return True


def main():
    print("=" * 60)
    print("  최면술 및 팻패밀리 비디오 선희 목소리(4K + 720p SNS) 빌드")
    print("=" * 60)

    # 1. 각 프로젝트별 에셋 셋업
    setup_hypnosis()
    setup_pet_family()

    # 2. 선희 목소리 전역 설정
    os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"
    print("\n[ENV] Set EDGE_ACTIVE_VOICE = sunhi")

    for name, config in PROJECTS.items():
        print(f"\n========================================================")
        print(f" 프로젝트 빌드 시작: {name.upper()}")
        print(f"========================================================")
        
        # 오디오 캐시 삭제
        clean_audio_cache()
        
        out_base = config["output_base"]
        args = config["compile_args"]
        sns_out = config["sns_output"]
        drive_map = config["drive_names"]
        
        # (1) make_video.py 컴파일
        log_path = os.path.join(config["output_dir"], "_build_all_voices.log")
        print("[1/4] 비디오 UHD 4K 컴파일 시작...")
        rc = run(["python", "make_video.py"] + args, log_path)
        if rc != 0 or not os.path.exists(out_base):
            print(f"[ERR] {name} 4K 컴파일 실패 (rc={rc})")
            continue
        print("[1/4] 비디오 4K 컴파일 완료 ✔")
        
        # (2) 영어 나레이션 추가 (add_en_narration.py)
        shutil.rmtree(os.path.join(config["output_dir"], "_en_tts"), ignore_errors=True)
        print("[2/4] 영어 나레이션 추가 시작...")
        narr_log = os.path.join(config["output_dir"], "_narr_all_voices.log")
        rc = run(["python", "add_en_narration.py", out_base], narr_log)
        print("[2/4] 영어 나레이션 추가 완료 (rc={rc}) ✔")
        
        # (3) 720p SNS용 저용량 사본 트랜스코딩
        print("[3/4] SNS용 720p 복제본 인코딩 시작...")
        if not transcode_to_sns(out_base, sns_out):
            print(f"[ERR] SNS 복제본 인코딩 실패")
            continue
        print("[3/4] SNS용 720p 복제본 인코딩 완료 ✔")
        
        # (4) 구글 드라이브 복사 및 대조 검증
        print("[4/4] 최종 결과물 구글 드라이브 복사 및 검증...")
        base_name = os.path.splitext(out_base)[0]
        files_to_upload = {
            out_base: os.path.join(DRIVE, drive_map["mp4"]),
            sns_out: os.path.join(DRIVE, drive_map["sns_mp4"]),
            base_name + ".ko.srt": os.path.join(DRIVE, drive_map["ko_srt"]),
            base_name + ".en.srt": os.path.join(DRIVE, drive_map["en_srt"]),
            base_name + ".en.m4a": os.path.join(DRIVE, drive_map["m4a"]),
        }
        
        # 썸네일 파일
        thumb_src = os.path.join(config["output_dir"], "scene_0_thumbnail_korean.png")
        if not os.path.exists(thumb_src):
            thumb_src = os.path.join(config["output_dir"], "scene_0_thumbnail.png")
            
        files_to_upload[thumb_src] = os.path.join(DRIVE, drive_map["thumb"])
        
        for src, dst in files_to_upload.items():
            copy_and_verify(src, dst)
            
        print(f"[SUCCESS] {name.upper()} 완료 및 구글 드라이브 업로드 완료!")
        
    print("\n[DONE] 최면술 및 팻패밀리 비디오의 모든 빌드가 성공적으로 종료되었습니다!")


if __name__ == "__main__":
    main()
