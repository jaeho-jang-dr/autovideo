# -*- coding: utf-8 -*-
"""아이키성장 v3 재빌드: scene9 교체 → finalize(재컴파일) → remux(오디오/자막 재먹싱) → v3 4K 마스터.
scene9는 동일 길이(8.0s·192f·1280x720) 드롭인이라 A/V 싱크 영향 없음. 오디오는 기존 교정 트랙 재사용."""
import subprocess, sys, os, shutil, time

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
CG = os.path.join(ROOT, "child_growth_science")
try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

def dur(p):
    try:
        return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],
                                    capture_output=True,text=True).stdout.strip())
    except Exception:
        return 0.0

t0 = time.time()
print("== [1/4] scene_9 교체 ==", flush=True)
src = os.path.join(ROOT, "child_growth", "scene_9.mp4")
dst = os.path.join(CG, "scene_9.mp4")
bak = os.path.join(ROOT, "scratch", "scene9_old_child_growth_science.mp4")
if os.path.exists(dst) and not os.path.exists(bak):
    shutil.copy2(dst, bak); print("  기존 scene_9 백업 ->", bak, flush=True)
shutil.copy2(src, dst)
print(f"  scene_9 교체 완료 (dur={dur(dst):.3f}s)", flush=True)

print("== [2/4] finalize.py (4K 재컴파일) ==", flush=True)
r = subprocess.run([sys.executable, os.path.join(CG, "finalize.py")], cwd=ROOT)
if r.returncode != 0:
    print("!! FINALIZE 실패", flush=True); sys.exit(1)
base = os.path.join(CG, "child_growth.mp4")
print(f"  child_growth.mp4 재컴파일 완료 (dur={dur(base):.1f}s)", flush=True)

print("== [3/4] remux_ko.py (오디오/자막 재먹싱) ==", flush=True)
r = subprocess.run([sys.executable, os.path.join(CG, "remux_ko.py")], cwd=ROOT)
if r.returncode != 0:
    print("!! REMUX 실패", flush=True); sys.exit(1)
dub = os.path.join(CG, "child_growth_dub.mp4")
print(f"  child_growth_dub.mp4 완료 (dur={dur(dub):.1f}s)", flush=True)

print("== [4/4] v3 4K 마스터 복사 ==", flush=True)
v3 = os.path.join(CG, "child_height_growth_science_4k_v3.mp4")
shutil.copy2(dub, v3)
print(f"  V3 MASTER: {v3}  ({os.path.getsize(v3)/1e6:.0f}MB, {dur(v3)/60:.2f}분)", flush=True)
print(f"== DONE in {(time.time()-t0)/60:.1f}분 ==", flush=True)
