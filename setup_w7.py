# -*- coding: utf-8 -*-
"""W7(인사말·자기소개) 세팅: 동동체 인사말 글자 생성 + scene_objects 배치 + 씬설정(지은·teacher·인사동).
재실행 안전(멱등). 실행: python setup_w7.py"""
import os, sqlite3, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
LDIR = os.path.join(ROOT, "assets", "graphics", "letters")
DB = os.path.join(ROOT, "channel", "content.db")
FONT = os.path.join(ROOT, "assets", "fonts", "Cafe24Dongdong.ttf")
os.makedirs(LDIR, exist_ok=True)

def render(text, color=(38, 38, 38, 255)):
    for fp in [FONT, "C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf"]:
        f = ImageFont.truetype(fp, 190)
        tmp = Image.new("RGBA", (len(text) * 210 + 120, 300), (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        b = d.textbbox((0, 0), text, font=f)
        d.text((40 - b[0], 40 - b[1]), text, font=f, fill=color)
        bb = tmp.split()[3].getbbox()
        if bb is not None:
            pad = 14
            return tmp.crop((max(0, bb[0]-pad), max(0, bb[1]-pad), bb[2]+pad, bb[3]+pad))
    return Image.new("RGBA", (60, 60), (0, 0, 0, 0))

# 씬별 화면 글자 (인사말/자기소개). key = 파일명, phrases per scene
SCENE_WORDS = {
    1:  [("w7_annyeong", "안녕하세요")],
    2:  [("w7_insa", "인사")],
    3:  [("w7_annyeong", "안녕하세요")],
    4:  [("w7_gamsa", "감사합니다")],
    5:  [("w7_bangap", "반갑습니다")],
    6:  [("w7_gaseyo", "안녕히 가세요"), ("w7_gyeseyo", "안녕히 계세요")],
    7:  [("w7_janeun", "저는 ~ 입니다")],
    8:  [("w7_minsu", "저는 민수입니다")],
    9:  [("w7_miguk", "저는 미국 사람입니다")],
    10: [("w7_haksaeng", "저는 학생입니다")],
    11: [("w7_gyeseyo", "안녕히 계세요")],
}

def main():
    con = sqlite3.connect(DB); cur = con.cursor()
    has_created = "created_at" in {r[1] for r in cur.execute("pragma table_info(assets)")}
    # 1) 글자 이미지 생성 + 등록(id 보존)
    made = {}
    for seq, ws in SCENE_WORDS.items():
        for key, text in ws:
            if key in made:
                continue
            im = render(text)
            im.save(os.path.join(LDIR, f"{key}.png"))
            fp = f"graphics/letters/{key}.png"
            row = cur.execute("SELECT id FROM assets WHERE file_path=?", (fp,)).fetchone()
            if row:
                aid = row[0]
                cur.execute("UPDATE assets SET name_kr=?, type=? WHERE id=?", (text, "word", aid))
            else:
                if has_created:
                    cur.execute("INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt,created_at) VALUES(?,?,?,?,?,datetime('now'))",
                                (text, key, "word", fp, "setup_w7.py"))
                else:
                    cur.execute("INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt) VALUES(?,?,?,?,?)",
                                (text, key, "word", fp, "setup_w7.py"))
                aid = cur.lastrowid
            made[key] = (aid, im.size, text)
    # 2) 졸라걸 캐릭터 asset id (poses/stickman_zw_base) — 지은은 포즈마다 옷 바뀌어 졸라걸로 교체
    jch = cur.execute("SELECT id FROM assets WHERE file_path LIKE '%stickman_zw_base%' LIMIT 1").fetchone()
    if not jch:
        cur.execute("INSERT INTO assets(name_kr,name_en,type,file_path) VALUES('졸라걸','zw_base','character','graphics/poses/stickman_zw_base.png')")
        jch = (cur.lastrowid,)
    jch = jch[0]
    # 3) 씬설정 + scene_objects
    for seq, ws in SCENE_WORDS.items():
        r = cur.execute("SELECT image_prompt FROM scenes WHERE episode='KO-W07' AND seq=?", (seq,)).fetchone()
        sp = json.loads(r[0]) if r and r[0] else {}
        sp["char_key"] = "zolla_girl"; sp["char_mode"] = "teacher"
        sp["draw_font"] = "cafe24_dongdong"; sp["draw_dur"] = 3.0
        sp["bg"] = f"bg_w7_{seq:02d}"; sp["place_en"] = "Insadong"
        sp["motion"] = sp.get("motion", "static")
        cur.execute("UPDATE scenes SET image_prompt=? WHERE episode='KO-W07' AND seq=?", (json.dumps(sp, ensure_ascii=False), seq))
        # scene_objects 재구성
        cur.execute("DELETE FROM scene_objects WHERE episode='KO-W07' AND scene_seq=?", (seq,))
        # 글자: 한 개면 중앙, 두 개면 상/하
        n = len(ws)
        for i, (key, text) in enumerate(ws):
            aid, size, _ = made[key]
            w, h = size
            # 캔버스 1280×720. 캐릭터(x≤548) 오른쪽 영역(560~1240)에 배치. 긴 문장은 더 축소
            sc = min(0.52, 650.0 / w)
            cy = 340 if n == 1 else (250 + i * 190)
            cur.execute("""INSERT INTO scene_objects(episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type)
                           VALUES('KO-W07',?,?,?,?,?,3,'fade_in')""", (seq, aid, 890, cy, round(sc, 3)))
        # 캐릭터(졸라걸) 좌측 — W5와 동일 규격(scale 0.72, cy 385)
        cur.execute("""INSERT INTO scene_objects(episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type)
                       VALUES('KO-W07',?,?,300,385,0.72,5,'gesture')""", (seq, jch))
    con.commit()
    print("W7 세팅 완료: 글자", len(made), "개 | 11씬 scene_objects + 설정(지은·teacher·동동체·인사동)")
    con.close()

if __name__ == "__main__":
    main()
