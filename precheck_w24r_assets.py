# -*- coding: utf-8 -*-
"""W24R 렌더 전 — 시나리오·모션이 요청한 것이 실물로 있고, 실제로 배선까지 되었는지 대조한다.
   ★사장님 지시(2026-08-07): "랜더 하기 전에 모든 준비가 다 되었는지 점검해보자"
   ★precheck_w24_assets.py(W24판) 계승. **읽기 전용** — DB·파일을 고치지 않는다.

   사용: python precheck_w24r_assets.py
"""
import glob
import os
import sqlite3
import sys

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
sys.path.insert(0, os.getcwd())

import numpy as np
from PIL import Image

import W24R.build_w24r as B
from W24R.place_chars import GROUP

BG_DIR = "assets/graphics/bg"
ok_all = True
warn = []


def chk(name, ok, detail=""):
    global ok_all
    if not ok:
        ok_all = False
    print(f"  [{'OK' if ok else 'X '}] {name}{('  — ' + detail) if detail else ''}")


def note(name, detail=""):
    warn.append(name)
    print(f"  [! ] {name}{('  — ' + detail) if detail else ''}")


sc = B.parse_scenario(B.SCEN)
mo = B.parse_motion(B.MOTION)
tracks_all = [(n, t) for n in sorted(sc) for t in mo.get(n, [])]

print("=== W24R 렌더 전 점검 ===")
print(f"시나리오 {len(sc)}씬 · 모션 트랙 {len(tracks_all)}줄")
print(f"컷 폴더(배선) CUT_DIR = {B.CUT_DIR}\n")

# ── 1. 배경 ──────────────────────────────────────────────
print("[1] 배경")
demoted, miss_still, used_bg = [], [], set()
for n in sorted(sc):
    key = sc[n]["bg"]
    mp4, png = f"{BG_DIR}/bg_w24_{key}.mp4", f"{BG_DIR}/bg_w24_{key}.png"
    if sc[n]["bgtype"] == "VIDEO":
        if os.path.exists(mp4):
            used_bg.add(os.path.basename(mp4))
        else:
            demoted.append(f"S{n}({key})")     # VIDEO 요청인데 mp4 없음 → 말없이 정지로 강등
    if os.path.exists(png):
        used_bg.add(os.path.basename(png))
    elif sc[n]["bgtype"] != "VIDEO":
        miss_still.append(f"S{n}({key})")
nv = sum(1 for n in sc if sc[n]["bgtype"] == "VIDEO")
chk(f"1a. VIDEO 요청 {nv}씬 전부 mp4 있음", not demoted,
    "정지로 강등됨: " + ", ".join(demoted) if demoted else f"{nv}/{nv}")
chk(f"1b. STILL 요청 {len(sc)-nv}씬 전부 png 있음", not miss_still,
    ", ".join(miss_still) if miss_still else f"{len(sc)-nv}/{len(sc)-nv}")

# ── 2. 캐릭터 포즈 ───────────────────────────────────────
print("\n[2] 캐릭터 포즈 (W24R/poses)")
on_disk = {os.path.basename(p)[5:-4] for p in glob.glob(f"{B.POSE_DIR}/w24r_*.png")}
missing, used_pose = [], set()
for n, t in tracks_all:
    pose = next((p for p in t["poses"] if not p.startswith("walk_")), None)
    if not pose:
        continue
    key = f"{t['char']}_{pose}"
    (used_pose.add(key) if key in on_disk else missing.append(f"S{n} {key}"))
chk(f"2a. 포즈 지정 {len(used_pose)+len(missing)}트랙 전부 PNG 존재", not missing,
    f"누락 {len(missing)}: " + ", ".join(missing[:8]) if missing else f"{len(used_pose)} 매칭")

walks = [(n, t) for n, t in tracks_all if any(p.startswith("walk_") for p in t["poses"])]
wmiss = [f"S{n} {t['char']}_{w}" for n, t in walks
         for w in [next(p for p in t["poses"] if p.startswith("walk_"))]
         if f"{t['char']}_{w}" not in on_disk]
chk(f"2b. 걷기 {len(walks)}트랙 컷 존재", not wmiss,
    ", ".join(wmiss[:8]) if wmiss else f"{len(walks)}/{len(walks)}")

# ── 3. 그룹 통짜 컷 (실물 품질까지) ──────────────────────
print(f"\n[3] 그룹 통짜 컷 — {B.CUT_DIR}")
bad, thin = [], []
for k in sorted(GROUP):
    d = f"{B.CUT_DIR}/{k}"
    ps = sorted(glob.glob(f"{d}/f*.png"))
    if len(ps) != 64:
        bad.append(f"{k}({len(ps)}장)")
        continue
    a = [float((np.array(Image.open(p).convert("RGBA"))[:, :, 3] > 128).mean()) for p in ps[::16]]
    if max(a) == 0:
        bad.append(f"{k}(빈컷)")
    elif min(a) == 0:
        thin.append(f"{k}(일부 빈컷)")
chk(f"3a. 동작 {len(GROUP)}개 전부 64컷 · 내용 있음", not bad,
    ", ".join(bad) if bad else f"{len(GROUP)}/{len(GROUP)}")
if thin:
    note("3b. 일부 컷이 비어 있음", ", ".join(thin))

# ── 4. 씬↔그룹 배선 : 만든 컷이 전부 쓰이는가 ────────────
print("\n[4] 씬↔그룹 배선 (만든 컷은 전량 소비돼야 한다)")
gmap = B.load_group_map()
placed = {g["tag"] for v in gmap.values() for g in v}
made = set(GROUP)
idle = sorted(made - placed)
ghost = sorted(placed - made)
chk(f"4a. 동작 {len(made)}개 전부 씬에 배정", not idle,
    "미사용: " + ", ".join(idle) if idle else f"{len(placed)}건 배정")
chk("4b. 배정됐는데 컷이 없는 동작 없음", not ghost,
    "컷 없음: " + ", ".join(ghost) if ghost else "없음")

# ── 5. DB 현재 상태 (참고) ───────────────────────────────
print("\n[5] DB 현재 상태 (channel/content.db)")
con = sqlite3.connect(B.DB)
cur = con.cursor()
nsc = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (B.EP,)).fetchone()[0]
nob = cur.execute("SELECT COUNT(*) FROM scene_objects WHERE episode=?", (B.EP,)).fetchone()[0]
rows = cur.execute(
    "SELECT a.file_path FROM scene_objects o JOIN assets a ON a.id=o.asset_id "
    "WHERE o.episode=? AND o.motion_type LIKE 'gseq:%'", (B.EP,)).fetchall()
con.close()
oldwire = [r[0] for r in rows if "group_cuts_w" not in (r[0] or "")]
print(f"       scenes {nsc}행 · scene_objects {nob}행")
chk("5a. DB에 씬이 들어 있음", nsc > 0, f"{nsc}행")
if nsc and oldwire:
    note("5b. DB가 아직 옛 컷 경로를 가리킴",
         f"{len(oldwire)}건 — build_w24r.py 재실행 필요")
elif nsc == 0:
    note("5b. DB 비어 있음", "build_w24r.py 재실행 필요")

# ── 6. 알려진 함정 ──────────────────────────────────────
print("\n[6] 알려진 함정")
bad_png = B.POSE_DIR + "/w24_"          # build_w24r.png_size 가 쓰는 접두어
sample = next(iter(on_disk), None)
if sample and not os.path.exists(f"{bad_png}{sample}.png"):
    note("6a. png_size() 가 'w24_' 접두어로 포즈를 찾는데 실물은 'w24r_'",
         "겹침 정리 폭이 기본값(300px)으로 계산됨")

print("\n" + ("=== 전부 통과 — 렌더 가능 ===" if ok_all and not warn else
             ("=== 통과(주의 " + str(len(warn)) + "건) ===" if ok_all else
              "=== 미비 있음 — 렌더 보류 ===")))
raise SystemExit(0 if ok_all else 1)
