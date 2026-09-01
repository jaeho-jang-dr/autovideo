# W1-3 시나리오 v2 — ㅇ + 모음으로 음절 만들고 낱말 짓기 (청계천) [23씬 · 목표 약 7분 30초]

> **강의** W1-3 · 1주차 Day 3 = 문법·어휘구성 · 초급 (`web/src/data/lessons168.json` seq 3)
> **제목(KO)** ㅇ + 모음으로 음절 만들고 낱말 짓기 ／ **(EN)** Building Syllables & Words with ㅇ + Vowel
> **캐릭터** 졸라걸(`zolla_girl` / DB 동작컷 `w12_zgirl`) — base_h 651, 163cm 환산
> **배경 장소** 청계천(Cheonggyecheon Stream), 서울 — `korea_168_scenic_places_details.md` #26
> v1(9블록, `W1_3/W1_3_scenario.md`)을 **대체**한다. 씬 번호·배경키·초가 어긋나면 안 되는
> 짝문서는 `W1_3/W1_3_motion_v2.md`.
> ★오늘도 시나리오 + 동작 시나리오뿐이다. 렌더·클립 생성은 사장님 승인 후 다음 단계.

## 0. 왜 다시 설계했는가 (사장님 지적 2026-09-01)

> "7분을 배경 7개로 어찌어찌 해결하려는 것이 잘못된 것이다.
>  시나리오·배경 다시 만들고 2씬당 한 배경으로 간다."

v1은 배경 하나(`cheonggye_stones`, 8초 원본)에 블록3 하나를 통째로 100초까지 밀어
넣었다. 8초 → 100초는 **12.5배 저속 재생**이라 카메라 움직임이 거의 멈춘 것처럼
퍼져 버리고, "보다가 지루해서 금방 돌리겠다"(사장님 확인)는 문제가 났다.

해법은 단순하다 — **W1-2 방식대로 씬을 잘게 쪼개서 배경마다 슬로우다운 배율을
낮춘다.** W1-2(`W1_2/W1_2_scenario.md`, v2 원안)는 26개 세부 씬을 7개 배경 그룹에
나눠 배정했고(예: `gwanghwamun_stall`이 S8~S12, 5씬·96초를 나눠 썼다), 씬 하나
평균 15~20초였다. 그 밀도를 그대로 옮긴다.

| | v1(9블록) | v2(23씬, 이 문서) |
|---|---:|---:|
| 씬(블록) 개수 | 9 | **23** |
| 씬 하나 평균 길이 | 50초 | **19.6초** |
| 가장 긴 단일 블록 | 100초(블록3) | 24초(S05) |
| 배경 개수 | 7 | **10**(기존 7 + 신규 3) |
| 배경 하나당 최대 슬로우다운 배율(8초 원본 기준) | **12.5배**(블록3) | **최대 6.9배**(willow·mural), 대부분 3.75~5.6배 |

교육 내용(초성 필수규칙 → 모아쓰기 배치규칙 → 오답개그 → 모음 롤콜 → 낱말짓기
이유·여유 → 보너스 우애 → 총정리)은 **그대로**다. 블록을 2~4개의 짧은 씬으로
세분화했을 뿐, 하나도 빼거나 줄이지 않았다.

### 구 블록 ↔ 신 씬 대응표

| 구 블록(v1) | 내용 | 신 씬(v2) |
|---|---|---|
| 1 도입 | 인사·복습·예고 | S01–S02 |
| 2 초성 필수 규칙 | 계단, 'ㅇ' 자리표시자 | S03–S04 |
| 3 모아쓰기 배치 규칙 | 징검다리, 세로/가로 모음 자리 | S05–S09 |
| 4 오답 개그 | 튕겨서 물에 빠짐 + 종성 예고 | S10–S11 |
| 5 모음 롤콜 마저 채우기 | 어?·으차!·에 | S12–S14 |
| 6 낱말짓기① 이유 | "유"+"이" | S15–S16 |
| 7 낱말짓기② 여유 | "유"+"여" | S17–S18 |
| 8 보너스 우애 + 총정리 | "우"+"애", 벽화 총정리 | S19–S21 |
| 9 마무리 | 규칙 요약, 퇴장 | S22–S23 |

## 1. 교육 근거 (그대로 계승)

`research/nlm/W1D2_curriculum_extract.md` §(3) + `research/nlm/w13_moaseugi.txt`
(2026-08-31, `nlm_ask.py` CDP 9222)에서 가져온 세 기둥 — v1에서 바뀌지 않았다.

1. **초성 필수 규칙(성자법)** — 모든 한글 음절은 자음으로 시작해야 하고 초성·중성이
   공간적으로 결합해야 한다. 모음으로 "시작하는 것처럼 들리는" 말도 실제로는 소릿값
   없는 **자리표시자 'ㅇ'**이 초성에 앉아 있다.
2. **★초성 ㅇ ≠ 종성 ㅇ** — 초성 ㅇ은 완전한 무음이지만, 받침(종성) 자리의 ㅇ은
   비음 [ŋ]으로 실제 소리가 난다(아 vs 강·방). W1-3은 이걸 **예고편으로만** 다룬다
   (받침은 아직 안 배웠다 — 새 자음 도입 금지).
3. **모아쓰기 배치** — 획이 **세로로 길쭉한 모음**(ㅏㅓㅣㅐㅔ)은 자음의 **오른쪽**,
   획이 **가로로 넓적한 모음**(ㅗㅜㅡ)은 자음의 **아래**에 붙는다.
   **세로 모음 = "오른쪽에 나란히 서는 친구/지팡이"**, **가로 모음 = "위에 올라앉는
   침대/기차"**. 잘못 끼우면(가로 모음을 오른쪽에) 자석처럼 튕겨 나간다.

## 2. 새로 짓는 낱말 — 왜 이 셋인가 (그대로 계승)

| 신규 낱말 | 구성 | 뜻 | 재사용 블록 | 발음 |
|---|---|---|---|---|
| **이유** | 이 + 유 | 까닭·reason | "이"(아이) + "유"(우유) | [i-yu] |
| **여유** | 여 + 유 | 느긋함·leisure | "여"(여우) + "유"(우유) | [yeo-yu] |
| **우애**(보너스) | 우 + 애 | 형제 사랑·brotherly love | 순수 8모음만, 새 블록 없음 | [u-ae] |

받침이 하나도 없는 낱말들이라 **연음·경음화가 없다** — 발음기호가 철자 그대로 읽힌다.

## 3. 8개 단모음 등장 대조표 (누락 금지 검사 — 씬 번호 갱신)

| 모음 | 어디서 등장하나 (씬) |
|---|---|
| ㅏ | 아이(S06)·아우(S08, 복습) |
| ㅓ | 롤콜(S12) + 감탄사 **"어?"**(S13, 신규 연출) |
| ㅗ | 오이(S07)·오 단독(S09, 복습) |
| ㅜ | 아우(S08, 복습) · **우애**(S19, 신규) |
| ㅡ | 롤콜(S12) + 감탄사 **"으차!"**(S13, 신규 연출) |
| ㅣ | 아이(S06)·오이(S07)·오 단독(S09, 복습) · **이유**(S15–S16, 신규) |
| ㅐ | **우애**(S19) — 이 낱말이 유일한 ㅐ 등장처 |
| ㅔ | 롤콜(S14, 조립만 — 실제 낱말 없음) |

8개 전부 S05~S09(모아쓰기 규칙 시연)와 S12~S14(롤콜)에서 최소 1회씩 등장한다.
렌더 전 `textrang`이 이 표로 자막 커버리지를 다시 검산한다.

## 4. 짜임 — 23씬 표

★배경란의 "(신규)"는 아직 만들지 않은 배경이다(§8 참조). 슬로우다운 배율은
그 배경이 이어서 쓰이는 씬 구간 전체 길이 ÷ 8초 원본으로 계산한다(한 배경이
여러 씬에 걸쳐 있으면 **하나의 연속된 저속 재생**으로 흐르고, 씬 경계에서 처음
프레임으로 되돌아가지 않는다 — §9 원칙).

| 씬 | 구 블록 | 내용 | 배경 | 초 | 누계 | 배경 구간 합/슬로우다운 |
|---|---|---|---|---:|---:|---|
| S01 | 1 | 인사 + 지난 시간 복습("아이·오이·아우") | `cheonggye_entrance` | 15 | 0:15 | 30초/3.75배 |
| S02 | 1 | 오늘 목표 예고("ㅇ은 왜?" + 새 낱말 예고) | `cheonggye_entrance` | 15 | 0:30 | ″ |
| S03 | 2 | 계단 비유 도입 — "첫 칸 있어야 다음 칸" → 모든 음절은 자음으로 시작 | `cheonggye_stairs` | 20 | 0:50 | 40초/5.0배 |
| S04 | 2 | 'ㅏ' 혼자 못 선다 → 'ㅇ'이 자리 채움 | `cheonggye_stairs` | 20 | 1:10 | ″ |
| S05 | 3 | **핵심** 징검다리=음절상자, 세로모음(오른쪽)·가로모음(아래) 규칙 도입 | `cheonggye_stones` | 24 | 1:34 | 44초/5.5배 |
| S06 | 3 | "아이" 데모 — 아·이 둘 다 오른쪽 | `cheonggye_stones` | 20 | 1:54 | ″ |
| S07 | 3 | "오이" 데모 — 오=아래, 이=오른쪽 | `cheonggye_stones_midstream`(신규) | 18 | 2:12 | 56초/7.0배 |
| S08 | 3 | "아우" 데모 — 아=오른쪽, 우=아래 | `cheonggye_stones_midstream`(신규) | 18 | 2:30 | ″ |
| S09 | 3 | "오"·"이" 단독 음절도 된다 + 정리 | `cheonggye_stones_midstream`(신규) | 20 | 2:50 | ″ |
| S10 | 4 | 오답 개그 — 가로모음 'ㅗ'를 오른쪽에 욱여넣다 튕겨 물에 빠짐 | `cheonggye_underpass` | 20 | 3:10 | 40초/5.0배 |
| S11 | 4 | 일어나 머리 긁적 + 종성 ㅇ 예고편("강·방…?") | `cheonggye_underpass` | 20 | 3:30 | ″ |
| S12 | 5 | 기본 4모음(아·오·우·이) 롤콜 복습 | `cheonggye_willow` | 18 | 3:48 | 55초/6.9배 |
| S13 | 5 | "어?"(물고기 놀람) + "으차!"(물 차가움) 신규 감탄사 2개 | `cheonggye_willow` | 20 | 4:08 | ″ |
| S14 | 5 | 'ㅔ' 조립 + 8모음 블록 전체 정렬·완성 | `cheonggye_willow` | 17 | 4:25 | ″ |
| S15 | 6 | 강 건너에서 "유" 블록이 헤엄쳐 옴 | `cheonggye_stones_downstream`(신규) | 22 | 4:47 | 45초/5.6배 |
| S16 | 6 | "이"와 결합 → **이유** 완성, 카드(뜻: 까닭) | `cheonggye_stones_downstream`(신규) | 23 | 5:10 | ″ |
| S17 | 7 | "유"+"여" 블록 결합 → **여유** 완성 | `cheonggye_willow_bench`(신규) | 22 | 5:32 | 45초/5.6배 |
| S18 | 7 | 그늘 벤치에 앉아 여유(느긋함)를 몸으로 보여줌 | `cheonggye_willow_bench`(신규) | 23 | 5:55 | ″ |
| S19 | 8 | "우"+"애" 두 블록을 부딪쳐 **우애** 완성(재활용 없는 순수 신규 낱말) | `cheonggye_mural` | 20 | 6:15 | 55초/6.9배 |
| S20 | 8 | 우애의 뜻 설명 + 지난 시간 "아우"와 연결 | `cheonggye_mural` | 15 | 6:30 | ″ |
| S21 | 8 | 벽화 총정리 — 8모음 블록 + 3낱말(이유·여유·우애) | `cheonggye_mural` | 20 | 6:50 | ″ |
| S22 | 9 | 오늘 규칙 한 줄 요약(자음 시작 + ㅇ 자리, 세로=오른쪽·가로=아래) | `cheonggye_bridge_dusk` | 20 | 7:10 | 40초/5.0배 |
| S23 | 9 | 인사 + 퇴장(달려서 멀어짐), 등불 점등 | `cheonggye_bridge_dusk` | 20 | 7:30 | ″ |

**합계 23씬 · 목표 7분 30초(450초)** · 씬 하나 평균 19.6초(최소 15초·최대 24초,
전부 15~25초 구간 안에 든다). 실제 러닝타임은 KO/EN 나레이션 TTS 실측 후
`max(KO,EN)+0.35s` 규칙으로 씬별 재계산한다([[subtitle-sync-burn-drive]]) — 이
표의 초는 대본 집필용 목표치다.

## 5. 나레이션 — 씬별 (한국어 초안 / 영어 초안)

### S01 — 인사 + 복습 (`cheonggye_entrance`)
- KO: "안녕! 지난 시간에 '아이', '오이', '아우' 같은 낱말을 배웠지요?"
- EN: "Hi! Last time we learned words like 아이, 오이, 아우."

### S02 — 오늘 목표 예고 (`cheonggye_entrance`)
- KO: "그런데 궁금하지 않았어요? '아'라고 쓸 때 왜 앞에 동그라미 'ㅇ'을 쓸까요?
  오늘은 그 이유를 밝히고, 우리가 직접 새 낱말도 만들어 볼 거예요."
- EN: "But have you wondered — why do we write a little circle 'ㅇ' before the vowel?
  Today we find out, and we'll even build brand-new words ourselves."

### S03 — 계단 비유 도입 (`cheonggye_stairs`)
- KO: "이 계단을 봐요. 계단은 반드시 첫 칸이 있어야 다음 칸으로 이어지죠? 한글
  글자도 똑같아요. **모든 음절은 자음으로 시작해야 해요.**"
- EN: "Look at these stairs — you need the first step before the next one. Hangeul
  syllables work the same way: **every syllable must start with a consonant.**"

### S04 — 'ㅇ'이 자리 채움 (`cheonggye_stairs`)
- KO: "그런데 'ㅏ'처럼 모음 소리로 시작하는 말은 자음이 없잖아요? 그럴 땐 소리가
  없는 친구, **'ㅇ'**이 대신 그 자리에 앉아요. 아무 소리도 안 내지만, 자리를
  지켜 주는 거예요."
- EN: "But a word like 'ㅏ' starts with a vowel sound — no consonant! So a silent
  friend, **'ㅇ'**, sits in that spot instead. It makes no sound, but it holds the
  place."

### S05 — 음절상자 규칙 도입 (`cheonggye_stones`, 핵심)
- KO: "이 징검다리가 오늘의 '음절 상자'예요. 'ㅇ'이 왼쪽 돌에 서면, 모음이 올
  자리가 생겨요. 그런데 어디에 서야 할까요? **키가 껑충한 모음**—'ㅏ' 'ㅓ' 'ㅣ'
  'ㅐ' 'ㅔ'—은 'ㅇ'의 **오른쪽**에 나란히 서요. 마치 손잡고 걷는 친구처럼요.
  반대로 **누워 있는 모음**—'ㅗ' 'ㅜ' 'ㅡ'—는 'ㅇ' **아래**에 올라타요.
  침대에 눕듯이요."
- EN: "These stepping stones are today's 'syllable box'. When 'ㅇ' stands on the
  left stone, a spot opens up for a vowel — but where? **Tall vowels** — ㅏ ㅓ ㅣ
  ㅐ ㅔ — stand to the **right** of ㅇ, like a friend holding hands. **Flat,
  lying-down vowels** — ㅗ ㅜ ㅡ — sit **below** ㅇ, like lying on a bed."

### S06 — "아이" 데모 (`cheonggye_stones`)
- KO: "봐요 — '아이'는 '아'도 오른쪽, '이'도 오른쪽. 둘 다 키가 껑충한 모음이라
  나란히 손을 잡아요."
- EN: "Look: in 아이, both 'a' and 'i' go right — both are tall vowels, so they
  stand hand in hand."

### S07 — "오이" 데모 (`cheonggye_stones_midstream`)
- KO: "이번엔 '오이'. '오'는 누워 있는 모음이라 아래에 올라타고, '이'는 오른쪽에
  서요. 자리가 서로 달라요."
- EN: "Now 오이 — 'o' is a lying-down vowel, so it sits below, while 'i' still
  stands to the right. Different vowels, different spots."

### S08 — "아우" 데모 (`cheonggye_stones_midstream`)
- KO: "'아우'도 마찬가지예요. '아'는 오른쪽, '우'는 아래. 자리가 딱 정해져 있어서,
  아무 데나 놓으면 안 돼요."
- EN: "아우 follows the same rule — 'a' goes right, 'u' goes below. Every vowel has
  its one true spot; you can't put it just anywhere."

### S09 — 단독 음절 + 정리 (`cheonggye_stones_midstream`)
- KO: "그런데 꼭 두 개를 겹쳐야 하는 건 아니에요. '오'나 '이'처럼, 모음 딱
  하나로도 이미 완전한 음절이 돼요. 자리를 지키는 'ㅇ' 하나면 충분하죠."
- EN: "But you don't always need two vowels stacked together. A single vowel, like
  'o' or 'i' alone, is already a complete syllable — one place-holding 'ㅇ' is
  enough."

### S10 — 오답 개그 (`cheonggye_underpass`)
- KO: "한번 일부러 틀려 볼까요? 누워 있는 모음 'ㅗ'를 오른쪽에 억지로 끼워
  볼게요… 안 돼요! 자리가 아니라서 팅! 튕겨 나가 첨벙, 물에 빠지고 말았어요."
- EN: "Let's make a mistake on purpose. I'll force the lying-down vowel 'ㅗ' onto
  the right side... nope! Wrong spot — bounce, splash, into the water!"

### S11 — 종성 ㅇ 예고편 (`cheonggye_underpass`)
- KO: "자리를 지키는 게 이렇게 중요해요. 참, 하나만 살짝 알려 줄게요 — 'ㅇ'이
  글자 맨 아래, 받침 자리에 오면 그때는 소리가 나요('강', '방'처럼요). 그건
  다음에 천천히 배워요."
- EN: "Keeping the right spot really matters. One quick peek ahead: when 'ㅇ' sits
  at the very bottom of a block instead, it DOES make a sound — like in 강 or 방.
  We'll learn that slowly, another day."

### S12 — 기본 4모음 롤콜 (`cheonggye_willow`)
- KO: "이제 여덟 모음을 다 세워 볼까요. 아, 오, 우, 이는 낱말로 이미 만나
  봤죠. 나머지도 인사해요."
- EN: "Let's line up all eight vowels. We've already met 아, 오, 우, 이 in real
  words. Let's greet the rest."

### S13 — "어?" · "으차!" (`cheonggye_willow`)
- KO: "물속에서 뭔가 움직여요 — **'어?'** 하고 놀라는 소리, 이게 바로 'ㅇ'과
  'ㅓ'가 만든 소리예요. 징검다리 물이 차가워서 — **'으차!'** 이건 'ㅇ'과 'ㅡ'."
- EN: "Something moves in the water — **'eo?'** — that surprised sound is 'ㅇ'
  plus 'ㅓ'. The stepping stone water is cold — **'eu-cha!'** — that's 'ㅇ' plus
  'ㅡ'."

### S14 — 'ㅔ' 조립 + 8블록 완성 (`cheonggye_willow`)
- KO: "그리고 'ㅔ'도 'ㅇ' 오른쪽에 서면 '에'가 완성돼요. 자, 여덟 블록이 모두
  섰어요: 아 어 오 우 으 이 애 에."
- EN: "And 'ㅔ' stands to the right of 'ㅇ' to make '에'. Now all eight blocks are
  standing: a eo o u eu i ae e."

### S15 — "유" 블록이 헤엄쳐 옴 (`cheonggye_stones_downstream`)
- KO: "이제 우리가 직접 새 낱말을 지어 볼 차례예요. 저 강 건너에서 '유' 블록이
  헤엄쳐 와요 — '우유'에서 만났던 그 블록이에요!"
- EN: "Now it's our turn to build a brand-new word. Look — the 'yu' block swims
  over from across the stream — the same one from 우유!"

### S16 — "이유" 완성 (`cheonggye_stones_downstream`)
- KO: "그리고 우리 '아이'의 '이' 블록과 손을 잡으면… **이유**! '까닭'이라는
  뜻의 새 낱말이 태어났어요."
- EN: "It joins hands with the 'i' block from 아이, and together they make...
  **이유** — a new word meaning 'reason'!"

### S17 — "여유" 완성 (`cheonggye_willow_bench`)
- KO: "'유' 블록이 이번엔 '여우'의 '여' 블록을 만났어요. 둘이 합치면 **여유**.
  '느긋함'이라는 뜻이에요."
- EN: "This time the 'yu' block meets the 'yeo' block from 여우. Together they
  make **여유** — meaning 'leisure, taking it easy'."

### S18 — 그늘 벤치, 여유 시연 (`cheonggye_willow_bench`)
- KO: "그러고 보니 저도 지금 나무 그늘 아래서 딱 여유롭게 쉬고 있네요."
- EN: "And look — I'm resting easy myself, right here in the shade."

### S19 — "우애" 완성 (`cheonggye_mural`)
- KO: "마지막 선물 하나. 이번엔 재활용 블록 없이, 순수하게 기본 모음 둘로만 지어
  볼게요. '우' 더하기 '애' — **우애**."
- EN: "One last gift — built purely from two basic vowels, no recycled blocks this
  time. 'U' plus 'ae' — **우애**."

### S20 — 우애의 뜻 (`cheonggye_mural`)
- KO: "형제자매 사이의 정을 뜻하는 말이에요. 지난 시간 '아우'가 동생이었죠?
  그 동생과 나누는 마음이 바로 우애예요."
- EN: "It means the bond of love between brothers and sisters. Remember 아우, the
  little sibling, from last time? 우애 is exactly that feeling."

### S21 — 벽화 총정리 (`cheonggye_mural`)
- KO: "벽에 오늘 배운 걸 다 그려 볼게요 — 여덟 모음 블록과 세 낱말, 이유·여유·
  우애."
- EN: "Let's paint today's whole lesson on this wall — eight vowel blocks and
  three words: 이유, 여유, 우애."

### S22 — 규칙 한 줄 요약 (`cheonggye_bridge_dusk`)
- KO: "오늘 배운 규칙, 한 줄로 정리해요. 모든 음절은 자음으로 시작하고, 소리
  없는 'ㅇ'이 그 자리를 지켜요. 그리고 세로 모음은 오른쪽, 가로 모음은 아래!"
- EN: "Let's sum up today's rule in one line: every syllable starts with a
  consonant, and silent 'ㅇ' holds that spot when there's no sound. Tall vowels go
  right, flat vowels go below!"

### S23 — 인사 + 퇴장 (`cheonggye_bridge_dusk`)
- KO: "다음에는 이 여덟 모음의 입 모양을 더 자세히 비교해 볼게요. 안녕!"
- EN: "Next time we'll compare the mouth shapes of these eight vowels more
  closely. Bye!"

## 6. 자막 — 5개 국어 (그대로 계승)

씬마다 한국어 원문 → `tx_sub`로 en·ja·zh-Hans·es-419. 모든 언어 자막에 한글을
남긴다([[subtitle-keep-hangeul-in-all-langs]]). 발음기호는 철자가 아니라 실제
발음 — 이번 낱말들은 전부 받침이 없어 **연음·경음화 변형이 없다.**

```
아 [a] · 어 [eo] · 오 [o] · 우 [u] · 으 [eu] · 이 [i] · 애 [ae] · 에 [e]
아이 [a-i] · 오이 [o-i] · 아우 [a-u]  (복습)
이유 [i-yu] · 여유 [yeo-yu] · 우애 [u-ae]  (신규)
```

## 7. 파라메트릭 렌더링 — 화면에 뜨는 글자 (그대로 계승)

`research/nlm/w13_moaseugi.txt`(2026-08-31 질의)에서 가져온 시각 언어를 그대로
쓴다. `textrang`이 `hangeul_write.py` 위에 이 규칙을 얹어 구현한다.

| 요소 | 규칙 |
|---|---|
| **엘코닌 박스(음절 상자)** | 점선 사각 슬롯. 자음이 서면 결합할 모음 방향(오른쪽/아래)에 맞춰 **빈 칸이 반짝이는 힌트**를 준다 |
| **색상 코드** | 양성 모음(ㅗㅏ) = 따뜻한 주황·빨강 / 음성 모음(ㅜㅓ) = 차가운 파랑·보라 / 중성 모음 ㅣ = 반투명 화이트 |
| **정답 스냅** | 자석처럼 "착!" 붙으며 노란색(#FFD700) 오버레이 라이팅 + 실로폰 소리 + 초록 원(O) |
| **오답 튕김** | 빨간 경고 진동 + 가새(X) + "띠익" 효과음 + 화면 밖으로 튕겨 나감(S10) |
| **글자 자리** | 상반부 중앙, 최대 세 줄, 캐릭터는 구역 제한 없음([[bg-never-empty-left-side]]) |
| **획순 장식** | 낱말 완성 시 붓질 한 번 스치는 정도(★수업 아님, W1-5 몫) |

## 8. 배경 총 개수 재산정

| 구분 | 개수 | 키 |
|---|---:|---|
| 기존 7개 **전부 재사용** | 7 | `cheonggye_entrance` `cheonggye_stairs` `cheonggye_stones` `cheonggye_underpass` `cheonggye_willow` `cheonggye_mural` `cheonggye_bridge_dusk` |
| 신규 필요 | 3 | `cheonggye_stones_midstream`(S07–S09) · `cheonggye_stones_downstream`(S15–S16) · `cheonggye_willow_bench`(S17–S18) |
| **합계** | **10** | 23씬 ÷ 10배경 ≈ **씬 2.3개당 배경 1개** |

신규 3개의 이유:
- `cheonggye_stones_midstream` / `_downstream` — 기존 `cheonggye_stones` 하나로
  S05~S09·S15~S16 **7개 씬(129초)**을 전부 감당하면 슬로우다운이 다시 16배를
  넘어 v1과 같은 문제가 재발한다. 같은 징검다리를 **다른 구간·각도**로 두 벌 더
  찍어 나눠 맡긴다(v1 메모에 이미 있던 "블록3·6이 같은 stones를 다른 구간으로
  써야 할 수도 있다"를 실제 배경 분리로 확정).
- `cheonggye_willow_bench` — 기존 `cheonggye_willow`(물가, S12–S14)와 그늘
  벤치(S17–S18)는 원래 카메라 무빙 성격이 다르다(물가=미풍에 흔들, 벤치=거의
  정지). 하나로 억지로 묶지 않고 별도 배경으로 분리한다.

## 9. 배경 재생 원칙 (재확인)

`MOTION25D_SPEC.md` §6 그대로: **되감기(ping-pong) 금지.** 한 배경이 여러 씬에
걸쳐 있을 때는 8초 원본을 **하나의 연속된 저속 재생**으로 이어 흘리고(씬 경계에서
프레임 0으로 되돌아가지 않는다), 재생이 원본 8초를 다 쓰면 마지막 프레임을
유지한다. §4 표의 "배경 구간 합/슬로우다운"이 이 연속 구간의 실제 배율이다.

## 10. 렌더 전 반드시 볼 것 (오늘은 해당 없음 — 다음 단계 메모)

1. 이 문서는 **시나리오만**이다. 신규 배경 3종·자막·최종 클립 합성은 전부 다음
   단계(사장님 승인 후)에 만든다.
2. 신규 배경이 만들어지면 `W1_3/W1_3_motion_v2.md`의 목표 초를 **실측치로 갱신**
   하고, §4의 "목표 초"를 "실측 초"로 바꿔 재계산한다.
3. 8개 단모음 커버리지(§3)와 낱말 발음기호(§6)는 자막 작업 전에 `textrang`이
   다시 검산한다.
4. 캐릭터 동작은 `W1_3/W1_3_motion_v2.md`를 따른다 — 새 동작 클립 7종은 이미
   생성 완료(§1 참조), 부족분은 같은 문서 §7에 정리했다.
