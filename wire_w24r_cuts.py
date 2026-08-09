# -*- coding: utf-8 -*-
"""W24R 투명 컷아웃(순백 배경 판)을 렌더 경로에 배선한다.
   ★사장님 지적(2026-08-07): "캐릭터 모션 동영상 12개 만든 것 하나도 사용 안 하고 렌더했네"

   원인 — wire_w24_cuts.py 는 옛 W24 폴더(W24/group_cuts_v2)를 등록한다.
   렌더러(compile_stickman)는 motion_type='gseq:<시퀀스>' 를 만나면
   anim_sequences / anim_char_poses(char_key='w24_grp') 에서 컷을 찾는다.
   거기 등록이 옛 폴더였으므로 오늘 만든 깨끗한 컷은 한 장도 쓰이지 않았다.

     anim_char_poses : char_key='w24_grp', pose_name='<동작>_f00' → W24R/group_cuts_w/<동작>/f00.png
     anim_sequences  : seq_name='w24_<동작>' → 64컷을 씬 길이에 맞춰 1회 재생(oneshot)

   씬 매핑은 건드리지 않는다 — build_w24r.py 가 이미 scene_objects.motion_type 에 넣었다.
   사용: python wire_w24r_cuts.py [--dry]
"""
import argparse
import glob
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from W24R.place_chars import GROUP

DB = "channel/content.db"
CUT_DIR = "W24R/group_cuts_w"       # ★순백 배경에서 뜬 깨끗한 컷
CHAR_KEY = "w24_grp"
SEQ_PREFIX = "w24_"
CANVAS_CX = 640                     # 통짜 배치 = 화면 중앙
NCUT, SECS = 64, 8.0                # 8초 동작 → 3프레임에 1장 = 64컷 (원래 속도 8fps)


def log(m):
    print(m, flush=True)


def main(dry):
    con = sqlite3.connect(DB)
    cur = con.cursor()

    want = {r[0][5:] for r in cur.execute(
        "SELECT DISTINCT motion_type FROM scene_objects "
        "WHERE episode='KO-W24' AND motion_type LIKE 'gseq:%'")}
    log(f"씬이 요구하는 시퀀스 {len(want)}개")

    if not dry:                      # 재실행 가능하게 — 이 회차 것만 지우고 다시 넣는다
        d1 = cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR_KEY,)).rowcount
        d2 = cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE ?",
                         (SEQ_PREFIX + "%",)).rowcount
        log(f"기존 배선 정리: 컷 {d1}행 · 시퀀스 {d2}행")

    npose, nseq, skipped = 0, 0, []
    for key in sorted(GROUP):
        cuts = sorted(glob.glob(f"{CUT_DIR}/{key}/f*.png"))
        if len(cuts) != 64:
            skipped.append(f"{key}({len(cuts)}장)")
            continue
        names = []
        for p in cuts:
            nm = f"{key}_{os.path.splitext(os.path.basename(p))[0]}"
            names.append(nm)
            if not dry:
                cur.execute(
                    "INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen,updated_at) "
                    "VALUES (?,?,?,0,0,datetime('now'))",
                    (CHAR_KEY, nm, p.replace("\\", "/")))
            npose += 1
        # ★사장님 지시(2026-08-07): "스틸동영상 속도는 원래 속도대로 상영한다."
        #   64컷은 8초짜리 동작을 3프레임에 1장씩 뽑은 것이므로 원래 속도 = 8fps.
        #   fps 를 실어 보내면 렌더러가 씬 길이와 무관하게 절대시간으로 재생한다.
        beats = [dict(name=names[0], cycle=names, x_from=CANVAS_CX, x_to=CANVAS_CX,
                      dur=1.0, oneshot=True, fps=NCUT / SECS)]
        seq = SEQ_PREFIX + key
        if not dry:
            cur.execute(
                "INSERT INTO anim_sequences (seq_name,beats_json,description,updated_at) "
                "VALUES (?,?,?,datetime('now'))",
                (seq, json.dumps(beats, ensure_ascii=False),
                 f"W24R 통짜 {len(names)}컷 — {CUT_DIR}/{key}"))
        nseq += 1

    if not dry:
        con.commit()

    have = {r[0] for r in cur.execute("SELECT seq_name FROM anim_sequences")}
    miss = sorted(w for w in want if w not in have)
    con.close()

    log(f"{'(모의) ' if dry else ''}컷 {npose}장 → anim_char_poses('{CHAR_KEY}')")
    log(f"{'(모의) ' if dry else ''}시퀀스 {nseq}개 → anim_sequences('{SEQ_PREFIX}*')")
    if skipped:
        log(f"★64컷이 아니라 건너뜀: {', '.join(skipped)}")
    log(f"씬이 요구하는데 없는 시퀀스: {miss if miss else '없음'}")
    return 0 if not miss else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    raise SystemExit(main(ap.parse_args().dry))
