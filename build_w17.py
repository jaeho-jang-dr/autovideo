# -*- coding: utf-8 -*-
"""W17(존댓말↔반말·축약어·K컬처) ~10분: 티쳐제이, 경주 불국사.
★ tj_w17 포즈(1024x1024·인물높이~897px·발끝y966) → 좌표 CHAR_CX/CY/SCALE (0.482*897≈432 렌더표준).
★ 걷기 2프레임(walk_right_1/2, walk_left_1/2) 교차 재생 + 좌우 이동 = '움직이는 컷'.
★ 화면 큰 한글 = glyph(write 모션), 나레이션 = script(KO/EN), 로마자는 compile_np가 SRT에만 후처리.
※ S0/S47(무나레이션·추천카드)은 렌더 씬에서 제외(cap_ko가 '('로 시작).
사용: python build_w17.py   → 이후 python compile_np.py KO-W17 hangeul_w17_teacherjay review en
"""
import sqlite3, json, os, re
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"; FONT = "assets/fonts/Cafe24Dongdong.ttf"
PLACE = "Bulguksa, Gyeongju"
EP = "KO-W17"; CHAR = "tj_w17"
# 서기 인물높이 897px → 렌더 432px(check_char_fit STAND_H). feet≈645, head≈213 (1280x720 안, 잘림0)
CHAR_CX, CHAR_CY, CHAR_SCALE = 335, 426, 0.482
SCENARIO = "W17_scenario.md"

VALID = {"wave", "bow", "greet_both", "explain", "explain_open", "present_right",
         "point_left", "point_right", "point_up", "point_self", "think", "compare",
         "finger_up", "clap", "cheer", "surprise", "phone", "phone_show", "sing",
         "hand_ear", "walk_left_1", "walk_left_2", "walk_right_1", "walk_right_2"}


def norm_quotes(s):
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"'([^']*?)([?!.]+)'", r"'\1'\2", s)
    return s


def wrap_write(gl, maxch=7):
    parts = [p.strip() for p in gl.split("/")] if "/" in gl else [gl]
    lines = []
    for part in parts:
        cur = ""
        for tok in part.split():
            if not cur: cur = tok
            elif len(cur) + 1 + len(tok) <= maxch: cur += " " + tok
            else: lines.append(cur); cur = tok
        if cur: lines.append(cur)
    return lines or [gl]


def clean_pose(tok):
    tok = tok.strip().strip("`").strip()
    m = re.search(r"\(=\s*([a-z_0-9]+)\s*\)", tok)   # nod(=present_right) -> present_right
    if m:
        tok = m.group(1)
    tok = tok.split("(")[0].strip()
    return tok if tok in VALID else None


def merge_walk(poses):
    """연속 walk_right_1/2 → 'walk_right'(이동 사이클), walk_left_1/2 → 'walk_left'."""
    out, i = [], 0
    while i < len(poses):
        p = poses[i]
        if p in ("walk_right_1", "walk_right_2"):
            j = i
            while j < len(poses) and poses[j] in ("walk_right_1", "walk_right_2"):
                j += 1
            out.append("walk_right"); i = j
        elif p in ("walk_left_1", "walk_left_2"):
            j = i
            while j < len(poses) and poses[j] in ("walk_left_1", "walk_left_2"):
                j += 1
            out.append("walk_left"); i = j
        else:
            out.append(p); i += 1
    return out


# ---------- 시나리오 파싱 (S1~S46, 카드씬 S0/S47 제외) ----------
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
        if cap_ko.startswith("("):     # (무나레이션·추천카드) = 카드 정적씬 → 제외
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
    """포즈 키 → (cycle 프레임 리스트, x_from, x_to). 걷기는 2프레임 교차 + 좌우 이동."""
    if p == "walk_right":
        return ["walk_right_1", "walk_right_2"], 210, CHAR_CX      # 왼→홈으로 걸어 들어옴
    if p == "walk_left":
        return ["walk_left_1", "walk_left_2"], 460, CHAR_CX
    return [p], CHAR_CX, CHAR_CX


def make_beats(poses):
    ps = poses or ["present_right"]
    share = round(1.0 / len(ps), 4)
    beats = []
    for p in ps:
        cyc, xf, xt = expand(p)
        beats.append({"name": cyc[0], "cycle": cyc, "x_from": xf, "x_to": xt, "dur": share})
    return beats


def make_glyph(gl, path):
    lines = wrap_write(gl, 7)
    f = ImageFont.truetype(FONT, 150)
    W = max(int(f.getlength(l)) for l in lines) + 40
    H = int(len(lines) * 150 * 1.2) + 40
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((20, 20 + i * int(150 * 1.2)), l, font=f, fill=(30, 30, 30, 255))
    bb = im.getbbox(); im = im.crop(bb) if bb else im
    os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path)


def make_yo_x_glyph(path):
    """★교정 '요' 탈락 시각화 — 「끝소리」 / 「요」(빨간 X). ★다른 글자처럼 컴팩트·깔끔하게(무섭지 않게).
    두 줄 같은 크기, 좁은 줄간격, 요만 단정히 감싸는 얇은 빨간 X (사장님 스케치: 끝소리 / 요 x)."""
    S = 120
    f = ImageFont.truetype(FONT, S)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    t1, t2 = "끝소리", "요"
    w1 = d0.textlength(t1, font=f); w2 = d0.textlength(t2, font=f)
    lh = int(S * 1.14)
    W = int(max(w1, w2)) + 60; H = lh * 2 + 40
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text(((W - w1) / 2, 10), t1, font=f, fill=(30, 30, 30, 255))           # 1줄 끝소리
    x2, y2 = (W - w2) / 2, 10 + lh
    d.text((x2, y2), t2, font=f, fill=(30, 30, 30, 255))                     # 2줄 요
    bb2 = d.textbbox((x2, y2), t2, font=f); pad = 8; lw = 9                  # 요만 감싸는 얇은 X
    x0, y0, x1, y1 = bb2[0] - pad, bb2[1] - pad, bb2[2] + pad, bb2[3] + pad
    d.line((x0, y0, x1, y1), fill=(220, 45, 45, 255), width=lw)
    d.line((x0, y1, x1, y0), fill=(220, 45, 45, 255), width=lw)
    bb = im.getbbox(); im = im.crop(bb) if bb else im
    os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path)


SC = parse_scenario(SCENARIO)
con = sqlite3.connect(DB); cur = con.cursor()

# 캐릭터 대표 asset(자리표시 — 렌더러는 char_key로 포즈를 찾음). 경로에 /poses/ 있어야 is_pose 감지됨.
BASEP = "assets/graphics/poses/tj_w17_present_right.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r:
    JI = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("티쳐제이W17base", "tj_w17_present_right", "pose", BASEP, "W17 base")); JI = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'tjw17_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

for i, sc in enumerate(SC, 1):
    sk = norm_quotes(sc["ko"]); se = norm_quotes(sc["en"]); gl = sc["glyph"]
    yox = "[요X]" in gl                      # ★교정: '요' 탈락 시각화 씬(정적 커스텀 글자)
    oneline = "[1줄]" in gl                   # ★교정: 무조건 한 줄로 렌더(줄바꿈 방지)
    gl = gl.replace("[요X]", "").replace("[1줄]", "").strip()
    aseq = f"tjw17_s{i:02d}"
    if yox:
        rel = f"graphics/letters/w17_{i:02d}_yox.png"; make_yo_x_glyph(f"assets/{rel}")
        r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
        gasset = r[0] if r else None
        if gasset is None:
            cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                        ("W17글자_요X", f"w17_{i:02d}_yox", "letter", rel, "요탈락")); gasset = cur.lastrowid
        draw_text = ""
        gobj = (gasset, 730, 165, 1.0, 3, "static")   # 정적 이미지(무변형), 글자영역 상단에 컴팩트
    else:
        rel = f"graphics/letters/w17_{i:02d}.png"; make_glyph(gl, f"assets/{rel}")
        r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
        gasset = r[0] if r else None
        if gasset is None:
            cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                        (f"W17글자_{gl[:8]}", f"w17_{i:02d}", "letter", rel, "동동")); gasset = cur.lastrowid
        # 글자(화면 큰 한글) 크기·위치 계산 (build_w15/16 규격 동일)
        GCX = 560; WB = 1265 - GCX; HB = 340; CAP = 150
        if oneline:                            # ★강제 1줄: wrap 없이 통째로, 폭에 맞춰 크기
            lines, nlines = [gl], 1
            size_px = max(52, min(WB / (max(1, len(gl)) * 0.98), HB / 1.18, CAP))
        else:
            best = None
            for _mc in range(4, 17):
                _ls = wrap_write(gl, _mc); _nl = len(_ls); _mx = max(len(l) for l in _ls)
                _f = min(WB / (_mx * 0.98), HB / (_nl * 1.18), CAP)
                if best is None or _f > best[0]:
                    best = (_f, _ls, _nl)
            size_px, lines, nlines = best; size_px = max(52, size_px)
        draw_text = "\n".join(lines)
        gscale = round(size_px / 200, 3); blockH = nlines * size_px * 1.18; gcy = int(28 + blockH / 2)
        gobj = (gasset, GCX, gcy, gscale, 3, "write")
    spec = {"cap_ko": sc["cap_ko"], "cap_en": sc["cap_en"], "motion": "static",
            "char_key": CHAR, "char_mode": "teacher", "draw_font": "cafe24_dongdong",
            "draw_dur": 3.0, "draw_text": draw_text, "draw_align": "left",
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
        fields["description"] = f"티쳐제이 W17 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
bgs = sorted({s["bg"] for s in SC})
poses = sorted({p for s in SC for p in s["poses"]})
con.close()
print(f"완료: {EP} {n}씬 (티쳐제이, 경주 불국사 · 반말·축약어·K컬처)")
print(f"배경 {len(bgs)}종: {bgs}")
print(f"포즈(beat) {len(poses)}종: {poses}")
