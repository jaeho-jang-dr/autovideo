# -*- coding: utf-8 -*-
"""W24(종합 진단·수료) : 7캐릭터 3그룹, DDP 전시실. build_w23 계승 — 다중 캐릭터 확장.

★사장님 확정 규칙 (2026-08-03)
 1. **걷기는 한 방향만.** 한 씬 안에서 좌우로 왔다 갔다 하지 않는다. 위반이면 빌드가 실패한다.
 2. **걷기 한 스트라이드 0.75초** (W23 과 동일 · `WALK_STRIDE_SEC=0.75`).
 3. **캐릭터 크기 상한** — 화면상 가장 큰 인물이 이전 회차(W23 인준 432px)를 넘지 않는다.
    규격 px(770 등)에 `GLOBAL_SCALE` 을 곱해 화면 높이를 만든다. 상대 키 비율은 유지된다.
 4. **파라메트릭 글자** — 최대 **2줄**, 이전보다 크게, 좌우 가장자리에서 90px 이상 떼고,
    **인물 얼굴 높이대를 피한다.** 인물이 화면을 넓게 채우면 머리 위로 올린다.
 5. 방향 원칙 P1~P10 — 왼편 인물은 오른쪽, 오른편 인물은 왼쪽을 본다.

입력:  W24/W24_scenario.md (34씬) · W24_motion.md (캐릭터 개별 트랙)
출력:  channel/content.db 의 episodes / scenes / scene_objects
사용:  python build_w24.py [--dry]
"""
import argparse
import glob
import importlib.util
import json
import os
import re
import sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

DB = "channel/content.db"
EP = "KO-W24"
PLACE = "Dongdaemun Design Plaza, Seoul"
SCEN = "W24/W24_scenario.md"
MOTION = "W24_motion.md"
POSE_DIR = "assets/graphics/poses"

CANVAS_W, CANVAS_H = 1280, 720
GROUND_Y = 662                      # 발끝이 닿는 바닥선
MAX_ON_SCREEN_H = 432               # ★W23 인준 화면 높이 — 이걸 넘지 않는다
WALK_STRIDE_SEC = 0.75              # ★한 스트라이드

# 규격 px (W24_concept.md) — 화면 높이 = 규격 × GLOBAL_SCALE
SPEC = {"injun": 770, "zolla_man": 761, "teacher_jay": 749, "stickman": 749,
        "jieun": 706, "zolla_girl": 697, "madam_jay": 693}
GLOBAL_SCALE = MAX_ON_SCREEN_H / max(SPEC.values())      # 432/770 ≈ 0.561

KO2KEY = {"인준": "injun", "지은": "jieun", "티쳐제이": "teacher_jay",
          "마담제이": "madam_jay", "졸라맨": "zolla_man", "졸라걸": "zolla_girl",
          "스틱맨": "stickman"}

# ── 그룹 통짜 컷 (사장님 지시 2026-08-04) ──
# 그룹 영상 한 컷에 2~3명이 상호작용 거리째로 들어있다. 잘라서 흩으면 상호작용이 깨지므로
# **통짜 한 덩어리**로 배치하고, 64컷을 씬 길이에 맞춰 1회 재생한다(motion_type='gseq:<시퀀스>').
CUT_DIR = "W24/group_cuts"
SEQ_PREFIX = "w24_"
REF2KEY = {"zollaman": "zolla_man", "zollagirl": "zolla_girl", "stickman": "stickman",
           "injun": "injun", "jieun": "jieun", "madamjay": "madam_jay",
           "teacherjay": "teacher_jay"}
EDGE_MARGIN = 24                    # 화면 좌우 끝에서 최소 이만큼
MIN_GAP = 16                        # ★인물 덩어리끼리 최소 간격 — 겹치지 않게

# ── 파라메트릭 글자 규칙 (사장님 지시) ──
TEXT_MARGIN = 154                   # ★좌우 안전여백 12%(1280×0.12) — 끝에 붙이지 않는다
                                    #   (W24R/TEXT_LAYOUT_SPEC.md · 사장님 지시 2026-08-06)
TEXT_MAX_LINES = 2                  # ★두 줄까지만
TEXT_MIN_PX, TEXT_MAX_PX = 84, 150  # ★이전(62~128)보다 크게
TEXT_BOX_W, TEXT_BOX_H = 470, 330
TEXT_SIDE_CX = {"left": 300, "right": 980}
TEXT_TOP_CY = 132                   # 인물이 화면을 넓게 채울 때 머리 위
TEXT_SIDE_CY = 250


def log(m):
    print(m, flush=True)


def z2x(z):
    return int(round(z / 100.0 * CANVAS_W))


def parse_scenario(path):
    out = {}
    for ln in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^- \*\*S(\d+)\*\*\s*(.*)$", ln)
        if not m:
            continue
        parts = [p.strip() for p in m.group(2).split("|")]
        if len(parts) < 4:
            continue
        glyph = parts[1].strip().strip("`").strip()
        narr = parts[2]
        ka = re.split(r"\s*→\s*(?=\()", narr, maxsplit=1)
        kside, eside = (ka if len(ka) == 2 else (narr, ""))
        km = re.search(r'"([^"]*)"', kside)
        ko = km.group(1).strip() if km else kside.strip().strip('"')
        eside = eside.strip()
        if eside.startswith("(") and eside.endswith(")"):
            eside = eside[1:-1].strip()
        bm = re.search(r"`?([a-z_]+)`?\s*\[(\w+)\]", parts[3])
        out[int(m.group(1))] = dict(
            title=parts[0], glyph=glyph, ko=ko, en=eside,
            bg=bm.group(1) if bm else "?", bgtype=bm.group(2) if bm else "STILL")
    return out


def parse_motion(path):
    """### S<n> 아래의 `- **캐릭터** Z.. | `포즈`(방향) — 설명` 을 캐릭터별로 모은다."""
    scenes, cur = {}, None
    for ln in open(path, encoding="utf-8").read().splitlines():
        h = re.match(r"^### S(\d+)\s*(.*)$", ln)
        if h:
            cur = int(h.group(1))
            scenes[cur] = []
            continue
        if cur is None:
            continue
        if ln.startswith("### ") or ln.startswith("## "):
            cur = None
            continue
        body = ln.strip()
        if body.startswith("- "):
            body = body[2:].strip()
        if body.startswith("※") or not body.startswith("**"):
            continue
        t = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", body)
        if not t:
            continue
        who = t.group(1).strip()
        if who not in KO2KEY:
            continue
        rest = t.group(2)
        zs = re.findall(r"Z(-?\d+)", rest)
        z_from = int(zs[0]) if zs else 50
        z_to = int(zs[1]) if len(zs) > 1 else z_from
        poses = re.findall(r"`([a-z_0-9]+)`", rest)
        dirm = re.search(r"\((→|←|F)\)", rest)
        ratio = re.search(r"\[(\d+)%\]", rest)
        scenes[cur].append(dict(
            char=KO2KEY[who], z_from=z_from, z_to=z_to, poses=poses,
            dir=dirm.group(1) if dirm else ("F" if "`F`" in rest else ""),
            ratio=int(ratio.group(1)) / 100.0 if ratio else 1.0))
    return scenes


# ★P1(화면 중앙 지향)의 **의도된 예외** — 이유를 적어 둔다. 적지 않은 위반은 빌드가 막는다.
P1_EXCEPT = {
    ("S16", "jieun"): "가리키는 방향 우선 — 오른쪽 길을 가리키고 인준의 시선이 따라간다",
    ("S32", "injun"): "교단이 왼쪽(Z22)이라 꽃다발을 받으려면 왼쪽을 봐야 한다",
}


def check_rules(sc, mo):
    """빌드 게이트 — 위반이 있으면 세우고 고치게 한다."""
    errs = []
    for n in sorted(sc):
        tracks = mo.get(n, [])
        walks = {t["char"]: [p for p in t["poses"] if p.startswith("walk_")] for t in tracks}
        # ① 걷기 단일 방향
        for ch, w in walks.items():
            dirs = {p for p in w}
            if len(dirs) > 1:
                errs.append(f"S{n} {ch}: 한 씬에서 걷기 방향이 둘 — {sorted(dirs)}")
        # ② 방향 원칙 P1 — 왼편은 오른쪽, 오른편은 왼쪽
        for t in tracks:
            if t["dir"] in ("→", "←") and (f"S{n}", t["char"]) not in P1_EXCEPT:
                mid = t["z_to"]
                if mid < 50 and t["dir"] == "←":
                    errs.append(f"S{n} {t['char']}: 왼편(Z{mid})인데 왼쪽을 본다(P1 위반)")
                if mid > 50 and t["dir"] == "→":
                    errs.append(f"S{n} {t['char']}: 오른편(Z{mid})인데 오른쪽을 본다(P1 위반)")
        # ③ 화면 밖 이탈 (도착 위치 기준)
        for t in tracks:
            x = z2x(t["z_to"])
            if not (-40 <= x <= CANVAS_W + 40):
                errs.append(f"S{n} {t['char']}: 도착 x={x} 가 화면 밖")
    return errs


def text_layout(glyph, ko, tracks):
    """글자 내용·크기·위치를 정한다. ★최대 2줄 · 얼굴 회피 · 좌우 여백."""
    from PIL import ImageFont
    kws = []
    for cand in re.split(r"[·,/]", re.sub(r"\([^)]*\)", "", glyph)) + re.findall(r"'([^']+)'", ko):
        cand = cand.strip().strip("`")
        if re.search(r"[0-9_]", cand):
            continue
        syl = re.findall(r"[가-힣ㄱ-ㅎㅏ-ㅣ]", cand)
        if not (1 <= len(syl) <= 12):
            continue
        if cand and cand not in kws:
            kws.append(cand)
    kws = kws[:TEXT_MAX_LINES]                      # ★두 줄까지만
    if not kws:
        return None

    f = ImageFont.truetype("assets/fonts/Cafe24Dongdong.ttf", 100)
    wmax = max(f.getbbox(k)[2] for k in kws) or 1
    size = min(100 * TEXT_BOX_W / wmax, TEXT_BOX_H / (len(kws) * 1.35), TEXT_MAX_PX)
    size = max(TEXT_MIN_PX, size)

    # 인물이 차지한 x 범위 → 반대편에 글자를 둔다
    xs = [z2x(t["z_to"]) for t in tracks] or [640]
    hw = 150
    left_edge, right_edge = min(xs) - hw, max(xs) + hw
    if left_edge > 560:
        side, cx, cy = "left", TEXT_SIDE_CX["left"], TEXT_SIDE_CY
    elif right_edge < 720:
        side, cx, cy = "right", TEXT_SIDE_CX["right"], TEXT_SIDE_CY
    else:
        side, cx, cy = "top", CANVAS_W // 2, TEXT_TOP_CY   # ★인물이 넓게 퍼지면 머리 위로

    # 좌우 여백 보장
    half = wmax * size / 200.0
    cx = max(TEXT_MARGIN + half, min(CANVAS_W - TEXT_MARGIN - half, cx))
    return dict(text="\n".join(kws), lines=len(kws), size=round(size / 200.0, 4),
                cx=int(cx), cy=int(cy), side=side)


_PNGSZ = {}


def png_size(key):
    """포즈 PNG 의 실제 크기(캐시). 겹침 정리에 화면 폭이 필요하다."""
    if key not in _PNGSZ:
        from PIL import Image
        p = f"{POSE_DIR}/w24_{key}.png"
        _PNGSZ[key] = Image.open(p).size if os.path.exists(p) else (300, 700)
    return _PNGSZ[key]


def load_group_map():
    """gen_w24_group_prompts.py 의 ACTS 가 원천 — 씬↔그룹동작 매핑은 추측하지 않는다.
    반환: {씬번호: [dict(seq, members, w, h), ...]}"""
    spec = importlib.util.spec_from_file_location("_g", "gen_w24_group_prompts.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    from PIL import Image
    def scene_nums(txt):
        ns = []
        for a, b in re.findall(r"S(\d+)\s*[~-]\s*S(\d+)", txt):
            ns += list(range(int(a), int(b) + 1))
        ns += [int(x) for x in re.findall(r"S(\d+)", re.sub(r"S\d+\s*[~-]\s*S\d+", "", txt))]
        return sorted(set(ns))

    entries = []
    for key, _grp, refs, scenes, _action in mod.ACTS:
        cuts = sorted(glob.glob(f"{CUT_DIR}/{key}/*.png"))
        if not cuts:
            continue                                   # 컷이 아직 없는 동작(gallery_emerge)
        w, h = Image.open(cuts[0]).size                # 한 동작 안에서 전 프레임 크기 동일
        entries.append((key, refs, scenes, scene_nums(scenes), w, h))

    # ★같은 '범위'를 여러 그룹이 공유하면(예: a/b/c_sit_class 가 모두 "S30~S32")
    #   한 씬에 다 넣지 말고 **씬마다 한 그룹씩** 나눠 배정한다.
    #   고정 배율에서 세 그룹을 한 화면에 넣으면 폭이 넘치고, 크기를 줄이는 건 금지다.
    shared = {}
    for e in entries:
        if "~" in e[2] or "-" in e[2]:
            shared.setdefault(e[2], []).append(e[0])

    out = {}
    for key, refs, scenes, ns, w, h in entries:
        peers = shared.get(scenes, [])
        targets = [ns[peers.index(key) % len(ns)]] if len(peers) > 1 else ns
        for n in targets:
            out.setdefault(n, []).append(dict(
                seq=SEQ_PREFIX + key, members=[REF2KEY[r] for r in refs],
                w=w, h=h, tag=key))
    return out


def layout_no_overlap(boxes):
    """★사장님 지시(2026-08-04) — 인물이 화면 안에서 겹치지 않게 정리한다.
    ★★★캐릭터 크기는 절대 바꾸지 않는다 — 크기가 바뀌면 영상 폐기 수준의 미달이다.
    그래서 겹침은 **위치로만** 푼다. 축소는 하지 않는다. 고정 배율로 안 들어가면
    빈 문자열이 아니라 사유를 돌려주고 빌드를 세운다(사람이 씬을 나눠야 한다).
    boxes: [dict(cx=희망중심, w=화면폭, ...)] — 제자리에서 고친다. 반환=넘침 사유 or None."""
    if not boxes:
        return None
    usable = CANVAS_W - 2 * EDGE_MARGIN
    need = sum(b["w"] for b in boxes) + MIN_GAP * (len(boxes) - 1)
    if need > usable:                                  # ★줄이지 않는다 — 세우고 사람에게 알린다
        return (f"고정 배율로 폭 {need:.0f}px 필요 > 가용 {usable}px — "
                f"덩어리 {len(boxes)}개({', '.join(b['tag'] for b in boxes)})")
    boxes.sort(key=lambda b: b["cx"])
    right = EDGE_MARGIN                                # 왼쪽부터 순서대로 앉힌다
    for b in boxes:
        cx = max(b["cx"], right + b["w"] / 2)
        b["cx"] = cx
        right = cx + b["w"] / 2 + MIN_GAP
    over = (right - MIN_GAP) - (CANVAS_W - EDGE_MARGIN)
    if over > 0:                                       # 오른쪽으로 삐져나가면 통째로 왼쪽으로
        shift = min(over, boxes[0]["cx"] - boxes[0]["w"] / 2 - EDGE_MARGIN)
        for b in boxes:
            b["cx"] -= shift
    for b in boxes:                                    # 마지막 안전장치 — 화면 안으로
        b["cx"] = max(EDGE_MARGIN + b["w"] / 2,
                      min(CANVAS_W - EDGE_MARGIN - b["w"] / 2, b["cx"]))
    return None


def main(dry):
    sc, mo = parse_scenario(SCEN), parse_motion(MOTION)
    log(f"시나리오 {len(sc)}씬 · 모션 트랙 {sum(len(v) for v in mo.values())}줄")
    log(f"캐릭터 화면 높이: 최대 {MAX_ON_SCREEN_H}px (배율 {GLOBAL_SCALE:.4f}) · "
        f"걷기 스트라이드 {WALK_STRIDE_SEC}s")

    errs = check_rules(sc, mo)
    if errs:
        log(f"\n★규칙 위반 {len(errs)}건 — 고친 뒤 다시 돌린다:")
        for e in errs[:20]:
            log(f"   {e}")
        return 1
    log("규칙 검사 통과 (걷기 단일방향 · P1 방향 · 화면 이탈 없음)")

    con = sqlite3.connect(DB); cur = con.cursor()
    # 포즈 자산 등록
    aid = {}
    for p in sorted(glob.glob(f"{POSE_DIR}/w24_*.png")):
        key = os.path.basename(p)[4:-4]
        r = cur.execute("SELECT id FROM assets WHERE file_path=?", (p,)).fetchone()
        if r:
            aid[key] = r[0]
        elif not dry:
            cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path) VALUES (?,?,?,?)",
                        (key, key, "character", p))
            aid[key] = cur.lastrowid
    log(f"포즈 자산 {len(aid)}종 준비")

    if not dry:
        cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
        cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
        cur.execute(
            "INSERT OR REPLACE INTO episodes (code,category,title_kr,title_en,status,notes) "
            "VALUES (?,?,?,?,?,?)",
            (EP, "KO", "종합 진단과 수료 발표", "Wrap-up Diagnostic & Graduation",
             "building", PLACE))

    # ★그룹 통짜 컷 배선 — 씬↔동작 매핑은 gen_w24_group_prompts 의 ACTS 가 원천
    gmap = load_group_map()
    log(f"그룹 동작 {sum(len(v) for v in gmap.values())}건이 {len(gmap)}개 씬에 배정됨")

    nobj, ntext, ngrp, nwrite, overflow = 0, 0, 0, 0, []
    for n in sorted(sc):
        s = sc[n]; tracks = mo.get(n, [])
        # ★compile_stickman.load_scenes 가 요구하는 키를 그대로 채운다(W23 규격).
        bgv = f"assets/graphics/bg/bg_w24_{s['bg']}.mp4"
        spec = dict(
            cap_ko="", cap_en="", motion="static",
            bg=f"bg_w24_{s['bg']}",
            bg_video=(bgv if s["bgtype"] == "VIDEO" and os.path.exists(bgv) else None),
            place_en=PLACE,
            draw_font="cafe24_dongdong", draw_dur=1.6, draw_align="left",
            # W24 전용 메타
            bgtype=s["bgtype"], glyph=s["glyph"], title=s["title"],
            walk_stride_sec=WALK_STRIDE_SEC, chars=[])
        if not dry:
            cur.execute(
                "INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,"
                "duration_sec) VALUES (?,?,?,?,?,?,?)",
                (EP, n, s["ko"], s["en"], json.dumps(spec, ensure_ascii=False), "", 8.0))
        # ── ① 그룹 통짜 컷 덩어리 (상호작용 거리째로 한 장) ──
        boxes, covered = [], set()
        for g in gmap.get(n, []):
            mt = [t for t in tracks if t["char"] in g["members"]]
            scale = round(GLOBAL_SCALE, 4)             # ★전 씬 고정 — 절대 바꾸지 않는다
            anchor = next((k for m in g["members"] for k in aid if k.startswith(m + "_")), None)
            if anchor is None:
                continue                               # 앵커(=/poses/ 경로) 없으면 시퀀스가 안 돈다
            cx = sum(z2x(t["z_to"]) for t in mt) / len(mt) if mt else CANVAS_W / 2
            boxes.append(dict(kind="grp", tag=g["tag"], seq=g["seq"], asset=anchor,
                              cx=cx, w=g["w"] * scale, h=g["h"] * scale, scale=scale))
            covered |= {t["char"] for t in mt}
        # ── ② 그룹에 안 들어간 인물은 기존대로 정지 포즈 ──
        for t in tracks:
            ch = t["char"]
            pose = next((p for p in t["poses"] if not p.startswith("walk_")), None)
            walk = next((p for p in t["poses"] if p.startswith("walk_")), None)
            key = f"{ch}_{pose}" if pose and f"{ch}_{pose}" in aid else None
            h = SPEC[ch] * GLOBAL_SCALE * t["ratio"]
            scale = round(GLOBAL_SCALE * t["ratio"], 4)
            spec["chars"].append(dict(char=ch, pose=pose, walk=walk, dir=t["dir"],
                                      z_from=t["z_from"], z_to=t["z_to"],
                                      cx=z2x(t["z_to"]), cy=int(GROUND_Y - h / 2),
                                      scale=scale, h=int(h), asset=key,
                                      in_group=ch in covered))
            if ch in covered or not key:
                continue
            boxes.append(dict(kind="one", tag=key, asset=key, cx=float(z2x(t["z_to"])),
                              w=png_size(key)[0] * scale, h=h, scale=scale,
                              motion="walk" if walk else "gesture"))
        # ── ③ 겹치지 않게 정리 (위치만 — 크기는 절대 안 건드린다) ──
        err = layout_no_overlap(boxes)
        if err:
            overflow.append(f"S{n}: {err}")
        for b in boxes:
            cy = int(GROUND_Y - b["h"] / 2)
            if not dry:
                cur.execute(
                    "INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,"
                    "motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                    (EP, n, aid[b["asset"]], int(round(b["cx"])), cy, b["scale"], 5,
                     f"gseq:{b['seq']}" if b["kind"] == "grp" else b["motion"], 0))
            nobj += 1
            if b["kind"] == "grp":
                ngrp += 1
        tl = text_layout(s["glyph"], s["ko"], tracks)
        if tl:
            spec["text"] = tl
            spec["draw_text"] = tl["text"]          # ★파라메트릭 글자 본문
            spec["draw_align"] = "center"
            ntext += 1
            # ★★파라메트릭 한글이 화면에 나오려면 **motion_type='write' scene_object** 가 있어야 한다.
            #   compile_stickman 은 이 오브젝트의 cx·cy·scale 로 글자를 그린다(draw_text 는 위치를 모른다).
            #   이게 빠져 있어서 W24 는 글자가 한 자도 안 나왔다(W23 은 36개) — 2026-08-06 복구.
            #   asset 은 경로만 있으면 되는 자리표시자다(파일명이 letter_/word_ 로 시작하지만 않으면 된다).
            if not dry and aid:
                ph = aid[sorted(aid)[0]]
                cur.execute(
                    "INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,"
                    "motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                    (EP, n, ph, tl["cx"], tl["cy"], tl["size"], 7, "write", 0))
                nwrite += 1
        if not dry:
            cur.execute("UPDATE scenes SET image_prompt=? WHERE episode=? AND seq=?",
                        (json.dumps(spec, ensure_ascii=False), EP, n))

    if not dry:
        con.commit()
    con.close()
    log(f"\n{'(모의) ' if dry else ''}씬 {len(sc)} · 배치된 인물 {nobj} · 글자 {ntext}씬")
    log(f"✅ {EP} → {DB}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    raise SystemExit(main(ap.parse_args().dry))
