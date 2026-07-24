# -*- coding: utf-8 -*-
"""W15 업로드 패키지 — 제목·설명(5개 언어) + 태그 + 챕터 + 매니페스트.
   ★이번엔 자막을 API로 올린다(사장님 지시) → 매니페스트 subs에 5개 언어 srt 경로 포함."""
import os, json
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w15pkg"
os.makedirs(PKG, exist_ok=True)

CH_KO = """0:00 한라산과 사계절 소개
1:14 봄 · 따뜻하다 · 꽃이 피다 · 선작지왓
2:58 여름 · 덥다 · 장마 · 소나기 · 돈내코
5:09 가을 · 단풍 · 하늘이 높다 · 영실기암
6:59 겨울 · 춥다 · 눈 · 첫눈 · 상고대
8:50 방한복 · 백록담 설경
9:33 사계절 복습"""
CH_EN = """0:00 Intro: Hallasan & the four seasons
1:14 Spring · warm · flowers bloom · Seonjakjiwat
2:58 Summer · hot · rainy season · Donnaeko
5:09 Autumn · foliage · high sky · Yeongsil rocks
6:59 Winter · cold · snow · first snow · frost
8:50 Winter gear · Baengnokdam snowscape
9:33 Four-season review"""

AI_KO = "\n🤖 제작 안내\n이 영상의 이미지·연출은 Google Gemini(Nano Banana)로 생성했고, 나레이션은 Microsoft Azure TTS(선희·Emma)로 만들었습니다.\n\n🌐 drjayed.com\n"
AI_EN = "\n🤖 Production note\nVisuals were generated with Google Gemini (Nano Banana); narration was created with Microsoft Azure TTS (SunHi & Emma).\n\n🌐 drjayed.com\n"

KEY_KO = ("날씨 · 날씨가 어때요? · 사계절 · 봄 · 여름 · 가을 · 겨울 · 따뜻하다 · 덥다 · 시원하다 · 춥다 · "
          "맑다 · 흐리다 · 비가 오다 · 눈이 오다 · 바람이 불다 · 습하다 · 건조하다 · 꽃이 피다 · 벚꽃 · "
          "단풍 · 단풍이 들다 · 낙엽 · 억새 · 장마 · 소나기 · 우비 · 우산 · 첫눈 · 눈사람 · 눈싸움 · 얼다 · "
          "영하 · 상고대 · 소풍 · 선작지왓 · 사라오름 · 돈내코 · 영실기암 · 어리목 · 백록담 · 한라산")
KEY_EN = ("날씨 (weather) · 사계절 (four seasons) · 봄 (spring) · 여름 (summer) · 가을 (autumn) · 겨울 (winter) · "
          "따뜻하다 (warm) · 덥다 (hot) · 시원하다 (cool) · 춥다 (cold) · 비가 오다 (rain) · 눈이 오다 (snow) · "
          "바람이 불다 (windy) · 꽃이 피다 (bloom) · 단풍 (foliage) · 첫눈 (first snow) · 눈사람 (snowman) · "
          "Hallasan · Seonjakjiwat · Saraoreum · Baengnokdam")

TITLES = {
    "ko": "날씨와 사계절 한국어 - 봄·여름·가을·겨울 총정리 | 한글 배우기 W15 (제주 한라산)",
    "en": "Korean Weather & Four Seasons - Spring, Summer, Fall, Winter | Learn Korean W15 (Hallasan)",
    "ja": "韓国語で天気と四季: 春・夏・秋・冬 | 韓国語学習 W15 (漢拏山)",
    "zh": "韩语天气与四季: 春夏秋冬 | 韩语学习 W15 (汉拿山)",
    "es": "Clima y las Cuatro Estaciones en Coreano: Primavera, Verano, Otoño, Invierno | Aprende Coreano W15",
}
DESCS = {
    "ko": f"""한국의 날씨와 사계절을 한국어로 배웁니다 — 제주 한라산에서 봄·여름·가을·겨울을 한 바퀴 돌아요.
따뜻한 봄의 선작지왓 산철쭉, 시원한 여름의 돈내코 계곡, 붉게 물든 가을의 영실기암, 눈 덮인 겨울의 백록담까지.
날씨 표현(맑다·비가 오다·눈이 오다·바람이 불다)과 계절 형용사(따뜻하다·덥다·시원하다·춥다)를 자연스럽게 익혀요.
지은과 함께 한라산 사계절을 여행하며 배워요. 초보자 환영!

📚 오늘 배우는 핵심 표현
{KEY_KO}

⏱️ 챕터
{CH_KO}
{AI_KO}""",
    "en": f"""Learn Korean weather and the four seasons — traveling through spring, summer, autumn, and winter on Hallasan, Jeju.
From spring azaleas at Seonjakjiwat, to the cool Donnaeko valley in summer, red foliage at Yeongsil in autumn, and snow-covered Baengnokdam in winter.
You'll pick up weather expressions (clear, rain, snow, windy) and seasonal adjectives (warm, hot, cool, cold) naturally.
Travel Hallasan's four seasons with Jieun. Beginners welcome!

📚 Key expressions
{KEY_EN}

⏱️ Chapters
{CH_EN}
{AI_EN}""",
    "ja": f"""韓国語で天気と四季を学びます — 済州の漢拏山（ハルラサン）で春・夏・秋・冬を一巡り。
春のソンジャクジワッのツツジ、夏のトンネコ渓谷、秋のヨンシル奇岩の紅葉、冬の白鹿潭の雪景色まで。
天気の表現と季節の形容詞を自然に覚えられます。チウンと一緒に漢拏山の四季を旅しましょう。初心者歓迎！

📚 重要表現
{KEY_EN}

⏱️ チャプター
{CH_EN}
{AI_EN}""",
    "zh": f"""用韩语学习天气与四季 — 在济州汉拿山，走过春夏秋冬。
从春天先作旨田的杜鹃，到夏天顿乃谷溪谷，秋天灵室奇岩的红叶，冬天白鹿潭的雪景。
自然地掌握天气表达与季节形容词。和智恩一起游览汉拿山的四季。欢迎初学者！

📚 重点表达
{KEY_EN}

⏱️ 章节
{CH_EN}
{AI_EN}""",
    "es": f"""Aprende el clima y las cuatro estaciones en coreano — recorriendo primavera, verano, otoño e invierno en Hallasan, Jeju.
Desde las azaleas de Seonjakjiwat en primavera, el valle Donnaeko en verano, el follaje rojo de Yeongsil en otoño, hasta el Baengnokdam nevado en invierno.
Aprenderás expresiones del clima y adjetivos de estación de forma natural. Viaja por las cuatro estaciones con Jieun. ¡Principiantes bienvenidos!

📚 Expresiones clave
{KEY_EN}

⏱️ Capítulos
{CH_EN}
{AI_EN}""",
}
TAGS = ("한국어 배우기,한글 배우기,korean weather,four seasons korea,learn korean,korean for beginners,"
        "날씨,사계절,계절,korean seasons,korean adjectives,봄 여름 가을 겨울,제주,한라산,hallasan,jeju,"
        "korean vocabulary,korean lesson,speak korean,drjayed")

for c, t in TITLES.items(): open(f"{PKG}/{c}_title.txt","w",encoding="utf-8").write(t)
for c, dd in DESCS.items(): open(f"{PKG}/{c}_desc.txt","w",encoding="utf-8").write(dd)
open(f"{PKG}/w15_tags.txt","w",encoding="utf-8").write(TAGS)

# 매니페스트 — ★자막 API 업로드(subs 채움)
YT5 = {"ko":"한국어","en":"영어","ja":"일본어","zh":"중국어(중국)","es":"스페인어"}
for lang in ("ko","en"):
    subdir = f"subs_upload/W15_{'1_한글판' if lang=='ko' else '2_영어판'}"
    mf = {
        "week":"W15","lang":lang,
        "video":f"hangeul_birth_vowels/hangeul_w15_jieun_np_{lang}.mp4",
        "thumbnail":f"hangeul_birth_vowels/thumb_w15_{lang}_1280x720.jpg",
        "defaultLanguage": lang,
        "title": TITLES[lang], "description": DESCS[lang],
        "localizations": {c:{"title":TITLES[c],"description":DESCS[c]} for c in ("ko","en","ja","zh","es")},
        "tags_file": f"{PKG}/w15_tags.txt",
        "subs": {c: f"{subdir}/{YT5[c]}.srt" for c in ("ko","en","ja","zh","es")},   # ★API 업로드
        "privacyStatus":"unlisted",
    }
    open(f"{PKG}/w15_{lang}_manifest.json","w",encoding="utf-8").write(json.dumps(mf,ensure_ascii=False,indent=2))

print(f"패키지: {PKG}")
for f in sorted(os.listdir(PKG)): print(f"  {f}")
