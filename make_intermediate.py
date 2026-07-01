#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_intermediate.py — 중급 1~7주(KO-W09~W15) 제너릭 빌더.
주차별 (주제·캐릭터·어휘) 설정으로 인트로/어휘/정리/아웃트로 씬을 자동 생성하고,
단어 글리프(PIL) + 발음 오디오(edge-tts, 없으면) 생성 + content.db(episodes/scenes/scene_objects/video_projects) 적재.
캐릭터: 한 영상당 한 명(스틱맨→졸라걸→졸라맨→지은→인준→마담제이→닥터제이). 흔들림 0·왼손/오른쪽 가리키기.
렌더: python hangeul_birth_vowels/compile_stickman.py --episode KO-W09 --prefix hangeul_w9_stickman --lang ko
재실행: python make_intermediate.py            (전체)
        python make_intermediate.py 9 10        (특정 주차만)
"""
import os
import sys
import json
import sqlite3
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from tts_manager import save_tts_edge_tts

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = os.path.join(ROOT, "channel", "content.db")
LDIR = os.path.join(ROOT, "assets", "graphics", "letters")
ADIR = os.path.join(ROOT, "web", "public", "audio", "jamo")
LOCAL_DIR = os.path.join(ROOT, "hangeul_birth_vowels")
FONT = "C:/Windows/Fonts/malgunbd.ttf" if os.path.exists("C:/Windows/Fonts/malgunbd.ttf") else "C:/Windows/Fonts/malgun.ttf"
FF = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs(LDIR, exist_ok=True)
os.makedirs(ADIR, exist_ok=True)

# ---- 주차 설정: (vocab = [(word, ko_gloss, en_gloss)]) ----
WEEKS = {
    9: dict(char="", scale=0.72, cy=385,
            gestures=["pointing_right", "standing", "thinking", "presenting", "cheer", "waving"],
            title_ko="우리 동네와 위치 표현", title_en="Neighborhood & Locations",
            hook_ko="앞·뒤·옆·위·밑, 위치를 말해 봐요",
            vocab=[("앞", "앞쪽", "front"), ("뒤", "뒤쪽", "back"), ("옆", "옆쪽", "beside"),
                   ("위", "위쪽", "above"), ("밑", "아래쪽", "under"),
                   ("마트", "물건을 사는 곳", "the mart"), ("학교", "공부하는 곳", "school")]),
    10: dict(char="zw", scale=0.72, cy=385,
             gestures=["zw_point_l", "zw_base", "zw_thinking", "zw_reading", "zw_cheering", "zw_waving"],
             title_ko="상점 구매와 가격 묻기", title_en="Shopping & Asking Prices",
             hook_ko="얼마예요? 사고 싶을 때 쓰는 말",
             vocab=[("얼마예요", "가격을 묻는 말", "how much?"), ("이거 주세요", "살 때 하는 말", "this, please"),
                    ("결제", "돈을 내는 것", "payment"), ("할인", "값을 깎아 주는 것", "discount")]),
    11: dict(char="zm", scale=0.72, cy=385,
             gestures=["zm_point_l", "zm_base", "zm_thinking", "zm_clapping", "zm_cheering", "zm_waving"],
             title_ko="식당 이용과 맛 표현", title_en="Food Ordering & Dining",
             hook_ko="주문하고 맛을 표현해 봐요",
             vocab=[("주문할게요", "음식을 시킬 때", "I'll order"), ("맛있어요", "맛이 좋아요", "it's delicious"),
                    ("매워요", "맛이 매워요", "it's spicy"), ("달아요", "맛이 달아요", "it's sweet")]),
    12: dict(char="jieun", scale=0.6, cy=400,
             gestures=["jieun_pointing", "jieun_clapping", "jieun_thinking", "jieun_reading", "jieun_cheering", "jieun_waving"],
             title_ko="교통수단과 지하철 환승", title_en="Transportation & Subway",
             hook_ko="버스·지하철로 이동하고 환승해요",
             vocab=[("버스", "타고 다니는 차", "bus"), ("지하철", "땅속을 달리는 기차", "subway"),
                    ("타다", "차에 오르다", "to ride"), ("환승", "갈아타는 것", "transfer")]),
    13: dict(char="injun", scale=0.6, cy=400,
             gestures=["injun_pointing", "injun_holding_book", "injun_thinking", "injun_presenting", "injun_cheering", "injun_waving"],
             title_ko="길 찾기와 위치 안내", title_en="Directions & Wayfinding",
             hook_ko="오른쪽? 왼쪽? 길을 안내해요",
             vocab=[("오른쪽", "오른편", "right"), ("왼쪽", "왼편", "left"),
                    ("똑바로 가다", "곧장 가다", "go straight"), ("건너다", "길을 넘어가다", "to cross")]),
    14: dict(char="madam_jay", scale=0.62, cy=395,
             gestures=["madam_jay_pointing", "madam_jay_base_front", "madam_jay_thinking",
                       "madam_jay_presenting", "madam_jay_cheering", "madam_jay_waving"],
             title_ko="나의 하루 일과와 동작", title_en="Daily Routines & Verbs",
             hook_ko="하루 동작을 동사로 말해요",
             vocab=[("일어나다", "잠에서 깨다", "wake up"), ("공부하다", "배우고 익히다", "study"),
                    ("일하다", "일을 하다", "work"), ("자다", "잠을 자다", "sleep")]),
    15: dict(char="dr_jay", scale=0.52, cy=400,
             gestures=["dr_jay_pointing", "dr_jay_base_front", "dr_jay_thinking",
                       "dr_jay_presenting", "dr_jay_cheering", "dr_jay_waving"],
             title_ko="날씨와 아름다운 사계절", title_en="Weather & Four Seasons",
             hook_ko="맑음·비·눈, 사계절을 말해요",
             vocab=[("맑음", "하늘이 맑음", "sunny"), ("비", "하늘에서 내리는 물", "rain"), ("눈", "하늘에서 내리는 흰 것", "snow"),
                    ("춥다", "날이 차다", "it's cold"), ("덥다", "날이 뜨겁다", "it's hot"), ("사계절", "봄 여름 가을 겨울", "four seasons")]),
    # ===== 중급 8주(W16): 캐릭터 순환 8번째 → 스틱맨 =====
    16: dict(char="", scale=0.72, cy=385,
             gestures=["pointing_right", "standing", "thinking", "presenting", "cheer", "waving"],
             title_ko="취미 생활과 빈도 묘사", title_en="Hobbies & Frequency",
             hook_ko="취미와 '자주·가끔'을 말해요",
             vocab=[("영화 감상", "영화를 보는 취미", "watching movies"), ("운동", "몸을 움직이는 활동", "exercise"),
                    ("자주", "여러 번 자주", "often"), ("가끔", "이따금 가끔", "sometimes"),
                    ("좋아하다", "마음에 들어 하다", "to like")]),
    # ===== 고급 1~8주(W17-24): 캐릭터 순환 동일(스틱맨→졸라걸→졸라맨→지은→인준→마담제이→닥터제이→스틱맨) =====
    17: dict(char="", scale=0.72, cy=385,
             gestures=["pointing_right", "standing", "thinking", "presenting", "cheer", "waving"],
             title_ko="K-컬처와 실생활 구어", title_en="K-Culture & Spoken Korean",
             hook_ko="드라마·K팝 속 진짜 한국어",
             vocab=[("반말", "친구끼리 쓰는 편한 말", "casual speech"), ("축약어", "줄여 쓰는 말", "abbreviation"),
                    ("케이팝", "한국 대중음악", "K-Pop"), ("케이드라마", "한국 드라마", "K-Drama")]),
    18: dict(char="zw", scale=0.72, cy=385,
             gestures=["zw_point_l", "zw_base", "zw_thinking", "zw_reading", "zw_cheering", "zw_waving"],
             title_ko="감정과 세밀한 마음 묘사", title_en="Feelings & Emotional Nuance",
             hook_ko="마음을 한국어로 섬세하게",
             vocab=[("기쁘다", "마음이 즐겁다", "happy"), ("슬프다", "마음이 아프다", "sad"),
                    ("긴장되다", "떨리고 불안하다", "nervous"), ("속상하다", "마음이 상하다", "upset")]),
    19: dict(char="zm", scale=0.72, cy=385,
             gestures=["zm_point_l", "zm_base", "zm_thinking", "zm_clapping", "zm_cheering", "zm_waving"],
             title_ko="논리적 의견과 설득하기", title_en="Opinions & Persuasion",
             hook_ko="내 생각을 논리적으로 말해요",
             vocab=[("생각해요", "의견을 말함", "I think"), ("왜냐하면", "이유를 말함", "because"),
                    ("따라서", "결론을 말함", "therefore")]),
    20: dict(char="jieun", scale=0.6, cy=400,
             gestures=["jieun_pointing", "jieun_clapping", "jieun_thinking", "jieun_reading", "jieun_cheering", "jieun_waving"],
             title_ko="돌발 상황 대처와 문제 해결", title_en="Emergencies & Problem-Solving",
             hook_ko="문제가 생겼을 때 도움 요청",
             vocab=[("분실", "물건을 잃어버림", "loss"), ("고장", "기계가 망가짐", "breakdown"),
                    ("예약 변경", "예약을 바꿈", "reschedule"), ("긴급", "아주 급함", "urgent")]),
    21: dict(char="injun", scale=0.6, cy=400,
             gestures=["injun_pointing", "injun_holding_book", "injun_thinking", "injun_presenting", "injun_cheering", "injun_waving"],
             title_ko="인물 묘사와 외모·성격", title_en="Describing People",
             hook_ko="사람의 외모와 성격을 묘사해요",
             vocab=[("외모", "겉모습", "appearance"), ("성격", "마음의 특징", "personality"),
                    ("내향적", "조용하고 차분한", "introverted"), ("외향적", "활발하고 사교적인", "extroverted")]),
    22: dict(char="madam_jay", scale=0.62, cy=395,
             gestures=["madam_jay_pointing", "madam_jay_base_front", "madam_jay_thinking",
                       "madam_jay_presenting", "madam_jay_cheering", "madam_jay_waving"],
             title_ko="여행 경험과 미래 계획", title_en="Travel & Plans",
             hook_ko="경험을 말하고 계획을 세워요",
             vocab=[("가 본 적이 있어요", "경험을 말함", "have been to"), ("여행", "다른 곳을 다녀옴", "travel"),
                    ("계획", "앞으로의 일정", "plan")]),
    23: dict(char="dr_jay", scale=0.52, cy=400,
             gestures=["dr_jay_pointing", "dr_jay_base_front", "dr_jay_thinking",
                       "dr_jay_presenting", "dr_jay_cheering", "dr_jay_waving"],
             title_ko="모임 약속과 사회적 조율", title_en="Social Planning",
             hook_ko="여럿의 일정을 맞춰 약속해요",
             vocab=[("약속을 잡다", "만날 약속을 정함", "make plans"), ("시간 조율", "시간을 맞춤", "coordinate time"),
                    ("모임", "여럿이 모임", "gathering")]),
    24: dict(char="", scale=0.72, cy=385,
             gestures=["cheer", "waving", "standing", "presenting", "pointing_right", "thinking"],
             title_ko="종합 정리와 수료 축하", title_en="Wrap-up & Graduation",
             hook_ko="24주 여정의 마무리, 축하해요!",
             vocab=[("수료", "과정을 마침", "completion"), ("발표", "사람들 앞에서 말함", "presentation"),
                    ("최종 평가", "마지막 평가", "final review")]),
}

EP = lambda w: f"KO-W{w:02d}"
PREFIX = lambda w: f"hangeul_w{w}_stickman"


# ---------- glyph ----------
def render_word(text):
    f = ImageFont.truetype(FONT, 200)
    tmp = Image.new("RGBA", (len(text) * 230 + 80, 320), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    b = d.textbbox((0, 0), text, font=f)
    d.text((40 - b[0], 40 - b[1]), text, font=f, fill=(28, 28, 28, 255))
    bb = tmp.split()[3].getbbox()
    return tmp.crop((max(0, bb[0] - 16), max(0, bb[1] - 16), bb[2] + 16, bb[3] + 16))


def ensure_glyph(cur, has, word):
    fp = f"graphics/letters/word_{word}.png"
    out = os.path.join(LDIR, f"word_{word}.png")
    if not os.path.exists(out):
        render_word(word).save(out)
    cur.execute("DELETE FROM assets WHERE file_path=?", (fp,))
    if has:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt,created_at) VALUES (?,?,?,?,?,datetime('now'))",
                    (word, f"word_{word}", "word", fp, "make_intermediate"))
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (word, f"word_{word}", "word", fp, "make_intermediate"))


def ensure_audio(word):
    out = os.path.join(ADIR, f"{word}.mp3")
    if os.path.exists(out):
        return
    tmp = os.path.join(ROOT, "scratch", "_im_tmp.mp3")
    if save_tts_edge_tts(word, tmp, lang="ko"):
        subprocess.run([FF, "-y", "-i", tmp, "-af", "apad=whole_dur=0.6", out],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"    +audio {word}")


# ---------- scene/object layout ----------
def CH(char, pose, scale, cy):
    nm = pose if not char or char == "" else pose          # gesture name already full (e.g. zw_point_l / pointing_right / jieun_base)
    return (f"stickman_{nm}", 300, cy, scale, 5, 0, "gesture")


def word_obj(word, cx, cy, sc):
    return (f"word_{word}", cx, cy, sc, 3, 0, "fade_in")


def wscale(word, big=0.7):
    n = len(word.replace(" ", ""))
    return min(big, 1.7 / max(2, n))                       # 글자수 많으면 작게(넘침 방지)


def build_week(w, cur, has):
    cfg = WEEKS[w]
    char = cfg["char"]
    g = cfg["gestures"]
    vocab = cfg["vocab"]
    # gesture name normalize: for non-empty char already includes prefix in our lists
    scenes = []

    def gest(i):
        return [g[i % len(g)], g[(i + 1) % len(g)], g[(i + 2) % len(g)]]

    # 1) intro
    scenes.append(dict(cap_ko="안녕하세요!", cap_en="Hello!",
                       script_kr=f"안녕하세요! 오늘은 '{cfg['title_ko']}'를 배워요. 함께 시작해요!",
                       script_en=f"Hello! Today we'll learn '{cfg['title_en']}'. Let's begin!",
                       gestures=[g[0], g[len(g) - 1], g[1]],
                       objs=[("__title__", cfg["title_ko"])]))
    # 2) concept (all words overview)
    scenes.append(dict(cap_ko="오늘의 표현", cap_en="Today's words",
                       script_kr="오늘 배울 표현들을 먼저 살펴볼까요? 하나씩 따라 해 봐요.",
                       script_en="Let's look at today's words first, then repeat them one by one.",
                       gestures=gest(1), objs=[("__overview__", None)]))
    # 3..) one scene per vocab
    for i, (word, kg, eg) in enumerate(vocab):
        scenes.append(dict(
            cap_ko=word, cap_en=eg,
            script_kr=f"'{word}'는 {kg}라는 뜻이에요. 따라 해 보세요. '{word}'.",
            script_en=f"'{word}' means {eg}. Repeat after me: '{word}'.",
            gestures=gest(i + 2), objs=[("__word__", word)]))
    # recap
    scenes.append(dict(cap_ko="정리해요", cap_en="Recap",
                       script_kr="오늘 배운 표현을 다시 정리해 볼까요? 소리 내어 읽어 보세요.",
                       script_en="Let's review what we learned today. Read them aloud.",
                       gestures=gest(3), objs=[("__overview__", None)]))
    # outro
    scenes.append(dict(cap_ko="다음 시간에 만나요!", cap_en="See you next time!",
                       script_kr="잘 하셨어요! 오늘 표현을 일상에서 써 보세요. 다음 시간에 또 만나요!",
                       script_en="Well done! Try using today's words in daily life. See you next time!",
                       gestures=[g[len(g) - 1], g[0], g[1]], objs=[("__title__", cfg["title_ko"])]))

    # ---- write episode/scenes/objects ----
    runtime = 0
    cur.execute("DELETE FROM scenes WHERE episode=?", (EP(w),))
    cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP(w),))
    dur_map = {"__word__": 20, "__overview__": 20, "__title__": 17}
    nar_kr, nar_en = [], []
    for seq, sc in enumerate(scenes, 1):
        dur = 18 if seq == 1 else dur_map.get(sc["objs"][0][0], 20)
        runtime += dur
        nar_kr.append(sc["script_kr"]); nar_en.append(sc["script_en"])
        spec = {"pose": f"stickman_{sc['gestures'][0]}", "gesture_seq": sc["gestures"],
                "cap_ko": sc["cap_ko"], "cap_en": sc["cap_en"], "motion": "static"}
        cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,sfx,duration_sec) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (EP(w), seq, sc["script_kr"], sc["script_en"], json.dumps(spec, ensure_ascii=False), "", None, dur))
        # objects: character + content
        objs = [CH(char, sc["gestures"][0], cfg["scale"], cfg["cy"])]
        kind, val = sc["objs"][0]
        if kind == "__word__":
            objs.append(word_obj(val, 900, 360, wscale(val)))
        elif kind == "__overview__":
            allw = [v[0] for v in vocab]
            objs += grid_words(allw)
        elif kind == "__title__":
            objs.append(word_obj(val, 900, 360, wscale(val, big=0.62)))
        for (name, cx, cy, scale, z, isp, mo) in objs:
            aid = resolve(cur, name)
            cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,is_point,motion_type) "
                        "VALUES (?,?,?,?,?,?,?,?,?)", (EP(w), seq, aid, cx, cy, scale, z, isp, mo))

    cur.execute("DELETE FROM episodes WHERE code=?", (EP(w),))
    style = {"look": f"character={char or 'stickman'}; left char + right vocab; no idle shake",
             "narration": "edge-tts SunHi 1.1x; DB clips boosted; bilingual KR/EN", "canvas": [1280, 720]}
    cur.execute("INSERT INTO episodes (code,category,title_kr,title_en,hook_kr,logline_kr,status,runtime_sec,"
                "narration_kr,narration_en,style_profile,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,datetime('now'))",
                (EP(w), "KO", cfg["title_ko"], cfg["title_en"], cfg["hook_ko"],
                 f"중급 {w-8}주차. {cfg['title_ko']} — {(char or 'stickman')} 진행, 이중언어.",
                 "scripting", runtime, "\n".join(nar_kr), "\n".join(nar_en), json.dumps(style, ensure_ascii=False)))
    cur.execute("DELETE FROM video_projects WHERE name=?", (PREFIX(w),))
    cur.execute("INSERT INTO video_projects (name,title_kr,description,local_dir,n_scenes,runtime_sec,status,notes,created_at,updated_at) "
                "VALUES (?,?,?,?,?,?,?,?,datetime('now'),datetime('now'))",
                (PREFIX(w), cfg["title_ko"], f"중급 {w-8}주차 {cfg['title_ko']} ({char or 'stickman'})",
                 LOCAL_DIR, len(scenes), runtime, "scripting", f"episode={EP(w)}; character={char or 'stickman'}"))
    print(f"  {EP(w)} ({char or 'stickman'}): {len(scenes)} scenes, ~{runtime}s, vocab={len(vocab)}")


def word_sentence_ko(word, gloss):
    return f"'{word}'라고 말해요. 따라 해 보세요."


def grid_words(words):
    """오버뷰: 단어들을 오른쪽 2열 그리드로."""
    out = []
    n = len(words)
    cols = 2 if n > 3 else 1
    x0, dx = (760, 320) if cols == 2 else (900, 0)
    y0 = 250
    dy = 110 if n > 4 else 130
    for i, wd in enumerate(words):
        r, c = divmod(i, cols)
        out.append(word_obj(wd, x0 + c * dx, y0 + r * dy, min(0.42, wscale(wd, big=0.42))))
    return out


# ---------- asset resolve ----------
SEARCH = ["assets/graphics", "assets/graphics/poses", "assets/graphics/letters", "assets/graphics/objects"]


def find_file(name):
    for d in SEARCH:
        p = os.path.join(ROOT, d, f"{name}.png")
        if os.path.exists(p):
            return os.path.relpath(p, ROOT).replace("\\", "/")
    return None


def resolve(cur, name):
    r = cur.execute("SELECT id FROM assets WHERE name_en=?", (name,)).fetchone()
    if r:
        return r[0]
    r = cur.execute("SELECT id FROM assets WHERE file_path LIKE ?", (f"%{name}.png",)).fetchone()
    if r:
        return r[0]
    fp = find_file(name)
    if not fp:
        raise FileNotFoundError(f"asset not found: {name}")
    typ = "character" if name.startswith("stickman_") else ("word" if name.startswith("word_") else "object")
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                (name, name, typ, fp, "auto make_intermediate"))
    return cur.lastrowid


def main():
    weeks = [int(a) for a in sys.argv[1:]] or list(WEEKS.keys())
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has = "created_at" in {r[1] for r in cur.execute("pragma table_info(assets)")}
    # 1) glyphs + audio for all vocab + title words
    allwords = set()
    for w in weeks:
        for (wd, _, _) in WEEKS[w]["vocab"]:
            allwords.add(wd)
        allwords.add(WEEKS[w]["title_ko"])
    print(f"glyphs/audio for {len(allwords)} words…")
    for wd in sorted(allwords):
        ensure_glyph(cur, has, wd)
        if " " not in wd and len(wd) <= 6:    # 어휘 클립(짧은 단어/구). 제목은 글리프만.
            pass
    con.commit()
    for w in weeks:
        for (wd, _, _) in WEEKS[w]["vocab"]:
            ensure_audio(wd)
    # 2) build each week
    for w in weeks:
        build_week(w, cur, has)
    con.commit()
    con.close()
    print("DONE")


if __name__ == "__main__":
    main()
