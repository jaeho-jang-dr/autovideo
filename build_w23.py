# -*- coding: utf-8 -*-
"""W23(모임 약속·시간 조율) : 인준(injun_w23), 에버랜드. build_w22 계승.
 - 캐릭터 = injun_w23 (1024x1280 · 발끝 1209 · 몸높이 770 → scale 0.561).
 - 걷기 = walk_r_0..6 / walk_l_0..6 (7프레임 순환, 한 스트라이드 250px 실측 · 0.75초).
 - 동작 동영상 = 64컷 시퀀스 12종(windmill_up 폐기). 정지 포즈 16종 + 좌향 `_flip` 10종.
 - 배경 = 씬별 bg 키 18종. `[VIDEO]` 표기 씬만 배경 동영상, 나머지는 정지.
 - 파라메트릭 = 카페24 동동 한글, **캐릭터 반대편**, 1~3줄(가능한 한 많은 한글).
 - ★방향 원칙 P1~P8 = W23/W23_motion_plan.md. 위반이 있으면 빌드가 실패한다.
사용: python build_w23.py
    → SUB_LANGS=en WALK_STRIDE_SEC=0.75 python compile_np.py KO-W23 hangeul_w23_injun review en
"""
import sqlite3, json, os, re, sys, glob

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"
PLACE = "Everland, Yongin"
EP = "KO-W23"; CHAR = "injun_w23"
SCEN = "W23/W23_scenario.md"; MOTION = "W23_motion.md"
CANVAS_W = 1280
CHAR_CX, CHAR_CY, CHAR_SCALE = 640, 345, 0.561
NWALK = 7                       # ★W23 걷기컷은 7프레임(한 스트라이드)

# 방향 태그 실측값 — W23/W23_motion_plan.md 2-1
DIR_R = {"present_right", "point_board", "hand_on_post", "lean_rail"}          # 오른쪽으로 뻗음
DIR_L = {"present_left", "explain", "tap_board", "count_three",
         "thumbs_up", "raising_hand"}                                          # 왼쪽으로 뻗음


def z2x(z): return int(round(z / 100.0 * CANVAS_W))
def norm_quotes(s): return s.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')


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
        if parts[0].startswith("("):
            continue
        glyph = parts[1].strip().strip("`").strip()
        narr = parts[2]
        ka = re.split(r"\s*→\s*(?=\()", narr, maxsplit=1)
        kside, eside = (ka if len(ka) == 2 else (narr.split("→", 1) if "→" in narr else (narr, "")))
        km = re.search(r'"([^"]*)"', kside)
        ko = km.group(1).strip() if km else kside.strip().strip('"').strip()
        eside = eside.strip()
        if eside.startswith("(") and eside.endswith(")"):
            eside = eside[1:-1].strip()
        bm = re.search(r"`?([a-z_]+)`?\s*\[(\w+)\]", parts[3])
        bg = bm.group(1) if bm else "gate_plaza"
        bgtype = bm.group(2) if bm else "STILL"
        out[seq] = dict(glyph=glyph, ko=ko, en=eside, bg=bg, bgtype=bgtype)
    return out


def korean_only(s): return re.sub(r"\([^)]*\)", "", s).strip()


def scene_keywords(glyph, ko):
    """★P8 — 가능한 한 많은 한글을 보여준다(1~3줄). 글리프 우선, 모자라면 나레이션 인용구로 채움."""
    kws = []
    for cand in re.split(r"[·,/]", korean_only(glyph)) + re.findall(r"'([^']+)'", ko):
        cand = cand.strip().strip("`")
        if re.search(r"[0-9_]", cand):
            continue
        syl = re.findall(r"[가-힣]", cand)
        if not (1 <= len(syl) <= 12):
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


con0 = sqlite3.connect(DB)
POSE_SET = {r[0] for r in con0.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))}
con0.close()

# 동작 동영상(64컷 시퀀스) — DB 등록분에서 프레임 수 산출. windmill_up 은 폐기.
MOTION_ACTS = ["greet_wave", "run_slide_in", "catch_petal", "lean_back_surprise", "backflip_land",
               "spin_phone", "railing_vault", "point_far_follow", "board_write", "jump_highfive",
               "follow_parade", "onehand_freeze", "check_ok"]
MOTION_N = {}
for _a in MOTION_ACTS:
    _idx = [int(re.match(rf"{_a}_(\d+)$", p).group(1)) for p in POSE_SET if re.match(rf"{_a}_(\d+)$", p)]
    MOTION_N[_a] = (max(_idx) + 1) if _idx else 0


def parse_motion(path):
    scenes, errs = {}, []
    for ln in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^- \*\*S(\d+)\*\*\s*(.*)$", ln)
        if not m:
            continue
        seq = int(m.group(1)); body = m.group(2)
        sz = re.search(r"Z(-?\d+)", body)
        cur_x = z2x(int(sz.group(1))) if sz else CHAR_CX
        beats = []
        for tm in re.finditer(r"`([a-z_0-9]+)`", body):
            tok = tm.group(1)
            if tok in ("walk_r", "walk_l"):
                am = re.search(r"Z(-?\d+)\s*→\s*\*\*Z(-?\d+)\*\*", body[tm.start():tm.start() + 80])
                xf, xt = (z2x(int(am.group(1))), z2x(int(am.group(2)))) if am else (cur_x, cur_x)
                beats.append(("walk", tok, xf, xt)); cur_x = xt
            elif tok in MOTION_ACTS and MOTION_N.get(tok, 0) > 0:
                # ★run_slide_in 은 실이동 클립 — 도착 x 가 따로 적혀 있으면 그리로 이동
                am = re.search(r"Z(-?\d+)\s*→\s*\*\*Z(-?\d+)\*\*", body[max(0, tm.start() - 60):tm.start() + 80])
                xt = z2x(int(am.group(2))) if (am and tok == "run_slide_in") else cur_x
                beats.append(("act", tok, cur_x, xt)); cur_x = xt
            elif tok in POSE_SET:
                beats.append(("pose", tok, cur_x, cur_x))
                # ★방향 검증 P1·P2
                base = tok[:-5] if tok.endswith("_flip") else tok
                if base in DIR_R or base in DIR_L:
                    eff = "L" if base in DIR_L else "R"
                    if tok.endswith("_flip"):
                        eff = "R" if eff == "L" else "L"
                    want = "R" if cur_x < CANVAS_W / 2 else "L"
                    if eff != want:
                        errs.append(f"S{seq} `{tok}` x={cur_x} → {want} 를 향해야 하는데 {eff}")
            else:
                errs.append(f"S{seq} `{tok}` 자산 없음")
        scenes[seq] = beats
    return scenes, errs


def cycle_for(kind, tok):
    if kind == "walk":
        d = "r" if tok == "walk_r" else "l"
        return [f"walk_{d}_{i}" for i in range(NWALK)], False
    if kind == "act":
        return [f"{tok}_{i}" for i in range(MOTION_N[tok])], True      # oneshot 64컷
    return [tok], False


def make_beats(parsed):
    if not parsed:
        parsed = [("pose", "explain", CHAR_CX, CHAR_CX)]
    weights = []
    for (k, tok, _, _) in parsed:
        weights.append(0.9 if k == "walk" else (2.0 if k == "act" else 1.0))
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
MOT, ERRS = parse_motion(MOTION)
if ERRS:
    print("★방향/자산 검증 실패 — 빌드 중단"); [print("  ", e) for e in ERRS]; sys.exit(1)

missing_bg = sorted({f"bg_w23_{s['bg']}" for s in SCN.values()
                     if not os.path.exists(f"assets/graphics/bg/bg_w23_{s['bg']}.png")})
if missing_bg:
    print("★배경 정지 파일 없음 — 빌드 중단:", missing_bg); sys.exit(1)

con = sqlite3.connect(DB); cur = con.cursor()
# ★기준 에셋 경로에 반드시 `/poses/` 가 들어가야 한다 — 렌더러가 `is_pose = "/poses/" in path`
#   로 판정해 동작선(anim_seq) 재생 여부를 정한다. poses_still_norm 에 두면 정지 이미지만 나온다.
BASEP = "assets/graphics/poses/injun_w23_explain.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r:
    JI = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("인준W23base", "injun_w23_explain", "pose", BASEP, "W23 base")); JI = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'iw23_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

seqs = sorted(SCN)
used_acts = set()
for i in seqs:
    sc = SCN[i]
    sk = norm_quotes(sc["ko"]); se = norm_quotes(sc["en"])
    aseq = f"iw23_s{i:02d}"
    dt, wscale, blk_w, blk_h = keyword_layout(scene_keywords(sc["glyph"], sk))
    bgkey = "bg_w23_" + sc["bg"]
    bgvid = f"W23/bg_clips/bg_w23_{sc['bg']}.mp4" if sc["bgtype"] == "VIDEO" else None
    if bgvid and not os.path.exists(bgvid):
        bgvid = None
    bj = make_beats(MOT.get(i, []))
    used_acts |= {b["cycle"][0].rsplit("_", 1)[0] for b in bj if b.get("oneshot")}
    # ★P5 — 글자는 '말하는' 위치의 반대편(걷기·화면밖 도착점 무시 → 얼굴 안 가림)
    _talk = [b for b in bj if not b["cycle"][0].startswith("walk")]
    stop_x = (max(_talk, key=lambda b: b["dur"])["x_to"] if _talk else (bj[-1]["x_to"] if bj else CHAR_CX))
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
        fields["description"] = f"인준 W23 {aseq}"
    cur.execute(f"INSERT INTO anim_sequences ({','.join(fields)}) VALUES ({','.join('?'*len(fields))})",
                list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
allposes = sorted({c for i in seqs for b in make_beats(MOT.get(i, [])) for c in b["cycle"]})
con.close()

bgs = sorted({SCN[i]["bg"] for i in seqs})
vids = sorted({SCN[i]["bg"] for i in seqs if SCN[i]["bgtype"] == "VIDEO"})
print(f"완료: {EP} {n}씬 (인준 · 에버랜드 · 모임 약속/시간 조율)")
print(f"배경 {len(bgs)}종 (동영상 {len(vids)}: {vids})")
print(f"사용 포즈/프레임 {len(allposes)}종")
unused = [a for a in MOTION_ACTS if a not in used_acts]
print(f"★동작컷 사용 {len(used_acts)}/{len(MOTION_ACTS)}종" + (f" · 미사용 {unused}" if unused else " · 전원 배정 ✅"))
miss = [p for p in allposes if p not in POSE_SET]
print(f"★DB 미등록 포즈: {miss if miss else '없음'}")
