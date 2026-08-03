# W24 시나리오 — 종합 진단과 수료 발표 (DDP) [3그룹 분할본 v2]

> **한 줄**: 일곱이 한꺼번에 나오지 않는다. **세 그룹이 번갈아 나와 24주를 되짚고**,
> 마지막에 전원이 모여 수료하고, 밤 광장의 군무로 닫는다.
> 사장님 지시 2026-08-03. 규격은 `W24_concept.md`, 모션은 `W24_motion.md`.
> (구버전 = `W24_scenario_v1_backup.md`)

---

## 0. 이 회차의 원칙

1. **★그룹 분할.** 한 화면에 일곱을 다 세우지 않는다. 세 그룹이 자기 차례를 가진다.

   | 그룹 | 구성 | 맡은 복습 | 성격 |
   |---|---|---|---|
   | **A** | 스틱맨 · 졸라맨 · 졸라걸 (3인) | **글자와 수** — 한글의 탄생 · 자모 · 모아쓰기 · 숫자 · 시간 | 선(線) 캐릭터. 글자를 직접 그린다 |
   | **B** | 인준 · 지은 (2인) | **거리에서 쓰는 말** — 쇼핑 · 교통 · 길찾기 · 취미 | 밖으로 다니며 묻고 답한다 |
   | **C** | 마담제이 · 티쳐제이 (2인) | **마음과 생각의 말** — 하루 · 날씨 · 감정 · 의견 · 여행 · 약속 | 앉아서 이야기한다 |

2. **합류는 이음매에만.** A→B 사이(S11), B→C 사이(S19)에 두 그룹이 잠깐 겹친다.
   전원이 모이는 건 **수료식(S28~)** 부터다. 그래야 마지막이 커진다.
3. **낮 → 밤.** 로비(아침) → 전시장(낮) → 둘레길(오후) → 잔디·장미정원(해질녘) → 교실(저녁) → 광장(밤).
4. **★전원이 화면 중앙을 향한다.** 왼편 인물은 오른쪽을, 오른편 인물은 왼쪽을 본다.
   글자는 인물의 **반대편**에 놓는다. (P1~P10 · `W24_motion.md`)
5. **단어·짧은 문장·긴 문장 처리**는 앞 회차 원칙 그대로 —
   자모는 `[발음]`, 단어는 `[실제발음] (뜻)`, 문장은 `(뜻)`. 철자가 아니라 **실제 발음**을 적는다.
6. **끝은 이미 완성된 피날레.** `W24/_final/W24_finale_50s_MASTER.mp4` (50초).
   ★이번 렌더에서는 **제외**한다(사장님 지시).

---

## A. 배경 계획

### A-1. 배경 동영상 4개 — "획기적 변화"가 있는 자리에만

| 키 | 씬 | 0-2초 | 2-6초 | 6-8초 |
|---|---|---|---|---|
| `ddp_arrive` | S1 | DDP 은빛 곡면 외관 원경 | 카메라가 곡면을 따라 미끄러지며 입구로 진입 | 로비 안쪽에 멎음 |
| `board_time` | S5 | 흰 벽에 분필 글씨 하나 | 글씨가 빛나며 **자모가 벽에서 걸어 나온다** | 전시장 공간에 떠 있음 |
| `classroom_sejong` | S31 | 교실 정면, 세종대왕 초상 액자 | ★**초상이 수염을 쓰다듬는다** | **빙그레 웃고** 다시 정지 |
| `plaza_gather` | S33 | 텅 빈 광장, 해질녘 | 사방에서 사람들이 몰려들어 원을 만듦 | 원 한가운데가 비고 조명이 켜짐 |

### A-2. 배경 정지 8키

| 키 | 내용 | 좌 앵커(x≈380) | 우 앵커(x≈850) |
|---|---|---|---|
| `ddp_lobby` | 은빛 곡면 로비, 곡선 난간 | 곡선 난간 | 안내 기둥 |
| `ddp_hall` | 전시장 내부, **흰 곡면 벽** — 선 캐릭터가 가장 잘 보이는 곳 | 낮은 전시 좌대 | 유리 난간 |
| `ddp_ruins` | 지하 유구전시장 — 조선 성벽·이간수문 | 성벽 돌 | 안내판(글자 없음) |
| `ddp_path` | 디자인둘레길 — 외벽 곡선을 따라 오르는 산책로 | 곡선 난간 | 조명 기둥 |
| `ddp_grass` | 잔디언덕, 은빛 건물이 뒤로 | 낮은 돌턱 | 벤치 |
| `ddp_rose` | LED 장미정원(초저녁) | 낮은 화단 턱 | 조명 기둥 |
| `classroom` | 교실. 칠판(왼쪽 뒤) · 의자 · 정면 벽 **세종대왕 초상 액자** | 칠판 아래 분필받이 | 빈 의자 등받이 |
| `plaza_day` | 어울림광장 낮, 넓은 바닥 | 낮은 단 | 가로등 |

> 공통: 왼편은 단순하게 · 바닥은 가로로 끊김 없이 · **글자·간판 문자 금지**.

---

## B. 캐릭터 자산 계획

### B-1. 키 규격 (`W24_concept.md` 확정 · 변경 없음)
인준 770 · 졸라맨 761 · 티쳐제이 749 · 스틱맨 749 · 지은 706 · 졸라걸 697 · 마담제이 693 (px, 서기 기준)

### B-2. 그룹 동작컷 — ★8초 → 192프레임 → **3장 중 1장 = 64컷**
사장님 확정(2026-08-03). Flow에 등록된 캐릭터를 참조로 **그룹 단위 동영상**을 만들고,
24fps 8초(192프레임)를 **3프레임마다 하나씩 뽑아 64컷** 투명컷으로 만든다(컷랑).

| 그룹 | 동작 키 | 내용 |
|---|---|---|
| A (3인) | `a_write_jamo` | 셋이 나란히 서서 허공에 자모를 그린다 |
| | `a_stack_block` | 셋이 글자 블록을 위로 쌓아 올린다 |
| | `a_count_up` | 셋이 차례로 손가락을 펴 수를 센다 |
| | `a_cheer` | 셋이 동시에 뛰며 환호 |
| B (2인) | `b_ask_price` | 인준이 묻고 지은이 손으로 값을 알려 준다 |
| | `b_point_way` | 지은이 길을 가리키고 인준이 그쪽을 본다 |
| | `b_ride_gesture` | 둘이 나란히 손잡이를 잡는 시늉 |
| | `b_highfive` | 둘이 하이파이브 |
| C (2인) | `c_talk_sit` | 둘이 마주 앉아 이야기한다 |
| | `c_weather_look` | 둘이 하늘을 올려다본다 |
| | `c_emotion_face` | 둘이 서로 보며 표정이 바뀐다 |
| | `c_nod_agree` | 둘이 서로 끄덕인다 |

### B-3. 걷기 — ★기존 자산 재사용
`walk_r_*` / `walk_l_*` 는 **이미 만들어 둔 것을 그대로 쓴다.** 새로 만들지 않는다.

---

## C. 오늘의 표현 (수료·소감·희망)

`배웠어요` · `어려웠어요` · `재미있었어요` · `-고 싶어요` · `더 배우고 싶어요` · `덕분에` ·
`고맙습니다` · `축하합니다` · `수료` · `앞으로` · `계속` · `열심히` · `자신 있어요` · `잘했어요` · `함께`

---

## 씬 (34 + 피날레)

### 1막 — 도착 (S1–S3) · 아침

- **S1** 마지막 시간에 모였어요 | `함께` | "안녕하세요! 오늘은 마지막 시간이에요. 스물네 주를 '함께' 걸어온 친구들이 한자리에 모였어요." → (Hello! This is our last lesson. The friends who walked twenty-four weeks '함께' (together) have gathered in one place.) | `ddp_arrive`[VIDEO] | 아무도 없는 로비로 카메라가 들어옴 · 인물은 아직 없다 | 도입
- **S2** 여기는 곡선으로 지은 집 | `배웠어요` | "여기는 서울의 디자인 전시장이에요. 곧은 선이 하나도 없죠. 우리도 곧게만 오지 않았어요. 돌아가며 '배웠어요'." → (This is a design hall in Seoul — not one straight line in it. We didn't come in a straight line either. We '배웠어요' (learned) by winding around.) | `ddp_lobby`[STILL] | 티쳐제이만 Z30에 서서 오른쪽을 보며 소개 | 장소소개
- **S3** 오늘의 순서 | `수료 · 앞으로` | "순서는 셋이에요. 글자를 되짚고, 거리의 말을 되짚고, 마음의 말을 되짚어요. 그리고 '수료'해요." → (Three parts today: we look back at the letters, then the street words, then the words of the heart. And then we '수료' (graduate).) | `ddp_lobby`[STILL] | 티쳐제이 Z30 point_board 오른쪽으로 손을 뻗어 안쪽을 가리킴 | 흐름

### 2막 — A그룹: 글자와 수 (S4–S10) · 낮 · 스틱맨 · 졸라맨 · 졸라걸

- **S4** 선으로 된 셋이 나왔어요 | `함께` | "먼저 선으로 그린 세 친구예요. 졸라맨, 졸라걸, 스틱맨. 글자도 선이니까 잘 어울리죠." → (First, the three drawn in lines: 졸라맨, 졸라걸, 스틱맨. Letters are lines too, so they suit each other.) | `ddp_hall`[STILL] | A그룹 walk_r 로 왼쪽에서 들어와 Z35·Z50·Z65 에 서서 정면 전환 | 그룹A등장
- **S5** 첫 주에 배운 것 — 하늘과 땅과 사람 | `ㄱ · ㄴ · ㅇ` | "첫 주에는 한글이 어떻게 태어났는지 배웠어요. 하늘과 땅과 사람. 그 셋에서 글자가 나왔어요." → (In week one we learned how Hangeul was born — heaven, earth and human. The letters came out of those three.) | `board_time`[VIDEO] | 흰 벽에서 자모가 걸어 나옴 · A그룹 a_write_jamo | 복습W1
- **S6** 자음을 다시 그려 봐요 | `ㄱ · ㄷ · ㅁ` | "자음은 입 모양을 본떴어요. 'ㄱ'은 혀뿌리, 'ㅁ'은 입술. 자, 따라 그려 보세요." → (Consonants copy the shape of the mouth: 'ㄱ' the root of the tongue, 'ㅁ' the lips. Trace them with me.) | `ddp_hall`[STILL] | A그룹 a_write_jamo · 글자는 화면 오른편, 셋은 왼편에서 오른쪽을 봄 | 복습W1
- **S7** 모아쓰면 글자가 돼요 | `가 · 나 · 다` | "자음과 모음을 모아쓰면 한 글자가 돼요. 블록처럼 쌓이죠. '가', '나', '다'." → (Put a consonant and a vowel together and you get one syllable block: '가', '나', '다'.) | `ddp_hall`[STILL] | A그룹 a_stack_block 셋이 글자 블록을 위로 쌓음 | 복습W2
- **S8** 받침이 어려웠어요 | `어려웠어요` | "아래에 하나 더 붙으면 받침이에요. 이게 '어려웠어요'. 그래도 여러분은 해냈죠." → (One more piece underneath is a 받침 (final consonant). That part '어려웠어요' (was hard) — but you did it.) | `ddp_hall`[STILL] | 졸라맨 Z40 앞으로 한 발 · 나머지 둘 끄덕임 | 복습W2
- **S9** 수를 세어 봐요 | `하나 · 둘 · 셋` | "이제 수예요. 하나, 둘, 셋. 한국말은 수를 두 가지로 세요. 하나 둘 셋, 그리고 일 이 삼." → (Now numbers: 하나, 둘, 셋. Korean counts two ways — 하나 둘 셋, and 일 이 삼.) | `ddp_hall`[STILL] | A그룹 a_count_up 셋이 차례로 손가락을 폄 | 복습W8
- **S10** 몇 시예요? | `몇 시예요?` | "시간을 물을 때는 '몇 시예요?' 해요. 한 시, 두 시, 세 시. 자, 따라 해 보세요." → (To ask the time, say '몇 시예요?' (what time is it?): 한 시, 두 시, 세 시. Repeat after me.) | `ddp_hall`[STILL] | 졸라걸 Z60 손을 들어 시계를 가리킴 왼쪽 | 복습W8

### 이음매 1 — A와 B가 만나요 (S11)

- **S11** 밖에서 부르는 소리 | `함께` | "그때 밖에서 부르는 소리가 들려요. 다른 친구들이 벌써 나가 있었어요." → (Just then someone calls from outside — the other friends had already gone out.) | `ddp_path`[STILL] | A그룹 Z25~45 왼편 · 인준·지은 Z75·Z88 오른편에서 손을 흔듦 · 서로 마주봄 | 합류1

### 3막 — B그룹: 거리에서 쓰는 말 (S12–S18) · 오후 · 인준 · 지은

- **S12** 둘이 다니며 배운 말 | `배웠어요` | "인준이와 지은이는 밖에서 쓰는 말을 배웠어요. 가게에서, 길에서, 버스에서요." → (인준 and 지은 learned the words you use outside — in shops, on the street, on the bus.) | `ddp_path`[STILL] | B그룹만 남음 · 인준 Z35 오른쪽 · 지은 Z65 왼쪽 마주봄 | 그룹B등장
- **S13** 얼마예요? | `얼마예요?` | "가게에서는 '얼마예요?' 하고 물어요. 값을 묻는 가장 짧은 말이에요. 자, 따라 해 보세요." → (In a shop you ask '얼마예요?' (how much is it?) — the shortest way to ask a price. Repeat after me.) | `ddp_path`[STILL] | B그룹 b_ask_price 인준이 묻고 지은이 손으로 값을 알려 줌 | 복습W10
- **S14** 깎아 주세요 | `깎아 주세요` | "조금 싸게 사고 싶으면 '깎아 주세요' 해요. 웃으면서 말하면 더 좋아요." → (If you want it cheaper, say '깎아 주세요' (please give me a discount) — better with a smile.) | `ddp_path`[STILL] | 지은 Z62 고개를 살짝 기울이며 웃음 왼쪽 | 복습W10
- **S15** 어떻게 가요? | `어떻게 가요?` | "길에서는 '어떻게 가요?' 하고 물어요. 지하철로 가요, 버스로 가요, 걸어서 가요." → (On the street you ask '어떻게 가요?' (how do I get there?): by subway, by bus, on foot.) | `ddp_ruins`[STILL] | B그룹 b_ride_gesture 둘이 나란히 손잡이를 잡는 시늉 | 복습W12
- **S16** 왼쪽으로 가세요 | `왼쪽 · 오른쪽 · 곧장` | "길을 알려 줄 때는 '왼쪽으로 가세요', '오른쪽으로 가세요', '곧장 가세요' 해요." → (To give directions: '왼쪽으로 가세요' (go left), '오른쪽으로 가세요' (go right), '곧장 가세요' (go straight).) | `ddp_ruins`[STILL] | B그룹 b_point_way 지은이 오른쪽을 가리키고 인준이 그쪽을 봄 | 복습W13
- **S17** 지하에는 옛 성벽이 | `배웠어요` | "여기 지하에는 조선의 성벽이 남아 있어요. 옛것 위에 새것이 서 있죠. 공부도 그래요." → (Below ground here, a Joseon-era wall remains. The new stands on the old — study is like that too.) | `ddp_ruins`[STILL] | 인준 Z38 point_board 성벽 쪽을 가리킴 · 지은 끄덕임 | 장소의미
- **S18** 자주 해요? | `자주 · 가끔 · 전혀` | "취미를 물을 때는 얼마나 자주 하는지도 물어요. '자주'는 부사예요. 자주, 가끔, 전혀." → (When you ask about hobbies, you also ask how often. '자주' (often) is an adverb: 자주, 가끔, 전혀.) | `ddp_path`[STILL] | B그룹 b_highfive 둘이 하이파이브 | 복습W16

### 이음매 2 — B와 C가 만나요 (S19)

- **S19** 잔디에 앉은 두 사람 | `함께` | "둘레길 끝, 잔디언덕에 두 사람이 먼저 앉아 있었어요." → (At the end of the path, on the grass hill, two people were already sitting.) | `ddp_grass`[STILL] | 인준·지은 Z20·Z32 왼편에서 걸어옴 · 마담제이·티쳐제이 Z70·Z84 앉아 있음 · 서로 봄 | 합류2

### 4막 — C그룹: 마음과 생각의 말 (S20–S27) · 해질녘 · 마담제이 · 티쳐제이

- **S20** 앉아서 나누는 말 | `배웠어요` | "마담제이와 티쳐제이는 마음을 말하는 법을 배웠어요. 앉아서 천천히 하는 이야기죠." → (마담제이 and 티쳐제이 learned how to speak the heart — the slow kind of talk you have sitting down.) | `ddp_grass`[STILL] | C그룹만 남음 · 티쳐제이 Z35 오른쪽 · 마담제이 Z65 왼쪽 마주 앉음 | 그룹C등장
- **S21** 하루를 말해요 | `일어나요 · 먹어요 · 자요` | "하루 일과를 말해 봐요. 일어나요, 먹어요, 일해요, 자요. 순서대로 말하면 쉬워요." → (Describe your day: 일어나요 (get up), 먹어요 (eat), 일해요 (work), 자요 (sleep). In order, it's easy.) | `ddp_grass`[STILL] | C그룹 c_talk_sit 둘이 마주 앉아 이야기 | 복습W14
- **S22** 날씨가 좋아요 | `비가 와요 · 맑아요` | "날씨는 이렇게 말해요. 맑아요, 비가 와요, 바람이 불어요. 오늘은 참 좋네요." → (For weather: 맑아요 (it's clear), 비가 와요 (it's raining), 바람이 불어요 (it's windy). Today is a fine one.) | `ddp_grass`[STILL] | C그룹 c_weather_look 둘이 하늘을 올려다봄 | 복습W15
- **S23** 기뻐요, 속상해요 | `기뻐요 · 속상해요` | "마음도 말할 수 있어요. 기뻐요, 속상해요, 설레요. 마음을 말하면 가벼워져요." → (You can speak feelings too: 기뻐요 (I'm glad), 속상해요 (I'm upset), 설레요 (I'm excited). Saying it makes it lighter.) | `ddp_rose`[STILL] | C그룹 c_emotion_face 둘이 서로 보며 표정이 바뀜 | 복습W18
- **S24** 제 생각에는 | `제 생각에는` | "의견을 말할 때는 '제 생각에는'으로 시작해요. 부드럽고 분명하게 들려요." → (To give an opinion, start with '제 생각에는' (in my opinion) — it sounds gentle and clear.) | `ddp_rose`[STILL] | 마담제이 Z62 stand_speak 왼쪽 · 티쳐제이 끄덕임 | 복습W19
- **S25** 저도 그렇게 생각해요 | `저도 그렇게 생각해요` | "동의할 때는 '저도 그렇게 생각해요' 해요. 짧지만 사이를 가깝게 만드는 말이에요." → (To agree: '저도 그렇게 생각해요' (I think so too) — short, but it brings people closer.) | `ddp_rose`[STILL] | C그룹 c_nod_agree 둘이 서로 끄덕임 | 복습W19
- **S26** 가 본 적이 있어요 | `가 본 적이 있어요` | "여행 이야기도 했죠. 경험은 '가 본 적이 있어요'로 말해요. 저는 제주도에 가 본 적이 있어요." → (We talked about travel too. For experience: '가 본 적이 있어요' (I have been there). I have been to Jeju.) | `ddp_rose`[STILL] | 티쳐제이 Z38 explain 오른쪽 · 마담제이 듣기 | 복습W22
- **S27** 약속을 잡아요 | `약속을 잡다 · 시간 조율` | "그리고 지난주엔 '약속을 잡다'와 '시간 조율'을 배웠어요. 여럿이 만나려면 꼭 필요하죠." → (And last week: '약속을 잡다' (set up an appointment) and '시간 조율' (coordinating times) — you need both to meet as a group.) | `ddp_rose`[STILL] | C그룹 c_talk_sit 둘이 손짓으로 날짜를 맞춤 | 복습W23

### 5막 — 전원 합류 · 수료식 (S28–S33) · 저녁

- **S28** 일곱이 모였어요 | `함께` | "이제 일곱이 다 모였어요. 스물네 주 만에 처음으로 한 교실에 앉았어요." → (Now all seven are together — sitting in one classroom for the first time in twenty-four weeks.) | `classroom`[STILL] | 전원 착석 · 티쳐제이 Z22 교단 오른쪽 · 학생 6인 Z50~Z84 왼쪽 | 전원합류
- **S29** 이제 수료해요 | `수료` | "이제 '수료'해요. 과정을 다 마쳤다는 뜻이에요. 자, 따라 해 보세요." → (Now we '수료' (complete the course) — it means you've finished the whole thing. Repeat after me.) | `classroom`[STILL] | 티쳐제이 call_name 오른쪽 · 전원 정면 | 어휘핵심
- **S30** 축하합니다, 고맙습니다 | `축하합니다 · 고맙습니다` | "이름을 부르면 나와서 받아요. 주는 사람은 '축하합니다', 받는 사람은 '고맙습니다'." → (When your name is called, come and receive it. The giver says '축하합니다' (congratulations), the receiver '고맙습니다' (thank you).) | `classroom`[STILL] | 티쳐제이 give_flower 오른쪽 · 인준 receive_flower 왼쪽 · 나머지 박수 | 어휘
- **S31** 앞에서 보고 계셨어요 | `덕분에` | "저 앞에서 계속 보고 계셨어요. 한글을 만드신 분이요. 그분 '덕분에' 우리가 여기까지 왔어요." → (Someone was watching from the front all along — the man who made Hangeul. '덕분에' (thanks to) him, we came this far.) | `classroom_sejong`[VIDEO] | 세종대왕 초상이 수염을 쓰다듬고 빙그레 웃는다 작게 한 번 · 전원 정면을 봄 | 디테일
- **S32** 자신 있어요 | `자신 있어요 · 잘했어요` | "이제 말할 수 있어요. '자신 있어요.' 서로에게도 말해 줘요. '잘했어요.'" → (Now you can say it: '자신 있어요' (I feel confident). And say it to each other too: '잘했어요' (well done).) | `classroom`[STILL] | 전원 박수 · 티쳐제이 clap 오른쪽 | 감정
- **S33** 밖으로 나가요 | `앞으로 · 계속` | "자, 밖으로 나가요. 오늘은 축제예요. '앞으로'도 '계속' 이어져요." → (Now let's go outside — today is a celebration. It keeps going '앞으로' (onward), '계속' (continuously).) | `plaza_gather`[VIDEO] | 사방에서 군중이 몰려와 원을 만듦 · 7인 원 안으로 걸어 들어감 | 전환

### 6막 — 피날레 (S34) · 밤

- **S34** 여러분 차례예요 | `자신 있어요 · 고맙습니다` | "여기까지 왔어요. 이제 여러분 차례예요. 자신 있게, 계속하세요. 고맙습니다!" → (You made it this far. Now it's your turn — go on with confidence. Thank you!) | `plaza_day`[STILL] | 이 씬 뒤에 완성된 피날레 50초를 붙인다 | 피날레

> ★**이번 렌더에서는 피날레(50초)를 붙이지 않는다.** 사장님 검수용이므로 S1~S34까지만 렌더한다.
> 최종 납품 때 `W24/_final/W24_finale_50s_MASTER.mp4` 를 S34 뒤에 이어 붙인다.

---

## D. 예상 러닝타임
씬 34 · 씬 길이 `max(KO_TTS, EN_TTS) + 0.40s` · W22/W23 캘리브레이션(KO 3.07음절/초, EN 8.63자/초)
→ **추정 7:10~7:40** (+ 피날레 50초 = 8:00~8:30)

## E. 생성 수량

| 구분 | 수량 | 생성처 | 비고 |
|---|---|---|---|
| 배경 동영상 | 4 | Flow(Veo) | `flow_make_bgmv` 절차 |
| 배경 정지 | 8 | 나노 바나나 | 왼편 단순·글자 금지 |
| 그룹 동작컷 | 12종 × 64컷 | Flow 8초 → 컷랑 | ★192프레임에서 3장 중 1장 |
| 걷기 | 0 | — | ★**기존 자산 재사용** |
| 세종대왕 초상 애니 | 1 | Flow (S31 전용) | |
| 피날레 | 완료 | — | `W24/_final/` 보관됨 |

## F. 착수 순서
1. `W24_motion.md` 그룹별 모션 블로킹 확정
2. `build_w24.py` → DB 반영 → **선희 음성 전량 사전 생성**
3. 자막 KO/EN + 발음기호
4. 배경 12키 · 그룹 동작컷 12종
5. 렌더(피날레 제외) → 교정앱
