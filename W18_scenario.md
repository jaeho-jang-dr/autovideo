# W18 시나리오 — 감정 표현 · 세밀한 마음 묘사 (마담제이 · 전주 한옥마을)

> **주제:** 기본 감정어(기쁘다·슬프다·긴장되다·속상하다) + 감정 원인 문형(`-아서/어서 -아요`) + 세밀한 마음 묘사(서운하다·뿌듯하다·벅차다·울컥하다·마음이 놓이다…) + 공감·위로 표현 + 한국의 **'정(情)'** 문화
> **범위 고정:** 웹 훈민정음 18주차 2분 핵심영상(`hangeul_w18_stickman`, 고급2주차 "감정과 세밀한 마음 묘사")을 기준으로, **감정 표현·세밀한 마음 묘사 바운더리 안에서만** 확장. 커리큘럼 타깃 = 기쁘다·슬프다·긴장되다·속상하다(+화나다·걱정되다·설레다), 문형 `-아서/어서`, 공감 "많이 속상했겠어요", 문화 '정(情)'.
> **캐릭터:** 마담제이(여) — 레퍼런스 락 = `assets/characters/cutouts/madam_jay_base_front.png` (연한 코랄 V넥 선생님 조끼[가슴 펜주머니+니트 밑단·흰 이너] · 흰 A라인 무릎치마 · 진갈색 탑번 쪽머리[양옆 잔머리 한 가닥] · 크림색 슬립온 · 크림 벙어리손 · 가는 스틱 팔다리 · 굵은 검정 외곽선 플랫카툰 · 큰 머리≈키 1/3)
> **배경:** **전주 한옥마을** — 입구 기와 전경·한옥 골목·경기전 돌담·한옥 마당(툇마루)·한지공방·전동성당 원경·오목대 정자·전주향교(은행나무)·남천교/청연루·노을 기와
> **길이:** 47씬(S0–S46) ≈ 8분
> **톤:** 마담제이 = 따뜻하고 섬세한 여선생님. 감정을 다루는 회차이므로 나레이션도 **부드럽고 공감적**으로. 단정보다 어루만지듯.
> **끝맺음:** 반복 어미 피하고 다양하게(~요/~죠/~답니다/~네요/~봐요/~보세요/~거든요/~ㄹ까요). 감정 회차라 "~겠어요/~겠죠"(공감 추측)도 적극 활용.
> **어휘 표기 원칙:** KO·EN 나레이션 모두 **`'한글' (뜻)`** 형식 — 따옴표 한글은 ko 여성음성(선희) 발음, `add_pron`이 [발음] 자막 자동. 영어 뜻/외래어는 Emma.
> **품사 짚기(W17부터 표준):** 핵심 감정어엔 "'기쁘다'는 감정을 나타내는 **형용사**예요"처럼 문법 속성을 짧게. `-아서/어서`는 **연결어미**로 짚기.
> **나레이터/성우:** 러닝 나레이션=선희, ' ' 속 한글 예문=선희 DB클립, 영어=Emma. 속도 1.1·딜레이 0. (W17 표준 계승)

---

## 배경 10종 (불투명, `w18/backgrounds/`)

| key | 장소 | 비고 |
|-----|------|------|
| `w18_bg_entrance` | 전주 한옥마을 입구·기와지붕 물결 전경 | 도입·마무리 |
| `w18_bg_alley` | 한옥 골목길(돌담·기와·처마) | 기본 감정 파트 |
| `w18_bg_gyeonggijeon` | 경기전 돌담·고목 숲(차분·장엄) | 긴장·속상 파트 |
| `w18_bg_yard` | 한옥 마당(툇마루·마루·장독대) | 감정 원인 문형 파트 |
| `w18_bg_hanji` | 한지 공방(색색 한지등·창호) | 뉘앙스 파트 |
| `w18_bg_cathedral` | 전동성당 원경(로맨틱·설렘) | 설렘·두근거림 |
| `w18_bg_omokdae` | 오목대 정자·전망(탁 트인 하늘) | 벅참·뭉클 파트 |
| `w18_bg_hyanggyo` | 전주향교 은행나무·고목(포근·정) | 정(情) 문화 파트 |
| `w18_bg_cheongyeonru` | 남천교·청연루(개천·다리) | 공감·위로 파트 |
| `w18_bg_sunset` | 노을 진 기와지붕 | 총정리·엔드카드 |

> 배경 규칙: **하나의 연속 장면으로 화면 전체를 꽉 채움**(왼쪽에 흰칸·패널·seam 금지). **왼편(마담제이 자리)은 풍경이 복잡하지 않게**(디테일 덜, 연속은 유지) — "비워라"는 말 금지, 캐릭터 자리는 합성으로 처리. 글자·숫자·상표 금지(픽토그램·표정 아이콘만). 2씬당 1배경. [[lesson-render-review-rules]]

## 포즈 24종 (투명 컷아웃, `assets/characters/mj_w18_<key>.png`, 마담제이 락 · 오른쪽 향함)

- **인사/기본:** `wave`(손 흔들기)·`bow`(정중히 인사)·`greet_both`(양팔 벌려 환영)
- **설명/제시:** `explain`(두 손 설명)·`explain_open`(양손 벌려)·`present_right`(오른손바닥 제시)·`point_right`(오른쪽 가리키기)·`point_self`(자기 가슴=마음)
- **기쁨 계열:** `smile_big`(환한 미소, 두 손 살짝 위)·`clap`(박수)·`cheer`(양팔 만세)
- **슬픔/속상:** `sad`(고개 숙여 시무룩)·`wipe_tear`(눈가 닦기)·`heavy_heart`(가슴에 손, 무거운 마음)
- **긴장/설렘:** `tense`(어깨 움츠려 두 주먹)·`deep_breath`(가슴에 손, 심호흡)·`flutter`(두 손 가슴, 두근두근)
- **뉘앙스/사색:** `think`(턱에 손)·`compare`(양손 좌우 비교)·`hand_heart`(두 손 가슴에 모아 뭉클)
- **공감/위로:** `comfort`(오른손 내밀어 위로)·`hold_hands`(두 손 맞잡기)·`nod_empathy`(공감하며 끄덕)
- **걷기:** `walk_right_1`/`walk_right_2`

---

# 씬별 시나리오 (47씬)

> 표기: **[씬] 자막(KO) | 화면글자 | 나레이션(KO) → (EN) | 배경 | 마담제이 동작(2~3 교차) | 태그**

## 1막 — 도입: 전주 한옥마을 (S0–S6)

- **S0** (무나레이션·추천카드) | (없음) | [정적 10초] | `w18_bg_entrance` | (정지) | 카드
- **S1** 전주 한옥마을에 오신 걸 환영해요 | `전주 한옥마을` | "안녕하세요, 여러분. 여기는 고운 기와지붕이 물결처럼 이어지는 '전주 한옥마을'이에요. 오늘은 저 마담제이와 함께, 마음을 표현하는 한국어를 배워 볼까요?" → (Hello, everyone. This is '전주 한옥마을' (Jeonju Hanok Village), where graceful tiled roofs ripple like waves. Today, with me, Madam J, shall we learn the Korean of the heart?) | `w18_bg_entrance` | walk_right_1→walk_right_2→wave | 인사
- **S2** 마음을 말로 | `기쁨 · 슬픔 · 설렘` | "우리는 하루에도 참 많은 감정을 느끼죠. 기쁨, 슬픔, 설렘… 그 마음을 말로 나눌 수 있다면, 한국어가 훨씬 더 따뜻해진답니다." → (We feel so many emotions each day — joy, sadness, flutter. When you can put those feelings into words, Korean grows much warmer.) | `w18_bg_entrance` | explain→point_self | 동기
- **S3** 오늘의 주제 | `감정 표현 · 마음 묘사` | "그래서 오늘의 주제는 '감정 표현' (expressing emotions)과, 한 걸음 더 들어간 '세밀한 마음 묘사'예요. 비슷해 보여도 미묘하게 다른 마음까지 짚어 봅시다." → (So today's theme is '감정 표현' (expressing emotions), and a step deeper — describing subtle feelings. We'll even catch emotions that look alike but differ ever so slightly.) | `w18_bg_entrance` | greet_both→explain_open | 예고
- **S4** 한옥을 거닐며 | `천천히, 마음으로` | "천천히 한옥 골목을 거닐다 보면 마음도 차분해지죠. 이렇게 편안한 곳에서 감정 표현을 배우면, 오래오래 기억에 남을 거예요." → (Strolling slowly through the hanok alleys, your heart settles too. Learning emotion words in such a calm place, they'll stay with you a long time.) | `w18_bg_alley` | walk_right_1→walk_right_2→present_right | 분위기
- **S5** 감정어는 그림씨 | `감정어 = 형용사` | "먼저 살짝 귀띔할게요. 한국어에서 감정을 나타내는 말은 대부분 '형용사' (adjective), 즉 상태를 그리는 그림씨예요. '기쁘다', '슬프다'처럼요." → (A little hint first: in Korean, most feeling words are '형용사' (adjectives) — words that paint a state, like '기쁘다' (to be glad) and '슬프다' (to be sad).) | `w18_bg_alley` | point_up(=present_right)→explain | 품사
- **S6** 수업 시작해요 | `시작해요` | "자, 포근한 이 골목에서 오늘 수업을 시작해 봐요. 마음을 살며시 들여다볼 준비, 되셨나요?" → (Now, let's begin today's lesson in this cozy alley. Are you ready to gently look inside your heart?) | `w18_bg_alley` | greet_both→smile_big | 전환

## 2막 — 기본 감정 네 가지 (S7–S18)

- **S7** 네 가지 기본 감정 | `기쁘다 · 슬프다 · 긴장되다 · 속상하다` | "오늘 꼭 익힐 기본 감정은 네 가지예요. '기쁘다' (to be happy), '슬프다' (to be sad), '긴장되다' (to feel nervous), 그리고 '속상하다' (to be upset). 하나씩 만나 볼까요?" → (There are four core feelings to master today: '기쁘다' (to be happy), '슬프다' (to be sad), '긴장되다' (to feel nervous), and '속상하다' (to be upset). Let's meet them one by one.) | `w18_bg_alley` | present_right→compare | 개요
- **S8** 기쁘다 | `기쁘다 (happy)` | "첫 번째, '기쁘다' (to be happy). 좋은 일이 생겨 마음이 환하게 밝아지는 느낌이에요. 얼굴에 절로 미소가 번지죠." → (First, '기쁘다' (to be happy) — the feeling of your heart brightening when something good happens. A smile spreads across your face.) | `w18_bg_alley` | smile_big→clap | 감정1
- **S9** 정말 기뻐요 | `기뻐요!` | "이렇게 써 봐요. '합격 소식을 들어서 정말 기뻐요.' 기쁠 땐 이렇게 환하게 말해 보세요. 듣는 사람도 함께 기뻐진답니다." → (Use it like this: '합격 소식을 들어서 정말 기뻐요' (I'm so glad to hear I passed). Say it brightly — the listener grows glad with you.) | `w18_bg_gyeonggijeon` | cheer→smile_big | 활용1
- **S10** 슬프다 | `슬프다 (sad)` | "두 번째, '슬프다' (to be sad). 마음이 가라앉고 눈시울이 뜨거워지는, 그런 먹먹한 감정이에요." → (Second, '슬프다' (to be sad) — that heavy feeling when your heart sinks and your eyes grow warm.) | `w18_bg_gyeonggijeon` | sad→wipe_tear | 감정2
- **S11** 조금 슬퍼요 | `슬퍼요…` | "'헤어지게 되어서 슬퍼요.' 슬플 땐 억지로 참기보다, 이렇게 솔직하게 말하는 것도 큰 위로가 돼요." → ('헤어지게 되어서 슬퍼요' (I'm sad because we have to part). When you're sad, saying it honestly like this can be a great comfort.) | `w18_bg_gyeonggijeon` | wipe_tear→heavy_heart | 활용2
- **S12** 긴장되다 | `긴장되다 (nervous)` | "세 번째, '긴장되다' (to feel nervous). 중요한 일을 앞두고 가슴이 두근거리고 몸이 굳는 느낌이죠. 발표 직전을 떠올려 보세요." → (Third, '긴장되다' (to feel nervous) — heart pounding, body stiffening before something important. Picture the moment right before a presentation.) | `w18_bg_gyeonggijeon` | tense→deep_breath | 감정3
- **S13** 너무 긴장돼요 | `긴장돼요` | "'면접을 앞두고 있어서 너무 긴장돼요.' 이럴 땐 숨을 크게 한 번 쉬고, '괜찮아, 잘할 수 있어'라고 스스로를 다독여 봐요." → ('면접을 앞두고 있어서 너무 긴장돼요' (I'm so nervous with the interview ahead). Take a deep breath and soothe yourself: 'It's okay, I can do it.') | `w18_bg_yard` | deep_breath→comfort | 활용3
- **S14** 속상하다 | `속상하다 (upset)` | "네 번째, '속상하다' (to be upset). 일이 뜻대로 안 되거나 마음이 상해서, 속이 쓰리고 답답한 감정이에요. 아주 자주 쓰는 말이랍니다." → (Fourth, '속상하다' (to be upset) — when things don't go your way and your heart aches, a sore, stuffy feeling. It's used very often.) | `w18_bg_yard` | heavy_heart→sad | 감정4
- **S15** 많이 속상해요 | `속상해요` | "'실수를 해서 많이 속상해요.' 속상할 땐 혼자 삭이지 말고 가까운 사람에게 이렇게 털어놓아 보세요. 한결 가벼워질 거예요." → ('실수를 해서 많이 속상해요' (I'm really upset because I made a mistake). Don't bottle it up — share it like this with someone close, and it'll feel lighter.) | `w18_bg_yard` | heavy_heart→hold_hands | 활용4
- **S16** 설레다 | `설레다 (fluttering)` | "여기에 하나 더, '설레다' (to feel a flutter). 좋은 일을 기대하며 가슴이 콩닥콩닥 뛰는, 기분 좋은 떨림이에요." → (One more: '설레다' (to feel a flutter) — the pleasant thrill of your heart pattering as you look forward to something good.) | `w18_bg_cathedral` | flutter→smile_big | 감정5
- **S17** 화나다 · 걱정되다 | `화나다 · 걱정되다` | "감정어는 더 있어요. 몹시 언짢은 '화나다' (to be angry), 마음이 놓이지 않는 '걱정되다' (to be worried)까지, 상황에 맞게 골라 쓰면 된답니다." → (There are more: '화나다' (to be angry) and '걱정되다' (to be worried). Pick the one that fits the moment.) | `w18_bg_cathedral` | tense→think | 확장
- **S18** 네 감정 정리 | `기쁘다 · 슬프다 · 긴장되다 · 속상하다` | "정리해 봐요. 기쁘고, 슬프고, 긴장되고, 속상하고. 이 네 감정만 잘 말해도 하루의 마음을 충분히 나눌 수 있어요." → (Let's recap: glad, sad, nervous, upset. Just these four already let you share a whole day's heart.) | `w18_bg_yard` | compare→present_right | 정리

## 3막 — 감정의 원인: `-아서/어서 -아요` (S19–S28)

- **S19** 왜 그런 기분일까? | `원인 + 감정` | "이제 한 단계 나아가 봐요. '왜' 그런 기분인지, 원인을 함께 말하는 법이에요. 원인과 감정을 이어 주는 연결 고리를 배워 봅시다." → (Now a step further: how to say 'why' you feel that way, joining the cause to the feeling. Let's learn the link that connects them.) | `w18_bg_yard` | explain→point_self | 개념
- **S20** -아서 / -어서 | `-아서 / -어서 (연결어미)` | "그 고리가 바로 '-아서'와 '-어서'예요. 원인을 잇는 '연결어미'죠. 밝은 모음엔 '-아서', 나머지엔 '-어서'를 붙여요." → (That link is '-아서' and '-어서' — connective endings that join a cause. Bright vowels take '-아서', the rest take '-어서'.) | `w18_bg_yard` | finger_up(=present_right)→explain | 규칙·품사
- **S21** 시험이 끝나서 기뻐요 | `시험이 끝나서 → 기뻐요` | "예문을 볼까요? '시험이 끝나서 기뻐요.' 앞에는 원인, 뒤에는 감정. '끝나다'에 '-아서'가 붙어 '끝나서'가 되었죠." → (An example: '시험이 끝나서 기뻐요' (I'm glad because the exam is over). Cause first, feeling next. '끝나다' plus '-아서' becomes '끝나서'.) | `w18_bg_yard` | present_right→smile_big | 예문1
- **S22** 원인 → 감정 | `왜? → 어떤 마음?` | "들리시나요? '왜 기쁜지'가 자연스럽게 이어지죠. 이렇게 말하면 상대가 내 마음을 훨씬 깊이 이해하게 돼요." → (Hear it? The 'why' flows right into the feeling. Speaking this way lets others understand your heart much more deeply.) | `w18_bg_hanji` | explain→nod_empathy | 설명1
- **S23** 비가 와서 속상해요 | `비가 와서 → 속상해요` | "이번엔 슬픈 쪽. '비가 와서 속상해요.' '오다'가 '와서'로 바뀌었네요. 소풍이 취소된 아이의 마음이 그려지죠." → (Now the sad side: '비가 와서 속상해요' (I'm upset because it rained). '오다' turns into '와서'. You can picture a child whose picnic was canceled.) | `w18_bg_hanji` | heavy_heart→sad | 예문2
- **S24** 이유가 있으니까 | `마음엔 이유가 있어요` | "모든 감정에는 이유가 있어요. 그 이유를 '-아서/어서'로 살며시 밝히면, 투정이 아니라 진심 어린 이야기가 된답니다." → (Every feeling has a reason. Reveal it gently with '-아서/어서', and it becomes not a complaint but a heartfelt story.) | `w18_bg_hanji` | explain_open→comfort | 설명2
- **S25** 발표가 있어서 긴장돼요 | `발표가 있어서 → 긴장돼요` | "긴장도 이렇게. '발표가 있어서 긴장돼요.' 원인을 말해 두면, 옆 사람이 '괜찮아, 잘할 거야' 하고 응원해 주기 쉬워지죠." → (Nervousness too: '발표가 있어서 긴장돼요' (I'm nervous because I have a presentation). Naming the cause makes it easy for others to cheer, 'You'll do great.') | `w18_bg_cathedral` | tense→deep_breath | 예문3
- **S26** 친구를 만나서 설레요 | `친구를 만나서 → 설레요` | "설렘도 넣어 봐요. '오랜 친구를 만나서 설레요.' 기대되는 마음이 '-아서'를 타고 콩닥콩닥 전해지네요." → (Add flutter: '오랜 친구를 만나서 설레요' (I feel a flutter because I'm meeting an old friend). The anticipation rides on '-아서', pit-a-pat.) | `w18_bg_cathedral` | flutter→smile_big | 예문4
- **S27** 칭찬을 들어서 뿌듯해요 | `칭찬을 들어서 → 뿌듯해요` | "하나 더. '칭찬을 들어서 뿌듯해요.' 여기 '뿌듯하다' (to feel proud and content)는 마음이 가득 차오르는 흐뭇한 감정이에요." → (One more: '칭찬을 들어서 뿌듯해요' (I feel proud because I was praised). '뿌듯하다' (proud and content) is that warm, filling feeling.) | `w18_bg_omokdae` | point_self→hand_heart | 예문5
- **S28** 문형 정리 | `원인 + -아서/어서 + 감정` | "정리하면, '원인 + 아서/어서 + 감정'이에요. 이 한 줄이면 '무슨 마음인지'와 '왜 그런지'를 한 번에 전할 수 있답니다." → (In sum: 'cause + 아서/어서 + feeling'. This one line conveys both what you feel and why, all at once.) | `w18_bg_omokdae` | compare→present_right | 정리

## 4막 — 세밀한 마음 묘사: 뉘앙스 (S29–S38) ★핵심 확장

- **S29** 비슷하지만 다른 마음 | `미묘한 차이` | "이제 오늘의 하이라이트예요. 비슷해 보이지만 결이 다른 감정들. 이 미묘한 차이를 알면, 마음을 정말 섬세하게 그릴 수 있어요." → (Now today's highlight: feelings that look similar but differ in texture. Knowing these subtle shades lets you paint your heart with real delicacy.) | `w18_bg_omokdae` | think→explain | 개념
- **S30** 속상하다 vs 서운하다 | `속상하다 ↔ 서운하다` | "'속상하다'는 일이 안 풀려 속이 상한 것, '서운하다' (to feel let down)는 상대에게 바란 게 채워지지 않아 섭섭한 마음이에요. '연락이 없어서 서운했어요'처럼요." → ('속상하다' is when things go wrong; '서운하다' (to feel let down) is the quiet hurt when someone doesn't meet what you'd hoped, like '연락이 없어서 서운했어요' (I felt let down that you didn't call).) | `w18_bg_hanji` | compare→heavy_heart | 뉘앙스1
- **S31** 뿌듯하다 | `뿌듯하다 (proud & full)` | "'뿌듯하다' (to feel proud and content)는 애쓴 만큼 마음이 가득 차오르는 흐뭇함이에요. '해내서 뿌듯해요'라고 하면, 그 벅찬 보람이 그대로 전해지죠." → ('뿌듯하다' (proud and content) is the warm fullness after real effort. Say '해내서 뿌듯해요' (I feel proud that I pulled it off), and the reward carries over.) | `w18_bg_hanji` | hand_heart→smile_big | 뉘앙스2
- **S32** 아쉽다 · 홀가분하다 | `아쉽다 ↔ 홀가분하다` | "끝날 때의 두 마음도 배워요. 남은 미련은 '아쉽다' (to feel it's a pity), 짐을 내려놓은 개운함은 '홀가분하다' (to feel light and free). 같은 이별에도 두 마음이 함께 있죠." → (Two feelings at an ending: lingering regret is '아쉽다' (what a pity), and the relief of setting a burden down is '홀가분하다' (light and free). One farewell can hold both.) | `w18_bg_hyanggyo` | sad→greet_both | 뉘앙스3
- **S33** 벅차다 · 뭉클하다 | `가슴이 벅차다 · 뭉클하다` | "감동이 클 땐, 가슴이 꽉 차는 '벅차다' (to be overwhelmed with emotion)와, 코끝이 찡해지는 '뭉클하다' (to be deeply moved)를 써요. '그 말에 마음이 뭉클했어요'처럼요." → (For deep emotion: '벅차다' (overwhelmed, heart brimming) and '뭉클하다' (deeply moved, throat tightening), as in '그 말에 마음이 뭉클했어요' (those words deeply moved me).) | `w18_bg_omokdae` | hand_heart→wipe_tear | 뉘앙스4
- **S34** 설레다 · 두근거리다 | `설레다 · 두근거리다` | "기대의 떨림도 두 결이에요. 은근히 부푸는 '설레다', 심장이 빠르게 뛰는 '두근거리다' (to have one's heart pound). '첫 여행이라 두근거려요'처럼 함께 써도 좋아요." → (Anticipation has two shades: the gentle swell of '설레다', and the fast beat of '두근거리다' (heart pounding), as in '첫 여행이라 두근거려요' (my heart's pounding — it's my first trip).) | `w18_bg_cathedral` | flutter→smile_big | 뉘앙스5
- **S35** 마음이 놓이다 | `마음이 놓이다 (relieved)` | "이번엔 '마음'으로 그리는 표현이에요. 걱정이 사라져 편안해지면 '마음이 놓이다' (to feel relieved). '무사하다니 마음이 놓여요'라고 하면 안도가 물씬 느껴지죠." → (Now expressions painted with '마음' (the heart): when worry lifts, '마음이 놓이다' (to feel relieved), as in '무사하다니 마음이 놓여요' (I'm so relieved you're safe).) | `w18_bg_cheongyeonru` | deep_breath→nod_empathy | 관용1
- **S36** 마음이 무겁다 · 가볍다 | `마음이 무겁다 ↔ 가볍다` | "걱정이 얹히면 '마음이 무겁다', 훌훌 털면 '마음이 가볍다'예요. 마음을 무게로 그리는, 참 한국어다운 표현이랍니다." → (Weighed by worry, '마음이 무겁다' (heavy-hearted); shaken off, '마음이 가볍다' (light-hearted). Painting the heart as weight — so very Korean.) | `w18_bg_cheongyeonru` | heavy_heart→greet_both | 관용2
- **S37** 울컥하다 | `울컥하다 (welling up)` | "감정이 왈칵 북받쳐 목이 메면 '울컥하다' (to well up with emotion). 고마움이나 서러움이 한꺼번에 밀려올 때, '편지를 읽다가 울컥했어요'라고 해요." → (When emotion surges and your throat catches, '울컥하다' (to well up). When gratitude or sorrow floods in at once: '편지를 읽다가 울컥했어요' (I welled up reading the letter).) | `w18_bg_cheongyeonru` | wipe_tear→hand_heart | 관용3
- **S38** 뉘앙스 정리 | `결이 다른 마음들` | "보셨죠? 속상함과 서운함, 벅참과 뭉클함… 결이 조금씩 달라요. 이 미세한 차이를 담을수록, 여러분의 한국어는 더 깊고 다정해진답니다." → (See? Upset and let-down, brimming and moved — each a slightly different grain. The more you catch these fine shades, the deeper and warmer your Korean becomes.) | `w18_bg_hyanggyo` | compare→hand_heart | 정리

## 5막 — 공감·위로 + 정(情) 문화 + 마무리 (S39–S46)

- **S39** 감정은 나누는 것 | `함께 느끼기` | "감정은 혼자 삼키는 게 아니라 나누는 거예요. 상대의 마음을 함께 느껴 주는 것, 그게 바로 '공감' (empathy)이랍니다." → (Feelings aren't meant to be swallowed alone but shared. Feeling another's heart together — that's '공감' (empathy).) | `w18_bg_hyanggyo` | comfort→nod_empathy | 개념
- **S40** 많이 속상했겠어요 | `많이 속상했겠어요` | "공감의 대표 표현이에요. '많이 속상했겠어요.' 여기 '-겠어요'는 상대의 마음을 헤아려 추측하는 다정한 어미죠. 이 한마디에 마음이 스르르 풀린답니다." → (The classic empathy line: '많이 속상했겠어요' (You must have been so upset). '-겠어요' is a tender ending that guesses at another's heart. This one phrase melts the tension away.) | `w18_bg_cheongyeonru` | comfort→hold_hands | 공감1
- **S41** 얼마나 기뻤어요! | `얼마나 기뻤어요` | "기쁜 일엔 함께 크게 기뻐해 줘요. '얼마나 기뻤어요!', '정말 설렜겠어요.' 이렇게 마음을 맞장구쳐 주면 기쁨이 두 배가 되죠." → (For happy news, rejoice big together: '얼마나 기뻤어요!' (How glad you must have been!), '정말 설렜겠어요' (You must have been so thrilled). Echoing the heart doubles the joy.) | `w18_bg_cheongyeonru` | cheer→smile_big | 공감2
- **S42** 곁에 있어 줄게요 | `괜찮아요, 곁에 있어요` | "때론 완벽한 말보다 곁에 있어 주는 게 더 큰 위로예요. '괜찮아요, 제가 곁에 있을게요.' 이 한마디의 온기를 기억해 두세요." → (Sometimes being there comforts more than perfect words: '괜찮아요, 제가 곁에 있을게요' (It's okay, I'll be by your side). Remember the warmth of this line.) | `w18_bg_hyanggyo` | hold_hands→comfort | 위로
- **S43** 한국의 '정(情)' | `정 (情)` | "이런 마음이 쌓이면 한국의 '정' (jeong)이 돼요. 말로 다 못 하는, 오래 함께한 사람들 사이의 깊고 따뜻한 유대감이랍니다." → (When such hearts pile up, they become Korea's '정' (jeong) — the deep, warm bond between people who've shared time, beyond what words can say.) | `w18_bg_hyanggyo` | hand_heart→explain | 문화1
- **S44** 말없이 건네는 마음 | `밥은 먹었어?` | "'정'은 소소한 데서 드러나요. '밥은 먹었어요?' 하고 안부를 챙기고, 말없이 반찬 한 접시를 더 놓아 주는 마음. 그게 한국인의 정이에요." → ('정' shows in little things — asking '밥은 먹었어요?' (Have you eaten?), quietly adding one more side dish. That is the jeong of Koreans.) | `w18_bg_hyanggyo` | present_right→nod_empathy | 문화2
- **S45** 오늘의 마음 정리 | `감정어 · -아서/어서 · 공감 · 정` | "오늘 우리는 기본 감정 네 가지부터, '-아서/어서'로 원인 잇기, 세밀한 뉘앙스, 공감과 위로, 그리고 '정'까지 마음을 그리는 한국어를 배웠어요." → (Today we learned to paint the heart in Korean — four core feelings, joining causes with '-아서/어서', subtle nuances, empathy and comfort, and even '정'.) | `w18_bg_sunset` | explain_open→present_right | 총정리
- **S46** 다음에 또 만나요 | `구독 · 좋아요` | "여러분의 오늘 하루는 어떤 마음이었나요? 댓글로 살며시 들려주세요. 마음을 나누는 한국어, 다음 시간에 또 함께해요. 구독과 좋아요, 잊지 마시고요!" → (What did your heart feel today? Share it gently in the comments. Let's meet again for the Korean of the heart — and don't forget to subscribe and like!) | `w18_bg_sunset` | wave→greet_both→smile_big | 마무리·엔드카드

---

## 제작 메모 (다음 단계용)
- **다음:** ①마담제이 포즈 24종 신규 생성(agy 4병렬, `mj_w18_*`, 마담제이 락 · 투명컷아웃 · 오른쪽 향함) → 뷰어(HTTP 갤러리)로 사장님 확인 ②전주 한옥마을 배경 10종 생성 → 확인 ③`build_w18.py`(build_w17 클론)로 content.db 반영 ④음성 DB: 따옴표 한글 예문·감정어를 선희로 사전 입력(커버리지 100% 확인 후 렌더) ⑤영어판 먼저 렌더→교정앱 ⑥교정 반영→한글판.
- **음성/자막 표준(W17 계승):** 러닝=선희, ' ' 한글=선희 DB클립, 영어=Emma, 속도 1.1·딜레이 0. 자막 로마자(시각용, 안 읽음) `add_pron`. 자막 번인 금지·소프트. es-419/zh-Hans.
- **캐릭터 게이트:** 렌더 전 `check_char_fit.py W18` 통과 필수(잘림·크기·방향).
- **감정 회차 특성:** 표정 다양성이 생명 — 같은 미소 반복 금지, 감정어마다 다른 포즈/표정 1:1 매칭.
