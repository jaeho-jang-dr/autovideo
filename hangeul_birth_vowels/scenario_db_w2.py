#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scenario_db_w2.py — 훈민정음 앱 초급 2주차 "기초 자음과 모아쓰기" 스틱맨 영상 시나리오 → content.db.
캐릭터는 **컬러 연필**을 들고 가르친다. ~8분, 26씬. 기초자음 10자 + 발음기관 상형 + 모아쓰기.
예시 단어는 Gemini가 생성(scratch/gemini_words.json) → 나·누나·머리·바나나·아버지·오이·호수·지도.
재실행: python hangeul_birth_vowels/scenario_db_w2.py
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
EP = "KO-W02"
PROJECT = "hangeul_w2_stickman"
LOCAL_DIR = os.path.join(ROOT, "hangeul_birth_vowels")

STYLE = {
    "look": "stickman line-art on cream→pastel radial bg, character holds a COLORED PENCIL",
    "method": "flat-layered PIL/MoviePy compositing", "ref": "Week-1 same method",
    "narration": "edge-tts SunHi female, 1.1x; jamo spliced with DB pronunciation; bilingual KR/EN",
    "font": "C:/Windows/Fonts/malgun.ttf", "canvas": [1280, 720],
}

# seq, dur, ko, en, cap_ko, cap_en, pose, objects, motion
SCENES = [
    dict(seq=1, dur=15, pose="pencil_wave", motion="static",
         ko="안녕하세요! 지난 시간엔 모음을 배웠죠. 오늘은 한글의 또 다른 주인공, 자음을 만나봅니다. 자음은 과연 어떤 모양을 본떠 만들었을까요?",
         en="Hello! Last time we learned the vowels. Today we meet the other hero of Hangeul: the consonants. What shapes were they modeled on?",
         cap_ko="기초 자음과 모아쓰기", cap_en="Basic Consonants & Syllable Blocks",
         objects=["floating_consonants"]),
    dict(seq=2, dur=16, pose="pencil_point", motion="static",
         ko="놀랍게도, 한글 자음은 소리를 내는 우리 몸, 바로 입과 혀와 목구멍의 모양을 본떠 만들었습니다. 이것을 '상형의 원리'라고 해요.",
         en="Amazingly, Hangeul consonants were modeled on the very organs that make sound: the mouth, the tongue, and the throat. This is the principle of shape.",
         cap_ko="발음 기관을 본뜨다", cap_en="Modeled on speech organs",
         objects=["organ_head_profile"]),
    dict(seq=3, dur=15, pose="mouth_demo", motion="static",
         ko="먼저 'ㄱ'. 혀뿌리가 목구멍을 막는 모양이에요. 소리를 내보면, '그'. 어금니 근처에서 나는 소리랍니다.",
         en="First, ㄱ. It shows the root of the tongue blocking the throat. Say it: 'g'. It sounds near the back teeth.",
         cap_ko="ㄱ — 혀뿌리가 목을 막는 모양", cap_en="ㄱ — tongue root blocks the throat",
         objects=["organ_g", "letter_ㄱ_big"]),
    dict(seq=4, dur=14, pose="mouth_demo", motion="static",
         ko="'ㄴ'은 혀끝이 윗잇몸에 닿는 모양입니다. '느'. 혀가 입천장 앞쪽에 살짝 붙죠.",
         en="ㄴ shows the tongue tip touching the upper gum. 'n'. The tongue gently meets the front roof of the mouth.",
         cap_ko="ㄴ — 혀끝이 잇몸에 닿는 모양", cap_en="ㄴ — tongue tip touches the gum",
         objects=["organ_n", "letter_ㄴ_big"]),
    dict(seq=5, dur=13, pose="mouth_demo", motion="static",
         ko="'ㅁ'은 꼭 다문 입의 모양이에요. '므'. 두 입술이 만나 닫히는 소리죠.",
         en="ㅁ is the shape of closed lips. 'm'. The two lips meet and close.",
         cap_ko="ㅁ — 다문 입 모양", cap_en="ㅁ — shape of closed lips",
         objects=["organ_m", "letter_ㅁ_big"]),
    dict(seq=6, dur=13, pose="mouth_demo", motion="static",
         ko="'ㅅ'은 뾰족한 이의 모양입니다. '스'. 이 사이로 바람이 새어 나오는 소리예요.",
         en="ㅅ is the shape of a tooth. 's'. Air slips out between the teeth.",
         cap_ko="ㅅ — 이의 모양", cap_en="ㅅ — shape of a tooth",
         objects=["organ_s", "letter_ㅅ_big"]),
    dict(seq=7, dur=14, pose="mouth_demo", motion="static",
         ko="'ㅇ'은 둥근 목구멍의 모양이에요. 받침으로 쓰면 콧소리 '응'이 됩니다. 첫소리 자리에선 소리가 없는 자리지킴이랍니다.",
         en="ㅇ is the round shape of the throat. As a final sound it becomes the nasal 'ng'. At the start, it is a silent placeholder.",
         cap_ko="ㅇ — 목구멍 모양", cap_en="ㅇ — shape of the throat",
         objects=["organ_o", "letter_ㅇ_big"]),
    dict(seq=8, dur=13, pose="pencil_present", motion="static",
         ko="이렇게 다섯 개의 기본 자음, 'ㄱ, ㄴ, ㅁ, ㅅ, ㅇ'이 우리 몸을 본떠 태어났습니다.",
         en="So the five basic consonants — ㄱ, ㄴ, ㅁ, ㅅ, ㅇ — were born from the shapes of our own body.",
         cap_ko="기본 자음 5: ㄱ ㄴ ㅁ ㅅ ㅇ", cap_en="5 basic consonants",
         objects=["row_basic5"]),
    dict(seq=9, dur=15, pose="pencil_point", motion="static",
         ko="그럼 나머지 자음은요? 아주 똑똑한 방법을 썼어요. 소리가 더 세지면, 기본 글자에 획을 하나씩 더합니다. 이것을 '가획의 원리'라고 해요.",
         en="What about the rest? A very clever method: when the sound gets stronger, you add one stroke to the basic letter. This is the stroke-adding principle.",
         cap_ko="가획의 원리 — 획을 더하다", cap_en="Adding strokes for stronger sounds",
         objects=["plus_stroke"]),
    dict(seq=10, dur=15, pose="pencil_write", motion="static",
         ko="'ㄴ'에 획을 더하면 'ㄷ', 'ㅁ'에 획을 더하면 'ㅂ'. 소리가 한층 또렷하고 단단해지죠.",
         en="Add a stroke to ㄴ and you get ㄷ; add to ㅁ and you get ㅂ. The sound becomes clearer and firmer.",
         cap_ko="ㄴ→ㄷ,  ㅁ→ㅂ", cap_en="ㄴ→ㄷ,  ㅁ→ㅂ",
         objects=["evo_n_d", "evo_m_b"]),
    dict(seq=11, dur=15, pose="pencil_write", motion="static",
         ko="'ㅅ'에 획을 더하면 'ㅈ', 'ㅇ'에 획을 더하면 'ㅎ'. 그리고 혀를 굴리는 'ㄹ'까지. 규칙이 보이나요?",
         en="Add a stroke to ㅅ for ㅈ, and to ㅇ for ㅎ. And the rolling ㄹ too. Do you see the pattern?",
         cap_ko="ㅅ→ㅈ,  ㅇ→ㅎ,  ㄹ", cap_en="ㅅ→ㅈ,  ㅇ→ㅎ,  ㄹ",
         objects=["evo_s_j", "evo_o_h", "letter_ㄹ_big"]),
    dict(seq=12, dur=15, pose="pencil_present", motion="static",
         ko="오늘 배울 기초 자음 열 개입니다. ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅅ, ㅇ, ㅈ, ㅎ. 함께 소리 내 볼까요?",
         en="Here are the ten basic consonants for today: ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅅ ㅇ ㅈ ㅎ. Let's say them together.",
         cap_ko="기초 자음 10자", cap_en="10 basic consonants",
         objects=["row_basic10"]),
    dict(seq=13, dur=15, pose="pencil_point", motion="static",
         ko="이제 가장 신기한 부분! 한글은 자음과 모음을 따로 쓰지 않고, 하나로 모아서 한 글자로 씁니다. 이것이 바로 '모아쓰기'예요.",
         en="Now the most magical part! Hangeul does not write consonant and vowel separately — it gathers them into one block. This is 'syllable assembly'.",
         cap_ko="모아쓰기 — 한 글자로 모으기", cap_en="Syllable assembly",
         objects=["block_intro"]),
    dict(seq=14, dur=15, pose="pencil_write", motion="static",
         ko="자음은 첫소리, 모음은 가운뎃소리. 첫소리 'ㄱ'과 가운뎃소리 'ㅏ'를 모으면? 바로 '가'가 됩니다.",
         en="The consonant is the first sound, the vowel the middle sound. Put first 'ㄱ' and middle 'ㅏ' together and you get '가'.",
         cap_ko="ㄱ + ㅏ → 가", cap_en="ㄱ + ㅏ → 가",
         objects=["assemble_ga"]),
    dict(seq=15, dur=15, pose="pencil_point", motion="static",
         ko="규칙은 간단해요. 세로로 선 모음 'ㅏ, ㅓ, ㅣ'는 자음의 오른쪽에 붙습니다. 나, 머, 디 처럼요.",
         en="The rule is simple. Upright vowels like ㅏ, ㅓ, ㅣ go to the right of the consonant — like 나, 머, 디.",
         cap_ko="세로 모음 → 오른쪽", cap_en="Upright vowels → right side",
         objects=["assemble_na", "assemble_meo"]),
    dict(seq=16, dur=15, pose="pencil_point", motion="static",
         ko="반대로 가로로 누운 모음 'ㅗ, ㅜ, ㅡ'는 자음의 아래에 붙습니다. 고, 누, 드 처럼요.",
         en="In contrast, flat vowels like ㅗ, ㅜ, ㅡ go below the consonant — like 고, 누, 드.",
         cap_ko="가로 모음 → 아래쪽", cap_en="Flat vowels → bottom",
         objects=["assemble_go", "assemble_nu"]),
    dict(seq=17, dur=13, pose="pencil_present", motion="static",
         ko="오늘은 받침이 없는 글자만 배워요. 받침이 없으면 소리가 시원하게 열려서, '열린 음절'이라고 부릅니다.",
         en="Today we use only letters without a final consonant. With no final, the sound stays open — an 'open syllable'.",
         cap_ko="받침 없는 열린 음절", cap_en="Open syllables (no final)",
         objects=["block_open"]),
    dict(seq=18, dur=15, pose="pencil_write", motion="static",
         ko="이제 단어를 만들어 볼까요? '고'와 '기'를 나란히 쓰면 '고기'. 글자 두 개가 모여 뜻이 생겼어요!",
         en="Let's build a word. Write '고' and '기' side by side: '고기' — meat. Two blocks join to make meaning!",
         cap_ko="고 + 기 → 고기", cap_en="고 + 기 → 고기 (meat)",
         objects=["word_gogi"]),
    dict(seq=19, dur=14, pose="pencil_present", motion="static",
         ko="가족을 불러볼까요? 'ㄴ'과 'ㅏ'로 '나', 그리고 '누나'. '오빠'와 '누나'는 가족을 부르는 정다운 말이에요.",
         en="Let's name family. 'ㄴ' and 'ㅏ' make '나', and '누나'. '오빠' and '누나' are warm words for family.",
         cap_ko="나 · 누나", cap_en="나 (me) · 누나 (sister)",
         objects=["word_na", "word_nuna"]),
    dict(seq=20, dur=14, pose="pencil_present", motion="static",
         ko="'ㅁ, ㅓ, ㄹ, ㅣ'로 '머리'. 'ㅂ, ㅏ, ㄴ, ㅏ, ㄴ, ㅏ'로 '바나나'. 자음과 모음이 척척 모이죠?",
         en="머리 means head. 바나나 means banana. The consonants and vowels snap together neatly!",
         cap_ko="머리 · 바나나", cap_en="머리 (head) · 바나나 (banana)",
         objects=["word_meori", "word_banana"]),
    dict(seq=21, dur=14, pose="pencil_present", motion="static",
         ko="'아버지'와 '어머니'. 받침 없는 글자만으로도 이렇게 따뜻한 말을 쓸 수 있어요.",
         en="아버지 (father) and 어머니 (mother). Even with only open syllables, we can write such warm words.",
         cap_ko="아버지 · 어머니", cap_en="아버지 (father) · 어머니 (mother)",
         objects=["word_abeoji", "word_eomeoni"]),
    dict(seq=22, dur=14, pose="pencil_present", motion="static",
         ko="'오이', '호수', '지도'. 모두 받침이 없는 쉬운 단어들이에요. 소리 내어 따라 읽어 보세요.",
         en="오이 (cucumber), 호수 (lake), 지도 (map) — easy open-syllable words. Read them aloud after me.",
         cap_ko="오이 · 호수 · 지도", cap_en="오이 · 호수 · 지도",
         objects=["word_oi", "word_hosu", "word_jido"]),
    dict(seq=23, dur=14, pose="pencil_point", motion="static",
         ko="자, 이제 플래시카드 놀이! 화면에 글자가 나오면, 자음과 모음을 떠올리며 또박또박 읽어 보세요.",
         en="Now a flashcard game! When a word appears, recall the consonant and vowel, and read it clearly.",
         cap_ko="플래시카드로 읽기", cap_en="Read with flashcards",
         objects=["flashcards"]),
    dict(seq=24, dur=13, pose="pencil_write", motion="static",
         ko="배운 자음을 연필로 한 획 한 획 직접 써 보는 것도 좋아요. 손으로 쓰면 모양과 소리가 더 잘 기억된답니다.",
         en="Try writing each consonant stroke by stroke with your pencil. Writing by hand helps you remember the shape and sound.",
         cap_ko="연필로 직접 써 보기", cap_en="Write it by hand",
         objects=["write_practice"]),
    dict(seq=25, dur=13, pose="pencil_present", motion="static",
         ko="오늘 우리는 기초 자음 열 개와, 자음과 모음을 모으는 모아쓰기를 배웠어요. 이제 여러분도 쉬운 단어를 읽고 쓸 수 있어요!",
         en="Today we learned ten basic consonants and how to assemble blocks. Now you can read and write simple words!",
         cap_ko="자음 10 + 모아쓰기 완성", cap_en="10 consonants + assembly",
         objects=["row_basic10", "block_intro"]),
    dict(seq=26, dur=13, pose="cheer", motion="static",
         ko="매일 조금씩 연습하면 한글이 쑥쑥 늘어요. 구독과 좋아요로 다음 한글 여행도 함께해요. 다음에 또 만나요!",
         en="Practice a little every day and your Hangeul will grow fast. Subscribe and like to join the next journey. See you next time!",
         cap_ko="구독 · 좋아요", cap_en="Subscribe & Like",
         objects=["obj_bell", "obj_sparkle"]),
]


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    runtime = sum(s["dur"] for s in SCENES)
    nar_kr = "\n".join(s["ko"] for s in SCENES)
    nar_en = "\n".join(s["en"] for s in SCENES)

    cur.execute("DELETE FROM episodes WHERE code=?", (EP,))
    cur.execute(
        "INSERT INTO episodes (code, category, title_kr, title_en, hook_kr, logline_kr, status, "
        "runtime_sec, narration_kr, narration_en, style_profile, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?, datetime('now'))",
        (EP, "KO", "기초 자음과 모아쓰기", "Basic Consonants & Syllable Blocks",
         "한글 자음은 우리 몸을 본떠 만들어졌다?",
         "컬러 연필 스틱맨과 함께 발음기관 상형·기초 자음 10자·모아쓰기를 배운다 (초급 2주차).",
         "scripting", runtime, nar_kr, nar_en, json.dumps(STYLE, ensure_ascii=False)))

    cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
    for s in SCENES:
        spec = {"pose": s["pose"], "objects": s["objects"],
                "cap_ko": s["cap_ko"], "cap_en": s["cap_en"], "motion": s["motion"]}
        cur.execute(
            "INSERT INTO scenes (episode, seq, script_kr, script_en, image_prompt, veo_prompt, sfx, duration_sec) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (EP, s["seq"], s["ko"], s["en"], json.dumps(spec, ensure_ascii=False), "", None, s["dur"]))

    cur.execute("DELETE FROM video_projects WHERE name=?", (PROJECT,))
    cur.execute(
        "INSERT INTO video_projects (name, title_kr, description, local_dir, n_scenes, runtime_sec, status, notes, created_at, updated_at) "
        "VALUES (?,?,?,?,?,?,?,?, datetime('now'), datetime('now'))",
        (PROJECT, "기초 자음과 모아쓰기 (스틱맨 · 초급 2주차)",
         "훈민정음 앱 초급 2주차. 컬러 연필 스틱맨, 발음기관 상형 + 자음 10자 + 모아쓰기, 이중언어.",
         LOCAL_DIR, len(SCENES), runtime, "scripting",
         f"episode={EP}; character=colored-pencil stickman; words from gemini_words.json"))

    con.commit()
    print(f"episode {EP}: {len(SCENES)} scenes, runtime ~{runtime}s ({runtime/60:.1f}min)")
    con.close()


if __name__ == "__main__":
    main()
