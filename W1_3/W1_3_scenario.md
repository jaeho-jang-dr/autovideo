# W1-3 시나리오 — ㅇ + 모음으로 음절 만들고 낱말 짓기 (청계천) [9블록 · 목표 약 7분 30초]

> **강의** W1-3 · 1주차 Day 3 = 문법·어휘구성 · 초급 (`web/src/data/lessons168.json` seq 3)
> **제목(KO)** ㅇ + 모음으로 음절 만들고 낱말 짓기 ／ **(EN)** Building Syllables & Words with ㅇ + Vowel
> **캐릭터** 졸라걸(`zolla_girl`, base_h 651, 163cm 환산) — 사장님 확정, 이번 회차부터 전환
> **배경 장소** 청계천(Cheonggyecheon Stream), 서울 — `korea_168_scenic_places_details.md` #26,
>   `lesson_places` bg_prefix `bg_w1d3`(구 레거시 표기) → 이 판은 `cheonggye_*` 키를 새로 쓴다
> **단계** ★오늘은 시나리오 + 동작 시나리오뿐이다. 렌더·클립 생성은 사장님 승인 후 다음 단계.
> 짝문서 `W1_3/W1_3_motion.md` — 씬 번호·배경키·초가 어긋나면 안 된다.

## 0. 이 판이 W1-2와 겹치지 않는 이유

W1-2(`W1_2/W1_2_scenario_v3.md`)는 **아이·오이·우유·이·오·아우·여우·야외** 여덟 낱말
자체를 "그림과 소리로" 가르쳤다. W1-3은 그 낱말들을 다시 가르치지 않는다.
대신 **그 낱말들이 왜 그렇게 생겼는지 규칙**과, 그 규칙으로 **한 번도 안 나온 새
낱말을 스스로 짓는 활동**만 다룬다.

| | W1-2 (어휘) | W1-3 (문법·어휘구성) |
|---|---|---|
| 묻는 것 | "이게 무슨 뜻이야?" | "왜 이렇게 생겼어? 나도 만들 수 있어?" |
| 다루는 낱말 | 아이·오이·우유·이·오·아우·여우·야외 (신규 8) | 위 낱말은 **복습용 재료**로만 재사용. 신규 낱말은 **이유·여유·우애** |
| 새로 넣는 것 | 낱말 자체 | **모아쓰기 배치 규칙**(수직=오른쪽·수평=아래) + **초성 ㅇ 자리표시자** 개념 |
| 다음 날 몫 (건드리지 않음) | — | W1-4(듣기·말하기: ㅗ/ㅜ·ㅐ/ㅔ·ㅏ/ㅓ 입모양 구별), W1-5(쓰기: 8모음 획순) |

★W1-3에서 하는 획순 연출은 **장식**(글자가 완성될 때 붓질이 스치는 정도)이지
"번호 매겨 따라 쓰기" 수업이 아니다 — 그건 W1-5 몫이다. 입모양 비교도 하지 않는다 —
그건 W1-4 몫이다.

## 1. 교육 근거 (NotebookLM「한글 교육: 자음과 모음의 과학적 원리 및 발음법」)

`research/nlm/W1D2_curriculum_extract.md` §(3) + 추가 질의 `research/nlm/w13_moaseugi.txt`
(2026-08-31, `nlm_ask.py` CDP 9222)에서 가져온 세 기둥:

1. **초성 필수 규칙(성자법)** — 모든 한글 음절은 자음으로 시작해야 하고 초성·중성이
   공간적으로 결합해야 한다. 모음으로 "시작하는 것처럼 들리는" 말도 실제로는 소릿값
   없는 **자리표시자 'ㅇ'**이 초성에 앉아 있다.
2. **★초성 ㅇ ≠ 종성 ㅇ** — 초성 ㅇ은 완전한 무음이지만, 받침(종성) 자리의 ㅇ은
   비음 [ŋ]으로 실제 소리가 난다(아 vs 강·방). W1-3은 이걸 **예고편으로만** 다룬다
   (받침은 아직 안 배웠다 — 새 자음 도입 금지).
3. **모아쓰기 배치** — 획이 **세로로 길쭉한 모음**(ㅏㅓㅣㅐㅔ)은 자음의 **오른쪽**,
   획이 **가로로 넓적한 모음**(ㅗㅜㅡ)은 자음의 **아래**에 붙는다.
   노트북이 제안한 아이 눈높이 비유를 그대로 쓴다 —
   **세로 모음 = "오른쪽에 나란히 서는 친구/지팡이"**, **가로 모음 = "위에 올라앉는
   침대/기차"**. 잘못 끼우면(가로 모음을 오른쪽에) 자석처럼 튕겨 나간다.

이 세 기둥이 이 판의 뼈대다. 시각 문법(레고 블록 색상·자석 스냅·엘코닌 박스)은
§5 "파라메트릭 렌더링"에 옮겨 적는다.

## 2. 새로 짓는 낱말 — 왜 이 셋인가

W1-2가 쓴 여덟 낱말은 국립국어원 자료가 정리한 "모음만으로 된 한국어 낱말" 전체
목록(`W1D2_curriculum_extract.md` §2)에서 **이유·여유**를 남겨 두었다. 이 둘을 오늘 쓴다.
★게다가 **새 글자를 하나도 안 그린다** — "유"는 W1-2 「우유」에서, "여"는 W1-2 「여우」에서
이미 본 블록이다. 그 블록이 **강 건너에서 헤엄쳐 와** 새 낱말에 재조립되는 것처럼 연출한다.
보너스 한 개(**우애**)는 8개 기본 단모음(ㅜ+ㅐ)만으로 짓는 "졸업 시험판" 낱말이고,
W1-2 「아우」(동생)와 뜻으로 이어진다.

| 신규 낱말 | 구성 | 뜻 | 재사용 블록 | 발음 |
|---|---|---|---|---|
| **이유** | 이 + 유 | 까닭·reason | "이"(아이) + "유"(우유) | [i-yu] |
| **여유** | 여 + 유 | 느긋함·leisure | "여"(여우) + "유"(우유) | [yeo-yu] |
| **우애**(보너스) | 우 + 애 | 형제 사랑·brotherly love | 순수 8모음만, 새 블록 없음 | [u-ae] |

받침이 하나도 없는 낱말들이라 **연음·경음화가 없다** — 발음기호가 철자 그대로 읽힌다.
(향후 받침 있는 낱말을 배울 때는 이렇게 쉽지 않다는 것도 짧게 언급한다.)

## 3. 8개 단모음 등장 대조표 (누락 금지 검사)

| 모음 | 어디서 등장하나 |
|---|---|
| ㅏ | 아이·아우(복습) · 우애[ae 아님, 두 번째 음절] → **아**(복습 낱말) |
| ㅓ | 블록 롤콜 + 감탄사 **"어?"**(물고기를 보고 놀람, 신규 연출) |
| ㅗ | 오·오이(복습) |
| ㅜ | 아우(복습) · **우애**(신규) |
| ㅡ | 블록 롤콜 + 감탄사 **"으차!"**(징검다리 물 닿아 차가움, 신규 연출) |
| ㅣ | 아이·오이(복습) · **이유**(신규) |
| ㅐ | **우애**(신규) — 이 낱말이 유일한 ㅐ 등장처 |
| ㅔ | 블록 롤콜(홀로 쓰는 실제 낱말이 없어 음절 조립 그 자체로 등장) |

8개 전부 블록 4(모아쓰기 규칙 시연)와 블록 5(롤콜)에서 최소 1회, 대부분 낱말
속에서 1회 더 등장한다. 렌더 전 `textrang`이 이 표로 자막 커버리지를 다시 검산한다.

## 4. 짜임 — 청계천에서 배우는 규칙

| 블록 | 내용 | 배경/씬 | 목표 초 | 누계 |
|---|---|---|---:|---:|
| 1 | **도입** 계단 위에서 인사, 지난 시간 복습 한 줄, 오늘 목표 예고 | `cheonggye_entrance` | 30 | 0:30 |
| 2 | **초성 필수 규칙** 계단을 내려가며 — 'ㅏ' 혼자 못 선다 → 'ㅇ'이 자리에 앉는다 | `cheonggye_entrance`→`cheonggye_stairs` | 40 | 1:10 |
| 3 | **모아쓰기 배치 규칙** 징검다리 = 음절상자. 세로 모음(오른쪽)·가로 모음(아래) 시연, 복습 낱말 5개로 확인 | `cheonggye_stones` | 100 | 2:50 |
| 4 | **오답 개그** 가로 모음을 오른쪽에 욱여넣다 튕겨 물에 빠짐 + 종성 ㅇ 예고편 | `cheonggye_underpass` | 40 | 3:30 |
| 5 | **모음 롤콜 마저 채우기** 어?(놀람) · 으차!(차가움) · 에(조립만) — 8개 블록 완성 | `cheonggye_willow` | 55 | 4:25 |
| 6 | **낱말 짓기 ①** "이"+"유" 블록이 강 건너에서 와 **이유** 완성 | `cheonggye_stones`(하류) | 45 | 5:10 |
| 7 | **낱말 짓기 ②** "여"+"유" 블록이 모여 **여유** 완성, 느긋한 몸짓으로 뜻을 보여 줌 | `cheonggye_willow`(그늘) | 45 | 5:55 |
| 8 | **보너스 낱말 + 총정리** "우"+"애" = **우애**, 벽화에 8블록·3낱말 총정리 | `cheonggye_mural` | 55 | 6:50 |
| 9 | **마무리** 다리 위 야경, 오늘 규칙 한 줄 요약, 인사하고 퇴장 | `cheonggye_bridge_dusk` | 40 | 7:30 |

합계 **목표 약 7분 30초**(W1-2 7:18과 비슷한 호흡). 실제 러닝타임은 KO/EN 나레이션
TTS 실측 후 `max(KO,EN)+0.35s` 규칙으로 블록별 재계산한다([[subtitle-sync-burn-drive]]) —
이 표의 초는 대본 집필용 목표치다.

## 5. 나레이션 — 블록별 (한국어 초안 / 영어 초안)

### 블록 1 — 도입 (계단 위)
- KO: "안녕! 지난 시간에 '아이', '오이', '아우' 같은 낱말을 배웠지요? 그런데 궁금하지
  않았어요? '아'라고 쓸 때 왜 앞에 동그라미 'ㅇ'을 쓸까요? 오늘은 그 이유를 밝히고,
  우리가 직접 새 낱말도 만들어 볼 거예요."
- EN: "Hi! Last time we learned words like 아이, 오이, 아우. But have you wondered —
  why do we write a little circle 'ㅇ' before the vowel? Today we find out, and we'll
  even build brand-new words ourselves."

### 블록 2 — 초성 필수 규칙 (계단)
- KO: "이 계단을 봐요. 계단은 반드시 첫 칸이 있어야 다음 칸으로 이어지죠? 한글 글자도
  똑같아요. **모든 음절은 자음으로 시작해야 해요.** 그런데 'ㅏ'처럼 모음 소리로 시작하는
  말은 자음이 없잖아요? 그럴 땐 소리가 없는 친구, **'ㅇ'**이 대신 그 자리에 앉아요.
  아무 소리도 안 내지만, 자리를 지켜 주는 거예요."
- EN: "Look at these stairs — you need the first step before the next one. Hangeul
  syllables work the same way: **every syllable must start with a consonant.** But a
  word like 'ㅏ' starts with a vowel sound — no consonant! So a silent friend, **'ㅇ'**,
  sits in that spot instead. It makes no sound, but it holds the place."

### 블록 3 — 모아쓰기 배치 규칙 (징검다리, 핵심)
- KO: "이 징검다리가 오늘의 '음절 상자'예요. 'ㅇ'이 왼쪽 돌에 서면, 모음이 올 자리가
  생겨요. 그런데 어디에 서야 할까요? **키가 껑충한 모음**—'ㅏ' 'ㅓ' 'ㅣ' 'ㅐ' 'ㅔ'—은
  'ㅇ'의 **오른쪽**에 나란히 서요. 마치 손잡고 걷는 친구처럼요. 반대로 **누워 있는
  모음**—'ㅗ' 'ㅜ' 'ㅡ'—는 'ㅇ' **아래**에 올라타요. 침대에 눕듯이요. 봐요 —
  '아이'는 '아'도 오른쪽, '이'도 오른쪽. '오이'는 '오'가 아래, '이'가 오른쪽.
  '아우'도 마찬가지예요. 자리가 딱 정해져 있어서, 아무 데나 놓으면 안 돼요."
- EN: "These stepping stones are today's 'syllable box'. When 'ㅇ' stands on the left
  stone, a spot opens up for a vowel — but where? **Tall vowels** — ㅏ ㅓ ㅣ ㅐ ㅔ —
  stand to the **right** of ㅇ, like a friend holding hands. **Flat, lying-down
  vowels** — ㅗ ㅜ ㅡ — sit **below** ㅇ, like lying on a bed. Look: in 아이, both
  'a' and 'i' go right. In 오이, 'o' goes below and 'i' goes right. 아우 follows the
  same rule. Every vowel has its one true spot."

### 블록 4 — 오답 개그 + 종성 ㅇ 예고편 (다리 밑)
- KO: "한번 일부러 틀려 볼까요? 누워 있는 모음 'ㅗ'를 오른쪽에 억지로 끼워 볼게요…
  안 돼요! 자리가 아니라서 팅! 튕겨 나가 첨벙, 물에 빠지고 말았어요. 자리를 지키는 게
  이렇게 중요해요. 참, 하나만 살짝 알려 줄게요 — 'ㅇ'이 글자 맨 아래, 받침 자리에 오면
  그때는 소리가 나요('강', '방'처럼요). 그건 다음에 천천히 배워요."
- EN: "Let's make a mistake on purpose. I'll force the lying-down vowel 'ㅗ' onto the
  right side... nope! Wrong spot — bounce, splash, into the water! Keeping the right
  spot really matters. One quick peek ahead: when 'ㅇ' sits at the very bottom of a
  block instead, it DOES make a sound — like in 강 or 방. We'll learn that slowly, another day."

### 블록 5 — 모음 롤콜 마저 채우기 (버드나무)
- KO: "이제 여덟 모음을 다 세워 볼까요. 아, 오, 우, 이는 낱말로 이미 만나 봤죠.
  나머지도 인사해요. 물속에서 뭔가 움직여요 — **'어?'** 하고 놀라는 소리, 이게 바로
  'ㅇ'과 'ㅓ'가 만든 소리예요. 징검다리 물이 차가워서 — **'으차!'** 이건 'ㅇ'과 'ㅡ'.
  그리고 'ㅔ'도 'ㅇ' 아래… 아니 오른쪽에 서면 '에'가 완성돼요. 자, 여덟 블록이 모두
  섰어요: 아 어 오 우 으 이 애 에."
- EN: "Let's line up all eight vowels. We've already met 아, 오, 우, 이 in real words.
  Let's greet the rest. Something moves in the water — **'eo?'** — that surprised
  sound is 'ㅇ' plus 'ㅓ'. The stepping stone water is cold — **'eu-cha!'** — that's
  'ㅇ' plus 'ㅡ'. And 'ㅔ' stands to the right of 'ㅇ' to make '에'. Now all eight
  blocks are standing: a eo o u eu i ae e."

### 블록 6 — 낱말 짓기 ① 이유 (징검다리 하류)
- KO: "이제 우리가 직접 새 낱말을 지어 볼 차례예요. 저 강 건너에서 '유' 블록이
  헤엄쳐 와요 — '우유'에서 만났던 그 블록이에요! 그리고 우리 '아이'의 '이' 블록과
  손을 잡으면… **이유**! '까닭'이라는 뜻의 새 낱말이 태어났어요."
- EN: "Now it's our turn to build a brand-new word. Look — the 'yu' block swims over
  from across the stream — the same one from 우유! It joins hands with the 'i' block
  from 아이, and together they make... **이유** — a new word meaning 'reason'!"

### 블록 7 — 낱말 짓기 ② 여유 (버드나무 그늘)
- KO: "'유' 블록이 이번엔 '여우'의 '여' 블록을 만났어요. 둘이 합치면 **여유**.
  '느긋함'이라는 뜻이에요. 그러고 보니 졸라걸도 지금 나무 그늘 아래서 딱 여유롭게
  쉬고 있네요."
- EN: "This time the 'yu' block meets the 'yeo' block from 여우. Together they make
  **여유** — meaning 'leisure, taking it easy'. And look — Zolla-girl herself is
  resting easy right here in the shade."

### 블록 8 — 보너스 낱말 우애 + 총정리 (벽화)
- KO: "마지막 선물 하나. 이번엔 재활용 블록 없이, 순수하게 기본 모음 둘로만 지어
  볼게요. '우' 더하기 '애' — **우애**. 형제자매 사이의 정을 뜻하는 말이에요. 지난
  시간 '아우'가 동생이었죠? 그 동생과 나누는 마음이 바로 우애예요. 벽에 오늘 배운 걸
  다 그려 볼게요 — 여덟 모음 블록과 세 낱말, 이유·여유·우애."
- EN: "One last gift — built purely from two basic vowels, no recycled blocks this
  time. 'U' plus 'ae' — **우애**, meaning the bond of love between brothers and
  sisters. Remember 아우, the little sibling, from last time? 우애 is exactly that
  feeling. Let's paint today's whole lesson on this wall — eight vowel blocks and
  three words: 이유, 여유, 우애."

### 블록 9 — 마무리 (다리 위 야경)
- KO: "오늘 배운 규칙, 한 줄로 정리해요. 모든 음절은 자음으로 시작하고, 소리 없는
  'ㅇ'이 그 자리를 지켜요. 그리고 세로 모음은 오른쪽, 가로 모음은 아래! 다음에는 이
  여덟 모음의 입 모양을 더 자세히 비교해 볼게요. 안녕!"
- EN: "Let's sum up today's rule in one line: every syllable starts with a consonant,
  and silent 'ㅇ' holds that spot when there's no sound. Tall vowels go right, flat
  vowels go below! Next time we'll compare the mouth shapes of these eight vowels
  more closely. Bye!"

## 6. 자막 — 5개 국어

블록마다 한국어 원문 → `tx_sub` 로 en·ja·zh-Hans·es-419. 모든 언어 자막에 한글을 남긴다
([[subtitle-keep-hangeul-in-all-langs]]). 발음기호는 철자가 아니라 실제 발음 —
단, §2에서 밝혔듯 이번 낱말들은 전부 받침이 없어 **연음·경음화 변형이 없다.**

```
아 [a] · 어 [eo] · 오 [o] · 우 [u] · 으 [eu] · 이 [i] · 애 [ae] · 에 [e]
아이 [a-i] · 오이 [o-i] · 아우 [a-u]  (복습)
이유 [i-yu] · 여유 [yeo-yu] · 우애 [u-ae]  (신규)
```

## 7. 파라메트릭 렌더링 — 화면에 뜨는 글자 (레고 블록/음절상자 시각 문법)

`research/nlm/w13_moaseugi.txt`(2026-08-31 질의)에서 가져온 시각 언어를 그대로 쓴다.
`textrang`이 `hangeul_write.py` 위에 이 규칙을 얹어 구현한다.

| 요소 | 규칙 |
|---|---|
| **엘코닌 박스(음절 상자)** | 점선 사각 슬롯. 자음이 서면 결합할 모음 방향(오른쪽/아래)에 맞춰 **빈 칸이 반짝이는 힌트**를 준다 |
| **색상 코드** | 양성 모음(ㅗㅏ) = 따뜻한 주황·빨강 / 음성 모음(ㅜㅓ) = 차가운 파랑·보라 / 중성 모음 ㅣ = 반투명 화이트 |
| **정답 스냅** | 자석처럼 "착!" 붙으며 노란색(#FFD700) 오버레이 라이팅 + 실로폰 소리 + 초록 원(O) |
| **오답 튕김** | 빨간 경고 진동 + 가새(X) + "띠익" 효과음 + 화면 밖으로 튕겨 나감(블록4) |
| **글자 자리** | W1-2와 동일 — 상반부 중앙, 최대 세 줄, 캐릭터는 구역 제한 없음([[bg-never-empty-left-side]] 원칙과 함께 `W1_2/W1_2_motion.md` §0-D 규칙을 그대로 물려받는다) |
| **획순 장식** | 낱말 완성 시 붓질 한 번 스치는 정도(★수업 아님, W1-5 몫) |

## 8. 렌더 전 반드시 볼 것 (오늘은 해당 없음 — 다음 단계 메모)

1. 이 문서는 **시나리오만**이다. 배경 동영상·정지 이미지, 캐릭터 동작 클립은
   전부 다음 단계(사장님 승인 후)에 만든다.
2. 배경·동작이 만들어지면 `W1_3/W1_3_motion.md`의 목표 초를 **실측치로 갱신**하고,
   이 표(§4)의 "목표 초"를 "실측 초"로 바꿔 재계산한다(`W1_2/measure_bg_events.py` 방식).
3. 8개 단모음 커버리지(§3)와 낱말 발음기호(§6)는 자막 작업 전에 `textrang`이 다시
   검산한다.
4. 캐릭터는 **졸라걸**로 확정 — 8방향 이동 컷 세트가 없으면 `W1_3/W1_3_motion.md` §2를
   보고 `characterang`/`cutrang`에 먼저 제작을 의뢰한다.
