# -*- coding: utf-8 -*-
"""W16 업로드 패키지 — 제목·설명(5개 언어) + 태그 + 챕터 + 매니페스트 + 고정댓글.
   주제: 취미(hobby) 어휘 + 빈도 표현(매일·보통·자주·가끔·거의 안·전혀 안 / 일주일에 세 번…).
   캐릭터: 인준 · 배경: 남이섬(춘천) · 37씬 / 6분 59초(419초) 4K.
   ★자막은 API 매니페스트 subs 5개 언어 srt 경로 포함(자막 파일은 사장님이 subs_upload/에 채움).
   (make_w15_pkg.py 복제·치환)"""
import os, json
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w16pkg"
os.makedirs(PKG, exist_ok=True)

# 챕터 — hangeul_w16_stickman_np.ko.srt 타임스탬프 기반 실제 씬 구간
CH_KO = """0:00 남이섬 도착 · '취미'가 뭐예요?
0:31 취미 묻고 답하기 (제 취미는… · 좋아해요)
1:22 얼마나 자주? 빈도 부사 6단계 (매일·보통·자주·가끔·거의 안·전혀 안)
2:49 남이섬 야외 취미 (자전거·산책·조깅·사진·낚시·짚와이어)
4:56 집에서 하는 취미 (독서·피아노·요리·영화·게임)
6:14 반전: 진짜 매일 하는 것 · 마무리"""
CH_EN = """0:00 Arrive at Nami Island · What is a '취미' (hobby)?
0:31 Asking & answering about hobbies (My hobby is… · I like…)
1:22 How often? 6 frequency adverbs (every day·usually·often·sometimes·rarely·never)
2:49 Outdoor hobbies on Nami Island (cycling·walking·jogging·photos·fishing·zip-wire)
4:56 Hobbies at home (reading·piano·cooking·movies·games)
6:14 The twist: what I really do every day · Wrap-up"""

# AI 고지 (precheck: 'AI' + 'Azure' 필수)
AI_KO = "\n🤖 제작 안내\n이 영상의 배경 이미지는 Google Gemini AI(Nano Banana)로 생성했고, 캐릭터 애니메이션은 자체 엔진으로 연출했으며, 나레이션은 Microsoft Azure TTS(선희·Emma)로 만들었습니다.\n\n🌐 drjayed.com\n"
AI_EN = "\n🤖 Production note\nBackground images were generated with Google Gemini AI (Nano Banana); character animation was directed with our own engine; narration was created with Microsoft Azure TTS (SunHi & Emma).\n\n🌐 drjayed.com\n"

# 핵심 표현 — ★영어판에도 한글 원문 유지 '한글' (뜻)
KEY_KO = ("취미 · 취미가 뭐예요? · 제 취미는 ~예요 · ~는 것을 좋아해요 · 얼마나 자주? · "
          "매일 · 보통 · 자주 · 가끔 · 거의 안 · 전혀 안 · "
          "일주일에 세 번 · 하루에 두 번 · 한 달에 한 번 · 일 년에 한 번 · "
          "자전거 타기 · 산책 · 조깅 · 사진 찍기 · 피크닉 · 연날리기 · 프리스비 · 배드민턴 · 낚시 · "
          "강아지 산책 · 짚와이어 · 캠핑 · 독서 · 그림 그리기 · 스케이트보드 · 피아노 · 요리 · 영화 보기 · 게임 · "
          "남이섬 · 춘천")
KEY_EN = ("취미 (hobby) · 취미가 뭐예요? (What's your hobby?) · 제 취미는 ~예요 (My hobby is ~) · "
          "~는 것을 좋아해요 (I like ~ing) · 얼마나 자주? (how often?) · "
          "매일 (every day) · 보통 (usually) · 자주 (often) · 가끔 (sometimes) · 거의 안 (rarely) · 전혀 안 (never) · "
          "일주일에 세 번 (three times a week) · 하루에 두 번 (twice a day) · 한 달에 한 번 (once a month) · "
          "자전거 타기 (cycling) · 산책 (a walk) · 조깅 (jogging) · 사진 찍기 (photography) · 낚시 (fishing) · "
          "짚와이어 (zip-wire) · 독서 (reading) · 피아노 (piano) · 요리 (cooking) · 영화 보기 (movies) · 게임 (games) · "
          "남이섬 (Nami Island)")

TITLES = {
    "ko": "취미와 빈도 표현 한국어 - 매일·자주·가끔 & 취미 20가지 | 한글 배우기 W16 (남이섬)",
    "en": "Korean Hobbies & Frequency - every day, often, sometimes | Learn Korean W16 (Nami Island)",
    "ja": "韓国語で趣味と頻度表現: 毎日・よく・時々 & 趣味20 | 韓国語学習 W16 (南怡島)",
    "zh": "韩语兴趣爱好与频率表达: 每天·经常·有时 & 20种爱好 | 韩语学习 W16 (南怡岛)",
    "es": "Pasatiempos y Frecuencia en Coreano: cada día, a menudo, a veces | Aprende Coreano W16 (Nami)",
}
DESCS = {
    "ko": f"""취미와 빈도 표현을 한국어로 배웁니다 — 인준과 함께 아름다운 섬 남이섬을 거닐며 취미 20가지와 '얼마나 자주' 하는지를 배워요.
'취미가 뭐예요?' 물어보고 '제 취미는 자전거 타기예요'라고 답하는 법, 그리고 매일·보통·자주·가끔·거의 안·전혀 안 같은 빈도 부사를 자연스럽게 익혀요.
'일주일에 세 번', '하루에 두 번' 같은 횟수 표현도 함께 배웁니다.
마지막엔 인준이 진짜 매일 빠지지 않고 하는 취미가 무엇인지 반전이 기다려요. 초보자 환영!

📚 오늘 배우는 핵심 표현
{KEY_KO}

⏱️ 챕터
{CH_KO}
{AI_KO}""",
    "en": f"""Learn Korean hobbies and how to say how often you do them — stroll through the beautiful Nami Island with Injun and pick up 20 hobbies plus frequency expressions.
Ask '취미가 뭐예요?' (What's your hobby?) and answer '제 취미는 자전거 타기예요' (My hobby is cycling), and learn frequency adverbs like 매일 (every day), 보통 (usually), 자주 (often), 가끔 (sometimes), 거의 안 (rarely), and 전혀 안 (never).
You'll also learn counts like '일주일에 세 번' (three times a week) and '하루에 두 번' (twice a day).
And there's a twist at the end — the one hobby Injun really does every day! Beginners welcome!

📚 Key expressions
{KEY_EN}

⏱️ Chapters
{CH_EN}
{AI_EN}""",
    "ja": f"""韓国語で趣味と頻度表現を学びます — インジュンと一緒に美しい南怡島（ナミソム）を散策しながら、20の趣味と「どのくらい頻繁に」するかを学びましょう。
「취미가 뭐예요?（趣味は何ですか？）」と尋ね、「제 취미는 자전거 타기예요（私の趣味はサイクリングです）」と答える言い方、そして 매일（毎日）・보통（普段）・자주（よく）・가끔（時々）・거의 안（ほとんど〜ない）・전혀 안（全く〜ない）などの頻度副詞を自然に覚えます。
最後にはインジュンが本当に毎日欠かさずする趣味は何か、どんでん返しが待っています。初心者歓迎！

📚 重要表現
{KEY_EN}

⏱️ チャプター
{CH_EN}
{AI_EN}""",
    "zh": f"""用韩语学习兴趣爱好与频率表达 — 和仁俊一起漫步美丽的南怡岛，学习20种爱好以及"多久做一次"。
学会问"취미가 뭐예요?（你的爱好是什么？）"并回答"제 취미는 자전거 타기예요（我的爱好是骑自行车）"，还有 매일（每天）·보통（通常）·자주（经常）·가끔（有时）·거의 안（很少）·전혀 안（从不）等频率副词。
你还会学到"일주일에 세 번（一周三次）"、"하루에 두 번（一天两次）"这样的次数表达。
最后还有一个反转——仁俊真正每天坚持的爱好是什么呢！欢迎初学者！

📚 重点表达
{KEY_EN}

⏱️ 章节
{CH_EN}
{AI_EN}""",
    "es": f"""Aprende los pasatiempos en coreano y cómo decir con qué frecuencia los haces — pasea por la hermosa isla de Nami con Injun y aprende 20 pasatiempos junto con expresiones de frecuencia.
Pregunta '취미가 뭐예요?' (¿Cuál es tu pasatiempo?) y responde '제 취미는 자전거 타기예요' (Mi pasatiempo es andar en bici), y aprende adverbios de frecuencia como 매일 (cada día), 보통 (normalmente), 자주 (a menudo), 가끔 (a veces), 거의 안 (rara vez) y 전혀 안 (nunca).
También aprenderás conteos como '일주일에 세 번' (tres veces por semana) y '하루에 두 번' (dos veces al día).
¡Y hay un giro al final — el único pasatiempo que Injun realmente hace todos los días! ¡Principiantes bienvenidos!

📚 Expresiones clave
{KEY_EN}

⏱️ Capítulos
{CH_EN}
{AI_EN}""",
}
TAGS = ("한국어 배우기,한글 배우기,korean hobbies,how often in korean,korean frequency adverbs,learn korean,"
        "korean for beginners,취미,빈도,매일 자주 가끔,korean adverbs,korean vocabulary,korean lesson,"
        "취미가 뭐예요,자전거 타기,speak korean,나미섬,nami island,춘천,chuncheon,korean phrases,drjayed")

# 고정댓글
COMMENTS = {
    "ko": """🚲 안녕하세요! 인준과 함께 남이섬을 거닐며 취미 20가지와 빈도 표현을 배워봤어요.
'취미가 뭐예요?' 묻고 답하는 법부터 매일·보통·자주·가끔·거의 안·전혀 안까지 — 얼마나 자주 하는지 말하는 법을 자연스럽게 익혀보세요.

👉 전체 168강: https://drjayed.com
여러분의 취미는 뭐예요? 그리고 얼마나 자주 하세요? 댓글로 알려주세요 😊""",
    "en": """🚲 Hello! We strolled through Nami Island with Injun to learn 20 hobbies and how to say how often you do them.
From '취미가 뭐예요?' (What's your hobby?) to 매일·보통·자주·가끔·거의 안·전혀 안 — pick up frequency expressions the natural way.

👉 Full 168-lesson course: https://drjayed.com
What's YOUR hobby, and how often do you do it? Let us know in the comments 😊""",
}

for c, t in TITLES.items(): open(f"{PKG}/{c}_title.txt", "w", encoding="utf-8").write(t)
for c, dd in DESCS.items(): open(f"{PKG}/{c}_desc.txt", "w", encoding="utf-8").write(dd)
for c, cm in COMMENTS.items(): open(f"{PKG}/{c}_comment.txt", "w", encoding="utf-8").write(cm)
open(f"{PKG}/w16_tags.txt", "w", encoding="utf-8").write(TAGS)

# 매니페스트 — ★자막 API 업로드(subs 5개 언어)
YT5 = {"ko": "한국어", "en": "영어", "ja": "일본어", "zh": "중국어(중국)", "es": "스페인어"}
for lang in ("ko", "en"):
    subdir = f"subs_upload/W16_{'1_한글판' if lang == 'ko' else '2_영어판'}"
    mf = {
        "week": "W16", "lang": lang,
        "video": f"hangeul_birth_vowels/hangeul_w16_stickman_np_{lang}.mp4",
        "thumbnail": f"hangeul_birth_vowels/thumb_w16_{lang}_1280x720.jpg",
        "defaultLanguage": lang,
        "title": TITLES[lang], "description": DESCS[lang],
        "localizations": {c: {"title": TITLES[c], "description": DESCS[c]} for c in ("ko", "en", "ja", "zh", "es")},
        "tags_file": f"{PKG}/w16_tags.txt",
        "subs": {c: f"{subdir}/{YT5[c]}.srt" for c in ("ko", "en", "ja", "zh", "es")},  # ★API 업로드
        "privacyStatus": "unlisted",
    }
    open(f"{PKG}/w16_{lang}_manifest.json", "w", encoding="utf-8").write(json.dumps(mf, ensure_ascii=False, indent=2))

print(f"패키지: {PKG}")
for f in sorted(os.listdir(PKG)): print(f"  {f}")
# 길이 검증
for c in ("ko", "en", "ja", "zh", "es"):
    t = open(f"{PKG}/{c}_title.txt", encoding="utf-8").read()
    print(f"  title[{c}] {len(t)}자")
tg = open(f"{PKG}/w16_tags.txt", encoding="utf-8").read()
print(f"  tags {len(tg)}자(원문)")
