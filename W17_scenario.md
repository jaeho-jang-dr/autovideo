# W17 시나리오 — 존댓말↔반말 · 축약어 · K컬처 학습법 (티쳐제이 · 경주)

> **주제:** 존댓말↔반말('요/습니다' 빼기) + 축약어(생축·아아·꿀잼) + K팝/K드라마 학습법 + 반말 전화회화
> **캐릭터:** 티쳐제이(남) — 레퍼런스 락 = `assets/characters/teacher_jay_style4.png` (체크무늬 파랑·흰 셔츠 + 베이지 팬츠 + 흰 스니커즈 + 대머리에 새싹머리 한 가닥, 굵은 검정 외곽선, 흰 벙어리손)
> **배경:** **경주** — 불국사(입구·계단·단청·석가탑·안뜰)·정원 + 남산 등산로 + 석굴암 + 아웃트로
> **길이:** 48씬
> **끝맺음 다듬기:** 원본이 "~더라고요/~편이에요"를 20회+ 반복 → **뜻 유지, 교사 존댓말로 자연스럽고 다양하게** (~요/~죠/~답니다/~봅시다/~보세요/~거든요/~네요/~ㅂ니다 순환)
> **어휘 표기 원칙:** KO·EN 나레이션 모두 **`'한글' (뜻)`** 형식 — 따옴표 한글은 ko 여성음성(선희) 발음, add_pron이 [발음] 자막 자동 ([[feedback-korean-pronunciation-principle]])

---

## 배경 10종 (불투명, `w17/backgrounds/`)

| key | 장소 | 비고 |
|-----|------|------|
| `w17_bg_entrance` | 불국사 일주문/입구 전경 | 도입·마무리 |
| `w17_bg_stairs` | 청운교·백운교 돌계단 | 등록 설명 파트 |
| `w17_bg_dancheong` | 처마 밑 단청(색색 서까래) | 반말 비교 파트 |
| `w17_bg_seokgatap` | 안뜰의 석가탑 | 인사말 비교 파트 |
| `w17_bg_courtyard` | 대웅전 앞마당 | 축약어 파트 |
| `w17_bg_garden` | 안양문 옆 연못 정원(녹음) | 축약어·마무리 |
| `w17_bg_namsan_trail` | ★ 경주 남산 등산로(돌길·숲) | K컬처 학습법 |
| `w17_bg_seokguram` | ★ 석굴암 본존불/석굴 입구 | 전화회화 도입 |
| `w17_bg_temple_valley` | 불국사 원경/계곡 | 도입·마무리 |
| `w17_bg_outro` | 노을 진 앞마당 | 구독 유도·엔드카드 |

## 포즈 24종 (투명 컷아웃, `assets/characters/tj_w17_<key>.png`, style4 락)

인사/감정: `wave`(손 흔들기)·`bow`(정중히 절)·`greet_both`(양팔 벌려 환영) · 설명: `explain`(두 손 설명)·`explain_open`(양손 벌려)·`present_right`(오른손바닥 제시) · 가리키기: `point_left`·`point_right`·`point_up`·`point_self`(자기 가슴) · 뉘앙스: `think`(턱에 손)·`compare`(양손 좌우 비교)·`finger_up`(검지 강조) · 반응: `clap`(박수)·`cheer`(양팔 만세)·`surprise`(놀람) · 소품/수업: `phone`(전화받기)·`phone_show`(폰 화면 가리키기)·`sing`(K팝 가사 낭독)·`hand_ear`(귀에 손, 듣기) · 걷기: `walk_right_1`/`walk_right_2`·`walk_left_1`/`walk_left_2`

---

# 씬별 시나리오 (48씬)

> 표기: **[씬] 자막(KO) | 화면글자 | 나레이션(KO) → (EN) | 배경 | 티쳐제이 동작(2~3 교차) | 태그**

## 1막 — 도입: 경주 불국사 (S0–S6)

- **S0** (무나레이션·추천카드) | (없음) | [정적 10초] | `w17_bg_entrance` | (정지) | 카드
- **S1** 경주 불국사에 오신 걸 환영해요! | `경주 불국사` | "안녕하세요, 여러분! 여기는 '경주'에 있는 '불국사'예요. 세계유산으로 이름난 아름다운 절이죠. 오늘도 저와 함께 살아 있는 한국어를 배워 볼까요?" → (Hello, everyone! This is '불국사' (Bulguksa) Temple in '경주' (Gyeongju) — a beautiful temple famous as a World Heritage site. Shall we learn living, real Korean together today?) | `w17_bg_entrance` | walk_right_1→walk_right_2→wave | 인사
- **S2** 진짜 한국어 | `드라마 · 케이팝` | "드라마를 보거나 '케이팝' (K-pop)을 들으면, 교과서엔 없는 진짜 한국어가 귀에 쏙쏙 들어와요. 그런 표현들이 바로 오늘의 주인공이에요." → (When you watch dramas or listen to '케이팝' (K-pop), you hear real Korean that no textbook teaches. Those expressions are today's stars.) | `w17_bg_temple_valley` | explain→present_right | 동기
- **S3** 편한 말 · 줄인 말 | `반말 · 축약어` | "오늘은 친구끼리 쓰는 '반말'과, 짧게 줄인 '축약어'를 함께 배웁니다. 그러면 한국 문화가 한층 더 가깝게 느껴질 거예요." → (Today we'll learn '반말' (casual speech) and '축약어' (shortened words). Korean culture will feel much closer to you.) | `w17_bg_temple_valley` | greet_both→explain_open | 예고
- **S4** 불국사를 거닐며 | `천 년 역사` | "천 년 역사가 살아 숨 쉬는 불국사를 거닐며 공부하니, 어렵던 한국어도 훨씬 재미있게 다가오네요." → (Strolling through Bulguksa, alive with a thousand years of history, even tricky Korean becomes much more fun.) | `w17_bg_entrance` | walk_right_1→walk_right_2→present_right | 분위기
- **S5** 말투가 달라져요 | `누구에게?` | "한국어엔 아주 중요한 특징이 하나 있어요. 상대가 누구냐에 따라 말투가 완전히 달라진다는 점이죠." → (Korean has one very important feature: the way you speak changes completely depending on who you're talking to.) | `w17_bg_stairs` | point_up→explain | 핵심예고
- **S6** 수업 시작! | `시작해요` | "자, 이 아름다운 돌계단 앞에서 오늘 수업을 시작해 봅시다. 다들 준비되셨나요?" → (Now, let's begin today's lesson before these beautiful stone stairs. Are you all ready?) | `w17_bg_stairs` | greet_both→present_right | 전환

## 2막 — 존댓말 vs 반말 ('요/습니다' 빼기) (S7–S18)

- **S7** 두 가지 말투 | `존댓말 ↔ 반말` | "한국어 말투는 크게 둘로 나뉩니다. 예의를 갖춘 '존댓말' (polite speech), 그리고 편하게 하는 '반말' (casual speech)이에요." → (Korean speech splits into two: '존댓말' (polite speech) and '반말' (casual speech).) | `w17_bg_stairs` | compare | 개념
- **S8** 언제 쓸까? | `어른 ↔ 친구` | "'존댓말' (polite speech)은 어른이나 처음 만난 사람에게 씁니다. 반대로 '반말' (casual speech)은 아주 친한 친구 사이에서만 쓰죠." → ('존댓말' (polite speech) is for elders and people you just met. '반말' (casual speech) is only for very close friends.) | `w17_bg_stairs` | point_left→point_right | 용법
- **S9** 비밀은 간단해요 | `'요' · '습니다' 빼기` | "비밀은 아주 간단해요. 문장 끝의 '요' (yo)나 '습니다' (seumnida)만 빼면 바로 반말이 됩니다. 함께 비교해 볼까요?" → (The secret is simple: just drop the ending '요' (yo) or '습니다' (seumnida), and it becomes casual. Let's compare!) | `w17_bg_stairs` | finger_up→explain | 규칙
- **S10** 밥 먹었어요? / 밥 먹었어? | `밥 먹었어요? → 밥 먹었어?` | "첫 번째예요. '밥 먹었어요?' (Have you eaten?) 여기서 '요'를 빼면, 친구에게는 '밥 먹었어?'가 됩니다." → (First: '밥 먹었어요?' (Have you eaten?). Drop the '요', and to a friend it becomes '밥 먹었어?'.) | `w17_bg_stairs` | present_right→clap | 비교1
- **S11** '요'만 빠졌어요 | `-요 X` | "들으셨나요? 두 문장의 끝만 다르죠. 친한 사이에선 '요'를 슬쩍 빼고 '밥 먹었어?'라고 편하게 묻는답니다." → (Did you hear it? Only the endings differ. Among close friends, we drop the '요' and casually ask '밥 먹었어?'.) | `w17_bg_dancheong` | explain→nod(=present_right) | 설명1
- **S12** 어디 가요? / 어디 가? | `어디 가요? → 어디 가?` | "두 번째예요. '어디 가요?' (Where are you going?) 이것도 친구끼리는 '요'를 빼고 '어디 가?'라고 물어요." → (Second: '어디 가요?' (Where are you going?). Among friends, drop the '요' and ask '어디 가?'.) | `w17_bg_dancheong` | point_right→present_right | 비교2
- **S13** 짧고 편하게 | `-요 X` | "'어디 가요?'가 '어디 가?'로, 이렇게 짧아지죠. 짧아질수록 더 가깝고 편한 사이라는 뜻이랍니다." → ('어디 가요?' shortens to '어디 가?'. The shorter it gets, the closer and more comfortable the relationship.) | `w17_bg_dancheong` | compare→explain | 설명2
- **S14** 고마워요 / 고마워 | `고마워요 → 고마워` | "고마운 마음도 마찬가지예요. '고마워요' (Thank you)에서 '요'를 빼면 친구에게 하는 '고마워'가 됩니다." → (Gratitude works the same. '고마워요' (Thank you) becomes '고마워' to a friend when you drop the '요'.) | `w17_bg_dancheong` | greet_both→present_right | 비교3
- **S15** 마음은 그대로 | `-요 X` | "말은 짧아져도 고마운 마음은 똑같아요. 가까운 친구에겐 '고마워'라고 따뜻하게 말해 보세요." → (The words shorten, but the gratitude stays the same. To a close friend, warmly say '고마워'.) | `w17_bg_seokgatap` | explain→wave | 설명3
- **S16** 잘 가요 / 잘 가 | `잘 가요 → 잘 가` | "헤어질 때도 그래요. '잘 가요' (Goodbye)에서 '요'를 빼면 친구에게 하는 '잘 가'가 됩니다." → (Same when parting. '잘 가요' (Goodbye) becomes '잘 가' to a friend without the '요'.) | `w17_bg_seokgatap` | wave→present_right | 비교4
- **S17** 끝만 잘 들어요 | `끝소리 [요X]` | "네 가지 모두 끝소리만 다르죠? 원어민을 따라 소리 내어 읽어 보세요. 끝의 '요'가 있고 없고를 귀로 느껴 봅시다." → (All four differ only at the ending. Read aloud after the native speaker, and feel the presence or absence of the final '요'.) | `w17_bg_seokgatap` | hand_ear→finger_up | 청취
- **S18** 반말 주의! | `상황에 맞게` | "다만 조심하세요. '반말' (casual speech)은 친하면 정겹지만, 어른이나 처음 본 사람에게 쓰면 아주 무례해 보입니다." → (But be careful: '반말' (casual speech) feels warm among friends, yet sounds very rude to elders or strangers.) | `w17_bg_seokgatap` | surprise→point_up | 주의

## 3막 — 축약어 (생축·아아·꿀잼) (S19–S28)

- **S19** 이번엔 축약어 | `축약어` | "이번엔 메신저나 SNS에서 자주 보이는 '축약어' (abbreviation)를 알아봅시다. 짧게 줄여 쓰는 재미있는 말이에요." → (Next, let's look at '축약어' (abbreviation), the fun shortened words you often see in messages and on social media.) | `w17_bg_courtyard` | explain→present_right | 개념
- **S20** 표준어는 아니지만 | `실생활 소통` | "'축약어' (abbreviation)는 정식 표준어는 아니에요. 하지만 알아 두면 요즘 한국 사람들의 대화를 훨씬 잘 이해하게 됩니다." → ('축약어' (abbreviation) isn't standard, but knowing it helps you understand real Korean conversations much better.) | `w17_bg_courtyard` | think→explain_open | 용법
- **S21** 빠르게 치다 보면 | `짧게 짧게` | "스마트폰으로 빠르게 메시지를 치다 보면, 자연스럽게 글자를 줄이게 되거든요. 표준어와 줄임말을 나란히 비교해 봐요." → (Typing fast on a smartphone, people naturally shorten words. Let's compare the full words with their short forms.) | `w17_bg_courtyard` | phone_show→present_right | 배경
- **S22** 생일 축하해 / 생축 | `생일 축하해 → 생축` | "'생일 축하해' (Happy birthday)를 짧게 줄이면 '생축'이 돼요. 친구 생일에 이렇게 톡을 보낸답니다." → ('생일 축하해' (Happy birthday) shortens to '생축'. Friends send this on birthdays.) | `w17_bg_courtyard` | cheer→present_right | 비교5
- **S23** 앞글자만 콕 | `앞글자` | "보세요, 앞글자만 콕 집어 '생축'이죠. 이렇게 각 단어의 첫 글자를 모으는 게 축약어의 기본이랍니다." → (See — just the first syllables make '생축'. Gathering each word's first letter is the basic rule of abbreviations.) | `w17_bg_garden` | explain→finger_up | 설명5
- **S24** 아이스 아메리카노 / 아아 | `아이스 아메리카노 → 아아` | "카페에서도 써요. '아이스 아메리카노' (iced americano)는 너무 길죠? 그래서 흔히 '아아'라고 줄여 부릅니다." → (Cafés use it too. '아이스 아메리카노' (iced americano) is long, so people often shorten it to '아아'.) | `w17_bg_garden` | present_right→clap | 비교6
- **S25** 카페에서 주문! | `아아 주세요` | "이제 카페에서 '아아 주세요'라고 말하면 진짜 한국 사람 같아요. 따뜻한 건 '뜨아'라고 한답니다." → (Order '아아 주세요' at a café and you'll sound truly Korean. The hot one is '뜨아'!) | `w17_bg_garden` | explain→cheer | 활용6
- **S26** 진짜 재미있다 / 꿀잼 | `진짜 재미있다 → 꿀잼` | "'진짜 재미있다' (really fun)는 어떻게 줄일까요? 달콤한 '꿀'과 '재미'가 만나 '꿀잼'이 됩니다." → (How about '진짜 재미있다' (really fun)? Sweet '꿀' (honey) meets '재미' (fun) to make '꿀잼'.) | `w17_bg_garden` | think→cheer | 비교7
- **S27** 반대말도 있어요 | `노잼` | "반대로 하나도 재미없으면 '노잼'이라고 해요. 영어 '노'와 '재미'를 붙인 말이죠. 참 기발하죠?" → (The opposite, not fun at all, is '노잼' — English 'no' plus '재미' (fun). Clever, right?) | `w17_bg_garden` | explain_open→clap | 확장7
- **S28** 축약어도 때와 장소 | `공식 자리 X` | "줄임말은 친구 사이에선 정겹지만, 공식적인 자리나 어른 앞에서는 피하는 게 좋습니다. 상황에 맞게 골라 쓰세요." → (Slang is warm among friends, but avoid it in formal settings or before elders. Choose the right words for the situation.) | `w17_bg_courtyard` | point_up→explain | 주의

## 4막 — K팝·K드라마 학습법 (S29–S32)

- **S29** K컬처로 공부해요 | `케이팝 · 케이드라마` | "이제 '케이팝' (K-pop)과 '케이드라마' (K-drama)로 한국어를 똑똑하게 공부하는 법을 이야기해 봅시다." → (Now let's talk about smart ways to study Korean with '케이팝' (K-pop) and K-drama.) | `w17_bg_namsan_trail` | walk_right_1→walk_right_2→present_right | 전환
- **S30** 최고의 학습 도구 | `발음 · 억양` | "좋아하는 노래와 드라마는 그냥 즐기기만 하면 아까워요. 발음과 억양을 익히는 최고의 교재가 되거든요." → (It's a waste just to enjoy your favorite songs and dramas — they're the best material for learning pronunciation and intonation.) | `w17_bg_namsan_trail` | explain→point_up | 원리
- **S31** 가사를 소리 내어 | `한 줄씩 낭독` | "좋아하는 노래 가사를 한 줄씩 소리 내어 읽어 보세요. 이게 발음 교정에 정말 큰 도움이 됩니다." → (Read your favorite lyrics aloud, one line at a time. This helps enormously with fixing your pronunciation.) | `w17_bg_namsan_trail` | sing→clap | 방법1
- **S32** 드라마 섀도잉 | `멈추고 따라 하기` | "드라마를 볼 땐 대사에서 잠깐 멈추고, 자막을 보며 한 문장씩 따라 해 보세요. 이 '섀도잉' (shadowing) 훈련이 아주 효과적이랍니다." → (With dramas, pause on a line and shadow the subtitle sentence by sentence. This '섀도잉' (shadowing) practice is very effective.) | `w17_bg_namsan_trail` | hand_ear→present_right | 방법2

## 5막 — 반말 전화회화 실전 (S33–S38)

- **S33** 전화 연습해 볼까요? | `친구와 전화` | "그럼 배운 반말로, 친한 친구와 나누는 실제 전화 통화를 연습해 봅시다. 조용한 '석굴암'에서요." → (Now let's practice a real phone call with a close friend using the casual speech we learned — here at the peaceful '석굴암' (Seokguram).) | `w17_bg_seokguram` | phone→present_right | 도입
- **S34** 먼저 잘 들어요 | `귀 기울여` | "친구가 편한 반말로 건네는 질문을, 먼저 귀 기울여 정확히 들어 보세요." → (First, listen carefully to the casual question your friend asks.) | `w17_bg_seokguram` | hand_ear→point_up | 청취
- **S35** 주말에 뭐 해? | `주말에 뭐 해?` | "질문이에요. '주말에 뭐 해?' (What are you doing this weekend?) 친구끼리 아주 자연스럽게 묻는 반말 질문이죠." → (The question: '주말에 뭐 해?' (What are you doing this weekend?) — a very natural casual question between friends.) | `w17_bg_seokguram` | phone→present_right | 질문
- **S36** 끝을 내려요 | `해요 → 해` | "'주말에 뭐 해요?'에서 '요'가 빠져 '주말에 뭐 해?'가 됐죠. 끝을 살짝 내려 말하는 게 반말의 느낌이에요." → ('주말에 뭐 해요?' drops the '요' to become '주말에 뭐 해?'. Lowering the ending gives that casual feel.) | `w17_bg_seokguram` | compare→explain | 설명
- **S37** 그냥 집에서 케이드라마 봐. 너는? | `그냥 집에서 케이드라마 봐. 너는?` | "이렇게 답해요. '그냥 집에서 케이드라마 봐. 너는?' (Just watching K-dramas at home. You?) 편안하게 되묻는 '너는?'이 참 친근하죠." → (Answer like this: '그냥 집에서 케이드라마 봐. 너는?' (Just watching K-dramas at home. You?). The casual '너는?' feels friendly.) | `w17_bg_garden` | phone_show→present_right | 답변
- **S38** 억양까지 따라 해요 | `섀도잉` | "이제 자연스러운 발음과 억양으로 '그냥 집에서 케이드라마 봐. 너는?'을 섀도잉해 보세요. 진짜 대화처럼요!" → (Now shadow '그냥 집에서 케이드라마 봐. 너는?' with natural pronunciation and intonation — like a real conversation!) | `w17_bg_garden` | sing→cheer | 실습

## 6막 — 정리·참여·마무리 (S39–S47)

- **S39** 오늘의 정리 | `존댓말↔반말 · 축약어` | "오늘은 존댓말과 반말의 차이를 하나하나 비교하고, 실생활 줄임말까지 배웠습니다. 정말 알차죠?" → (Today we compared '존댓말' and '반말' one by one, and learned everyday slang too. Quite a full lesson!) | `w17_bg_garden` | explain→clap | 정리
- **S40** 큰 소리로 반복 | `또박또박` | "실생활 문장은 또박또박 큰 소리로 반복해 읽는 게 좋아요. 그럴수록 한국어 읽는 속도가 쑥쑥 빨라집니다." → (Read real-life sentences aloud, clearly and repeatedly. Your Korean reading speed will grow quickly.) | `w17_bg_garden` | present_right→finger_up | 학습법
- **S41** 문장으로 익혀요 | `단어 넘어 문장` | "낱글자 암기를 넘어 진짜 회화 문장으로 연습하다 보면, 어느새 한국어가 훨씬 친숙해질 거예요." → (Practice with real conversation sentences, not just isolated letters, and Korean will soon feel much more familiar.) | `w17_bg_garden` | explain_open→nod(=present_right) | 격려
- **S42** 오늘 꼭 한 번 | `하루 한번 [1줄]` | "오늘 배운 비교 표현을, 하루에 한 번은 꼭 써 보시길 권합니다. 작은 연습이 큰 실력이 되니까요." → (I recommend using today's expressions at least once a day. Small practice builds big skills.) | `w17_bg_temple_valley` | point_up→present_right | 실천
- **S43** 경주에서 배우니 | `천 년 고도` | "천 년 고도 경주에서 한국어를 공부하니, 배움이 한결 더 생생하게 느껴지네요." → (Studying Korean in Gyeongju, a thousand-year-old capital, makes the learning feel wonderfully vivid.) | `w17_bg_temple_valley` | greet_both→cheer | 감상
- **S44** 순서를 지켜요 | `존댓말 먼저` | "먼저 표준이 되는 존댓말을 충분히 익히고, 친한 친구와 조금씩 반말을 섞는 순서가 가장 좋습니다." → (Master standard '존댓말' first, then gradually mix in '반말' with close friends — that's the best order.) | `w17_bg_courtyard` | compare→explain | 조언
- **S45** 다음에 또 만나요 | `또 다른 명소에서` | "다음 시간에도 아름다운 한국의 명소에서, 유익한 실생활 한국어로 찾아뵙겠습니다." → (Next time, I'll meet you again at another beautiful Korean landmark with useful, real-life Korean.) | `w17_bg_entrance` | walk_right_1→walk_right_2→wave | 예고
- **S46** 구독과 좋아요! | `구독 · 좋아요` | "구독과 좋아요는 더 풍성한 한국어 교육을 만드는 데 큰 힘이 됩니다. 오늘도 정말 잘하셨어요. 안녕히 계세요!" → (Subscribing and liking give great strength to making richer Korean lessons. Great job today — goodbye!) | `w17_bg_outro` | greet_both→wave→bow | 마무리
- **S47** (무나레이션·추천카드) | (없음) | [정적 10초] | `w17_bg_outro` | (정지) | 카드

---

## 다듬기 노트 (반복 끝맺음 제거)
- 원본 "~더라고요"(약 14회)·"~편이에요/편입니다"(약 9회) → 전부 제거하고 문맥별로 **~요/~죠/~됩니다/~봅시다/~보세요/~거든요/~네요/~ㅂ니다/~할까요?** 로 다양화. 교사 존댓말 톤 유지, 교육 내용(4개 비교쌍·3개 축약어·학습법·전화회화) 그대로 보존.
- 추가 학습 포인트(무리 없이 자연 삽입): '뜨아'(S25)·'노잼'(S27)·'너는?'(S37) — 원본 어휘 범위 안에서 짝을 이루는 확장.
