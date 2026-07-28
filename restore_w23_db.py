# -*- coding: utf-8 -*-
"""W23 DB 레코드 복구 (2026-07-28).

★사고: `channel/content.db` 가 git 추적 대상이라, git-filter-repo 가 히스토리를 다시 쓰면서
  작업 트리를 갱신할 때 **DB를 마지막 커밋 시점으로 되돌렸다.** 디스크의 이미지·영상·패키지는
  전부 무사하므로 DB 레코드만 다시 만든다.

복구 대상
  1. anim_char_poses  — injun_w23 프레임컷 + 정지포즈 + 좌향 flip
  2. youtube_uploads  — 공개된 KO/EN 2편
  (씬·scene_objects·anim_sequences 는 `python build_w23.py` 가 다시 만든다)

사용: python restore_w23_db.py
"""
import glob
import os
import re
import sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
DB = "channel/content.db"
CHAR = "injun_w23"
DIRECTIONAL = ["present_right", "point_board", "hand_on_post", "lean_rail",
               "present_left", "explain", "tap_board", "count_three", "thumbs_up", "raising_hand"]

con = sqlite3.connect(DB)
cur = con.cursor()

# ── 1. 프레임컷 (W23/poses/injun_w23_<action>_<n>.png) ───────────────────────
cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR,))
n_cut = 0
for p in sorted(glob.glob("W23/poses/injun_w23_*_*.png")):
    name = os.path.basename(p)[:-4]
    m = re.match(r"injun_w23_(.+_\d+)$", name)
    if not m:
        continue
    pose = m.group(1)
    # ★walk_l_* 파일은 **이미 좌우반전된 실물** — flip=1 을 또 걸면 뒷걸음질이 된다(W23 사고)
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,0,0)",
                (CHAR, pose, p.replace("\\", "/")))
    n_cut += 1

# ── 2. 정지 포즈 + 좌향 flip (assets/graphics/poses/) ─────────────────────────
n_still = n_flip = 0
for p in sorted(glob.glob("assets/graphics/poses/injun_w23_*.png")):
    key = os.path.basename(p)[len("injun_w23_"):-4]
    if re.search(r"_\d+$", key):            # 프레임컷이 섞여 있으면 건너뜀
        continue
    fp = p.replace("\\", "/")
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,0,0)",
                (CHAR, key, fp))
    n_still += 1
    if key in DIRECTIONAL:
        cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,1,0)",
                    (CHAR, key + "_flip", fp))
        n_flip += 1

# ── 3. 유튜브 업로드 기록 ────────────────────────────────────────────────────
UPLOADS = [
    ("ko", "5xet4FQDdX8", "모임 약속 잡기 - '약속을 잡다' & '시간 조율' | 한글 배우기 W23 (에버랜드)"),
    ("en", "8lob0SW542k", "Making Plans in Korean: '약속을 잡다' & '시간 조율' | Learn Korean W23"),
]
cols = [c[1] for c in cur.execute("PRAGMA table_info(youtube_uploads)")]
n_up = 0
for lang, vid, title in UPLOADS:
    if cur.execute("SELECT 1 FROM youtube_uploads WHERE video_id=?", (vid,)).fetchone():
        continue
    row = {"project": "hangeul_w23_meetup", "kind": "lesson", "lang": lang, "video_id": vid,
           "url": f"https://www.youtube.com/watch?v={vid}", "title": title, "visibility": "public",
           "thumbnail_path": f"hangeul_birth_vowels/thumb_w23_{lang}_1280x720.jpg",
           "local_path": f"hangeul_birth_vowels/hangeul_w23_injun_np_{lang}.mp4",
           "channel": "drjay-ed", "ai_disclosure": 1, "category": "27"}
    row = {k: v for k, v in row.items() if k in cols}
    ks = ",".join(row)
    cur.execute(f"INSERT INTO youtube_uploads ({ks}) VALUES ({','.join('?'*len(row))})", list(row.values()))
    n_up += 1

con.commit()
tot = cur.execute("SELECT COUNT(*) FROM anim_char_poses WHERE char_key=?", (CHAR,)).fetchone()[0]
con.close()
print(f"프레임컷 {n_cut} · 정지 {n_still} · 좌향flip {n_flip} → injun_w23 총 {tot}행")
print(f"유튜브 업로드 기록 {n_up}건 복구")
print("\n▶ 다음: python build_w23.py   (씬 36 · scene_objects · anim_sequences 재생성)")
