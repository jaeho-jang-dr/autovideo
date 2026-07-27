# -*- coding: utf-8 -*-
"""W21 업로드 패키지 생성 — 제목/설명(5개국)·태그·고정댓글·매니페스트(ko/en)."""
import os, json
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w21pkg"
os.makedirs(PKG, exist_ok=True)
def w(name, text): open(os.path.join(PKG, name), "w", encoding="utf-8").write(text.strip() + "\n")

TITLES = {
 "ko": "인물 묘사 한국어 - 외모·성격 표현 & '-고'로 잇기 (키가 크고 친절해요) | 한글 배우기 W21 (성수동)",
 "en": "Describing People in Korean: Looks, Personality & Linking with '-고' | Learn Korean W21 (Seongsu-dong)",
 "ja": "韓国語で人物描写 - 外見・性格の表現と「-고」で繋ぐ (키가 크고 친절해요) | 韓国語を学ぶ W21 (聖水洞)",
 "zh": "用韩语描述人物 - 外貌·性格表达 & 用'-고'连接 (키가 크고 친절해요) | 学韩语 W21 (圣水洞)",
 "es": "Describir personas en coreano: apariencia, personalidad y unir con '-고' | Aprende coreano W21 (Seongsu-dong)",
}

CHAP = """⏱️ 챕터 / Chapters
0:00 성수동 도착 · 오늘의 인물 묘사 수업
0:49 외모 표현 (키 · 머리 · 예쁘다 · 잘생기다 · 멋있다 · 날씬 · 안경)
2:33 성격 표현 (친절 · 착하다 · 재미있다 · 조용 · 활발 · 똑똑)
3:57 '-고'로 잇기 (키가 크고 친절해요)
6:01 친구 소개 · 복습 · 마무리"""

AI = ("🤖 제작 안내 / AI note\n"
      "배경 이미지는 Google Gemini(Nano Banana)로 생성했고, 캐릭터 애니메이션은 자체 엔진, "
      "나레이션은 Microsoft Azure TTS(선희·Emma)로 만들었습니다. "
      "Backgrounds by Google Gemini, character animation by our own engine, narration by Azure TTS.")

KEYVOCAB = ("외모 · 성격 · 형용사 · 키가 크다 · 키가 작다 · 머리가 길다 · 머리가 짧다 · 예쁘다 · 잘생기다 · "
            "멋있다 · 날씬하다 · 안경을 쓰다 · 친절하다 · 착하다 · 재미있다 · 조용하다 · 활발하다 · 똑똑하다 · "
            "-고 · 키가 크고 친절해요 · 머리가 길고 예뻐요 · 재미있고 활발해요 · 안녕히 가세요")

DESC = {
 "ko": f"""마담제이와 함께 붉은 벽돌과 예쁜 카페가 가득한 서울 '성수동'을 걸으며, 사람의 '외모'와 '성격'을 한국어로 묘사하는 법을 배웁니다.

키가 크고 작음, 머리가 길고 짧음, '예쁘다'·'잘생기다'·'멋있다'·'날씬하다'로 외모를 말하고, '친절하다'·'착하다'·'재미있다'·'조용하다'·'활발하다'·'똑똑하다'로 성격을 표현해요. 그리고 오늘의 핵심 — 연결어미 '-고'로 두 가지를 한 문장에 잇는 법을 규칙부터 차근차근 배웁니다. '크다'는 '크고', '작다'는 '작고'처럼 기본형에서 '다'를 떼고 '고'를 붙이면 '키가 크고 친절해요'가 완성돼요. 마지막엔 배운 표현으로 친구를 소개하는 연습까지!

초보자와 중급자 모두 환영합니다. 한글만으로 공부하는 분들을 위해 자막에 로마자 발음기호도 넣었어요.

📚 오늘 배우는 핵심 표현
{KEYVOCAB}

{CHAP}

{AI}

🌐 drjayed.com""",

 "en": f"""Walk through Seoul's '성수동' (Seongsu-dong) with Madam J and learn how to describe a person's looks (외모) and personality (성격) in Korean.

Talk about height (키가 크다/작다), hair (머리가 길다/짧다), and use '예쁘다' (pretty), '잘생기다' (handsome), '멋있다' (cool), '날씬하다' (slim) for looks — and '친절하다' (kind), '착하다' (good-hearted), '재미있다' (fun), '조용하다' (quiet), '활발하다' (lively), '똑똑하다' (smart) for personality. Then today's key point: the connective '-고' that joins two descriptions in one sentence. Just drop '다' from the base form and add '고' — '크다' becomes '크고' — to make '키가 크고 친절해요' (tall and kind). Finish by introducing a friend with everything you learned!

Great for beginners and intermediate learners. Romanization is included in the subtitles for those studying with Korean only.

📚 Key expressions
{KEYVOCAB}

{CHAP}

{AI}

🌐 drjayed.com""",

 "ja": f"""マダムJと一緒に、赤レンガとおしゃれなカフェが並ぶソウルの「성수동(聖水洞)」を歩きながら、人の「외모(外見)」と「성격(性格)」を韓国語で描写する方法を学びます。

背の高さ(키가 크다/작다)、髪の長さ(머리가 길다/짧다)、「예쁘다(きれい)」「잘생기다(かっこいい)」「멋있다(素敵)」「날씬하다(スリム)」で外見を、「친절하다(親切)」「착하다(優しい)」「재미있다(面白い)」「조용하다(静か)」「활발하다(活発)」「똑똑하다(賢い)」で性格を表現。そして今日の核心 — 二つを一文でつなぐ連結語尾「-고」。基本形から「다」を取って「고」を付けるだけで「키가 크고 친절해요(背が高くて親切です)」が完成します。

初級・中級者歓迎。ハングルだけで学ぶ方のために字幕にローマ字発音も入れました。

📚 主な表現
{KEYVOCAB}

{CHAP}

{AI}

🌐 drjayed.com""",

 "zh": f"""和Madam J一起漫步首尔充满红砖与美丽咖啡馆的「성수동(圣水洞)」，学习用韩语描述一个人的「외모(外貌)」和「성격(性格)」。

用身高(키가 크다/작다)、发型(머리가 길다/짧다)，以及「예쁘다(漂亮)」「잘생기다(帅)」「멋있다(帅气)」「날씬하다(苗条)」描述外貌；用「친절하다(亲切)」「착하다(善良)」「재미있다(有趣)」「조용하다(安静)」「활발하다(活泼)」「똑똑하다(聪明)」描述性格。今天的重点 — 用连接语尾「-고」把两个描述连成一句。只需从原形去掉「다」加上「고」，「크다」变「크고」，就能说出「키가 크고 친절해요(又高又亲切)」。

欢迎初级和中级学习者。为只用韩文学习的朋友，字幕中加入了罗马音。

📚 核心表达
{KEYVOCAB}

{CHAP}

{AI}

🌐 drjayed.com""",

 "es": f"""Camina por el barrio de '성수동' (Seongsu-dong) en Seúl con Madam J y aprende a describir la apariencia (외모) y la personalidad (성격) de una persona en coreano.

Habla de la altura (키가 크다/작다), el cabello (머리가 길다/짧다) y usa '예쁘다' (bonita), '잘생기다' (guapo), '멋있다' (con estilo), '날씬하다' (delgado) para la apariencia — y '친절하다' (amable), '착하다' (bondadoso), '재미있다' (divertido), '조용하다' (callado), '활발하다' (activo), '똑똑하다' (inteligente) para la personalidad. Y lo esencial de hoy: el conector '-고' que une dos descripciones en una frase. Solo quita '다' de la forma base y añade '고' — '크다' se convierte en '크고' — para decir '키가 크고 친절해요' (alto y amable).

Ideal para principiantes e intermedios. Los subtítulos incluyen romanización para quienes estudian solo con hangul.

📚 Expresiones clave
{KEYVOCAB}

{CHAP}

{AI}

🌐 drjayed.com""",
}

TAGS = ("learn korean, korean for beginners, korean lesson, speak korean, korean language, study korean, "
        "describing people in korean, korean adjectives, korean personality words, korean appearance, "
        "korean grammar, korean connective go, korean phrases, korean for travel, "
        "한국어 배우기, 한국어 회화, 왕초보 한국어, 인물 묘사, 외모 성격, 형용사, 연결어미 고, 성수동, "
        "描述人物 韓国語, 韓国語 学習, 学韩语, 韩语描述人物, aprender coreano, describir personas coreano, "
        "seongsu, madam j, drjayed, TOPIK")

COMMENT = {
 "ko": ("오늘의 핵심 '-고'로 잇기! 👀 '크다'는 '크고', '작다'는 '작고' — 기본형에서 '다'를 떼고 '고'만 붙이면 돼요. "
        "그럼 '키가 크고 친절해요'처럼 외모와 성격을 한 문장에! 여러분 친구는 어떤 사람인가요? 댓글로 소개해 주세요 😊 "
        "구독하고 다음 강의도 함께해요! 🌐 drjayed.com"),
 "en": ("Today's key: link with '-고'! 👀 '크다' → '크고', '작다' → '작고' — just drop '다' and add '고'. "
        "Then you get '키가 크고 친절해요' (tall AND kind) in one sentence! How would you describe your friend? "
        "Tell us in the comments 😊 Subscribe for more! 🌐 drjayed.com"),
}

for lg in TITLES: w(f"{lg}_title.txt", TITLES[lg])
for lg in DESC:   w(f"{lg}_desc.txt", DESC[lg])
w("w21_tags.txt", TAGS)
for lg in COMMENT: w(f"{lg}_comment.txt", COMMENT[lg])

# 매니페스트(ko/en) — yt_api.py localize 소비
def manifest(video_lang, video_path):
    rows = [
        ("한국어", "ko", False, ["sub"]),
        ("영어", "en", True, ["sub", "meta"]),
        ("일본어", "ja", True, ["sub", "meta"]),
        ("중국어(중국)", "zh", True, ["sub", "meta"]),
        ("스페인어", "es", True, ["sub", "meta"]),
    ]
    langs = []
    for row, code, add, do in rows:
        e = {"row": row, "srt": f"{PKG}/hangeul_w21_madam_np.{code}.srt", "add": add, "do": do}
        if "meta" in do:
            e["title"] = f"{PKG}/{code}_title.txt"; e["desc"] = f"{PKG}/{code}_desc.txt"
        langs.append(e)
    return {"week": "W21", "video_lang": video_lang, "video": video_path,
            "thumbnail": f"hangeul_birth_vowels/thumb_w21_{'ko' if video_lang=='한국어' else 'en'}_1280x720.jpg",
            "langs": langs, "tags_file": f"{PKG}/w21_tags.txt",
            "privacyStatus": "unlisted", "video_id": "", "url": ""}

json.dump(manifest("한국어", "hangeul_birth_vowels/hangeul_w21_madam_np_ko.mp4"),
          open(f"{PKG}/w21_ko_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(manifest("영어", "hangeul_birth_vowels/hangeul_w21_madam_np_en.mp4"),
          open(f"{PKG}/w21_en_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("W21 패키지 생성:", sorted(os.listdir(PKG)))
print("태그 길이:", len(TAGS), "자")
