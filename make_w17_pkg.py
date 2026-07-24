# -*- coding: utf-8 -*-
"""W17 업로드 패키지 — 제목·설명(5개 언어) + 태그 + 챕터 + 매니페스트 + 고정댓글.
   주제: 존댓말↔반말('요/습니다' 빼기) + 축약어(생축·아아·꿀잼·노잼) + K팝/K드라마 학습법 + 반말 전화회화.
   캐릭터: 티쳐제이 · 배경: 불국사(경주) · 46씬 / 8분 37초(517초) 4K.
   ★자막은 API 매니페스트 subs 5개 언어 srt 경로 포함(자막 파일은 pack_subs가 subs_upload/에 채움).
   (make_w16_pkg.py 복제·치환)"""
import os, json
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w17pkg"
os.makedirs(PKG, exist_ok=True)

# 챕터 — hangeul_w17_teacherjay_np_timeline.json 기반 실제 막 구간(6막)
CH_KO = """0:00 경주 불국사 도착 · 진짜 한국어
1:11 존댓말 vs 반말 ('요/습니다' 빼기 · 4개 비교)
3:43 축약어 (생축·아아·꿀잼·노잼)
5:44 K팝·K드라마로 똑똑하게 공부하기 (섀도잉)
6:24 반말 전화회화 실전 (주말에 뭐 해?)
7:27 오늘의 정리 · 마무리"""
CH_EN = """0:00 Arrive at Bulguksa, Gyeongju · real Korean
1:11 Polite vs Casual — dropping '요/습니다' (4 pairs)
3:43 Slang (생축·아아·꿀잼·노잼)
5:44 Study smart with K-pop & K-drama (shadowing)
6:24 Casual phone-call practice (주말에 뭐 해?)
7:27 Review · wrap-up"""

# AI 고지 (precheck: 'AI' + 'Azure' 필수)
AI_KO = "\n🤖 제작 안내\n이 영상의 배경 이미지는 Google Gemini AI(Nano Banana)로 생성했고, 캐릭터 애니메이션은 자체 엔진으로 연출했으며, 나레이션은 Microsoft Azure TTS(선희·Emma)로 만들었습니다.\n\n🌐 drjayed.com\n"
AI_EN = "\n🤖 Production note\nBackground images were generated with Google Gemini AI (Nano Banana); character animation was directed with our own engine; narration was created with Microsoft Azure TTS (SunHi & Emma).\n\n🌐 drjayed.com\n"

# 핵심 표현 — ★영어판에도 한글 원문 유지 '한글' (뜻)
KEY_KO = ("존댓말 · 반말 · '요'/'습니다' 빼기 · "
          "밥 먹었어요? → 밥 먹었어? · 어디 가요? → 어디 가? · 고마워요 → 고마워 · 잘 가요 → 잘 가 · "
          "축약어 · 생축(생일 축하해) · 아아(아이스 아메리카노) · 뜨아 · 꿀잼(진짜 재미있다) · 노잼 · "
          "케이팝 · 케이드라마 · 섀도잉 · 주말에 뭐 해? · 그냥 집에서 케이드라마 봐. 너는? · "
          "불국사 · 경주")
KEY_EN = ("존댓말 (polite speech) · 반말 (casual speech) · dropping '요'/'습니다' · "
          "밥 먹었어요? → 밥 먹었어? (Have you eaten?) · 어디 가요? → 어디 가? (Where are you going?) · "
          "고마워요 → 고마워 (thank you) · 잘 가요 → 잘 가 (goodbye) · "
          "축약어 (slang/abbreviations) · 생축 (happy birthday) · 아아 (iced americano) · 꿀잼 (really fun) · 노잼 (not fun) · "
          "케이팝 (K-pop) · 케이드라마 (K-drama) · 섀도잉 (shadowing) · "
          "주말에 뭐 해? (What are you doing this weekend?) · 불국사 (Bulguksa) · 경주 (Gyeongju)")

TITLES = {
    "ko": "반말·축약어 한국어 - 존댓말 vs 반말 & 생축·아아·꿀잼 | 한글 배우기 W17 (불국사)",
    "en": "Korean Casual Speech & Slang - Polite vs Casual & K-Slang | Learn Korean W17 (Bulguksa)",
    "ja": "韓国語のタメ口と略語: 敬語vsタメ口 & 生祝・アア・クルジェム | 韓国語学習 W17 (仏国寺)",
    "zh": "韩语半语与缩略语: 敬语vs半语 & 生祝·冰美·超有趣 | 韩语学习 W17 (佛国寺)",
    "es": "Coreano Informal y Jerga - Formal vs Informal & K-Slang | Aprende Coreano W17 (Bulguksa)",
}
DESCS = {
    "ko": f"""친구끼리 쓰는 반말과 요즘 축약어를 한국어로 배웁니다 — 티쳐제이와 함께 천 년 고도 경주의 불국사를 거닐며 교과서엔 없는 '진짜 한국어'를 익혀요.
예의를 갖춘 '존댓말'과 편하게 하는 '반말'의 차이를 '밥 먹었어요? → 밥 먹었어?'처럼 하나하나 비교하고, 문장 끝의 '요'나 '습니다'만 빼면 반말이 되는 규칙을 배웁니다.
'생축'(생일 축하해), '아아'(아이스 아메리카노), '꿀잼'(진짜 재미있다), '노잼' 같은 실생활 축약어와, 케이팝·케이드라마로 발음과 억양을 익히는 섀도잉 학습법, 그리고 친구와의 반말 전화회화까지 실전으로 연습해요. 초보자 환영!

📚 오늘 배우는 핵심 표현
{KEY_KO}

⏱️ 챕터
{CH_KO}
{AI_KO}""",
    "en": f"""Learn the casual speech friends use and today's popular slang in Korean — stroll through Bulguksa in Gyeongju, a thousand-year-old capital, with Teacher Jay and pick up the 'real Korean' textbooks never teach.
Compare polite '존댓말' and casual '반말' one pair at a time, like '밥 먹었어요? → 밥 먹었어?' (Have you eaten?), and learn the simple rule: just drop the sentence-ending '요' or '습니다' to make it casual.
You'll also learn everyday slang like '생축' (happy birthday), '아아' (iced americano), '꿀잼' (really fun) and '노잼' (not fun), a shadowing method for mastering pronunciation with K-pop & K-drama, and a real casual phone call with a friend. Beginners welcome!

📚 Key expressions
{KEY_EN}

⏱️ Chapters
{CH_EN}
{AI_EN}""",
    "ja": f"""友達同士で使うタメ口と最近の略語を韓国語で学びます — ティーチャー・ジェイと一緒に千年の古都・慶州（キョンジュ）の仏国寺（プルグクサ）を散策しながら、教科書にはない「本物の韓国語」を身につけましょう。
丁寧な「존댓말（敬語）」と気楽な「반말（タメ口）」の違いを「밥 먹었어요? → 밥 먹었어?（ご飯食べた？）」のように一つずつ比べ、文末の「요」や「습니다」を外すだけでタメ口になるルールを学びます。
「생축（誕生日おめでとう）」「아아（アイスアメリカーノ）」「꿀잼（超おもしろい）」「노잼（つまらない）」などの略語、K-POP・K-ドラマでのシャドーイング学習法、友達とのタメ口電話会話も実践します。初心者歓迎！

📚 重要表現
{KEY_EN}

⏱️ チャプター
{CH_EN}
{AI_EN}""",
    "zh": f"""用韩语学习朋友之间使用的半语和最近流行的缩略语 — 和Teacher Jay一起漫步千年古都庆州的佛国寺，学习教科书里没有的"真正的韩语"。
把礼貌的"존댓말（敬语）"和随意的"반말（半语）"像"밥 먹었어요? → 밥 먹었어?（吃饭了吗？）"这样一对一对地比较，并学会一个简单规则：只要去掉句尾的"요"或"습니다"就变成半语。
你还会学到"생축（生日快乐）""아아（冰美式）""꿀잼（超有趣）""노잼（无聊）"等生活缩略语，用K-pop和K-drama练发音语调的跟读法，以及和朋友的半语电话对话实战。欢迎初学者！

📚 重点表达
{KEY_EN}

⏱️ 章节
{CH_EN}
{AI_EN}""",
    "es": f"""Aprende el habla informal que usan los amigos y la jerga actual en coreano — pasea por Bulguksa en Gyeongju, una capital milenaria, con Teacher Jay y aprende el 'coreano real' que los libros nunca enseñan.
Compara el formal '존댓말' y el informal '반말' par por par, como '밥 먹었어요? → 밥 먹었어?' (¿Has comido?), y aprende la regla simple: solo quita el '요' o '습니다' final para volverlo informal.
También aprenderás jerga cotidiana como '생축' (feliz cumpleaños), '아아' (americano helado), '꿀잼' (muy divertido) y '노잼' (aburrido), un método de shadowing con K-pop y K-drama, y una llamada informal real con un amigo. ¡Principiantes bienvenidos!

📚 Expresiones clave
{KEY_EN}

⏱️ Capítulos
{CH_EN}
{AI_EN}""",
}
TAGS = ("한국어 배우기,한글 배우기,korean casual speech,banmal,korean slang,learn korean,korean honorifics,"
        "존댓말 반말,반말,축약어,생축,아아,꿀잼,노잼,k-slang,korean for beginners,korean vocabulary,korean lesson,"
        "케이팝,케이드라마,shadowing korean,speak korean,korean phrases,불국사,bulguksa,경주,gyeongju,drjayed,"
        "korean conversation,korean pronunciation,real korean,한국어 슬랭,韓国語 勉強,韓国語 タメ口,韓国語 略語,"
        "学韩语,韩语口语,韩语俚语,韩语敬语,coreano informal,aprender coreano,jerga coreana,티쳐제이,korean study")

# 고정댓글
COMMENTS = {
    "ko": """🏯 안녕하세요! 티쳐제이와 함께 경주 불국사를 거닐며 반말과 축약어를 배워봤어요.
'밥 먹었어요? → 밥 먹었어?'처럼 '요'만 빼면 반말이 되는 규칙부터 생축·아아·꿀잼 같은 요즘 줄임말, 케이팝·케이드라마 섀도잉 학습법까지 — 교과서엔 없는 진짜 한국어를 익혀보세요.

👉 전체 168강: https://drjayed.com
여러분이 아는 한국어 축약어가 있나요? 댓글로 알려주세요 😊""",
    "en": """🏯 Hello! We strolled through Bulguksa in Gyeongju with Teacher Jay to learn casual speech and slang.
From the simple rule — drop the '요' to turn '밥 먹었어요?' into '밥 먹었어?' — to today's slang like 생축·아아·꿀잼 and a K-pop / K-drama shadowing method, pick up the real Korean textbooks never teach.

👉 Full 168-lesson course: https://drjayed.com
What Korean slang do you know? Let us know in the comments 😊""",
}

for c, t in TITLES.items(): open(f"{PKG}/{c}_title.txt", "w", encoding="utf-8").write(t)
for c, dd in DESCS.items(): open(f"{PKG}/{c}_desc.txt", "w", encoding="utf-8").write(dd)
for c, cm in COMMENTS.items(): open(f"{PKG}/{c}_comment.txt", "w", encoding="utf-8").write(cm)
open(f"{PKG}/w17_tags.txt", "w", encoding="utf-8").write(TAGS)

# 매니페스트 — ★자막 API 업로드(subs 5개 언어)
YT5 = {"ko": "한국어", "en": "영어", "ja": "일본어", "zh": "중국어(중국)", "es": "스페인어"}
for lang in ("ko", "en"):
    subdir = f"subs_upload/W17_{'1_한글판' if lang == 'ko' else '2_영어판'}"
    mf = {
        "week": "W17", "lang": lang,
        "video": f"hangeul_birth_vowels/hangeul_w17_teacherjay_np_{lang}.mp4",
        "thumbnail": f"hangeul_birth_vowels/thumb_w17_{lang}_1280x720.jpg",
        "defaultLanguage": lang,
        "title": TITLES[lang], "description": DESCS[lang],
        "localizations": {c: {"title": TITLES[c], "description": DESCS[c]} for c in ("ko", "en", "ja", "zh", "es")},
        "tags_file": f"{PKG}/w17_tags.txt",
        "subs": {c: f"{subdir}/{YT5[c]}.srt" for c in ("ko", "en", "ja", "zh", "es")},  # ★API 업로드
        "privacyStatus": "unlisted",
    }
    open(f"{PKG}/w17_{lang}_manifest.json", "w", encoding="utf-8").write(json.dumps(mf, ensure_ascii=False, indent=2))

print(f"패키지: {PKG}")
for f in sorted(os.listdir(PKG)): print(f"  {f}")
# 길이 검증
for c in ("ko", "en", "ja", "zh", "es"):
    t = open(f"{PKG}/{c}_title.txt", encoding="utf-8").read()
    print(f"  title[{c}] {len(t)}자")
tg = open(f"{PKG}/w17_tags.txt", encoding="utf-8").read()
print(f"  tags {len(tg)}자(원문)")
