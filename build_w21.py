# -*- coding: utf-8 -*-
"""W21(인물 묘사·외모/성격) : 마담제이(mj_w21), 성수동. build_w20 계승.
차이점:
 - 캐릭터 = mj_w21 (1024x1280·발끝 y1209·몸높이 770 통일, injun_w20와 동일 규격 → scale 0.561).
 - 걷기 = 투명컷 8프레임 순환(walk_r1..8 / walk_l1..8), 인사 = greet1..8. 방향성 포즈는 좌·우향 정식 생성.
 - ★동작 = W21_motion.md 블로킹을 파싱 → 씬별 beats(걸어들어오기·포즈·걸어나가기, x 절대이동). 화면 전체 로밍.
 - 배경 = 14 고유(컷마다 다름) → SCENE_BG 매핑, 파일 assets/graphics/bg/bg_w21_<key>.png.
 - ★왼편 = 파라메트릭 동동체 한글 키워드(크게·2~3줄, 자막보다 큼). 노트박스(제목) 없음(cap 비움).
 - 자막 = 영어만(SUB_LANGS=en), 나레이션 = Emma(영)+선희 DB(따옴표 한글). touch_hair 포즈 사용 안 함.
사용: python build_w21.py → SUB_LANGS=en WALK_STRIDE_SEC=1.08 python compile_np.py KO-W21 hangeul_w21_madam review en
"""
import sqlite3, json, os, re

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"
PLACE = "Seongsu-dong, Seoul"
EP = "KO-W21"; CHAR = "mj_w21"
SCEN = "W21_scenario.md"; MOTION = "W21_motion.md"
CANVAS_W = 1280
CHAR_CX, CHAR_CY, CHAR_SCALE = 640, 345, 0.561   # cx=로밍 기본(beats가 덮어씀), cy/scale=injun_w20 동일
NWALK = 10
NGREET = 9

# 컷(2씬)마다 고유 배경 14종. 파일 = assets/graphics/bg/bg_w21_<key>.png
SCENE_BG = {
    1: "alley_entrance", 2: "alley_entrance", 3: "brick_street", 4: "brick_street",
    5: "shoe_street", 6: "shoe_street", 7: "cafe_interior", 8: "cafe_interior",
    9: "popup_front", 10: "popup_front", 11: "forest_path", 12: "forest_path",
    13: "brick_factory", 14: "brick_factory", 15: "cafe_terrace", 16: "cafe_terrace",
    17: "understand_ave", 18: "understand_ave", 19: "popup_inside", 20: "popup_inside",
    21: "forest_pond", 22: "forest_pond", 23: "flower_cafe", 24: "flower_cafe",
    25: "print_alley", 26: "rooftop",
}


def z2x(z):
    return int(round(z / 100.0 * CANVAS_W))


def norm_quotes(s):
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    return s


# ---------- 시나리오: 글리프/나레이션(KO/EN)/키워드 ----------
def parse_scenario(path):
    out = {}
    for ln in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^- \*\*S(\d+)\*\*\s*(.*)$", ln)
        if not m:
            continue
        seq = int(m.group(1))
        parts = [p.strip() for p in m.group(2).split("|")]
        if len(parts) < 4:
            continue
        cap_ko = parts[0].strip()
        if cap_ko.startswith("("):        # S0 정적 카드 제외
            continue
        glyph = parts[1].strip().strip("`").strip()
        narr = parts[2]
        ka = re.split(r"\s*→\s*(?=\()", narr, maxsplit=1)   # → (EN)
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
        out[seq] = dict(glyph=glyph, ko=ko, en=eside)
    return out


def korean_only(s):
    s = re.sub(r"\([^)]*\)", "", s)                 # (tall) 등 영어 뜻 제거
    return s.strip()


def scene_keywords(glyph, ko):
    """파라메트릭용 한글 키워드: 글리프(한글) + 나레이션 따옴표 한글, 중복제거·최대 5(2~7음절)."""
    kws = []
    g = korean_only(glyph)
    for cand in [g] + re.findall(r"'([^']+)'", ko):
        cand = cand.strip()
        if re.search(r"[0-9_]", cand):
            continue
        syl = re.findall(r"[가-힣]", cand)
        if len(syl) < 1 or len(syl) > 7:
            continue
        if cand and cand not in kws:
            kws.append(cand)
    return kws[:5]


# 파라메트릭(동동체) — 상단, 크게(W20 대비 +10%), 2~3줄. 좌우 위치는 캐릭터 정지 반대편(빌드가 정함).
WRITE_CY = 236
WRITE_ALIGN = "left"
WRITE_MAX_W, WRITE_MAX_H = 540, 400
WRITE_MIN_PX, WRITE_MAX_PX = 62, 128   # ★글자 10% 키움(56/116 → 62/128)
WRITE_MARGIN = 40                      # 좌/우 여백


def keyword_layout(keywords):
    """→ (draw_text, scale, block_w_px, block_h_px). 블록 폭/높이를 반환해 좌우 배치·겹침판정에 사용."""
    from PIL import ImageFont
    if not keywords:
        return "", 0.3, 0, 0
    f = ImageFont.truetype("assets/fonts/Cafe24Dongdong.ttf", 100)
    nlines = len(keywords)
    wmax = max(f.getbbox(k)[2] for k in keywords) or 1
    size_w = 100 * WRITE_MAX_W / wmax
    size_h = WRITE_MAX_H / (nlines * 1.35)
    size = min(size_w, size_h, WRITE_MAX_PX)
    size = max(WRITE_MIN_PX, size)
    block_w = int(wmax * size / 100.0)
    block_h = int(nlines * size * 1.35)
    return "\n".join(keywords), round(size / 200.0, 4), block_w, block_h


# ---------- 모션 문서: 씬별 blocking → beats ----------
def load_pose_set():
    con = sqlite3.connect(DB)
    rows = [r[0] for r in con.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))]
    con.close()
    return set(rows)


POSE_SET = load_pose_set()
DIRBASE = {"present": ("present_left", "present_right"),
           "point": ("point_left", "point_right_fr"),
           "explain": ("explain_fl", "explain_fr"),
           "look_up": ("look_up_fl", "look_up_fr"),
           "look_around": ("look_around_l", "look_around_r")}
SKIP_POSES = {"touch_hair_long", "touch_hair_short", "touch_hair_long_fl", "touch_hair_long_fr"}


def resolve_pose(tok, paren):
    tok = tok.strip()
    if tok in SKIP_POSES:
        return None
    if tok == "greet":                     # 인사 = greet1..8 순환(cycle_for에서 처리)
        return "greet"
    face = ""
    for f in ("FL", "FR", "L", "R", "F"):
        if re.search(r"\b" + f + r"\b", paren):
            face = f; break
    for base, (lk, rk) in DIRBASE.items():          # 방향성: 표기된 facing으로 좌/우 정식 포즈 선택
        if tok == base or tok.startswith(base):
            if face in ("FL", "L"):
                cand = lk
            elif face in ("FR", "R"):
                cand = rk
            else:                                   # F/미표기 = 기본(정면 base가 있으면 그것)
                cand = tok
            return cand if cand in POSE_SET else (tok if tok in POSE_SET else None)
    return tok if tok in POSE_SET else None


def parse_motion(path):
    scenes = {}
    for ln in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^- \*\*S(\d+)\*\*\s*(.*)$", ln)
        if not m:
            continue
        seq = int(m.group(1)); body = m.group(2)
        cols = body.split("|")
        sz = re.search(r"Z(-?\d+)", cols[1] if len(cols) > 1 else "")
        cur_x = z2x(int(sz.group(1))) if sz else CHAR_CX
        beats = []
        for tm in re.finditer(r"`([a-z_0-9]+)`(?:\(([^)]*)\))?", body):
            tok = tm.group(1); paren = tm.group(2) or ""
            if tok in ("walk_r", "walk_l"):
                am = re.search(r"Z(-?\d+)\s*→\s*\*\*Z(-?\d+)\*\*", body[tm.start():tm.start() + 70])
                if am:
                    xf, xt = z2x(int(am.group(1))), z2x(int(am.group(2)))
                else:
                    xf, xt = cur_x, cur_x
                beats.append(("walk", tok, xf, xt)); cur_x = xt
            elif tok == "turn":
                continue
            else:
                pose = resolve_pose(tok, paren)
                if pose:
                    beats.append(("pose", pose, cur_x, cur_x))
        scenes[seq] = beats
    return scenes


def cycle_for(kind, tok):
    if kind == "walk":
        d = "r" if tok == "walk_r" else "l"
        return [f"walk_{d}{i}" for i in range(1, NWALK + 1)]
    if tok == "greet":
        return [f"greet{i}" for i in range(1, NGREET + 1)]
    return [tok]


def make_beats(parsed):
    if not parsed:
        parsed = [("pose", "present_right", CHAR_CX, CHAR_CX)]
    weights = [0.7 if k == "walk" else 1.0 for (k, _, _, _) in parsed]
    tot = sum(weights) or 1.0
    out = []
    for (k, tok, xf, xt), w in zip(parsed, weights):
        cyc = cycle_for(k, tok)
        out.append({"name": cyc[0], "cycle": cyc, "x_from": xf, "x_to": xt, "dur": round(w / tot, 4)})
    return out


# ---------- 빌드 ----------
SCN = parse_scenario(SCEN)
MOT = parse_motion(MOTION)
con = sqlite3.connect(DB); cur = con.cursor()

BASEP = "assets/graphics/poses/mj_w21_present_right.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r:
    JI = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("마담제이W21base", "mj_w21_present_right", "pose", BASEP, "W21 base")); JI = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'mjw21_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

seqs = sorted(SCN)
for i in seqs:
    sc = SCN[i]
    sk = norm_quotes(sc["ko"]); se = norm_quotes(sc["en"])
    aseq = f"mjw21_s{i:02d}"
    kws = scene_keywords(sc["glyph"], sk)
    dt, wscale, blk_w, blk_h = keyword_layout(kws)
    bgkey = "bg_w21_" + SCENE_BG.get(i, "brick_street")
    bj = make_beats(MOT.get(i, []))
    # ★캐릭터 정지 위치(첫 포즈 beat x) → 파라메트릭 글자는 그 반대편(겹침 방지). 걷기 통과는 무관.
    pose_beats = [b for b in bj if len(b["cycle"]) == 1]
    stop_x = pose_beats[0]["x_from"] if pose_beats else CHAR_CX
    if stop_x < CANVAS_W / 2:                       # 캐릭터가 왼쪽에 정지 → 글자 오른쪽
        write_cx = CANVAS_W - WRITE_MARGIN - blk_w
    else:                                           # 캐릭터가 오른쪽에 정지 → 글자 왼쪽
        write_cx = WRITE_MARGIN
    spec = {"cap_ko": "", "cap_en": "", "motion": "static",
            "char_key": CHAR, "char_mode": "teacher", "draw_font": "cafe24_dongdong",
            "draw_dur": 1.6, "draw_text": dt, "draw_align": WRITE_ALIGN,
            "bg": bgkey, "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) "
                "VALUES (?,?,?,?,?,?,?)", (EP, i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, JI, CHAR_CX, CHAR_CY, CHAR_SCALE, 5, "gesture", 0))
    if dt:
        cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                    "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, JI, write_cx, WRITE_CY, wscale, 7, "write", 0))
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols:
        fields["description"] = f"마담제이 W21 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
bgs = sorted({("bg_w21_" + SCENE_BG[i]) for i in seqs})
allposes = sorted({c for i in seqs for b in make_beats(MOT.get(i, [])) for c in b["cycle"]})
con.close()
print(f"완료: {EP} {n}씬 (마담제이, 성수동 · 인물 묘사)")
print(f"배경 {len(bgs)}종: {[b[len('bg_w21_'):] for b in bgs]}")
print(f"사용 포즈/프레임 {len(allposes)}종")
missing = [p for p in allposes if p not in POSE_SET]
print(f"★DB 미등록 포즈: {missing if missing else '없음'}")
