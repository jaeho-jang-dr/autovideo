# -*- coding: utf-8 -*-
"""W24 렌더 전 — 시나리오와 에셋이 얼마나 충실히 쓰이는지 대조한다.
   ★사장님 지적(2026-08-03): "포즈·배경 다 만들어 놓고 쓰지도 않더라"
   → 요청(시나리오·모션) ↔ 실물(파일) ↔ 실사용(DB/렌더 경로) 3자를 맞춰 본다.
   읽기 전용. DB·파일을 고치지 않는다.  사용: python precheck_w24_assets.py
   (precheck_w22.py 계승 · 파서는 build_w24 를 그대로 재사용)"""
import os, glob, sqlite3, collections
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")

import build_w24 as B

DB = "channel/content.db"
BG_DIR = "assets/graphics/bg"
CUT_DIR = "W24/group_cuts"

ok_all = True


def chk(name, ok, detail=""):
    global ok_all
    if not ok:
        ok_all = False
    print(f"  [{'OK' if ok else '✗ '}] {name}{(' — ' + detail) if detail else ''}")


sc = B.parse_scenario(B.SCEN)
mo = B.parse_motion(B.MOTION)
tracks_all = [(n, t) for n in sorted(sc) for t in mo.get(n, [])]

print("=== W24 시나리오·에셋 충실도 대조 ===")
print(f"시나리오 {len(sc)}씬 · 모션 트랙 {len(tracks_all)}줄\n")

# ── 1. 배경 : 시나리오가 요청한 것이 실제로 그 형태로 쓰이는가 ──
print("[1] 배경")
want_v = [n for n in sc if sc[n]["bgtype"] == "VIDEO"]
want_s = [n for n in sc if sc[n]["bgtype"] != "VIDEO"]
demoted, miss_still, used_bg = [], [], set()
for n in sorted(sc):
    key = sc[n]["bg"]
    mp4, png = f"{BG_DIR}/bg_w24_{key}.mp4", f"{BG_DIR}/bg_w24_{key}.png"
    if sc[n]["bgtype"] == "VIDEO":
        if os.path.exists(mp4):
            used_bg.add(os.path.basename(mp4))
        else:
            demoted.append(f"S{n}({key})")          # ★VIDEO 요청인데 mp4 없음 → 말없이 정지로 강등
    if os.path.exists(png):
        used_bg.add(os.path.basename(png))
    elif sc[n]["bgtype"] != "VIDEO":
        miss_still.append(f"S{n}({key})")
chk(f"1a. VIDEO 요청 {len(want_v)}씬 전부 mp4 있음", not demoted,
    "강등 " + ", ".join(demoted) if demoted else f"{len(want_v)}/{len(want_v)}")
chk(f"1b. STILL 요청 {len(want_s)}씬 전부 png 있음", not miss_still,
    ", ".join(miss_still) if miss_still else f"{len(want_s)}/{len(want_s)}")

# ── 2. 캐릭터 포즈 : 모션이 지정한 포즈가 실물 PNG 로 존재하는가 ──
print("\n[2] 캐릭터 포즈")
on_disk = {os.path.basename(p)[4:-4] for p in glob.glob(f"{B.POSE_DIR}/w24_*.png")}
matched, missing, used_pose = 0, [], set()
for n, t in tracks_all:
    pose = next((p for p in t["poses"] if not p.startswith("walk_")), None)
    if not pose:
        continue
    key = f"{t['char']}_{pose}"
    if key in on_disk:
        matched += 1
        used_pose.add(key)
    else:
        missing.append(f"S{n} {key}")
posed = matched + len(missing)
chk(f"2a. 포즈 지정 {posed}트랙 전부 PNG 존재", not missing,
    f"매칭 {matched} · 누락 {len(missing)}")
if missing:
    print("       ↳ 누락(화면에 안 나옴): " + ", ".join(missing[:12])
          + (f" 외 {len(missing)-12}건" if len(missing) > 12 else ""))

# 걷기 트랙은 build 가 asset 조회를 안 한다 → 별도로 본다
walks = [(n, t) for n, t in tracks_all if any(p.startswith("walk_") for p in t["poses"])]
wmiss = []
for n, t in walks:
    w = next(p for p in t["poses"] if p.startswith("walk_"))
    if f"{t['char']}_{w}" not in on_disk:
        wmiss.append(f"S{n} {t['char']}_{w}")
chk(f"2b. 걷기 {len(walks)}트랙 컷 존재", not wmiss,
    ", ".join(wmiss[:8]) if wmiss else f"{len(walks)}/{len(walks)}")

# ── 3. 만들어 놓고 안 쓰는 것 (사장님 지적의 핵심) ──
print("\n[3] 만들고 안 쓰는 에셋")
idle_pose = sorted(on_disk - used_pose)
chk(f"3a. 포즈 PNG {len(on_disk)}장 전부 사용", not idle_pose,
    f"미사용 {len(idle_pose)}장: " + ", ".join(idle_pose[:10]) if idle_pose else "")
bg_files = {os.path.basename(p) for p in glob.glob(f"{BG_DIR}/bg_w24_*")}
idle_bg = sorted(bg_files - used_bg)
chk(f"3b. 배경 파일 {len(bg_files)}개 전부 사용", not idle_bg,
    f"미사용 {len(idle_bg)}개: " + ", ".join(idle_bg) if idle_bg else "")

# ── 4. 투명 컷아웃 시퀀스 : 렌더 경로에 연결돼 있는가 ★사장님 "전부 써야지" ──
print("\n[4] 투명 컷아웃 시퀀스 (전부 써야 함)")
acts = sorted(d for d in os.listdir(CUT_DIR) if os.path.isdir(f"{CUT_DIR}/{d}")) \
    if os.path.isdir(CUT_DIR) else []
ncut = {a: len(glob.glob(f"{CUT_DIR}/{a}/*.png")) for a in acts}
total_cuts = sum(ncut.values())
con = sqlite3.connect(DB)
nseq = con.execute("SELECT COUNT(*) FROM anim_sequences WHERE seq_name LIKE '%w24%'").fetchone()[0]
npose_db = con.execute("SELECT COUNT(*) FROM anim_char_poses WHERE char_key LIKE '%w24%'").fetchone()[0]
nobj = con.execute("SELECT COUNT(*) FROM scene_objects WHERE episode=?", (B.EP,)).fetchone()[0]
con.close()
print(f"       동작 {len(acts)}개 · 컷 {total_cuts}장 ({'/'.join(str(ncut[a]) for a in acts[:6])}…)")
chk(f"4a. 컷 {total_cuts}장이 anim_char_poses 에 등록", npose_db >= total_cuts,
    f"등록 {npose_db}장")
chk(f"4b. 동작 {len(acts)}개가 anim_sequences 로 재생", nseq >= len(acts),
    f"w24 시퀀스 {nseq}개")
chk("4c. scene_objects 배치됨", nobj > 0, f"{nobj}개")

print("\n" + ("=== ✅ 전부 통과 — 렌더 가능 ==="
             if ok_all else "=== ✗ 미사용/누락 있음 — 렌더 보류 ==="))
raise SystemExit(0 if ok_all else 1)
