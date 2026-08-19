# -*- coding: utf-8 -*-
"""W1-2 v4 대사 — **낱말 하나는 한 곳에서만 꺼낸다.**

★사장님 지시(2026-08-17)
  "아직도 전반부에 아이가 중복되고 있고 우유가 두 번 나오는데, 앞엣것은 빼고
   뒤에 **우유가 떨어지는 배경**에서 우유와 이유를 설명하자. 시나리오·나레이션·
   자막을 다 바꾼다고 생각해. 동영상 순서나 동영상은 그대로 하고. 더 짧아도 되니
   중복은 빼고, 잘 만든 동영상은 빼지 말고 현명하게 단어를 잘 섞어봐."

## v3 가 왜 지루했나
낱말을 **여러 블록에서 거듭 도입**했다. `아이` 는 수문장·광화문·계단 세 곳에서
저마다 "오늘의 첫 낱말" 이라고 소개했고, `우유` 는 **오이가 굴러오는 장면**에서
먼저 꺼낸 뒤 우유가 떨어지는 장면에서 또 꺼냈다. 배경이 말하는 것과 입이 말하는
것이 어긋나면, 같은 말을 두 번 듣는 것보다 더 지루해진다.

## v4 의 규칙
1. **낱말 하나 = 도입 한 곳.** 뜻·자모·발음을 그 자리에서 한 번에 끝낸다.
2. 도입 자리는 **배경이 그 낱말을 보여 주는 곳**으로 정한다.
   좌판 60초는 앞 40초가 오이(S8·S9), 뒤 20초가 우유(S10)다 — 그대로 따른다.
3. 다시 부르는 것은 **복습으로만**. 새 설명을 붙이지 않는다.
4. 영상·순서·길이는 건드리지 않는다. 바뀌는 것은 말뿐이다.

## 낱말이 어디서 나오나 (15개)
  B3 광화문   아이          B4 계단     이 · 위
  B6 좌판앞   오이 · 유아    B6 좌판뒤   우유 · 이유
  B7 분수대   오 · 우와      B9 태권도   야외 · 야유
  B10 벤치    아우          B11 여우·은행길  여우 · 아야 · 여유

  줄 = {"ko":…, "en":…, "box":…, "hangeul":…}
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

V2 = {d["s"]: d for d in json.load(io.open("W1_2/_v2_lines.json", encoding="utf-8"))}


def v2(*ns):
    return [{"ko": V2[n]["ko"], "en": V2[n]["en"],
             "box": V2[n]["box"], "hangeul": V2[n]["hangeul"]} for n in ns if n in V2]


def L(ko, en, box="", hangeul=""):
    return {"ko": ko, "en": en, "box": box, "hangeul": hangeul}


# ── B1 도착 (14초) ────────────────────────────────────────────────
ARRIVE = [
    L("안녕하세요! 지난 시간에는 기본 모음 여덟 자를 배웠지요. ㅏ, ㅓ, ㅗ, ㅜ, ㅡ, ㅣ, ㅐ, ㅔ.",
      "Hello! Last time we learned the eight simple vowels — ㅏ, ㅓ, ㅗ, ㅜ, ㅡ, ㅣ, ㅐ, ㅔ.",
      "지난 시간 · 기본 모음 8자"),
    L("오늘은 그 모음만으로 낱말을 만들어 봅니다. 자음은 하나도 쓰지 않아요.",
      "Today we'll build whole words from those vowels alone — not a single consonant.",
      "오늘 · 모음만으로 낱말"),
]

# ── B2 수문장 교대식 (26초) ────────────────────────────────────────
# ★v3 에서는 여기서 `아이` 를 꺼냈다. 수문장이 걸어오는 화면과 아무 상관이 없어
#   말과 그림이 따로 놀았다. 이 블록은 **원근**만 맡는다 — 뒤에서 캐릭터가
#   작아졌다 커지는 장면이 계속 나오므로, 여기서 눈을 길들여 두면 그다음이 쉽다.
GUARD = [
    L("광화문 앞에서는 하루에 두 번, 수문장 교대의식이 열려요.",
      "In front of Gwanghwamun, the changing of the guard happens twice a day.",
      "수문장 교대의식"),
    L("북소리에 맞춰 걸음을 맞추고, 창을 세워 자리를 지킵니다.",
      "They march to the drum, spears upright, holding their posts."),
    L("저 수문장이 걸어오지요? 아주 멀리서 점처럼 작게 시작해서 점점 커집니다.",
      "See the guard walking towards us? He starts tiny, far away, and grows.",
      "멀면 작게, 가까우면 크게"),
    L("사람이 가까이 올수록 커 보이는 것 — 이게 원근이에요.",
      "The closer someone comes, the bigger they look. That is perspective."),
    L("멀 때는 점만 하던 사람이, 이제 얼굴까지 보이지요.",
      "A dot in the distance — and now you can see his face."),
    L("오늘은 이렇게 광장을 걸어 다니며 낱말을 하나씩 주워 볼 거예요.",
      "Today we'll walk this square and pick up words as we go."),
]

# ── B3 광화문 앞 (22초) — ★아이는 여기서만 ────────────────────────
PLAZA = [
    L("글로 쓸 때는 앞에 작은 동그라미 ㅇ이 붙어요. 소리는 나지 않는 자리지기예요.",
      "When we write, a small circle ㅇ sits in front — but it makes no sound at all.",
      "ㅇ은 소리 없는 자리지기"),
    L("광화문에 도착했어요. 자, 오늘의 첫 낱말을 만나 볼까요?",
      "We've reached Gwanghwamun. Shall we meet today's first word?",
      "광화문 광장"),
    L("아이. 어린이를 뜻하는 말이에요. ㅏ와 ㅣ, 모음 두 개가 나란히 앉았지요.",
      "아이 — it means a child. ㅏ and ㅣ, two vowels sitting side by side.",
      "아이 [a-i] child", "아이"),
    L("아 — 이. 천천히 붙여 보세요. 아이.",
      "아 — 이. Slowly now, join them. 아이.",
      "아 + 이 → 아이", "아 이"),
]

# ── B4 계단 (42초) — ★이 · 위 ─────────────────────────────────────
# ★v3 는 여기서 `아이` 를 또 소개했다(광화문에 이어 세 번째). 계단은 **한 칸에
#   한 소리**라는 그림을 가진 자리이니, 한 글자짜리 낱말 `이` 와 계단 꼭대기가
#   그대로 뜻이 되는 `위` 를 맡긴다.
STEPS = [
    L("계단을 하나씩 내려가 볼까요? 한 계단에 한 소리예요.",
      "Shall we step down one at a time? One step, one sound.",
      "한 계단 = 한 소리"),
    L("이. 한 글자만으로도 낱말이 됩니다. 우리 입 안의 치아를 뜻해요.",
      "이 — a single letter is already a word. It's the tooth in your mouth.",
      "이 [i] tooth", "이"),
    L("입을 옆으로 활짝 당기면 이 소리가 나요.",
      "Pull your lips wide to the sides and you get 이.",
      "입을 옆으로"),
    L("아까 배운 아와 이, 두 글자 다 곧게 선 모양이지요. 서 있는 사람을 본떴어요.",
      "ㅏ and ㅣ both stand upright — shaped after a person standing tall.",
      "선 사람 모양"),
    L("계단 위를 보세요. 위. 우와 이가 만나 한 글자가 됐어요. 높은 쪽을 뜻해요.",
      "Look up the steps — 위. ㅜ and ㅣ joined into one letter. It means above.",
      "위 [wi] above", "위"),
    L("이 계단 위에서 세종대왕이 우리를 내려다보고 계세요. 한글을 만드신 분이지요.",
      "King Sejong looks down from the top of these steps — the man who made Hangeul.",
      "세종대왕"),
    # ★교정(사장님 2026-08-18) — "이 '난간 ~ 있어요' 나레이션과 자막은 빼는 것이
    #   좋겠다. 한글에서도 빼고 영어판에서도 빼자." 계단을 내려오는 대목이라
    #   난간을 잡는 그림도 없었다.
    L("계단을 다 내려왔어요. 이제 물로 만든 터널로 가 볼까요?",
      "Down the last step. Shall we head for the tunnel made of water?"),
]

# ── B5 터널분수 (18.4초) — 낱말 도입 없음 ─────────────────────────
# ★v3 는 여기서 `우유` 를 꺼냈다. 물 터널과 우유는 아무 관계가 없고, 좌판에서
#   우유가 실제로 떨어질 때 또 꺼냈다. 여기서는 **위** 를 한 번 되짚기만 한다.
# ★교정(사장님 2026-08-18) — "배경은 **뒷걸음 치지 말고 세우지도 말고** 사람이 앞으로
#   걷기만 좀 느리게 계속 상영하고, **캐릭터도 세우지 말고** 끝까지 달려 갔다가
#   돌아 오게." 멈춰 서는 구간을 다 걷어내니 씬이 **16초**가 되었다.
#   나레이션을 그 안에 넣어야 배경도 캐릭터도 멎지 않는다 — 다섯 줄을 셋으로 줄였다.
#   ('위' 복습 줄은 뺐다. 계단에서 이미 가르쳤고, 여기서는 달리기가 주인공이다.)
TUNNEL = [
    L("광화문광장에는 물로 만든 터널이 있어요. 물줄기 일흔일곱 개가 아치를 이룹니다.",
      "Gwanghwamun Square has a tunnel of water — seventy-seven jets arching overhead.",
      "터널분수"),
    L("스틱맨이 저 끝까지 달려갔다 돌아오네요. 멀어지면 작아지고, 가까워지면 커지지요.",
      "Stickman runs to the far end and back — smaller going, bigger returning."),
    L("물줄기 사이를 지나면, 저 앞 좌판에 오늘의 낱말이 기다려요.",
      "Walk on through the jets — the next words wait at the stall ahead."),
]

# ── B6 좌판 (60초) ────────────────────────────────────────────────
# ★영상은 **앞 40초가 오이**(S8 굴러옴 · S9 입 모양), **뒤 20초가 우유**(S10 떨어짐)다.
#   사장님 지시대로 우유는 **떨어지는 그 자리에서** 처음 꺼내고, 까닭을 묻는
#   `이유` 를 나란히 붙인다. 앞쪽은 오이와 `유아` 로만 채운다.
STALL = [
    # ── 앞 40초 · 오이 ──
    L("어? 뭔가 굴러오네요. 오늘의 두 번째 낱말, 오이예요.",
      "Oh — something's rolling this way. Today's second word: 오이, a green cucumber.",
      "오이 [o-i] cucumber", "오이"),
    L("입을 동그랗게 모아 오. 그다음 옆으로 당겨 이. 오 — 이. 오이.",
      "Round your lips for 오, then pull them wide for 이. 오 — 이. 오이.",
      "오 → 이", "오 이"),
    L("아이와 오이. 끝소리가 같지요? 앞소리 하나만 바꿨는데 뜻이 아주 달라졌어요.",
      "아이 and 오이 — same ending. Change one sound in front and the meaning changes.",
      "아이 · 오이"),
    L("초록빛으로 길쭉한 그것, 바로 먹는 오이랍니다.",
      "The long green one — that's the cucumber you eat."),
    L("좌판 옆에 아주 어린 아기가 있네요. 이런 아기를 유아라고 불러요.",
      "There's a tiny baby by the stall. A very young child is a 유아.",
      "유아 [yu-a] infant", "유아"),
    L("유와 아. 이것도 자음 없이 모음뿐이에요.",
      "ㅠ and ㅏ — vowels only again, no consonant."),
    L("모음은 자음 없이도 혼자 설 수 있어요. 글자 세계에서는 드문 일이랍니다.",
      "Vowels can stand alone with no consonant — rare among writing systems."),
    L("모음 두 개가 나란히 놓이면, 두 소리가 그대로 이어져 들립니다.",
      "Put two vowels side by side and you hear both sounds, one after the other."),
    L("앞 글자와 뒤 글자, 크기가 같지요? 한글은 네모 칸에 맞춰 씁니다.",
      "Both letters are the same size — Hangeul is written to fit a square block.",
      "네모 칸에 맞춰"),
]

# ── B6b 좌판·우유 (S10 · 20초) ────────────────────────────────────
# ★교정(사장님 2026-08-18) — "영어판 배경 나레이션 자막 타이밍이 안 맞다.
#   **특히 밀크에 관한 것** 할 때. 다시 체크해 보고 다 새로 맞춰."
#   좌판을 한 블록(68초)으로 두었더니, 입 모양 구간을 늘린 만큼 **우유가 떨어지는
#   시각이 +40 에서 +54.6초로 밀렸는데** "우유가 떨어져요" 는 +42.1초에 그대로
#   있었다 — 12.5초 어긋났다. 씬을 **오이(S8+S9) / 우유(S10)** 두 블록으로 쪼개
#   블록 머리가 곧 S10 머리가 되게 한다. 그러면 우유는 언제나 **+6.6초**에 떨어진다.
#   첫 줄은 낙하 직전을 가리키는 짧은 말로 두어, 두 번째 줄이 낙하 순간에 걸친다.
STALL_MILK = [
    L("어? 좌판 오른편이 흔들리네요.",
      "Wait — something's tipping over on the right side of the stall."),
    L("조심! 저기 우유가 떨어져요. 하얗고 고소한 우유예요.",
      "Careful — the milk is falling! 우유 — sweet white milk.",
      "우유 [u-yu] milk", "우유"),
    L("입술을 앞으로 쭉 내밀어 우. 그대로 유. 우 — 유. 우유.",
      "Push your lips forward for 우, then 유. 우 — 유. 우유.",
      "우 → 유", "우 유"),
    L("왜 얼른 주웠을까요? 그 까닭을 이유라고 해요.",
      "Why pick it up so fast? That reason is 이유.",
      "이유 [i-yu] reason", "이유"),
    L("이와 유. 이유도 모음 두 개로만 만들어진 말이지요.",
      "ㅣ and ㅠ — 이유 is made of two vowels too."),
]

# ── B7 원형 분수대 (19초) — ★오 · 우와 ────────────────────────────
FOUNTAIN = [
    L("우아! 분수가 하늘로 솟았어요. 놀랄 때 내는 소리, 오!",
      "Whoa! The fountain shoots up. The sound you make when startled — 오!",
      "오 [o] oh!", "오"),
    L("오. 한 글자뿐이지만 어엿한 낱말이에요.",
      "오 — just one letter, and a real word all the same."),
    L("게다가 오는 숫자 다섯이기도 해요. 하나, 둘, 셋, 넷, 다섯 — 오!",
      "And 오 also means five. One, two, three, four, five — 오!",
      "오 = 5"),
    L("더 크게 놀라면 우와. 이것도 모음만으로 씁니다.",
      "For a bigger surprise — 우와. Wow. Vowels only again.",
      "우와 [u-wa] wow", "우와"),
]

# ── B8 한글분수 네온 (20.4초) — 훈민정음 이야기 ───────────────────
HANGEUL_F = [
    L("이곳에는 한글분수가 있어요. 바닥의 노즐 이백스물다섯 개가",
      "Here stands the Hangeul Fountain — two hundred twenty-five floor nozzles",
      "한글분수"),
    # ★교정(r15 #1) — "여기 천 지 인 ㆍ ㅡ ㅣ 을 자막에 이렇게 다시 바꾸어서 표현해 줘."
    #   옛 자막은 ○ □ △ 라고 적어 **훈민정음 제자원리와 달랐다.** 모음의 바탕이 되는
    #   기본자 셋은 하늘 ㆍ, 땅 ㅡ, 사람 ㅣ 다 — 오늘 배운 모음이 모두 여기서 나온다.
    L("하늘 ㆍ, 땅 ㅡ, 사람 ㅣ. 천지인 석 자가 모든 모음의 바탕이에요.",
      "Heaven ㆍ, Earth ㅡ, Human ㅣ — these three shapes make every vowel.",
      "천 ㆍ · 지 ㅡ · 인 ㅣ"),
    # ★교정(한글판 r1) — 한글분수 블록은 배경이 20.4초짜리 고정 클립이라 늘릴 수
    #   없다. 한국어 나레이션이 7.3초 넘쳐 끝에서 멈춰 서 있었다. 자음·모음·옛 글자를
    #   **한 줄로 합쳐** 그 시간을 없앤다(내용은 그대로다).
    L("자음 열네 자, 모음 열 자, 그리고 지금은 쓰지 않는 옛 글자 네 자.",
      "Fourteen consonants, ten vowels, and four old letters no longer used today.",
      "자음 14 · 모음 10 · 옛 4"),
    L("아래아, 반치음, 옛이응, 여린히읗.",
      "Araea, Bansiot, Yet-ieung, Yeorin-hieut."),
    L("물처럼 나타났다 흩어지지요. 글자도 시대에 따라 변합니다.",
      "They rise and scatter like water. Letters change with the times."),
]

# ── B9 태권도 (21초) — ★야외 · 야유 ───────────────────────────────
TKD = [
    L("광장에서는 태권도 시범도 열려요.",
      "The square also hosts taekwondo demonstrations.",
      "태권도 시범"),
    L("뛰어 옆차기, 오백사십도 회전 차기, 그리고 한 번 뛰어 네 장 격파.",
      "A flying side kick, a 540 spinning kick, and four boards in one jump."),
    L("저렇게 밖에서 하는 것을 야외라고 해요. 야와 외예요.",
      "Doing it outdoors like this is 야외 — ㅑ and ㅚ.",
      "야외 [ya-oe] outdoors", "야외"),
    L("스틱맨도 구경꾼 사이에서 손을 들어 환호하네요.",
      "Stickman cheers from among the crowd, hand in the air."),
    L("반대로 못마땅해 소리치는 건 야유라고 해요. 야와 유예요.",
      "Shouting in disapproval is 야유 — ㅑ and ㅠ.",
      "야유 [ya-yu] booing", "야유"),
]

# ── B10 벤치 (36초) — ★아우 ───────────────────────────────────────
BENCH = [
    L("벤치에 누가 앉아 있네요. 여섯 번째 낱말, 아우예요. 손아래 형제를 뜻해요.",
      "Someone's on the bench. Sixth word — 아우, a warm word for a younger sibling.",
      "아우 [a-u] younger sibling", "아우"),
    L("아에서 우로. 입을 크게 벌렸다가 앞으로 모읍니다. 아 — 우.",
      "From ㅏ to ㅜ. Open wide, then round forward. 아 — 우.",
      "아 → 우", "아 우"),
    L("소리에도 온도가 있어요. ㅏ와 ㅗ는 밝고 따뜻하고, ㅓ와 ㅜ는 어둡고 서늘하지요.",
      "Sounds have a temperature too. ㅏ and ㅗ are bright and warm; ㅓ and ㅜ are darker."),
    L("온도가 같으면 자석처럼 착 붙어요. 따뜻한 것끼리, 서늘한 것끼리.",
      "Same temperature, and they snap together like magnets — warm with warm, cool with cool."),
    L("ㅣ만은 예외예요. 선 사람을 본뜬 글자라 양쪽 모두와 잘 어울립니다.",
      "Only ㅣ is the exception — shaped after a standing person, it gets along with both."),
    L("나란히 앉아 입 모양을 맞춰 볼까요?",
      "Let's sit side by side and match our mouths."),
    L("제 입 모양을 따라 해 보세요. 옆에 앉은 친구도 따라 하고 있지요?",
      "Copy my mouth. See — my friend beside me is copying too.",
      "따라 해 보세요"),
]

# ── B11 여우 · 은행나무길 (23.3초) — ★여우 · 아야 · 여유 ──────────
FOX = [
    L("쉿… 덤불에서 뭔가 움직여요. 일곱 번째 낱말, 여우예요.",
      "Shh… something's in the bush. Seventh word — 여우, the red fox.",
      "여우 [yeo-u] fox", "여우"),
    L("어, 숨어 버렸네요. 여 — 우. 여우.",
      "Oh, it's gone. 여 — 우. 여우.",
      "여 → 우", "여 우"),
    L("아야. 놀라서 엉덩방아를 찧었네요. 아프면 아야 하고 소리치지요.",
      "아야 — ouch! A tumble on the leaves. That's what you say when it hurts.",
      "아야 [a-ya] ouch", "아야"),
    L("노란 잎이 내리는 길을 천천히 걸어요. 이런 느긋한 마음을 여유라고 해요.",
      "Walking slowly under the falling leaves — that calm is 여유, leisure.",
      "여유 [yeo-yu] leisure", "여유"),
]

# ── B12 노을 등 (30초) ────────────────────────────────────────────
# ★교정(r15 #2·#3) — "그림 보고 말하기, 카드에 그림이 하나도 안 보인다. 구현하기
#   힘들 것 같으니 빼 버리자. 중복되기도 하고. 여기는 **카드 들고 있는 캐릭터도
#   다 빼자.**" → 퀴즈 줄과 카드 줄을 없애고, 씬에서도 카드 포즈를 걷어냈다
#   (scene_defs S23). 대신 해가 지고 등이 켜지는 것을 **함께 올려다보는** 장면이 된다.
# ★교정(사장님 2026-08-18) — 노을도 좌판과 같은 어긋남이 있었다. 등이 켜지는
#   사건은 S24 의 7.9초(블록 +21.9초)인데 그때 **말이 없었다.** S23/S24 를 나눠
#   블록 머리가 곧 씬 머리가 되게 하면, 두 번째 줄이 점등 순간에 걸친다.
DUSK = [                                              # B12 — S23 (14초)
    L("해가 뉘엿뉘엿 넘어가요. 하루 종일 걸어 다닌 광장이 붉게 물듭니다.",
      "The sun is going down. The square we walked all day turns red.",
      "해 질 녘 광화문광장"),
    L("친구들이 하나둘 모여듭니다. 다 같이 하늘을 올려다볼까요?",
      "Friends gather one by one. Shall we all look up at the sky?"),
]

DUSK_LAMP = [                                         # B12b — S24 (16초) · 점등 +7.9초
    L("해가 지고, 광장의 등이 왼쪽부터 하나씩 차례로 켜집니다.",
      "The sun sets, and the lanterns come on one by one, starting from the left."),
    L("마지막 등이 켜지면, 다 함께 손을 번쩍 들어요.",
      "When the last lantern lights up, we all raise our hands together."),
    L("우리가 하루 종일 걸어 다닌 이곳, 바로 야외예요.",
      "This place we've walked all day — that's 야외, outdoors.",
      "야외 [ya-oe] outdoors"),
]

# ── B13 별 · 마무리 (32초) ────────────────────────────────────────
# ★v3 는 다음 시간 예고를 **두 줄에 걸쳐 두 번** 했다("ㅇ을 붙여 음절" / "자음을
#   만난다"). 한 줄로 합친다.
END = [
    L("거울을 꺼내 볼까요? 입 모양을 직접 보면서 따라 해 보세요.",
      "Take out a mirror. Watch your own mouth as you copy me.",
      "거울로 입 모양 보기"),
    L("아, 이, 오, 우. 입이 어떻게 바뀌는지 보이지요?",
      "아, 이, 오, 우. See how the shape changes each time?",
      "아 이 오 우", "아 이 오 우"),
    L("오늘 배운 낱말이에요. 아이, 이, 위, 오이, 유아, 우유, 이유.",
      "Today's words — 아이, 이, 위, 오이, 유아, 우유, 이유.",
      "오늘의 낱말 ①"),
    L("그리고 오, 우와, 야외, 야유, 아우, 여우, 아야, 여유. 모두 열다섯이에요.",
      "And 오, 우와, 야외, 야유, 아우, 여우, 아야, 여유 — fifteen in all.",
      "오늘의 낱말 ②"),
    L("모두 모음만으로 만든 말이에요. 자음은 하나도 쓰지 않았지요.",
      "Every one is built from vowels alone. Not a single consonant."),
    L("다음 시간에는 소리 없는 ㅇ을 모음 앞에 붙여 음절을 만들어 봅니다. 드디어 자음이에요.",
      "Next time we'll put the silent ㅇ in front of a vowel and build syllables — consonants at last.",
      "다음 시간 · 자음"),
    L("오늘도 잘 따라와 주셔서 고마워요. 다음 시간에 또 만나요!",
      "Thank you for following along. See you next time!"),
]

# ── 13블록 ─────────────────────────────────────────────────────────
# (번호, 제목, 씬 영상, 초, 줄들) — ★영상과 순서는 v3 그대로다.
BLOCKS = [
    (1,  "도착",           "W1_2/_scn/s1_plaza.mp4",            14.0, ARRIVE),
    (2,  "수문장 교대식",    "W1_2/motion6/guard_scene.mp4",      26.0, GUARD),
    (3,  "광화문 앞",       "W1_2/_scenes/w1d2_s3_4.mp4",        22.0, PLAZA),
    (4,  "계단",           "W1_2/_scenes/w1d2_s5_6_v4.mp4",     42.0, STEPS),
    (5,  "터널분수",        "W1_2/motion6/tunnel_scene_v9.mp4",   16.0, TUNNEL),
    # ★2026-08-18 — 좌판을 **오이 / 우유** 두 블록으로 쪼갰다(위 STALL_MILK 주석 참조).
    #   블록 머리가 곧 씬 머리라야 배경 사건과 말이 붙는다.
    (6,  "좌판·오이",       "W1_2/_scenes/w1d2_s8_9.mp4",           48.0, STALL),
    (61, "좌판·우유",       "W1_2/_scenes/w1d2_s10.mp4",            20.0, STALL_MILK),
    (7,  "원형 분수대",      "W1_2/_scenes/w1d2_s13.mp4",         19.0, FOUNTAIN),
    (8,  "한글분수 네온",    "W1_2/motion6/fountain_neon.mp4",    20.4, HANGEUL_F),
    (9,  "태권도",          "W1_2/motion6/tkd_show_v9.mp4",      21.0, TKD),
    (10, "벤치",           "W1_2/_scenes/w1d2_s15_16_v2.mp4",   36.0, BENCH),
    (11, "여우·은행나무길",   "W1_2/_fox/fox_road.mp4",            23.3, FOX),
    (12,  "노을",           "W1_2/_scenes/w1d2_s23.mp4",            14.0, DUSK),
    (121, "노을·등",        "W1_2/_scenes/w1d2_s24.mp4",            16.0, DUSK_LAMP),
    # ★교정(2026-08-18, 사장님 "마지막 달리기 하는 스틱맨 화면에서 완전히 사라지게")
    #   마무리 씬은 43초다. 32초로 잡으면 **달려 나가 사라지는 마지막 8.6초가 잘려**
    #   스틱맨이 화면 한복판에 선 채로 영상이 끝났다. 나레이션이 끝난 뒤 소리 없이
    #   달려 나가는 것이 맺음으로 알맞다.
    (13, "별 · 마무리",     "W1_2/_scenes/w1d2_s25_26_v6.mp4",      45.0, END),
]


def all_lines():
    for n, title, clip, sec, lines in BLOCKS:
        for i, l in enumerate(lines):
            yield n, title, i, l
