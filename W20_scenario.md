# W20 시나리오 — 돌발 상황 대처와 문제 해결 (인준 · 이태원)

> **주제:** 응급 어휘(아프다·다치다·잃어버리다·약국·병원·112·119) + 핵심 문형 **"___을 잃어버렸어요 / 도와주세요"** + 아파요·다쳤어요 + 긴급 통화 듣기(무슨 일·어디) + 도움 요청 역할극 + 침착하게 대처하는 한국 문화
> **범위 고정(★제목 주제 안에서만):** 웹 훈민정음 20주차 2분 핵심영상(`hangeul_w20_stickman`) = "112·119 신고와 약국·병원 이용 등 위급할 때 도움받는 법" 바운더리 안에서만 확장. 참고=Gemini Notebook 한글교육 노트북(고급4주차, 돌발상황). ★주제를 넘지 않는다(호칭·여행계획 등 다음 주 내용 금지).
> **캐릭터:** 인준(남, 어린 대학생) — 락 = `home_vocab/injun_base.png` (짧은 검정 머리·캐주얼 반팔티·바지·운동화·플랫 카툰). ★자기소개("저는 인준입니다") 금지 — 바로 인사하고 시작. 어린 학생답게 표정 다양(놀람·걱정·안도·깨달음·뿌듯·침착 등).
> **배경:** **이태원** — ★**2씬당 1개, 총 23종**으로 이태원 구석구석(세계음식거리·루프탑·약국·병원·파출소·유실물센터·응급실·소방서·경리단길·성원 오르막·녹사평 등). 다국적·이국 거리 분위기 + 응급 상황 지원 장소.
> **길이:** 47씬(S0–S46) ≈ 8분
> **★걷기:** 인준 Veo 투명컷 16(오른쪽8+돌아오기8, `injun_w20_walk_{r,l}_0..7`)을 컷랑으로 신규 제작 → 순환+이동으로 거리 이동컷. [[action-cutout-animation-engine]] [[character-walk-veo-cutout-method]]
> **★자막 원칙(항상 동일·3단계):**
>   - **단어** = `'한글' [발음기호] (뜻)` — 예: `'약국' [yak-guk] (pharmacy)`
>   - **짧은 문장** = `'한글' [발음기호] (뜻)` — 예: `'도와주세요' [do-wa-ju-se-yo] (please help me)`
>   - **긴 문장** = `한글 (영어뜻)` — 발음기호 없이 **영어뜻만**
>   - 따옴표 한글=선희 발음, `add_pron`이 [로마자] 자막 자동. **번인 금지·소프트 자막**. KO 자막에도 발음기호(외국인 학습). es-419/zh-Hans.
> **품사 짚기(표준):** "'잃어버리다'는 **동사**", "'아프다'는 상태를 나타내는 **형용사**", "'도와주세요'는 '돕다'+'-아 주세요'의 **정중한 요청**" 짧게.
> **★나레이터/성우(두 번 렌더 방지):**
>   - **DB 선희(따옴표 한글 발음)** = **처음부터 Azure TTS 선희**(`ko-KR-SunHiNeural`) — 초안·최종 재사용.
>   - **영어 나레이션 = Emma**(`en-US-EmmaMultilingualNeural`): EN 초안=edge-tts → 최종만 Azure.
>   - **KO 러닝 나레이션 = 선희**: KO 최종=Azure.
>   - **★렌더 순서: 영어판 먼저** 렌더 → 교정앱 → 확정 시 KO + Azure 최종.
>   - 1.1배속·딜레이0. [[tts-narration-tier-policy]] [[tts-cache-engine-trap]]
> **좌상단 텍스트박스:** 화면글자=좌상단 코랄 박스(build_w20가 cap 비우고 박스PNG static). [[project-w19]] 방식.

---

## 배경 23종 (불투명, `w20/backgrounds/`, 1280×720, 2씬당 1개 · 이태원 구석구석)

| # | key | 장소 | 씬 |
|---|-----|------|----|
| 1 | `station` | 이태원 거리 초입·다국적 간판(글자 없음)·전구 조명 | S1–2 |
| 2 | `food_street` | 세계음식 거리·각국 노점·이국 인파 | S3–4 |
| 3 | `rooftop` | 루프탑 테라스·초저녁 서울 전경 | S5–6 |
| 4 | `antique_street` | 앤틱 가구·이국 상점 언덕 거리 | S7–8 |
| 5 | `pharmacy` | 약국 앞·초록 십자 표시(글자 없음) | S9–10 |
| 6 | `clinic` | 의원 입구·적십자 표지·깔끔한 로비 | S11–12 |
| 7 | `police_box` | 파출소 앞·파란 표지등(112) | S13–14 |
| 8 | `convenience` | 24시 편의점 앞·야간 조명 | S15–16 |
| 9 | `alley` | 이태원 좁은 언덕 골목·계단 | S17–18 |
| 10 | `mosque_road` | 서울중앙성원 오르막·이국 거리 | S19–20 |
| 11 | `gyeongridan` | 경리단길 카페 골목·화분 | S21–22 |
| 12 | `crosswalk` | 큰 사거리 횡단보도·다국적 인파 | S23–24 |
| 13 | `plaza` | 호텔 앞 광장·분수·벤치 | S25–26 |
| 14 | `subway_inside` | 지하철 역사 내부·개찰구 | S27–28 |
| 15 | `lost_center` | 유실물 센터 안내데스크·선반 | S29–30 |
| 16 | `hospital_er` | 병원 응급실 입구·구급차(119) | S31–32 |
| 17 | `street_night` | 밤 이태원 번화가·네온 불빛 | S33–34 |
| 18 | `bus_stop` | 버스정류장·정류장 지붕·노선표(글자 없음) | S35–36 |
| 19 | `cafe_inside` | 카페 안·창가 자리·따뜻한 조명 | S37–38 |
| 20 | `fire_station` | 소방서 앞·소방차 차고(119) | S39–40 |
| 21 | `noksapyeong` | 녹사평·용산공원 초입 잔디·나무 | S41–42 |
| 22 | `info_center` | 관광 안내소 앞·다국어 안내판(글자 없음) | S43–44 |
| 23 | `sunset_hill` | 이태원 언덕에 노을·거리 실루엣 | S45–46 |

> 배경 규칙(★W18·W19 교훈): 하나의 연속 장면으로 전체를 꽉 채움. 왼편(인준 자리)은 풍경이 복잡하지 않게(연속 유지, 흰칸·seam 금지). **글자·숫자·상표 금지**(112·119·약국 등은 색·기호로만 암시). [[lesson-render-review-rules]]

## 포즈 30종 (투명 컷아웃, `assets/graphics/poses/injun_w20_<key>.png`, casual 락 · 오른쪽 향함) + 걷기 16컷

- **인사/기본:** `wave`·`greet_both`·`bow`
- **설명/제시:** `explain`·`explain_open`·`present_right`·`point_right`·`point_self`·`point_up`
- **응급/도움:** `worried`(눈썹 모으고 걱정)·`hurt`(아픈 곳에 손·찡그림)·`help_gesture`(두 손 앞으로·도와주세요)·`search_pockets`(주머니 뒤짐·물건 찾음)·`phone`(휴대폰으로 신고)·`calm`(손바닥 아래로·침착)·`reassure`(괜찮아요·손 내밀어 안심)·`relieved`(안도의 한숨)
- **★다양한 표정(어린 학생):** `surprised`(놀람)·`curious`(궁금·몸 기울여)·`aha`(깨달음! 검지 번쩍)·`proud`(뿌듯·가슴에 손)·`smile_bright`(환한 미소)·`determined`(파이팅·주먹 불끈)·`think`(턱에 손)·`nod_agree`(밝게 끄덕)·`thumbs_up`(엄지척)·`weigh`(양손 저울=상황 판단)·`confident`(자신만만)·`finger_up`(검지 강조)·`look_view`(손차양 둘러봄)
- **걷기(신규 제작):** `walk_r_0..7`(오른쪽) · `walk_l_0..7`(왼쪽/돌아오기) — 순환+이동

> 인준 base(`home_vocab/injun_base.png`) 키프레임에서 신규 생성. ★남학생답게 씩씩·침착 표정.

---

# 씬별 시나리오 (47씬)

> 표기: **[씬] 자막(KO) | 화면글자 | 나레이션(KO) → (EN) | 배경 | 인준 동작·표정(2~3) | 태그**

## 1막 — 도입: 이태원 (S0–S6)

- **S0** (무나레이션·추천카드) | (없음) | [정적 10초] | `station` | (정지) | 카드
- **S1** 이태원에 잘 오셨어요! | `이태원` | "안녕하세요, 여러분! 여기는 세계 각국의 문화가 모인 서울 '이태원'이에요. 오늘은 함께 거리를 걸으며, 갑작스러운 돌발 상황에 한국어로 대처하는 법을 배워 봐요!" → (Hi, everyone! This is Seoul's '이태원' (Itaewon), where cultures from around the world meet. Today, let's walk the streets together and learn to handle sudden emergencies in Korean!) | `station` | walk_r→wave→smile_bright | 인사
- **S2** 갑자기 이런 일이? | `돌발 상황` | "여행 중엔 갑자기 몸이 아프거나, 소중한 물건을 잃어버릴 수 있어요. 그럴 때 당황하지 않는 법, 궁금하지 않으세요?" → (While traveling, you might suddenly feel sick or lose something precious. Curious how to stay calm?) | `station` | surprised→curious | 동기
- **S3** 오늘의 주제 | `돌발 상황 · 도움 요청` | "오늘 주제는 '돌발 상황' (emergencies)에 대처하고 '도움' (help)을 청하는 법이에요. 몇 마디만 알면 위급할 때 큰 힘이 돼요." → (Today's theme: handling '돌발 상황' (emergencies) and asking for '도움' (help). A few phrases go a long way in a crisis.) | `food_street` | greet_both→explain_open | 예고
- **S4** 침착하게 한 걸음씩 | `침착하게` | "가장 중요한 건 '침착함'이에요. 이 북적이는 거리에서도, 천천히 한 마디씩 익혀 봐요." → (The most important thing is staying '침착' (calm). Even on this busy street, let's learn one phrase at a time.) | `food_street` | walk_r→calm | 분위기
- **S5** 도움은 부끄럽지 않아요 | `도와주세요` | "기억할 것 하나. 위급할 땐 주변에 '도와주세요'라고 말하는 걸 부끄러워하지 마세요. 한국 사람들은 기꺼이 도와줘요." → (Remember: never be shy to say '도와주세요' (help me) in an emergency. Koreans are glad to help.) | `rooftop` | present_right→reassure | 핵심예고
- **S6** 시작해요! | `시작해요` | "자, 이 활기찬 이태원 거리에서 오늘 수업을 시작해요. 다들 준비됐나요?" → (Now, let's begin today's lesson on the lively streets of Itaewon. Ready?) | `rooftop` | excited→greet_both | 전환

## 2막 — 응급 어휘 (S7–S16)

- **S7** 아프다 | `아프다 (to be sick/hurt)` | "몸이 안 좋을 때 쓰는 말이에요. '아프다'. '배가 아파요', '머리가 아파요'처럼 아픈 곳을 앞에 붙여요. '아프다'는 상태를 나타내는 '형용사'예요." → (When you feel unwell: '아프다' (to be sick/hurt). Say '배가 아파요' (my stomach hurts). '아프다' is a descriptive adjective.) | `antique_street` | hurt→explain | 어휘1·품사
- **S8** 다치다 | `다치다 (to get hurt)` | "넘어지거나 부딪쳐 몸을 상했을 땐 '다치다'예요. '넘어져서 다쳤어요.' 이렇게 말해요." → (If you fall or bump into something: '다치다' (to get injured). '넘어져서 다쳤어요' — I fell and got hurt.) | `antique_street` | surprised→point_self | 어휘2
- **S9** 약국 | `약국 (pharmacy)` | "가벼운 증상엔 '약국'을 찾아요. 초록색 십자 표시가 있는 곳이에요. '약국이 어디예요?'라고 물으면 돼요." → (For mild symptoms, find a '약국' (pharmacy) — look for the green cross. Ask '약국이 어디예요?' (Where's a pharmacy?).) | `pharmacy` | point_right→look_view | 어휘3
- **S10** 약 주세요 | `약 주세요` | "약국에선 '감기약 주세요', '두통약 주세요'처럼 말해요. '-약 주세요' 한마디면 충분해요." → (At the pharmacy: '감기약 주세요' (cold medicine, please). Just '-약 주세요' is enough.) | `pharmacy` | present_right→smile_bright | 활용3
- **S11** 병원 | `병원 (hospital/clinic)` | "많이 아프거나 다치면 '병원'에 가요. '병원에 가고 싶어요'라고 하면 주변에서 길을 알려줄 거예요." → (If it's serious, go to a '병원' (hospital/clinic). Say '병원에 가고 싶어요' (I want to go to a hospital).) | `clinic` | explain→point_up | 어휘4
- **S12** 괜찮으세요? | `괜찮으세요?` | "누가 아파 보이면 '괜찮으세요?'라고 물어요. 상대를 살피는 따뜻한 한마디예요." → (See someone unwell? Ask '괜찮으세요?' (Are you okay?) — a kind, caring phrase.) | `clinic` | reassure→nod_agree | 활용4
- **S13** 119 | `119 (구급·소방)` | "불이 나거나 크게 다쳐 구급차가 필요할 땐 '119'예요. '119죠? 도와주세요!'라고 전화해요." → (For fire or an ambulance, call '119'. Say '119죠? 도와주세요!' (Is this 119? Please help!).) | `police_box` | phone→point_up | 어휘5
- **S14** 112 | `112 (경찰)` | "도둑을 만나거나 위험한 일엔 '112', 경찰이에요. '112'와 '119'는 24시간, 요금도 없어요." → (For crime or danger, call '112' (police). Both '112' and '119' are free, 24 hours.) | `police_box` | phone→explain | 어휘6
- **S15** 잃어버리다 | `잃어버리다 (to lose)` | "물건이 사라졌을 땐 '잃어버리다'예요. '잃어버리다'는 동작을 나타내는 '동사'고, 뒤에서 배울 오늘의 핵심 표현이에요." → (When something's gone: '잃어버리다' (to lose) — a verb, and today's key expression.) | `convenience` | search_pockets→think | 어휘7·품사
- **S16** 도와주세요 | `도와주세요 (please help me)` | "가장 든든한 한마디. '도와주세요.' '돕다'에 '-아 주세요'를 붙인, 아주 정중한 요청이에요." → (The most reassuring phrase: '도와주세요' (please help me) — a polite request from '돕다' (to help).) | `convenience` | help_gesture→reassure | 어휘8·품사

## 3막 — 핵심 문형 "___을 잃어버렸어요 / 도와주세요" (S17–S28)

- **S17** ___을 잃어버렸어요 | `___을/를 잃어버렸어요` | "오늘의 핵심 문형이에요. 무언가 잃어버렸을 땐 '___을 잃어버렸어요.' 잃어버린 물건을 앞에 쏙 넣어요." → (Today's core pattern: '___을 잃어버렸어요' (I lost ___). Put the lost item in the blank.) | `alley` | explain_open→point_up | 개념
- **S18** 지갑을 잃어버렸어요 | `지갑을 잃어버렸어요` | "'지갑을 잃어버렸어요.' '여권을 잃어버렸어요.' '휴대폰을 잃어버렸어요.' 물건만 바꾸면 다 돼요." → ('지갑을 잃어버렸어요' (I lost my wallet). Swap the item: 여권 (passport), 휴대폰 (phone).) | `alley` | search_pockets→explain | 예문1
- **S19** 도와주세요, ~ | `도와주세요, ~` | "앞에 '도와주세요'를 붙이면 더 간절하게 들려요. '도와주세요, 가방을 잃어버렸어요!'" → (Add '도와주세요' up front for urgency: '도와주세요, 가방을 잃어버렸어요!' (Help! I lost my bag!).) | `mosque_road` | help_gesture→worried | 예문2
- **S20** 어디에서 잃어버렸어요? | `어디에서 ~?` | "도와주는 사람이 이렇게 물을 거예요. '어디에서 잃어버렸어요?' 그럼 '식당에서요', '지하철에서요'처럼 답해요." → (They'll ask '어디에서 잃어버렸어요?' (Where did you lose it?). Answer '지하철에서요' (on the subway).) | `mosque_road` | curious→present_right | 활용
- **S21** 아파요 / 다쳤어요 | `아파요 · 다쳤어요` | "몸이 안 좋을 땐 '배가 아파요', 다쳤을 땐 '다리를 다쳤어요.' 아픈 곳을 콕 집어 말해요." → ('배가 아파요' (my stomach hurts), '다리를 다쳤어요' (I hurt my leg). Point to where it hurts.) | `gyeongridan` | hurt→point_self | 예문3
- **S22** 구체적으로 말해요 | `구체적으로` | "도움을 청할 땐 구체적으로! '그냥 아파요'보다 '어제부터 열이 나요'처럼 또렷할수록 빨리 도와줄 수 있어요." → (Be specific: '어제부터 열이 나요' (I've had a fever since yesterday) beats a vague 'I'm sick.') | `gyeongridan` | explain→finger_up | 팁
- **S23** 도움을 청하며 걸어요 | `실례합니다, 도와주세요` | "이렇게 말하며 도움을 청해요. '실례합니다, 도와주세요. 여권을 잃어버렸어요.'" → ('실례합니다, 도와주세요. 여권을 잃어버렸어요.' (Excuse me, please help. I lost my passport.).) | `crosswalk` | walk_r→help_gesture | 예문4
- **S24** 감사 인사도 잊지 마요 | `고맙습니다` | "도움을 받았으면 '고맙습니다', '정말 감사합니다'로 마음을 전해요. 작은 인사가 큰 고마움이 돼요." → (After help, say '고맙습니다' (thank you). A small thanks means a lot.) | `crosswalk` | bow→smile_bright | 예의
- **S25** 표정·손짓도 함께 | `침착하게` | "위급할수록 표정과 손짓이 도움이 돼요. 아픈 곳을 가리키고, 침착한 얼굴로 또박또박 말해요." → (Gestures help: point to where it hurts, and speak clearly with a calm face.) | `plaza` | point_self→calm | 팁
- **S26** 따라 말해 봐요 | `잃어버렸어요 · 도와주세요` | "저를 따라 소리 내어 말해 봐요. '___을 잃어버렸어요. 도와주세요.' 이 두 문장이면 어디서든 도움을 받아요!" → (Say it after me: '___을 잃어버렸어요. 도와주세요.' Two sentences to get help anywhere!) | `plaza` | present_right→determined | 청취·활용
- **S27** 정중하게 부탁해요 | `실례합니다 · -요` | "부탁은 정중하게. '실례합니다'로 시작하고 '-요'로 맺으면, 처음 본 사람도 기꺼이 도와줘요." → (Be polite: start with '실례합니다' (excuse me), end with '-요'. Even strangers will gladly help.) | `subway_inside` | bow→explain | 주의
- **S28** 문형 정리 | `___을 잃어버렸어요 · 도와주세요` | "정리! '___을 잃어버렸어요. 도와주세요.' 그리고 '배가 아파요', '다쳤어요.' 이 표현이면 돌발 상황도 문제없어요!" → (In sum: '___을 잃어버렸어요. 도와주세요.' plus '아파요', '다쳤어요' — you're ready for emergencies!) | `subway_inside` | weigh→proud | 정리

## 4막 — 긴급 통화 듣기 · 핵심 잡기 (S29–S38)

- **S29** 신고 전화를 들어 봐요 | `무슨 일 · 어디` | "이제 긴급 통화를 들어 봐요. 신고할 땐 '무슨 일'이 '어디에서' 일어났는지, 이 두 가지가 핵심이에요." → (Now, listen to an emergency call. Two keys: what happened and where.) | `lost_center` | think→point_up | 개념
- **S30** 무슨 일이에요? | `무슨 일이에요?` | "전화를 받으면 이렇게 물어요. '무슨 일이에요?' 그럼 침착하게 상황을 말하면 돼요." → (They'll ask '무슨 일이에요?' (What happened?). Just explain calmly.) | `lost_center` | curious→present_right | 문형
- **S31** 119 통화 | `다쳤어요 · 여기는 ~` | "'119죠? 친구가 넘어져서 다쳤어요. 여기는 이태원이에요.' 다친 일과 위치를 함께 말해요." → ('119죠? 친구가 다쳤어요. 여기는 이태원이에요.' (Is this 119? My friend is hurt. We're in Itaewon.).) | `hospital_er` | phone→worried | 듣기1
- **S32** 112 통화 | `잃어버렸어요 · 도와주세요` | "'112죠? 지하철에서 가방을 잃어버렸어요. 도와주세요.' 잃어버린 물건과 장소를 또렷하게요." → ('112죠? 가방을 잃어버렸어요. 도와주세요.' (Is this 112? I lost my bag. Please help.).) | `hospital_er` | phone→explain | 듣기2
- **S33** 핵심만 메모하듯 | `무슨 일 · 어디` | "통화를 들을 땐 '무슨 일 = 다침, 어디 = 이태원'처럼 핵심만 콕콕 잡으세요. 한눈에 들어오죠." → (Catch just the core: 'what = injury, where = Itaewon.') | `street_night` | think→weigh | 청취법
- **S34** 천천히 또박또박 | `천천히 다시 말할게요` | "급해도 천천히요! 상대가 못 알아들으면 '천천히 다시 말할게요'라고 해요. 정확한 게 결국 빠른 거예요." → (Even in a rush, go slow: '천천히 다시 말할게요' (Let me say it again slowly). Clear is fast.) | `street_night` | calm→reassure | 팁
- **S35** 다시 물어봐도 돼요 | `다시 말해 주세요` | "못 들었으면 '다시 말해 주세요'라고 해요. 부끄러운 게 아니에요. 정확히 아는 게 더 중요하니까요." → (If you miss it: '다시 말해 주세요' (Please say it again). No shame — accuracy matters.) | `bus_stop` | curious→point_self | 질문
- **S36** 위치를 알려요 | `여기는 ~ 근처예요` | "위치는 '여기는 이태원역 근처예요'처럼 알려요. 주변 큰 건물이나 역 이름을 대면 금방 찾아와요." → ('여기는 이태원역 근처예요' (I'm near Itaewon Station). Name a landmark or station.) | `bus_stop` | point_right→explain | 활용
- **S37** 함께 가 달라고 해요 | `같이 가 주세요` | "혼자 무섭다면 '같이 가 주세요'라고 부탁해도 돼요. 카페 직원이나 주변 사람에게요." → (If you're scared alone: '같이 가 주세요' (Please come with me). Ask a café worker or a passerby.) | `cafe_inside` | help_gesture→reassure | 역할
- **S38** 통화 정리 | `무슨 일 · 어디 · 침착` | "정리! 신고는 '무슨 일'과 '어디'를 침착하게. 이 두 가지만 또렷하면 도움이 금방 와요." → (In sum: report 'what' and 'where', calmly. Help comes fast.) | `cafe_inside` | weigh→confident | 정리

## 5막 — 도움 요청 역할극 · 대처 문화 · 마무리 (S39–S46)

- **S39** 역할극 해 볼까요 | `약국 · 병원 · 분실` | "이제 역할극이에요. 약국, 병원, 분실 상황에서 오늘 배운 표현을 직접 써 봐요." → (Now a roleplay: use today's phrases at a pharmacy, a clinic, and a lost-item desk.) | `fire_station` | present_right→smile_bright | 개념
- **S40** 약국에서 | `배가 아파요, 약 주세요` | "약국에서. '안녕하세요, 배가 아파요. 소화제 주세요.' 증상을 말하고 약을 청하면 돼요." → ('배가 아파요. 소화제 주세요.' (My stomach hurts. Digestive medicine, please.).) | `fire_station` | hurt→present_right | 역할극1
- **S41** 유실물 센터에서 | `가방을 잃어버렸어요` | "유실물 센터에서. '실례합니다, 지하철에서 가방을 잃어버렸어요. 도와주세요.' 물건과 장소를 함께요." → ('가방을 잃어버렸어요. 도와주세요.' (I lost my bag. Please help.).) | `noksapyeong` | search_pockets→help_gesture | 역할극2
- **S42** 서로 돕는 한국 문화 | `침착 · 서로 도움` | "한국에선 위급할 때 서로 돕는 걸 당연하게 여겨요. 낯선 사람도 기꺼이 119를 대신 불러 주기도 해요." → (In Korea, helping in a crisis is natural — a stranger will even call 119 for you.) | `noksapyeong` | reassure→greet_both | 문화1
- **S43** 다국어 도움도 있어요 | `도움을 받을 수 있어요` | "외국인도 걱정 마요. '112'와 '119'는 통역 도움을 받을 수 있고, 관광 안내소에서도 도와줘요." → (Foreigners, don't worry: '112' and '119' offer interpreter help, and tourist centers assist too.) | `info_center` | explain→thumbs_up | 문화2
- **S44** 이태원에서 한마디 | `해결했어요!` | "자, 오늘 배운 표현으로 상황을 해결했어요! '도와주세요' 한마디가 이렇게 큰 힘이 되네요." → (We solved it with today's phrases! '도와주세요' really is powerful.) | `info_center` | cheer→proud | 성취
- **S45** 오늘의 정리 | `아프다 · 잃어버렸어요 · 도와주세요 · 112·119` | "오늘 우리는 '아프다·다치다·잃어버리다'를 배우고, '___을 잃어버렸어요'와 '도와주세요'로 도움을 청하고, '112·119' 신고까지 익혔어요." → (Today we learned '아프다·다치다·잃어버리다', asked for help with '___을 잃어버렸어요' and '도와주세요', and practiced calling '112·119'.) | `sunset_hill` | explain_open→present_right | 총정리
- **S46** 다음에 또 만나요 | `구독 · 좋아요` | "여러분은 어떤 돌발 상황을 겪어 봤나요? 댓글로 들려주세요. 이태원에서 배운 든든한 한국어, 다음에 또 함께해요! 구독과 좋아요 잊지 마시고요!" → (What emergencies have you faced? Tell us in the comments. Let's meet again for helpful Korean — and don't forget to subscribe and like!) | `sunset_hill` | wave→greet_both→cheer | 마무리·엔드카드

---

## 제작 메모 (다음 단계)
- **걷기(컷랑)**: `injun_w20_walk_{r,l}_0..7` 신규 제작 — 인준 측면 걷기영상 Flow 생성 → `cutrang.py dump/build`로 8투명컷+리버스, 키통일. 거리 이동 씬(S1·S4·S23)에 순환+이동. [[action-cutout-animation-engine]]
- **포즈 신규 생성**: 위 30종을 `injun_base` 키프레임에서 agy 4병렬 생성(투명컷·오른쪽 향함)·cutout·정규화·register. ★응급/도움 표정(worried·hurt·help_gesture·phone·calm·reassure)이 이 회차 핵심.
- **배경 23종**: 이태원 구석구석 agy 직접생성(연속 장면·왼편 복잡하지 않게·글자/숫자/상표 없음) → 뷰어 확인.
- **자막·음성 표준(항상 동일)**: `'한글'[발음](뜻)`·품사·번인금지 소프트·선희/Emma·1.1배속·KO자막도 발음기호·es-419/zh-Hans. add_pron.
- **좌상단 텍스트박스**: build_w20가 cap="" + 박스PNG static(코랄).
- **캐릭터 게이트**: 렌더 전 `check_char_fit.py KO-W20`.
- **★범위 준수**: 응급·도움요청·112·119 안에서만. 호칭/인물묘사(W21)·여행계획(W22) 등 다음 주 내용 절대 금지.
