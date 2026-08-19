# -*- coding: utf-8 -*-
"""W1-2 v3 대사 — **12블록**으로 재배치한 나레이션 원천.

★사장님 지시(2026-08-14) "자막 → 나레이션 음성 → v2 문장 재배치, 1 2 3 순서대로."

v2(26씬)의 KO/EN 문장 26줄을 그대로 살리고, 이번에 새로 만든 **특별 컷 넷**의
문장을 더해 12블록에 나눠 담았다. 자막·TTS·화면 글자가 모두 이 한 파일에서 나온다
— 세 갈래가 어긋나지 않게 하려면 원천이 하나여야 한다.

  BLOCKS[i] = (블록번호, 제목, 씬파일, 초, [줄, ...])
  줄 = {"ko":…, "en":…, "box":…, "hangeul":…}
    box      좌상단 텍스트박스에 뜨는 짧은 말
    hangeul  화면 가운데 파라메트릭 획순으로 그릴 한글 (없으면 "")

★규칙
  · 화면에 뜨는 한글은 **자막과 나레이션에 다 들어 있어야 한다** (3채널 동기)
  · 자막은 번인하지 않는다 — srt 로 따로 낸다
  · 발음기호는 철자가 아니라 **실제 발음**으로 적는다
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

V2 = {d["s"]: d for d in json.load(io.open("W1_2/_v2_lines.json", encoding="utf-8"))}


def v2(*ns):
    """v2 씬 번호로 문장을 그대로 가져온다."""
    return [{"ko": V2[n]["ko"], "en": V2[n]["en"],
             "box": V2[n]["box"], "hangeul": V2[n]["hangeul"]} for n in ns if n in V2]


def L(ko, en, box="", hangeul=""):
    return {"ko": ko, "en": en, "box": box, "hangeul": hangeul}


# ── 특별 컷 넷의 새 문장 ────────────────────────────────────────────
GUARD = [
    L("광화문 앞에서는 하루에 두 번, 수문장 교대의식이 열려요.",
      "In front of Gwanghwamun, the changing of the guard happens twice a day.",
      "수문장 교대의식"),
    L("저 수문장이 걸어오지요? 아주 멀리서 점처럼 작게 시작해서 점점 커집니다.",
      "See the guard walking towards us? He starts tiny, far away, and grows.",
      "멀면 작게, 가까우면 크게"),
    L("사람이 가까이 올수록 커 보이는 것 — 이게 원근이에요.",
      "The closer someone comes, the bigger they look. That is perspective."),
    L("자, 오늘 첫 단어예요. 아이. 어린이를 뜻하는 말이지요.",
      "Here is today's first word. 아이 — it means a child.",
      "아이 [a-i] child", "아이"),
    L("아 하고 이, 두 모음만으로 만들어진 단어예요.",
      "ㅏ and ㅣ — a word made of two vowels alone."),
    L("그리고 이. 한 글자로도 단어가 됩니다. 우리 입 안의 이예요.",
      "And 이 — one letter is already a word. The teeth in your mouth.",
      "이 [i] tooth", "이"),
]

TUNNEL = [
    L("광화문광장에는 물로 만든 터널이 있어요.",
      "Gwanghwamun Square has a tunnel made of water.",
      "터널분수"),
    L("물줄기 일흔일곱 개가 아치를 이루고, 그 아래를 걸어 지나갑니다.",
      "Seventy-seven jets arch overhead, and you walk right through."),
    L("스틱맨이 저 끝까지 달려갔다가 돌아오네요. 멀어지면 작아지고, 가까워지면 커지지요.",
      "Stickman runs to the far end and back — smaller going, bigger returning."),
    # ★2026-08-17 — 여기서 우유를 먼저 소개하고 좌판(B6)에서 또 소개했다.
    #   낱말은 그 물건이 나오는 자리에서 한 번만 꺼낸다. 여기는 물 터널을 지나는
    #   장면이니 아치 아래를 걸으며 위를 올려다보는 말로 바꾼다.
    L("고개를 들면 물이 머리 위로 아치를 그려요. 아까 계단에서 배운 그 위예요.",
      "Look up — the water arches overhead. That's the 위 we learned on the steps.",
      "위 [wi] above"),
    L("물줄기 사이로 걸어 나가면, 저 앞 좌판에 오늘의 낱말이 기다려요.",
      "Walk on through the jets — the next words wait at the stall ahead."),
]

HANGEUL_F = [
    L("이곳에는 한글분수가 있어요. 바닥의 노즐 이백스물다섯 개가",
      "Here stands the Hangeul Fountain — two hundred twenty-five floor nozzles",
      "한글분수"),
    L("하늘 동그라미, 땅 네모, 사람 세모 모양으로 놓여 훈민정음 스물여덟 자를 그립니다.",
      "laid out as sky ○, earth □ and human △, drawing the twenty-eight letters."),
    L("자음 열네 자를 먼저 볼까요.",
      "Let us see the fourteen consonants first.",
      "자음 14자"),
    L("그리고 모음 열 자와, 지금은 쓰지 않는 옛 글자 네 자.",
      "Then ten vowels, and four old letters no longer used today.",
      "모음 10 + 옛 4"),
    L("아래아, 반치음, 옛이응, 여린히읗.",
      "Araea, Bansiot, Yet-ieung, Yeorin-hieut."),
    L("물처럼 나타났다 흩어지지요. 글자도 시대에 따라 변합니다.",
      "They rise and scatter like water. Letters change with the times."),
]

TKD = [
    L("광장에서는 태권도 시범도 열려요.",
      "The square also hosts taekwondo demonstrations.",
      "태권도 시범"),
    L("뛰어 옆차기, 오백사십도 회전 차기, 그리고 한 번 뛰어 네 장 격파.",
      "A flying side kick, a 540 spinning kick, and four boards in one jump."),
    L("저렇게 밖에서 하는 것을 야외라고 해요.",
      "Doing it outdoors like this is called 야외.",
      "야외 [ya-oe] outdoors", "야외"),
    L("야와 외. 오늘 배운 여덟 번째 말이에요.",
      "ㅑ and ㅚ — today's eighth word."),
    # ★2026-08-17 — 환호만 말하던 줄에 **야유**를 붙였다. 야외와 야유가 나란히
    #   ㅑ 로 시작해 짝이 되고, 시범을 보는 자리라 뜻이 바로 와 닿는다.
    L("스틱맨도 손을 들어 환호하네요. 반대로 못마땅해 소리치는 건 야유라고 해요.",
      "Stickman cheers, hand in the air. Booing is 야유 — ㅑ and ㅠ.",
      "야유 [ya-yu] booing", "야유"),
]

# ── 새로 만든 씬에 붙일 나레이션 (2026-08-14) ──────────────────────
# 26씬 동선을 다시 짜면서 **입 모양 씬**(S9·S11·S16·S20)과 **셋이 나오는 씬**
# (S23·S24)이 새로 생겼는데, v2 대본 26줄은 이미 다 쓰여 남는 문장이 없었다.
# 그대로 두면 좌판 블록만 37초가 무음이다 — 동작과 나레이션은 1:1이어야 한다.
# 그래서 새 씬이 하는 일을 그대로 말하는 문장을 보탠다.

PLAZA_MORE = [                                        # B3 — S3·S4 (아이 · 이)
    L("광화문 앞에 도착했어요. 여기서 첫 단어를 만나 볼까요?",
      "We've reached Gwanghwamun. Shall we meet our first word here?",
      "광화문 광장"),
    L("아이. 아 하고 이, 두 모음이 나란히 앉았어요.",
      "아이 — ㅏ and ㅣ, two vowels sitting side by side.",
      "아이 [a-i] child", "아이"),
]

STALL_MORE = [                                        # B6 — S8·S9·S10 (오이 · 우유)
    # ★2026-08-17 (사장님 지시) — 좌판 블록 12줄에서 **오이 도입이 세 번, 우유
    #   도입이 세 번** 되풀이됐다. 굴러오는 오이를 소개하는 말이 v2 에 이미 있는데
    #   여기서 또 소개하고, 뒤에서 또 했다. 되풀이 자리를 **새 낱말과 원리**로 바꾼다.
    L("아주 어린 아기는 유아라고 불러요. 유와 아, 이것도 모음뿐이지요.",
      "A very young baby is called a 유아 — ㅠ and ㅏ, vowels only again.",
      "유아 [yu-a] infant", "유아"),
    L("모음은 자음 없이도 혼자 설 수 있어요. 글자 세계에서는 드문 일이랍니다.",
      "Vowels can stand alone with no consonant at all — rare among writing systems."),
    # ★2026-08-17 — '오 — 이' 를 세 번째 되풀이하던 줄을 **이유**로 갈았다.
    #   좌판에서 물건을 고르는 자리라 "왜 고르나 = 이유" 가 그대로 붙는다.
    L("왜 그걸 골랐어요? 까닭을 이유라고 해요. 이와 유, 이것도 모음뿐이지요.",
      "Why did you pick it? The reason is 이유 — again, ㅣ and ㅠ, vowels only.",
      "이유 [i-yu] reason", "이유"),
    L("앞소리 하나만 바꿔도 뜻이 통째로 달라져요. 먹는 것이 마시는 것이 되지요.",
      "Change just the first sound and the meaning flips — from food to drink."),
    L("입술을 앞으로 쭉 내밀어 우. 그대로 유. 우유.",
      "Push your lips forward for 우, then 유. 우유.",
      "우 → 유", "우 유"),
]

BENCH_MORE = [                                        # B10 — S15·S16 (아우 · 따라 하기)
    L("친구와 나란히 앉아 볼까요? 아우는 손아래 형제를 뜻하는 말이에요.",
      "Let's sit side by side. 아우 means a younger sibling.",
      "아우 [a-u] younger sibling", "아우"),
    L("아 — 우. 입을 크게 벌렸다가, 앞으로 모읍니다.",
      "아 — 우. Open wide, then round forward.",
      "아 → 우", "아 우"),
    L("제 입 모양을 따라 해 보세요. 옆에 앉은 친구도 따라 하고 있죠?",
      "Copy my mouth. See — my friend beside me is copying too.",
      "따라 해 보세요"),
]

DUSK_MORE = [                                         # B12 — S23·S24 (카드 · 손 들기)
    L("오늘 배운 단어를 카드로 나눠 볼까요? 오이, 우유, 여우.",
      "Shall we share today's words as cards? 오이, 우유, 여우.",
      "오이 · 우유 · 여우", "오이 우유 여우"),
    L("해가 지고 등이 하나씩 켜집니다.",
      "The sun goes down and the lanterns come on, one by one."),
    L("마지막 등이 켜지면, 다 함께 손을 들어요.",
      "When the last lantern lights up, we all raise our hands."),
    L("야외. 바깥이라는 뜻이에요. 오늘 우리가 걸어 다닌 이곳이 바로 야외예요.",
      "야외 — outdoors. That's exactly where we've been walking all day.",
      "야외 [ya-oe] outdoors", "야외"),
]

STEPS_MORE = [                                        # B4 — 계단 (아이 · 이)
    L("계단을 하나씩 내려가 볼까요? 한 계단에 한 소리예요.",
      "Shall we step down one at a time? One step, one sound.",
      "한 계단 = 한 소리"),
    # ★2026-08-17 — 바로 앞줄(v2 6)이 "한 계단에 한 소리, 붙이면 아이" 를 이미
    #   말한다. 같은 말을 두 번 하지 않고, 여기서는 **글자 모양**을 짚는다.
    L("두 글자 다 곧게 선 모양이지요. 서 있는 사람을 본떠 만든 글자예요.",
      "Both letters stand upright — shaped after a person standing tall.",
      "선 사람 모양"),
    L("이번엔 이 하나만. 한 글자로도 단어가 됩니다. 우리 입 안의 치아예요.",
      "Now just 이. A single letter is already a word — the tooth in your mouth.",
      "이 [i] tooth", "이"),
    # ★2026-08-17 (사장님 지시) — "아이 이 오이 우유만 계속 반복해 지루하다.
    #   모음만으로 만든 단어가 많으니 더 넣자." 여기 있던 '이=치아' 되풀이 줄을
    #   **위**로 갈아 끼웠다. 계단 위에 세종대왕이 서 있으니 뜻이 눈앞에 있다.
    L("계단 위를 보세요. 위. 우와 이가 만나 한 글자가 됐어요. 높은 쪽을 뜻해요.",
      "Look up the steps. 위 — ㅜ and ㅣ joined into one letter. It means above.",
      "위 [wi] above", "위"),
    L("입을 옆으로 활짝 당기면 이 소리가 나요. 이.",
      "Pull your lips wide to the sides and you get 이.",
      "입을 옆으로"),
]

STALL_MORE2 = [                                       # B6 — 뜻을 한 번 더 짚는다
    # ★2026-08-17 — 여기서 오이·우유 뜻을 **세 번째로** 되풀이하고 있었다.
    #   초록과 하양을 한 줄에 나란히 놓아 한 번만 짚고, 남는 자리는 정리에 쓴다.
    L("초록빛 길쭉한 오이, 하얗고 고소한 우유. 좌판에서 둘을 만났어요.",
      "The long green 오이, the mild white 우유 — we met them both at the stall."),
    L("자음이 하나도 없는 낱말이 오늘만 벌써 여럿이지요.",
      "That's already several words today without a single consonant."),
]

FOUNTAIN_MORE = [                                     # B7 — 원형 분수대 (오)
    L("분수가 하늘로 솟았어요. 오! 하고 놀랐지요?",
      "The fountain shoots up. 오! — surprised, aren't you?",
      "오 [o] oh!", "오"),
    # ★2026-08-17 — '오' 를 한 번 더 설명하던 줄을 **우와**로 갈았다.
    #   물이 솟는 자리라 감탄이 자연스럽고, 오(놀람)와 우와(감탄)가 짝이 된다.
    L("더 크게 놀라면 우와. 우와도 자음 없이 모음만으로 씁니다.",
      "For a bigger surprise — 우와. Wow. Vowels only again, no consonants.",
      "우와 [u-wa] wow", "우와"),
]

# ★2026-08-17 — B11 뒤 두 줄(v2 21·22)은 **B10 과 같은 말**이었다. 소리의 온도와
#   ㅣ 의 예외는 벤치에서 이미 다 설명했다. 그 자리를 새 낱말 둘에 내준다.
#   엉덩방아(S20)와 은행잎 길(S21·S22)이 뜻을 그대로 보여 준다.
FOX_MORE = [                                          # B11 — 여우 · 은행나무길
    L("아야. 놀라서 엉덩방아를 찧었네요. 아프면 아야 하고 소리치지요.",
      "아야 — ouch! A tumble on the leaves. That's what you say when it hurts.",
      "아야 [a-ya] ouch", "아야"),
    L("노란 잎이 내리는 길을 천천히 걸어요. 이런 느긋한 마음을 여유라고 해요.",
      "Walking slowly under the falling leaves — that calm is 여유, leisure.",
      "여유 [yeo-yu] leisure", "여유"),
]

STEPS_MORE2 = [                                       # B4 — 세종대왕 계단·난간
    L("이 계단 위에서 세종대왕이 우리를 내려다보고 계세요. 한글을 만드신 분이지요.",
      "King Sejong looks down from the top of these steps — the man who made Hangeul.",
      "세종대왕"),
    L("난간을 잡고 광장을 한번 보세요. 오늘 배울 말들이 저기 다 숨어 있어요.",
      "Hold the railing and look out over the plaza. Today's words are all hiding out there."),
]

DUSK_END = [                                          # B12 — S25 거울 · S26 마무리
    L("거울을 꺼내 볼까요? 입 모양을 직접 보면서 따라 해 보세요.",
      "Take out a mirror. Watch your own mouth as you copy me.",
      "거울로 입 모양 보기"),
    L("아, 이, 오, 우. 입이 어떻게 바뀌는지 보이지요?",
      "아, 이, 오, 우. See how the shape changes each time?",
      "아 이 오 우", "아 이 오 우"),
    # ★2026-08-17 — 낱말이 여덟에서 **열넷**으로 늘었다(위·이유·우와·야유·아야·여유).
    #   한 줄에 열넷을 다 부르면 숨이 차서, 여덟 + 여섯 두 줄로 나눠 부른다.
    L("오늘 배운 낱말을 다시 볼까요? 아이, 이, 오이, 우유, 오, 아우, 여우, 야외.",
      "Let's see today's words again — 아이, 이, 오이, 우유, 오, 아우, 여우, 야외.",
      "오늘의 낱말"),
    L("여기에 위, 이유, 우와, 야유, 아야, 여유, 유아까지. 모두 열다섯 낱말이에요.",
      "And 위, 이유, 우와, 야유, 아야, 여유, 유아 — fifteen words in all.",
      "낱말 15개"),
    L("모두 모음만으로 만든 말이에요. 자음은 하나도 쓰지 않았지요.",
      "Every one is built from vowels alone. Not a single consonant."),
    L("다음 시간에는 드디어 자음을 만나 볼 거예요.",
      "Next time, we finally meet the consonants.",
      "다음 시간 · 자음"),
    L("오늘도 잘 따라와 주셔서 고마워요. 다음 시간에 또 만나요!",
      "Thank you for following along. See you next time!"),
]

# ── 12블록 ─────────────────────────────────────────────────────────
# (번호, 제목, 씬 영상, 초, 줄들)
BLOCKS = [
    (1, "도착", "W1_2/_scn/s1_plaza.mp4", 14.0, v2(1, 2)),
    (2, "수문장 교대식", "W1_2/motion6/guard_scene.mp4", 26.0, GUARD),
    # ★2026-08-14 — 비어 있던 네 블록을 26씬 동선 렌더로 채웠다.
    #   길이가 그대로 맞는다: B3=S3+S4(34s) · B6=S8+S9+S10(60s) · B10=S15+S16(40s)
    #   B12=S23+S24(42s, 4초는 assemble 이 늘린다)
    (3, "광화문 앞", "W1_2/_scenes/w1d2_s3_4.mp4", 22.0, v2(3, 4) + PLAZA_MORE),
    # ★2026-08-15 — 옛 `_steps/steps_scene.mp4` 는 **서양 왕관을 쓴 동상** 계단이었다.
    #   세종대왕 계단(steps_seat.png) 배경의 S5+S6+S7 렌더로 갈아 끼운다. 22+20+18=60초.
    # ★2026-08-17 (사장님 승인) — 계단은 **고친 S5+S6** 로 갈아 끼운다.
    #   뒷모습 걷기(walkback 투명컷 10장·머리 흰색)로 올라가 정면으로 앉고, 정면
    #   걷기로 내려와 오른편으로 달려 나간다. 42초. S7 은 뺐다 — 같은 계단에서
    #   같은 설명이 한 번 더 나와 늘어졌다.
    #   나레이션은 겹치던 STEPS_MORE #0("계단을 하나씩 내려가 볼까요")만 뺐다 —
    #   바로 앞 v2(6) 이 이미 같은 말을 한다. `이`(치아) 도입줄은 그대로 둔다.
    (4, "계단", "W1_2/_scenes/w1d2_s5_6_v2.mp4", 42.0,
     v2(5, 6) + STEPS_MORE[1:] + STEPS_MORE2),
    # ★2026-08-15 (교정앱 r4 #4) — v3 는 배경을 `fs + fs[::-1]` 로 되감아 물줄기가
    #   거꾸로 빨려 들어갔다. tunnel_scene.py 를 고쳐 **정상 재생 + 마지막 프레임 유지**
    #   로 다시 뽑은 v4 를 쓴다.
    (5, "터널분수", "W1_2/motion6/tunnel_scene_v4.mp4", 18.4, TUNNEL),
    (6, "좌판", "W1_2/_scenes/w1d2_s8_9_10.mp4", 60.0,
     v2(8, 9, 10, 11, 12) + STALL_MORE + STALL_MORE2),
    # ★2026-08-15 (교정앱 r4 #5) — 옛 `_s11/s11_fountain.mp4` 는 주캐릭터와 보조가
    #   몸통째 겹쳐 있었고 그 영상을 만든 스크립트가 남아 있지 않다.
    #   26씬의 S13(분수)이 마침 같은 22초라 그것으로 갈아 끼운다(겹침은 교정27로 해소).
    (7, "원형 분수대", "W1_2/_scenes/w1d2_s13.mp4", 19.0, v2(13, 14) + FOUNTAIN_MORE),
    (8, "한글분수 네온", "W1_2/motion6/fountain_neon.mp4", 20.4, HANGEUL_F),
    (9, "태권도", "W1_2/motion6/tkd_show_v7.mp4", 21.0, TKD),
    (10, "벤치", "W1_2/_scenes/w1d2_s15_16.mp4", 36.0, v2(15, 16, 17, 18) + BENCH_MORE),
    # ★2026-08-17 (교정앱 r9 #6·#7) — "여우씬 **뒷부분은 반복되니** 그것을 달리기 신으로
    #   바꾸어줘. 2/3는 여우신, 1/3은 저 멀리 달려갔다 돌아오는 신. 달리기 신은 전에
    #   만들었어. 교정까지 다 했는데 **찾아서 써라**."
    #   → `_fox/fox_scene.mp4` 는 **8초뿐**이라 24초 블록에서 세 번 되풀이됐다.
    #     8월 13일에 만들어 둔 `_road/road_scene.mp4`(은행나무길, 달려갔다 휙 돌아
    #     달려온다 · 15.3초)를 찾아 뒤에 붙였다 → `_fox/fox_road.mp4` 23.3초.
    (11, "여우·은행나무길", "W1_2/_fox/fox_road.mp4", 23.3, v2(19, 20) + FOX_MORE),
    # ★2026-08-15 — 설명도 다 못 하고 끊겼다(사장님 지적). S25(거울)·S26(퇴장)을 붙여
    #   74초로 늘리고 마무리 나레이션을 보태 제대로 끝낸다.
    # ★2026-08-17 (사장님 지시) — "노을씬이 너무 길어. 노을씬과 별씬의 길이를 비슷하게
    #   해서 나레이션을 넣어서 조절해." 한 덩어리 62초를 **노을 30초 / 별 32초** 두
    #   블록으로 쪼갰다. 늘어진 원인은 길이가 아니라 **겹치는 나레이션**이었다 —
    #   v2(25)"거울 앞에서 연습" 은 DUSK_END #0 거울과, v2(24)"일곱 낱말 정리" 는
    #   DUSK_END #2 여덟 낱말과 같은 말이었다. 둘 다 뒤엣것(더 완전한 쪽)만 남긴다.
    #   v2(26)"ㅇ 을 모음에 붙여 음절을 만든다" 는 DUSK_END #4 보다 구체적이라
    #   그쪽을 살리고 #4 를 뺐다.
    (12, "노을 등", "W1_2/_scenes/w1d2_s23_24.mp4", 30.0,
     v2(23) + DUSK_MORE),
    (13, "별 · 마무리", "W1_2/_scenes/w1d2_s25_26.mp4", 32.0,
     DUSK_END[:4] + v2(26) + DUSK_END[5:]),
]


def all_lines():
    for n, title, clip, sec, lines in BLOCKS:
        for i, l in enumerate(lines):
            yield n, title, i, l


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    tot_sec = sum(b[3] for b in BLOCKS)
    tot_ko = sum(len(l["ko"]) for _, _, _, l in all_lines())
    n_line = sum(1 for _ in all_lines())
    print("블록 %d · 줄 %d · KO %d자 · 영상 %.1f초 (%d분 %d초)"
          % (len(BLOCKS), n_line, tot_ko, tot_sec, tot_sec // 60, tot_sec % 60))
    print("읽는 데 필요한 시간 대략 %.0f초 — 영상보다 %+.0f초"
          % (tot_ko / 5.5, tot_ko / 5.5 - tot_sec))
    print()
    for n, title, clip, sec, lines in BLOCKS:
        ko = sum(len(l["ko"]) for l in lines)
        hg = [l["hangeul"] for l in lines if l["hangeul"]]
        print("  %2d %-16s %5.1f초 · %d줄 · KO %3d자 (%4.1f초분) · 화면한글 %s"
              % (n, title, sec, len(lines), ko, ko / 5.5, " ".join(hg) or "-"))
