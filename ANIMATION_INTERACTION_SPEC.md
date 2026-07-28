# 애니메이션 상호작용 연출 규격 (W24~)

> **목표: "일어날 수 없지만 상상해 볼 수 있는" 진짜 애니메이션다운 상호작용.**
> 사장님 지시 2026-07-28 (W23 회고에서 나옴). 이제부터 이것이 연출의 중심 목표다.

---

## 1. W23 회고 — 무엇이 아쉬웠나

W23에서 **움직이는 배경 × 움직이는 캐릭터**의 상호작용을 처음 시도했으나 기대에 못 미쳤다.

| 씬 | 의도 | 실제 | 문제 |
|----|------|------|------|
| S6 꽃길 터널 | 날리는 **꽃잎**을 손으로 받는다 | **나뭇잎**을 땄다 | 배경의 소재(꽃)와 캐릭터가 만지는 물체(잎)가 **불일치** |
| S22 회전목마 도착 | 난간을 뛰어넘어 착지 | 점프 | 평범하다. **빗자루를 타고 날아가는** 편이 훨씬 재미있었을 것 |

**교훈**: 상호작용은 "캐릭터가 움직인다 + 배경이 움직인다"로는 부족하다.
**둘이 같은 사물을 두고 주고받아야** 하고, **현실 물리를 벗어난 발상**이 있어야 기억에 남는다.

---

## 2. 앞으로 넣을 연출 4종 (사장님 제시)

### ① 펑 하고 변신 (장면 전환)
캐릭터가 연기·별가루와 함께 **펑** 터지며 다음 장면의 복장·자세로 바뀐다.
장면 전환을 컷 편집이 아니라 **캐릭터의 변신**으로 처리한다.

### ② 빗자루를 타고 이동
걸어가거나 뛰어넘는 대신 **빗자루를 타고 날아** 다른 장소로 간다.
배경 전환과 캐릭터 이동을 한 동작으로 묶는다. (W23 S22 회전목마 도착이 이 케이스였다)

### ③ 그림이 살아나 튀어나온다
칠판·게시판·화면 속에 그려져 있던 **그림이 살아서 튀어나와** 캐릭터 옆에서 함께 논다.
- 후보: 강아지 · 개 · 호랑이 (한국 교재에 자주 나오는 동물)
- 튀어나온 뒤 **캐릭터와 눈을 맞추고 반응**해야 한다. 옆에 서 있기만 하면 실패.

### ④ 배경 소재와 정확히 같은 물체를 주고받기
배경이 꽃밭이면 **꽃잎**, 단풍이면 **단풍잎**, 눈이면 **눈송이**.
배경 프롬프트와 캐릭터 동작 프롬프트에 **같은 명사**를 박아 넣는다.

---

## 3. 제작 규칙

| # | 규칙 |
|---|------|
| R1 | **소재 일치** — 배경 프롬프트의 소재 명사(petal / maple leaf / snowflake)를 캐릭터 동작 프롬프트에 **그대로** 쓴다. 다른 단어를 쓰면 다른 물체가 나온다(W23 꽃잎→나뭇잎 사고) |
| R2 | **한 씬에 상호작용 1개** — 여러 개를 겹치면 무엇을 보라는 건지 흐려진다 |
| R3 | **비현실 동작은 전환부에 배치** — 막이 바뀌는 자리(도착·이동·마무리)에서만. 어휘 설명 중엔 쓰지 않는다 |
| R4 | 튀어나온 캐릭터(동물)는 **반드시 반응**한다 — 시선 교환·따라 하기·놀람 중 하나 이상 |
| R5 | 변신·비행은 **컷랑 프레임컷**으로 만든다. 배경 동영상과 캐릭터가 따로 놀지 않게 **같은 타이밍**으로 자른다 |
| R6 | 방향 원칙(P1~P8, `W23/W23_motion_plan.md`)은 그대로 유지 — 날아가더라도 **화면 중앙을 향해** 난다 |

---

## 4. Veo 프롬프트에 넣을 문구 (초안)

**펑 변신**
> He is enveloped in a puff of white smoke and star sparkles for a moment; when the smoke clears he
> stands in the same spot in a different pose. Cartoon transformation, no morphing of the face.

**빗자루 비행**
> He hops onto a wooden broom and flies off, tilting with the turn, hair and clothes streaming back,
> the ground sweeping past below. Whole body in frame the entire time.

**그림이 튀어나옴**
> A drawing of a puppy on the board glows, peels off the flat surface and pops out into the scene,
> lands beside him with a bounce, looks up at him and wags its tail; he looks back and smiles.

**소재 주고받기 (꽃잎)**
> Cherry blossom **petals** (not leaves) drift down; he reaches out and catches one **petal** on his
> open palm, looks at it, then lets it go.

---

## 5. 관련 문서
- `W23/W23_motion_plan.md` — 방향 원칙 P1~P8 · 검증 게이트
- `VEO_WORKFLOW.md` — Veo/Flow 생성 규격
- `PRODUCTION_PLAYBOOK.md` — 영상 제작 표준 0~8단계
