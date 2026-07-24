# -*- coding: utf-8 -*-
"""W12 업로드 패키지 생성 — 제목·설명(챕터 자동)·태그·매니페스트. w11pkg 형식 그대로.
사용: python build_w12pkg.py   (최종 렌더 후 타임라인 json 필요)"""
import os, json

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w12pkg"
os.makedirs(PKG, exist_ok=True)
TL = "hangeul_birth_vowels/hangeul_w12_injun_np_timeline.json"

# ---------- 챕터: 막 시작 씬 → 실제 타임스탬프 ----------
CHAPTERS = [  # (시작 씬번호, 한글 제목, 영어 제목)
    (1,  "인천공항 도착 · 어떻게 가요?", "Arriving at Incheon Airport"),
    (6,  "공항버스 · 몇 번 버스예요?",   "Airport Bus - Which bus number?"),
    (13, "교통카드 · 충전하기",          "Transit Card & Top-up"),
    (19, "공항철도 타기 · 이거 서울역 가요?", "Riding the Airport Railroad"),
    (27, "★ 서울역 환승 · 갈아타다",     "Transferring at Seoul Station"),
    (37, "강남역 도착 · 몇 번 출구예요?", "Arriving at Gangnam - Which exit?"),
    (43, "오늘의 표현 정리",             "Today's Phrases"),
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
    print("⚠️ 타임라인 없음 — 챕터 시간 비워둠(최종 렌더 후 재실행)")

KO_TITLE = "지하철·버스 한국어 - 교통카드·환승·출구 총정리 | 한글 배우기 W12 (인천공항→강남역)"
EN_TITLE = "Korean Subway & Bus - Transit Card, Transfer & Exits | Learn Korean W12"

AI_KO = "🤖 이 영상의 배경·캐릭터 이미지는 AI(Google Gemini/Veo·Flow)로 생성·연출했고, 나레이션은 AI 음성(Microsoft Azure TTS)입니다."
AI_EN = "🤖 Backgrounds and characters in this video were generated with AI (Google Gemini/Veo, Flow); narration uses AI speech (Microsoft Azure TTS)."

KO_DESC = f"""한국에서 대중교통 타는 법을 한국어로 배웁니다 — 인천공항에서 강남역까지 실제로 이동하며 배워요.
공항버스와 지하철 비교, 교통카드 충전, 반대 방향 안 타는 법, 서울역 환승, 강남역 출구 찾기까지.
관광가이드 인준과 함께 따라 하면 서울에서 길 잃지 않아요. 한국 여행·유학·일상 실전 회화. 초보자 환영!

📚 오늘 배우는 핵심 표현
어떻게 가요? · 서울까지 어떻게 가요? · 타다 · 버스 · 지하철 · 정류장 · 몇 번 버스예요? · 얼마나 걸려요? · 요금이 얼마예요? · 교통카드 주세요 · 충전 · 카드를 대세요 · 서울역행 · 이거 서울역 가요? · 손잡이 · 몇 정거장이에요? · 환승 · 갈아타다 · 어디서 갈아타요? · 2호선 · 내리다 · 몇 번 출구예요?

⏱️ 챕터
{chr(10).join(chap_ko)}

🎧 자막 5개 국어(한국어·English·日本語·中文·Español)를 켜고 보세요.
🇰🇷 한국어 오디오 버전입니다. 영어 나레이션 버전은 채널에서 확인하세요.

{AI_KO}

🔗 더 많은 한국어 강의: https://drjayed.com
"""

EN_DESC = f"""Learn how to use public transport in Korea — we actually travel from Incheon Airport to Gangnam Station.
Airport bus vs subway, buying and charging a transit card, avoiding the wrong direction, transferring at Seoul Station, and finding the right exit at Gangnam.
Follow your guide Injun and you'll never get lost in Seoul. Real, practical Korean for travel, study and daily life. Beginners welcome!

📚 Key phrases in this lesson
어떻게 가요? (How do I get there?) · 타다 (to ride) · 버스 (bus) · 지하철 (subway) · 정류장 (bus stop) · 몇 번 버스예요? (Which bus number?) · 얼마나 걸려요? (How long?) · 요금 (fare) · 교통카드 주세요 (A transit card, please) · 충전 (top up) · 카드를 대세요 (Tap your card) · 이거 서울역 가요? (Does this go to Seoul Station?) · 손잡이 (strap) · 환승 (transfer) · 갈아타다 (to change trains) · 2호선 (Line 2) · 내리다 (to get off) · 몇 번 출구예요? (Which exit?)

⏱️ Chapters
{chr(10).join(chap_en)}

🎧 Turn on subtitles — available in Korean, English, Japanese, Chinese and Spanish.
🇺🇸 This is the English-audio version. A Korean-audio version is also on the channel.

{AI_EN}

🔗 More Korean lessons: https://drjayed.com
"""

TAGS = ("한국어,한글,Learn Korean,Korean lesson,지하철 한국어,한국어 회화,Korean subway,Seoul subway,"
        "subway transfer,transit card,Korean transportation,Incheon airport to Seoul,Gangnam station,"
        "환승,교통카드,지하철 타는 법,Korean for beginners,learn hangul,travel Korean,Korean phrases,"
        "한국어 공부,韓国語,韓国語勉強,韓国語会話,ハングル,韓国地下鉄,乗り換え,韓国旅行,"
        "学韩语,韩语,韩语会话,韩国地铁,换乘,韩国旅游,"
        "aprender coreano,coreano para principiantes,metro de Seul,transporte Corea")

def w(name, text):
    open(os.path.join(PKG, name), "w", encoding="utf-8").write(text.strip() + "\n")

w("ko_title.txt", KO_TITLE)
w("en_title.txt", EN_TITLE)
w("ko_desc.txt", KO_DESC)
w("en_desc.txt", EN_DESC)
w("w12_tags.txt", TAGS)
w("ko_comment.txt", "🚇 인천공항에서 강남역까지, 한국어로 대중교통 타는 법을 전부 담았어요! 교통카드·환승·출구까지 이 영상 하나면 서울에서 길 잃지 않습니다. 자막은 한국어·English·日本語·中文·Español 5개 언어로 켤 수 있어요. 여러분은 한국에서 어디를 가장 가고 싶나요? 댓글로 알려주세요 👇")
w("en_comment.txt", "🚇 From Incheon Airport all the way to Gangnam — everything you need to ride Korean public transport in Korean! Transit card, transfers, exits. Subtitles in English · 한국어 · 日本語 · 中文 · Español. Where in Korea do you most want to go? Tell us below 👇")

# 태그 글자수(YouTube 계산법: 띄어쓰기 있으면 +2)
tl_ = [t.strip() for t in TAGS.split(",") if t.strip()]
total = sum(len(t) + 2 if " " in t else len(t) for t in tl_) + (len(tl_) - 1)
print(f"패키지 생성: {PKG}")
print(f"  제목 KO: {KO_TITLE[:50]}… ({len(KO_TITLE)}자)")
print(f"  제목 EN: {EN_TITLE[:50]}… ({len(EN_TITLE)}자)")
print(f"  태그: {len(tl_)}개 / 약 {total}자 (목표 ~490)")
print(f"  챕터: {len(chap_ko)}개 {'✅' if chap_ko else '⚠️ 타임라인 필요'}")
