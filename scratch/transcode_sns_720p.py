#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SNS용 720p 저용량 복제본 변환 및 구글 드라이브 업로드 스크립트."""
import os
import sys
import shutil
import subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = r"d:\Entertainments\DevEnvironment\autovideo"
DRIVE = r"G:\내 드라이브\AutoVideo"
MAX_SIZE = 300 * 1024 * 1024  # 300MB

TASKS = [
    {
        "name": "child_growth_science",
        "src": os.path.join(ROOT, "child_growth_science", "child_growth.mp4"),
        "dst": os.path.join(ROOT, "child_growth_science", "child_growth_sns_720p.mp4"),
        "drive_name": "child_growth_sns_720p.mp4"
    },
    {
        "name": "turtle_neck_science",
        "src": os.path.join(ROOT, "turtle_neck_science", "turtle_neck_science.mp4"),
        "dst": os.path.join(ROOT, "turtle_neck_science", "turtle_neck_science_sns_720p.mp4"),
        "drive_name": "turtle_neck_science_sns_720p.mp4"
    },
    {
        "name": "binge_watching",
        "src": os.path.join(ROOT, "binge_watching", "binge_watching.mp4"),
        "dst": os.path.join(ROOT, "binge_watching", "binge_watching_sns_720p.mp4"),
        "drive_name": "binge_watching_sns_720p.mp4"
    },
    {
        "name": "workout_injury_science",
        "src": os.path.join(ROOT, "workout_injury_science", "workout_injury.mp4"),
        "dst": os.path.join(ROOT, "workout_injury_science", "workout_injury_sns_720p.mp4"),
        "drive_name": "workout_injury_sns_720p.mp4"
    }
]

def transcode(src, dst):
    print(f"\n[TRANSCODE] Start encoding 720p: {os.path.basename(src)} -> {os.path.basename(dst)}")
    # FFmpeg Command
    # -map 0 : 모든 스트림(비디오, 다국어 오디오, 자막 트랙)을 다 포함하여 복제
    # -c:v libx264 -preset medium -crf 24 : 720p에 적합하고 용량이 작게 설계
    # -maxrate 1.8M -bufsize 3.6M : 비디오 비트레이트가 과도하게 치솟지 않도록 제어
    # -vf scale=1280:720 : 해상도를 720p로 고정 다운스케일
    # -c:a aac -b:a 128k : 오디오 트랙을 고압축 aac 128k로 트랜스코딩
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
    
    print(f"Executing command: {' '.join(cmd)}")
    rc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if rc.returncode != 0:
        print("[ERR] FFmpeg Transcoding failed!")
        print(rc.stdout.decode("utf-8", errors="ignore"))
        return False
        
    print("[TRANSCODE] Encoding finished successfully.")
    return True

def copy_and_verify(src, dst):
    print(f"[DRIVE] Copying to Drive: {os.path.basename(src)} -> {dst}")
    if os.path.exists(dst):
        try:
            os.remove(dst)
        except Exception:
            pass
    shutil.copy2(src, dst)
    ok = os.path.exists(dst) and os.path.getsize(src) == os.path.getsize(dst)
    if ok:
        print(f"[DRIVE] Copy success: {os.path.basename(dst)} ({os.path.getsize(dst)} bytes)")
    else:
        print(f"[DRIVE] Copy failed or size mismatch!")
    return ok

def main():
    print("=" * 60)
    print("  SNS용 720p 저용량 복제본 일괄 변환 및 업로드")
    print("=" * 60)
    
    success_count = 0
    for task in TASKS:
        name = task["name"]
        src = task["src"]
        dst = task["dst"]
        drive_dst = os.path.join(DRIVE, task["drive_name"])
        
        print(f"\n>>> Processing: {name.upper()}")
        
        if not os.path.exists(src):
            print(f"[ERR] Source 4K video not found: {src}")
            continue
            
        # 1. 720p 변환
        if not transcode(src, dst):
            print(f"[ERR] Transcode failed for {name}")
            continue
            
        # 2. 용량 한도 체크 (300MB 미만)
        size = os.path.getsize(dst)
        size_mb = size / (1024 * 1024)
        print(f"[VERIFY] Output size: {size_mb:.2f} MB ({size} bytes)")
        
        if size >= MAX_SIZE:
            print(f"[ERR] File size exceeds 300MB limit: {size_mb:.2f} MB")
            continue
        print(f"[VERIFY] File size is within 300MB limit (OK)")
        
        # 3. 구글 드라이브 복제
        if copy_and_verify(dst, drive_dst):
            print(f"[SUCCESS] Completed task for {name.upper()}")
            success_count += 1
        else:
            print(f"[ERR] Drive upload failed for {name}")
            
    print("\n" + "=" * 60)
    print(f"  모든 작업 종료. (성공: {success_count}/{len(TASKS)})")
    print("=" * 60)

if __name__ == "__main__":
    main()
