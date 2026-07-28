# W23 모션 블로킹 v3 (인준 · 에버랜드) — 방향 우선 재배치

> **v3 변경점 (2026-07-28)**
> 1. **방향 원칙 P1~P8 전면 적용** — 캐릭터는 언제나 화면 중앙을 향한다. 반대 방향 포즈는 `_flip` 사용.
> 2. **실물 없는 토큰 5개 교체** — `wave`→`greet_wave` · `open_arms`→`catch_petal` · `phone_call`→`spin_phone`
>    · `write_note`→`board_write` · `handshake`→`jump_highfive`
> 3. **동작컷 12종 전원 배정** — 미배정이던 `backflip_land` `onehand_freeze` `railing_vault` `run_slide_in`
>    까지 넣고, 씬당 동작 2개 연결을 허용했다. `windmill_up`은 다리 3개로 **폐기**.
> 4. 걷기 뒤에는 반드시 정지 포즈(정면/3-4)를 붙여 **측면으로 서 있는 상태를 없앴다**(P7).
>
> **표기**: `- **S<n>** <시작Z> | 비트 나열` — 비트는 백틱 토큰. `walk_r`/`walk_l` 뒤에는 `Z<시작> → **Z<도착>**`.
> 포즈 뒤 괄호는 방향 문서화용(`F` 정면 / `→` 오른쪽 뻗음 / `←` 왼쪽 뻗음) — 파서는 무시한다.
> `※` 는 배경 앵커 상호작용 메모.
>
> **좌표계**: `z2x(z) = z/100 × 1280`. 화면 밖 왼쪽 **Z-20**(x=-256) / 오른쪽 **Z120**(x=1536).
> 말하는 위치는 **Z30**(x=384 · 글자 오른쪽) / **Z66**(x=845 · 글자 왼쪽) **두 곳만**.
> **걷기** `WALK_STRIDE_SEC=0.75` · 한 스트라이드 **250px**(실측). **규격** `injun_w23` 1024x1280 ·
> 발끝 1209 · 몸높이 770 → `CHAR_SCALE 0.561`, `CHAR_CX/CY = 640/345`.

---

## 0. 방향 규칙 (자산 실측 기반)

| 위치 | 향해야 할 쪽 | 그대로 쓰는 포즈 | `_flip` 으로 뒤집어 쓰는 포즈 |
|------|--------------|------------------|-------------------------------|
| **Z30** (왼편) | → 오른쪽(중앙) | `present_right` `point_board` `hand_on_post` `lean_rail` | `explain_flip` `present_left_flip` `tap_board_flip` `count_three_flip` `thumbs_up_flip` `raising_hand_flip` |
| **Z66** (오른편) | ← 왼쪽(중앙) | `explain` `present_left` `tap_board` `count_three` `thumbs_up` `raising_hand` | `hand_on_post_flip` `lean_rail_flip` `point_board_flip` `present_right_flip` |

중립(양쪽 가능): `bow` `hard_smile` `invite_hand` `lean_bench` `nod_agree` `phone_calendar`

동작컷 이동 방향: `run_slide_in` 만 실이동(왼→오른 +430px) → **왼쪽 밖에서 시작**.
나머지는 제자리·좌우대칭이라 양쪽 배치 가능(합성 단계에서 x 이동으로 연출).

---

## 1. 씬 블로킹 36

- **S1** Z-20 | `run_slide_in` Z-20 → **Z30** `greet_wave`(F)  ※ 정문 아치를 통과하며 왼쪽 밖에서 달려 들어와 멈춰 서서 크게 인사 (배경 동영상)
- **S2** Z66 | `hand_on_post_flip`(←) `count_three`(F)  ※ 안내 지도판 왼쪽 모서리에 손 짚음
- **S3** Z30 | `lean_rail`(→) `explain_flip`(→)  ※ 화단 돌난간에 팔 기대고 꽃밭 쪽(중앙)을 봄
- **S4** Z66 | `point_board_flip`(←) `explain`(←)  ※ 안내 지도판을 손끝으로 짚어 가리킴
- **S5** Z120 | `walk_l` Z120 → **Z30** `count_three_flip`(→) `lean_rail`(→)  ※ 돌난간에 팔 얹고 마무리
- **S6** Z66 | `catch_petal`(F) `present_left`(←)  ※ 꽃길 터널 도착, 날리는 꽃잎을 손으로 받아 중앙으로 내밈 (배경 동영상)
- **S7** Z30 | `hand_on_post`(→) `explain_flip`(→)  ※ 가로등 기둥에 손 짚음
- **S8** Z-20 | `walk_r` Z-20 → **Z66** `lean_bench`(F) `present_left`(←)  ※ 나무 벤치 등받이에 손 얹음
- **S9** Z30 | `hand_on_post`(→) `phone_calendar`(F)  ※ 아치 벽돌 기둥에 손 짚고 달력 확인
- **S10** Z66 | `invite_hand`(F) `present_left`(←)  ※ 화분대 너머로 중앙을 향해 손짓해 부름
- **S11** Z30 | `tap_board_flip`(→) `raising_hand_flip`(→)  ※ 벽 달력보드를 손끝으로 두드림
- **S12** Z120 | `walk_l` Z120 → **Z66** `hand_on_post_flip`(←) `explain`(←)  ※ 파라솔 기둥에 손 짚음
- **S13** Z30 | `point_board`(→) `nod_agree`(F)  ※ 달력보드의 한 칸을 짚어 가리킴
- **S14** Z-20 | `walk_r` Z-20 → **Z66** `lean_back_surprise`(F) `explain`(←)  ※ 코앞으로 달려드는 열차에 상체를 젖혔다 되돌아와 설명 (배경 동영상)
- **S15** Z30 | `lean_rail`(→) `explain_flip`(→)  ※ 관람 난간에 팔 기대고
- **S16** Z66 | `hand_on_post_flip`(←) `explain`(←)  ※ 목재 지지 기둥에 손 짚고 조심스레
- **S17** Z30 | `lean_rail`(→) `backflip_land`(F)  ※ 데크 난간에 팔 걸치고 판다 쪽을 보다가, 가볍게 뒤로 돌아 착지 — "천천히"의 반전 강조
- **S18** Z66 | `spin_phone`(←) `nod_agree`(F)  ※ 대나무 기둥에 등을 기댄 채 폰을 돌려 쥐고 통화
- **S19** Z30 | `thumbs_up_flip`(→) `lean_rail`(→)  ※ 난간에 팔 얹고 여유롭게
- **S20** Z120 | `walk_l` Z120 → **Z66** `lean_bench`(F) `hard_smile`(F)  ※ 피크닉 테이블에 손 얹고 미안한 미소
- **S21** Z30 | `hand_on_post`(→) `nod_agree`(F)  ※ 큰 나무 줄기에 손 짚고
- **S22** Z-20 | `walk_r` Z-20 → **Z30** `railing_vault`(F) `point_far_follow`(F)  ※ 난간을 짚고 뛰어넘어 착지하자마자 팔을 뻗어 회전목마를 가리키며 시선이 회전을 따라감 (배경 동영상)
- **S23** Z30 | `lean_rail`(→) `explain_flip`(→)  ※ 회전목마 울타리에 손 얹고
- **S24** Z66 | `point_board_flip`(←) `explain`(←)  ※ 광장 안내판의 정문 위치를 짚어 가리킴
- **S25** Z30 | `invite_hand`(F) `present_right`(→)  ※ 울타리 너머로 중앙을 향해 손 내밀어 권함
- **S26** Z66 | `board_write`(←)  ※ 매표소 난간에 수첩을 얹고 적음 — **노트 들고 정면 보는 마지막 컷이 끝 포즈**(뒤따르던 `nod_agree` 제거, 사장님 교정 2026-07-28)
- **S27** Z30 | `jump_highfive`(F) `thumbs_up_flip`(→)  ※ 잔디 경계 돌턱 앞에서 뛰어올라 손뼉 맞장구 — 확정의 환호
- **S28** Z66 | `lean_rail_flip`(←) `phone_calendar`(F)  ※ 매표소 난간에 손 얹고 예약 확인
- **S29** Z30 | `follow_parade`(F) `onehand_freeze`(F)  ※ 밀려드는 행렬을 눈·손으로 좇다가 한 손으로 몸을 지탱해 정지 — 퍼레이드의 흥 (배경 동영상)
- **S30** Z66 | `hand_on_post_flip`(←) `present_left`(←)  ※ 화분대에 손 짚고
- **S31** Z30 | `lean_rail`(→) `count_three_flip`(→)  ※ 거리 펜스에 팔 기대고 손가락으로 셈
- **S32** Z66 | `lean_bench`(F) `nod_agree`(F)  ※ 벤치 등받이에 손 얹고
- **S33** Z30 | `lean_rail`(→) `present_right`(→)  ※ 분수 테두리 돌턱에 손 짚고 중앙을 향해 내밈
- **S34** Z66 | `hand_on_post_flip`(←) `explain`(←)  ※ 석조 기둥에 손 짚고
- **S35** Z30 | `tap_board_flip`(→) `check_ok`(F)  ※ 큰 게시판을 두드리며 빈칸 확인, 좋다는 손짓
- **S36** Z-20 | `walk_r` Z-20 → **Z66** `greet_wave`(F) `bow`(F) `walk_r` Z66 → **Z120**  ※ 불꽃을 올려다보며 인사하고 절한 뒤 오른쪽으로 퇴장 (배경 동영상)

---

## 2. 동작컷 사용 점검 (12종 전원 배정 — 지시 준수)

| 클립 | 씬 | 비고 |
|------|-----|------|
| `run_slide_in` | S1 | 유일한 실이동 클립 — 왼쪽 밖 진입 |
| `greet_wave` | S1 S36 | 등장·퇴장 인사 |
| `catch_petal` | S6 | 꽃길 도착 |
| `lean_back_surprise` | S14 | 코스터 배경 상호작용 |
| `backflip_land` | S17 | "천천히"의 반전 |
| `spin_phone` | S18 | 통화 |
| `railing_vault` | S22 | 난간 넘어 회전목마 도착 |
| `point_far_follow` | S22 | 회전목마 가리킴 |
| `board_write` | S26 | 수첩 적기 |
| `jump_highfive` | S27 | 확정 환호 |
| `follow_parade` | S29 | 퍼레이드 좇기 |
| `onehand_freeze` | S29 | 퍼레이드 정지 포즈 |
| `check_ok` | S35 | 복습 확인 |
| ~~`windmill_up`~~ | — | **폐기(다리 3개)** |

정지 포즈 16종 전원 사용 · 좌향 `_flip` 10종 DB 등록 완료 · 걷기 `walk_r` 5회 / `walk_l` 3회.
