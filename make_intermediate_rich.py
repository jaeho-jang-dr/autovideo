#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_intermediate_rich.py — 중급 1~7주(W9-15) **충실한** 재작성.
각 표현마다 뜻 + 실제 예문(화면 표시) + 발음/사용 팁, 그리고 주차별 실제 상황 대화까지.
외국인 학습자를 친절히 안내하는 따뜻한 톤. 웹 커리큘럼(개념/연습/응용) 근거 + DB 발음 클립.
캐릭터/스케일/포즈는 make_intermediate.WEEKS 재사용(한 영상당 한 명).
재실행: python make_intermediate_rich.py [week ...]
"""
import os
import sys
import json
import sqlite3
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from tts_manager import save_tts_edge_tts
from make_intermediate import WEEKS as CHARCFG   # char/scale/cy/gestures 재사용

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = os.path.join(ROOT, "channel", "content.db")
LDIR = os.path.join(ROOT, "assets", "graphics", "letters")
ADIR = os.path.join(ROOT, "web", "public", "audio", "jamo")
LOCAL_DIR = os.path.join(ROOT, "hangeul_birth_vowels")
FONT = "C:/Windows/Fonts/malgunbd.ttf" if os.path.exists("C:/Windows/Fonts/malgunbd.ttf") else "C:/Windows/Fonts/malgun.ttf"
FF = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs(LDIR, exist_ok=True)

# v: (단어, 뜻ko, 예문ko, 예문en, 팁ko, en뜻)
RICH = {
    9: dict(intro_ko="안녕하세요! 한국에서 살다 보면 '어디에 있어요?'라는 질문을 자주 들어요. 오늘은 위치를 말하는 표현을 배워서, 우리 동네를 자신 있게 안내해 봐요.",
            intro_en="Hello! Living in Korea, you'll often hear 'Where is it?'. Today we'll learn how to describe locations so you can confidently guide people around your neighborhood.",
            concept_ko="위치는 보통 '장소 + 위치말 + 에' 순서로 말해요. 예를 들어 '학교 앞에'처럼요. 천천히 함께 익혀 봐요.",
            concept_en="Location is usually said as 'place + position word + 에'. For example, '학교 앞에' (in front of the school). Let's learn it slowly together.",
            dlg=[("마트가 어디에 있어요?", "Where is the mart?"), ("학교 앞에 있어요.", "It's in front of the school.")],
            vocab=[
                ("앞", "어떤 것의 정면 쪽", "학교 앞에서 만나요.", "Let's meet in front of the school.", "장소 뒤에 '앞에'를 붙여요.", "front"),
                ("뒤", "정면의 반대, 등지는 쪽", "집 뒤에 공원이 있어요.", "There's a park behind the house.", "'뒤에'로 위치를 말해요.", "back"),
                ("옆", "바로 곁, 나란한 쪽", "은행 옆에 카페가 있어요.", "There's a cafe next to the bank.", "두 장소가 나란할 때 써요.", "beside"),
                ("위", "더 높은 쪽", "책상 위에 책이 있어요.", "There's a book on the desk.", "표면 '위에' 무엇이 있는지 말해요.", "above/on"),
                ("밑", "더 낮은 쪽, 아래", "의자 밑에 가방이 있어요.", "There's a bag under the chair.", "'밑'과 '아래'는 비슷해요.", "under"),
                ("마트", "물건을 파는 큰 가게", "마트에서 우유를 사요.", "I buy milk at the mart.", "받침 없이 부드럽게, 마트.", "the mart"),
                ("학교", "공부하는 곳", "학교에 걸어서 가요.", "I walk to school.", "장소 뒤 '에'는 방향을 나타내요.", "school"),
            ]),
    10: dict(intro_ko="안녕하세요! 가게에서 물건을 살 때 꼭 필요한 표현들이 있어요. 오늘 배우면 한국 어디서든 자신 있게 쇼핑할 수 있어요.",
             intro_en="Hello! There are must-know phrases for shopping. After today, you can shop confidently anywhere in Korea.",
             concept_ko="쇼핑은 '가격 묻기 → 고르기 → 결제' 순서로 흘러가요. 핵심 표현을 하나씩 익혀 봐요.",
             concept_en="Shopping flows as 'ask price → choose → pay'. Let's learn each key phrase.",
             dlg=[("이거 얼마예요?", "How much is this?"), ("오천 원이에요. 지금 할인 중이에요!", "It's 5,000 won. It's on sale now!")],
             vocab=[
                 ("얼마예요", "가격을 묻는 말", "이거 얼마예요?", "How much is this?", "물건을 가리키며 말해요.", "how much?"),
                 ("이거 주세요", "이것을 달라는 말", "이거 주세요.", "This one, please.", "'이거/그거/저거 + 주세요'.", "this, please"),
                 ("결제", "돈을 내는 것", "카드로 결제할게요.", "I'll pay by card.", "'카드/현금으로 결제'.", "payment"),
                 ("할인", "값을 깎아 주는 것", "이거 할인 돼요?", "Is this discounted?", "세일할 때 자주 들어요.", "discount"),
             ]),
    11: dict(intro_ko="안녕하세요! 한국 식당은 정말 다양해요. 오늘은 주문하고 맛을 표현하는 법을 배워서, 맛있는 한 끼를 즐겨 봐요.",
             intro_en="Hello! Korean restaurants are wonderfully diverse. Today we'll learn to order and describe taste, so you can enjoy a delicious meal.",
             concept_ko="식당에서는 '주문 → 먹기 → 맛 표현' 순서로 말해요. 맛은 형용사로 표현해요.",
             concept_en="At a restaurant: 'order → eat → describe taste'. Taste is expressed with adjectives.",
             dlg=[("뭐 주문할까요?", "What shall we order?"), ("불고기 주문할게요. 안 매워요!", "I'll order bulgogi. It's not spicy!")],
             vocab=[
                 ("주문할게요", "음식을 시키겠다는 말", "비빔밥 주문할게요.", "I'll order bibimbap.", "메뉴 이름 + 주문할게요.", "I'll order"),
                 ("맛있어요", "맛이 좋아요", "와, 정말 맛있어요!", "Wow, it's really delicious!", "엄지를 들며 말해 보세요.", "it's delicious"),
                 ("매워요", "고추처럼 매운맛", "이 김치가 좀 매워요.", "This kimchi is a bit spicy.", "'안 매워요'는 맵지 않다는 뜻.", "it's spicy"),
                 ("달아요", "설탕처럼 단맛", "이 케이크가 달아요.", "This cake is sweet.", "단맛을 말할 때 써요.", "it's sweet"),
             ]),
    12: dict(intro_ko="안녕하세요! 한국의 대중교통은 빠르고 편리해요. 오늘은 버스와 지하철을 타고 환승하는 표현을 배워서, 어디든 갈 수 있게 해요.",
             intro_en="Hello! Korea's public transit is fast and convenient. Today we'll learn bus, subway, and transfer phrases so you can go anywhere.",
             concept_ko="교통은 '무엇을 타다 → 어디서 내리다 → 환승하다' 순서로 말해요. 'X을/를 타다'를 기억하세요.",
             concept_en="Transit: 'take what → get off where → transfer'. Remember 'take X' = 'X을/를 타다'.",
             dlg=[("강남역에 어떻게 가요?", "How do I get to Gangnam Station?"), ("지하철을 타고 시청역에서 환승하세요.", "Take the subway and transfer at City Hall Station.")],
             vocab=[
                 ("버스", "여러 사람이 타는 큰 차", "버스를 타고 가요.", "I go by bus.", "'버스를 타다'로 써요.", "bus"),
                 ("지하철", "땅속을 달리는 기차", "지하철이 더 빨라요.", "The subway is faster.", "호선 번호로 길을 찾아요.", "subway"),
                 ("타다", "차에 오르다", "여기서 2호선을 타요.", "I take Line 2 here.", "'을/를 타다' 형태로 써요.", "to ride"),
                 ("환승", "다른 노선으로 갈아타기", "시청역에서 환승해요.", "I transfer at City Hall.", "역 안내 방송에서 자주 들어요.", "transfer"),
             ]),
    13: dict(intro_ko="안녕하세요! 길을 잃어도 걱정 마세요. 오늘은 길을 묻고 안내하는 표현을 배워서, 어디서든 길을 찾고 도와줄 수 있게 해요.",
             intro_en="Hello! Don't worry if you get lost. Today we'll learn to ask for and give directions, so you can find your way and help others.",
             concept_ko="길 안내는 '방향 + 가다/돌다/건너다'로 말해요. 손으로 방향을 가리키면 더 쉬워요.",
             concept_en="Directions use 'direction + go/turn/cross'. Pointing with your hand makes it easier.",
             dlg=[("지하철역이 어디예요?", "Where is the subway station?"), ("똑바로 가서 오른쪽으로 길을 건너세요.", "Go straight, then cross the street to the right.")],
             vocab=[
                 ("오른쪽", "오른편 방향", "오른쪽으로 도세요.", "Turn to the right.", "'오른쪽으로 + 동사'.", "right"),
                 ("왼쪽", "왼편 방향", "왼쪽에 편의점이 있어요.", "There's a convenience store on the left.", "오른쪽의 반대예요.", "left"),
                 ("똑바로 가다", "곧장 앞으로 가다", "이 길로 똑바로 가세요.", "Go straight along this road.", "'쭉 가세요'와 비슷해요.", "go straight"),
                 ("건너다", "길 반대편으로 넘어가다", "횡단보도에서 길을 건너세요.", "Cross at the crosswalk.", "'길을 건너다'로 써요.", "to cross"),
             ]),
    14: dict(intro_ko="안녕하세요! 하루 일과를 한국어로 말할 수 있으면 자기소개가 훨씬 풍부해져요. 오늘은 아침부터 밤까지의 동작을 배워 봐요.",
             intro_en="Hello! Describing your daily routine makes your Korean much richer. Today we'll learn actions from morning to night.",
             concept_ko="일과는 시간 순서로 말해요. '아침에 일어나다 → 낮에 일하다 → 밤에 자다'처럼요.",
             concept_en="Describe routines in time order: 'wake up in the morning → work during the day → sleep at night'.",
             dlg=[("보통 몇 시에 일어나요?", "What time do you usually wake up?"), ("일곱 시에 일어나서 도서관에서 공부해요.", "I wake up at seven and study at the library.")],
             vocab=[
                 ("일어나다", "잠에서 깨어 몸을 일으키다", "아침 일곱 시에 일어나요.", "I wake up at seven in the morning.", "'~시에 일어나요'로 써요.", "to wake up"),
                 ("공부하다", "배우고 익히다", "도서관에서 한국어를 공부해요.", "I study Korean at the library.", "장소 + 에서 + 공부해요.", "to study"),
                 ("일하다", "직장에서 일을 하다", "회사에서 아홉 시부터 일해요.", "I work from nine at the company.", "'에서 일해요'로 써요.", "to work"),
                 ("자다", "잠을 자다", "밤 열한 시에 자요.", "I go to sleep at eleven at night.", "'일찍/늦게 자요'도 자주 써요.", "to sleep"),
             ]),
    15: dict(intro_ko="안녕하세요! 한국은 사계절이 뚜렷해서 날씨 이야기를 자주 해요. 오늘은 날씨와 계절 표현을 배워서, 매일의 대화를 시작해 봐요.",
             intro_en="Hello! Korea has four distinct seasons, so weather is a common topic. Today we'll learn weather and season words to start everyday conversations.",
             concept_ko="날씨는 '오늘 날씨가 + 상태'로 말해요. 형용사는 '춥다, 덥다'처럼 끝이 바뀌어요.",
             concept_en="Weather is said as 'today's weather is + state'. Adjectives change endings, like '춥다, 덥다'.",
             dlg=[("오늘 날씨 어때요?", "How's the weather today?"), ("맑아요. 그런데 바람이 불어서 좀 추워요.", "It's clear, but it's a bit cold because of the wind.")],
             vocab=[
                 ("맑음", "구름 없이 하늘이 맑은 상태", "오늘은 날씨가 맑아요.", "The weather is clear today.", "일기예보에서 자주 봐요.", "sunny/clear"),
                 ("비", "하늘에서 내리는 물", "비가 와요. 우산을 챙기세요.", "It's raining. Take an umbrella.", "'비가 오다/내리다'.", "rain"),
                 ("눈", "겨울에 내리는 흰 것", "겨울에 눈이 많이 내려요.", "It snows a lot in winter.", "'눈이 오다/내리다'.", "snow"),
                 ("춥다", "기온이 낮아 차갑다", "겨울은 정말 추워요.", "Winter is really cold.", "말할 때 '추워요'로 바뀌어요.", "cold"),
                 ("덥다", "기온이 높아 뜨겁다", "여름은 너무 더워요.", "Summer is very hot.", "말할 때 '더워요'로 바뀌어요.", "hot"),
                 ("사계절", "봄·여름·가을·겨울", "한국은 사계절이 뚜렷해요.", "Korea has four distinct seasons.", "계절마다 날씨가 달라요.", "four seasons"),
             ]),
    # ===== 중급 8주(W16) 취미·빈도 =====
    16: dict(intro_ko="안녕하세요! 취미를 한국어로 말할 수 있으면 친구를 사귀기가 훨씬 쉬워져요. 오늘은 취미와 '얼마나 자주' 하는지를 표현하는 법을 배워 봐요.",
             intro_en="Hello! Talking about hobbies in Korean makes it much easier to make friends. Today we'll learn hobbies and how to say 'how often' you do them.",
             concept_ko="취미는 '저는 ~을 좋아해요'로, 빈도는 '자주·가끔'으로 말해요. 동사 앞에 빈도 부사를 넣어요.",
             concept_en="Say hobbies with '저는 ~을 좋아해요', and frequency with '자주' (often) or '가끔' (sometimes), placed before the verb.",
             dlg=[("취미가 뭐예요?", "What's your hobby?"), ("저는 영화 감상을 좋아해요. 주말에 자주 봐요.", "I like watching movies. I watch them often on weekends.")],
             vocab=[
                 ("영화 감상", "영화를 보며 즐기는 취미", "주말에 영화 감상을 해요.", "I watch movies on weekends.", "'영화를 보다'와 같은 뜻이에요.", "watching movies"),
                 ("운동", "몸을 움직여 건강을 지키는 활동", "저는 매일 아침 운동을 해요.", "I exercise every morning.", "'운동을 하다'로 써요.", "exercise"),
                 ("자주", "짧은 사이를 두고 여러 번", "저는 자주 음악을 들어요.", "I often listen to music.", "동사 앞에 넣어 빈도를 말해요.", "often"),
                 ("가끔", "이따금, 드물게 한 번씩", "가끔 친구와 등산을 가요.", "I sometimes go hiking with friends.", "'자주'의 반대예요.", "sometimes"),
                 ("좋아하다", "마음에 들어 즐기다", "저는 한국 음식을 좋아해요.", "I like Korean food.", "'~을/를 좋아해요'로 써요.", "to like"),
             ]),
    # ===== 고급 1~8주(W17-24) =====
    17: dict(intro_ko="안녕하세요! 드라마와 K팝을 보면 교과서에 없는 진짜 한국어가 들려요. 오늘은 친구끼리 쓰는 편한 말과 줄임말을 배워, 한국 문화를 더 가깝게 느껴 봐요.",
             intro_en="Hello! In dramas and K-pop you'll hear real Korean that's not in textbooks. Today we'll learn casual speech and abbreviations to feel Korean culture up close.",
             concept_ko="친한 사이에서는 '반말'을, SNS에서는 '축약어'를 자주 써요. 상황에 맞게 골라 쓰는 게 중요해요.",
             concept_en="Among close friends, people use casual speech (반말); online, abbreviations. Choosing the right one for the situation matters.",
             dlg=[("주말에 뭐 해?", "What are you doing this weekend?"), ("그냥 집에서 케이드라마 봐. 너는?", "Just watching K-dramas at home. You?")],
             vocab=[
                 ("반말", "친구·가까운 사이에서 쓰는 편한 말투", "친구에게는 '밥 먹었어?'처럼 반말로 말해요.", "To a friend you say casually, 'Did you eat?'", "처음 본 사람에겐 존댓말을 써요.", "casual speech"),
                 ("축약어", "길게 쓰는 말을 짧게 줄인 말", "'생일 축하해'를 줄여 '생축'이라고 해요.", "'Happy birthday' is shortened to '생축'.", "SNS·메시지에서 자주 봐요.", "abbreviation"),
                 ("케이팝", "전 세계가 즐기는 한국 대중음악", "저는 케이팝을 들으며 한국어를 배워요.", "I learn Korean by listening to K-pop.", "가사를 따라 부르면 발음 연습이 돼요.", "K-Pop"),
                 ("케이드라마", "한국에서 만든 드라마", "케이드라마로 자연스러운 표현을 익혀요.", "I pick up natural expressions from K-dramas.", "자막을 켜고 한 문장씩 따라 해 보세요.", "K-Drama"),
             ]),
    18: dict(intro_ko="안녕하세요! 마음을 정확히 표현하면 대화가 훨씬 깊어져요. 오늘은 기쁨부터 속상함까지, 다양한 감정을 한국어로 섬세하게 말하는 법을 배워 봐요.",
             intro_en="Hello! Expressing your feelings precisely makes conversations deeper. Today we'll learn to describe emotions from joy to disappointment in Korean.",
             concept_ko="감정은 형용사로 말해요. 말할 때는 '기쁘다 → 기뻐요'처럼 부드럽게 끝을 바꿔요.",
             concept_en="Emotions are adjectives. When speaking, endings soften: '기쁘다 → 기뻐요'.",
             dlg=[("시험 어떻게 됐어요?", "How did the exam go?"), ("합격했어요! 정말 기뻐요.", "I passed! I'm really happy.")],
             vocab=[
                 ("기쁘다", "마음이 즐겁고 좋다", "합격해서 정말 기뻐요.", "I'm so happy I passed.", "말할 때 '기뻐요'로 바뀌어요.", "happy"),
                 ("슬프다", "마음이 아프고 울고 싶다", "영화가 슬퍼서 울었어요.", "The movie was sad, so I cried.", "'슬퍼요'로 부드럽게 말해요.", "sad"),
                 ("긴장되다", "떨리고 마음이 불안하다", "발표 전에는 긴장돼요.", "I get nervous before a presentation.", "'긴장돼요'로 자주 써요.", "nervous"),
                 ("속상하다", "일이 잘 안돼 마음이 상하다", "실수해서 속상해요.", "I'm upset that I made a mistake.", "아쉽고 마음 아플 때 써요.", "upset"),
             ]),
    19: dict(intro_ko="안녕하세요! 자기 생각을 논리적으로 말하면 신뢰를 얻어요. 오늘은 의견을 밝히고 이유를 들어 설득하는 표현을 배워 봐요.",
             intro_en="Hello! Stating your views logically builds trust. Today we'll learn to give opinions and persuade with reasons.",
             concept_ko="의견은 '~다고 생각해요', 이유는 '왜냐하면', 결론은 '따라서'로 이어요. 이 흐름을 기억하세요.",
             concept_en="State opinion with '~라고 생각해요', reason with '왜냐하면', conclusion with '따라서'. Remember this flow.",
             dlg=[("운동이 정말 중요할까요?", "Is exercise really important?"), ("네, 건강에 좋다고 생각해요. 왜냐하면 몸이 튼튼해지니까요.", "Yes, I think it's good for health, because it makes the body strong.")],
             vocab=[
                 ("생각해요", "자기 의견을 밝히는 말", "저는 그게 좋다고 생각해요.", "I think that's a good idea.", "'~다고 생각해요'로 의견을 말해요.", "I think"),
                 ("왜냐하면", "이유를 설명할 때 쓰는 말", "왜냐하면 시간이 절약되니까요.", "Because it saves time.", "이유 문장 앞에 붙여요.", "because"),
                 ("따라서", "앞 내용의 결론을 말하는 말", "따라서 저는 찬성해요.", "Therefore, I agree.", "결론을 정리할 때 써요.", "therefore"),
             ]),
    20: dict(intro_ko="안녕하세요! 여행이나 일상에서 갑작스러운 문제가 생길 수 있어요. 오늘은 물건을 잃거나 고장 났을 때 침착하게 도움을 요청하는 표현을 배워 봐요.",
             intro_en="Hello! Unexpected problems can happen anytime. Today we'll learn to calmly ask for help when you lose something or something breaks.",
             concept_ko="돌발 상황에서는 '무엇이 어떻게 됐어요'를 분명히 말하고 도움을 요청해요.",
             concept_en="In emergencies, clearly say 'what happened' and ask for help.",
             dlg=[("무슨 일이세요?", "What's the matter?"), ("지갑을 분실했어요. 도와주세요.", "I lost my wallet. Please help me.")],
             vocab=[
                 ("분실", "물건을 잃어버리는 것", "지하철에서 가방을 분실했어요.", "I lost my bag on the subway.", "'분실했어요'로 신고해요.", "loss"),
                 ("고장", "기계가 망가져 작동 안 함", "휴대폰이 고장 났어요.", "My phone is broken.", "'고장 났어요'로 말해요.", "breakdown"),
                 ("예약 변경", "정한 예약을 바꾸는 것", "예약을 변경하고 싶어요.", "I'd like to reschedule my reservation.", "정중히 부탁해요.", "reschedule"),
                 ("긴급", "아주 급해 빨리 도와야 함", "긴급 상황이에요, 빨리요!", "It's an emergency, quickly please!", "급할 때 분명히 말해요.", "urgent"),
             ]),
    21: dict(intro_ko="안녕하세요! 사람을 소개할 때 외모와 성격을 잘 묘사하면 대화가 생생해져요. 오늘은 인물을 섬세하게 표현하는 어휘를 배워 봐요.",
             intro_en="Hello! Describing looks and personality makes conversations vivid. Today we'll learn vocabulary to portray people in detail.",
             concept_ko="사람은 '외모'(겉모습)와 '성격'(마음)으로 나눠 묘사해요. 성격은 '내향적/외향적'으로 표현할 수 있어요.",
             concept_en="Describe people by '외모' (looks) and '성격' (personality). Personality can be 'introverted/extroverted'.",
             dlg=[("새 친구는 어때요?", "What's your new friend like?"), ("성격이 밝고 외향적이에요.", "She's bright and extroverted.")],
             vocab=[
                 ("외모", "사람의 겉모습", "그 배우는 외모가 멋있어요.", "That actor is good-looking.", "키·눈매·머리형을 함께 말해요.", "appearance"),
                 ("성격", "사람의 마음과 행동 특징", "제 친구는 성격이 친절해요.", "My friend has a kind personality.", "'성격이 + 형용사'로 써요.", "personality"),
                 ("내향적", "조용하고 차분한 성격", "저는 좀 내향적이에요.", "I'm a bit introverted.", "혼자 있는 걸 편해해요.", "introverted"),
                 ("외향적", "활발하고 사람을 좋아하는 성격", "그는 외향적이라 친구가 많아요.", "He's extroverted, so he has many friends.", "사람들과 어울리길 좋아해요.", "extroverted"),
             ]),
    22: dict(intro_ko="안녕하세요! 여행 이야기는 어디서나 즐거운 대화 주제예요. 오늘은 다녀온 경험을 말하고 앞으로의 계획을 세우는 표현을 배워 봐요.",
             intro_en="Hello! Travel stories are a delightful topic anywhere. Today we'll learn to talk about past trips and make future plans.",
             concept_ko="경험은 '~한 적이 있어요', 계획은 '~할 거예요'로 말해요. 과거와 미래를 자연스럽게 이어 봐요.",
             concept_en="Talk about experience with '~한 적이 있어요' and plans with '~할 거예요'. Connect past and future naturally.",
             dlg=[("제주도에 가 봤어요?", "Have you been to Jeju Island?"), ("네, 두 번 가 본 적이 있어요. 다음엔 부산에 갈 계획이에요.", "Yes, I've been twice. Next, I plan to go to Busan.")],
             vocab=[
                 ("가 본 적이 있어요", "전에 가 본 경험을 말하는 표현", "저는 서울에 가 본 적이 있어요.", "I have been to Seoul.", "'장소에 가 본 적이 있어요'.", "have been to"),
                 ("여행", "다른 곳에 다녀오는 것", "여름에 가족과 여행을 가요.", "In summer I travel with my family.", "'여행을 가다/하다'.", "travel"),
                 ("계획", "앞으로 하려고 정한 일", "주말에 등산할 계획이에요.", "I plan to go hiking this weekend.", "'~할 계획이에요'로 말해요.", "plan"),
             ]),
    23: dict(intro_ko="안녕하세요! 여러 사람과 모임을 잡으려면 일정 조율이 필요해요. 오늘은 약속을 정하고 시간을 맞추는 표현을 배워, 사회생활을 부드럽게 해 봐요.",
             intro_en="Hello! Setting up a group meetup needs schedule coordination. Today we'll learn to make plans and align times for smooth social life.",
             concept_ko="모임은 '약속을 잡다 → 시간 조율 → 확정' 순서로 진행돼요. 정중하게 제안하고 조율해요.",
             concept_en="A gathering flows as 'make plans → coordinate time → confirm'. Suggest and adjust politely.",
             dlg=[("이번 주에 모임 어때요?", "How about a meetup this week?"), ("좋아요. 시간 조율해서 약속을 잡아요.", "Sounds good. Let's coordinate times and set it up.")],
             vocab=[
                 ("약속을 잡다", "만날 약속을 정하는 것", "친구와 저녁 약속을 잡았어요.", "I made dinner plans with a friend.", "'약속을 잡다/정하다'.", "make plans"),
                 ("시간 조율", "서로 맞는 시간을 정하는 것", "다 같이 시간 조율이 필요해요.", "We all need to coordinate times.", "여러 일정을 맞출 때 써요.", "coordinate time"),
                 ("모임", "여러 사람이 함께 모이는 것", "금요일에 동아리 모임이 있어요.", "There's a club gathering on Friday.", "'모임이 있다/하다'.", "gathering"),
             ]),
    24: dict(intro_ko="안녕하세요! 드디어 마지막 시간이에요. 24주 동안 정말 잘 해내셨어요. 오늘은 그동안의 여정을 정리하고, 수료를 축하하며 발표로 마무리해 봐요.",
             intro_en="Hello! At last, the final lesson. You've done wonderfully over 24 weeks. Today we'll review the journey, celebrate your completion, and wrap up with a presentation.",
             concept_ko="끝까지 해낸 자신을 칭찬해요. 배운 것을 '발표'로 정리하면 실력이 한 번 더 단단해져요.",
             concept_en="Praise yourself for finishing. Summarizing what you learned in a 'presentation' makes your skills even stronger.",
             dlg=[("드디어 수료네요! 소감이 어때요?", "You're finally graduating! How do you feel?"), ("뿌듯해요. 이제 한국어로 자신 있게 말할 수 있어요!", "I'm proud. Now I can speak Korean with confidence!")],
             vocab=[
                 ("수료", "과정을 끝까지 마치는 것", "한국어 과정을 수료했어요.", "I completed the Korean course.", "'수료를 축하해요!'", "completion"),
                 ("발표", "사람들 앞에서 내용을 말하는 것", "내일 한국어로 발표가 있어요.", "I have a presentation in Korean tomorrow.", "천천히 또박또박 말해요.", "presentation"),
                 ("최종 평가", "마지막으로 실력을 확인하는 것", "오늘 최종 평가를 잘 봤어요.", "I did well on the final review today.", "그동안의 노력을 보여 줘요.", "final review"),
             ]),
}

EP = lambda w: f"KO-W{w:02d}"
PREFIX = lambda w: f"hangeul_w{w}_stickman"


def render_word(text, color=(28, 28, 28, 255)):
    f = ImageFont.truetype(FONT, 180)
    tmp = Image.new("RGBA", (max(1, len(text)) * 210 + 80, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    b = d.textbbox((0, 0), text, font=f)
    d.text((40 - b[0], 40 - b[1]), text, font=f, fill=color)
    bb = tmp.split()[3].getbbox()
    return tmp.crop((max(0, bb[0] - 14), max(0, bb[1] - 14), bb[2] + 14, bb[3] + 14))


def ensure_glyph(cur, has, text, key=None):
    key = key or f"word_{text}"
    fp = f"graphics/letters/{key}.png"
    out = os.path.join(LDIR, f"{key}.png")
    render_word(text).save(out)
    cur.execute("DELETE FROM assets WHERE file_path=?", (fp,))
    if has:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt,created_at) VALUES (?,?,?,?,?,datetime('now'))",
                    (text, key, "word", fp, "make_intermediate_rich"))
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (text, key, "word", fp, "make_intermediate_rich"))
    return key


SEARCH = ["assets/graphics", "assets/graphics/poses", "assets/graphics/letters", "assets/graphics/objects"]


def find_file(name):
    for d in SEARCH:
        p = os.path.join(ROOT, d, f"{name}.png")
        if os.path.exists(p):
            return os.path.relpath(p, ROOT).replace("\\", "/")
    return None


def resolve(cur, name):
    r = cur.execute("SELECT id FROM assets WHERE name_en=?", (name,)).fetchone()
    if r:
        return r[0]
    r = cur.execute("SELECT id FROM assets WHERE file_path LIKE ?", (f"%{name}.png",)).fetchone()
    if r:
        return r[0]
    fp = find_file(name)
    if not fp:
        raise FileNotFoundError(f"asset not found: {name}")
    typ = "character" if name.startswith("stickman_") else ("word" if name.startswith("word_") else "object")
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                (name, name, typ, fp, "auto rich"))
    return cur.lastrowid


def slug(text):
    return "ex_" + "".join(ch for ch in text if ch.isalnum() or ('가' <= ch <= '힣'))[:18]


def build(w, cur, has):
    char = CHARCFG[w]["char"]
    scale = CHARCFG[w]["scale"]
    cy = CHARCFG[w]["cy"]
    g = CHARCFG[w]["gestures"]
    rich = RICH[w]
    vocab = rich["vocab"]

    def gz(i):
        return [g[i % len(g)], g[(i + 1) % len(g)], g[(i + 2) % len(g)]]

    scenes = []
    # intro
    scenes.append(dict(cap_ko="안녕하세요!", cap_en="Welcome!", kr=rich["intro_ko"], en=rich["intro_en"],
                       gest=[g[0], g[len(g) - 1], g[1]], objs=[("title", CHARCFG[w].get("title_ko", ""))]))
    # concept
    scenes.append(dict(cap_ko="오늘의 핵심", cap_en="Key idea", kr=rich["concept_ko"], en=rich["concept_en"],
                       gest=gz(1), objs=[("overview", [v[0] for v in vocab])]))
    # per vocab (rich)
    for i, (word, mean, ex, ex_en, tip, en) in enumerate(vocab):
        kr = f"'{word}'는 {mean}라는 뜻이에요. 예를 들어, {ex} 라고 말해요. {tip} 자, 천천히 따라 해 보세요. '{word}'."
        en_s = f"'{word}' means {en}. For example: {ex_en} Now repeat slowly after me: '{word}'."
        scenes.append(dict(cap_ko=f"{word} — {mean}", cap_en=f"{word} = {en}", kr=kr, en=en_s,
                           gest=gz(i + 2), objs=[("vocab", (word, ex))]))
    # dialogue
    q, a = rich["dlg"][0], rich["dlg"][1]
    kr = f"이번엔 실제 상황이에요. 누군가 '{q[0]}' 하고 물으면, '{a[0]}' 하고 답할 수 있어요. 함께 연습해 봐요."
    en_s = f"Now a real situation. If someone asks, '{q[1]}', you can answer, '{a[1]}'. Let's practice together."
    scenes.append(dict(cap_ko="이렇게 말해요", cap_en="Real conversation", kr=kr, en=en_s,
                       gest=gz(3), objs=[("dialogue", (q[0], a[0]))]))
    # recap
    scenes.append(dict(cap_ko="정리해요", cap_en="Recap", gest=gz(4),
                       kr="오늘 배운 표현이에요. 소리 내어 한 번 더 읽어 볼까요? 잘 하고 있어요!",
                       en="Here are today's expressions. Let's read them aloud once more. You're doing great!",
                       objs=[("overview", [v[0] for v in vocab])]))
    # outro
    scenes.append(dict(cap_ko="다음 시간에 만나요!", cap_en="See you next time!", gest=[g[len(g) - 1], g[0], g[1]],
                       kr="훌륭해요! 오늘 표현을 오늘 하루 꼭 한 번 써 보세요. 작은 연습이 큰 실력이 돼요. 다음 시간에 또 만나요!",
                       en="Wonderful! Try using today's expressions at least once today. Small practice builds big skills. See you next time!",
                       objs=[("title", CHARCFG[w].get("title_ko", ""))]))

    # ---- write DB ----
    cur.execute("DELETE FROM scenes WHERE episode=?", (EP(w),))
    cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP(w),))
    nar_kr, nar_en, runtime = [], [], 0
    for seq, sc in enumerate(scenes, 1):
        dur = max(16, min(34, int(len(sc["kr"]) * 0.42)))
        runtime += dur
        nar_kr.append(sc["kr"]); nar_en.append(sc["en"])
        spec = {"pose": f"stickman_{sc['gest'][0]}", "gesture_seq": sc["gest"],
                "cap_ko": sc["cap_ko"], "cap_en": sc["cap_en"], "motion": "static"}
        cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,sfx,duration_sec) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (EP(w), seq, sc["kr"], sc["en"], json.dumps(spec, ensure_ascii=False), "", None, dur))
        objs = [(f"stickman_{sc['gest'][0]}", 285, cy, scale, 5, 0, "gesture")]
        kind, val = sc["objs"][0]
        if kind == "vocab":
            word, ex = val
            objs.append((f"word_{word}", 900, 300, wscale(word, 0.66), 3, 0, "fade_in"))
            k = ensure_glyph(cur, has, ex, slug(ex))
            objs.append((k, 905, 500, exscale(ex), 3, 0, "fade_in"))
        elif kind == "dialogue":
            qk = ensure_glyph(cur, has, "Q. " + val[0], slug("Q" + val[0]))
            ak = ensure_glyph(cur, has, "A. " + val[1], slug("A" + val[1]))
            objs.append((qk, 905, 300, exscale("Q. " + val[0]), 3, 0, "fade_in"))
            objs.append((ak, 905, 470, exscale("A. " + val[1]), 3, 0, "fade_in"))
        elif kind == "overview":
            objs += grid_words(val)
        elif kind == "title":
            objs.append((f"word_{val}", 905, 360, wscale(val, 0.5), 3, 0, "fade_in"))
        for (name, cx, cyy, scl, z, isp, mo) in objs:
            aid = resolve(cur, name)
            cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,is_point,motion_type) "
                        "VALUES (?,?,?,?,?,?,?,?,?)", (EP(w), seq, aid, cx, cyy, scl, z, isp, mo))

    title_ko = CHARCFG[w].get("title_ko", "")
    cur.execute("UPDATE episodes SET runtime_sec=?, narration_kr=?, narration_en=? WHERE code=?",
                (runtime, "\n".join(nar_kr), "\n".join(nar_en), EP(w)))
    cur.execute("UPDATE video_projects SET runtime_sec=?, n_scenes=? WHERE name=?", (runtime, len(scenes), PREFIX(w)))
    print(f"  {EP(w)} ({char or 'stickman'}): {len(scenes)} scenes, ~{runtime}s, vocab={len(vocab)} (RICH)")


def wscale(word, big=0.62):
    n = len(word.replace(" ", ""))
    return min(big, 1.6 / max(2, n))


def exscale(text):
    n = len(text.replace(" ", ""))
    return max(0.17, min(0.28, 3.6 / max(6, n)))


def grid_words(words):
    out = []
    n = len(words)
    cols = 2 if n > 3 else 1
    x0, dx = (760, 320) if cols == 2 else (905, 0)
    y0 = 250
    dy = 105 if n > 4 else 130
    for i, wd in enumerate(words):
        r, c = divmod(i, cols)
        out.append((f"word_{wd}", x0 + c * dx, y0 + r * dy, min(0.4, wscale(wd, 0.4)), 3, 0, "fade_in"))
    return out


def main():
    weeks = [int(a) for a in sys.argv[1:]] or list(RICH.keys())
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has = "created_at" in {r[1] for r in cur.execute("pragma table_info(assets)")}
    # vocab word glyphs (재생성, 큰 사이즈)
    for w in weeks:
        for (word, *_rest) in RICH[w]["vocab"]:
            ensure_glyph(cur, has, word)
        ensure_glyph(cur, has, CHARCFG[w].get("title_ko", ""))
    con.commit()
    for w in weeks:
        build(w, cur, has)
    con.commit()
    con.close()
    print("DONE (rich)")


if __name__ == "__main__":
    main()
