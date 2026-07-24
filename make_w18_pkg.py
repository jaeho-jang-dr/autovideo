# -*- coding: utf-8 -*-
"""W18 업로드 패키지 — 제목·설명(5개 언어) + 태그 + 챕터 + 매니페스트 + 고정댓글.
   주제: 감정 표현(기쁘다·슬프다·긴장되다·속상하다) + 감정 원인 문형(-아서/어서) + 세밀한 마음 묘사(서운하다·뿌듯하다·벅차다·뭉클하다·울컥하다) + 공감·위로 + 한국의 '정(情)'.
   캐릭터: 마담제이 · 배경: 전주 한옥마을 · 46씬 4K.
   챕터는 타임라인 json(막 경계 씬)에서 자동 계산.
   (make_w17_pkg.py 복제·치환)"""
import os, json
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w18pkg"
os.makedirs(PKG, exist_ok=True)

# ---------- 챕터: 타임라인에서 막 경계(씬 1/7/19/29/39/45) 시작 시각 계산 ----------
def mmss(sec):
    sec = int(sec + 0.5); return f"{sec // 60}:{sec % 60:02d}"

TL = "hangeul_birth_vowels/hangeul_w18_madamjay_np_timeline.json"
ACT_STARTS = [(1, "전주 한옥마을 도착 · 오늘의 마음 수업", "Arrive at Jeonju Hanok Village · today's lesson"),
              (7, "기본 감정 네 가지 (기쁘다·슬프다·긴장되다·속상하다)", "Four core feelings (happy·sad·nervous·upset)"),
              (19, "감정의 원인 잇기 (-아서/어서)", "Linking cause & feeling (-아서/어서)"),
              (29, "세밀한 마음 묘사 (서운하다·뿌듯하다·벅차다·울컥하다)", "Subtle nuances (let-down·proud·overwhelmed·welling up)"),
              (39, "공감·위로와 한국의 '정(情)'", "Empathy, comfort & Korean 'jeong'"),
              (45, "오늘의 정리 · 마무리", "Review · wrap-up")]

def chapters():
    ko, en = [], []
    if os.path.exists(TL):
        tl = json.load(open(TL, encoding="utf-8"))
        lead = tl.get("lead", 0.0)
        dur = {s["seq"]: s["dur"] for s in tl["scenes"]}
        seqs = sorted(dur)
        cum = {}
        acc = lead
        for sq in seqs:
            cum[sq] = acc; acc += dur[sq]
        for sq, k, e in ACT_STARTS:
            t = cum.get(sq, 0.0) if sq != 1 else 0.0
            ko.append(f"{mmss(t)} {k}"); en.append(f"{mmss(t)} {e}")
    else:  # 타임라인 없으면 근사
        approx = [0, 75, 210, 360, 480, 600]
        for (sq, k, e), t in zip(ACT_STARTS, approx):
            ko.append(f"{mmss(t)} {k}"); en.append(f"{mmss(t)} {e}")
    return "\n".join(ko), "\n".join(en)

CH_KO, CH_EN = chapters()

AI_KO = "\n🤖 제작 안내\n이 영상의 배경 이미지는 Google Gemini AI(Nano Banana)로 생성했고, 캐릭터 애니메이션은 자체 엔진으로 연출했으며, 나레이션은 Microsoft Azure TTS(선희·Emma)로 만들었습니다.\n\n🌐 drjayed.com\n"
AI_EN = "\n🤖 Production note\nBackground images were generated with Google Gemini AI (Nano Banana); character animation was directed with our own engine; narration was created with Microsoft Azure TTS (SunHi & Emma).\n\n🌐 drjayed.com\n"

KEY_KO = ("감정 표현 · 기쁘다 · 슬프다 · 긴장되다 · 속상하다 · 설레다 · 화나다 · 걱정되다 · "
          "-아서/어서 (감정의 원인) · 시험이 끝나서 기뻐요 · 비가 와서 속상해요 · "
          "세밀한 마음 묘사 · 서운하다 · 뿌듯하다 · 아쉽다 · 홀가분하다 · 벅차다 · 뭉클하다 · 두근거리다 · "
          "마음이 놓이다 · 마음이 무겁다 · 울컥하다 · 공감 · 많이 속상했겠어요 · 위로 · 정(情) · 전주 한옥마을")
KEY_EN = ("emotions · 기쁘다 (happy) · 슬프다 (sad) · 긴장되다 (nervous) · 속상하다 (upset) · 설레다 (fluttering) · "
          "-아서/어서 (cause of feeling) · 시험이 끝나서 기뻐요 (glad the exam is over) · 비가 와서 속상해요 (upset it rained) · "
          "subtle feelings · 서운하다 (let down) · 뿌듯하다 (proud) · 아쉽다 (a pity) · 홀가분하다 (light & free) · "
          "벅차다 (overwhelmed) · 뭉클하다 (deeply moved) · 두근거리다 (heart pounding) · "
          "마음이 놓이다 (relieved) · 울컥하다 (welling up) · empathy · 많이 속상했겠어요 (you must have been upset) · "
          "정 (jeong) · 전주 한옥마을 (Jeonju Hanok Village)")

TITLES = {
    "ko": "감정 표현 한국어 - 기쁘다·슬프다·속상하다 & 세밀한 마음 묘사 | 한글 배우기 W18 (전주 한옥마을)",
    "en": "Korean Emotions & Feelings - Happy, Sad, Upset & Subtle Nuances | Learn Korean W18 (Jeonju Hanok)",
    "ja": "韓国語の感情表現: 嬉しい・悲しい・悔しい & 繊細な心の描写 | 韓国語学習 W18 (全州韓屋村)",
    "zh": "韩语情感表达: 高兴·伤心·难过 & 细腻的心情描写 | 韩语学习 W18 (全州韩屋村)",
    "es": "Emociones en Coreano: Feliz, Triste, Dolido y Matices Sutiles | Aprende Coreano W18 (Jeonju)",
}
DESCS = {
    "ko": f"""마음을 표현하는 한국어를 배웁니다 — 마담제이와 함께 고운 기와지붕이 이어지는 전주 한옥마을을 거닐며, 감정을 섬세하게 그리는 '진짜 한국어'를 익혀요.
'기쁘다', '슬프다', '긴장되다', '속상하다' 같은 기본 감정어부터, '시험이 끝나서 기뻐요'처럼 감정의 원인을 잇는 '-아서/어서' 문형, 그리고 '속상하다'와 '서운하다', '벅차다'와 '뭉클하다'처럼 비슷하지만 미묘하게 다른 '세밀한 마음 묘사'까지 배웁니다.
'많이 속상했겠어요' 같은 공감·위로 표현과, 말로 다 못 하는 한국의 '정(情)' 문화도 함께 느껴봐요. 초보자와 중급자 모두 환영!

📚 오늘 배우는 핵심 표현
{KEY_KO}

⏱️ 챕터
{CH_KO}
{AI_KO}""",
    "en": f"""Learn the Korean of the heart — stroll through Jeonju Hanok Village, where graceful tiled roofs ripple like waves, with Madam J and pick up the 'real Korean' for expressing feelings with delicacy.
From core emotion words like '기쁘다' (happy), '슬프다' (sad), '긴장되다' (nervous) and '속상하다' (upset), to the '-아서/어서' pattern that links a cause to a feeling ('시험이 끝나서 기뻐요' — glad the exam is over), and subtle nuances such as '속상하다' vs '서운하다' and '벅차다' vs '뭉클하다'.
You'll also learn empathy and comfort like '많이 속상했겠어요' (you must have been so upset), and feel Korea's '정' (jeong) — the warmth beyond words. Beginners and intermediate learners welcome!

📚 Key expressions
{KEY_EN}

⏱️ Chapters
{CH_EN}
{AI_EN}""",
    "ja": f"""心を表す韓国語を学びます — マダム・ジェイと一緒に、美しい瓦屋根が続く全州（チョンジュ）韓屋村を散策しながら、感情を繊細に描く「本物の韓国語」を身につけましょう。
「기쁘다（嬉しい）」「슬프다（悲しい）」「긴장되다（緊張する）」「속상하다（悔しい・つらい）」などの基本の感情語から、「시험이 끝나서 기뻐요（試験が終わって嬉しい）」のように原因をつなぐ「-아서/어서」の文型、そして「속상하다」と「서운하다」、「벅차다」と「뭉클하다」のような繊細な心の描写まで学びます。
「많이 속상했겠어요（とてもつらかったでしょう）」という共感・慰めの表現や、言葉にできない韓国の「정（情）」も感じてみましょう。初級・中級者歓迎！

📚 重要表現
{KEY_EN}

⏱️ チャプター
{CH_EN}
{AI_EN}""",
    "zh": f"""学习表达内心的韩语 — 和Madam J一起漫步在瓦屋顶连绵起伏的全州韩屋村，学习细腻描写情感的"真正的韩语"。
从"기쁘다（高兴）""슬프다（伤心）""긴장되다（紧张）""속상하다（难过）"等基本情感词，到"시험이 끝나서 기뻐요（考完试很开心）"这样连接原因的"-아서/어서"句型，再到"속상하다"与"서운하다"、"벅차다"与"뭉클하다"这些相似却微妙不同的细腻心情描写。
还会学到"많이 속상했겠어요（你一定很难过吧）"这样的共情安慰表达，以及言语难以尽述的韩国"정（情）"文化。欢迎初中级学习者！

📚 重点表达
{KEY_EN}

⏱️ 章节
{CH_EN}
{AI_EN}""",
    "es": f"""Aprende el coreano del corazón — pasea por el Pueblo Hanok de Jeonju, donde los tejados de tejas ondulan como olas, con Madam J y aprende el 'coreano real' para expresar sentimientos con delicadeza.
Desde palabras básicas de emoción como '기쁘다' (feliz), '슬프다' (triste), '긴장되다' (nervioso) y '속상하다' (dolido), hasta el patrón '-아서/어서' que une una causa con un sentimiento ('시험이 끝나서 기뻐요' — feliz porque terminó el examen), y matices sutiles como '속상하다' vs '서운하다'.
También aprenderás empatía y consuelo como '많이 속상했겠어요' (debiste sentirte muy mal), y sentirás el '정' (jeong) de Corea, la calidez más allá de las palabras. ¡Principiantes e intermedios bienvenidos!

📚 Expresiones clave
{KEY_EN}

⏱️ Capítulos
{CH_EN}
{AI_EN}""",
}
TAGS = ("한국어 배우기,한글 배우기,korean emotions,korean feelings,learn korean,감정 표현,기쁘다,슬프다,속상하다,긴장되다,"
        "korean adjectives,아서 어서,korean grammar,세밀한 마음 묘사,서운하다,뿌듯하다,벅차다,뭉클하다,울컥하다,"
        "korean empathy,정 情,jeong,korean for beginners,korean vocabulary,korean lesson,speak korean,korean phrases,"
        "전주 한옥마을,jeonju,jeonju hanok village,drjayed,korean conversation,korean pronunciation,real korean,"
        "韓国語 勉強,韓国語 感情,感情表現,学韩语,韩语情感,韩语语法,coreano emociones,aprender coreano,마담제이,korean study")

COMMENTS = {
    "ko": """🏯 안녕하세요! 마담제이와 함께 전주 한옥마을을 거닐며 마음을 표현하는 한국어를 배워봤어요.
'기쁘다·슬프다·긴장되다·속상하다' 같은 기본 감정어부터, '시험이 끝나서 기뻐요'처럼 원인을 잇는 '-아서/어서', 그리고 '서운하다·뿌듯하다·뭉클하다'처럼 미묘하게 다른 마음까지 — 교과서엔 없는 섬세한 한국어를 익혀보세요.

👉 전체 168강: https://drjayed.com
오늘 여러분의 마음은 어떤 감정이었나요? 댓글로 살며시 들려주세요 😊""",
    "en": """🏯 Hello! We strolled through Jeonju Hanok Village with Madam J to learn the Korean of the heart.
From core feelings like '기쁘다·슬프다·긴장되다·속상하다' to the '-아서/어서' pattern that links a cause ('시험이 끝나서 기뻐요'), and subtle nuances like '서운하다·뿌듯하다·뭉클하다' — pick up the delicate Korean textbooks never teach.

👉 Full 168-lesson course: https://drjayed.com
What did your heart feel today? Share it gently in the comments 😊""",
}

for c, t in TITLES.items(): open(f"{PKG}/{c}_title.txt", "w", encoding="utf-8").write(t)
for c, dd in DESCS.items(): open(f"{PKG}/{c}_desc.txt", "w", encoding="utf-8").write(dd)
for c, cm in COMMENTS.items(): open(f"{PKG}/{c}_comment.txt", "w", encoding="utf-8").write(cm)
open(f"{PKG}/w18_tags.txt", "w", encoding="utf-8").write(TAGS)

YT5 = {"ko": "한국어", "en": "영어", "ja": "일본어", "zh": "중국어(중국)", "es": "스페인어"}
for lang in ("ko", "en"):
    subdir = f"subs_upload/W18_{'1_한글판' if lang == 'ko' else '2_영어판'}"
    mf = {
        "week": "W18", "lang": lang,
        "video": f"hangeul_birth_vowels/hangeul_w18_madamjay_np_{lang}.mp4",
        "thumbnail": f"hangeul_birth_vowels/thumb_w18_{lang}_1280x720.jpg",
        "defaultLanguage": lang,
        "title": TITLES[lang], "description": DESCS[lang],
        "localizations": {c: {"title": TITLES[c], "description": DESCS[c]} for c in ("ko", "en", "ja", "zh", "es")},
        "tags_file": f"{PKG}/w18_tags.txt",
        "subs": {c: f"{subdir}/{YT5[c]}.srt" for c in ("ko", "en", "ja", "zh", "es")},
        "privacyStatus": "unlisted",
    }
    open(f"{PKG}/w18_{lang}_manifest.json", "w", encoding="utf-8").write(json.dumps(mf, ensure_ascii=False, indent=2))

print(f"패키지: {PKG}")
print(f"챕터(KO):\n{CH_KO}")
for c in ("ko", "en", "ja", "zh", "es"):
    t = open(f"{PKG}/{c}_title.txt", encoding="utf-8").read()
    print(f"  title[{c}] {len(t)}자")
