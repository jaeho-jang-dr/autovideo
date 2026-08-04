# -*- coding: utf-8 -*-
"""W24 투명 컷아웃 1,152장을 렌더 경로에 배선한다.
   ★사장님 지시(2026-08-04): "투명 컷아웃한 스틸동영상은 모두 써야지" · "그룹 컷 통짜로 가자"

   그룹 컷(2~3명이 상호작용 거리째로 한 장)을 **통짜 한 덩어리**로 배치한다.
   컷 자체는 W24/group_cuts/ 에 그대로 두고(487MB — 복사도 커밋도 안 한다) DB 에는 경로만 넣는다.

     anim_char_poses : char_key='w24_grp', pose_name='<동작>_<컷번호>' → W24/group_cuts/<동작>/NN.png
     anim_sequences  : seq_name='w24_<동작>' → 64컷을 씬 길이에 맞춰 처음~끝 1회 재생(oneshot)

   씬 매핑은 추측하지 않는다 — gen_w24_group_prompts.py 의 ACTS 테이블('쓰이는 씬')이 원천이다.
   사용: python wire_w24_cuts.py [--dry]
"""
import argparse
import glob
import importlib.util
import json
import os
import re
import sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

DB = "channel/content.db"
CUT_DIR = "W24/group_cuts"
CHAR_KEY = "w24_grp"                # 그룹 컷은 '한 덩어리'라 캐릭터 키 하나로 모은다
SEQ_PREFIX = "w24_"
CANVAS_CX = 640                     # 통짜 배치 = 화면 중앙


def log(m):
    print(m, flush=True)


def load_acts():
    """gen_w24_group_prompts.py 의 ACTS = (키, 그룹, 참조캐릭터, 쓰이는 씬, 액션본문)."""
    spec = importlib.util.spec_from_file_location("_g", "gen_w24_group_prompts.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    return mod.ACTS


def parse_scenes(text):
    """'S30~S32' · 'S5 S6' · '씬 전환용' → 씬 번호 리스트(전환용은 빈 리스트)."""
    out = []
    for a, b in re.findall(r"S(\d+)\s*[~-]\s*S(\d+)", text):
        out += list(range(int(a), int(b) + 1))
    stripped = re.sub(r"S\d+\s*[~-]\s*S\d+", "", text)
    out += [int(x) for x in re.findall(r"S(\d+)", stripped)]
    return sorted(set(out))


def main(dry):
    acts = load_acts()
    con = sqlite3.connect(DB)
    cur = con.cursor()

    if not dry:                      # 재실행 가능하게 — 이 회차 것만 지우고 다시 넣는다
        d1 = cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR_KEY,)).rowcount
        d2 = cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE ?",
                         (SEQ_PREFIX + "%",)).rowcount
        if d1 or d2:
            log(f"기존 W24 배선 정리: 컷 {d1}행 · 시퀀스 {d2}행")

    npose, nseq, skipped, mapping = 0, 0, [], {}
    for key, grp, refs, scenes, _action in acts:
        cuts = sorted(glob.glob(f"{CUT_DIR}/{key}/*.png"))
        if not cuts:
            skipped.append(key)
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
        # 64컷을 씬 길이 전체에 걸쳐 처음~끝 1회 (★8초→64컷 전체 상영)
        beats = [dict(name=names[0], cycle=names, x_from=CANVAS_CX, x_to=CANVAS_CX,
                      dur=1.0, oneshot=True)]
        seq = SEQ_PREFIX + key
        if not dry:
            cur.execute(
                "INSERT INTO anim_sequences (seq_name,beats_json,description,updated_at) "
                "VALUES (?,?,?,datetime('now'))",
                (seq, json.dumps(beats, ensure_ascii=False),
                 f"W24 그룹{grp} 통짜 {len(names)}컷 — {scenes}"))
        nseq += 1
        for s in parse_scenes(scenes):
            mapping.setdefault(s, []).append(seq)

    if not dry:
        con.commit()
    con.close()

    log(f"{'(모의) ' if dry else ''}컷 {npose}장 → anim_char_poses('{CHAR_KEY}')")
    log(f"{'(모의) ' if dry else ''}시퀀스 {nseq}개 → anim_sequences('{SEQ_PREFIX}*')")
    if skipped:
        log(f"★컷이 없어 건너뜀: {', '.join(skipped)}")
    log("\n씬별 시퀀스 (씬 전환용 점프는 특정 씬에 안 붙음):")
    for s in sorted(mapping):
        log(f"  S{s:<3} {', '.join(mapping[s])}")
    log(f"\n배선된 씬 {len(mapping)}개")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    raise SystemExit(main(ap.parse_args().dry))
