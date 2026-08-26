# -*- coding: utf-8 -*-
"""
scripts/start_review_servers.py — W1-6 교정 리뷰앱 3종 상시 구동 런처
"""
import os
import sys
import subprocess
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_EXE = r"C:\Python313\python.exe"

APPS = [
    ("hangeul_birth_vowels/hangeul_w1_6_stickman_np_np_ko.mp4", "hangeul_birth_vowels/hangeul_w1_6_stickman_np_np.ko.srt", "W1-6 한글판 31씬 전체 통본 (v1)", 8932),
    ("hangeul_birth_vowels/piran_v12.mp4", "hangeul_birth_vowels/piran_v12.ko.srt", "W1-6 피란길 v12", 8930),
    ("hangeul_birth_vowels/seongbukdong_v3.mp4", "hangeul_birth_vowels/seongbukdong_v3.ko.srt", "W1-6 성북동 v3", 8950),
]

def is_running(port):
    try:
        res = urllib.request.urlopen(f"http://localhost:{port}/", timeout=1)
        return res.status == 200
    except Exception:
        return False

def start_app(video, srt, label, port):
    if is_running(port):
        print(f"Port {port} ({label}) is ALREADY RUNNING.")
        return
    
    video_path = os.path.join(ROOT, video)
    srt_path = os.path.join(ROOT, srt)
    script_path = os.path.join(ROOT, "review_lesson.py")
    
    # DETACHED_PROCESS flag for Windows (0x00000008)
    DETACHED_PROCESS = 0x00000008
    
    cmd = [PYTHON_EXE, script_path, video_path, srt_path, label, str(port)]
    subprocess.Popen(
        cmd,
        cwd=ROOT,
        creationflags=DETACHED_PROCESS,
        close_fds=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"Spawned server on port {port}: {label}")

def main():
    print("Starting all W1-6 review servers...")
    for video, srt, label, port in APPS:
        start_app(video, srt, label, port)
    
    time.sleep(2)
    print("\n--- Health Check ---")
    for _, _, label, port in APPS:
        status = "OK (200)" if is_running(port) else "FAILED"
        print(f"http://localhost:{port}/ -> {label} [{status}]")

if __name__ == "__main__":
    main()
