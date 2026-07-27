# -*- coding: utf-8 -*-
"""W22 6개 동작 동영상 → 64프레임 투명컷(서기키 770 고정) 배치. 백그라운드 실행용."""
import glob, subprocess, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
JOBS = [
    ("look_out",  "W22/Teacher_JY_looking_out_window_*.mp4"),
    ("magnify",   "W22/Woman_investigating_with_magnify*.mp4"),
    ("point_far", "W22/Woman_pointing_at_distance_*.mp4"),
    ("dream",     "W22/Woman_teacher_clasping_hands_dre*.mp4"),
    ("open_arms", "W22/Woman_teacher_welcoming_gesture_*.mp4"),
    ("wave",      "W22/Woman_waving_on_white_background_*.mp4"),
]
for action, pat in JOBS:
    fs = sorted(glob.glob(pat))
    if not fs:
        print(f"[SKIP] {action}: 파일없음 {pat}", flush=True); continue
    vid = fs[-1]
    print(f"\n===== CUT {action}  <-  {os.path.basename(vid)} =====", flush=True)
    r = subprocess.run([sys.executable, "cut_motion_seq.py", "--video", vid,
                        "--char", "jieun_w22", "--action", action, "--project", "W22"])
    print(f"[{action}] rc={r.returncode}", flush=True)
print("\n===== ALL CUTS DONE =====", flush=True)
