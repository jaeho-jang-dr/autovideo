# -*- coding: utf-8 -*-
"""W14 업로드 패키지 — 제목·설명(5개 언어) + 태그 + 매니페스트.
   ★자막은 사장님이 직접 올리시므로 매니페스트의 자막 항목은 비워둔다.
   W13 패키지(w13pkg) 구조를 그대로 따른다."""
import os, json

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w14pkg"
os.makedirs(PKG, exist_ok=True)

CHAPTERS = """0:00 협재의 아침 · 일어나다
1:10 아침 준비 · 세수·이 닦기·옷 입기
1:45 아침 식사 · 먹다/마시다
2:21 낮 · 일하다·공부하다
3:08 점심 · 쉬다
3:37 오후 · 산책·수영·사진
4:14 저녁 · 먹다·전화하다
4:51 노을 보기 · 아름다워요
5:04 밤 · 샤워·일기·별
5:29 자다 · 하루의 끝"""

CH_EN = """0:00 Morning at Hyeopjae · Waking up
1:10 Getting ready · Wash face, brush teeth, get dressed
1:45 Breakfast · Eat & drink
2:21 Daytime · Work & study
3:08 Lunch · Rest
3:37 Afternoon · Walk, swim, photos
4:14 Evening · Dinner & phone call
4:51 Watching the sunset · It's beautiful
5:04 Night · Shower, diary, stars
5:29 Sleep · End of the day"""

AI_NOTE_KO = """
🤖 제작 안내
이 영상의 이미지·영상 연출은 Google Gemini(Nano Banana)로 생성했고,
나레이션은 Microsoft Azure TTS(선희·Emma)로 만들었습니다.

🌐 drjayed.com
"""
AI_NOTE_EN = """
🤖 Production note
Visuals in this video were generated with Google Gemini (Nano Banana),
and the narration was created with Microsoft Azure TTS (SunHi & Emma).

🌐 drjayed.com
"""

KEY_KO = ("일과 · 일어나다 · 아침에 일어나요 · 몇 시에 일어나요? · 일찍 · 늦게 · 창문을 열어요 · "
          "세수하다 · 이를 닦다 · 옷을 입다 · 옷을 벗다 · 아침을 먹다 · 마시다 · 늦었어요 · 서두르다 · "
          "일하다 · 카페에서 일해요 · 공부하다 · 한국어를 공부해요 · 책을 읽다 · 쓰다 · 점심을 먹다 · "
          "쉬다 · 산책하다 · 해변을 걸어요 · 수영하다 · 사진을 찍다 · 재미있어요 · 피곤해요 · "
          "저녁을 먹다 · 전화하다 · 텔레비전을 보다 · 노을을 보다 · 아름다워요 · 샤워하다 · "
          "일기를 쓰다 · 자다 · 열한 시에 자요")

KEY_EN = ("일과 (daily routine) · 일어나다 (wake up) · 세수하다 (wash face) · 이를 닦다 (brush teeth) · "
          "옷을 입다 (get dressed) · 아침을 먹다 (eat breakfast) · 마시다 (drink) · 서두르다 (hurry) · "
          "일하다 (work) · 공부하다 (study) · 책을 읽다 (read) · 쓰다 (write) · 쉬다 (rest) · "
          "산책하다 (take a walk) · 수영하다 (swim) · 사진을 찍다 (take a photo) · 피곤해요 (I'm tired) · "
          "저녁을 먹다 (eat dinner) · 전화하다 (call) · 노을을 보다 (watch the sunset) · "
          "샤워하다 (shower) · 일기를 쓰다 (write a diary) · 자다 (sleep)")

TITLES = {
    "ko": "하루 일과 한국어 - 일어나다·먹다·일하다·자다 총정리 | 한글 배우기 W14 (제주 협재해수욕장)",
    "en": "Korean Daily Routine - Wake Up, Eat, Work & Sleep | Learn Korean W14 (Jeju)",
    "ja": "韓国語で一日の生活: 起きる・食べる・働く・寝る | 韓国語学習 W14 (済州)",
    "zh": "韩语日常作息: 起床·吃饭·工作·睡觉 | 韩语学习 W14 (济州)",
    "es": "Rutina Diaria en Coreano: Despertar, Comer, Trabajar y Dormir | Aprende Coreano W14",
}

DESCS = {
    "ko": f"""한국어로 나의 하루 일과를 말하는 법을 배웁니다 — 제주 협재해수욕장에서 아침부터 밤까지 함께해요.
아침에 일어나서 세수하고, 밥을 먹고, 카페에서 일하고 공부하고, 바닷가를 산책하고,
저녁을 먹고 노을을 보고, 일기를 쓰고 잠자리에 들 때까지 — 하루에 쓰는 동사를 순서대로 익힙니다.
마담제이와 함께 따라 하면 나의 하루를 한국어로 말할 수 있어요. 초보자 환영!

📚 오늘 배우는 핵심 표현
{KEY_KO}

⏱️ 챕터
{CHAPTERS}
{AI_NOTE_KO}""",
    "en": f"""Learn how to talk about your daily routine in Korean — from morning to night at Hyeopjae Beach, Jeju.
Wake up, wash your face, eat breakfast, work at a cafe, study Korean, walk on the beach,
have dinner, watch the sunset, write a diary, and go to sleep —
you'll learn the everyday verbs in the order you actually use them.
Follow Madam J and you'll be able to describe your whole day in Korean. Beginners welcome!

📚 Key expressions in this lesson
{KEY_EN}

⏱️ Chapters
{CH_EN}
{AI_NOTE_EN}""",
    "ja": f"""韓国語で一日の生活を話す方法を学びます — 済州のヒョプチェビーチで、朝から夜まで一緒に過ごしましょう。
朝起きて顔を洗い、ご飯を食べ、カフェで働き、勉強し、海辺を散歩し、
夕食を食べて夕焼けを見て、日記を書いて眠りにつくまで — 一日で使う動詞を順番に学びます。
マダムJと一緒に練習すれば、あなたの一日を韓国語で話せるようになります。初心者歓迎！

📚 このレッスンの重要表現
{KEY_EN}

⏱️ チャプター
{CH_EN}
{AI_NOTE_EN}""",
    "zh": f"""学习用韩语描述你的一天 — 在济州协才海水浴场，从早到晚一起度过。
早上起床、洗脸、吃早饭、在咖啡厅工作学习、在海边散步、
吃晚饭、看晚霞、写日记，直到入睡 — 按顺序学会一天中使用的动词。
跟着Madam J一起练习，你就能用韩语讲述自己的一天。欢迎初学者！

📚 本课重点表达
{KEY_EN}

⏱️ 章节
{CH_EN}
{AI_NOTE_EN}""",
    "es": f"""Aprende a hablar de tu rutina diaria en coreano — desde la mañana hasta la noche en la playa Hyeopjae, Jeju.
Despertarse, lavarse la cara, desayunar, trabajar en un café, estudiar, pasear por la playa,
cenar, ver el atardecer, escribir un diario y dormir —
aprenderás los verbos cotidianos en el orden en que realmente se usan.
Sigue a Madam J y podrás describir todo tu día en coreano. ¡Principiantes bienvenidos!

📚 Expresiones clave de esta lección
{KEY_EN}

⏱️ Capítulos
{CH_EN}
{AI_NOTE_EN}""",
}

TAGS = ("한국어 배우기,한글 배우기,korean daily routine,learn korean,korean for beginners,"
        "korean verbs,일과,하루 일과,korean lesson,speak korean,korean listening,"
        "korean vocabulary,제주,협재해수욕장,jeju,hyeopjae beach,korean study,"
        "한국어 회화,korean conversation,drjayed")

for code, t in TITLES.items():
    open(f"{PKG}/{code}_title.txt", "w", encoding="utf-8").write(t)
for code, d in DESCS.items():
    open(f"{PKG}/{code}_desc.txt", "w", encoding="utf-8").write(d)
open(f"{PKG}/w14_tags.txt", "w", encoding="utf-8").write(TAGS)

# 매니페스트 — ★자막은 사장님이 직접 올리시므로 subs를 비운다
for lang in ("ko", "en"):
    mf = {
        "week": "W14",
        "lang": lang,
        "video": f"hangeul_birth_vowels/hangeul_w14_madam_np_{lang}_4k.mp4",
        "thumbnail": f"hangeul_birth_vowels/thumb_w14_{lang}_1280x720.jpg",
        "defaultLanguage": "ko" if lang == "ko" else "en",
        "title": TITLES["ko"] if lang == "ko" else TITLES["en"],
        "description": DESCS["ko"] if lang == "ko" else DESCS["en"],
        "localizations": {c: {"title": TITLES[c], "description": DESCS[c]}
                          for c in ("ko", "en", "ja", "zh", "es")},
        "tags_file": f"{PKG}/w14_tags.txt",
        "subs": {},   # ★비움 — 사장님이 유튜브 UI로 직접 업로드(API 쿼터 4,000 절약)
        "privacyStatus": "unlisted",
    }
    open(f"{PKG}/w14_{lang}_manifest.json", "w", encoding="utf-8").write(
        json.dumps(mf, ensure_ascii=False, indent=2))

print(f"패키지 생성: {PKG}")
for f in sorted(os.listdir(PKG)):
    print(f"   {f}  ({os.path.getsize(os.path.join(PKG,f))}B)")
