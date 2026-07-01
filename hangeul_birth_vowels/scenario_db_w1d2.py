#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scenario_db_w1d2.py — 훈민정음 초급 1주차 **화요일(2강) · 어휘**
                      "모음만으로 만드는 첫 단어" 시나리오를 content.db 에 기록.

설계(플랫 캔버스 + 약간의 애니메이션, Stickly 드라마 풍):
 - 대사(씬)마다 Flow 파스텔 배경 1장(다양하되 일정한 색감 + 소품 + 드라마틱).
 - 좌측: 설명하는 스틱맨(파라메트릭 제스처 순환).
 - 우측: 오늘의 글자/단어가 오토드로잉(획/잉크 리빌)으로 생겼다 사라짐.
 - 하단: 자막. 상단: 캡션.
 - 배경 한쪽 귀퉁이에 작은 새/벌/나비가 살짝 — 강의에 방해 안 될 만큼만(주체는 글자·캐릭터).

대상 어휘(모음만/ㅇ+모음): 아이 · 이 · 오이 · 우유 · 오 · 아우  (지난 1강 단모음 8개의 첫 활용)
재실행: python hangeul_birth_vowels/scenario_db_w1d2.py
"""
import os
import sys
import json
import math
import random
import sqlite3

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stickman_factory import stamp_stroke, SS

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "channel", "content.db")
EP = "KO-W01D2"
PROJECT = "hangeul_w1d2_flat"
LOCAL_DIR = os.path.join(ROOT, "hangeul_birth_vowels")
WORD_DIR = os.path.join(ROOT, "assets", "graphics", "words")
BG_DIR = os.path.join(ROOT, "assets", "graphics", "bg")
os.makedirs(WORD_DIR, exist_ok=True)
os.makedirs(BG_DIR, exist_ok=True)
FONT_BD = "C:/Windows/Fonts/malgunbd.ttf"

STYLE = {
    "look": "flat-canvas Flow pastel background + parametric stickman (left) + auto-draw letters (right)",
    "method": "Flow bg per scene (consistent pastel) + flat-layered PIL compositing + ink auto-draw",
    "ref": "youtu.be/clMvmiiM_Ro (Stickly style ref) + A_sticky screenshots",
    "narration": "edge-tts SunHi female, 1.1x; bilingual KR/EN toggle",
    "font": "C:/Windows/Fonts/malgun.ttf",
    "canvas": [1280, 720],
    "layout": "character LEFT, letters RIGHT, subtitle BOTTOM, tiny ambient critter in a corner",
}

# 각 씬: seq, dur, ko, en, cap_ko, cap_en, gestures(스틱맨 포즈 순환), words(우측 오토드로우),
#        bg(Flow 배경 키), bg_prompt(Flow 생성 프롬프트), critter(작은 배경 동물/None), sfx
SCENES = [
    dict(seq=1, dur=11,
         ko="안녕하세요! 지난 시간엔 단모음 여덟 개를 배웠죠. 오늘은 그 모음만으로 만드는 아주 쉬운 첫 단어들을 함께 익혀 봐요.",
         en="Hello! Last time we learned the eight simple vowels. Today, let's learn some very first words made with those vowels alone.",
         cap_ko="모음으로 만드는 첫 단어", cap_en="First Words from Vowels",
         gestures=["greeting_wave", "presenting", "arms_open"], words=[],
         bg="bg_w1d2_s01", critter=None, sfx="chime",
         bg_prompt="soft pastel storybook meadow at gentle morning, low rolling green hill, a few simple round flowers, big open cream-blue sky, thick friendly outlines, flat colors, no text, no people, leave the left third and the lower area empty and open, children's book illustration, 16:9"),
    dict(seq=2, dur=12,
         ko="첫 번째 단어, '아이'. 어린아이를 뜻하는 말이에요. 받침 없이 'ㅏ'와 'ㅣ', 모음 두 개로만 이루어졌어요. 따라 해 보세요, 아이.",
         en="Our first word, 'a-i' — it means a child. It's made of just two vowels, 'a' and 'i', with no batchim. Say it with me: a-i.",
         cap_ko="아이 = a child", cap_en="아이 = a child",
         gestures=["presenting", "pointing_right", "z_explain"], words=["아이"],
         bg="bg_w1d2_s02", critter="bird", sfx="pop",
         bg_prompt="cozy pastel park playground, a small soft slide and a single round tree on the right side, gentle cream-green palette, thick outlines, flat storybook colors, no text, no people, leave the left third and lower area open, 16:9"),
    dict(seq=3, dur=11,
         ko="두 번째, '이'. 입을 옆으로 활짝 당겨 내는 'ㅣ' 하나면 단어가 돼요. 우리 몸의 '이', 바로 치아를 뜻하지요.",
         en="Second, 'i'. A single 'i' — lips pulled wide — is already a word. It means 'tooth'.",
         cap_ko="이 = a tooth", cap_en="이 = a tooth",
         gestures=["z_explain", "mouth_demo", "pointing_right"], words=["이"],
         bg="bg_w1d2_s03", critter=None, sfx="pop",
         bg_prompt="warm pastel cream room interior, a round wall mirror on the right and a small shelf, soft peach and cream palette, thick friendly outlines, flat storybook colors, no text, no people, leave left third and lower area open, 16:9"),
    dict(seq=4, dur=13,
         ko="세 번째, '오이'. 아삭아삭한 초록 채소죠. 'ㅗ'와 'ㅣ', 역시 모음 두 개예요. 입술을 동그랗게 모았다가 옆으로 당기며, 오이.",
         en="Third, 'o-i' — a crunchy green cucumber. Again two vowels, 'o' and 'i'. Round your lips, then pull them wide: o-i.",
         cap_ko="오이 = a cucumber", cap_en="오이 = a cucumber",
         gestures=["presenting", "z_point_r", "z_explain"], words=["오이"],
         bg="bg_w1d2_s04", critter="bee", sfx="pop",
         bg_prompt="cute pastel vegetable garden bed with leafy green plants and a low wooden fence on the right, soft pastel green and brown palette, thick outlines, flat storybook colors, no text, no people, leave left third and lower area open, 16:9"),
    dict(seq=5, dur=13,
         ko="네 번째, '우유'. 하얗고 고소한 우유예요. 'ㅜ'와 'ㅠ', 둘 다 입술을 동그랗게 내미는 소리죠. 천천히, 우유.",
         en="Fourth, 'u-yu' — sweet white milk. Both 'u' and 'yu' push the lips forward and round. Slowly now: u-yu.",
         cap_ko="우유 = milk", cap_en="우유 = milk",
         gestures=["z_explain", "presenting", "pointing_right"], words=["우유"],
         bg="bg_w1d2_s05", critter="butterfly", sfx="pop",
         bg_prompt="gentle pastel farm field with a small red-roof barn and a friendly round cow far on the right, soft sky-blue and green palette, thick friendly outlines, flat storybook colors, no text, no people, leave left third and lower area open, 16:9"),
    dict(seq=6, dur=11,
         ko="다섯 번째, '오'. 놀랄 때 '오!' 하고 내는 그 소리, 그대로 단어가 돼요. 입술을 동그랗게, 오.",
         en="Fifth, 'o'. The very sound you make when surprised — 'oh!' — is itself a word. Round your lips: o.",
         cap_ko="오 = oh! / five", cap_en="오 = oh! / five",
         gestures=["z_strong", "arms_open", "cheer"], words=["오"],
         bg="bg_w1d2_s06", critter=None, sfx="chime",
         bg_prompt="calm pastel evening sky with five soft glowing stars and a thin crescent moon on the right, gentle lavender to peach gradient, a low dark hill at the bottom, thick outlines, flat storybook colors, no text, no people, leave left third and lower area open, 16:9"),
    dict(seq=7, dur=12,
         ko="여섯 번째, '아우'. 손아래 동생을 다정하게 부르는 말이에요. 'ㅏ'에서 'ㅜ'로, 입을 크게 열었다 동그랗게 모으며, 아우.",
         en="Sixth, 'a-u' — a warm word for a younger sibling. Open wide for 'a', then round for 'u': a-u.",
         cap_ko="아우 = younger sibling", cap_en="아우 = younger sibling",
         gestures=["z_explain", "presenting", "z_point_r"], words=["아우"],
         bg="bg_w1d2_s07", critter="bird", sfx="pop",
         bg_prompt="warm cozy pastel living room with a soft sofa and a round window with curtains on the right, soft cream and warm-orange palette, thick friendly outlines, flat storybook colors, no text, no people, leave left third and lower area open, 16:9"),
    dict(seq=8, dur=13,
         ko="자, 오늘 배운 여섯 단어를 모아 볼까요? 아이, 이, 오이, 우유, 오, 아우. 모두 자음 없이 모음만으로 만든 단어랍니다. 정말 쉽죠?",
         en="Let's gather today's six words: a-i, i, o-i, u-yu, o, a-u. Every one is made of vowels alone, with no consonants. Easy, right?",
         cap_ko="오늘의 단어 모으기", cap_en="Today's Words",
         gestures=["arms_open", "presenting", "z_cheer"],
         words=["아이", "이", "오이", "우유", "오", "아우"],
         bg="bg_w1d2_s08", critter=None, sfx="chime",
         bg_prompt="bright pastel classroom wall with a soft rounded board and a small potted plant in the corner, warm cream and mint palette, thick friendly outlines, flat storybook colors, no text, no people, leave the center and lower area open, 16:9"),
    dict(seq=9, dur=10,
         ko="오늘 배운 단어를 거울 앞에서 또박또박 말해 보세요. 다음 시간엔 자음을 더해 더 많은 단어를 만들어 봐요. 또 만나요!",
         en="Practice today's words clearly in front of a mirror. Next time, we'll add consonants to make even more words. See you soon!",
         cap_ko="복습 · 다음 시간 예고", cap_en="Review & Next Time",
         gestures=["cheer", "greeting_wave", "thumbs_up"], words=[],
         bg="bg_w1d2_s09", critter="bird", sfx="chime",
         bg_prompt="cheerful pastel meadow with a soft rainbow arc and two round balloons on the right, warm bright pastel palette, thick friendly outlines, flat storybook colors, no text, no people, leave left third and lower area open, 16:9"),
]


# ---------- 단어 잉크 글리프 사전 렌더 (오토드로우용 완성본; 렌더러가 진행도로 리빌) ----------
def render_word_glyph(text, out_path, px=240):
    """한글 단어를 잉크 라인 스타일 글리프 PNG(RGBA)로 렌더. 렌더러가 좌→우로 점진 리빌."""
    pad = int(px * 0.18)
    f = ImageFont.truetype(FONT_BD, px)
    tmp = Image.new("RGBA", (10, 10))
    d0 = ImageDraw.Draw(tmp)
    l, t, r, b = d0.textbbox((0, 0), text, font=f)
    tw, th = r - l, b - t
    W = tw + pad * 2
    H = th + pad * 2
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fbig = ImageFont.truetype(FONT_BD, px * SS)
    lb, tb, rb, bb = d.textbbox((0, 0), text, font=fbig)
    ox = (W * SS - (rb - lb)) / 2 - lb
    oy = (H * SS - (bb - tb)) / 2 - tb
    # 잉크 느낌: 짙은 먹색 본체 + 아주 옅은 따뜻한 외곽(번짐) 한 겹
    d.text((ox, oy), text, font=fbig, fill=(247, 243, 233, 70),
           stroke_width=int(px * SS * 0.06), stroke_fill=(247, 243, 233, 70))
    d.text((ox, oy), text, font=fbig, fill=(34, 31, 28, 255))
    img = img.resize((W, H), Image.LANCZOS)
    img.save(out_path)
    return W, H


def ensure_word_glyphs():
    words = sorted({w for s in SCENES for w in s["words"]})
    made = []
    for w in words:
        p = os.path.join(WORD_DIR, f"word_{w}.png")
        render_word_glyph(w, p)
        made.append(w)
    return made


def export_bg_prompts():
    """Flow 배경 생성용 프롬프트를 한 파일로 — 단일 세션 붙여넣기 워크플로우."""
    lines = []
    for s in SCENES:
        lines.append(f"{s['bg']}: {s['bg_prompt']}")
    out = os.path.join(ROOT, "hangeul_w1d2_bg_prompts.txt")
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return out, len(lines)


# ---------- scene_objects 레이아웃 ----------
def layout_for(s):
    """좌측 스틱맨 + 우측 단어(오토드로우) 배치. 반환 [(name,cx,cy,scale,z,is_point,motion)]."""
    items = [("stickman_" + s["gestures"][0], 285, 470, 0.60, 5, 0, "gesture")]
    words = s["words"]
    if not words:
        return items
    if len(words) == 1:
        items.append((f"word_{words[0]}", 880, 320, 1.0, 4, 0, "draw"))
    elif len(words) <= 3:
        for i, w in enumerate(words):
            items.append((f"word_{w}", 880, 230 + i * 150, 0.8, 4, 0, "draw"))
    else:  # recap: 2열 그리드
        for i, w in enumerate(words):
            col, row = i % 2, i // 2
            items.append((f"word_{w}", 740 + col * 320, 220 + row * 150, 0.62, 4, 0, "draw"))
    return items


def resolve_asset(cur, name):
    r = cur.execute("SELECT id FROM assets WHERE name_en=?", (name,)).fetchone()
    if r:
        return r[0]
    # disk lookup
    cands = [
        os.path.join(ROOT, "assets", "graphics", "poses", f"{name}.png"),
        os.path.join(ROOT, "assets", "graphics", "words", f"{name}.png"),
        os.path.join(ROOT, "assets", "graphics", f"{name}.png"),
    ]
    fp = next((os.path.relpath(c, ROOT).replace("\\", "/") for c in cands if os.path.exists(c)), None)
    if not fp:
        raise FileNotFoundError(name)
    typ = "character" if name.startswith("stickman_") else ("word" if name.startswith("word_") else "object")
    cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                (name, name, typ, fp, "auto by scenario_db_w1d2"))
    return cur.lastrowid


def main():
    made = ensure_word_glyphs()
    bgfile, nbg = export_bg_prompts()

    con = sqlite3.connect(DB)
    cur = con.cursor()
    runtime = sum(s["dur"] for s in SCENES)
    nar_kr = "\n".join(s["ko"] for s in SCENES)
    nar_en = "\n".join(s["en"] for s in SCENES)

    cur.execute("DELETE FROM episodes WHERE code=?", (EP,))
    cur.execute(
        "INSERT INTO episodes (code, category, title_kr, title_en, hook_kr, logline_kr, status, "
        "runtime_sec, narration_kr, narration_en, style_profile, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?, datetime('now'))",
        (EP, "KO", "모음으로 만드는 첫 단어 (1주 2강·어휘)", "First Words from Vowels (W1 D2 · Vocabulary)",
         "자음 없이, 모음만으로 만드는 가장 쉬운 첫 단어들",
         "지난 1강 단모음 8개로 '아이·이·오이·우유·오·아우' 어휘를 익힌다 (초급 1주 화요일).",
         "scripting", runtime, nar_kr, nar_en, json.dumps(STYLE, ensure_ascii=False)),
    )

    cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
    for s in SCENES:
        spec = {
            "cap_ko": s["cap_ko"], "cap_en": s["cap_en"], "motion": "animate",
            "gesture_seq": s["gestures"], "words": s["words"],
            "bg": s["bg"], "bg_prompt": s["bg_prompt"], "critter": s["critter"],
        }
        cur.execute(
            "INSERT INTO scenes (episode, seq, script_kr, script_en, image_prompt, veo_prompt, sfx, duration_sec) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (EP, s["seq"], s["ko"], s["en"], json.dumps(spec, ensure_ascii=False), "", s["sfx"], s["dur"]),
        )

    cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
    POSE_SCALE = 1.10
    nobj = 0
    for s in SCENES:
        for (name, cx, cy, scale, z, isp, mo) in layout_for(s):
            aid = resolve_asset(cur, name)
            if name.startswith("stickman_"):
                scale = round(scale * POSE_SCALE, 3); cy -= 18
            cur.execute(
                "INSERT INTO scene_objects (episode, scene_seq, asset_id, cx, cy, scale, z_order, is_point, motion_type) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, s["seq"], aid, cx, cy, scale, z, isp, mo))
            nobj += 1

    cur.execute("DELETE FROM video_projects WHERE name=?", (PROJECT,))
    cur.execute(
        "INSERT INTO video_projects (name, title_kr, description, local_dir, n_scenes, runtime_sec, status, notes, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?, datetime('now'), datetime('now'))",
        (PROJECT, "모음으로 만드는 첫 단어 (플랫캔버스 · 초급 1주 2강)",
         "Flow 파스텔 배경 + 스틱맨 + 글자 오토드로우. 초급 1주 화요일 어휘.",
         LOCAL_DIR, len(SCENES), runtime, "scripting",
         f"episode={EP}; method=flat-canvas Flow bg + parametric stickman + auto-draw"),
    )

    con.commit()
    con.close()
    print(f"episode {EP}: {len(SCENES)} scenes, ~{runtime}s ({runtime/60:.1f}min), {nobj} placements")
    print(f"word glyphs: {made}")
    print(f"bg prompts -> {os.path.relpath(bgfile, ROOT)} ({nbg} scenes)")


if __name__ == "__main__":
    main()
