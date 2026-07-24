# W16 시나리오 — 취미생활과 빈도 묘사 (인jun · 남이섬) ★8분 중복제거 최적화판

> **주제:** 취미(hobby) 어휘 + **빈도 표현**(매일·자주·가끔·일주일에 세 번 …)
> **캐릭터:** 인준(남) — 남이섬 액티비티 포즈 다수
> **배경:** **남이섬**(강원 춘천) — 메타세쿼이아길·강변·잔디밭·자전거길·짚와이어·동물방사장
> **길이:** **정확히 48씬** / **완벽한 8분 피팅**
> **방향 규칙:** 달리기와 걷기는 시선의 어색함 없이 무조건 **오른쪽 방향**(`walk_right`, `jogging`)으로만 가도록 통일.
> **컨셉:** "취미 부자" 인준이 남이섬을 돌며 취미 자랑 → 반전(야구·게임 "거의 안 해요") → 메타(진짜 매일 = "한국어 공부")

---

# 씬별 시나리오 (48씬)

> 표기: **[씬] 자막(KO) | 화면글자 | 나레이션(KO) → (EN) | 배경 | 인준 동작 | 태그**

## 1막 — 도입: 남이섬과 취미 (S1–S6)
- **S1** 남이섬에 왔어요! | `남이섬` | "안녕하세요, 여러분! 저는 인준이에요. 만나서 반가워요. 오늘은 아주 아름다운 섬, 남이섬에 왔어요. 날씨도 좋고 나무도 정말 많죠?" → (Hello, everyone! I'm Injun, nice to meet you. Today I'm on a beautiful island — '남이섬' (Nami Island). Lovely weather and so many trees, right?) | dock | walk_right→greeting→presenting | 도입
- **S2** 취미 | `취미` | "여러분, '취미'가 뭐예요? '취미'는 시간이 있을 때 즐겁게 하는 일이에요. 예를 들면 운동, 독서, 그림 같은 거예요." → ('Hobby' — '취미' (hobby) — is a fun thing you do in your free time, like sports, reading, or drawing.) | dock | presenting→point_self | 어휘
- **S3** 취미가 뭐예요? | `취미가 / 뭐예요?` | "친구를 만나면 이렇게 물어봐요. '취미가 뭐예요?' 아주 자주 쓰는 질문이에요. 같이 말해 볼까요? '취미가 뭐예요?'" → (When you meet a friend, ask: '취미가 뭐예요?' (What's your hobby?). A very common question — say it with me!) | metasequoia | walk_right→presenting | 질문문형
- **S4** 제 취미는… | `제 취미는` | "대답은 이렇게 해요. '제 취미는 자전거 타기예요.' '제 취미는 독서예요.' 여러분의 취미도 넣어서 말해 보세요." → (Answer like this: '제 취미는 자전거 타기예요' (My hobby is cycling), '제 취미는 독서예요' (My hobby is reading). Try it with your own hobby!) | metasequoia | presenting→point_self | 답변문형
- **S5** 좋아해요 | `좋아해요` | "이렇게도 말해요. '저는 사진 찍는 것을 좋아해요.' 동사에 '-는 것을 좋아해요'를 붙이면 돼요. '걷는 것을 좋아해요.'" → (You can also say: '저는 사진 찍는 것을 좋아해요' (I like taking photos). Add '-는 것을 좋아해요' to a verb — '걷는 것을 좋아해요' (I like walking).) | metasequoia | taking_photo→presenting | ~는 것을 좋아해요
- **S6** 얼마나 자주? | `얼마나 / 자주?` | "그런데 취미에서 정말 중요한 게 하나 있어요. 바로 '얼마나 자주' 하느냐예요. 매일? 가끔? 오늘 이걸 배워요." → (But one thing really matters with hobbies: '얼마나 자주' (how often)? Every day? Sometimes? Let's learn this today.) | lawn | thinking→point_up | 빈도 예고

## 2막 — 빈도 부사 사다리 (S7–S13)
- **S7** 매일 | `매일` | "먼저 '매일'이에요. '매일'은 하루도 빠지지 않고 한다는 뜻이에요. '저는 매일 조깅해요.' 매일매일, 하루도 안 빠져요." → ('매일' (every day) means every day, without missing a single day. '저는 매일 조깅해요' (I jog every day).) | riverside | walk_right→jogging | 100%
- **S8** 보통 | `보통` | "'보통'은 대개, 거의 그렇다는 뜻이에요. '저는 보통 아침에 산책해요.' 백 퍼센트는 아니지만 거의요." → ('보통' (usually) means usually. '저는 보통 아침에 산책해요' (I usually walk in the morning) — not always, but most of the time.) | metasequoia | walk_right→presenting | ~80%
- **S9** 자주 | `자주` | "'자주'는 여러 번, 흔히 한다는 뜻이에요. '저는 자주 사진을 찍어요.' 남이섬은 예뻐서 사진을 정말 자주 찍게 돼요." → ('자주' (often) means often. '저는 자주 사진을 찍어요' (I often take photos) — Nami Island is so pretty I photograph it a lot.) | ginkgo | taking_photo→point_right | ~70%
- **S10** 가끔 | `가끔` | "'가끔'은 이따금, 어쩌다 한 번씩이에요. '저는 가끔 낚시를 해요.' 매일은 아니고 생각날 때만요." → ('가끔' (sometimes) means sometimes. '저는 가끔 낚시를 해요' (I sometimes fish) — only now and then.) | fishing_pier | thinking→fishing | ~30%
- **S11** 거의 안 | `거의 안` | "'거의 안 해요'는 하기는 하는데 아주 드물다예요. '저는 게임을 거의 안 해요.' 한 달에 한 번쯤?" → ('거의 안 해요' (rarely) means rarely. '저는 게임을 거의 안 해요' (I rarely play games) — maybe once a month?) | lawn | thinking→point_left | ~10%
- **S12** 전혀 안 | `전혀 안` | "'전혀 안 해요'는 하나도 안 한다예요. 제로! '저는 커피를 전혀 안 마셔요.' '담배는 전혀 안 피워요.'" → ('전혀 안 해요' (never) means never — zero! '저는 커피를 전혀 안 마셔요' (I never drink coffee).) | lawn | point_left→clapping | 0%
- **S13** 어순 | `매일 산책해요` | "빈도 말은 동사 앞에 놓아요. '매일 산책해요.' '자주 사진을 찍어요.' 순서를 꼭 기억하세요. '저는 자주 걸어요.'" → (Put the frequency word before the verb: '매일 산책해요' (I walk every day), '자주 사진을 찍어요' (I often take photos). '저는 자주 걸어요' (I often walk).) | art_plaza | walk_right→presenting | 어순

## 3막 — 남이섬 취미 대공개 (S14–S25)
- **S14** 자전거 타기 | `자전거 타기` | "남이섬 하면 뭐니 뭐니 해도 자전거죠! 시원한 바람을 맞으며 자전거를 타요. 제 취미 중 최고예요." → (When you think of '남이섬' (Nami Island), you think '자전거' (cycling)! Riding in the cool breeze — my favorite hobby.) | bike_path | walk_right→cycling | 도입
- **S15** 자전거 빈도 | `일주일에 세 번` | "얼마나 자주 타냐고요? 일주일에 세 번 타요. '저는 일주일에 세 번 자전거를 타요.' 꽤 자주죠?" → (How often? Three times a week. '저는 일주일에 세 번 자전거를 타요' (I cycle three times a week) — quite a lot!) | bike_path | cycling→cheering | 일주일에 세 번
- **S16** 산책 | `산책` | "이 메타세쿼이아 길을 보세요. 여기서 산책하는 걸 정말 좋아해요. 저는 매일 산책해요." → (Look at this metasequoia road! I love '산책' (walking) here. '저는 매일 산책해요' (I walk every day).) | metasequoia | walk_right→presenting | 매일
- **S17** 조깅 | `조깅` | "아침에는 강변에서 조깅해요. 건강에 최고죠. '저는 매일 아침에 조깅해요.' 상쾌해요!" → (In the morning I do '조깅' (jogging) by the river. '저는 매일 아침에 조깅해요' (I jog every morning). So refreshing!) | riverside | jogging→stretching | 매일 아침
- **S18** 사진 찍기 | `사진 찍기` | "이렇게 예쁜 길에서는 사진을 안 찍을 수가 없어요. 저는 사진 찍는 걸 아주 좋아해서 자주 찍어요." → (On these pretty lanes I love '사진' (photos). '저는 사진 찍는 것을 좋아해요' (I like taking photos), so I do it '자주' (often).) | ginkgo | taking_photo→presenting | 자주
- **S19** 피크닉 | `피크닉` | "날씨 좋은 날엔 잔디밭에서 피크닉을 해요. 김밥도 싸 오고요. 주말에 자주 해요." → (On nice days I enjoy a '피크닉' (picnic) on the lawn — I even pack '김밥' (gimbap). I do it '자주' (often) on weekends.) | lawn | walk_right→picnic_sit | 자주
- **S20** 연날리기 | `연날리기` | "넓은 잔디밭에서는 연을 날려요. 바람이 불면 딱 좋아요. 가끔 하는 취미예요." → (On the wide lawn I fly a '연' (kite). It's a '가끔' (sometimes) hobby — perfect when it's windy.) | lawn | kite→cheering | 가끔
- **S21** 프리스비 | `프리스비` | "친구랑 프리스비도 던져요. 원반을 휙 던지고 받고, 재미있어요. 이것도 가끔요." → (I also play '프리스비' (frisbee) with a friend — throw and catch, so fun. Also '가끔' (sometimes).) | lawn | frisbee→cheering | 가끔
- **S22** 배드민턴 | `배드민턴` | "배드민턴도 좋아해요. 셔틀콕을 주고받죠. 일주일에 한 번 정도 쳐요." → (I like '배드민턴' (badminton) too — hitting the shuttlecock back and forth. About '일주일에 한 번' (once a week).) | lawn | badminton→cheering | 일주일에 한 번
- **S23** 낚시 | `낚시` | "강가에서는 낚시를 해요. 조용히 앉아서 기다리는 게 매력이에요. 가끔, 마음이 편할 때요." → (By the river I do '낚시' (fishing) — the charm is waiting quietly. '가끔' (sometimes), when I want to relax.) | fishing_pier | walk_right→fishing | 가끔
- **S24** 강아지 산책 | `강아지 산책` | "우리 강아지랑 산책도 해요. 강아지는 매일 나가야 하죠. 그래서 하루에 두 번 산책시켜요." → (I also do '강아지 산책' (dog-walking). Dogs need daily walks, so '하루에 두 번' (twice a day).) | pine_forest | walking_dog→presenting | 하루에 두 번
- **S25** 짚와이어 | `짚와이어` | "이건 특별해요. 짚와이어! 하늘을 나는 기분이에요. 무서워서 일 년에 한 번만 타요." → (This one's special — '짚와이어' (zip-wire)! Like flying. It's scary, so '일 년에 한 번' (once a year).) | zipwire | cheering→zipwire | 일 년에 한 번

## 4막 — 집에서 하는 취미와 계절 (S26–S33)
- **S26** 캠핑 | `캠핑` | "가끔은 캠핑도 가요. 텐트를 치고 밤을 보내죠. 한 달에 한 번 정도 캠핑을 해요." → (Sometimes I go '캠핑' (camping) — pitch a tent, spend the night. About '한 달에 한 번' (once a month).) | campsite | walk_right→camping | 한 달에 한 번
- **S27** 독서 | `독서` | "강변 벤치에 앉아서 책도 읽어요. 조용하고 좋아요. 저는 매일 저녁에 책을 읽어요." → (I read on a riverside bench — quiet and nice. '저는 매일 저녁에 책을 읽어요' (I read every evening).) | bench_rest | reading_bench→thinking | 매일 저녁
- **S28** 그림 그리기 | `그림 그리기` | "예술의 섬이니까 그림도 그려요. 풍경을 스케치하죠. 한 달에 두 번 정도 그려요." → (It's an art island, so I do '그림 그리기' (drawing) — sketching scenery. About '한 달에 두 번' (twice a month).) | art_plaza | painting→presenting | 한 달에 두 번
- **S29** 스케이트보드 | `스케이트보드` | "요즘 새로 시작한 취미가 있어요. 스케이트보드! 아직 서툴지만 요즘 자주 타요." → (My new hobby lately is '스케이트보드' (skateboarding)! Still clumsy, but '자주' (often) these days.) | bike_path | skateboard→cheering | 자주
- **S30** 피아노 | `피아노` | "집에서는 피아노를 쳐요. 좋아하는 곡을 연주하면 기분이 좋아져요. 매일 조금씩 연습해요." → (At home I play the '피아노' (piano) — my favorite songs lift my mood. '매일' (every day) I practice a little.) | home_living | piano→presenting | 매일
- **S31** 요리 | `요리` | "집에서는 가끔 요리도 해요. 앞치마를 두르고 맛있는 걸 만들어요. '저는 가끔 요리해요.'" → (At home I sometimes do '요리' (cooking). '저는 가끔 요리해요' (I sometimes cook).) | kitchen | cooking→presenting | 가끔
- **S32** 영화 보기 | `영화 보기` | "주말마다 집에서 영화를 봐요. 소파에 앉아 팝콘을 먹으면서요. 이게 주말의 행복이에요." → (Every weekend I do '영화 보기' (watching movies) at home — sofa and popcorn. '주말마다' (every weekend).) | home_living | watching_movie→clapping | 주말마다
- **S33** 게임 | `게임` | "게임도 좋아해요. 매일 조금씩 해요. 재미있으니까요, 하하." → (I also enjoy '게임' (games) — a little '매일' (every day), because it's fun. Haha.) | home_living | gaming→thinking | 매일(복선)

## 5막 — 반전·참여·마무리 (S34–S37)
- **S34** 진짜 매일 하는 건? | `매일 하는 건?` | "제가 취미가 참 많죠? 그런데 딱 하나, 진짜 매일 빠지지 않고 하는 게 있어요. 뭘까요? 맞혀 보세요." → (I have so many hobbies, right? But there's one thing I do '매일' (every day) without fail. What is it? Take a guess!) | dock_sunset | thinking→point_self→presenting | 궁금증
- **S35** 반전: 한국어 공부! | `매일 한국어 공부!` | "바로 매일 한국어 공부예요! 지금 이 영상을 보는 여러분처럼요. 이게 제 진짜 매일 취미예요." → (It's studying '한국어' (Korean) every day! Just like you, watching right now. That's my real daily hobby.) | dock_sunset | cheering→reading_bench | 반전
- **S36** 여러분의 취미는? | `여러분은?` | "여러분의 취미는 뭐예요? 그리고 얼마나 자주 하세요? 댓글로 꼭 알려주세요. 정말 궁금해요!" → (What's YOUR '취미' (hobby)? And '얼마나 자주' (how often) do you do it? Please tell me in the comments — I'm really curious!) | metasequoia | point_right→presenting | 참여
- **S37** 마무리 | `또 만나요!` | "즐거운 취미 생활 하세요! 그리고 매일 한국어 공부도 잊지 마세요. 다음 시간에 또 만나요. 안녕히 계세요!" → (Enjoy your hobbies! And don't forget to study '한국어' (Korean) '매일'. See you next time — 안녕히 계세요! (Goodbye!)) | dock_sunset | waving | 마무리
- **S48** (면책·무나레이션) | (화면 글자 없음) | [나레이션 없음] | dock_sunset | (없음) | 면책
  - KO: 이 모든 활동을 남이섬에서 다 할 수 있는 것은 아니에요. 남이섬은 이 한글 교육 영상의 배경으로만 사용되었어요.
  - EN: Not all of these activities can actually be done on Nami Island. It was used only as the backdrop for this Korean-learning video.
  - JA: これらの活動すべてを南怡島（ナミソム）でできるわけではありません。南怡島はこの韓国語学習動画の背景として使われただけです。
  - ZH: 并非所有这些活动都能在南怡岛进行。南怡岛只是作为这部韩语教学视频의 배경으로만 사용되었어요.
  - ES: No todas estas actividades se pueden hacer en la isla de Nami. La isla de Nami se usó solo como escenario para este video de aprendizaje de coreano.
