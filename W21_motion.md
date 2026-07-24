# W21 동작(블로킹) 시나리오 v2 — 다이나믹 (마담제이 살색·싱글라인 · 성수동)

> 교육 내용은 `W21_scenario.md` 26씬 그대로. **동작만 다시(더 다이나믹)**.

## 동작 원칙 (build_w21.py 준수)
1. **정지=정면**: 걷다가 화면 안에서 멈춰 말할 땐 **반드시 정면(front) 포즈**. 옆으로 선 채 정지 금지. 걷기(측면 사이클)는 이동할 때만.
2. **글자 회피**: 파라메트릭 글자는 캐릭터 **정지 위치의 반대편**에 렌더(빌드가 자동 계산). 캐릭터는 글자 자리에 **서지 않는다**. 단 **걸어서 글자 영역을 지나가는 것은 허용**(정지만 피함).
3. **화면 가로지르기·퇴장**: 매 컷 좌↔우로 크게 이동, 진입 방향 교차(walk_r=왼→오 / walk_l=오른→왼), 일부 컷은 포즈 후 **화면 밖으로 걸어 퇴장**(잠깐 캐릭터 없어도 OK).
4. **창의 포즈 적극 사용**: 현미경 관찰·망원경·노트+펜·의자 앉기·책·돋보기·하늘 가리키기 등 내용에 맞게.
5. 걷기 프레임 10(walk_r1..10 / walk_l1..10), 인사 9(greet1..9). 배경 14 고유(2씬당 1컷).

## 위치·표기
`Z0`=왼끝, `Z50`=중앙, `Z100`=오른끝(캔버스 1280). `Z-8`=왼밖, `Z108`=오른밖, `Z115`=오른퇴장.
표기: **[씬] | 시작Z | 이동(walk Zx→**Zy**) | 정면 포즈들 | (선택)퇴장**. 포즈는 전부 정면.

---

### 컷1 · `alley_entrance` (S1 인사 / S2 주제)
- **S1** | Z-8 | `walk_r` Z-8→**Z68** | `greet`→`smile_bright`→`present_left` |
- **S2** | Z68 | `walk_l` Z68→**Z30** | `count_two`→`explain`→`present_right` → `walk_r` Z30→**Z115**(퇴장)

### 컷2 · `brick_street` (S3 형용사 / S4 키가 크다)
- **S3** | Z-8 | `walk_r` Z-8→**Z66** | `explain`→`hold_book`→`point_up` |
- **S4** | Z66 | `walk_l` Z66→**Z28** | `point_up`→`admire`→`telescope_look` |

### 컷3 · `shoe_street` (S5 키가 작다 / S6 머리가 길다)
- **S5** | Z108 | `walk_l` Z108→**Z30** | `crouch_low`→`smile_bright`→`present_right` |
- **S6** | Z30 | `walk_r` Z30→**Z70** | `present_right`→`admire`→`magnifier_look` → `walk_r` Z70→**Z115**(퇴장)

### 컷4 · `cafe_interior` (S7 머리가 짧다 / S8 예쁘다)
- **S7** | Z-8 | `walk_r` Z-8→**Z66** | `point_left`→`explain`→`hold_book` |
- **S8** | Z66 | `walk_l` Z66→**Z28** | `admire`→`hand_heart`→`smile_bright` |

### 컷5 · `popup_front` (S9 잘생기다 / S10 멋있다)
- **S9** | Z108 | `walk_l` Z108→**Z32** | `point_right`→`thumbs_up`→`present_left` |
- **S10** | Z32 | `walk_r` Z32→**Z72** | `magnifier_look`→`present_right`→`thumbs_up` → `walk_r` Z72→**Z115**(퇴장)

### 컷6 · `forest_path` (S11 날씬·안경 / S12 친절)
- **S11** | Z-8 | `walk_r` Z-8→**Z66** | `slim_gesture`→`push_glasses`→`present_left` |
- **S12** | Z66 | `walk_l` Z66→**Z28** | `hands_together`→`smile_bright`→`nod` |

### 컷7 · `brick_factory` (S13 착하다 / S14 재미있다)
- **S13** | Z108 | `walk_l` Z108→**Z32** | `hand_heart`→`nod`→`present_right` |
- **S14** | Z32 | `walk_r` Z32→**Z70** | `laugh`→`clap`→`cheer_arms` → `walk_r` Z70→**Z115**(퇴장)

### 컷8 · `cafe_terrace` (S15 조용하다 / S16 활발하다)
- **S15** | Z-8 | `walk_r` Z-8→**Z66** | `finger_lips`→`explain`→`present_left` |
- **S16** | Z66 | `walk_l` Z66→**Z28** | `cheer_arms`→`point_up`→`laugh` |

### 컷9 · `understand_ave` (S17 똑똑하다 / S18 '-고' 문법)
- **S17** | Z108 | `walk_l` Z108→**Z32** | `point_head`→`notebook_write`→`explain` |
- **S18** | Z32 | `walk_r` Z32→**Z62** | `connect_hands`→`explain`→`count_two` |

### 컷10 · `popup_inside` (S19 크고 친절 / S20 길고 예뻐)
- **S19** | Z108 | `walk_l` Z108→**Z30** | `present_right`→`hands_together`→`smile_bright` |
- **S20** | Z30 | `walk_r` Z30→**Z70** | `admire`→`hand_heart`→`magnifier_look` → `walk_r` Z70→**Z115**(퇴장)

### 컷11 · `forest_pond` (S21 재미있고 활발 / S22 여러 명)
- **S21** | Z-8 | `walk_r` Z-8→**Z66** | `laugh`→`cheer_arms`→`point_up` |
- **S22** | Z66 | `walk_l` Z66→**Z28** | `microscope_bend`→`point_left`→`point_right` |

### 컷12 · `flower_cafe` (S23 친구 소개 / S24 복습)
- **S23** | Z108 | `walk_l` Z108→**Z32** | `present_right`→`smile_bright`→`hand_heart` |
- **S24** | Z32 | `walk_r` Z32→**Z66** | `sit_explain`→`count_fingers`→`nod` |

### 컷13 · `print_alley` (S25 걸으며 연습)
- **S25** | Z-8 | `walk_r` Z-8→**Z60** | `telescope_look`→`present_right`→`explain` → `walk_r` Z60→**Z115**(퇴장)

### 컷14 · `rooftop` (S26 마무리)
- **S26** | Z108 | `walk_l` Z108→**Z46** | `greet`→`wave` → `walk_r` Z46→**Z115**(퇴장)

---

## 포즈(정면 31 · 살색 싱글라인) — DB mj_w21
표정·제스처: smile_bright · explain · present_right · present_left · point_right · point_left · point_up · count_two · count_fingers · hand_heart · thumbs_up · admire · slim_gesture · push_glasses · hands_together · nod · laugh · clap · finger_lips · cheer_arms · point_head · connect_hands · crouch_low · think · wave
창의 오브젝트: microscope_bend · telescope_look · notebook_write · sit_explain · hold_book · magnifier_look
걷기: walk_r1..10 / walk_l1..10 · 인사: greet1..9

## 배경 (14 고유 · 컷마다 · bg_w21_<key>.png)
컷1 alley_entrance · 컷2 brick_street · 컷3 shoe_street · 컷4 cafe_interior · 컷5 popup_front · 컷6 forest_path · 컷7 brick_factory · 컷8 cafe_terrace · 컷9 understand_ave · 컷10 popup_inside · 컷11 forest_pond · 컷12 flower_cafe · 컷13 print_alley · 컷14 rooftop
