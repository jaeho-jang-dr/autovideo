# W19 시나리오 — 논리적 의견과 설득하기 (지은 · 설악산)

> **주제:** 의견 표현 어휘(제 생각에는·왜냐하면·동의하다·반대하다) + 핵심 문형 **"저는 ___다고 생각해요, 왜냐하면 ___"**(주장+근거) + 근거 잇기(따라서) + 찬반 토론 듣기 + 설득·정중히 반대하기 + 한국의 토론 문화
> **범위 고정:** 웹 훈민정음 19주차 2분 핵심영상(`hangeul_w19_stickman`)을 기준으로 의견·설득 바운더리 안에서 확장. 타깃 = `~고 생각해요/왜냐하면/따라서`, 어휘 = 제 생각에는·왜냐하면·동의/반대, 문화 = 근거 들어 정중히.
> **캐릭터:** 지은(여, 어린 대학생) — 락 = `home_vocab/w15/jieun_hiking_base.png` (긴 갈색 웨이브·빨강검정 등산재킷·검정 배낭·회색 등산바지·갈색 등산화·플랫 카툰). **★어린 학생답게 표정이 아주 다양**(신남·활짝웃음·궁금·자신만만·뿌듯·깨달음·갸우뚱 등).
> **배경:** **설악산** — ★**2씬당 1개, 총 23종**으로 설악산 구석구석(입구·신흥사·흔들바위·울산바위·케이블카·비룡폭포·천불동·공룡능선·대청봉·운해·노을…).
> **길이:** 47씬(S0–S46) ≈ 8분
> **★걷기:** 이미 완성된 **Veo 투명컷 16(오른쪽8+돌아오기8, `jieun_w19_walk_{r,l}_0..7`)** 사용 — 순환+이동으로 등산로 이동컷. [[character-walk-veo-cutout-method]]
> **★자막 원칙(항상 동일·3단계):**
>   - **단어** = `'한글' [발음기호] (뜻)` — 예: `'왜냐하면' [wae-nya-ha-myeon] (because)`
>   - **짧은 문장** = `'한글' [발음기호] (뜻)` — 예: `'저도 그렇게 생각해요' [jeo-do geu-reo-ke saeng-ga-kae-yo] (I think so too)`
>   - **긴 문장** = `한글 (영어뜻)` — 발음기호 없이 **영어뜻만**
>   - 따옴표 한글=선희 발음, `add_pron`이 [로마자] 자막 자동. **번인 금지·소프트 자막**. es-419/zh-Hans.
> **품사 짚기(표준):** "'생각하다'는 **동사**", "'왜냐하면'은 이유 잇는 **접속부사**", "'-다고'는 **간접인용**" 짧게.
> **★나레이터/성우(두 번 렌더 방지):**
>   - **DB 선희(따옴표 한글 발음)** = **처음부터 Azure TTS 선희**(`ko-KR-SunHiNeural`) — 초안·최종 재사용, 재생성 안 함.
>   - **영어 나레이션 = Emma**(`en-US-EmmaMultilingualNeural`): EN 초안=edge-tts → 최종만 Azure.
>   - **KO 러닝 나레이션 = 선희**: KO 최종=Azure.
>   - **★렌더 순서: 영어판 먼저** 렌더 → 교정앱 → 확정 시 KO + Azure 최종.
>   - 1.1배속·딜레이0. [[tts-narration-tier-policy]] [[tts-cache-engine-trap]]
> **좌상단 텍스트박스:** 화면글자=좌상단 코랄 박스(build_w19가 cap 비우고 박스PNG static). [[project-w18-emotion]] 방식.

---

## 배경 23종 (불투명, `w19/backgrounds/`, 1280×720, 2씬당 1개 · 설악산 구석구석)

| # | key | 장소 | 씬 |
|---|-----|------|----|
| 1 | `entrance` | 설악산 입구 일주문·단풍 전경 | S1–2 |
| 2 | `sinheungsa` | 신흥사 절·통일대불(큰 청동불상) | S3–4 |
| 3 | `trail_low` | 단풍 물든 초입 돌계단 등산로 | S5–6 |
| 4 | `heundeul` | 계조암 흔들바위(둥근 큰 바위) | S7–8 |
| 5 | `ulsan` | 울산바위 거대 화강암 암봉 전망 | S9–10 |
| 6 | `cable_station` | 권금성 케이블카 탑승장 | S11–12 |
| 7 | `cable_view` | 케이블카에서 내려다본 단풍 능선 | S13–14 |
| 8 | `gwongeumseong` | 권금성 옛 성터·사방 전망 | S15–16 |
| 9 | `biryong` | 비룡폭포(가는 물줄기)·계곡 | S17–18 |
| 10 | `towang` | 토왕성폭포 원경 전망대 | S19–20 |
| 11 | `cheonbuldong` | 천불동 계곡 단풍·기암 | S21–22 |
| 12 | `bridge` | 계곡 위 구름다리(현수교) | S23–24 |
| 13 | `maple_tunnel` | 단풍 터널 숲길(양옆 붉은 단풍) | S25–26 |
| 14 | `rock_ridge` | 기암괴석 늘어선 능선길 | S27–28 |
| 15 | `gongryong` | 공룡능선 파노라마(뾰족 봉우리 줄) | S29–30 |
| 16 | `madeungnyeong` | 마등령 갈림길 이정표(글자 없는 나무기둥) | S31–32 |
| 17 | `shelter` | 중청·소청 대피소(산장) | S33–34 |
| 18 | `final_ridge` | 대청봉 오르는 마지막 관목 능선 | S35–36 |
| 19 | `summit` | 대청봉 정상 바위·탁 트인 하늘 | S37–38 |
| 20 | `unhae` | 정상에서 본 운해(구름바다) | S39–40 |
| 21 | `descent` | 하산길 붉은 단풍 사면 | S41–42 |
| 22 | `osaek` | 오색 단풍 계곡·약수터 | S43–44 |
| 23 | `sunset` | 능선에 노을 진 단풍 | S45–46 |

> 배경 규칙(★W18 교훈): 하나의 연속 장면으로 전체를 꽉 채움. 왼편(지은 자리)은 풍경이 복잡하지 않게(연속 유지, 흰칸·seam 금지). 글자·숫자·상표 금지. [[lesson-render-review-rules]]

## 포즈 30종 (투명 컷아웃, `assets/graphics/poses/jieun_w19_<key>.png`, hiking 락 · 오른쪽 향함) + 걷기 16컷

- **인사/기본:** `wave`·`greet_both`·`bow`
- **설명/제시:** `explain`·`explain_open`·`present_right`·`point_right`·`point_self`·`point_up`
- **의견/주장:** `raise_hand`(손 들어 의견)·`finger_up`(검지 강조=왜냐하면)·`think`(턱에 손)·`weigh`(양손 저울=찬반)·`confident`(양손 허리·자신만만)
- **동의/반대:** `nod_agree`(밝게 끄덕)·`shake_no`(손사래)·`persuade`(두 손 앞 설득)·`tilt_puzzled`(고개 갸우뚱·궁금)
- **★다양한 표정(어린 학생):** `smile_bright`(환한 미소)·`laugh_big`(활짝 웃음)·`excited`(신나서 폴짝)·`surprised`(놀람)·`aha`(깨달음! 검지 번쩍+눈 크게)·`proud`(뿌듯·가슴에 손)·`curious`(궁금·몸 기울여 봄)·`sparkle`(눈 반짝 감탄)·`pout`(살짝 삐침)·`determined`(파이팅·주먹 불끈)·`clap`·`cheer`·`thumbs_up`(엄지척)
- **설악산 동작:** `climb`(등산 오르기)·`look_view`(손차양 전망 감탄)
- **걷기(완성됨):** `walk_r_0..7`(오른쪽) · `walk_l_0..7`(왼쪽/돌아오기) — 순환+이동

> 기존 hiking 3컷(base·climb·point_up) 재사용, 나머지는 `jieun_hiking_base` 키프레임에서 신규 생성.

---

# 씬별 시나리오 (47씬)

> 표기: **[씬] 자막(KO) | 화면글자 | 나레이션(KO) → (EN) | 배경 | 지은 동작·표정(2~3) | 태그**

## 1막 — 도입: 설악산 (S0–S6)

- **S0** (무나레이션·추천카드) | (없음) | [정적 10초] | `entrance` | (정지) | 카드
- **S1** 설악산에 오신 걸 환영해요! | `설악산` | "안녕하세요, 여러분! 여기는 단풍으로 붉게 물든 '설악산'이에요. 오늘은 저 지은이와 함께 산을 오르며 한국어를 배워 봐요!" → (Hi, everyone! This is '설악산' (Seoraksan), ablaze with red autumn leaves. Today, let's climb with me, Jieun, and learn Korean!) | `entrance` | walk_r→wave→smile_bright | 인사
- **S2** 내 생각을 말해요 | `의견 · 근거` | "산에 오르면 이런저런 생각이 떠올라요. 그 생각을 조리 있게 말하는 법, 궁금하지 않으세요?" → (Climbing a mountain stirs up all kinds of thoughts. Curious how to say them clearly?) | `sinheungsa` | curious→point_self | 동기
- **S3** 오늘의 주제 | `의견 말하기 · 설득` | "오늘 주제는 '의견 표현' (expressing opinions)과 '설득' (persuasion)이에요. 주장과 근거를 함께 말하면 한국어가 훨씬 논리적으로 들려요." → (Today's theme is '의견 표현' (expressing opinions) and '설득' (persuasion). Pairing a claim with a reason makes your Korean sound far more logical.) | `sinheungsa` | greet_both→explain_open | 예고
- **S4** 단풍길을 오르며 | `천천히, 조리 있게` | "붉은 단풍길을 한 걸음씩 오르며 공부해 봐요. 생각을 정리하듯 차근차근요." → (Let's study climbing the red-leaf trail step by step, organizing our thoughts as we go.) | `trail_low` | walk_r→look_view | 분위기
- **S5** 의견엔 근거가 필요해요 | `주장 + 근거` | "기억할 것 하나. 좋은 의견에는 반드시 '근거' (reason)가 따라와야 해요. '왜 그런지'가 있어야 설득력이 생기거든요." → (Remember: a good opinion needs a '근거' (reason). The 'why' makes it persuasive.) | `trail_low` | finger_up→explain | 핵심예고
- **S6** 수업 시작! | `시작해요` | "자, 이 시원한 단풍길에서 오늘 수업을 시작해요. 다들 준비됐나요?" → (Now, let's begin today's lesson on this crisp autumn trail. Ready?) | `trail_low` | excited→greet_both | 전환

## 2막 — 의견 표현 어휘 (S7–S16)

- **S7** 제 생각에는 | `제 생각에는 (in my opinion)` | "의견을 꺼낼 때 가장 자주 쓰는 말이에요. '제 생각에는'. 이 말로 시작하면 '지금부터 내 의견이에요'라는 신호가 돼요." → (The most common opener: '제 생각에는' (in my opinion). It signals 'here comes my view.') | `heundeul` | present_right→point_self | 어휘1
- **S8** 이렇게 써 봐요 | `제 생각에는 ~` | "'제 생각에는, 설악산이 한국에서 가장 아름다워요.' 앞에 붙이기만 하면 정중한 의견이 돼요." → ('제 생각에는, 설악산이 한국에서 가장 아름다워요' — In my opinion, Seoraksan is the most beautiful in Korea.) | `heundeul` | sparkle→look_view | 활용1
- **S9** 저는 ~다고 생각해요 | `저는 ~다고 생각해요 (I think ~)` | "또렷하게 주장할 땐 '저는 ~다고 생각해요'예요. 여기 '생각하다'는 마음속 판단을 나타내는 '동사'예요." → (To state a claim clearly, use '저는 ~다고 생각해요' (I think ~). '생각하다' (to think) is a verb.) | `ulsan` | confident→explain | 어휘2·품사
- **S10** 저 큰 바위 좀 봐요! | `울산바위` | "저는 저 '울산바위' (Ulsanbawi)가 정말 웅장하다고 생각해요! 어때요, 감탄이 절로 나오죠?" → (I think '울산바위' (Ulsanbawi) over there is truly majestic! It takes your breath away, right?) | `ulsan` | surprised→point_up | 활용2
- **S11** 동의하다 | `동의하다 (to agree)` | "상대 말에 찬성할 땐 '동의하다'예요. '저도 그렇게 생각해요', '동의해요'라고 하면 부드럽게 맞장구가 돼요." → (To agree, use '동의하다'. '저도 그렇게 생각해요' or '동의해요'.) | `cable_station` | nod_agree→smile_bright | 어휘3
- **S12** 반대하다 | `반대하다 (to disagree)` | "생각이 다를 땐 '반대하다'를 써요. 무작정 반대가 아니라 이유를 붙여 정중히 말하는 게 한국식이에요." → (When you differ, use '반대하다'. The Korean way: add a reason and stay polite.) | `cable_station` | shake_no→explain | 어휘4
- **S13** 정중한 반대 | `그렇지만 저는 ~` | "예를 들어 '좋은 말씀이에요. 그렇지만 저는 조금 다르게 생각해요.' 상대를 먼저 존중하면 기분이 안 상해요." → ('Good point. But I see it a bit differently.' Respecting the other first keeps it pleasant.) | `cable_view` | tilt_puzzled→persuade | 활용4
- **S14** 왜냐하면 | `왜냐하면 (because)` | "가장 중요한 말이에요. '왜냐하면'. 이유를 이어 주는 '접속부사'로, 주장 뒤에 근거를 붙일 때 써요." → (The key word: '왜냐하면' (because), a conjunctive adverb that attaches a reason.) | `cable_view` | aha→finger_up | 어휘5·품사
- **S15** 왜냐하면 ~기 때문이에요 | `왜냐하면 ~기 때문이에요` | "'왜냐하면, 공기가 맑기 때문이에요.' 이렇게 이유를 또렷하게 밝힐 수 있어요." → ('왜냐하면, 공기가 맑기 때문이에요' — because the air is clean.) | `gwongeumseong` | explain→look_view | 활용5
- **S16** 따라서 | `따라서 (therefore)` | "근거에서 결론으로 넘어갈 땐 '따라서'나 '그래서'를 써요. '따라서, 저는 등산을 추천해요.'처럼요." → (To move from reason to conclusion, use '따라서' (therefore).) | `gwongeumseong` | present_right→thumbs_up | 어휘6

## 3막 — 핵심 문형 "저는 ___다고 생각해요, 왜냐하면 ___" (S17–S28)

- **S17** 주장 + 근거 한 문장 | `주장 + 왜냐하면 + 근거` | "오늘의 핵심 문형이에요. 주장과 근거를 한 문장에! '저는 ___다고 생각해요, 왜냐하면 ___.'" → (Today's core pattern — claim and reason in one: '저는 ___다고 생각해요, 왜냐하면 ___.') | `biryong` | explain_open→finger_up | 개념
- **S18** -다고 생각해요 | `-다고 (간접인용)` | "여기 '-다고'는 생각이나 말을 옮겨 담는 '간접인용'이에요. '예쁘다'는 '예쁘다고', '좋다'는 '좋다고'처럼 바꿔요." → ('-다고' is indirect quotation: '예쁘다' becomes '예쁘다고', '좋다' becomes '좋다고'.) | `biryong` | think→explain | 규칙·품사
- **S19** 예문 하나 | `설악산이 아름답다고 생각해요` | "'저는 설악산이 아름답다고 생각해요, 왜냐하면 단풍이 정말 곱기 때문이에요.' 주장 뒤에 이유가 착 붙었죠." → (I think Seoraksan is beautiful, because the leaves are truly lovely.) | `towang` | present_right→sparkle | 예문1
- **S20** 왜? 가 보여요 | `주장 ← 근거` | "들었나요? '왜 그렇게 생각하는지'가 한 문장에 다 있어요. 이러면 듣는 사람이 고개를 끄덕여요." → (Hear it? The 'why' sits inside the sentence, and the listener nods along.) | `towang` | nod_agree→persuade | 설명1
- **S21** 예문 둘 | `케이블카가 편하다고 생각해요` | "'저는 케이블카가 편하다고 생각해요, 왜냐하면 힘을 아낄 수 있기 때문이에요.' 생활 속 의견도 척척!" → (I think the cable car is convenient, because it saves energy.) | `cheonbuldong` | point_up→explain | 예문2
- **S22** 근거는 구체적으로 | `구체적인 이유` | "근거는 두루뭉술하지 않게 구체적으로! '좋으니까'보다 '경치가 탁 트여서'처럼 또렷할수록 설득력이 커져요." → (Make reasons specific: 'the view opens up wide' beats just 'because it's nice.') | `cheonbuldong` | confident→finger_up | 팁
- **S23** 예문 셋 | `걷는 게 좋다고 생각해요` | "반대 의견도 같은 틀로. '저는 걷는 게 더 좋다고 생각해요, 왜냐하면 단풍을 천천히 볼 수 있기 때문이에요.'" → (I think walking is better, because you can enjoy the leaves slowly.) | `bridge` | walk_r→persuade | 예문3
- **S24** 따라서 결론 | `따라서 ~` | "근거를 말했으면 '따라서'로 맺어요. '따라서 저는 걸어서 오르기로 했어요.' 결론까지 있으면 완성!" → (After reasons, close with '따라서': 'Therefore, I decided to hike up.') | `bridge` | present_right→cheer | 예문3-결론
- **S25** 표정·손짓도 함께 | `자연스럽게` | "의견을 말할 땐 표정과 손짓도 함께예요. 확신엔 밝은 얼굴로, 이유엔 손가락을 세워서요." → (Let expression and gesture join your words — a bright face for conviction, a raised finger for the reason.) | `maple_tunnel` | laugh_big→finger_up | 팁
- **S26** 따라 말해 봐요 | `주장 + 왜냐하면 + 따라서` | "저를 따라 소리 내어 말해 봐요. '저는 ~다고 생각해요, 왜냐하면 ~, 따라서 ~.' 세 박자를 익히면 술술!" → (Say it after me: 'I think ~, because ~, therefore ~.') | `maple_tunnel` | present_right→determined | 청취·활용
- **S27** 존댓말로 정중하게 | `-요 · -습니다` | "의견은 특히 정중하게. 끝을 '-요'나 '-습니다'로 맺으면 강한 주장도 부드럽게 들려요." → (Keep opinions polite. Ending with '-요' or '-습니다' softens even a strong claim.) | `rock_ridge` | bow→explain | 주의
- **S28** 문형 정리 | `저는 ~다고 생각해요, 왜냐하면 ~` | "정리! '저는 ~다고 생각해요, 왜냐하면 ~.' 이 한 문형이면 주장·근거·설득이 한 번에!" → (In sum: 'I think ~, because ~.' One pattern for claim, reason, and persuasion.) | `rock_ridge` | weigh→proud | 정리

## 4막 — 찬반 토론 듣기 · 근거 잡기 (S29–S38)

- **S29** 짧은 토론 | `찬성 ↔ 반대` | "이제 짧은 토론을 들어 봐요. 한 주제에 '찬성'과 '반대'가 오갈 때, 양쪽 근거를 잡아내는 게 핵심이에요." → (Now a short debate. When '찬성' (for) and '반대' (against) go back and forth, catch each side's reasons.) | `gongryong` | weigh→think | 개념
- **S30** 주제 정하기 | `케이블카 vs 등산` | "오늘 토론 주제는 '설악산을 케이블카로 오를까, 걸어서 오를까'예요. 가볍고 재미있죠?" → (Today's topic: 'Cable car up Seoraksan, or hike?' Light and fun, right?) | `gongryong` | present_right→smile_bright | 주제
- **S31** 찬성 의견 | `찬성: 케이블카` | "먼저 찬성. '저는 케이블카가 좋다고 생각해요, 왜냐하면 시간을 아끼고 경치도 볼 수 있기 때문이에요.' 근거가 두 개!" → (In favor: 'I think the cable car is good, because it saves time and you can enjoy the view.' Two reasons!) | `madeungnyeong` | point_up→persuade | 찬성
- **S32** 반대 의견 | `반대: 걷기` | "이번엔 반대. '저는 걸어야 한다고 생각해요, 왜냐하면 단풍을 가까이서 느낄 수 있기 때문이에요.'" → (Against: 'I think we should walk, because you feel the leaves up close.') | `madeungnyeong` | shake_no→explain | 반대
- **S33** 근거를 메모하듯 | `근거1 · 근거2` | "토론을 들을 땐 양쪽 근거를 콕콕 메모하세요. '찬성=시간 절약, 반대=단풍 감상.' 한눈에 보이죠." → (Jot each reason: 'for = saves time, against = enjoy leaves.') | `shelter` | think→weigh | 청취법
- **S34** 동의하며 잇기 | `저도 그렇게 생각해요` | "상대 근거에 공감되면 '저도 그렇게 생각해요'로 이어요. 동의는 토론을 부드럽게 하는 윤활유예요." → (If a reason resonates, follow with '저도 그렇게 생각해요' (I think so too).) | `shelter` | nod_agree→clap | 동의
- **S35** 정중히 반대하며 잇기 | `그 점도 맞지만 저는 ~` | "반대할 땐 '그 점도 맞지만, 저는 ~다고 생각해요'처럼 먼저 인정하고 이어요. 그러면 다툼이 아니라 대화예요." → (Disagree by first acknowledging: 'That's true, but I think ~.' Then it's a conversation.) | `final_ridge` | present_right→persuade | 반대
- **S36** 질문으로 확인 | `왜 그렇게 생각하세요?` | "이유가 궁금하면 '왜 그렇게 생각하세요?'라고 물어봐요. 상대 근거를 더 듣는 좋은 질문이에요." → (Curious? Ask '왜 그렇게 생각하세요?' (Why do you think so?).) | `final_ridge` | curious→point_self | 질문
- **S37** 열린 마음 | `서로 배워요` | "토론은 이기는 게 아니라 서로 배우는 거예요. 좋은 근거를 들으면 '아, 그렇군요!' 하고 생각을 바꿀 줄도 알아야죠." → (A debate is about learning, not winning. On a good reason, say 'Ah, I see!' and be ready to change your mind.) | `summit` | surprised→nod_agree | 태도
- **S38** 토론 정리 | `찬성·반대 모두 근거로` | "찬성이든 반대든, 근거만 또렷하면 훌륭한 의견이에요. 중요한 건 '왜'를 말할 수 있느냐예요." → (For or against, a clear reason makes a fine opinion. What matters is saying 'why.') | `summit` | weigh→confident | 정리

## 5막 — 설득 역할극 · 한국 토론 문화 · 마무리 (S39–S46)

- **S39** 설득해 볼까요 | `근거로 마음을 움직이기` | "이제 설득이에요. 설득은 억지가 아니라, 좋은 근거로 상대 마음을 살며시 움직이는 거예요." → (Now, persuasion — not force, but gently moving someone's heart with good reasons.) | `unhae` | persuade→smile_bright | 개념
- **S40** 설득 역할극 | `같이 정상까지 가요` | "'조금만 더 힘내요! 저는 우리가 정상까지 갈 수 있다고 생각해요, 왜냐하면 여기까지 잘 왔기 때문이에요.'" → ('Just a little more! I think we can reach the top, because we've made it this far.') | `unhae` | determined→persuade | 역할극
- **S41** 공감 먼저, 근거 나중 | `마음 + 근거` | "설득의 비결은 '공감 먼저, 근거 나중'. '힘든 거 알아요. 그렇지만 조금만 더 가면 멋진 풍경이 있거든요.'" → (The secret: empathy first, reason second. 'I know it's hard. But a bit farther, there's a gorgeous view.') | `descent` | present_right→look_view | 팁
- **S42** 한국의 토론 문화 | `예의와 존중` | "한국에선 의견을 나눌 때 '예의'를 아주 중요하게 여겨요. 아무리 반대해도 상대를 존중하고, 끝엔 웃으며 마무리해요." → (In Korea, courtesy matters greatly. However much you disagree, respect the other and end with a smile.) | `descent` | bow→greet_both | 문화1
- **S43** 나이·관계도 살펴요 | `어른께는 더 정중히` | "어른이거나 처음 본 사이면 더 정중히요. '제 생각을 말씀드려도 될까요?'처럼 양해를 먼저 구하면 아주 공손해요." → (With elders, be extra polite. 'May I share my view?' asks leave first.) | `osaek` | bow→present_right | 문화2
- **S44** 정상에서 한마디 | `해냈어요!` | "드디어 정상! '저는 우리가 해낼 줄 알았다고 생각해요, 왜냐하면 끝까지 포기하지 않았기 때문이에요.' 오늘 문형, 정상에서도 딱!" → (The summit at last! 'I knew we'd make it, because we never gave up.') | `osaek` | cheer→proud | 성취
- **S45** 오늘의 정리 | `주장 · 왜냐하면 · 따라서 · 정중히` | "오늘 우리는 '제 생각에는'으로 열고, '왜냐하면'으로 근거를 대고, '따라서'로 맺고, 정중히 동의·반대하는 법까지 배웠어요." → (Today we learned to open with '제 생각에는', give a reason with '왜냐하면', close with '따라서', and agree/disagree politely.) | `sunset` | explain_open→present_right | 총정리
- **S46** 다음에 또 만나요 | `구독 · 좋아요` | "여러분은 어떤 의견이 있나요? 근거와 함께 댓글로 들려주세요. 설악산에서 배운 논리적인 한국어, 다음에 또 함께해요! 구독과 좋아요 잊지 마시고요!" → (What's your opinion? Share it with a reason in the comments. Let's meet again for logical Korean — and don't forget to subscribe and like!) | `sunset` | wave→greet_both→laugh_big | 마무리·엔드카드

---

## 제작 메모 (다음 단계)
- **걷기**: 완성된 Veo 투명컷 16(r/l) 사용 — 등산로 이동 씬에 순환+이동. 재제작 불필요.
- **포즈 신규 생성**: 위 표정 다양 30종을 `jieun_hiking_base` 키프레임에서 agy 4병렬 생성(투명컷·오른쪽 향함)·cutout·정규화·register_jieun_w19_poses. ★어린 학생 표정 다양성이 핵심.
- **배경 23종**: 설악산 구석구석 agy 직접생성(연속 장면·왼편 복잡하지 않게·글자 없음) → 뷰어 확인.
- **자막·음성 표준(항상 동일)**: `'한글'[발음](뜻)`·품사·번인금지 소프트·선희/Emma·1.1배속·es-419/zh-Hans. add_pron.
- **좌상단 텍스트박스**: build_w19가 cap="" + 박스PNG static(코랄).
- **캐릭터 게이트**: 렌더 전 `check_char_fit.py KO-W19`.
