#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
seed_curriculum.py — Hangeul 36-week (3 levels x 12 weeks) bilingual curriculum seeder.

What it does
------------
1. Parses the canonical week titles out of the source plan
   (scratch/found_curriculum_073ae673-b8ee-4586-b9c2-f4f12e7276a1.md) and
   cross-checks that all 36 weeks (12 x beginner/intermediate/advanced) are present.
2. Creates `hangeul_curriculum` in BOTH backends and upserts the 36 enriched rows:
     - Supabase Postgres  (psycopg2, credentials from repo-root .env)   [best-effort]
     - channel/content.db (local SQLite, dev fallback / parity)         [always]
3. Writes a static JSON dump web/src/data/curriculum_fallback.json that the
   Astro site imports at build time and the /api/curriculum route serves as a
   fallback when Supabase is unreachable.

The source plan gives the Korean week titles and the per-week learning focus, plus
the "daily 1-hour = Concept(20m) + Interactive Practice(20m) + Real-life Application(20m)"
structure. The English copy, the explicit 3-step split and the per-week `target_letters`
are derived from that plan and recorded here as the single source of truth for seeding.

Usage:
    python scripts/seed_curriculum.py
"""
import json
import os
import re
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOURCE_MD = os.path.join(ROOT, "scratch", "found_curriculum_073ae673-b8ee-4586-b9c2-f4f12e7276a1.md")
SQLITE_DB = os.path.join(ROOT, "channel", "content.db")
JSON_OUT = os.path.join(ROOT, "web", "src", "data", "curriculum_fallback.json")

LEVELS = ["beginner", "intermediate", "advanced"]
LEVEL_KO = {"beginner": "초급", "intermediate": "중급", "advanced": "고급"}

# 소스 플랜의 레벨 헤더 마커 -> 내부 레벨 키 (해당 마커 뒤의 'N주 차:' 라인이 그 레벨에 속함)
LEVEL_MARKERS = [
    ("🌟 초급반", "beginner"),
    ("🌟 중급반", "intermediate"),
    ("🌟 고급반", "advanced"),
]

# ---------------------------------------------------------------------------
# 36주 커리큘럼 (소스 플랜 기반 + 3단계/영문/타깃 자모 보강)
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
         "엘코닌 음절 상자에 모음 블록을 끼우는 드래그&드롭 게임으로 모음 위치를 체득합니다.",
         "Drag-and-drop vowel blocks into the Elkonin syllable box to feel where each vowel sits.",
         "거울을 보며 단모음을 또박또박 소리 내고 입모양을 스스로 점검합니다.",
         "Say each simple vowel aloud in front of a mirror and self-check your mouth shape.",
         "ㅏ, ㅓ, ㅗ, ㅜ, ㅡ, ㅣ, ㅐ, ㅔ"),
        (2, "이중모음과 기초 자음 (1)", "Diphthongs & Basic Consonants (1)",
         "이중모음(ㅑ·ㅕ·ㅛ·ㅠ)과 기본 자음 ㄱ·ㄴ·ㄷ·ㄹ·ㅁ을 학습합니다.",
         "Learn the y-glide diphthongs (ㅑ·ㅕ·ㅛ·ㅠ) and the basic consonants ㄱ·ㄴ·ㄷ·ㄹ·ㅁ.",
         "자음과 모음을 합쳐 '나·너·고기·구두' 같은 기초 어휘를 블록으로 조립합니다.",
         "Combine consonants and vowels into basic words like 나·너·고기·구두 using the block builder.",
         "플래시카드를 보고 배운 글자로 받침 없는 단어를 읽어 봅니다.",
         "Read open-syllable (no-batchim) words from flashcards using the letters you learned.",
         "ㅑ, ㅕ, ㅛ, ㅠ, ㄱ, ㄴ, ㄷ, ㄹ, ㅁ"),
        (3, "기초 자음 (2)와 단어 확장", "Basic Consonants (2) & Word Building",
         "기본 자음 ㅂ·ㅅ·ㅇ·ㅈ·ㅎ을 익히고 단어를 확장합니다.",
         "Learn the basic consonants ㅂ·ㅅ·ㅇ·ㅈ·ㅎ and expand your vocabulary.",
         "'아이·여우·오이·우유' 등 친숙한 단어를 플래시카드와 그림자 맞추기로 연습합니다.",
         "Practice familiar words like 아이·여우·오이·우유 with flashcards and shadow-matching games.",
         "배운 자음으로 주변 사물의 이름을 한 단어씩 적어 봅니다.",
         "Write down the names of objects around you, one word at a time, using the new consonants.",
         "ㅂ, ㅅ, ㅇ, ㅈ, ㅎ"),
        (4, "거센소리와 된소리", "Aspirated & Tense Consonants",
         "가획 원리로 거센소리(ㅋ·ㅌ·ㅍ·ㅊ)와 된소리(ㄲ·ㄸ·ㅃ·ㅆ·ㅉ)의 공기 세기 차이를 비교합니다.",
         "Use the stroke-adding principle to compare the airflow of aspirated (ㅋ·ㅌ·ㅍ·ㅊ) and tense (ㄲ·ㄸ·ㅃ·ㅆ·ㅉ) consonants.",
         "휴지를 입 앞에 두고 'ㄱ-ㅋ-ㄲ' 최소대립쌍을 발음하며 떨림 차이를 눈으로 확인합니다.",
         "Hold a tissue in front of your mouth and pronounce minimal pairs like ㄱ-ㅋ-ㄲ to see the airflow difference.",
         "비슷한 소리 단어(개-캐-깨)를 듣고 받아쓰며 구분합니다.",
         "Listen to similar-sounding words (개-캐-깨) and distinguish them by dictation.",
         "ㅋ, ㅌ, ㅍ, ㅊ, ㄲ, ㄸ, ㅃ, ㅆ, ㅉ"),
        (5, "받침(종성)의 이해", "Understanding Batchim (Final Consonants)",
         "한글의 7개 대표 받침소리(ㄱ·ㄴ·ㄷ·ㄹ·ㅁ·ㅂ·ㅇ) 규칙을 이해합니다.",
         "Understand the rule of the 7 representative batchim sounds (ㄱ·ㄴ·ㄷ·ㄹ·ㅁ·ㅂ·ㅇ).",
         "초성+중성 블록 아래에 받침 블록을 끼워 '가→강, 고→곰'으로 3단 조립합니다.",
         "Slide a final-consonant block under a syllable to assemble 3-tier blocks: 가→강, 고→곰.",
         "받침 노래를 따라 부르며 '공·엄마·밥'을 정확히 발음합니다.",
         "Sing along to the batchim song and pronounce 공·엄마·밥 accurately.",
         "받침 ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅇ"),
        (6, "기초 음운 규칙과 연음", "Basic Sound Rules & Liaison",
         "자연스럽게 읽기 위한 연음 법칙을 학습합니다(예: 음악[으막], 웃어요[우서요]).",
         "Learn the liaison rule for natural reading (e.g., 음악→[으막], 웃어요→[우서요]).",
         "받침이 다음 글자로 넘어가는 애니메이션을 보며 표기형과 발음형을 짝짓는 게임을 합니다.",
         "Watch a batchim slide into the next syllable and match the written vs. spoken forms in a game.",
         "짧은 문장을 표기대로/발음대로 두 번 읽어 차이를 느껴 봅니다.",
         "Read short sentences twice—as written and as pronounced—to feel the difference.",
         "연음, [으막], [우서요]"),
        (7, "인사와 자기소개", "Greetings & Self-Introduction",
         "'안녕하세요?·감사합니다·반가워요' 등 필수 인사말과 자기소개 문장을 읽고 씁니다.",
         "Read and write essential greetings like 안녕하세요?·감사합니다·반가워요 and self-introduction sentences.",
         "역할극 카드로 만났다 헤어지는 상황의 인사 대화를 주고받습니다.",
         "Use role-play cards to exchange greeting dialogues for meeting and parting.",
         "이름·국적·직업을 넣어 나를 소개하는 3문장을 만들어 말합니다.",
         "Make and speak 3 sentences introducing yourself with your name, country, and job.",
         "안녕하세요, 감사합니다, 반가워요"),
        (8, "숫자와 시간, 요일", "Numbers, Time & Days",
         "고유어/한자어 숫자를 구분하고 시간·요일·계절 표현을 익힙니다.",
         "Distinguish native and Sino-Korean numbers and learn time, day-of-week, and season expressions.",
         "시계 그림과 달력을 이용해 시간 말하기·요일 맞추기 퀴즈를 풉니다.",
         "Use a clock image and a calendar to do telling-time and day-matching quizzes.",
         "오늘 날짜와 지금 시간을 한국어로 말하고 적어 봅니다.",
         "Say and write today's date and the current time in Korean.",
         "하나~열, 1~10, 요일"),
        (9, "일상 어휘 (1)", "Everyday Vocabulary (1)",
         "가족·신체·색깔·과일·동물 등 흥미를 끄는 기본 명사를 학습합니다.",
         "Learn engaging basic nouns: family, body, colors, fruit, and animals.",
         "그림-단어 카드 짝맞추기와 빙고로 명사를 반복 노출합니다.",
         "Repeat noun exposure with picture-word matching cards and bingo.",
         "집 안의 물건과 가족을 가리키며 배운 단어로 이름을 붙여 봅니다.",
         "Point to objects and family members at home and label them with the new words.",
         "가족, 신체, 색깔, 과일, 동물"),
        (10, "일상 어휘 (2)와 기초 동사/형용사", "Everyday Vocabulary (2) & Basic Verbs/Adjectives",
         "음식·옷·직업 어휘와 자주 쓰는 기본 동사/형용사를 익힙니다.",
         "Learn food, clothing, and job vocabulary plus high-frequency basic verbs and adjectives.",
         "동작 카드를 보고 몸으로 표현하는 제스처 게임으로 동사를 익힙니다.",
         "Play a gesture game acting out action cards to learn verbs.",
         "오늘 먹은 음식과 입은 옷을 짧은 문장으로 말해 봅니다.",
         "Describe what you ate and wore today in short sentences.",
         "음식, 옷, 직업, 가다, 좋다"),
        (11, "나의 동네와 장소", "My Neighborhood & Places",
         "집·동네·위치 표현을 배우고 가로세로 낱말퍼즐로 복습합니다.",
         "Learn home, neighborhood, and location expressions and review with a crossword puzzle.",
         "지도 위에서 '앞·뒤·옆·사이' 위치말을 붙이는 인터랙티브 활동을 합니다.",
         "Do an interactive activity placing position words (앞·뒤·옆·사이) on a map.",
         "우리 동네 약도를 그리고 장소 이름을 한국어로 표시합니다.",
         "Draw a simple map of your neighborhood and label the places in Korean.",
         "집, 동네, 앞, 뒤, 옆"),
        (12, "짧은 이야기 읽기 및 초급 총정리", "Short Story Reading & Beginner Review",
         "그림책 기반 짧은 문장을 읽고 초급 전 과정을 총정리합니다.",
         "Read short picture-book sentences and review the entire beginner course.",
         "받아쓰기 연습과 초급 레벨 진단 평가 퀴즈를 풉니다.",
         "Do dictation practice and take the beginner-level diagnostic quiz.",
         "배운 단어로 나에 대한 짧은 그림일기 한 편을 완성합니다.",
         "Complete a short illustrated diary about yourself using the words you learned.",
         "받아쓰기, 진단 평가"),
    ],
    "intermediate": [
        (1, "심화 음운 규칙 (1)", "Advanced Sound Rules (1)",
         "ㅎ 탈락, 기식음화(축약) 등 자연스러운 발음을 위한 규칙을 학습합니다.",
         "Learn rules for natural pronunciation such as ㅎ-deletion and aspiration (contraction).",
         "원어민 음성을 듣고 표기와 실제 발음을 비교·표시하는 듣기 활동을 합니다.",
         "Listen to native audio and mark the gap between spelling and actual pronunciation.",
         "'좋아요·축하해요' 같은 단어를 규칙대로 발음하며 녹음해 비교합니다.",
         "Pronounce words like 좋아요·축하해요 by the rules and record yourself to compare.",
         "ㅎ 탈락, 기식음화(축약)"),
        (2, "심화 음운 규칙 (2)", "Advanced Sound Rules (2)",
         "경음화·구개음화·비음화 규칙을 마스터합니다.",
         "Master the rules of tensification, palatalization, and nasalization.",
         "규칙별 예시 단어를 듣고 받아쓰며 어떤 규칙이 적용됐는지 분류합니다.",
         "Hear example words per rule, take dictation, and classify which rule applies.",
         "뉴스 한 문장을 골라 적용된 음운 규칙을 표시하며 또렷이 읽습니다.",
         "Pick one news sentence, mark the sound rules used, and read it clearly.",
         "경음화, 구개음화, 비음화"),
        (3, "공공장소 이용하기", "Using Public Places",
         "우체국·은행·병원 등 공공장소에서 쓰는 필수 대화와 어휘를 익힙니다.",
         "Learn essential dialogues and vocabulary for public places like the post office, bank, and hospital.",
         "창구 직원과 손님 역할을 나눠 상황별 대화를 연습합니다.",
         "Split into clerk and customer roles to practice situational dialogues.",
         "실제로 은행/우체국에서 할 한 가지 용무를 한국어 문장으로 준비합니다.",
         "Prepare one real errand for the bank or post office as Korean sentences.",
         "우체국, 은행, 병원"),
        (4, "교통수단과 길 찾기", "Transportation & Directions",
         "다양한 교통수단 어휘와 지도를 보며 길 묻고 답하기를 배웁니다.",
         "Learn transportation vocabulary and how to ask for and give directions with a map.",
         "지하철 노선도를 보며 환승 경로를 묻고 답하는 상황극을 합니다.",
         "Role-play asking and answering transfer routes using a subway map.",
         "집에서 목적지까지 가는 길을 한국어로 설명해 봅니다.",
         "Explain the route from home to a destination in Korean.",
         "지하철, 버스, 환승, 길 묻기"),
        (5, "물건 구매와 음식 주문", "Shopping & Ordering Food",
         "가게에서 사이즈·색상 묻기, 식당에서 주문·결제하는 실전 회화를 배웁니다.",
         "Learn practical conversation for asking size/color in shops and ordering/paying at restaurants.",
         "메뉴판과 가격표 소품으로 주문-계산 역할극을 진행합니다.",
         "Run an ordering-and-paying role-play with menu and price-tag props.",
         "좋아하는 식당 메뉴를 한국어로 주문하는 대사를 만들어 말합니다.",
         "Write and speak lines to order your favorite restaurant menu in Korean.",
         "사이즈, 색상, 주문, 결제"),
        (6, "감정과 의견 표현하기", "Expressing Feelings & Opinions",
         "다양한 형용사로 감정 상태와 간단한 의견을 표현합니다.",
         "Express emotional states and simple opinions with a range of adjectives.",
         "감정 카드를 뽑아 이유와 함께 '왜냐하면…' 문장으로 말하는 게임을 합니다.",
         "Draw emotion cards and play a game saying '왜냐하면…' sentences with reasons.",
         "오늘 하루 기분과 그 이유를 3문장으로 일기처럼 적습니다.",
         "Write 3 diary-like sentences about today's mood and why.",
         "감정 형용사, 의견 표현"),
        (7, "전화 통화와 메시지 남기기", "Phone Calls & Messages",
         "전화 예절, 약속 잡기, 문자/SNS로 소통하는 법을 배웁니다.",
         "Learn phone etiquette, making appointments, and communicating via text/SNS.",
         "전화 대화 스크립트로 약속을 잡고 변경하는 롤플레이를 합니다.",
         "Role-play making and changing appointments with a phone-call script.",
         "친구에게 약속을 제안하는 한국어 문자 메시지를 작성합니다.",
         "Write a Korean text message proposing a meet-up to a friend.",
         "전화 예절, 약속, 문자"),
        (8, "직장 및 학교생활 기초", "Workplace & School Basics",
         "서비스 센터 방문, 직장·학교에서의 가벼운 업무 보고와 지시를 다룹니다.",
         "Cover service-center visits and light work reports and instructions at work or school.",
         "간단한 업무 지시-보고 대화를 듣고 핵심 정보를 메모하는 활동을 합니다.",
         "Listen to simple instruction-report dialogues and note the key information.",
         "오늘 한 일을 보고하는 짧은 업무 메시지를 한국어로 써 봅니다.",
         "Write a short Korean work message reporting what you did today.",
         "업무 보고, 지시, 서비스 센터"),
        (9, "한국의 문화와 생활 (1)", "Korean Culture & Life (1)",
         "한국의 전통과 명절(추석 등)에 대해 읽고 이야기를 나눕니다.",
         "Read and talk about Korean traditions and holidays such as Chuseok.",
         "명절 풍습 사진을 보며 어휘를 익히고 자기 나라 명절과 비교합니다.",
         "Learn vocabulary from holiday photos and compare with holidays in your own country.",
         "내 나라의 명절 하나를 한국어로 두세 문장 소개합니다.",
         "Introduce one holiday from your country in two or three Korean sentences.",
         "명절, 추석, 전통"),
        (10, "한국의 문화와 생활 (2)", "Korean Culture & Life (2)",
         "한류(K-드라마·K-POP·한복) 관련 지문을 읽고 감상을 나눕니다.",
         "Read passages on the Korean Wave (K-drama, K-pop, hanbok) and share impressions.",
         "K-POP 가사 한 구절을 받아쓰고 핵심 표현을 함께 분석합니다.",
         "Take dictation of a K-pop lyric line and analyze the key expressions together.",
         "좋아하는 K-콘텐츠를 추천하는 짧은 글을 한국어로 씁니다.",
         "Write a short Korean recommendation for your favorite K-content.",
         "한류, K-POP, 한복"),
        (11, "간단한 수필 및 일기 쓰기", "Simple Essays & Journaling",
         "나의 경험을 바탕으로 일기를 쓰고 간단한 수필 구조를 익힙니다.",
         "Write a journal from your own experience and learn a simple essay structure.",
         "처음-가운데-끝 구조 카드로 한 단락을 함께 배열해 봅니다.",
         "Arrange a paragraph together using beginning-middle-end structure cards.",
         "최근 인상 깊었던 하루를 한 단락 수필로 완성합니다.",
         "Complete a one-paragraph essay about a recent memorable day.",
         "일기, 수필 구조"),
        (12, "상황별 역할극 및 중급 총정리", "Situational Role-play & Intermediate Review",
         "배운 상황들로 롤플레이를 하고 중급 전 과정을 총정리합니다.",
         "Role-play the situations you learned and review the whole intermediate course.",
         "문단 읽기와 중급 진단 평가로 유창성을 점검합니다.",
         "Check fluency with paragraph reading and the intermediate diagnostic test.",
         "관심 주제로 1분 자기 표현 말하기를 녹음해 스스로 평가합니다.",
         "Record a 1-minute self-expression talk on a topic of interest and self-evaluate.",
         "롤플레이, 진단 평가"),
    ],
    "advanced": [
        (1, "최신 사회 및 경제 동향", "Current Society & Economic Trends",
         "구독 경제 등 경제 전문가 인터뷰 영상을 보고 독해합니다.",
         "Watch and read economic-expert interviews on topics like the subscription economy.",
         "인터뷰의 주장과 근거를 표로 정리하며 듣기 요약 활동을 합니다.",
         "Summarize the interview by organizing claims and evidence into a table.",
         "최근 경제 이슈 하나에 대한 내 생각을 한 단락으로 씁니다.",
         "Write one paragraph of your own view on a recent economic issue.",
         "구독 경제, 인터뷰 독해"),
        (2, "환경과 기후 변화", "Environment & Climate Change",
         "기후 변화의 현상과 대책에 관한 대담을 듣고 요약합니다.",
         "Listen to a discussion on climate-change phenomena and countermeasures, then summarize.",
         "찬반 의견을 나눠 토론 카드로 근거를 주고받는 미니 토론을 합니다.",
         "Hold a mini-debate exchanging evidence with pro/con discussion cards.",
         "일상에서 실천할 환경 행동 3가지를 한국어 문장으로 제안합니다.",
         "Propose 3 everyday environmental actions in Korean sentences.",
         "기후 변화, 대담 요약"),
        (3, "한국의 역사와 기록물", "Korean History & Records",
         "왕과 관련된 기록물과 역사적 의의를 다룬 다큐멘터리/강연을 시청합니다.",
         "Watch documentaries/lectures on royal records and their historical significance.",
         "연표를 보며 사건의 인과를 잇는 읽기 활동을 합니다.",
         "Do a reading activity linking cause and effect of events along a timeline.",
         "관심 있는 역사 인물·기록을 한국어로 짧게 소개합니다.",
         "Briefly introduce a historical figure or record you find interesting in Korean.",
         "기록물, 다큐멘터리"),
        (4, "한국의 예술과 미학", "Korean Art & Aesthetics",
         "건축의 공간 미학, 민화, 서예(캘리그래피)를 다룬 설명문을 읽습니다.",
         "Read expository texts on architectural spatial aesthetics, folk painting, and calligraphy.",
         "작품 이미지를 보고 인상을 묘사하는 형용사 어휘를 확장합니다.",
         "Expand descriptive adjective vocabulary by describing impressions of artwork images.",
         "좋아하는 한국 예술 작품을 골라 감상을 한 단락으로 씁니다.",
         "Choose a Korean artwork you like and write a one-paragraph appreciation.",
         "건축 미학, 민화, 서예"),
        (5, "비즈니스 한국어 (1)", "Business Korean (1)",
         "공식적인 이메일 작성법과 회의에서의 논리적 의견 제시·설득을 배웁니다.",
         "Learn formal email writing and logical opinion-giving and persuasion in meetings.",
         "이메일 템플릿을 분석하고 정중한 표현으로 문장을 바꿔 쓰는 연습을 합니다.",
         "Analyze email templates and rewrite sentences with polite expressions.",
         "회의 일정을 제안하는 격식체 이메일 한 통을 작성합니다.",
         "Write one formal email proposing a meeting schedule.",
         "공식 이메일, 회의, 설득"),
        (6, "비즈니스 한국어 (2)", "Business Korean (2)",
         "프레젠테이션 기법과 비즈니스 문서·보고서 해석을 익힙니다.",
         "Learn presentation techniques and how to interpret business documents and reports.",
         "보고서 도표를 읽고 핵심 수치를 말로 설명하는 활동을 합니다.",
         "Read report charts and explain the key figures aloud.",
         "관심 분야 제품/서비스를 1분 발표 슬라이드 개요로 정리합니다.",
         "Outline a 1-minute pitch deck for a product/service in your field.",
         "프레젠테이션, 보고서"),
        (7, "한국 문학과 시", "Korean Literature & Poetry",
         "한국의 유명한 시와 단편 소설을 감상하고 은유적 표현을 이해합니다.",
         "Appreciate famous Korean poems and short stories and understand metaphorical expressions.",
         "시 한 편의 이미지와 비유를 함께 해석하고 낭송합니다.",
         "Interpret the imagery and metaphors of a poem together and recite it.",
         "짧은 시 한 편을 골라 느낀 점을 한국어로 적습니다.",
         "Choose a short poem and write your reflections in Korean.",
         "시, 단편 소설, 은유"),
        (8, "속담과 관용어", "Proverbs & Idioms",
         "한국인이 자주 쓰는 속담과 관용 표현을 익혀 대화에 적용합니다.",
         "Learn common Korean proverbs and idioms and apply them in conversation.",
         "상황과 속담을 짝짓는 카드 게임으로 의미를 추론합니다.",
         "Infer meanings with a card game matching situations to proverbs.",
         "오늘 상황에 어울리는 속담 하나를 골라 문장에 써 봅니다.",
         "Pick one proverb that fits today and use it in a sentence.",
         "속담, 관용 표현"),
        (9, "뉴스 리터러시", "News Literacy",
         "TV 뉴스 보도와 신문 사설(논설문)을 읽고 핵심 주장을 파악합니다.",
         "Read TV news reports and newspaper editorials and identify the core argument.",
         "사설에서 사실과 의견을 색으로 구분해 표시하는 분석 활동을 합니다.",
         "Color-code facts vs. opinions in an editorial as an analysis activity.",
         "관심 뉴스 한 건을 골라 3문장으로 요약·논평합니다.",
         "Choose one news item and summarize and comment on it in 3 sentences.",
         "뉴스, 사설, 논설문"),
        (10, "토론과 논증 (1)", "Debate & Argument (1)",
         "특정 사회적 찬반 이슈에 대해 자신의 논리를 세워 주장하는 말하기를 연습합니다.",
         "Practice building and asserting your own logic on a social pro/con issue.",
         "주장-근거-예시(PREP) 틀로 발언문을 구성하는 연습을 합니다.",
         "Practice structuring statements with the claim-reason-example (PREP) frame.",
         "관심 이슈에 대한 1분 주장 말하기를 준비해 발표합니다.",
         "Prepare and deliver a 1-minute argument on an issue of interest.",
         "찬반, 주장, 근거"),
        (11, "토론과 논증 (2)와 논리적 글쓰기", "Debate & Argument (2) & Logical Writing",
         "사회 문제에 대한 논술문/사설을 작성하고 상호 첨삭합니다.",
         "Write argumentative essays/editorials on social issues and peer-edit them.",
         "서론-본론-결론 구조로 한 편의 글을 함께 설계합니다.",
         "Design an essay together with intro-body-conclusion structure.",
         "관심 주제로 한 단락 논설문을 작성해 동료와 첨삭합니다.",
         "Write a one-paragraph argumentative essay and peer-edit it.",
         "논술, 사설, 첨삭"),
        (12, "최종 프로젝트 및 고급 총정리", "Final Project & Advanced Review",
         "심도 깊은 사회적 주제 하나를 선정해 발표하고 고급 인증 평가를 받습니다.",
         "Choose one in-depth social topic to present and take the advanced certification assessment.",
         "발표 리허설과 질의응답으로 논리와 전달력을 점검합니다.",
         "Check logic and delivery with a presentation rehearsal and Q&A.",
         "주제 발표(PT) 자료를 완성하고 고급 총정리 평가에 응시합니다.",
         "Complete your presentation (PT) materials and take the advanced wrap-up assessment.",
         "발표(PT), 고급 인증 평가"),
    ],
}

FIELDS = [
    "level", "week", "title_ko", "title_en",
    "concept_ko", "concept_en", "practice_ko", "practice_en",
    "application_ko", "application_en", "target_letters",
]

# 레벨별 보상(프런트 모달에서 노출). 스키마에는 넣지 않고 JSON 덤프에 부가 정보로만 싣는다.
LEVEL_REWARDS = {
    "beginner": {
        "ko": "생존 배지 · 올바른 획순/연음 발음 애니메이션 가이드",
        "en": "Survival badges · stroke-order & liaison-pronunciation animation guides",
    },
    "intermediate": {
        "ko": "K-컬처 프리미엄 콘텐츠 해금 (웹툰 · 드라마 · K-POP 영상)",
        "en": "K-Culture premium unlocks (webtoons, drama & K-pop videos)",
    },
    "advanced": {
        "ko": "TOPIK/세종한국어평가 모의고사 무료 응시권 · 뽐내기 대회 출전권",
        "en": "Free TOPIK/SKA mock-exam ticket · speech-contest entry pass",
    },
}


def parse_source_titles(md_path):
    """소스 플랜에서 레벨별 'N주 차: 제목' 12개씩을 추출해 검증용으로 돌려준다."""
    if not os.path.exists(md_path):
        print(f"[WARN] 소스 플랜을 찾지 못함 (검증 건너뜀): {md_path}")
        return {}
    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()

    current = None
    titles = {lvl: [] for lvl in LEVELS}
    week_re = re.compile(r"^\s*(\d+)\s*주\s*차\s*[::]\s*(.+?)\s*$")
    for line in lines:
        for marker, lvl in LEVEL_MARKERS:
            if marker in line and "1~12주" in line:
                current = lvl
                break
        if current is None:
            continue
        m = week_re.match(line)
        if m:
            titles[current].append((int(m.group(1)), m.group(2)))
    return titles


def build_rows():
    """CURRICULUM -> 정렬된 dict 행 리스트(36개)."""
    rows = []
    for lvl in LEVELS:
        weeks = CURRICULUM[lvl]
        if len(weeks) != 12:
            raise ValueError(f"{lvl}: 12주가 아님 ({len(weeks)}주)")
        for tup in sorted(weeks, key=lambda t: t[0]):
            rows.append(dict(zip(FIELDS, (lvl,) + tup)))
    return rows


# ---------------------------------------------------------------------------
# SQLite (channel/content.db) — 항상 실행
# ---------------------------------------------------------------------------
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
    cols = ", ".join(FIELDS)
    ph = ", ".join("?" for _ in FIELDS)
    updates = ", ".join(f"{c}=excluded.{c}" for c in FIELDS if c not in ("level", "week"))
    sql = (f"INSERT INTO hangeul_curriculum ({cols}) VALUES ({ph}) "
           f"ON CONFLICT(level, week) DO UPDATE SET {updates}")
    n = 0
    for r in rows:
        cur.execute(sql, [r[c] for c in FIELDS])
        n += 1
    conn.commit()
    per = {lvl: cur.execute(
        "SELECT COUNT(*) FROM hangeul_curriculum WHERE level=?", (lvl,)).fetchone()[0]
        for lvl in LEVELS}
    total = cur.execute("SELECT COUNT(*) FROM hangeul_curriculum").fetchone()[0]
    conn.close()
    print(f"[SQLite] {SQLITE_DB}")
    print(f"  upserted {n} rows  |  table total {total}  "
          f"(beginner {per['beginner']}, intermediate {per['intermediate']}, advanced {per['advanced']})")
    return total


# ---------------------------------------------------------------------------
# Supabase Postgres (psycopg2) — best-effort
# ---------------------------------------------------------------------------
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

    migration = os.path.join(ROOT, "supabase", "migrations",
                             "202606250000_create_hangeul_curriculum.sql")
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
        # 1) 마이그레이션(테이블/인덱스/RLS) 적용
        if os.path.exists(migration):
            with open(migration, encoding="utf-8") as f:
                cur.execute(f.read())
            print(f"[Supabase] migration applied: {os.path.basename(migration)}")
        # 2) 업서트
        cols = ", ".join(FIELDS)
        ph = ", ".join("%s" for _ in FIELDS)
        updates = ", ".join(f"{c}=EXCLUDED.{c}" for c in FIELDS if c not in ("level", "week"))
        sql = (f"INSERT INTO hangeul_curriculum ({cols}) VALUES ({ph}) "
               f"ON CONFLICT (level, week) DO UPDATE SET {updates}")
        n = 0
        for r in rows:
            cur.execute(sql, [r[c] for c in FIELDS])
            n += 1
        cur.execute("SELECT level, COUNT(*) FROM hangeul_curriculum GROUP BY level")
        per = dict(cur.fetchall())
        cur.execute("SELECT COUNT(*) FROM hangeul_curriculum")
        total = cur.fetchone()[0]
        print(f"[Supabase] {host}")
        print(f"  upserted {n} rows  |  table total {total}  "
              f"(beginner {per.get('beginner', 0)}, intermediate {per.get('intermediate', 0)}, "
              f"advanced {per.get('advanced', 0)})")
        return total
    except Exception as e:
        print(f"[Supabase] 시드 중 오류 — 건너뜀: {type(e).__name__}: {e}")
        return None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 정적 JSON 덤프 (web/src/data/curriculum_fallback.json)
# ---------------------------------------------------------------------------
def write_json(rows):
    data = {
        "generated_from": "scratch/found_curriculum_073ae673-b8ee-4586-b9c2-f4f12e7276a1.md",
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
    print("  Hangeul 36-week Curriculum Seeder")
    print("=" * 70)

    rows = build_rows()
    print(f"[Build] {len(rows)} rows (3 levels x 12 weeks)")

    # 소스 플랜과 제목 교차 검증
    parsed = parse_source_titles(SOURCE_MD)
    if parsed:
        for lvl in LEVELS:
            got = parsed.get(lvl, [])
            print(f"[Parse] {LEVEL_KO[lvl]}({lvl}): 소스에서 {len(got)}개 주차 제목 추출")
            if len(got) != 12:
                print(f"  [WARN] {lvl} 주차 수가 12가 아님 — 큐레이션 데이터 기준으로 진행")

    seed_sqlite(rows)
    seed_postgres(rows)
    write_json(rows)

    print("=" * 70)
    print("  완료: SQLite + (Supabase best-effort) + JSON 덤프")
    print("=" * 70)


if __name__ == "__main__":
    main()
