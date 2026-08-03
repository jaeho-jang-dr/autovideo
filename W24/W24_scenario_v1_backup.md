# W24 시나리오 — 종합 진단과 수료 발표 (전 캐릭터 · DDP) [기획본 v1]

> **한 줄**: 낮의 교실에서 시작해 서울의 네온 밤 광장 군무로 끝나는 **수료식 회차**.
> 사장님 컨셉 확정 2026-07-28. 규격은 `W24_concept.md`, 방향 원칙은 `W23/W23_motion_plan.md`.

---

## 0. 이 회차의 원칙

1. **낮 → 밤.** 교실(낮) → DDP 산책(오후) → 광장(해질녘) → 네온 밤(피날레). 빛이 계속 변한다.
2. **복습은 가운데.** 앞은 소감·희망, 가운데는 칠판 복습, 뒤는 수료식과 축제.
3. **교실은 비운다.** 칠판과 의자뿐. 정면 벽에 **세종대왕 초상 액자** 하나.
   ★수료식 순간 초상이 **수염을 쓰다듬으며 빙그레 웃는다** — 작게, 한 번만. 이 회차 최고의 디테일.
4. **캐릭터 운용 2트랙**
   - 졸라맨 · 졸라걸 · 스틱맨 = **스틱맨 엔진(무료·관절)** 으로 앉기·손들기·춤까지 전부 처리
   - 티쳐제이 · 인준 · 지은 · 마담제이 = **캐릭터 스틸 애니메이션**(앉기/서기/동작 컷)
5. **끝은 플래시몹.** 광장에서 군중에 둘러싸여 음악에 맞춰 **군무**. 말을 줄이고 몸으로 닫는다.
6. 방향 원칙 P1~P10 유지 — 교실은 **티쳐 왼편(오른쪽 봄) / 학생 오른편(왼쪽 봄)** 이라 자동 충족.

---

## A. 배경 계획

### A-1. 배경 동영상 5개 — "획기적 변화"가 있는 자리에만

| 키 | 씬 | 0-2초 | 2-6초 | 6-8초 |
|---|---|---|---|---|
| `ddp_arrive` | S1 | DDP 은빛 곡면 외관 원경 | 카메라가 곡면을 따라 미끄러지며 입구로 진입 | 로비 안쪽에 멎음 |
| `board_time` | S15 | 칠판 클로즈업, 분필 글씨 | 글씨가 빛나며 **그림이 칠판에서 튀어나옴** | 교실 공간에 떠 있음 |
| `classroom_sejong` | S27 | 교실 정면, 세종대왕 초상 액자 | ★**초상이 수염을 쓰다듬는다** | **빙그레 웃고** 다시 정지 |
| `plaza_gather` | S32 | 텅 빈 광장, 해질녘 | 사방에서 사람들이 몰려들어 원을 만듦 | 원 한가운데가 비고 조명이 켜짐 |
| `night_finale` | S36 | 광장 군무, 해가 넘어감 | 네온이 순차 점등, 카메라 상승 | 서울 밤 스카이라인 전경 |

### A-2. 배경 정지 9키

| 키 | 내용 | 좌 앵커(x≈380) | 우 앵커(x≈850) |
|---|---|---|---|
| `classroom` | ★**우측 3/4 구도 교실**. 칠판(왼쪽 뒤) · 교탁 · 의자 원형 배치 · 정면 벽 **세종대왕 초상 액자** | 칠판 아래 분필받이 | 빈 의자 등받이 |
| `ddp_lobby` | 은빛 곡면 로비, 곡선 난간 | 곡선 난간 | 안내 기둥 |
| `ddp_hall` | 전시장 내부, 흰 곡면 벽 | 전시 좌대 | 유리 난간 |
| `ddp_ruins` | 지하 유구전시장 — 조선 성벽·이간수문 | 성벽 돌 | 안내판 |
| `ddp_grass` | 잔디언덕, 은빛 건물이 뒤로 | 낮은 돌턱 | 벤치 |
| `ddp_path` | 디자인둘레길 — 건물 외벽 곡선을 따라 오르는 산책로 | 곡선 난간 | 조명 기둥 |
| `ddp_rose` | LED 장미정원(초저녁) | 낮은 화단 턱 | 조명 기둥 |
| `plaza_day` | 어울림광장 낮, 넓은 바닥 | 낮은 단 | 가로등 |
| `seoul_neon` | 밤 네온 거리, 간판 불빛 | 난간 | 기둥 |

> 공통: 왼편은 단순하게 · 바닥은 가로로 끊김 없이 · **글자·간판 문자 금지**(네온은 색면과 도형으로만).

---

## B. 캐릭터 계획

### B-1. 키 규격 (`W24_concept.md` 확정)
인준 770 · 졸라맨 761 · 티쳐제이 749 · 스틱맨 749 · 지은 706 · 졸라걸 697 · 마담제이 693 (px, 서기 기준)

### B-2. 스틱맨 3인방 — **무료 트랙**
`stickman_factory.py`(12관절)로 생성: `sit_listen` `sit_raise_hand` `sit_clap` `stand_up` `walk` `dance_a` `dance_b` `write_jamo`
★`write_jamo` 는 `hangeul_write.py` 획순 애니메이션과 팔 관절을 물린다 — 선 캐릭터가 선 글자를 그린다.

### B-3. 사람 4인 — 스틸 애니메이션 트랙
| 캐릭터 | 필요한 컷 |
|---|---|
| 티쳐제이 | `stand_teach` `point_board` `call_name` `give_flower` `clap` `walk` `dance` |
| 인준 | `sit_listen` `sit_raise_hand` `stand_speak` `receive_flower` `clap` `walk` `dance` |
| 지은 | 〃 |
| 마담제이 | 〃 |

앉기 컷은 **의자를 포함**해 잘라내고, 책상이 없으므로 가림 레이어는 쓰지 않는다(교실에 의자만 둔다).

---

## C. 오늘의 표현 (수료·소감·희망)

`배웠어요` · `어려웠어요` · `재미있었어요` · `-고 싶어요` · `더 배우고 싶어요` · `덕분에` ·
`고맙습니다` · `축하합니다` · `수료` · `앞으로` · `계속` · `열심히` · `자신 있어요` · `잘했어요` ·
`제 생각에는` · `함께`

---

## 씬 (36)

### 1막 — 도착 · 오늘 무엇을 하는가 (S1–S5)

- **S1** DDP에 모이다 | `함께` | "안녕하세요! 오늘은 마지막 시간이에요. 스물네 주 동안 함께 공부한 친구들이 한자리에 모였어요." → (Hello! This is our last lesson. Everyone who studied together for twenty-four weeks has gathered in one place.) | `ddp_arrive`[VIDEO] | 전원 도착 · 티쳐제이 먼저 서 있고 나머지가 걸어 들어옴 | 도입
- **S2** 이곳은 디자인의 집 | `배웠어요` | "여기는 서울의 디자인 전시장이에요. 곡선으로만 지은 건물이죠. 우리도 곧게만 오지 않았어요. 돌아가며 배웠어요." → (This is a design hall in Seoul, built entirely of curves. We did not come in a straight line either — we learned by winding around.) | `ddp_lobby`[STILL] | 티쳐제이 `point_board`(→) · 학생들 걸어 들어옴 | 장소소개
- **S3** 교실에 앉다 | `함께` | "안쪽 방에 교실을 마련했어요. 칠판 하나, 의자 몇 개. 그리고 저 앞에는 한글을 만드신 분이 계세요." → (We set up a classroom in the inner room — one board, a few chairs. And up front hangs the man who created Hangeul.) | `classroom`[STILL] | 전원 착석 · 세종대왕 초상 정면 | 공간
- **S4** 오늘의 순서 | `수료 · 앞으로` | "순서는 간단해요. 소감을 나누고, 배운 걸 되짚고, 수료해요. 그리고 밖으로 나가요." → (Simple order: share how it went, look back at what we learned, graduate — then head outside.) | `classroom`[STILL] | 티쳐제이 `stand_teach`(→) · 학생 `sit_listen` | 흐름
- **S5** 먼저 소감부터 | `제 생각에는` | "먼저 소감이에요. '제 생각에는'으로 시작하면 편해요. 자, 누가 먼저 말할까요?" → (First, impressions. Starting with '제 생각에는' (in my opinion) makes it easy. Who wants to go first?) | `classroom`[STILL] | 티쳐제이 `point_board`(→) · 졸라맨 `sit_raise_hand` | 문형진입

### 2막 — 공부 이야기 (S6–S13)

- **S6** 어려웠어요 | `어려웠어요` | "'어려웠어요'는 힘들었던 걸 말할 때 써요. 받침이 어려웠어요. 자, 따라 해 보세요." → ('어려웠어요' (it was hard) is for what gave you trouble: 받침이 어려웠어요. Repeat after me.) | `classroom`[STILL] | 졸라맨 `stand_up` → `sit_listen` | 어휘1
- **S7** 재미있었어요 | `재미있었어요` | "'재미있었어요'는 즐거웠던 걸 말해요. 노래로 배운 게 재미있었어요. 자, 따라 해 보세요." → ('재미있었어요' (it was fun) is for what you enjoyed: 노래로 배운 게 재미있었어요. Repeat after me.) | `classroom`[STILL] | 졸라걸 `sit_raise_hand` → `sit_clap` | 어휘2
- **S8** 배웠어요 | `배웠어요` | "'배웠어요'는 익힌 걸 말해요. 스물네 주 동안 많이 배웠어요. 자, 따라 해 보세요." → ('배웠어요' (I learned) is for what you took in: 스물네 주 동안 많이 배웠어요. Repeat after me.) | `classroom`[STILL] | 인준 `stand_speak`(←) | 어휘3
- **S9** 덕분에 | `덕분에` | "'덕분에'는 고마움을 담는 말이에요. 선생님 덕분에 자신이 생겼어요. 자, 따라 해 보세요." → ('덕분에' (thanks to) carries gratitude: 선생님 덕분에 자신이 생겼어요. Repeat after me.) | `classroom`[STILL] | 지은 `stand_speak`(←) · 티쳐제이 끄덕임 | 어휘4·핵심
- **S10** 더 배우고 싶어요 | `더 배우고 싶어요` | "'-고 싶어요'는 바람을 말해요. 저는 더 배우고 싶어요. 자, 따라 해 보세요." → ('-고 싶어요' (I want to) states a wish: 저는 더 배우고 싶어요. Repeat after me.) | `classroom`[STILL] | 마담제이 `stand_speak`(←) | 어휘5·핵심
- **S11** 무엇이 더 필요할까요 | `계속 · 열심히` | "무엇이 더 필요할까요? 계속 듣고, 계속 말하는 거예요. 열심히 하면 늘어요." → (What else do we need? Keep listening, keep speaking. Work at it and it grows.) | `classroom`[STILL] | 티쳐제이 `stand_teach`(→) · 스틱맨 `sit_raise_hand` | 문형
- **S12** 자신 있어요 | `자신 있어요` | "이제 '자신 있어요'라고 말해 봐요. 인사는 자신 있어요. 자, 따라 해 보세요." → (Now try '자신 있어요' (I feel confident): 인사는 자신 있어요. Repeat after me.) | `classroom`[STILL] | 스틱맨 `stand_up` · 나머지 `sit_clap` | 어휘6
- **S13** 잘했어요 | `잘했어요` | "서로 칭찬해요. '잘했어요'는 짧지만 큰 말이에요. 자, 따라 해 보세요." → (Praise each other. '잘했어요' (well done) is short but carries a lot. Repeat after me.) | `classroom`[STILL] | 전원 `sit_clap` | 어휘7

### 3막 — 칠판 타임머신 · 복습 (S14–S23)

- **S14** 칠판을 봐요 | `배웠어요` | "이제 되짚어 볼까요? 칠판에 쓰면 그때가 살아나요." → (Shall we look back? Write it on the board and that week comes alive.) | `classroom`[STILL] | 티쳐제이 `point_board`(→) | 전환
- **S15** 첫 주 — 한글의 탄생 | `ㄱ · ㄴ · ㄷ` | "첫 주에는 한글이 어떻게 태어났는지 배웠어요. 하늘과 땅과 사람이었죠." → (In week one we learned how Hangeul was born — heaven, earth and human.) | `board_time`[VIDEO] | ★칠판에서 자모가 걸어 나옴 · 졸라맨·졸라걸 `write_jamo` | 복습 W1
- **S16** 자음과 모아쓰기 | `가 · 나 · 다` | "자음을 배우고 모아쓰기를 했어요. 글자가 블록처럼 쌓였죠." → (We learned consonants and stacked them into syllable blocks.) | `classroom`[STILL] | 스틱맨 `write_jamo` | 복습 W2
- **S17** 숫자와 시간 | `하나 · 둘 · 셋` | "숫자를 세고 시간을 말했어요. 한 시, 두 시, 세 시." → (We counted and told time: one o'clock, two, three.) | `classroom`[STILL] | 졸라걸 `sit_raise_hand` → `stand_up` | 복습 W8
- **S18** 쇼핑과 교통 | `얼마예요? · 어떻게 가요?` | "가게에서 '얼마예요?' 하고 물었고, 길에서 '어떻게 가요?' 하고 물었어요." → (We asked '얼마예요?' (how much) in shops and '어떻게 가요?' (how do I get there) on the street.) | `classroom`[STILL] | 인준 `stand_speak`(←) | 복습 W10·W12
- **S19** 하루와 날씨 | `일어나요 · 비가 와요` | "하루 일과를 말하고 날씨를 말했어요. 일어나요, 먹어요, 자요. 비가 와요." → (We described our day and the weather: get up, eat, sleep. It's raining.) | `classroom`[STILL] | 마담제이 `stand_speak`(←) · 지은 끄덕임 | 복습 W14·W15
- **S20** 감정과 의견 | `기뻐요 · 제 생각에는` | "마음을 말했고 의견을 말했어요. 기뻐요. 제 생각에는요." → (We named feelings and gave opinions: I'm glad. In my opinion.) | `classroom`[STILL] | 지은 `stand_speak`(←) | 복습 W18·W19
- **S21** 여행과 약속 | `가 본 적이 있어요 · 약속을 잡다` | "여행 경험을 말하고 약속을 잡았어요. 가 본 적이 있어요. 약속을 잡아요." → (We talked about trips and made plans: I have been there. Let's set a date.) | `classroom`[STILL] | 인준 `stand_speak`(←) · 전원 끄덕임 | 복습 W22·W23
- **S22** 스물네 주가 지나갔어요 | `앞으로` | "이렇게 스물네 주가 지나갔어요. 짧지 않았죠. 앞으로도 이어져요." → (And so twenty-four weeks went by. Not a short road. It keeps going from here.) | `classroom`[STILL] | 티쳐제이 `stand_teach`(→) · 전원 `sit_listen` | 마무리
- **S23** 이제 수료해요 | `수료` | "이제 수료해요. '수료'는 과정을 마쳤다는 뜻이에요. 자, 따라 해 보세요." → (Now we graduate. '수료' means you have completed the course. Repeat after me.) | `classroom`[STILL] | 티쳐제이 `call_name`(→) | 어휘8

### 4막 — 수료식 (S24–S28)

- **S24** 이름을 부릅니다 | `축하합니다` | "이름을 부를게요. 대답하고 앞으로 나오세요. '축하합니다'는 기쁜 날에 하는 말이에요." → (I'll call your names — answer and come forward. '축하합니다' (congratulations) is for happy days.) | `classroom`[STILL] | 티쳐제이 `call_name`(→) · 한 명씩 `stand_up` | 어휘9
- **S25** 꽃다발을 받아요 | `고맙습니다` | "꽃다발을 드려요. 받으면 '고맙습니다' 하고 인사해요." → (Here are your flowers. When you receive them, say '고맙습니다' (thank you).) | `classroom`[STILL] | 티쳐제이 `give_flower`(→) · 인준 `receive_flower`(←) | 어휘10
- **S26** 모두 박수 | `잘했어요` | "모두 박수! 서로에게 '잘했어요' 하고 말해 줘요." → (A round of applause! Tell each other '잘했어요' (well done).) | `classroom`[STILL] | 전원 `clap` / `sit_clap` | 감정
- **S27** ★ 앞에서 보고 계셨어요 | `고맙습니다` | "저 앞에서 계속 보고 계셨어요. 한글을 만드신 분이요." → (Someone has been watching from the front all along — the man who made Hangeul.) | `classroom_sejong`[VIDEO] | ★**세종대왕 초상이 수염을 쓰다듬고 빙그레 웃는다**(작게, 한 번) · 전원 정면을 봄 | ★디테일
- **S28** 밖으로 나가요 | `앞으로` | "자, 이제 밖으로 나가요. 오늘은 축제예요." → (Now let's head outside. Today is a celebration.) | `classroom`[STILL] | 전원 `stand_up` → `walk` | 전환

### 5막 — DDP를 걷다 (S29–S32)

- **S29** 지하에는 옛 성벽이 | `배웠어요` | "지하에는 조선의 성벽이 남아 있어요. 옛것 위에 새것이 서 있죠. 우리 공부도 그래요." → (Below ground, a Joseon-era wall remains. The new stands on the old — our study is like that too.) | `ddp_ruins`[STILL] | 티쳐제이 `point_board`(→) · 학생들 둘러봄 | 장소·의미
- **S30** 잔디언덕에서 | `재미있었어요` | "잔디언덕에 앉아 볼까요? 여기서 보면 건물이 물결 같아요." → (Shall we sit on the grass hill? From here the building looks like a wave.) | `ddp_grass`[STILL] | 전원 앉기 컷 · 졸라맨·졸라걸 뒹굴기 | 휴식
- **S31** 둘레길을 걸어요 | `계속` | "건물을 따라 도는 길이 있어요. 끝까지 걸으면 하늘이 가까워져요." → (A path curves around the building. Walk it to the end and the sky comes closer.) | `ddp_path`[STILL] | 전원 `walk` 우향 진행 | 이동
- **S32** 광장에 사람이 모여요 | `함께` | "광장에 사람들이 모이고 있어요. 무슨 일일까요?" → (People are gathering in the plaza. What's going on?) | `plaza_gather`[VIDEO] | ★사방에서 군중이 몰려와 원을 만듦 · 7인 원 안으로 | 전환

### 6막 — 플래시몹 · 서울의 밤 (S33–S36)

- **S33** 음악이 시작돼요 | `함께` | "음악이 시작돼요. 오늘은 말 대신 몸으로 해요." → (The music starts. Today we speak with our bodies instead of words.) | `plaza_day`[STILL] | 티쳐제이 `dance` 시작 · 나머지 따라 시작 | 도입
- **S34** 다 같이 춤을 | `함께 · 잘했어요` | "다 같이! 스물네 주를 몸으로 축하해요." → (Everybody! Let's celebrate twenty-four weeks with our whole bodies.) | `plaza_day`[STILL] | 전원 `dance_a` → `dance_b` · 군중도 따라 함 | 절정
- **S35** 해가 넘어가요 | `앞으로` | "해가 넘어가고 불빛이 켜져요. 서울의 밤이에요." → (The sun goes down and the lights come on. This is Seoul at night.) | `ddp_rose`[STILL] | 전원 `dance_b` · LED 장미 점등 | 전환
- **S36** 여러분 차례예요 | `자신 있어요 · 고맙습니다` | "여기까지 왔어요. 이제 여러분 차례예요. 자신 있게, 계속하세요. 고맙습니다!" → (You made it this far. Now it's your turn — go on with confidence. Thank you!) | `night_finale`[VIDEO] | ★군무 마무리 → 카메라 상승 → 서울 밤 전경 | 피날레

---

## D. 예상 러닝타임
씬 36 · 씬 길이 `max(KO_TTS, EN_TTS) + 0.40s` · W22/W23 캘리브레이션(KO 3.07음절/초, EN 8.63자/초)
→ **추정 7:30~8:00**. 목표 6:00~8:00 충족.

## E. 생성 수량

| 구분 | 수량 | 생성처 |
|---|---|---|
| 배경 동영상 | 5 | Flow(Veo) |
| 배경 정지 | 9 | 나노 바나나 + 동영상 프레임 추출 |
| 스틱맨 3인 동작 | 8종 × 3 | **stickman_factory.py (무료)** |
| 사람 4인 동작컷 | 7종 × 4 | Flow 8초 → 컷랑 |
| 세종대왕 초상 애니 | 1 | Flow (S27 전용) |

## F. 착수 순서
1. 스틱맨 3인방 8동작 생성(무료) → 교실 구도·키 검증
2. 배경 `classroom` 먼저 만들어 3/4 구도 확정
3. 사람 4인 앉은 동작 Flow → 컷랑 분해
4. 나머지 배경 · 세종대왕 초상 애니
5. `build_w24.py` → 렌더 → 교정
