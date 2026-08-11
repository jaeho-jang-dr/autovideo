# W1-2 시나리오 — 모음으로 만드는 첫 단어 (광화문광장) [22씬 · 약 7분]

> **강의** W1-2 · 1주차 **Day 2 = 어휘 확장** · 초급
> **제목(KO)** 모음으로 만드는 첫 단어 ／ **(EN)** First Words from Vowels
> **배경** 광화문광장 (`korea_lesson_places.json` week1/day2)
> **캐릭터** 스틱맨 단독
> **단어 7개** 아이 · 이 · 오이 · 우유 · 오 · 아우 · **여우**

## 근거 자료 (셋을 겹쳐서 만들었다)

| 출처 | 가져온 것 |
|---|---|
| 웹 `hangeul_w1d2_notes_ko.md` · `slides.pdf`(9쪽) | 9섹션 뼈대 · 6단어 · 나레이션 어투 |
| NotebookLM「한글 교육」 Day2 설계 | **활동 2가지**(삽화 매칭 · 음절 끊어 읽기) · **여우** 추가 |
| 노트북 메모 9개 | 레고 블록 · 컬러 코딩(양성 난색/음성 한색) · 음절 상자 |

## ★경계 — 옆날을 침범하지 않는다

| | 그날 몫 |
|---|---|
| **Day 2 (오늘)** | **어휘.** 그림↔글자 잇기, 음절 끊어 읽기 |
| Day 3 | ㅇ+모음 결합 규칙 · 좌우/상하 결합 → **오늘은 한 줄만 짚고 넘어간다** |
| Day 4 | ㅓ/ㅗ, ㅡ/ㅜ 발음 대조 → **오늘은 깊이 들어가지 않는다** |
| Day 5 | 3초 발성 드릴 · Day 6 획순 쓰기 · Day 7 평가 |

---

## 0. 원칙

1. **자음을 가르치지 않는다.** 소리는 전부 모음이다
2. **그림과 소리로 익힌다** — 단어마다 **삽화 카드**를 글자 옆에 붙인다(1:1 매칭)
3. **음절을 끊어 읽는다** — 블록 두 개가 스냅으로 붙는 모션과 함께
4. **컬러 코딩** — 양성(ㅏㅗ)=난색, 음성(ㅓㅜ)=한색, 중성(ㅣ)=무채색·반투명
5. 한 씬 = 나레이션 한 덩어리. 동작은 나레이션과 1:1
6. 글자는 인물 반대편. 자막은 5개국어 소프트(번인 금지)

## 0-B. 화면 구성

```
┌──────────────────────────────────────┐
│ ┌────────────┐                       │
│ │ 씬 핵심     │      광화문광장         │
│ │ 텍스트박스   │                       │
│ └────────────┘         스틱맨          │
│      [삽화카드] + 파라메트릭 한글        │
│         (자막 = 소프트 srt 5개국어)      │
└──────────────────────────────────────┘
```

## 0-C. 배경 (2~3씬당 1개 · 왼편 비움)

| 배경키 | 장면 | 씬 |
|---|---|---|
| `gwanghwamun_wide` | 광장 전경, 세종대왕 동상이 오른편 멀리 | S1–S3 |
| `gwanghwamun_statue` | 동상 아래 계단 | S4–S6 |
| `gwanghwamun_stall` | 광장 한켠 좌판 — 오이·우유가 놓임 | S7–S11 |
| `gwanghwamun_bench` | 벤치와 화단 | S12–S16 |
| `gwanghwamun_path` | 은행나무 산책로 | S17–S19 |
| `gwanghwamun_dusk` | 해질녘, 광화문에 불이 들어옴 | S20–S22 |

---

## 1. 씬 구성표

| 씬 | 배경 | 초 | 누계 | 핵심 |
|---|---|---:|---:|---|
| S1 | wide | 18 | 0:18 | 인사 · 어제 배운 모음 8개 |
| S2 | wide | 20 | 0:38 | 오늘은 그 모음만으로 **단어**를 만든다 |
| S3 | wide | 18 | 0:56 | 소리 없는 ㅇ은 자리만 지킨다 (한 줄) |
| S4 | statue | 22 | 1:18 | **아이** — 삽화 카드 등장 |
| S5 | statue | 20 | 1:38 | 아이 — 음절 끊어 읽기 (블록 스냅) |
| S6 | statue | 18 | 1:56 | **이** — 한 글자도 단어 |
| S7 | stall | 22 | 2:18 | **오이** — 좌판의 초록 채소 |
| S8 | stall | 20 | 2:38 | 오이 — 끊어 읽기 |
| S9 | stall | 22 | 3:00 | **우유** — 하얀 우유 |
| S10 | stall | 20 | 3:20 | 우유 — 끊어 읽기 |
| S11 | stall | 18 | 3:38 | 아이·오이 — 뒷소리가 같다 |
| S12 | bench | 18 | 3:56 | **오** — 놀랄 때 그 소리 |
| S13 | bench | 22 | 4:18 | **아우** — 손아래 동생 |
| S14 | bench | 20 | 4:38 | 아우 — 끊어 읽기 |
| S15 | bench | 22 | 5:00 | **여우** — 숲의 여우 |
| S16 | bench | 20 | 5:20 | 여우 — 끊어 읽기 |
| S17 | path | 22 | 5:42 | 컬러 코딩 — 따뜻한 소리, 차가운 소리 |
| S18 | path | 20 | 6:02 | 'ㅣ'는 무채색 — 누구와도 어울린다 |
| S19 | path | 22 | 6:24 | **삽화 매칭 놀이** — 그림과 글자 잇기 |
| S20 | dusk | 22 | 6:46 | 일곱 단어 한 번에 |
| S21 | dusk | 20 | 7:06 | 거울 앞에서 또박또박 |
| S22 | dusk | 18 | 7:24 | 다음 시간 예고 · 인사 |

**총 22씬 · 7분 24초**

---

## 2. 씬별 나레이션

### S1 `gwanghwamun_wide` — 인사
**KO** 안녕하세요! 지난 시간엔 단모음 여덟 개를 배웠죠. ㅏ, ㅓ, ㅗ, ㅜ, ㅡ, ㅣ, ㅐ, ㅔ.
**EN** Hello! Last time we learned the eight simple vowels — ㅏ, ㅓ, ㅗ, ㅜ, ㅡ, ㅣ, ㅐ, ㅔ.
**텍스트박스** 단모음 8개
**화면 한글** ㅏ ㅓ ㅗ ㅜ ㅡ ㅣ ㅐ ㅔ

### S2 `gwanghwamun_wide` — 오늘의 목표
**KO** 오늘은 그 모음만으로 만드는 아주 쉬운 첫 단어들을 함께 익혀 봐요.
자음은 하나도 쓰지 않습니다.
**EN** Today we'll learn the very first words made from those vowels alone. Not a single consonant.
**텍스트박스** 모음만으로 만드는 단어
**화면 한글** 모음 + 모음 = 단어

### S3 `gwanghwamun_wide` — ㅇ 한 줄
**KO** 글자를 쓸 때 앞자리에 동그라미 ㅇ이 앉지만, 소리는 나지 않아요. 자리만 지키는 빈 의자랍니다.
**EN** When we write, a small circle ㅇ sits in front — but it makes no sound. It just holds the seat.
**텍스트박스** ㅇ = 소리 없는 자리
**화면 한글** 아 = ㅇ + ㅏ

### S4 `gwanghwamun_statue` — 아이
**KO** 첫 번째 단어, 아이. 어린아이를 뜻하는 말이에요. 받침 없이 ㅏ와 ㅣ, 모음 두 개로만 이루어졌어요.
**EN** Our first word — 아이. It means a child. Just two vowels, ㅏ and ㅣ, and no batchim.
**텍스트박스** 아이 (a child)
**화면 한글** 아이 · **삽화** 아이 그림 카드

### S5 `gwanghwamun_statue` — 아이 끊어 읽기
**KO** 끊어서 두 번. 아 — 이. 이제 붙여서 한 번. 아이. 따라 해 보세요.
**EN** Break it in two. 아 — 이. Now together. 아이. Say it with me.
**텍스트박스** 아 + 이 → 아이
**화면 한글** 아│이 → 아이 (블록 스냅)

### S6 `gwanghwamun_statue` — 이
**KO** 두 번째, 이. 입을 옆으로 활짝 당겨 내는 ㅣ 하나면 단어가 돼요. 우리 몸의 이, 바로 치아를 뜻하지요.
**EN** Second — 이. A single ㅣ, lips pulled wide, is already a word. It means a tooth.
**텍스트박스** 이 (a tooth)
**화면 한글** 이 · **삽화** 치아 그림 카드

### S7 `gwanghwamun_stall` — 오이
**KO** 세 번째, 오이. 아삭아삭한 초록 채소죠. ㅗ와 ㅣ, 역시 모음 두 개예요.
**EN** Third — 오이, a crunchy green cucumber. Again two vowels, ㅗ and ㅣ.
**텍스트박스** 오이 (a cucumber)
**화면 한글** 오이 · **삽화** 오이 그림 카드

### S8 `gwanghwamun_stall` — 오이 끊어 읽기
**KO** 입술을 동그랗게 모았다가 옆으로 당기며. 오 — 이. 오이.
**EN** Round your lips, then pull them wide. 오 — 이. 오이.
**텍스트박스** 오 + 이 → 오이
**화면 한글** 오│이 → 오이 (블록 스냅)

### S9 `gwanghwamun_stall` — 우유
**KO** 네 번째, 우유. 하얗고 고소한 우유예요. ㅜ와 ㅠ, 둘 다 입술을 동그랗게 내미는 소리죠.
**EN** Fourth — 우유, sweet white milk. Both ㅜ and ㅠ push the lips forward and round.
**텍스트박스** 우유 (milk)
**화면 한글** 우유 · **삽화** 우유팩 그림 카드

### S10 `gwanghwamun_stall` — 우유 끊어 읽기
**KO** 천천히. 우 — 유. 우유.
**EN** Slowly now. 우 — 유. 우유.
**텍스트박스** 우 + 유 → 우유
**화면 한글** 우│유 → 우유 (블록 스냅)

### S11 `gwanghwamun_stall` — 뒷소리가 같다
**KO** 아이와 오이. 뒷소리가 같지요? 둘 다 이로 끝나요. 앞소리 하나가 바뀌면 뜻이 달라집니다.
**EN** 아이 and 오이 — same ending, both end in 이. Change one sound in front and the meaning changes.
**텍스트박스** 아이 ↔ 오이
**화면 한글** 아**이** · 오**이**

### S12 `gwanghwamun_bench` — 오
**KO** 다섯 번째, 오. 놀랄 때 오! 하고 내는 그 소리, 그대로 단어가 돼요. 숫자 다섯이기도 하지요.
**EN** Fifth — 오. The sound you make when surprised, 오!, is itself a word. It also means five.
**텍스트박스** 오 (oh! / five)
**화면 한글** 오 · **삽화** 손가락 다섯 그림 카드

### S13 `gwanghwamun_bench` — 아우
**KO** 여섯 번째, 아우. 손아래 동생을 다정하게 부르는 말이에요.
**EN** Sixth — 아우, a warm word for a younger sibling.
**텍스트박스** 아우 (younger sibling)
**화면 한글** 아우 · **삽화** 형제 그림 카드

### S14 `gwanghwamun_bench` — 아우 끊어 읽기
**KO** ㅏ에서 ㅜ로. 입을 크게 열었다 동그랗게 모으며. 아 — 우. 아우.
**EN** From ㅏ to ㅜ. Open wide, then round. 아 — 우. 아우.
**텍스트박스** 아 + 우 → 아우
**화면 한글** 아│우 → 아우 (블록 스냅)

### S15 `gwanghwamun_bench` — 여우
**KO** 일곱 번째, 여우. 숲에 사는 붉은 여우예요. 여와 우, 이것도 모음뿐이랍니다.
**EN** Seventh — 여우, the red fox of the forest. 여 and 우 — vowels only again.
**텍스트박스** 여우 (a fox)
**화면 한글** 여우 · **삽화** 여우 그림 카드

### S16 `gwanghwamun_bench` — 여우 끊어 읽기
**KO** 여 — 우. 여우. 여는 ㅣ와 ㅓ가 빨리 이어진 소리예요. 지금은 한 소리로 익혀 두세요.
**EN** 여 — 우. 여우. 여 is ㅣ sliding quickly into ㅓ. For now, just learn it as one sound.
**텍스트박스** 여 + 우 → 여우
**화면 한글** 여│우 → 여우 (블록 스냅)

### S17 `gwanghwamun_path` — 컬러 코딩
**KO** 소리에는 온도가 있어요. ㅏ와 ㅗ는 밝고 따뜻한 소리, ㅓ와 ㅜ는 어둡고 차가운 소리.
같은 온도끼리 만나면 자석처럼 잘 붙습니다.
**EN** Sounds have temperature. ㅏ and ㅗ are bright and warm; ㅓ and ㅜ are dark and cool.
Same temperature, and they snap together like magnets.
**텍스트박스** 따뜻한 소리 · 차가운 소리
**화면 한글** ㅏ ㅗ (난색) ／ ㅓ ㅜ (한색)

### S18 `gwanghwamun_path` — 중성 ㅣ
**KO** 그런데 ㅣ는 색이 없어요. 서 있는 사람을 본뜬 글자라서, 따뜻한 소리와도 차가운 소리와도
사이좋게 어울립니다.
**EN** But ㅣ has no colour. Shaped after a standing person, it gets along with warm and cool alike.
**텍스트박스** ㅣ = 중립
**화면 한글** ㅏ+ㅣ · ㅗ+ㅣ · ㅜ+ㅣ

### S19 `gwanghwamun_path` — 삽화 매칭 놀이
**KO** 이제 맞춰 볼까요? 그림을 보고 단어를 말해 보세요. 초록 채소는? 하얀 음료는? 붉은 짐승은?
**EN** Now let's match. Look at the picture and say the word. The green vegetable? The white drink? The red animal?
**텍스트박스** 그림 ↔ 글자
**화면 한글** 오이 · 우유 · 여우 (카드 3장)

### S20 `gwanghwamun_dusk` — 모으기
**KO** 오늘 배운 일곱 단어를 모아 볼까요? 아이, 이, 오이, 우유, 오, 아우, 여우.
모두 자음 없이 모음만으로 만든 단어랍니다.
**EN** Let's gather today's seven words — 아이, 이, 오이, 우유, 오, 아우, 여우.
Every one made of vowels alone.
**텍스트박스** 오늘의 일곱 단어
**화면 한글** 아이 이 오이 우유 오 아우 여우

### S21 `gwanghwamun_dusk` — 복습 과제
**KO** 오늘 배운 단어를 거울 앞에서 또박또박 말해 보세요. 입 모양이 보이면 소리도 또렷해집니다.
**EN** Practice today's words clearly in front of a mirror. When you can see the shape, the sound gets clearer.
**텍스트박스** 거울 앞에서 연습
**화면 한글** 아이 오이 우유

### S22 `gwanghwamun_dusk` — 예고 · 인사
**KO** 다음 시간엔 소리 없는 ㅇ에 모음을 붙여 글자 블록을 만들어 봐요. 또 만나요!
**EN** Next time we'll join the silent ㅇ to a vowel and build syllable blocks. See you soon!
**텍스트박스** 내일 — ㅇ + 모음
**화면 한글** ㅇ + ㅏ = 아

---

## 3. 자막 규격

| 대상 | 표기 |
|---|---|
| 자모 | `ㅏ [a]` |
| 단어 | `아이 [a-i] (a child)` — ★철자가 아니라 **실제 발음** |
| 문장 | `한글 (뜻)` |

5개국어 ko / en / ja / **zh-Hans** / **es-419** · 소프트 srt · **번인 금지**
★외국어 자막에도 **한글을 남긴다**

## 4. 나레이션

영문·한글 **두 편** · 1.1배속 · 초안 edge-tts → 최종 Azure(선희/Emma)
★**한글 낱말·자모는 영어판에서도 한국어 음성**으로 읽는다
