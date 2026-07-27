# -*- coding: utf-8 -*-
"""W22(여행 경험·미래 계획) : 지은(jieun_w22), 전망대. build_w21 계승.
 - 캐릭터 = jieun_w22 (1024x1280·발끝1209·몸높이770 → scale 0.561, injun_w20/mj_w21 동일 규격).
 - 걷기 = walk_r_0..9 / walk_l_0..9 (10프레임 순환). 포즈 = 등록된 직접 이름(9정지+동작대표).
 - 배경 = 시나리오 씬별 bg 키(elevator_up 등) → assets/graphics/bg/bg_w22_<key>.png (정지스틸).
 - 파라메트릭 = 동동체 한글, 캐릭터 정지 반대편, 1~3줄. 자막=영어(SUB_LANGS=en). 나레이션 Emma+선희 DB.
사용: python build_w22.py → SUB_LANGS=en WALK_STRIDE_SEC=1.08 python compile_np.py KO-W22 hangeul_w22_jieun review en
"""
import sqlite3, json, os, re
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"
PLACE = "Seoul Sky, Seoul"
EP = "KO-W22"; CHAR = "jieun_w22"
SCEN = "W22/W22_scenario.md"; MOTION = "W22_motion.md"
CANVAS_W = 1280
CHAR_CX, CHAR_CY, CHAR_SCALE = 640, 345, 0.561
NWALK = 10

# ★씬별 배경 = 정지배경 위주 + 배경영상은 각 1씬만. (12 정지 + 6 영상키)
SCENE_BG = {
    1: "elevator_up", 2: "arrival", 3: "sky_window", 4: "window_bench", 5: "deck_interior",
    6: "glass_floor", 7: "planning", 8: "cafe", 9: "panorama_day", 10: "panorama_day",
    11: "sea_view", 12: "panorama_day", 13: "window_bench", 14: "deck_interior", 15: "arrival",
    16: "sunset_city", 17: "window_bench", 18: "planning", 19: "cafe", 20: "cafe",
    21: "window_bench", 22: "panorama_day", 23: "deck_interior", 24: "night_stars",
}
VIDEO_SCENES = {1, 3, 5, 6, 16, 24}       # 이 씬만 배경 동영상(각 1회), 나머지는 정지배경
BGVID = {"elevator_up": "W22/bg/vid_elevator_up_v2.mp4", "sky_window": "W22/bg/vid_sky_window_v2.mp4",
         "deck_interior": "W22/bg/vid_deck_interior.mp4", "sunset_city": "W22/bg/vid_sunset_city_v2.mp4",
         "glass_floor": "W22/bg/vid_glass_floor_v2.mp4", "night_stars": "W22/bg/vid_night_stars_v2.mp4"}


def z2x(z): return int(round(z / 100.0 * CANVAS_W))
def norm_quotes(s): return s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')


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
        if cap_ko.startswith("("):
            continue
        glyph = parts[1].strip().strip("`").strip()
        narr = parts[2]
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
        # 배경 키 = parts[3] 의 `key`[..] 에서 추출
        bg = "deck_interior"
        bm = re.search(r"`?([a-z_]+)`?\s*\[", parts[3]) if len(parts) > 3 else None
        if bm:
            bg = bm.group(1)
        out[seq] = dict(glyph=glyph, ko=ko, en=eside, bg=bg)
    return out


def korean_only(s): return re.sub(r"\([^)]*\)", "", s).strip()


def scene_keywords(glyph, ko):
    kws = []
    g = korean_only(glyph)
    for cand in re.split(r"[·,/]", g) + re.findall(r"'([^']+)'", ko):
        cand = cand.strip()
        if re.search(r"[0-9_]", cand):
            continue
        syl = re.findall(r"[가-힣]", cand)
        if len(syl) < 1 or len(syl) > 10:
            continue
        if cand and cand not in kws:
            kws.append(cand)
    return kws[:3]


WRITE_CY = 236; WRITE_ALIGN = "left"
WRITE_MAX_W, WRITE_MAX_H = 560, 400
WRITE_MIN_PX, WRITE_MAX_PX = 62, 128
WRITE_MARGIN = 40


def keyword_layout(keywords):
    from PIL import ImageFont
    if not keywords:
        return "", 0.3, 0, 0
    f = ImageFont.truetype("assets/fonts/Cafe24Dongdong.ttf", 100)
    nlines = len(keywords)
    wmax = max(f.getbbox(k)[2] for k in keywords) or 1
    size = min(100 * WRITE_MAX_W / wmax, WRITE_MAX_H / (nlines * 1.35), WRITE_MAX_PX)
    size = max(WRITE_MIN_PX, size)
    return "\n".join(keywords), round(size / 200.0, 4), int(wmax * size / 100.0), int(nlines * size * 1.35)


def load_pose_set():
    con = sqlite3.connect(DB)
    rows = [r[0] for r in con.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))]
    con.close()
    return set(rows)


POSE_SET = load_pose_set()

# 동작 동영상(64프레임 시퀀스) — 처음~끝 1회 재생(oneshot). 프레임수는 DB 등록분에서 계산.
import re as _re
MOTION_ACTS = ["wave", "open_arms", "point_right", "point_left", "dream", "magnify", "look_out"]
MOTION_N = {}
for _a in MOTION_ACTS:
    _idx = [int(_re.match(rf"{_a}_(\d+)$", p).group(1)) for p in POSE_SET if _re.match(rf"{_a}_(\d+)$", p)]
    MOTION_N[_a] = (max(_idx) + 1) if _idx else 0
# 정지포즈(단일 프레임)
STILL_POSES = {"explain", "present_right", "present_left", "think_recall", "shake",
               "phone_tap", "count_two", "bag_ready", "heart"}


def resolve_pose(tok, paren):
    tok = tok.strip()
    if tok in MOTION_ACTS and MOTION_N.get(tok, 0) > 0:
        return tok
    return tok if tok in POSE_SET else None


def parse_motion(path):
    scenes = {}
    for ln in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^- \*\*S(\d+)\*\*\s*(.*)$", ln)
        if not m:
            continue
        seq = int(m.group(1)); body = m.group(2)
        cols = body.split("|")
        sz = re.search(r"Z(-?\d+)", cols[0] if cols else "")
        cur_x = z2x(int(sz.group(1))) if sz else CHAR_CX
        beats = []
        for tm in re.finditer(r"`([a-z_0-9]+)`(?:\(([^)]*)\))?", body):
            tok = tm.group(1); paren = tm.group(2) or ""
            if tok in ("walk_r", "walk_l"):
                am = re.search(r"Z(-?\d+)\s*→\s*\*\*Z(-?\d+)\*\*", body[tm.start():tm.start() + 80])
                xf, xt = (z2x(int(am.group(1))), z2x(int(am.group(2)))) if am else (cur_x, cur_x)
                beats.append(("walk", tok, xf, xt)); cur_x = xt
            else:
                pose = resolve_pose(tok, paren)
                if pose:
                    beats.append(("pose", pose, cur_x, cur_x))
        scenes[seq] = beats
    return scenes


def cycle_for(kind, tok):
    if kind == "walk":
        d = "r" if tok == "walk_r" else "l"
        return [f"walk_{d}_{i}" for i in range(NWALK)], False
    if tok in MOTION_ACTS and MOTION_N.get(tok, 0) > 0:
        return [f"{tok}_{i}" for i in range(MOTION_N[tok])], True   # oneshot 동작 시퀀스
    return [tok], False


def make_beats(parsed):
    if not parsed:
        parsed = [("pose", "explain", CHAR_CX, CHAR_CX)]
    # 동작 시퀀스·걷기는 시간 더 배분(충분히 재생), 정지포즈는 기본
    weights = []
    for (k, tok, _, _) in parsed:
        if k == "walk":
            weights.append(0.9)
        elif tok in MOTION_ACTS:
            weights.append(2.0)     # 동작 동영상 = 충분한 시간(처음~끝 재생)
        else:
            weights.append(1.0)
    tot = sum(weights) or 1.0
    out = []
    for (k, tok, xf, xt), w in zip(parsed, weights):
        cyc, oneshot = cycle_for(k, tok)
        b = {"name": cyc[0], "cycle": cyc, "x_from": xf, "x_to": xt, "dur": round(w / tot, 4)}
        if oneshot:
            b["oneshot"] = True
        out.append(b)
    return out


# ---------- build ----------
SCN = parse_scenario(SCEN)
MOT = parse_motion(MOTION)
con = sqlite3.connect(DB); cur = con.cursor()

BASEP = "assets/graphics/poses/jieun_w22_present_right.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r:
    JI = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("지은W22base", "jieun_w22_present_right", "pose", BASEP, "W22 base")); JI = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'jw22_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

seqs = sorted(SCN)
for i in seqs:
    sc = SCN[i]
    sk = norm_quotes(sc["ko"]); se = norm_quotes(sc["en"])
    aseq = f"jw22_s{i:02d}"
    kws = scene_keywords(sc["glyph"], sk)
    dt, wscale, blk_w, blk_h = keyword_layout(kws)
    bgk = SCENE_BG.get(i, sc["bg"])
    bgkey = "bg_w22_" + bgk
    bgvid = BGVID.get(bgk) if i in VIDEO_SCENES else None    # 영상은 지정 씬만
    bj = make_beats(MOT.get(i, []))
    # ★글자 위치 = 캐릭터가 '말하는' 포즈/동작 위치 반대편(걷기·화면밖 도착점 무시 → 얼굴 안 가림)
    _talk = [b for b in bj if not b["cycle"][0].startswith("walk")]
    stop_x = (max(_talk, key=lambda b: b["dur"])["x_from"] if _talk else (bj[-1]["x_to"] if bj else CHAR_CX))
    write_cx = (CANVAS_W - WRITE_MARGIN - blk_w) if stop_x < CANVAS_W / 2 else WRITE_MARGIN
    spec = {"cap_ko": "", "cap_en": "", "motion": "static",
            "char_key": CHAR, "char_mode": "teacher", "draw_font": "cafe24_dongdong",
            "draw_dur": 1.6, "draw_text": dt, "draw_align": WRITE_ALIGN,
            "bg": bgkey, "bg_video": bgvid, "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) "
                "VALUES (?,?,?,?,?,?,?)", (EP, i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, JI, CHAR_CX, CHAR_CY, CHAR_SCALE, 5, "gesture", 0))
    if dt:
        cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                    "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, JI, write_cx, WRITE_CY, wscale, 7, "write", 0))
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols:
        fields["description"] = f"지은 W22 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
bgs = sorted({"bg_w22_" + SCN[i]["bg"] for i in seqs})
allposes = sorted({c for i in seqs for b in make_beats(MOT.get(i, [])) for c in b["cycle"]})
con.close()
print(f"완료: {EP} {n}씬 (지은, 전망대 · 여행 경험/계획)")
print(f"배경 {len(bgs)}종: {[b[len('bg_w22_'):] for b in bgs]}")
print(f"사용 포즈/프레임 {len(allposes)}종")
missing = [p for p in allposes if p not in POSE_SET]
print(f"★DB 미등록 포즈: {missing if missing else '없음'}")
