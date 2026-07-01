#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scenario_db.py — 훈민정음 앱 초급 1주차 "한글의 탄생과 단모음" 스틱맨 영상 시나리오를
                 content.db 에 기록한다 (DB 중심 워크플로우).

생성/갱신 대상 (모두 멱등):
 - episodes        : KO-W01 (제목/내레이션/런타임/스타일)
 - scenes          : seq 1..15 (script_kr/en, image_prompt=비주얼 스펙 JSON, veo_prompt=모션, duration, sfx)
 - video_projects  : hangeul_w1_stickman (로컬 디렉터리/씬수/상태)

scene_objects(에셋 배치)와 객체 에셋 등록은 '스크립트 확정 후' 다음 단계에서 채운다.
재실행: python hangeul_birth_vowels/scenario_db.py
"""
import os
import sys
import json
import sqlite3

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "channel", "content.db")
EP = "KO-W01"
PROJECT = "hangeul_w1_stickman"
LOCAL_DIR = os.path.join(ROOT, "hangeul_birth_vowels")

STYLE = {
    "look": "stickman line-art on cream #F5F5F0",
    "method": "flat-layered PIL/MoviePy compositing",
    "ref": "youtu.be/Nj97sKnitKM (style ref)",
    "narration": "gTTS ko female, 1.1x; bilingual KR/EN toggle",
    "font": "C:/Windows/Fonts/malgun.ttf",
    "canvas": [1280, 720],
}

# 각 씬: seq, dur, ko, en, cap_ko, cap_en, pose, objects(힌트), motion(static|animate), sfx, veo(모션 프롬프트)
SCENES = [
    dict(seq=1, dur=12,
         ko="안녕하세요! 세계에서 가장 과학적인 문자, 한글. 오늘은 한글이 어떻게 태어났는지, 그리고 단모음 여덟 개의 비밀을 함께 풀어봅니다.",
         en="Hello! Hangeul is one of the most scientific writing systems in the world. Today, let's discover how it was born and unlock the secret of its eight simple vowels.",
         cap_ko="한글의 탄생과 단모음", cap_en="Birth of Hangeul & Simple Vowels",
         pose="greeting_wave", objects=["floating_vowels"], motion="static", sfx="chime"),
    dict(seq=2, dur=14,
         ko="아주 먼 옛날, 우리에겐 우리글이 없어서 어려운 한자를 빌려 썼습니다. 한자는 너무 복잡해서 글을 읽지 못하는 백성이 많았지요.",
         en="Long ago, Koreans had no script of their own, so they borrowed complex Chinese characters. Hanja was so hard that most common people could not read at all.",
         cap_ko="우리글이 없던 시절", cap_en="Before we had our own script",
         pose="reading", objects=["obj_book_chalk", "qmark"], motion="static", sfx=None),
    dict(seq=3, dur=15,
         ko="글을 몰라 억울한 일을 겪는 백성을 본 세종대왕은 마음 깊이 안타까워했습니다. '내 이를 가엾게 여겨, 새로 스물여덟 글자를 만드노라.'",
         en="Seeing his people suffer because they could not read, King Sejong was deeply moved. 'Out of compassion, I create twenty-eight new letters.'",
         cap_ko="세종대왕의 마음", cap_en="King Sejong's compassion",
         pose="sejong", objects=["obj_crown_chalk", "badge_28"], motion="static", sfx=None),
    dict(seq=4, dur=13,
         ko="마침내 1443년, 누구나 쉽게 배우는 글자 '훈민정음'이 태어났습니다. 슬기로운 사람은 하루아침에, 누구든 열흘이면 깨치는 글자였죠.",
         en="Finally, in 1443, Hunminjeongeum was born — a script anyone could learn. The wise learned it in a morning; anyone, within ten days.",
         cap_ko="1443년 훈민정음 창제", cap_en="1443: Hunminjeongeum is created",
         pose="presenting", objects=["obj_haerye_scroll", "sparkle"], motion="animate", sfx="whoosh",
         veo="the rolled scroll unfurls smoothly to reveal glowing Hangeul letters, soft sparkles, gentle camera push-in"),
    dict(seq=5, dur=16,
         ko="한글 모음은 우주의 세 요소, 하늘과 땅과 사람을 본떠 만들었습니다. 하늘은 둥근 점, 땅은 평평한 가로선, 사람은 곧게 선 세로선이지요.",
         en="Hangeul's vowels are modeled on three elements of the universe: heaven, earth, and human. Heaven is a round dot, earth a flat horizontal line, and human an upright vertical line.",
         cap_ko="천 · 지 · 인", cap_en="Heaven · Earth · Human",
         pose="pointing_up", objects=["sym_heaven_dot", "sym_earth_line", "sym_human_line"], motion="static", sfx="pop"),
    dict(seq=6, dur=16,
         ko="사람을 뜻하는 세로선에 하늘의 점이 오른쪽에 붙으면, 해가 뜨는 동쪽 — 밝은 소리 'ㅏ'! 왼쪽에 붙으면 해가 지는 서쪽 — 어두운 소리 'ㅓ'!",
         en="Add the heaven dot to the right of the human line and you get the bright sound 'ㅏ', the rising sun in the east. Put it on the left, and you get the dark sound 'ㅓ', the setting sun in the west.",
         cap_ko="ㅣ + 점 → ㅏ / ㅓ", cap_en="vertical + dot → ㅏ / ㅓ",
         pose="pointing_right", objects=["letter_ㅣ", "obj_sun", "letter_ㅏ", "letter_ㅓ"], motion="animate", sfx="whoosh",
         veo="a small sun arcs from the right (rising, bright) across to the left (setting), the dot snaps onto the vertical line forming ㅏ then ㅓ"),
    dict(seq=7, dur=14,
         ko="땅을 뜻하는 가로선 위에 점이 오르면 'ㅗ', 아래로 내려가면 'ㅜ'. 위로 솟으면 밝고, 아래로 가라앉으면 어둡습니다.",
         en="Place the dot above the earth line and you get 'ㅗ'; below it, 'ㅜ'. Rising above is bright; sinking below is dark.",
         cap_ko="ㅡ + 점 → ㅗ / ㅜ", cap_en="horizontal + dot → ㅗ / ㅜ",
         pose="pointing_down", objects=["letter_ㅡ", "sym_heaven_dot", "letter_ㅗ", "letter_ㅜ"], motion="static", sfx="pop"),
    dict(seq=8, dur=12,
         ko="그래서 밝은 모음은 밝은 모음끼리, 어두운 모음은 어두운 모음끼리 어울립니다. 이 아름다운 질서를 '모음조화'라고 불러요.",
         en="So bright vowels pair with bright, and dark vowels with dark. This beautiful order is called vowel harmony.",
         cap_ko="모음조화", cap_en="Vowel Harmony",
         pose="arms_open", objects=["group_bright", "group_dark"], motion="static", sfx="pop"),
    dict(seq=9, dur=14,
         ko="이제 소리를 내볼까요? 한국어 단모음은 여덟 개. 영어와 달리, 소리 내는 동안 입 모양이 절대 흔들리지 않는 것이 핵심입니다. 함께 따라 해 봅시다. ㅏ, ㅓ, ㅗ, ㅜ, ㅡ, ㅣ, ㅐ, ㅔ.",
         en="Now let's make some sounds. Korean has eight simple vowels. Unlike English, the secret is to keep your mouth shape perfectly still. Let's say them together. ㅏ, ㅓ, ㅗ, ㅜ, ㅡ, ㅣ, ㅐ, ㅔ.",
         cap_ko="단모음 8개: ㅏ ㅓ ㅗ ㅜ ㅡ ㅣ ㅐ ㅔ", cap_en="8 simple vowels",
         pose="mouth_demo", objects=["row_8_vowels"], motion="static", sfx="chime"),
    dict(seq=10, dur=14,
         ko="먼저 'ㅏ'와 'ㅓ'. 둘 다 턱을 아래로 크게 떨어뜨려 입을 세로로 열고, 입술은 평평하게 둡니다. 'ㅏ'는 더 활짝, 'ㅓ'는 살짝 좁혀서.",
         en="First, 'ㅏ' and 'ㅓ'. For both, drop your jaw to open wide and keep your lips flat. Open wider for 'ㅏ', a bit narrower for 'ㅓ'.",
         cap_ko="ㅏ / ㅓ — 입을 세로로, 입술은 평평", cap_en="ㅏ / ㅓ — open vertical, lips flat",
         pose="presenting", objects=["mouth_open_vertical", "letter_ㅏ", "letter_ㅓ"], motion="static", sfx=None),
    dict(seq=11, dur=14,
         ko="'ㅗ'와 'ㅜ'는 빨대를 문 것처럼 입술을 동그랗게 모아 앞으로 내밉니다. 'ㅗ'는 조금 크게, 'ㅜ'는 더 작고 뾰족하게.",
         en="For 'ㅗ' and 'ㅜ', round your lips like holding a straw and push them forward. 'ㅗ' is a little bigger, 'ㅜ' smaller and tighter.",
         cap_ko="ㅗ / ㅜ — 입술을 동그랗게", cap_en="ㅗ / ㅜ — round your lips",
         pose="mouth_demo", objects=["mouth_rounded", "letter_ㅗ", "letter_ㅜ"], motion="static", sfx=None),
    dict(seq=12, dur=14,
         ko="'ㅡ'는 억지 미소처럼 입술을 양옆으로 납작하게, 'ㅣ'는 그보다 더 활짝 옆으로 당겨 이가 살짝 보이게 합니다.",
         en="For 'ㅡ', stretch your lips flat sideways like a forced smile. For 'ㅣ', pull them even wider so your teeth almost show.",
         cap_ko="ㅡ / ㅣ — 입술을 옆으로 납작", cap_en="ㅡ / ㅣ — stretch lips sideways",
         pose="presenting", objects=["mouth_flat_wide", "letter_ㅡ", "letter_ㅣ"], motion="static", sfx=None),
    dict(seq=13, dur=12,
         ko="마지막으로 'ㅐ'와 'ㅔ'. 입을 적당히 벌리고 혀를 앞에 둔 채 소리 내면 됩니다. 오늘날 두 소리는 거의 같게 발음돼요.",
         en="Finally, 'ㅐ' and 'ㅔ'. Open your mouth moderately with the tongue forward. In modern Korean, the two sounds are almost the same.",
         cap_ko="ㅐ / ㅔ — 가운데로 살짝 벌려", cap_en="ㅐ / ㅔ — open mid, tongue forward",
         pose="mouth_demo", objects=["mouth_mid_open", "letter_ㅐ", "letter_ㅔ"], motion="static", sfx=None),
    dict(seq=14, dur=12,
         ko="거울을 보며 확인해요! 'ㅗ, ㅜ'를 말할 때만 입술이 동그래지고, 'ㅓ, ㅡ'에선 절대 동그래지면 안 됩니다.",
         en="Check in a mirror! Your lips should round only for 'ㅗ' and 'ㅜ' — never for 'ㅓ' or 'ㅡ'.",
         cap_ko="거울로 점검", cap_en="Check in the mirror",
         pose="holding_mirror", objects=["obj_mirror"], motion="static", sfx="pop"),
    dict(seq=15, dur=12,
         ko="오늘 배운 단모음, 거울 앞에서 매일 연습해 보세요. 구독과 좋아요를 누르면 더 재미있는 한글 여행이 이어집니다. 다음에 또 만나요!",
         en="Practice today's vowels in front of a mirror every day. Subscribe and like for more fun Hangeul adventures. See you next time!",
         cap_ko="구독 · 좋아요", cap_en="Subscribe & Like",
         pose="cheer", objects=["obj_bell", "sparkle"], motion="static", sfx="chime"),
]


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    runtime = sum(s["dur"] for s in SCENES)
    nar_kr = "\n".join(s["ko"] for s in SCENES)
    nar_en = "\n".join(s["en"] for s in SCENES)

    # episodes (upsert by code)
    cur.execute("DELETE FROM episodes WHERE code=?", (EP,))
    cur.execute(
        "INSERT INTO episodes (code, category, title_kr, title_en, hook_kr, logline_kr, status, "
        "runtime_sec, narration_kr, narration_en, style_profile, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?, datetime('now'))",
        (EP, "KO", "한글의 탄생과 단모음", "Birth of Hangeul & Simple Vowels",
         "세계에서 가장 과학적인 문자는 어떻게 태어났을까?",
         "스틱맨과 함께 천지인 창제원리와 단모음 8개를 배운다 (초급 1주차).",
         "scripting", runtime, nar_kr, nar_en, json.dumps(STYLE, ensure_ascii=False)),
    )

    # scenes (replace all for this episode)
    cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
    for s in SCENES:
        spec = {
            "pose": s["pose"], "objects": s["objects"],
            "cap_ko": s["cap_ko"], "cap_en": s["cap_en"], "motion": s["motion"],
        }
        cur.execute(
            "INSERT INTO scenes (episode, seq, script_kr, script_en, image_prompt, veo_prompt, sfx, duration_sec) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (EP, s["seq"], s["ko"], s["en"], json.dumps(spec, ensure_ascii=False),
             s.get("veo", ""), s["sfx"], s["dur"]),
        )

    # video_projects (upsert by name)
    cur.execute("DELETE FROM video_projects WHERE name=?", (PROJECT,))
    cur.execute(
        "INSERT INTO video_projects (name, title_kr, description, local_dir, n_scenes, runtime_sec, status, notes, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?, datetime('now'), datetime('now'))",
        (PROJECT, "한글의 탄생과 단모음 (스틱맨 · 초급 1주차)",
         "훈민정음 앱 초급 1주차 레슨 영상. 스틱맨 플랫 레이어드, 단모음 8개, 이중언어 KR/EN.",
         LOCAL_DIR, len(SCENES), runtime, "scripting",
         f"episode={EP}; ref=youtu.be/Nj97sKnitKM; method=stickman_factory + flat-layered"),
    )

    con.commit()
    print(f"episode {EP}: {len(SCENES)} scenes, runtime ~{runtime}s ({runtime/60:.1f}min)")
    print(f"project {PROJECT} registered (local_dir={LOCAL_DIR})")
    con.close()


if __name__ == "__main__":
    main()
