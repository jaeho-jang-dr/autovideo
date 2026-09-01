# -*- coding: utf-8 -*-
"""W1-3용 신규 졸라걸(zgirl) 동작 10종을 `anim_char_poses`에 등록한다.
char_key는 기존 w12_zgirl 관례를 그대로 따른다(기존 zgirl_run_side 등록 방식과 동일 —
프레임 폴더를 그대로 가리키는 w12_stick/run_back 방식 참고, 파일을 복사하지 않는다).

한 프레임 = 한 행. UNIQUE(char_key,pose_name) 라 재실행해도 안전(INSERT OR REPLACE).

사용법: python W1_3/register_w1_3_motions.py [--dry-run]
"""
import os
import sys
import sqlite3
import glob

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO_ROOT, "channel", "content.db")
CHAR_KEY = "w12_zgirl"

# ★2026-09-01 — 신규 10종이 전부 검은 머리로 잘못 생성됨(기존 확정 캐릭터는 주황
#   머리)이 발견돼 `W1_3/recolor_hair.py`로 보정 사본(`*_recolored/`)을 만들었다.
#   DB는 그 보정 사본을 가리키도록 등록한다 — 원본(검은 머리) 파일은 지우지 않고
#   그대로 남겨 둔다(향후 캐릭터랑이 기준 이미지로 재생성할 때 비교용).
# (폴더, 종류) — 종류는 로그용
MOTION_DIRS = [
    ("W1_2/motion6_stride_recolored/zgirl_walk_side", "순환(11장) — S06-S08 징검다리 이동"),
    ("W1_2/motion6_stride_recolored/zgirl_walk_front", "순환(32장) — S03 계단 정면 전환"),
    ("W1_2/motion6_stride_recolored/zgirl_run_front", "순환(14장) — S01 원경 등장"),
    ("W1_2/motion6_stride_recolored/zgirl_walk_back", "순환(17장) — S03 계단 진입 뒷모습"),
    ("W1_2/motion6_stride_recolored/zgirl_run_back", "순환(13장) — S23 퇴장"),
    ("W1_2/motion6_stride_recolored/zgirl_stone_hop", "순환(42장) — S06-S08 돌 사이 홉 대체안"),
    ("W1_2/motion6_cuts_recolored/zgirl_block_touch", "1회성(64컷) — S15/S17 블록 결합"),
    ("W1_2/motion6_cuts_recolored/zgirl_stumble_bounce", "1회성(64컷) — S10 오답 개그"),
    ("W1_2/motion6_cuts_recolored/zgirl_cold_flinch", "1회성(64컷) — S13 '으차!' 대체안"),
    ("W1_2/motion6_cuts_recolored/zgirl_clap_together", "1회성(64컷) — S19 '우애' 블록 부딪치기 대체안"),
]


def main():
    dry = "--dry-run" in sys.argv
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    total = 0
    for rel_dir, note in MOTION_DIRS:
        abs_dir = os.path.join(REPO_ROOT, rel_dir.replace("/", os.sep))
        pngs = sorted(glob.glob(os.path.join(abs_dir, "*.png")))
        if not pngs:
            print("!! 프레임 없음:", rel_dir)
            continue
        for p in pngs:
            fname = os.path.basename(p)
            pose_name = os.path.splitext(fname)[0]
            file_path = (rel_dir + "/" + fname)
            if dry:
                print("DRY", CHAR_KEY, pose_name, file_path)
            else:
                c.execute(
                    "INSERT OR REPLACE INTO anim_char_poses "
                    "(char_key, pose_name, file_path, updated_at, flip, pen) "
                    "VALUES (?, ?, ?, datetime('now'), 0, 0)",
                    (CHAR_KEY, pose_name, file_path),
                )
            total += 1
        print("%-40s %3d장  %s" % (rel_dir, len(pngs), note))

    if not dry:
        conn.commit()
    conn.close()
    print("\n총 등록 프레임 수 =", total, ("(dry-run, 실제 반영 안 됨)" if dry else "(반영 완료)"))


if __name__ == "__main__":
    main()
