# -*- coding: utf-8 -*-
"""거북목 쇼츠 9:16 클립 생성 — 제미나이가 실행. scene 2,4,5를 9:16으로 생성.
scene_1,3은 이미 있음(건드리지 않음). 결과는 turtle_short_v916/scene_N.mp4."""
import subprocess, os, sys
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PROMPTS = "turtle_short_v916_prompts.txt"
NEED = [2, 4, 5]
GOOD_PROFILES = [1, 0]  # 로그인 확실한 프로필만 (2,4,5는 로그인 약함)
for i, n in enumerate(NEED):
    out = f"turtle_short_v916/scene_{n}.mp4"
    if os.path.exists(out):
        # 9:16 확인
        w = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
            "-show_entries","stream=width","-of","csv=p=0",out],
            capture_output=True,text=True).stdout.strip()
        if w == "720":
            print(f"[SKIP] scene_{n} 이미 9:16 있음"); continue
        os.remove(out)  # 잘못된 아스펙트 삭제
    prof = GOOD_PROFILES[i % len(GOOD_PROFILES)]
    print(f"=== scene {n} 생성 (프로필 {prof}, 9:16) ===", flush=True)
    r = subprocess.run(["python","autoveo_flow.py","--prompts",PROMPTS,
        "--scene",str(n),"--aspect","9:16","--profile-idx",str(prof),"--force"])
    ok = os.path.exists(out) and os.path.getsize(out) > 0
    w = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream=width","-of","csv=p=0",out],
        capture_output=True,text=True).stdout.strip() if ok else ""
    print(f"[{'OK' if w=='720' else 'FAIL'}] scene_{n}: exists={ok} width={w}", flush=True)
print("=== 완료 ===")
for n in (1,2,3,4,5):
    p = f"turtle_short_v916/scene_{n}.mp4"
    print(p, "있음" if os.path.exists(p) else "없음")
