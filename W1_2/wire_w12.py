# -*- coding: utf-8 -*-
"""W1-2 렌더 배선 — `anim_sequences` + `assets` + `scene_objects`.

★[[w24r-render-wiring-chain]] : 렌더는 컷 폴더를 보지 않는다.
  `scene_objects` → `assets`(asset_id 조인) → `anim_char_poses` 이 세 개만 본다.
  하나라도 비면 **캐릭터가 조용히 사라진다**.

## 이 스크립트가 채우는 것
1. `assets`   — 캐릭터마다 대표 이미지 1행(조인용 자리). 실제 그림은 매 프레임 교체된다
2. `anim_sequences` — 씬×캐릭터마다 비트 하나. `oneshot`+`fps` 로 **원래 속도 1회 재생**
3. `scene_objects` — asset_id + `motion_type='gseq:<char_key>:<시퀀스>'`
   (compile_stickman 의 gseq 갈래를 캐릭터 지정 가능하게 확장해 두었다)

## 한계 — 지금은 이렇게 간다
씬 안에서 **깊이가 변하는 것**(M→D1→M)은 비트로 표현할 수 없다. `seq_state` 는 x 만
돌려주고 배율은 안 돌려준다. 그래서 **그 씬의 대표 깊이로 배율을 고정**한다.
깊이 이동까지 넣으려면 렌더러를 한 번 더 손봐야 한다.

    python W1_2/wire_w12.py
"""
import glob
import json
import os
import sqlite3
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

import w12_manifest as MAN                               # noqa: E402

DB = "channel/content.db"
EP = "KO-W1-2"
CUT_FPS = 8.0                    # 64컷 ÷ 8초 = 8fps (원래 속도)

# ★★가장 작아질 때의 화면 키 — **배경이 정한다** (사장님 확정 2026-08-13)
#   "만약 배경에 길이 앞뒤로 혹은 사선으로 저 끝까지 죽 이어져 있고, 고속도로나
#    시베리아 벌판 길처럼 연속으로 배경 전장에 걸쳐 있다면 **0까지도 가능**해야지 —
#    0이면 없어지는 것이니까. 그렇지만 **담벼락이 있으면 300에서도 캐릭터가 사라져야**
#    겠지. 그래서 **1**로 정한 것이다. 0은 무한대라서 계산 못 하니까."
#
#   → 상수 하한(옛 MIN_H=250)은 틀렸다. 그 배경의 **땅이 어디서 끝나느냐**가 하한이다.
#     `measure_ground.py` 가 배경마다 지평선 y 를 실측해 앵커에 적어 두었고,
#     `stage_solve.py` 가 그 지평선에서 원근을 푼다. 여기서는 그 값을 읽어
#     **그 배경에서 갈 수 있는 가장 먼 자리의 키**를 하한으로 쓴다.
#     계산이 무너지지 않게 바닥만 1 로 막는다.
#   ★결론 — **하한은 1이다.** 그 위로 얼마에서 사라지느냐는 배경의 땅이 정한다.
MIN_H = 1
CHAR_DB = {"stickman": "w12_stick", "zolla_man": "w12_zman", "zolla_girl": "w12_zgirl"}

# ★캐릭터별 키 비율 — DB `char_heights` 의 ratio (스틱맨 700 을 1.0 으로)
#   졸라맨 178cm → 1.016 · 졸라걸 163cm → 0.9306
CHAR_RATIO = {"stickman": 1.0, "zolla_man": 1.016, "zolla_girl": 0.9306}
# ★그림 한 장의 **잉크 높이** (measure_cuts.py 실측)
#   스틱맨 컷·포즈 740 · 졸라맨 775 · 졸라걸 745
POSE_H = {"stickman": 740.0, "zolla_man": 775.0, "zolla_girl": 745.0}


def poses_of(con, ck):
    return {r[0]: r[1] for r in con.execute(
        "SELECT pose_name,file_path FROM anim_char_poses WHERE char_key=?", (ck,))}


def frames_of(pool, key):
    """<key>_00, _01 … 로 시작하는 프레임 이름을 순서대로."""
    fs = sorted(n for n in pool if n.startswith(key + "_") and n[len(key) + 1:].isdigit())
    return fs


def main():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS anim_sequences(
        id INTEGER PRIMARY KEY, seq_name TEXT UNIQUE, beats_json TEXT,
        description TEXT, updated_at TEXT)""")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pools = {ck: poses_of(con, ck) for ck in set(CHAR_DB.values()) | {"m6_stick"}}

    # ── 1. assets — 캐릭터별 대표 1행 ──
    aid = {}
    for logical, ck in list(CHAR_DB.items()) + [("m6_stick", "m6_stick")]:
        pool = pools[ck]
        if not pool:
            print("  ★포즈 없음:", ck)
            continue
        rep = sorted(pool)[0]
        fp = pool[rep]
        r = con.execute("SELECT id FROM assets WHERE name_en=?", (ck,)).fetchone()
        if r:
            aid[logical] = r[0]
            con.execute("UPDATE assets SET file_path=? WHERE id=?", (fp, r[0]))
        else:
            c = con.execute(
                "INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt,created_at)"
                " VALUES(?,?,?,?,?,?)",
                ("W1-2 " + logical, ck, "character", fp, "W1_2 cut/pose", now))
            aid[logical] = c.lastrowid
    print("assets 대표행:", {k: v for k, v in aid.items()})

    # ── 2·3. 씬×캐릭터 시퀀스 + scene_objects ──
    import build_w12 as B                                 # noqa: E402  CHARS·DEPTH 재사용
    man = {s[0]: s for s in MAN.SCENES}
    con.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
    nseq = nobj = 0
    for seq, entries in sorted(B.CHARS.items()):
        sec = man[seq][1]
        for i, (logical, key, depth, cx) in enumerate(entries):
            ck = CHAR_DB[logical]
            # ★m6_* 는 어제 만든 스틱맨 이동컷 라이브러리(char_key='m6_stick') 다.
            #   w12_* 에는 없으므로 그쪽을 가리킨다([[stickman-move-cut-library]]).
            if key.startswith("m6_"):
                ck = "m6_stick"
                if ck not in pools:
                    pools[ck] = poses_of(con, ck)
                key = key[3:]                             # DB 이름은 접두사 없이 run_exit_r_00
            pool = pools[ck]
            fr = frames_of(pool, key)
            # ★깊이 이동 — "V→M" · "M→D1→M" 처럼 화살표로 잇는다.
            #   단계 n 개면 비트 n-1 개를 만들고, 컷 프레임을 고르게 나눠 싣는다.
            #   배율은 **가장 큰 깊이를 기준(1.0)** 으로 잡는다 — 원본보다 확대하지 않으려고.
            stages = [s.strip() for s in depth.split("→")]
            hs = [max(MIN_H, B.DEPTH.get(s, B.DEPTH["M"])[0]) for s in stages]
            h_ref = max(hs)
            foot_y = B.DEPTH.get(stages[0], B.DEPTH["M"])[1]

            # ★비트는 **언제나 하나**다. 쪼개면 oneshot+fps 재생이 절대시간을 쓰는 탓에
            #   뒤 비트가 마지막 프레임만 나와 **동작이 반만 돌고 끝난다**(2026-08-12 사고).
            #   깊이 변화는 `s_keys` 로 한 비트 안에서 표현한다.
            n = len(hs)
            s_keys = [[round(i / float(max(1, n - 1)), 4), round(h / float(h_ref), 4)]
                      for i, h in enumerate(hs)]
            if fr:                                        # 동작 컷 — 원래 속도 1회 재생
                beats = [{"dur": 1.0, "x_from": cx, "x_to": cx,
                          "cycle": fr, "oneshot": True, "fps": CUT_FPS,
                          "s_keys": s_keys}]
                kind = "컷 %d장 (%.1f초)" % (len(fr), len(fr) / CUT_FPS)
            elif key in pool:                             # 정지 포즈 — 한 장 유지
                beats = [{"dur": 1.0, "x_from": cx, "x_to": cx, "cycle": [key],
                          "s_keys": s_keys}]
                kind = "정지"
            else:
                print("  ★S%-2d %s: '%s' 를 %s 에서 못 찾음" % (seq, logical, key, ck))
                continue

            sname = "w12_s%02d_%s" % (seq, logical)
            con.execute(
                "INSERT INTO anim_sequences(seq_name,beats_json,description,updated_at)"
                " VALUES(?,?,?,?) ON CONFLICT(seq_name) DO UPDATE SET"
                " beats_json=excluded.beats_json, updated_at=excluded.updated_at",
                (sname, json.dumps(beats, ensure_ascii=False),
                 "W1-2 S%d %s %s" % (seq, logical, key), now))
            nseq += 1

            # ★cy 는 **이미지 중심**이다(렌더러가 `cy - height/2` 로 얹는다).
            #   여기에 발 y 를 넣었다가 캐릭터 아랫다리가 화면 밖으로 잘렸다(2026-08-12).
            #   기준 배율에서의 키 절반만큼 올려 **발이 foot_y 에 닿게** 한다.
            cy = int(foot_y - (h_ref * CHAR_RATIO.get(logical, 1.0)) // 2)
            # ★키 비율과 그림 높이를 **둘 다** 본다 (사장님 지시 2026-08-13
            #   "머리의 아래위 높이가 비율을 정하는 척도").
            #   · 깊이표의 h_ref 는 **스틱맨** 기준 화면 키다
            #   · 졸라맨은 그보다 1.6% 크고 졸라걸은 6.9% 작다 (char_heights)
            #   · 나눌 값은 그 캐릭터 **그림의 실제 잉크 높이**다(스틱맨 740·졸라 745/775).
            #     740 으로 뭉뚱그리면 졸라가 제 키보다 크거나 작게 나온다.
            h_char = h_ref * CHAR_RATIO.get(logical, 1.0)
            src_h = POSE_H.get(logical, 740.0)
            con.execute(
                "INSERT INTO scene_objects(episode,scene_seq,asset_id,cx,cy,scale,z_order,"
                "is_point,motion_type) VALUES(?,?,?,?,?,?,?,?,?)",
                (EP, seq, aid[logical], cx, cy, round(h_char / src_h, 4),
                 5 + i, 0, "gseq:%s:%s" % (ck, sname)))
            nobj += 1
            print("  S%-2d %-11s %-22s %-11s cx%-5d 키 %s  %s"
                  % (seq, logical, key, depth, cx,
                     "→".join(str(h) for h in hs), kind))

    # ── 4. 파라메트릭 한글 글자 오브젝트 ──
    # ★렌더러는 `motion_type='write'` 인 **별도 오브젝트**가 있어야 글자를 그린다
    #   (compile_stickman 740행). 캐릭터만 넣고 이걸 빠뜨려 1차 렌더에 글자가 통째로
    #   안 나왔다(2026-08-12). 글자 내용은 씬의 `draw_text` 가 준다.
    # ★자리 = 화면 **상반부 중앙**(사장님 확정) — cx 640 · cy 200 · 최대 세 줄.
    # ★크기는 **가장 긴 줄의 글자 수**로 정한다. 렌더러는 `size_px = 200 × scale` 로
    #   글자 하나의 크기를 잡으므로, 긴 줄일수록 배율을 낮춰야 화면 폭(1280)에 든다.
    #   1차 렌더에서 "모음 + 모음 = 단어" 가 양쪽으로 잘려 나갔다(2026-08-12).
    TEXT_CX, TEXT_CY = 640, 200
    MAX_W = 1120.0                                        # 좌우 80px 씩 여백
    ntext = 0
    for seq, _ in sorted(((s[0], s[1]) for s in MAN.SCENES)):
        r = con.execute("SELECT image_prompt FROM scenes WHERE episode=? AND seq=?",
                        (EP, seq)).fetchone()
        if not r:
            continue
        g = (json.loads(r[0]).get("draw_text") or "").strip()
        if not g:
            continue
        widest = max((len(ln.replace(" ", "")) + ln.count(" ") * 0.5)
                     for ln in g.split("\n")) or 1
        scale = min(1.15, MAX_W / (200.0 * widest))       # 200px = 글자 하나 기준
        nline = g.count("\n") + 1
        cy = TEXT_CY + (nline - 1) * 60                   # 여러 줄이면 조금 내려 상반부에 담는다
        con.execute(
            "INSERT INTO scene_objects(episode,scene_seq,asset_id,cx,cy,scale,z_order,"
            "is_point,motion_type) VALUES(?,?,?,?,?,?,?,?,?)",
            (EP, seq, aid["stickman"], TEXT_CX, cy, round(scale, 3), 9, 0, "write"))
        ntext += 1

    con.commit()
    print("\n시퀀스 %d개 · 캐릭터 %d행 · 글자 %d행" % (nseq, nobj, ntext))
    nobj += ntext

    # ── 검증 — 조인이 실제로 살아 있는가 ──
    n = con.execute(
        "SELECT COUNT(*) FROM scene_objects o JOIN assets a ON a.id=o.asset_id"
        " WHERE o.episode=?", (EP,)).fetchone()[0]
    print("assets 조인 통과 %d/%d행%s" % (n, nobj, "" if n == nobj else "  ★일부 조인 실패"))
    con.close()
    return 0 if n == nobj else 1


if __name__ == "__main__":
    raise SystemExit(main())
