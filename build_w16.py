# -*- coding: utf-8 -*-
"""W16(취미와 빈도) 74씬 ~10분: 인준, 남이섬.
★ injun_w16 포즈(1376x880 정규화·발끝y800·서기640) → 좌표 300/385/0.675 (0.675*640=432 렌더표준).
★ 걷기 4프레임(walk_r1/r2, walk_l1/l2) + 모션활동 2프레임(_b) 교차 재생 = '움직이는 컷'.
★ 화면 큰 한글 = glyph(write 모션), 나레이션 = script(KO/EN), 로마자는 compile_np가 SRT에만 후처리.
※ S75 면책 자막은 여기 넣지 않는다 — 렌더 후 5개국어 SRT 말미 + 영상 tail로 처리.
사용: python build_w16.py   → 이후 python compile_np.py KO-W16 hangeul_w16_stickman review en
"""
import sqlite3, json, os, re
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"; FONT = "assets/fonts/Cafe24Dongdong.ttf"
PLACE = "Nami Island, Chuncheon"
EP = "KO-W16"; CHAR = "injun_w16"
CHAR_CX, CHAR_CY, CHAR_SCALE = 300, 385, 0.675
SCENARIO = "W16_scenario.md"
MOTION = {"cycling", "jogging", "jump_rope", "badminton", "frisbee", "skateboard"}  # _b 프레임 교차


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


# ---------- 시나리오 파싱 (S1~S74) ----------
def parse_scenario(path):
    out = []
    for ln in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^- \*\*S(\d+)\*\*\s*(.*)$", ln)
        if not m:
            continue
        n = int(m.group(1))
        if n >= 48:
            continue  # 면책 씬 제외
        parts = [p.strip() for p in m.group(2).split("|")]
        if len(parts) < 5:
            continue
        cap_ko = parts[0].strip()
        glyph = parts[1].strip().strip("`").strip()
        narr = parts[2]
        bg = parts[3].strip()
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
        poses = [p.strip() for p in re.split(r"[→/]", posestr)
                 if p.strip() and p.strip() not in ("—", "-", "")]
        # cap_en = EN 나레이션의 첫 괄호 뜻(있으면), 없으면 빈값
        gm = re.search(r"\(([^()]+)\)", en)
        cap_en = gm.group(1).strip() if gm else ""
        out.append(dict(n=n, cap_ko=cap_ko, cap_en=cap_en, glyph=glyph,
                        ko=ko, en=en, bg=bg, poses=poses))
    return out


def expand(p):
    """포즈 키 → (cycle 프레임 리스트, x_from, x_to). 걷기/모션은 다프레임 교차."""
    if p == "walk_right":
        return ["walk_r1", "walk_r2"], 180, 400
    if p == "walk_left":
        return ["walk_l1", "walk_l2"], 400, 180
    if p == "walking":
        return ["walk_r1", "walk_r2"], 250, 360
    if p in MOTION:
        return [p, p + "_b"], CHAR_CX, CHAR_CX
    return [p], CHAR_CX, CHAR_CX


def make_beats(poses):
    ps = poses or ["presenting"]
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


SC = parse_scenario(SCENARIO)
con = sqlite3.connect(DB); cur = con.cursor()

# 캐릭터 대표 asset(자리표시 — 렌더러는 char_key로 포즈를 찾음)
BASEP = "assets/graphics/poses/injun_w16_presenting.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r:
    JI = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("인준W16base", "injun_w16_presenting", "pose", BASEP, "W16 base")); JI = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'inw16_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

for i, sc in enumerate(SC, 1):
    sk = norm_quotes(sc["ko"]); se = norm_quotes(sc["en"]); gl = sc["glyph"]
    rel = f"graphics/letters/w16_{i:02d}.png"; make_glyph(gl, f"assets/{rel}")
    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
    if r:
        gasset = r[0]
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (f"W16글자_{gl[:8]}", f"w16_{i:02d}", "letter", rel, "동동")); gasset = cur.lastrowid
    aseq = f"inw16_s{i:02d}"
    # 글자(화면 큰 한글) 크기·위치 계산 (build_w15 규격 동일)
    GCX = 560; WB = 1265 - GCX; HB = 340; CAP = 150
    best = None
    for _mc in range(4, 17):
        _ls = wrap_write(gl, _mc); _nl = len(_ls); _mx = max(len(l) for l in _ls)
        _f = min(WB / (_mx * 0.98), HB / (_nl * 1.18), CAP)
        if best is None or _f > best[0]:
            best = (_f, _ls, _nl)
    size_px, lines, nlines = best; size_px = max(52, size_px)
    draw_text = "\n".join(lines)
    gscale = round(size_px / 200, 3); blockH = nlines * size_px * 1.18; gcy = int(28 + blockH / 2)
    spec = {"cap_ko": sc["cap_ko"], "cap_en": sc["cap_en"], "motion": "static",
            "char_key": CHAR, "char_mode": "teacher", "draw_font": "cafe24_dongdong",
            "draw_dur": 3.0, "draw_text": draw_text, "draw_align": "left",
            "bg": sc["bg"] if sc["bg"].startswith("bg_") else f"bg_w16_{sc['bg']}",
            "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) "
                "VALUES (?,?,?,?,?,?,?)",
                (EP, i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, gasset, GCX, gcy, gscale, 3, "write", 0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, JI, CHAR_CX, CHAR_CY, CHAR_SCALE, 5, "gesture", 0))
    bj = make_beats(sc["poses"])
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols:
        fields["description"] = f"인준 W16 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
bgs = sorted({(s["bg"] if s["bg"].startswith("bg_") else f"bg_w16_{s['bg']}") for s in SC})
poses = sorted({p for s in SC for p in s["poses"]})
con.close()
print(f"완료: {EP} {n}씨 (인준, 남이섬 취미·빈도)")
print(f"배경 {len(bgs)}종: {[b.replace('bg_w16_','') for b in bgs]}")
print(f"포즈 {len(poses)}종: {poses}")
