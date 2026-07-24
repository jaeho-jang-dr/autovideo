# -*- coding: utf-8 -*-
"""W18(감정 표현·세밀한 마음 묘사) ~8분: 마담제이, 전주 한옥마을.
★ build_w17 계승. 차이점:
  - 캐릭터 = mj_w18 (마담제이 컷아웃, 1024·발끝y965·몸높이~895).
  - ★화면글자(2번째 칸)는 W17의 '중앙 큰 한글 획순쓰기'가 아니라 **좌상단 텍스트박스**로 렌더한다.
    → 박스 배경까지 넣은 PNG를 미리 만들어 좌상단 static 오브젝트로 배치(compile 코드 수정 불필요).
  - 나레이션=선희(한)+Emma(영), ' ' 예문=선희 DB클립. (엔진=초안 edge-tts)
사용: python build_w18.py  → python compile_np.py KO-W18 hangeul_w18_madamjay review en
"""
import sqlite3, json, os, re
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"
BOXFONT = "C:/Windows/Fonts/malgunbd.ttf"   # 좌상단 박스: 한/영 혼용 → 맑은고딕 볼드
PLACE = "Jeonju Hanok Village"
EP = "KO-W18"; CHAR = "mj_w18"
# mj_w18 포즈 = tj_w17 동일 규격(1024·발끝y~965·몸높이~895) → 좌표 계승
CHAR_CX, CHAR_CY, CHAR_SCALE = 335, 426, 0.482
SCENARIO = "W18_scenario.md"

# 좌상단 텍스트박스 위치(중심 좌표). 로고(좌상단 꼭짓점) 아래에 놓아 겹침 방지.
BOX_LEFT = 20          # 박스 왼쪽 x
BOX_TOP = 54           # 박스 위쪽 y (로고[18,14]~30px 바로 아래)

VALID = {"wave", "bow", "greet_both", "explain", "explain_open", "present_right",
         "point_right", "point_self", "smile_big", "clap", "cheer", "sad", "wipe_tear",
         "heavy_heart", "tense", "deep_breath", "flutter", "think", "compare",
         "hand_heart", "comfort", "hold_hands", "nod_empathy", "walk_right_1", "walk_right_2"}


def norm_quotes(s):
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"'([^']*?)([?!.]+)'", r"'\1'\2", s)
    return s


def clean_pose(tok):
    tok = tok.strip().strip("`").strip()
    m = re.search(r"\(=\s*([a-z_0-9]+)\s*\)", tok)
    if m:
        tok = m.group(1)
    tok = tok.split("(")[0].strip()
    return tok if tok in VALID else None


def merge_walk(poses):
    out, i = [], 0
    while i < len(poses):
        p = poses[i]
        if p in ("walk_right_1", "walk_right_2"):
            j = i
            while j < len(poses) and poses[j] in ("walk_right_1", "walk_right_2"):
                j += 1
            out.append("walk_right"); i = j
        else:
            out.append(p); i += 1
    return out


def parse_scenario(path):
    out = []
    for ln in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^- \*\*S(\d+)\*\*\s*(.*)$", ln)
        if not m:
            continue
        parts = [p.strip() for p in m.group(2).split("|")]
        if len(parts) < 5:
            continue
        cap_ko = parts[0].strip()
        if cap_ko.startswith("("):     # 카드 정적씬 제외
            continue
        glyph = parts[1].strip().strip("`").strip()
        narr = parts[2]
        bg = parts[3].strip().strip("`").strip()
        posestr = parts[4].strip()
        if "→" in narr:
            kside, eside = narr.split("→", 1)
        else:
            kside, eside = narr, ""
        km = re.search(r'"([^"]*)"', kside)
        ko = km.group(1).strip() if km else kside.strip().strip('"').strip()
        eside = eside.strip()
        if eside.startswith("(") and eside.endswith(")"):
            eside = eside[1:-1].strip()
        en = eside
        raw = [p.strip() for p in re.split(r"[→/]", posestr) if p.strip()]
        poses = [q for q in (clean_pose(p) for p in raw) if q]
        poses = merge_walk(poses)
        gm = re.search(r"\(([^()]+)\)", en)
        cap_en = gm.group(1).strip() if gm else ""
        out.append(dict(cap_ko=cap_ko, cap_en=cap_en, glyph=glyph,
                        ko=ko, en=en, bg=bg, poses=poses))
    return out


def expand(p):
    if p == "walk_right":
        return ["walk_right_1", "walk_right_2"], 210, CHAR_CX
    return [p], CHAR_CX, CHAR_CX


def make_beats(poses):
    ps = poses or ["present_right"]
    share = round(1.0 / len(ps), 4)
    beats = []
    for p in ps:
        cyc, xf, xt = expand(p)
        beats.append({"name": cyc[0], "cycle": cyc, "x_from": xf, "x_to": xt, "dur": share})
    return beats


def make_textbox(text, path):
    """★좌상단 텍스트박스: 크림 라운드 박스 + 코랄 왼쪽 악센트 바 + 진회색 텍스트.
       ' / ' 나 ' ↔ ' 는 줄바꿈. 한/영 혼용(맑은고딕 볼드). 배경 위에서도 잘 보이게 반투명 크림."""
    text = text.replace("↔", "／").replace(" / ", "\n").replace("/", "\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()] or [text]
    S = 40
    f = ImageFont.truetype(BOXFONT, S)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = max(int(d0.textlength(l, font=f)) for l in lines)
    lh = int(S * 1.34)
    padx, pady = 26, 16
    accent = 12
    W = accent + padx * 2 + tw
    H = pady * 2 + lh * len(lines)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rad = 20
    # 크림 반투명 박스 + 은은한 외곽선
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=rad, fill=(255, 251, 244, 238),
                        outline=(60, 55, 50, 90), width=2)
    # 코랄 왼쪽 악센트 바
    d.rounded_rectangle([0, 0, accent + rad, H - 1], radius=rad, fill=(240, 138, 116, 255))
    d.rectangle([accent, 0, accent + rad, H - 1], fill=(255, 251, 244, 238))
    d.rounded_rectangle([0, 0, accent, H - 1], radius=0, fill=(240, 138, 116, 255))
    for i, l in enumerate(lines):
        d.text((accent + padx, pady + i * lh), l, font=f, fill=(45, 42, 40, 255))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    return W, H


SC = parse_scenario(SCENARIO)
con = sqlite3.connect(DB); cur = con.cursor()

# 캐릭터 대표 asset(자리표시 — 렌더러는 char_key로 포즈를 찾음). 경로에 /poses/ 있어야 is_pose 감지.
BASEP = "assets/graphics/poses/mj_w18_present_right.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r:
    JI = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("마담제이W18base", "mj_w18_present_right", "pose", BASEP, "W18 base")); JI = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'mjw18_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

for i, sc in enumerate(SC, 1):
    sk = norm_quotes(sc["ko"]); se = norm_quotes(sc["en"]); gl = sc["glyph"]
    aseq = f"mjw18_s{i:02d}"
    # 좌상단 텍스트박스 PNG
    rel = f"graphics/letters/w18_{i:02d}_box.png"
    bw, bh = make_textbox(gl, f"assets/{rel}")
    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
    gasset = r[0] if r else None
    if gasset is None:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (f"W18박스_{gl[:8]}", f"w18_{i:02d}_box", "letter", rel, "좌상단박스")); gasset = cur.lastrowid
    # 좌상단 static 배치 (cx,cy = 박스 중심)
    gcx = BOX_LEFT + bw / 2
    gcy = BOX_TOP + bh / 2
    gobj = (gasset, int(gcx), int(gcy), 1.0, 6, "static")
    # ★cap_ko/en 을 비워 compile 기본 '버전언어 박스'(draw_note_box)를 끈다 → 내 코랄 텍스트박스만 좌상단에.
    spec = {"cap_ko": "", "cap_en": "", "motion": "static",
            "char_key": CHAR, "char_mode": "teacher", "draw_font": "malgun",
            "draw_dur": 0.0, "draw_text": "", "draw_align": "left",
            "bg": sc["bg"], "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) "
                "VALUES (?,?,?,?,?,?,?)",
                (EP, i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, gobj[0], gobj[1], gobj[2], gobj[3], gobj[4], gobj[5], 0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, JI, CHAR_CX, CHAR_CY, CHAR_SCALE, 5, "gesture", 0))
    bj = make_beats(sc["poses"])
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols:
        fields["description"] = f"마담제이 W18 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
bgs = sorted({s["bg"] for s in SC})
poses = sorted({p for s in SC for p in s["poses"]})
con.close()
print(f"완료: {EP} {n}씬 (마담제이, 전주 한옥마을 · 감정표현·세밀한 마음묘사)")
print(f"배경 {len(bgs)}종: {bgs}")
print(f"포즈(beat) {len(poses)}종: {poses}")
