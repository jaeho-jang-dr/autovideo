# W20 시나리오 v2 (재작성·중복제거) — 돌발 상황 대처와 문제 해결 (인준 · 이태원)

> **v2 변경(사장님 지시 2026-07-23)**: ① 후반 중복(재교육) 제거 → 28씬·6~7분. ② 걷기 남발 제거 = 짧은 걸어들어오기 2회(`walk_r`)+깊은 걸어들어오기 2회(`walk_deep`)만, 나머지는 서서 다양한 표정. ③ **자막=영어만**, 대신 따옴표 한글을 늘려 **선희 DB 발음을 최대한 많이**. ④ 캐릭터=인준(`injun_w20`), 배경=이태원 23종 재사용.
> **자막 표기(영어판 1줄)**: 단어/짧은문장 `'한글' [발음] (뜻)`, 긴문장 `한글 (영어뜻)`. `[발음]`은 add_pron이 SRT에 자동. 번인 금지·소프트, **영어 트랙만**.
> **나레이터**: 영어=Emma, 따옴표 한글=선희 DB(초판 edge-tts). 한글은 선희·영어는 엠마로 자동 분리.
> **표기**: **[씬] 자막(KO 원문) | 화면글자(좌상단) | 나레이션(KO) → (EN) | 배경 | 인준 동작·표정 | 태그**
> **걷기 토큰**: `walk_r`=왼끝→30% 짧게 / `walk_deep`=왼끝→중간까지 깊게.

---

## 1막 — 도입 (S1–S3)

- **S0** (무나레이션·추천카드) | (없음) | [정적 8초] | `station` | (정지) | 카드
- **S1** 이태원에 잘 오셨어요! | `이태원` | "안녕하세요! 세계 각국의 문화가 모인 서울 '이태원'이에요. 오늘은 갑작스러운 돌발 상황에 한국어로 대처하는 법을 배워 봐요!" → (Hi! This is Seoul's '이태원', where cultures from around the world meet. Today, let's learn to handle sudden emergencies in Korean!) | `station` | walk_r→wave→smile_bright | 인사
- **S2** 갑자기 이런 일이? | `돌발 상황` | "여행 중엔 갑자기 몸이 아프거나 소중한 물건을 '잃어버릴' 수 있어요. 그럴 때 가장 중요한 건 '침착'이에요." → (While traveling, you might suddenly feel sick or '잃어버리다' something precious. The most important thing is to stay '침착'.) | `food_street` | surprised→calm | 동기
- **S3** 도움은 부끄럽지 않아요 | `도와주세요` | "기억하세요. 위급할 땐 '도와주세요'라고 말하는 걸 부끄러워하지 마세요. 한국 사람들은 기꺼이 도와줘요." → (Remember: never be shy to say '도와주세요' in an emergency. Koreans are glad to help.) | `rooftop` | present_right→reassure | 핵심예고

## 2막 — 응급 어휘 (S4–S11)

- **S4** 아프다 | `아프다 (to be sick)` | "몸이 안 좋을 때는 '아프다'예요. 상태를 나타내는 형용사죠. 아픈 곳을 앞에 붙여 '배가 아파요'라고 해요." → (When you feel unwell: '아프다' (to be sick), a descriptive adjective. Put the spot in front: '배가 아파요' — my stomach hurts.) | `antique_street` | hurt→explain | 어휘1
- **S5** 다치다 | `다치다 (to get hurt)` | "넘어지거나 부딪쳐 몸을 상하면 '다치다'예요. 동사고요, '다리를 다쳤어요'처럼 써요." → (If you fall or bump into something: '다치다' (to get hurt), a verb. '다리를 다쳤어요' — I hurt my leg.) | `antique_street` | surprised→point_self | 어휘2
- **S6** 약국 | `약국 (pharmacy)` | "가벼운 증상엔 '약국'을 찾아요. 초록색 십자 표시가 있는 곳이에요. '약 주세요'라고 하면 돼요." → (For mild symptoms, find a '약국' — look for the green cross. Just say '약 주세요' — medicine, please.) | `pharmacy` | walk_deep→point_right→present_right | 어휘3
- **S7** 병원 | `병원 (hospital)` | "많이 아프거나 다치면 '병원'에 가요. '병원에 가고 싶어요'라고 하면 주변에서 길을 알려줄 거예요." → (If it's serious, go to a '병원'. Say '병원에 가고 싶어요' — I want to go to a hospital.) | `clinic` | explain→point_up | 어휘4
- **S8** 119 | `119 (구급·소방)` | "불이 나거나 크게 다쳐 구급차가 필요할 땐 '119'예요. 전화해서 '도와주세요'라고 해요." → (For fire or an ambulance, call '119'. Call and say '도와주세요'.) | `police_box` | phone→point_up | 어휘5
- **S9** 112 | `112 (경찰)` | "도둑을 만나거나 위험한 일엔 '112', 경찰이에요. '112'와 '119'는 24시간, 요금도 없어요." → (For crime or danger, call '112', the police. Both '112' and '119' are free, 24 hours.) | `police_box` | phone→explain | 어휘6
- **S10** 잃어버리다 | `잃어버리다 (to lose)` | "물건이 사라졌을 땐 '잃어버리다'예요. 동사고, 오늘의 핵심 표현이에요." → (When something's gone: '잃어버리다' (to lose), a verb — and today's key expression.) | `convenience` | search_pockets→think | 어휘7
- **S11** 도와주세요 | `도와주세요 (please help me)` | "가장 든든한 한마디, '도와주세요.' '돕다'에 '-아 주세요'를 붙인 아주 정중한 요청이에요." → (The most reassuring phrase: '도와주세요' — a polite request from '돕다' (to help).) | `convenience` | help_gesture→reassure | 어휘8

## 3막 — 핵심 문형 (S12–S17)

- **S12** ___을 잃어버렸어요 | `___을 잃어버렸어요` | "오늘의 핵심 문형이에요. '___을 잃어버렸어요.' 잃어버린 물건을 앞에 쏙 넣어요." → (Today's core pattern: '___을 잃어버렸어요' (I lost ___). Put the lost item in the blank.) | `alley` | explain_open→point_up | 개념
- **S13** 지갑을 잃어버렸어요 | `지갑 · 여권 · 휴대폰` | "'지갑을 잃어버렸어요.' '여권을 잃어버렸어요.' 물건만 바꾸면 다 돼요." → ('지갑을 잃어버렸어요' — I lost my wallet. Swap the item: '여권', '휴대폰'.) | `alley` | walk_r→search_pockets→explain | 예문1
- **S14** 도와주세요, ~ | `도와주세요, ~` | "앞에 '도와주세요'를 붙이면 더 간절하게 들려요. '도와주세요, 가방을 잃어버렸어요!'" → (Add '도와주세요' up front for urgency: '도와주세요, 가방을 잃어버렸어요!' — Help, I lost my bag!) | `gyeongridan` | help_gesture→worried | 예문2
- **S15** 어디에서 잃어버렸어요? | `어디에서 ~?` | "도와주는 사람이 물을 거예요. '어디에서 잃어버렸어요?' 그럼 '지하철에서요'라고 답해요." → (They'll ask '어디에서 잃어버렸어요?' — Where did you lose it? Answer '지하철에서요' — on the subway.) | `crosswalk` | curious→present_right | 활용
- **S16** 아파요 / 다쳤어요 | `아파요 · 다쳤어요` | "몸이 안 좋을 땐 '배가 아파요', 다쳤을 땐 '다리를 다쳤어요.' 아픈 곳을 콕 집어 말해요." → ('배가 아파요' — my stomach hurts; '다리를 다쳤어요' — I hurt my leg. Point to where it hurts.) | `crosswalk` | hurt→point_self | 예문3
- **S17** 정중하게 부탁해요 | `실례합니다` | "부탁은 정중하게 해요. '실례합니다'로 시작하면, 처음 본 사람도 기꺼이 도와줘요." → (Be polite. Start with '실례합니다' (excuse me), and even strangers will gladly help.) | `subway_inside` | bow→explain | 주의

## 4막 — 긴급 통화 (S18–S22)

- **S18** 무슨 일 · 어디 | `무슨 일 · 어디` | "신고할 땐 두 가지가 핵심이에요. '무슨 일'이 '어디'에서 일어났는지, 이 두 가지만 또렷하면 돼요." → (When you report, two keys: what happened, and where. Just be clear about those two.) | `lost_center` | walk_l→think→point_up | 개념(오른→왼 걷기)
- **S19** 무슨 일이에요? | `무슨 일이에요?` | "전화를 받으면 이렇게 물어요. '무슨 일이에요?' 그럼 침착하게 상황을 말하면 돼요." → (They'll ask '무슨 일이에요?' — What happened? Just explain calmly.) | `lost_center` | curious→present_right | 문형
- **S20** 119 통화 | `다쳤어요 · 여기는 ~` | "'119죠 친구가 다쳤어요 여기는 이태원이에요'라고 해요. 다친 일과 위치를 함께 말해요." → (Call and say '119죠 친구가 다쳤어요 여기는 이태원이에요' — Is this 119? My friend is hurt. We're in Itaewon.) | `hospital_er` | walk_deep→phone→worried | 듣기1
- **S21** 112 통화 | `잃어버렸어요 · 도와주세요` | "'112죠 가방을 잃어버렸어요 도와주세요'라고 해요. 잃어버린 물건과 장소를 또렷하게요." → (Call and say '112죠 가방을 잃어버렸어요 도와주세요' — Is this 112? I lost my bag. Please help.) | `hospital_er` | phone→explain | 듣기2
- **S22** 천천히 또박또박 | `다시 말해 주세요` | "급해도 천천히요. 못 알아들으면 '다시 말해 주세요.' 위치는 '여기는 이태원역 근처예요'처럼 알려요." → (Even in a rush, go slow. If they don't understand: '다시 말해 주세요' — please say it again. Give your spot: '여기는 이태원역 근처예요' — I'm near Itaewon Station.) | `street_night` | calm→point_right | 팁

## 5막 — 역할극 · 문화 · 마무리 (S23–S28)

- **S23** 약국에서 | `배가 아파요, 소화제 주세요` | "이제 역할극이에요. 약국에서 '배가 아파요', '소화제 주세요'라고 해요. 증상을 말하고 약을 청해요." → (Now a roleplay. At the pharmacy, say '배가 아파요', '소화제 주세요' — My stomach hurts; digestive medicine, please.) | `cafe_inside` | hurt→present_right | 역할극1
- **S24** 유실물 센터에서 | `가방을 잃어버렸어요` | "유실물 센터에서 '실례합니다, 가방을 잃어버렸어요. 도와주세요.' 물건과 장소를 함께요." → (At the lost-and-found: '가방을 잃어버렸어요. 도와주세요.' — I lost my bag. Please help.) | `noksapyeong` | search_pockets→help_gesture | 역할극2
- **S25** 서로 돕는 한국 문화 | `서로 도움 · 통역` | "한국에선 위급할 때 서로 돕는 걸 당연하게 여겨요. '112'와 '119'는 통역 도움도 받을 수 있어요." → (In Korea, helping in a crisis is natural. '112' and '119' even offer interpreter help.) | `info_center` | reassure→thumbs_up | 문화
- **S26** 감사 인사도 잊지 마요 | `고맙습니다` | "도움을 받았으면 '고맙습니다', '정말 감사합니다.' 작은 인사가 큰 고마움이 돼요." → (After help, say '고맙습니다' — thank you. A small thanks means a lot.) | `info_center` | bow→smile_bright | 예의
- **S27** 오늘의 정리 | `아프다 · 잃어버렸어요 · 도와주세요 · 112·119` | "오늘 우리는 '아프다', '다치다', '잃어버리다'를 배우고, '___을 잃어버렸어요'와 '도와주세요'로 도움을 청하고, '112'와 '119' 신고까지 익혔어요." → (Today we learned '아프다', '다치다', '잃어버리다', asked for help with '___을 잃어버렸어요' and '도와주세요', and practiced calling '112' and '119'.) | `sunset_hill` | explain_open→present_right | 총정리
- **S28** 다음에 또 만나요 | `구독 · 좋아요` | "여러분은 어떤 돌발 상황을 겪어 봤나요? 댓글로 들려주세요. 이태원에서 배운 든든한 한국어, 다음에 또 함께해요! 구독과 좋아요도 잊지 마세요." → (What emergencies have you faced? Tell us in the comments. Let's meet again for helpful Korean — and don't forget to subscribe and like!) | `sunset_hill` | wave→greet_both | 마무리
