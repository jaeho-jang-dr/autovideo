#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
seed_curriculum.py — Hangeul 24-week (3 levels x 8 weeks) bilingual curriculum seeder.

What it does
------------
1. Creates `hangeul_curriculum` in BOTH backends and upserts the 24 enriched rows:
     - Supabase Postgres  (psycopg2, credentials from repo-root .env)   [best-effort]
     - channel/content.db (local SQLite, dev fallback / parity)         [always]
2. Writes a static JSON dump web/src/data/curriculum_fallback.json that the
   Astro site imports at build time.
"""
import json
import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SQLITE_DB = os.path.join(ROOT, "channel", "content.db")
JSON_OUT = os.path.join(ROOT, "web", "src", "data", "curriculum_fallback.json")

LEVELS = ["beginner", "intermediate", "advanced"]
LEVEL_KO = {"beginner": "초급", "intermediate": "중급", "advanced": "고급"}

# ---------------------------------------------------------------------------
# 24주 커리큘럼 (3단계/영문/타깃 자모 보강)
#   각 항목: (week, title_ko, title_en,
#             concept_ko, concept_en,            # 1단계 개념 이해(20분)
#             practice_ko, practice_en,          # 2단계 시청각/놀이 연습(20분)
#             application_ko, application_en,    # 3단계 실생활 적용(20분)
#             target_letters)
# ---------------------------------------------------------------------------
CURRICULUM = {
    "beginner": [
        (1, "한글의 탄생과 단모음", "Birth of Hangeul & Simple Vowels",
         "천·지·인 창제 원리를 소개하고 단모음 8개의 소릿값과 입모양을 익힙니다.",
         "Meet the heaven-earth-human design principle and learn the sound and mouth shape of the 8 simple vowels.",
         "엘코닌 음절 상자에 모음 블록을 끼우는 게임으로 모음 위치를 체득합니다.",
         "Drag-and-drop vowel blocks into the Elkonin syllable box to feel where each vowel sits.",
         "거울을 보며 단모음을 또박또박 소리 내고 입모양을 스스로 점검합니다.",
         "Say each simple vowel aloud in front of a mirror and self-check your mouth shape.",
         "ㅏ, ㅓ, ㅗ, ㅜ, ㅡ, ㅣ, ㅐ, ㅔ"),
        (2, "기초 자음과 모아쓰기", "Basic Consonants & Syllable Blocks",
         "발음 기관 상형 원리와 기초 자음 10자 및 모아쓰기(초성+중성) 구조를 학습합니다.",
         "Learn the voice-organ shape design, 10 basic consonants, and the initial-vowel block structure.",
         "자음과 모음을 합쳐 '나, 너, 고기, 사자, 하루' 같은 기초 단어를 조립합니다.",
         "Combine consonants and vowels into basic words like 나·너·고기·사자·하루 using blocks.",
         "플래시카드를 보고 배운 글자로 받침 없는 단어를 읽어 봅니다.",
         "Read open-syllable (no-batchim) words from flashcards using the letters you learned.",
         "ㄱ, ㄴ, ㅁ, ㅅ, ㅇ, ㄷ, ㄹ, ㅂ, ㅈ, ㅎ"),
        (3, "거센소리와 된소리", "Aspirated & Tense Consonants",
         "가획 원리에 따른 격음/경음 차이와 공기 압력/성대 긴장도를 학습합니다.",
         "Use the stroke-adding principle to compare the airflow of aspirated and tense consonants.",
         "휴지를 입 앞에 두고 'ㄱ-ㅋ-ㄲ' 최소대립쌍을 발음하며 차이를 눈으로 확인합니다.",
         "Hold a tissue in front of your mouth and pronounce minimal pairs like ㄱ-ㅋ-ㄲ to see the airflow difference.",
         "비슷한 소리 단어(개-캐-깨)를 듣고 받아쓰며 구분합니다.",
         "Listen to similar-sounding words (개-캐-깨) and distinguish them by dictation.",
         "ㅋ, ㅌ, ㅍ, ㅊ, ㄲ, ㄸ, ㅃ, ㅆ, ㅉ"),
        (4, "받침(종성)과 대표 7음", "Basic Batchim & 7 Representative Sounds",
         "종성(받침)의 배치 구조와 7개 대표 받침 소릿값 규칙을 이해합니다.",
         "Understand the final-consonant structure and the rule of the 7 representative batchim sounds.",
         "초성+중성 블록 아래에 받침 블록을 끼워 '가→강, 고→곰'으로 3단 조립합니다.",
         "Slide a final-consonant block under a syllable to assemble 3-tier blocks: 가→강, 고→곰.",
         "받침 노래를 따라 부르며 '공, 엄마, 밥, 물, 책'을 정확히 발음합니다.",
         "Sing along to the batchim song and pronounce 공·엄마·밥·물·책 accurately.",
         "ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅇ"),
        (5, "이중모음과 반모음 활주", "Double Vowels & Semivowel Glides",
         "단모음의 결합으로 만들어지는 이중모음 및 반모음 활주(Gliding) 조음 원리를 학습합니다.",
         "Learn how double vowels are formed and study semivowel gliding mechanics.",
         "'교실, 우유, 의자, 과자, 원숭이' 등의 단어 그림을 매칭하고 발음을 따라해 봅니다.",
         "Match double-vowel words like 교실·우유·의자·과자 to cards and practice their pronunciation.",
         "가족과 친구들의 이름에 들어간 이중모음을 찾아서 크게 발음해 봅니다.",
         "Find double vowels in the names of family or friends and say them out loud.",
         "야, 여, 요, 유, 와, 워, 위, 외, 의, 얘, 예"),
        (6, "자연스러운 연음과 음운 변동", "Liaison & Sound Rules",
         "자연스럽게 읽기 위한 연음 법칙과 받침 중화 규칙을 학습합니다.",
         "Learn the liaison rule and final-consonant neutralization rules for natural reading.",
         "받침이 다음 글자로 넘어가는 애니메이션을 보며 표기형과 발음형을 짝짓는 게임을 합니다.",
         "Watch a batchim slide into the next syllable and match the written vs. spoken forms (e.g. 음악->[으막]).",
         "짧은 문장을 표기대로/발음대로 두 번 읽어 차이를 느껴 봅니다.",
         "Read short sentences twice—as written and as pronounced—to feel the difference.",
         "연음, 대표음 중화, [으막], [우서요]"),
        (7, "필수 인사말과 자기소개", "Greetings & Self-Introduction",
         "필수 인사말과 국적, 이름, 직업을 넣은 자신감 있는 자기소개 문장을 학습합니다.",
         "Learn essential greetings and how to introduce yourself using name, nationality, and job.",
         "카드 뉴스 형태의 대화를 보며 가상의 인물로 자기소개 대화를 롤플레잉합니다.",
         "Practice conversational dialogues for meeting and introducing yourself using card flows.",
         "나의 이름, 국적, 직업을 포함하여 3문장으로 자기소개를 스피칭하고 기록합니다.",
         "Write and speak a 3-sentence self-introduction covering your name, nationality, and occupation.",
         "안녕하세요, 감사합니다, 반갑습니다"),
        (8, "숫자 표현과 날짜, 시간", "Numbers, Dates & Time",
         "고유어 숫자와 한자어 숫자의 쓰임 구분, 시간, 요일, 날짜 묻고 답하기를 학습합니다.",
         "Learn native vs. Sino-Korean numbers and how to ask/tell time, dates, and days.",
         "달력과 가상 시계 바늘을 이용한 시간 맞추기 퀴즈를 풀어 봅니다.",
         "Solve time-telling and day-matching quiz panels using calendars and virtual clocks.",
         "오늘 날짜와 현재 시각을 한국어로 쓰고 일과 말하기를 시작해 봅니다.",
         "Say and write today's date and the current time in Korean.",
         "하나~열, 일~십, 요일, 시간"),
    ],
    "intermediate": [
        (9, "우리 동네와 위치 표현", "Neighborhood & Locations",
         "우리 동네의 주요 장소와 물건의 위치(앞, 뒤, 옆, 위, 밑)를 설명하는 방법을 학습합니다.",
         "Learn key places in a neighborhood and how to describe locations of objects (front, back, side, top, bottom).",
         "지도 그림에서 핀을 꼽고 특정 위치를 묘사하는 인터랙티브 퍼즐을 풉니다.",
         "Solve interactive placement puzzles pointing to positions on a grid map.",
         "내 책상 위에 있는 여러 물건의 상대적 위치를 한국어 문장으로 적어 봅니다.",
         "Describe the positions of multiple items on your desk using Korean location sentences.",
         "앞, 뒤, 옆, 위, 밑, 마트, 학교"),
        (10, "상점 구매와 가격 묻기", "Shopping & Asking Prices",
         "가게에서 필요한 물건을 찾고, 가격을 묻고, 결제하는 실전 쇼핑 표현을 학습합니다.",
         "Learn practical conversation for asking prices in shops and ordering/paying at restaurants.",
         "가게 점원과 손님이 되어 결제 수단을 고르고 가격을 조율하는 역할극을 합니다.",
         "Play a shop clerk and customer role-playing game choosing methods of payment.",
         "마트나 옷 가게에서 물건을 살 때의 대화를 한국어로 작성해 봅니다.",
         "Draft a grocery or clothing shopping dialogue in Korean.",
         "얼마예요, 이거 주세요, 결제, 할인"),
        (11, "식당 이용과 맛 표현", "Food Ordering & Dining",
         "한국 식당에서 메뉴를 주문하고 맛(맵다, 달다, 짜다, 싱겁다)을 표현하는 회화를 학습합니다.",
         "Learn how to order food at Korean restaurants and describe tastes (spicy, sweet, salty, bland).",
         "식당 메뉴판 카드를 보며 음식 주문하기 및 맛 설명 매칭 퀴즈를 풉니다.",
         "Take food ordering and flavor-matching quizzes based on restaurant menus.",
         "가장 좋아하는 한국 음식을 골라 맛을 상세하게 묘사하는 대화 문장을 녹음합니다.",
         "Write and record dialogue lines ordering your favorite Korean food and describing its taste.",
         "주문할게요, 맛있어요, 매워요, 달아요"),
        (12, "교통수단과 지하철 환승", "Transportation & Subway Transfers",
         "버스, 지하철 등 대중교통 이용법과 노선도를 읽고 목적지까지 가기 위한 회화를 학습합니다.",
         "Learn how to use public transit and navigate routes/transfers using subway maps.",
         "지하철 노선도 그래픽을 보며 최적의 환승 경로를 안내하는 대화를 진행합니다.",
         "Role-play asking and answering transfer routes using a subway map.",
         "내 집에서 가고 싶은 서울 명소까지의 교통 경로를 한국어로 설명합니다.",
         "Explain the transportation route from your location to a Seoul landmark in Korean.",
         "버스, 지하철, 타다, 환승"),
        (13, "길 찾기와 위치 안내", "Directions & Wayfinding",
         "길을 잃었을 때 다른 사람에게 묻거나, 목적지까지의 방향을 친절하게 설명하는 표현을 학습합니다.",
         "Learn how to ask for directions or guide someone to a destination using directional terms.",
         "미로 찾기 형식의 맵 보드에서 음성 안내 힌트를 따라 목적지를 찾아냅니다.",
         "Find destinations on a maze board by following spoken direction clues.",
         "내 집 방에서 현관 입구까지 나가는 세부 길 안내를 구두로 진행해 봅니다.",
         "Explain a walking route from your room to the main entrance aloud.",
         "오른쪽, 왼쪽, 똑바로 가다, 건너다"),
        (14, "나의 하루 일과와 동작", "Daily Routines & Action Verbs",
         "아침에 일어나서 밤에 잠들 때까지의 일과를 시간 순서대로 묘사하는 연결 표현을 학습합니다.",
         "Learn how to describe daily schedules chronologically using common action verbs.",
         "하루 일과 동작 카드를 적합한 타임라인 블록 위에 배열하는 퍼즐을 풉니다.",
         "Align action cards onto a timeline to complete a standard daily routine game.",
         "나의 어제 하루 또는 오늘 보낸 일과표를 한국어 문장으로 작성해 소리 내어 맑게 읽습니다.",
         "Write down your daily routine in Korean sentences and read it clearly.",
         "일어나다, 공부하다, 일하다, 자다"),
        (15, "날씨와 아름다운 사계절", "Weather & Four Seasons",
         "한국 사계절의 특징과 매일의 날씨 상태를 기후 표현으로 묘사하는 법을 학습합니다.",
         "Learn about Korea's four seasons and how to describe daily weather conditions.",
         "일일 기상 캐스터가 되어 전국 기상 정보를 화면을 보며 예보해보는 상황극을 합니다.",
         "Role-play as a weather reporter presenting regional forecasts from a weather map.",
         "내가 가장 사랑하는 한국의 계절과 날씨 상태를 그 이유와 함께 한국어로 씁니다.",
         "Write about your favorite season and weather conditions, explaining why.",
         "맑음, 비, 눈, 춥다, 덥다, 사계절"),
        (16, "취미 생활과 빈도 묘사", "Hobbies & Frequency",
         "여가 시간에 주로 즐기는 활동(취미)과 빈도(자주, 가끔, 전혀)를 문장으로 표현하는 회화를 익힙니다.",
         "Learn hobbies and how to express their frequencies (often, sometimes, never).",
         "다양한 취미 액티비티 카드 덱에서 나와 짝의 공통 취미를 찾아내는 게임을 합니다.",
         "Play cards to identify shared hobbies and frequencies with your classmates.",
         "내가 즐겨 하는 취미를 상대에게 영어와 한국어로 자신 있게 소개하고 녹음해 봅니다.",
         "Record an introduction of your hobby and how often you practice it in Korean.",
         "영화 감상, 운동, 자주, 가끔, 좋아하다"),
    ],
    "advanced": [
        (17, "K-컬처와 실생활 구어", "K-Culture & Spoken Tones",
         "대중문화(K-POP, 드라마) 속 구어체 어조와 실생활 속 축약어, 친근한 반말 어미를 학습합니다.",
         "Learn informal spoken tones, K-Pop lyrics, K-Drama lines, and trendy modern slang.",
         "드라마 명대사를 배우의 호흡과 감정에 맞추어 더빙하듯 낭독 연습을 진행합니다.",
         "Read famous K-Drama dialogue scripts aloud, matching the actors' emotional pacing.",
         "한국 노래 가사 중 숨은 구어체 약어의 원래 형태를 복원하는 퀴즈를 풉니다.",
         "Decrypt spoken abbreviations in song lyrics back to their dictionary forms in a quiz.",
         "K-Drama, K-Pop, 반말, 축약어"),
        (18, "감정과 세밀한 마음 묘사", "Feelings & Emotional Nuances",
         "기쁨, 슬픔, 불안 등 사람이 느끼는 복잡한 마음을 적절한 형용사와 문맥으로 묘사합니다.",
         "Learn to express nuanced emotional states (joy, sadness, anxiety, frustration) in context.",
         "표정 일러스트와 정확한 한글 감정 묘사를 짝맞추는 카드 덱을 수행합니다.",
         "Match portrait illustrations with precise Korean emotional vocabulary.",
         "최근 일주일 동안 일상에서 겪은 감정 상태 변화를 한글로 가볍게 일기처럼 씁니다.",
         "Write a short diary entry describing your emotional changes over the past week.",
         "기쁘다, 슬프다, 긴장되다, 속상하다"),
        (19, "논리적 의견과 설득하기", "Opinions & Logical Arguments",
         "특정 사회 주제에 대해 찬반 의견을 펼치고 논리적 인과 표현(~고 생각해요, 왜냐하면)을 학습합니다.",
         "Learn to state pros/cons on topics and build logical flows using causative structures.",
         "제시된 토론 카드의 찬반 지문에 맞추어 3줄 요약 논리 구조를 완성하는 퍼즐을 풉니다.",
         "Complete 3-sentence logical debate scripts matching arguments and reasons.",
         "\"한국어를 학습하는 나의 목표\"에 대하여 논점과 이유를 엮어 1분 스피치 녹음을 완성합니다.",
         "Deliver and record a 1-minute speech stating your goals for learning Korean and your reasons.",
         "~고 생각해요, 왜냐하면, 따라서"),
        (20, "돌발 상황 대처와 문제 해결", "Emergencies & Troubleshooting",
         "약속을 변경하거나, 물건 분실, 서비스 고장 등 돌발상황에서 도움을 요청하는 긴급 회화를 배웁니다.",
         "Learn coping phrases for unexpected conflicts like schedule changes, lost property, or service issues.",
         "가상 전화 인터페이스를 열고 상담원에게 불만 사항을 전달하고 타협하는 시뮬레이션을 합니다.",
         "Simulate troubleshooting telephone calls to customer service regarding lost items.",
         "물건 분실 상황에서 경찰서나 관련 부서에 긴급 메일을 보내는 문장을 작성합니다.",
         "Write a formal emergency inquiry regarding a lost item to an official center.",
         "분실, 고장, 예약 변경, 긴급"),
        (21, "인물 묘사와 외모/성격", "Describing People & Personalities",
         "타인의 성격적 특징(외향적/내향적)과 외모(키, 눈매, 머리형)를 세밀하게 묘사하는 어휘를 배웁니다.",
         "Learn how to describe characters, appearances, and personality traits in detail.",
         "텍스트 힌트를 따라 몽타주 퍼즐을 매칭하여 가상의 범인을 추리하는 게임을 합니다.",
         "Match portrait options with description cards to identify a person of interest.",
         "자신의 롤모델이나 가장 친한 친구의 성격과 인상을 묘사하는 짧은 수필을 작성합니다.",
         "Write a short essay describing the personality and appearance of your role model.",
         "외모, 성격, 내향적, 외향적"),
        (22, "여행 경험과 미래 계획", "Travel Experiences & Plans",
         "과거에 다녀온 여행 경험(~해 본 적이 있다)과 미래의 여행 일정을 구체적으로 진술하는 법을 학습합니다.",
         "Learn to talk about past travel experiences and draft upcoming itineraries.",
         "여행 트렁크 그래픽에 준비물 품목 카드를 연결하고 일정을 맵에 배치하는 보드를 풉니다.",
         "Organize travel packing lists and map out routes on a virtual board game.",
         "과거 기억에 남는 최고의 명소 여행지를 친구에게 가이드 투어로 설명하듯 발표합니다.",
         "Deliver a short presentation recommending a past vacation destination to a friend.",
         "~한 적이 있어요, 여행, 계획"),
        (23, "모임 약속과 사회적 조율", "Social Planning & Agreements",
         "여러 사람의 일정을 조율하고 모임 시간과 장소를 제안하여 약속을 확정하는 표현을 익힙니다.",
         "Learn how to schedule meetings, suggest times/venues, and coordinate group appointments.",
         "캘린더 데이터가 다른 인물들의 빈 슬롯을 찾아 최적의 약속 시간을 결정하는 퍼즐을 풉니다.",
         "Solve meeting-slot conflicts to find the optimal date/time for a group gathering.",
         "한국인 지인이나 동료를 맛집 모임에 격식 있게 초대하는 한글 이메일 편지를 작성합니다.",
         "Write a formal gathering invitation email to a Korean colleague or friend.",
         "약속을 잡다, 시간 조율, 모임"),
        (24, "종합 진단과 수료 발표", "Wrap-up Diagnostic & Graduation",
         "24주간의 모든 과정을 총정리하고, 학습 성취를 돌아보며 최종 수료 소감을 한국어로 발표합니다.",
         "Summarize the entire 24-week curriculum, take the final diagnostic, and present a graduation speech.",
         "24주 전 범위 학습을 점검하는 최종 종합 인증 퀴즈 세트를 통과합니다.",
         "Take the comprehensive end-of-course assessment covering all 24 weeks.",
         "1분 분량의 과정 수료 소감 및 향후 목표를 한국어 멘트로 발표 녹음하여 완수합니다.",
         "Deliver a 1-minute speech in Korean sharing your graduation experience and future goals.",
         "수료, 발표, 최종 평가"),
    ],
}

FIELDS = [
    "level", "week", "title_ko", "title_en",
    "concept_ko", "concept_en", "practice_ko", "practice_en",
    "application_ko", "application_en", "target_letters",
]

LEVEL_REWARDS = {
    "beginner": {
        "ko": "한글 생존 배지 · 올바른 획순/연음 발음 애니메이션 가이드",
        "en": "Hangeul Survival Badge · stroke-order & liaison animation guides",
    },
    "intermediate": {
        "ko": "K-컬처 프리미엄 콘텐츠 해금 (웹툰 · 드라마 대사 · K-POP 비디오)",
        "en": "K-Culture premium unlocks (webtoons, drama lines & K-pop videos)",
    },
    "advanced": {
        "ko": "24주 수료증 다운로드 및 뽐내기 대회 온라인 출전권 제공",
        "en": "24-Week Graduation Certificate download & speech contest entry pass",
    },
}


def build_rows():
    rows = []
    for lvl in LEVELS:
        weeks = CURRICULUM[lvl]
        if len(weeks) != 8:
            raise ValueError(f"{lvl}: 8주가 아님 ({len(weeks)}주)")
        for tup in sorted(weeks, key=lambda t: t[0]):
            rows.append(dict(zip(FIELDS, (lvl,) + tup)))
    return rows


SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS hangeul_curriculum (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    level          TEXT NOT NULL,
    week           INTEGER NOT NULL,
    title_ko       TEXT NOT NULL,
    title_en       TEXT NOT NULL,
    concept_ko     TEXT NOT NULL,
    concept_en     TEXT NOT NULL,
    practice_ko    TEXT NOT NULL,
    practice_en    TEXT NOT NULL,
    application_ko TEXT NOT NULL,
    application_en TEXT NOT NULL,
    target_letters TEXT NOT NULL,
    created_at     TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(level, week)
);
"""


def seed_sqlite(rows):
    conn = sqlite3.connect(SQLITE_DB)
    conn.executescript(SQLITE_SCHEMA)
    cur = conn.cursor()
    # 청소 (24주 전용으로 변경되므로 기존의 행 전체 삭제)
    cur.execute("DELETE FROM hangeul_curriculum")
    
    cols = ", ".join(FIELDS)
    ph = ", ".join("?" for _ in FIELDS)
    sql = f"INSERT INTO hangeul_curriculum ({cols}) VALUES ({ph})"
    n = 0
    for r in rows:
        cur.execute(sql, [r[c] for c in FIELDS])
        n += 1
    conn.commit()
    per = {lvl: cur.execute("SELECT COUNT(*) FROM hangeul_curriculum WHERE level=?", (lvl,)).fetchone()[0] for lvl in LEVELS}
    total = cur.execute("SELECT COUNT(*) FROM hangeul_curriculum").fetchone()[0]
    conn.close()
    print(f"[SQLite] {SQLITE_DB}")
    print(f"  Cleaned and inserted {n} rows  |  table total {total}  "
          f"(beginner {per['beginner']}, intermediate {per['intermediate']}, advanced {per['advanced']})")
    return total


def seed_postgres(rows):
    try:
        import psycopg2
    except ImportError:
        print("[Supabase] psycopg2 미설치 — 건너뜀 (SQLite/JSON만 사용)")
        return None

    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, ".env"))
    except Exception:
        pass

    host = os.environ.get("SUPABASE_DB_HOST")
    if not host:
        print("[Supabase] SUPABASE_DB_* 환경변수 없음 — 건너뜀")
        return None

    migration = os.path.join(ROOT, "supabase", "migrations", "202606250000_create_hangeul_curriculum.sql")
    try:
        conn = psycopg2.connect(
            host=host,
            port=os.environ.get("SUPABASE_DB_PORT", "5432"),
            user=os.environ.get("SUPABASE_DB_USER"),
            password=os.environ.get("SUPABASE_DB_PASSWORD"),
            dbname=os.environ.get("SUPABASE_DB_NAME", "postgres"),
            sslmode="require",
            connect_timeout=15,
        )
    except Exception as e:
        print(f"[Supabase] 연결 실패 — 건너뜀: {type(e).__name__}: {e}")
        return None

    try:
        conn.autocommit = True
        cur = conn.cursor()
        if os.path.exists(migration):
            with open(migration, encoding="utf-8") as f:
                cur.execute(f.read())
            print(f"[Supabase] migration applied: {os.path.basename(migration)}")
        
        # 청소
        cur.execute("DELETE FROM hangeul_curriculum")
        
        cols = ", ".join(FIELDS)
        ph = ", ".join("%s" for _ in FIELDS)
        sql = f"INSERT INTO hangeul_curriculum ({cols}) VALUES ({ph})"
        n = 0
        for r in rows:
            cur.execute(sql, [r[c] for c in FIELDS])
            n += 1
        cur.execute("SELECT level, COUNT(*) FROM hangeul_curriculum GROUP BY level")
        per = dict(cur.fetchall())
        cur.execute("SELECT COUNT(*) FROM hangeul_curriculum")
        total = cur.fetchone()[0]
        print(f"[Supabase] {host}")
        print(f"  Cleaned and inserted {n} rows  |  table total {total}  "
              f"(beginner {per.get('beginner', 0)}, intermediate {per.get('intermediate', 0)}, "
              f"advanced {per.get('advanced', 0)})")
        return total
    except Exception as e:
        print(f"[Supabase] 시드 중 오류 — 건너뜀: {type(e).__name__}: {e}")
        return None
    finally:
        conn.close()


def write_json(rows):
    data = {
        "generated_from": "24-Week Compacted Fast-Track",
        "structure": "Daily 1 hour = Concept(20m) + Interactive Practice(20m) + Real-life Application(20m)",
        "levels": LEVELS,
        "level_ko": LEVEL_KO,
        "rewards": LEVEL_REWARDS,
        "counts": {lvl: sum(1 for r in rows if r["level"] == lvl) for lvl in LEVELS},
        "weeks": rows,
    }
    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[JSON] {os.path.relpath(JSON_OUT, ROOT)}  ({len(rows)} weeks)")


def main():
    print("=" * 70)
    print("  Hangeul 24-week Curriculum Seeder (Fast-Track)")
    print("=" * 70)

    rows = build_rows()
    print(f"[Build] {len(rows)} rows (3 levels x 8 weeks = 24 weeks total)")

    seed_sqlite(rows)
    seed_postgres(rows)
    write_json(rows)

    print("=" * 70)
    print("  완료: SQLite + (Supabase best-effort) + JSON 덤프")
    print("=" * 70)


if __name__ == "__main__":
    main()
