# -*- coding: utf-8 -*-
"""W20(돌발 상황 대처·문제 해결) ~8분: 인준(캐주얼), 이태원.
★ build_w19 계승. 차이점:
  - 캐릭터 = injun_w20 (인준 컷아웃, 1024x1280·발끝 y1209·몸높이 770 통일).
  - 걷기 = Veo 투명컷 7프레임 순환(walk_r_0..6 / walk_l_0..6) — anim beat cycle+이동.
  - ★사장님 지시(활동적): 배경(장소)이 바뀌는 씬마다 walk_r을 앞에 붙여 '걸어서 그 장소로
    들어오며' 시작 → 이태원 이곳저곳 많이 걸어다니게. 이어서 다양한 표정으로 설명.
  - 화면글자 = 좌상단 코랄 텍스트박스(cap 비워 draw_note_box 끔).
  - 나레이션=선희(한)+Emma(영), ' ' 예문=선희 DB클립. 배경키 'w20_' 접두.
사용: python build_w20.py  → python compile_np.py KO-W20 hangeul_w20_injun review en
"""
import sqlite3, json, os, re
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"
BOXFONT = "C:/Windows/Fonts/malgunbd.ttf"
PLACE = "Itaewon, Seoul"
EP = "KO-W20"; CHAR = "injun_w20"
# injun_w20 포즈 = 1024x1280·발끝 y1209·몸높이 770. STAND_H=432 → scale=432/770=0.561.
CHAR_CX, CHAR_CY, CHAR_SCALE = 330, 345, 0.561
SCENARIO = "W20_scenario_v2.md"   # ★v2: 중복제거·걷기 명시·영어자막만
BG_PREFIX = "w20_"

# ★왼편 텍스트박스 = 그 언어의 '페이지 제목'. KO=glyph(한글), EN=아래 영어 제목(사장님 지시).
TITLE_EN = [
    "Welcome to Itaewon", "Sudden Emergencies", "Don't Be Shy to Ask for Help",
    "To Be Sick", "To Get Hurt", "Pharmacy", "Hospital", "Emergency Call: 119",
    "Police: 112", "To Lose Something", "Please Help Me", 'Core Pattern: "I Lost ___"',
    "I Lost My Wallet", "Help! I Lost My Bag", "Where Did You Lose It?",
    "It Hurts / I Got Hurt", "Ask Politely", "What Happened & Where", "What Happened?",
    "Calling 119", "Calling 112", "Slowly & Clearly", "At the Pharmacy",
    "At Lost & Found", "Koreans Help Each Other", "Don't Forget to Say Thanks",
    "Today's Summary", "See You Next Time",
]

BOX_LEFT = 20
BOX_TOP = 54

POSE_KEYS = {"wave", "greet_both", "bow", "explain", "explain_open", "present_right",
             "point_right", "point_self", "point_up", "worried", "hurt", "help_gesture",
             "search_pockets", "phone", "calm", "reassure", "relieved", "surprised",
             "curious", "aha", "proud", "smile_bright", "determined", "think", "nod_agree",
             "thumbs_up", "weigh", "confident", "finger_up", "look_view",
             # 시나리오에 등장하나 별도 클립 없는 것 → 유사 포즈로 매핑
             "excited"}
POSE_ALIAS = {"excited": "determined", "cheer": "thumbs_up"}   # 없는 포즈 안전 매핑
WALK = {"walk_r", "walk_l", "walk_deep"}   # walk_r=짧게(→30%), walk_deep=깊게(→중간), walk_l=돌아감
VALID = POSE_KEYS | WALK
NWALK = 7   # walk_r_0..6 / walk_l_0..6
DEEP_X = 660   # 깊은 걸어들어오기 도착점(중간≈640 이상)


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
    tok = POSE_ALIAS.get(tok, tok)
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


def add_walking(SC):
    """★활동적: 장소(배경)가 바뀌는 첫 씬마다 walk_r을 맨 앞에 붙여 '걸어서 들어오며' 시작.
       이미 걷기로 시작하면 두지 않는다. 이태원 이곳저곳 많이 걸어다니는 느낌."""
    prev = None
    for sc in SC:
        starts_walk = sc["poses"] and sc["poses"][0] in WALK
        if sc["bg"] != prev and not starts_walk:
            sc["poses"] = ["walk_r"] + sc["poses"]
        prev = sc["bg"]
    return SC


def expand(p):
    """포즈 토큰 → (순환 포즈 리스트, x_from, x_to). 걷기=7컷 순환하며 이동."""
    if p == "walk_r":       # 왼끝 → 30%(짧게, 오른쪽 향함)
        return ([f"walk_r_{i}" for i in range(NWALK)], 120, CHAR_CX)
    if p == "walk_deep":    # 왼끝 → 중간 이상(깊게, 오른쪽 향함)
        return ([f"walk_r_{i}" for i in range(NWALK)], 120, DEEP_X)
    if p == "walk_l":       # 오른끝 → 왼쪽 제자리(오른→왼, 왼쪽 향함)
        return ([f"walk_l_{i}" for i in range(NWALK)], 1050, CHAR_CX)
    return ([p], CHAR_CX, CHAR_CX)


def scene_keywords(ko_narr):
    """씬 나레이션에서 따옴표 친 한글 키워드·짧은표현을 모두 추출(숫자·밑줄·긴것 제외),
       중복제거·최대 5개. ★파라메트릭은 한글만(사장님 지시: 한글은 그림·동동체로 자랑)."""
    kws = []
    for m in re.findall(r"'([^']+)'", ko_narr):
        m = m.strip()
        if re.search(r"[0-9_]", m):                 # 숫자(119)·밑줄 제외
            continue
        syl = re.findall(r"[가-힣]", m)
        if len(syl) < 2 or len(syl) > 7:            # 2~7음절(단어·짧은표현)
            continue
        if m not in kws:
            kws.append(m)
    return kws[:5]


# 오른편 상단 파라메트릭 — 우상단 1/4(x≈700~1270, y≈20~350) 안에 키워드 모두, 동동체, 1.5배 크게
WRITE_CX, WRITE_CY = 985, 175           # 블록 중심(우상단 사분면)
WRITE_MAX_W = 545                       # 가용 폭
WRITE_MAX_H = 320                       # 가용 높이(top half)
WRITE_MIN_PX, WRITE_MAX_PX = 46, 96     # 자막보다 크게 ~ 1.5배(너무 크지 않게)


def keyword_layout(keywords):
    """키워드 리스트 → (draw_text[\\n 줄바꿈], scale). 각 키워드 한 줄, 우상단 1/4 안에 맞게 가변 크기."""
    from PIL import ImageFont
    if not keywords:
        return "", 0.3
    fp = "assets/fonts/Cafe24Dongdong.ttf"
    f = ImageFont.truetype(fp, 100)
    nlines = len(keywords)
    wmax = max(f.getbbox(k)[2] for k in keywords) or 1      # 100px 기준 최장 줄 폭
    size_w = 100 * WRITE_MAX_W / wmax                        # 폭 맞춤
    size_h = WRITE_MAX_H / (nlines * 1.35)                   # 높이 맞춤(줄간격 1.35)
    size = min(size_w, size_h, WRITE_MAX_PX)
    size = max(WRITE_MIN_PX, size)
    return "\n".join(keywords), round(size / 200, 4)


def make_beats(poses):
    ps = poses or ["present_right"]
    # 걷기 비트는 화면시간을 조금 더 짧게(걸어 들어온 뒤 설명에 시간 배분)
    weights = [0.7 if p in WALK else 1.0 for p in ps]
    tot = sum(weights)
    beats = []
    for p, w in zip(ps, weights):
        cyc, xf, xt = expand(p)
        beats.append({"name": cyc[0], "cycle": cyc, "x_from": xf, "x_to": xt, "dur": round(w / tot, 4)})
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


SC = parse_scenario(SCENARIO)   # ★v2: 걷기는 시나리오에 명시(walk_r/walk_deep/walk_l), 자동삽입 안 함
con = sqlite3.connect(DB); cur = con.cursor()

BASEP = "assets/graphics/poses/injun_w20_present_right.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r:
    JI = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("인준W20base", "injun_w20_present_right", "pose", BASEP, "W20 base")); JI = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'inw20_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

for i, sc in enumerate(SC, 1):
    sk = norm_quotes(sc["ko"]); se = norm_quotes(sc["en"]); gl = sc["glyph"]
    aseq = f"inw20_s{i:02d}"
    rel = f"graphics/letters/w20_{i:02d}_box.png"
    bw, bh = make_textbox(gl, f"assets/{rel}")
    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
    gasset = r[0] if r else None
    if gasset is None:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (f"W20박스_{gl[:8]}", f"w20_{i:02d}_box", "letter", rel, "좌상단박스")); gasset = cur.lastrowid
    gcx = BOX_LEFT + bw / 2
    gcy = BOX_TOP + bh / 2
    kws = scene_keywords(sk)   # ★오른편 상단 파라메트릭 = 그 씬 키워드 모두(한글만)
    if not kws:                # 따옴표 키워드가 숫자뿐이면(예: S9 '112'/'119') glyph의 한글로 폴백
        _gk = [r for r in re.findall(r"[가-힣]+", gl) if len(r) >= 2]
        if _gk:
            kws = [max(_gk, key=len)]
    dt, wscale = keyword_layout(kws)   # 멀티라인·동동체·1.5배·우상단 1/4 자동맞춤
    # ★왼편 박스 = 언어별 제목(draw_note_box가 그림). KO=glyph(한글), EN=영어 제목.
    cap_en = TITLE_EN[i - 1] if i - 1 < len(TITLE_EN) else ""
    spec = {"cap_ko": gl, "cap_en": cap_en, "motion": "static",
            "char_key": CHAR, "char_mode": "teacher", "draw_font": "cafe24_dongdong",
            "draw_dur": 1.6, "draw_text": dt, "draw_align": "center",
            "bg": BG_PREFIX + sc["bg"], "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) "
                "VALUES (?,?,?,?,?,?,?)",
                (EP, i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    # (정적 한글 박스 씬오브젝트 제거 — 박스는 render_lang의 draw_note_box가 언어별로 그린다)
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, JI, CHAR_CX, CHAR_CY, CHAR_SCALE, 5, "gesture", 0))
    if dt:   # ★오른편 상단 파라메트릭 = 키워드 모두(동동체·한글만·우상단 1/4)
        cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) "
                    "VALUES (?,?,?,?,?,?,?,?,?)", (EP, i, gasset, WRITE_CX, WRITE_CY, wscale, 7, "write", 0))
    bj = make_beats(sc["poses"])
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols:
        fields["description"] = f"인준 W20 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
bgs = sorted({BG_PREFIX + s["bg"] for s in SC})
poses = sorted({p for s in SC for p in s["poses"]})
nwalk = sum(1 for s in SC if s["poses"] and s["poses"][0] in WALK)
con.close()
print(f"완료: {EP} {n}씬 (인준, 이태원 · 돌발 상황 대처)")
print(f"배경 {len(bgs)}종")
print(f"포즈(beat) {len(poses)}종: {poses}")
print(f"★걷기로 시작하는 씬(걸어 들어오는 장면): {nwalk}/{n}")
