# W15 캐릭터 제작 지시서 (제미나이 / Antigravity)

> **감독(Claude) → 조감독(제미나이)**: W15 "날씨와 사계절" 영상용 지은 캐릭터 포즈 세트.
> 시나리오 = `W15_scenario.md` (75씬). 아래 목록의 포즈를 **의상별로** 제작한다.

---

## 🔒 절대 원칙 (사장님 최우선 지시)

1. **얼굴·머리·체형은 모든 이미지에서 100% 동일** — 레퍼런스: `home_vocab/w13/jieun_w13_base.png`
   - 긴 갈색 웨이브 머리 · 점 두 개 검은 눈 · 옅은 미소 · 흰 피부 · 갸름한 얼굴 · 소녀 체형·키
   - ⚠️ 얼굴 생김새·눈·머리색·머리길이·웨이브·피부색·키·체형 **절대 변경 금지**. 옷 갈아입어도 "같은 사람"이 한눈에 보여야 한다.
2. **옷과 신발만 계절별로 바뀐다.** 종이인형처럼 옷만 바꾸는 게 아니라, **그 옷을 입은 채로 각 동작을 실제로 하는** 그림이어야 한다 (몸·팔·다리·표정이 동작에 맞게 움직임).
3. 스타일: 굵은 검정 외곽선 플랫 컬러 카툰(지은 원본과 동일 화풍). 전신(머리끝~발끝) 다 보이게. 단색 흰 배경. 그림자·텍스트·서명 없음.
4. 저장: `home_vocab/w15/jieun_<의상>_<포즈>.png` (예: `jieun_spring_cheering.png`)
5. 크기 규격: W13 지은 포즈와 동일 캔버스(560×860 기준, 전신). 정규화는 감독(Claude)이 나중에 처리하니, **전신이 잘리지 않게** 그리기만 하면 됨.

---

## 의상 스펙 (7벌)

| 의상코드 | 옷 | 신발 |
|---|---|---|
| **spring** | 연분홍 얇은 카디건 + 하늘색 민소매 원피스 | 흰 운동화 |
| **summer** | 흰·하늘색 반팔 블라우스 + 연한 반바지, 밀짚모자 | 갈색 샌들 |
| **rain** | 밝은 노란 우비(레인코트)+모자, 우산 듦 | 노란 장화 |
| **autumn** | 머스타드 긴팔 니트 + 베이지 얇은 자켓 + 청바지 | 갈색 앵클부츠 |
| **winter** | 두꺼운 아이보리 니트 + 코트 + 빨간 목도리 | 갈색 부츠 |
| **winterpad** | 두꺼운 남색 롱패딩 + 털모자 + 목도리 + 벙어리장갑 | 방한 부츠 |
| **hiking** | 빨강·검정 등산 재킷 + 등산바지 + 배낭 | 등산화 |

---

## 포즈 목록 (의상별) — 시나리오에서 실제 쓰는 동작만

### 🌸 spring (봄옷) — 봄 막 + 도입/정리에서 사용
| 포즈파일 | 동작·표정 |
|---|---|
| `jieun_spring_base` | 정면 기본(팔 내림), 밝은 표정 |
| `jieun_spring_greeting` | 인사(한 손 들어 안녕), 웃음 (도입 S1) |
| `jieun_spring_presenting` | 한 손 펴서 설명하는 자세 |
| `jieun_spring_presenting_a` | presenting 중간동작(팔 살짝 다른 각도) |
| `jieun_spring_point_up` | 한 손으로 위(하늘/꽃) 가리키며 올려다봄 |
| `jieun_spring_point_right` | 한 손으로 오른쪽(콘텐츠) 가리킴 |
| `jieun_spring_cheering` | 두 손 들고 감탄·기뻐함 (선작지왓 꽃밭 감탄 S13) |
| `jieun_spring_excited` | 신나서 폴짝(소풍) 밝은 표정 (S18) |
| `jieun_spring_look_up` | 두 손 모으고 하늘/벚꽃 올려다보며 감탄 |
| `jieun_spring_walk1` | 걷기 프레임1 (오른발 앞) |
| `jieun_spring_walk2` | 걷기 프레임2 (왼발 앞) |
| `jieun_spring_wave` | 손 흔들기(마무리 인사 S75, 봄옷 복귀) |

### ☀️ summer (여름옷) — 여름 막
| 포즈파일 | 동작·표정 |
|---|---|
| `jieun_summer_base` | 정면 기본 |
| `jieun_summer_presenting` | 설명 자세 |
| `jieun_summer_presenting_a` | 설명 중간동작 |
| `jieun_summer_fan` | 손으로 부채질하며 "더워"하는 표정(땀 한 방울) (S24 덥다) |
| `jieun_summer_point_right` | 오른쪽 가리킴 |
| `jieun_summer_relax` | 시원한 그늘에서 편안·"시원해" 표정 (S32) |
| `jieun_summer_cheering` | 신나서 두 손 들기 (돈내코 계곡 S33) |
| `jieun_summer_eat` | 수박 한 조각 들고 먹으며 행복 (S34) |
| `jieun_summer_walk1` | 걷기1 |
| `jieun_summer_walk2` | 걷기2 |

### 🌧️ rain (우비) — 여름 비/장마
| 포즈파일 | 동작·표정 |
|---|---|
| `jieun_rain_umbrella` | 우비 입고 우산 펴서 든 자세 (S29) |
| `jieun_rain_surprise` | 소나기에 놀라 우산 급히 드는 표정 (S30) |
| `jieun_rain_walk1` | 우산 들고 걷기1 |
| `jieun_rain_walk2` | 우산 들고 걷기2 |

### 🍁 autumn (가을옷) — 가을 막
| 포즈파일 | 동작·표정 |
|---|---|
| `jieun_autumn_base` | 정면 기본 |
| `jieun_autumn_presenting` | 설명 자세 |
| `jieun_autumn_presenting_a` | 설명 중간동작 |
| `jieun_autumn_look_up` | 고개 들어 높은 하늘 올려다봄 (S41 하늘이 높다) |
| `jieun_autumn_point_right` | 오른쪽 가리킴 |
| `jieun_autumn_cheering` | 두 손 들고 감탄 (영실기암 단풍 S43) |
| `jieun_autumn_step_leaves` | 낙엽 밟으며 걷는 즐거운 자세 (S46) |
| `jieun_autumn_happy` | 두 손 모으고 행복한 표정 (가을 음식 S49) |
| `jieun_autumn_walk1` | 걷기1 |
| `jieun_autumn_walk2` | 걷기2 |

### ❄️ winter (겨울 일반옷) — 겨울 막 전반
| 포즈파일 | 동작·표정 |
|---|---|
| `jieun_winter_base` | 정면 기본 |
| `jieun_winter_presenting` | 설명 자세 |
| `jieun_winter_presenting_a` | 설명 중간동작 |
| `jieun_winter_shiver` | 두 팔로 몸 감싸고 추워서 덜덜 떠는 표정 (S53 춥다) |
| `jieun_winter_firstsnow` | 손 내밀어 첫눈 받으며 설레는 표정, 위 올려다봄 (S55 첫눈) |
| `jieun_winter_catch_snow` | 두 손 벌려 눈 맞으며 기뻐함 (S56 눈이 오다) |
| `jieun_winter_snowman` | 쪼그려/서서 눈사람 만드는 자세 (S58 눈사람) |
| `jieun_winter_snowball` | 눈뭉치 던지려는 신난 자세 (S59 눈싸움) |
| `jieun_winter_cheering` | 감탄(상고대 S62) |
| `jieun_winter_shiver_hard` | 더 심하게 덜덜 떨며 "너무 추워" (S64 방한 필요) |
| `jieun_winter_walk1` | 걷기1 |
| `jieun_winter_walk2` | 걷기2 |

### 🧥 winterpad (방한복) — 겨울 정상
| 포즈파일 | 동작·표정 |
|---|---|
| `jieun_winterpad_base` | 방한복 완전무장 정면 기본 |
| `jieun_winterpad_warm` | 두 팔 벌려 "이제 안 추워" 든든·따뜻한 표정 (S66) |
| `jieun_winterpad_presenting` | 설명 자세 |
| `jieun_winterpad_amazed` | 두 팔 활짝 벌려 백록담 설경에 벅차 감탄 (S67) |
| `jieun_winterpad_walk1` | 걷기1 |
| `jieun_winterpad_walk2` | 걷기2 |

### ⛰️ hiking (등산복) — 선택 (백록담 오르는 장면에 쓰면 넣고, 안 쓰면 방한복으로 대체 가능)
| 포즈파일 | 동작·표정 |
|---|---|
| `jieun_hiking_base` | 등산복 정면 기본 |
| `jieun_hiking_climb` | 지팡이/손 짚고 오르는 자세 |

---

## 우선순위 (계절 순서대로 제작하면 감독이 막 단위로 렌더 검증 가능)
1. **spring 12종** (봄 막) → 감독이 얼굴 일관성 먼저 확인
2. summer 10종 + rain 4종
3. autumn 10종
4. winter 12종 + winterpad 6종
5. hiking 2종

**총 약 56종.** spring 세트 먼저 만들어 감독(Claude)에게 주면, 얼굴 일관성·화풍을 검증하고 OK 나오면 나머지를 같은 기준으로 진행한다.

---

## 참고
- 걷기(walk1/2)는 좌우 다리·팔 교차 2프레임 (졸라맨 걷기 규칙과 동일: 오른팔+왼다리 앞 / 반대).
- `_a` 접미사 = 중간동작(설명 시 팔 각도가 살짝 다른 프레임, 부드러운 전환용).
- 소품(우산·수박·눈뭉치 등)은 그 동작에 필요한 것만 함께 그린다.
