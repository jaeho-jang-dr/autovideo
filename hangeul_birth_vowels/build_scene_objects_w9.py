#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_scene_objects_w9.py — KO-W09 캐릭터 무빙 시나리오 + 씬설정.
 - 캐릭터 = 마담제이(작게). 포즈는 나레이션 내용과 일치(의미 있는 동작, 반복 금지).
 - 씬별 배경 bg_w9_sNN + 중앙위 캡션 제거(cap="") + 좌상단 로고만.
 - 자막에서 말하는 핵심 글자(word/예문, 동동체)를 씬에 배치.
재실행: python hangeul_birth_vowels/build_scene_objects_w9.py
"""
import os, sys, json, sqlite3
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "channel", "content.db")
EP = "KO-W09"

CX, CY, CSC = 280, 445, 0.48      # 마담제이 원래 크기·위치(W7 기준)

def apath(pose):  return f"assets/graphics/poses/madam_jay_{pose}.png"
def lpath(name):  return f"assets/graphics/letters/{name}.png"

# 씬 → (마담제이 포즈[내용일치], [(글자에셋, cx, cy, scale, motion)...])
#   pose: 앞=pointing 위=raising_hand 왼쪽=point_left 오른쪽/옆=point_right 걷기=walk_right/left
#         인사=waving 설명/장소=presenting 생각=thinking 축하=cheering
W = lambda name, cx, cy, sc, m="elastic_pop": (lpath(f"word_{name}"), cx, cy, sc, m)
E = lambda key, cx, cy, sc, m="fade_in":      (lpath(f"ex_{key}"), cx, cy, sc, m)
SCN = {
 1:  ("waving",     [W("위치와 장소 표현", 1030, 330, 0.34)]),
 2:  ("presenting", [W("앞", 720, 300, 0.34), W("뒤", 900, 300, 0.34), W("옆", 1080, 300, 0.34),
                     W("위", 810, 470, 0.34), W("밑", 990, 470, 0.34)]),
 3:  ("point_right", [W("앞", 980, 300, 0.6), E("학교앞에서만나요", 1000, 520, 0.46)]),
 4:  ("thinking",   [W("뒤", 980, 300, 0.6), E("집뒤에공원이있어요", 1000, 520, 0.46)]),
 5:  ("point_right",[W("옆", 980, 300, 0.6), E("은행옆에카페가있어요", 1000, 520, 0.46)]),
 6:  ("raising_hand",[W("위", 980, 280, 0.6), E("책상위에책이있어요", 1000, 520, 0.46)]),
 7:  ("thinking",   [W("밑", 980, 320, 0.6), E("의자밑에가방이있어요", 1000, 540, 0.46)]),
 8:  ("presenting", [W("안", 980, 300, 0.6), E("가방안에책이있어요", 1000, 520, 0.46)]),
 9:  ("presenting", [W("밖", 980, 300, 0.6), E("집밖에자동차가있어요", 1000, 520, 0.46)]),
 10: ("presenting", [W("사이", 980, 300, 0.55), E("은행과카페사이에있어요", 1000, 520, 0.42)]),
 11: ("point_left", [W("왼쪽", 980, 300, 0.55), E("왼쪽에학교가있어요", 1000, 520, 0.46)]),
 12: ("point_right",[W("오른쪽", 980, 300, 0.5), E("오른쪽에마트가있어요", 1000, 520, 0.46)]),
 13: ("presenting", [W("마트", 980, 300, 0.6), E("마트에서우유를사요", 1000, 520, 0.46)]),
 14: ("walk_right", [W("학교", 980, 300, 0.6), E("학교에걸어서가요", 1000, 520, 0.46)]),
 15: ("presenting", [W("은행", 740, 300, 0.42), W("카페", 980, 300, 0.42), W("공원", 1200, 300, 0.42),
                     E("공원안에서산책해요", 1000, 520, 0.44)]),
 16: ("presenting", [E("학교에걸어서가요", 900, 320, 0.44), E("마트에서우유를사요", 900, 500, 0.44)]),
 17: ("thinking",   [E("Q마트가어디에있어요", 990, 320, 0.46), E("A학교앞에있어요", 990, 520, 0.46)]),
 18: ("presenting", [E("Q은행이어디에있어요", 990, 320, 0.44), E("A카페옆에있어요", 990, 520, 0.46)]),
 19: ("point_left", [E("왼쪽으로가세요", 980, 320, 0.5), E("학교앞에서오른쪽", 980, 520, 0.48)]),
 20: ("cheering",   [W("앞", 660, 250, 0.3), W("뒤", 800, 250, 0.3), W("옆", 940, 250, 0.3), W("위", 1080, 250, 0.3), W("밑", 1220, 250, 0.3),
                     W("안", 700, 420, 0.3), W("밖", 840, 420, 0.3), W("사이", 980, 420, 0.3), W("왼쪽", 1130, 420, 0.3)]),
}

def get_asset(cur, fp, name="", typ="pose"):
    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (fp,)).fetchone()
    if r: return r[0]
    has = "created_at" in {d[1] for d in cur.execute("pragma table_info(assets)")}
    if has:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt,created_at) VALUES (?,?,?,?,?,datetime('now'))",
                    (name or os.path.basename(fp), name, typ, fp, "build_scene_objects_w9.py"))
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (name or os.path.basename(fp), name, typ, fp, "build_scene_objects_w9.py"))
    return cur.lastrowid

def main():
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
    for seq, (pose, glyphs) in SCN.items():
        # 씬 설정 JSON (image_prompt) : 배경·캡션제거·캐릭터
        spec = {"cap_ko": "", "cap_en": "", "motion": "static",
                "bg": f"bg_w9_s{seq:02d}", "char_key": "madam_jay", "place_en": "Haeundae Beach"}
        cur.execute("UPDATE scenes SET image_prompt=? WHERE episode=? AND seq=?", (json.dumps(spec, ensure_ascii=False), EP, seq))
        z = 3
        # 글자들(뒤 레이어)
        for fp, cx, cy, sc, m in glyphs:
            aid = get_asset(cur, fp, typ="word")
            cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,is_point,motion_type) VALUES (?,?,?,?,?,?,?,?,?)",
                        (EP, seq, aid, cx, cy, sc, z, 0, m)); z += 1
        # 마담제이(앞 레이어)
        aid = get_asset(cur, apath(pose), name=f"madam_jay_{pose}", typ="pose")
        cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,is_point,motion_type) VALUES (?,?,?,?,?,?,?,?,?)",
                    (EP, seq, aid, CX, CY, CSC, 8, 0, "fade_in"))
    con.commit()
    n = cur.execute("SELECT COUNT(*) FROM scene_objects WHERE episode=?", (EP,)).fetchone()[0]
    con.close()
    print(f"KO-W09 캐릭터 무빙 시나리오 완료: 20씬, scene_objects {n}개 (마담제이 내용맞춤 포즈 + 동동체 글자 + 씬별 해운대 배경 + 캡션제거)")

if __name__ == "__main__":
    main()
