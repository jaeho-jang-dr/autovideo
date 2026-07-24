# -*- coding: utf-8 -*-
"""W19(논리적 의견과 설득하기) ~8분: 지은(등산복), 설악산.
★ build_w18 계승. 차이점:
  - 캐릭터 = jieun_w19 (지은 컷아웃, 1024x1280·발끝 y1210·몸높이 770 통일).
  - 걷기 = Veo 투명컷 8프레임 순환(walk_r_0..7 / walk_l_0..7) — anim beat cycle+이동.
  - 화면글자 = 좌상단 코랄 텍스트박스(build_w18 방식, cap 비워 draw_note_box 끔).
  - 나레이션=선희(한)+Emma(영), ' ' 예문=선희 DB클립(★Azure 처음부터). 배경키 'w19_' 접두.
사용: python build_w19.py  → python compile_np.py KO-W19 hangeul_w19_jieun review en
"""
import sqlite3, json, os, re
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"
BOXFONT = "C:/Windows/Fonts/malgunbd.ttf"
PLACE = "Seoraksan Mountain"
EP = "KO-W19"; CHAR = "jieun_w19"
# jieun_w19 포즈 = 1024x1280·발끝 y1210·몸높이 770. STAND_H=432 → scale=432/770=0.561.
CHAR_CX, CHAR_CY, CHAR_SCALE = 330, 345, 0.561
SCENARIO = "W19_scenario.md"
BG_PREFIX = "w19_"

BOX_LEFT = 20
BOX_TOP = 54

POSE_KEYS = {"wave", "greet_both", "bow", "explain", "explain_open", "present_right",
             "point_right", "point_self", "point_up", "raise_hand", "finger_up", "think",
             "weigh", "confident", "nod_agree", "shake_no", "persuade", "tilt_puzzled",
             "smile_bright", "laugh_big", "excited", "surprised", "aha", "proud", "curious",
             "sparkle", "pout", "determined", "clap", "cheer", "thumbs_up", "look_view"}
WALK = {"walk_r", "walk_l"}
VALID = POSE_KEYS | WALK


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
        if cap_ko.startswith("("):        # 카드 정적씬 제외(S0)
            continue
        glyph = parts[1].strip().strip("`").strip()
        narr = parts[2]
        bg = parts[3].strip().strip("`").strip()
        posestr = parts[4].strip()
        # ★KO/EN 구분자 = 'EN 여는 괄호 앞의 →'. 나레이션 내부 화살표(예: '예쁘다 → 예쁘다고')와 충돌 방지.
        ka = re.split(r"\s*→\s*(?=\()", narr, maxsplit=1)
        if len(ka) == 2:
            kside, eside = ka
        elif "→" in narr:
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
        out.append(dict(cap_ko=cap_ko, glyph=glyph, ko=ko, en=en, bg=bg, poses=poses))
    return out


def expand(p):
    """포즈 토큰 → (순환 포즈 리스트, x_from, x_to). 걷기=8컷 순환하며 화면 안으로 이동."""
    if p == "walk_r":
        return ([f"walk_r_{i}" for i in range(8)], 130, CHAR_CX)     # 왼→제자리(걸어 들어옴)
    if p == "walk_l":
        return ([f"walk_l_{i}" for i in range(8)], CHAR_CX, 130)     # 제자리→왼(돌아감)
    return ([p], CHAR_CX, CHAR_CX)


def make_beats(poses):
    ps = poses or ["present_right"]
    share = round(1.0 / len(ps), 4)
    beats = []
    for p in ps:
        cyc, xf, xt = expand(p)
        beats.append({"name": cyc[0], "cycle": cyc, "x_from": xf, "x_to": xt, "dur": share})
    return beats


def make_textbox(text, path):
    """좌상단 텍스트박스: 크림 라운드 박스 + 코랄 왼쪽 악센트 바 + 진회색 텍스트."""
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
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=rad, fill=(255, 251, 244, 238),
                        outline=(60, 55, 50, 90), width=2)
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

BASEP = "assets/graphics/poses/jieun_w19_present_right.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r:
    JI = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("지은W19base", "jieun_w19_present_right", "pose", BASEP, "W19 base")); JI = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'jiw19_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

for i, sc in enumerate(SC, 1):
    sk = norm_quotes(sc["ko"]); se = norm_quotes(sc["en"]); gl = sc["glyph"]
    aseq = f"jiw19_s{i:02d}"
    rel = f"graphics/letters/w19_{i:02d}_box.png"
    bw, bh = make_textbox(gl, f"assets/{rel}")
    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
    gasset = r[0] if r else None
    if gasset is None:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (f"W19박스_{gl[:8]}", f"w19_{i:02d}_box", "letter", rel, "좌상단박스")); gasset = cur.lastrowid
    gcx = BOX_LEFT + bw / 2
    gcy = BOX_TOP + bh / 2
    spec = {"cap_ko": "", "cap_en": "", "motion": "static",
            "char_key": CHAR, "char_mode": "teacher", "draw_font": "malgun",
            "draw_dur": 0.0, "draw_text": "", "draw_align": "left",
            "bg": BG_PREFIX + sc["bg"], "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) "
                "VALUES (?,?,?,?,?,?,?)",
                (EP, i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, gasset, int(gcx), int(gcy), 1.0, 6, "static", 0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, JI, CHAR_CX, CHAR_CY, CHAR_SCALE, 5, "gesture", 0))
    bj = make_beats(sc["poses"])
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols:
        fields["description"] = f"지은 W19 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
bgs = sorted({BG_PREFIX + s["bg"] for s in SC})
poses = sorted({p for s in SC for p in s["poses"]})
con.close()
print(f"완료: {EP} {n}씨 (지은, 설악산 · 논리적 의견·설득)")
print(f"배경 {len(bgs)}종: {bgs}")
print(f"포즈(beat) {len(poses)}종: {poses}")
