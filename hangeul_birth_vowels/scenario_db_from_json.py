#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scenario_db_from_json.py — 제미나이(조감독)가 작성한 시나리오 JSON을 content.db에 등록(범용).

입력 JSON 스키마:
{
  "episode": "KO-W01D3", "title_ko": "...", "title_en": "...",
  "scenes": [{"seq","dur","ko","en","cap_ko","cap_en","gestures":[pose...],"words":[...],
              "bg","bg_prompt","critter"}]
}
캐릭터 포즈는 gestures[0]을 좌측 캐릭터 에셋으로 배치(스틱맨/졸라맨/졸라걸 모두 직접 파일명 우선).
단어 잉크 글리프 사전렌더 + scene_objects(좌 캐릭터 + 우 단어 오토드로우) + bg 프롬프트 내보내기.

사용: python hangeul_birth_vowels/scenario_db_from_json.py scratch/w1d3_scenario.json --prefix hangeul_w1d3_flat
"""
import os
import sys
import json
import argparse
import sqlite3

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stickman_factory import SS  # noqa

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "channel", "content.db")
WORD_DIR = os.path.join(ROOT, "assets", "graphics", "words")
BG_DIR = os.path.join(ROOT, "assets", "graphics", "bg")
os.makedirs(WORD_DIR, exist_ok=True)
os.makedirs(BG_DIR, exist_ok=True)
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"
LOCAL_DIR = os.path.join(ROOT, "hangeul_birth_vowels")


def render_word_glyph(text, out_path, px=240):
    pad = int(px * 0.18)
    f = ImageFont.truetype(FONT_BD, px)
    tmp = Image.new("RGBA", (10, 10)); d0 = ImageDraw.Draw(tmp)
    l, t, r, b = d0.textbbox((0, 0), text, font=f)
    W = (r - l) + pad * 2; H = (b - t) + pad * 2
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fbig = ImageFont.truetype(FONT_BD, px * SS)
    lb, tb, rb, bb = d.textbbox((0, 0), text, font=fbig)
    ox = (W * SS - (rb - lb)) / 2 - lb; oy = (H * SS - (bb - tb)) / 2 - tb
    d.text((ox, oy), text, font=fbig, fill=(247, 243, 233, 70),
           stroke_width=int(px * SS * 0.06), stroke_fill=(247, 243, 233, 70))
    d.text((ox, oy), text, font=fbig, fill=(34, 31, 28, 255))
    img.resize((W, H), Image.LANCZOS).save(out_path)


# 제미나이가 쓴 졸라맨 포즈 별칭(zm_*) → 실제 파일(zollaman_*) 매핑
POSE_MAP = {
    "zm_base": "zollaman_base", "zm_waving": "zollaman_waving", "zm_pointing": "zollaman_pointing",
    "zm_point_l": "zollaman_pointing", "zm_point_r": "zollaman_pointing", "zm_thinking": "zollaman_thinking",
    "zm_reading": "zollaman_reading", "zm_studying": "zollaman_studying", "zm_cheering": "zollaman_cheering",
    "zm_clapping": "zollaman_clapping", "zm_jumping": "zollaman_jumping", "zm_bowing": "zollaman_bowing",
    "zm_sitting": "zollaman_sitting", "zm_explain": "zollaman_pointing",
    # 졸라걸 별칭
    "zw_base": "zollanyeo_base", "zw_waving": "zollanyeo_waving", "zw_pointing": "zollanyeo_pointing",
    "zw_point_l": "zollanyeo_pointing", "zw_point_r": "zollanyeo_pointing", "zw_thinking": "zollanyeo_thinking",
    "zw_reading": "zollanyeo_reading", "zw_studying": "zollanyeo_studying", "zw_cheering": "zollanyeo_cheering",
    "zw_clapping": "zollanyeo_clapping", "zw_raising_hand": "zollanyeo_raising_hand", "zw_explain": "zollanyeo_pointing",
}


def norm_pose(nm):
    return POSE_MAP.get(nm, nm)


def resolve_asset(cur, name):
    name = norm_pose(name)
    r = cur.execute("SELECT id FROM assets WHERE name_en=?", (name,)).fetchone()
    if r:
        return r[0]
    cands = [os.path.join(ROOT, "assets", "graphics", "poses", f"{name}.png"),
             os.path.join(ROOT, "home_vocab", f"{name}.png"),
             os.path.join(ROOT, "assets", "graphics", "poses", f"stickman_{name}.png"),
             os.path.join(ROOT, "assets", "graphics", "words", f"{name}.png"),
             os.path.join(ROOT, "assets", "graphics", f"{name}.png")]
    fp = next((os.path.relpath(c, ROOT).replace("\\", "/") for c in cands if os.path.exists(c)), None)
    if not fp:
        raise FileNotFoundError(name)
    typ = "word" if name.startswith("word_") else ("character" if "/poses/" in fp else "object")
    cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                (name, name, typ, fp, "auto by scenario_db_from_json"))
    return cur.lastrowid


def _glyph_wh(word):
    try:
        im = Image.open(os.path.join(WORD_DIR, f"word_{word}.png"))
        return im.width, im.height
    except Exception:
        return len(word) * 165, 300


def _fit_scale(word, base, maxw):
    gw, _ = _glyph_wh(word)
    return round(max(0.40, min(base, maxw / max(1, gw))), 3)


def layout_for(s):
    """좌측 캐릭터(gestures[0]) + 우측 단어(오토드로우).
    실제 글리프 크기로 세로 간격을 잡아 '첫단/둘째단'이 붙지 않게, 폭/세로 초과 시 자동 축소."""
    char = s["gestures"][0]
    items = [(char, 285, 470, 0.60, 5, 0, "gesture")]
    words = s.get("words") or []
    n = len(words)
    CX, CY, AVAIL, MARGIN = 880, 360, 460, 30
    if n == 0:
        return items
    if n == 1:
        sc = _fit_scale(words[0], 1.0, 520)
        items.append((f"word_{words[0]}", CX, CY, sc, 4, 0, "draw"))
        return items
    if n <= 3:
        base = 0.70 if n == 2 else 0.52
        scales = [_fit_scale(w, base if i == 0 else round(base * 0.8, 3), 430) for i, w in enumerate(words)]
        heights = [_glyph_wh(w)[1] * scales[i] for i, w in enumerate(words)]
        total = sum(heights) + MARGIN * (n - 1)
        if total > AVAIL:                                   # 세로 공간 초과 → 전체 축소
            f = AVAIL / total
            scales = [round(sc * f, 3) for sc in scales]
            heights = [h * f for h in heights]
            total = AVAIL
        y = CY - total / 2
        for i, w in enumerate(words):
            items.append((f"word_{w}", CX, int(round(y + heights[i] / 2)), scales[i], 4, 0, "draw"))
            y += heights[i] + MARGIN
        return items
    # 4+ : 2열 그리드 (복습)
    sc = 0.46
    rows = (n + 1) // 2
    scales = [_fit_scale(w, sc, 300) for w in words]
    rowh = max(_glyph_wh(w)[1] * scales[i] for i, w in enumerate(words)) + 28
    y0 = CY - rowh * (rows - 1) / 2
    for i, w in enumerate(words):
        col, row = i % 2, i // 2
        items.append((f"word_{w}", 730 + col * 330, int(round(y0 + row * rowh)), scales[i], 4, 0, "draw"))
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--prefix", required=True)
    args = ap.parse_args()
    data = json.load(open(os.path.join(ROOT, args.json) if not os.path.isabs(args.json) else args.json, encoding="utf-8"))
    EP = data["episode"]; SCENES = data["scenes"]; PROJECT = args.prefix

    # word glyphs
    words = sorted({w for s in SCENES for w in (s.get("words") or [])})
    for w in words:
        render_word_glyph(w, os.path.join(WORD_DIR, f"word_{w}.png"))

    # bg prompts (key: prompt)
    bgf = os.path.join(ROOT, f"{args.prefix}_bg_prompts.txt")
    open(bgf, "w", encoding="utf-8").write(
        "\n".join(f"{s['bg']}: {s['bg_prompt']}" for s in SCENES) + "\n")

    con = sqlite3.connect(DB); cur = con.cursor()
    runtime = sum(int(s["dur"]) for s in SCENES)
    cur.execute("DELETE FROM episodes WHERE code=?", (EP,))
    cur.execute(
        "INSERT INTO episodes (code, category, title_kr, title_en, status, runtime_sec, "
        "narration_kr, narration_en, created_at) VALUES (?,?,?,?,?,?,?,?, datetime('now'))",
        (EP, "KO", data["title_ko"], data["title_en"], "scripting", runtime,
         "\n".join(s["ko"] for s in SCENES), "\n".join(s["en"] for s in SCENES)))

    cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
    for s in SCENES:
        spec = {"cap_ko": s["cap_ko"], "cap_en": s["cap_en"], "motion": "animate",
                "gesture_seq": [norm_pose(g) for g in s["gestures"]], "words": s.get("words") or [],
                "bg": s["bg"], "bg_prompt": s["bg_prompt"], "critter": s.get("critter"),
                "place_en": s.get("place_en", "")}
        cur.execute("INSERT INTO scenes (episode, seq, script_kr, script_en, image_prompt, veo_prompt, sfx, duration_sec) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (EP, s["seq"], s["ko"], s["en"], json.dumps(spec, ensure_ascii=False), "", "", int(s["dur"])))

    cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
    nobj = 0
    for s in SCENES:
        for (name, cx, cy, scale, z, isp, mo) in layout_for(s):
            aid = resolve_asset(cur, name)
            if "/poses/" in (cur.execute("SELECT file_path FROM assets WHERE id=?", (aid,)).fetchone()[0]):
                scale = round(scale * 1.10, 3); cy -= 18
            cur.execute("INSERT INTO scene_objects (episode, scene_seq, asset_id, cx, cy, scale, z_order, is_point, motion_type) "
                        "VALUES (?,?,?,?,?,?,?,?,?)", (EP, s["seq"], aid, cx, cy, scale, z, isp, mo))
            nobj += 1

    cur.execute("DELETE FROM video_projects WHERE name=?", (PROJECT,))
    cur.execute("INSERT INTO video_projects (name, title_kr, description, local_dir, n_scenes, runtime_sec, status, notes, created_at, updated_at) "
                "VALUES (?,?,?,?,?,?,?,?, datetime('now'), datetime('now'))",
                (PROJECT, data["title_ko"], "flat-canvas Flow bg + character + auto-draw (Gemini scenario)",
                 LOCAL_DIR, len(SCENES), runtime, "scripting", f"episode={EP}"))
    con.commit(); con.close()
    print(f"episode {EP}: {len(SCENES)} scenes, ~{runtime}s, {nobj} placements, words={words}")
    print(f"bg prompts -> {os.path.relpath(bgf, ROOT)}")


if __name__ == "__main__":
    main()
