# -*- coding: utf-8 -*-
"""W13 업로드 패키지 — 제목·설명(챕터 자동)·태그·고정댓글. w12pkg 형식 그대로."""
import os, json

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w13pkg"
os.makedirs(PKG, exist_ok=True)
TL = "hangeul_birth_vowels/hangeul_w13_jieun_np_timeline.json"

CHAPTERS = [
    (1,  "성산일출봉 도착 · 길을 잃었어요", "Arriving at Seongsan - I'm lost"),
    (5,  "실례합니다 · 길 좀 물어봐도 돼요?", "Excuse me - May I ask for directions?"),
    (9,  "★ 오른쪽 · 왼쪽",                  "Right & Left"),
    (13, "다시 말해 주세요 · 천천히",        "Please say that again / slowly"),
    (15, "★ 똑바로 가다 · 건너다",           "Go straight & Cross"),
    (21, "사거리 · 신호등 · 편의점 기준",    "Landmarks - intersection, light, store"),
    (25, "거리와 위치 · 얼마나 멀어요?",     "Distance & Position"),
    (33, "일출봉 오르기 · 다 왔어요!",       "Climbing to the top"),
    (39, "이번엔 내가 안내!",                "Now I give directions!"),
    (43, "오늘의 표현 정리",                 "Today's phrases"),
]

def ts(sec):
    m, s = int(sec // 60), int(sec % 60)
    return f"{m}:{s:02d}"

chap_ko, chap_en = [], []
if os.path.exists(TL):
    tl = json.load(open(TL, encoding="utf-8"))
    starts, t = {}, 0.0
    for sc in tl["scenes"]:
        starts[sc["seq"]] = t; t += sc["dur"]
    for seq, ko, en in CHAPTERS:
        st = starts.get(seq, 0)
        chap_ko.append(f"{ts(st)} {ko}")
        chap_en.append(f"{ts(st)} {en}")
else:
    print("⚠️ 타임라인 없음 — 최종 렌더 후 재실행")

KO_TITLE = "길 찾기 한국어 - 오른쪽·왼쪽·똑바로 총정리 | 한글 배우기 W13 (제주 성산일출봉)"
EN_TITLE = "Korean Directions - Right, Left & Go Straight | Learn Korean W13 (Jeju)"

AI_KO = "🤖 이 영상의 배경·캐릭터 이미지는 AI(Google Gemini)로 생성·연출했고, 나레이션은 AI 음성(Microsoft Azure TTS)입니다."
AI_EN = "🤖 Backgrounds and characters in this video were generated with AI (Google Gemini); narration uses AI speech (Microsoft Azure TTS)."

KO_DESC = f"""한국에서 길을 묻고 안내하는 법을 배웁니다 — 제주 성산일출봉을 함께 걸으며 배워요.
길을 잃었을 때 묻는 법, 오른쪽·왼쪽·똑바로 같은 방향 표현, 못 알아들었을 때 다시 물어보는 법,
거리와 위치를 말하는 법, 그리고 마지막엔 여러분이 직접 남에게 길을 안내합니다.
지은과 함께 따라 하면 한국 어디서도 길을 잃지 않아요. 초보자 환영!

📚 오늘 배우는 핵심 표현
여기가 어디예요? · 길을 잃었어요 · 실례합니다 · 길 좀 물어봐도 돼요? · 어떻게 가요? · 오른쪽 · 왼쪽 · 오른쪽으로 가세요 · 다시 말해 주세요 · 천천히 말해 주세요 · 똑바로 가세요 · 쭉 가세요 · 건너다 · 길을 건너세요 · 돌다 · 오른쪽으로 도세요 · 사거리 · 신호등 · 편의점에서 오른쪽으로 가세요 · 알겠어요 · 얼마나 멀어요? · 가까워요 · 멀어요 · 근처 · 앞 · 뒤 · 옆 · 사이 · 올라가다 · 내려가다 · 다 왔어요

⏱️ 챕터
{chr(10).join(chap_ko)}

🎧 자막 5개 국어(한국어·English·日本語·中文·Español)를 켜고 보세요.
🇰🇷 한국어 오디오 버전입니다. 영어 나레이션 버전은 채널에서 확인하세요.

{AI_KO}

🔗 더 많은 한국어 강의: https://drjayed.com
"""

EN_DESC = f"""Learn how to ask for and give directions in Korean — while walking around Seongsan Ilchulbong in Jeju.
How to ask when you're lost, direction words like right/left/straight, how to ask someone to repeat slowly,
how to talk about distance and position, and finally — you give directions to someone else.
Follow Jieun and you'll never be lost in Korea again. Beginners welcome!

📚 Key phrases in this lesson
여기가 어디예요? (Where am I?) · 길을 잃었어요 (I'm lost) · 실례합니다 (Excuse me) · 길 좀 물어봐도 돼요? (May I ask directions?) · 오른쪽 (right) · 왼쪽 (left) · 다시 말해 주세요 (Say that again) · 천천히 말해 주세요 (Speak slowly) · 똑바로 가세요 (Go straight) · 건너다 (to cross) · 돌다 (to turn) · 사거리 (intersection) · 신호등 (traffic light) · 얼마나 멀어요? (How far?) · 가까워요 / 멀어요 (near/far) · 근처 (nearby) · 앞/뒤/옆/사이 (front/back/beside/between) · 올라가다 / 내려가다 (go up/down)

⏱️ Chapters
{chr(10).join(chap_en)}

🎧 Turn on subtitles — available in Korean, English, Japanese, Chinese and Spanish.
🇺🇸 This is the English-audio version. A Korean-audio version is also on the channel.

{AI_EN}

🔗 More Korean lessons: https://drjayed.com
"""

TAGS = ("한국어,한글,Learn Korean,Korean lesson,길 찾기,방향 한국어,한국어 회화,Korean directions,"
        "ask directions Korean,Korean phrases,right left Korean,go straight Korean,오른쪽,왼쪽,똑바로,"
        "Korean for beginners,learn hangul,travel Korean,Jeju,제주도,성산일출봉,Seongsan Ilchulbong,"
        "한국어 공부,Korea travel,韓国語,韓国語勉強,韓国語会話,ハングル,道案内,韓国旅行,済州島,"
        "学韩语,韩语,韩语会话,问路,韩国旅游,济州岛,"
        "aprender coreano,coreano para principiantes,direcciones en coreano,viajar Corea")

def w(name, text):
    open(os.path.join(PKG, name), "w", encoding="utf-8").write(text.strip() + "\n")

w("ko_title.txt", KO_TITLE)
w("en_title.txt", EN_TITLE)
w("ko_desc.txt", KO_DESC)
w("en_desc.txt", EN_DESC)
w("w13_tags.txt", TAGS)
w("ko_comment.txt", "🧭 제주 성산일출봉에서 길 찾기 한국어를 배워요! 오른쪽·왼쪽·똑바로·건너다, 그리고 못 알아들었을 때 쓰는 '다시 말해 주세요'까지. 마지막엔 여러분이 직접 길을 안내합니다! 자막은 한국어·English·日本語·中文·Español 5개 언어로 켤 수 있어요. 한국에서 길을 잃어본 적 있나요? 댓글로 알려주세요 👇")
w("en_comment.txt", "🧭 Learn Korean directions at Seongsan Ilchulbong, Jeju! Right, left, go straight, cross — plus the lifesaver phrase '다시 말해 주세요' (Please say that again). And at the end, YOU give the directions! Subtitles in English · 한국어 · 日本語 · 中文 · Español. Ever gotten lost in Korea? Tell us below 👇")

tl_ = [t.strip() for t in TAGS.split(",") if t.strip()]
total = sum(len(t) + 2 if " " in t else len(t) for t in tl_) + (len(tl_) - 1)
print(f"패키지: {PKG}")
print(f"  제목 KO {len(KO_TITLE)}자 / EN {len(EN_TITLE)}자")
print(f"  태그 {len(tl_)}개 / ~{total}자 (≤500)")
print(f"  챕터 {len(chap_ko)}개 {'✅' if chap_ko else '⚠️ 타임라인 필요'}")
