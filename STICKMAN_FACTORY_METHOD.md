# 스틱맨 포즈 라이브러리 제작법 — 재현용 매뉴얼

> 레퍼런스(크림 배경 검은 잉크 라인아트 스틱맨 설명 영상) 스타일의 포즈를
> **파라메트릭 Python 생성기**로 무한 생성하는 검증된 방법. 작성: 감독(Claude).
> 철학: 메모리 `feedback-flat-layered-method`(플랫 레이어드·왜곡0·완전제어)와 정합.

---

## 1. 왜 AI 생성이 아니라 파라메트릭인가
- 스틱맨은 12관절 + 베지어 사지 + 둥근 머리(표정)로 **완전히 수식화**된다.
- AI(Flow/Nano Banana) 생성은 포즈마다 스타일이 흔들리고(머리 크기·선 굵기·얼굴)
  왜곡 위험이 있다. 파라메트릭은 **모든 포즈가 픽셀 단위로 일관**, 즉시 재생성,
  표정/facing 파라미터화, 24주 전체 재사용.

## 2. 도구 — `stickman_factory.py` (프로젝트 루트)
- 모델: `stickman_svg_editor` 의 12점 + 큐빅 베지어(`M p0 C p0, mid, end`)를 PIL로 재현.
  - 점: head, chest, body, pelvis, (elbow/hand)L·R, (knee/feet)L·R — 60×80 좌표계.
  - 사지 = 두꺼운 둥근 잉크 스탬프(미세 사인 흔들림 = 손그림 느낌), 머리 = 빈 원(ring).
  - 표정 expr: neutral / happy / sad / talk(=o입) / tired / surprised. facing: front/left/right.
  - 2x 슈퍼샘플 → 1024² 투명 PNG. 출력: `assets/graphics/poses/stickman_<name>.png`.
- 실행:
  ```bash
  python stickman_factory.py            # POSES 전체 생성 + _manifest.json
  python stickman_factory.py thinking   # 특정 포즈만
  ```
- **새 포즈 추가**: `POSES` 딕셔너리에 `P(elbowRight=(x,y), handRight=(x,y), ...)` 한 줄.
  좌표 감각: x=30 중앙, y=20 어깨/y=41 골반, 위로 갈수록 y 작아짐.

## 3. DB 등록 — `register_poses.py`
- `_manifest.json` 을 읽어 `content.db` `assets` 테이블에 upsert(멱등).
  - type='character', file_path='assets/graphics/poses/stickman_<name>.png',
    name_kr=한글 설명, flow_prompt=생성 방식+expr/facing.
  - 기존 stickman 포즈 행 삭제 후 재삽입 → 포즈 다시 뽑고 재실행하면 DB 동기화.
- 실행: `python register_poses.py`

## 4. 현재 라이브러리 (30포즈)
- 일상/범용: standing, standing_happy, greeting_wave, arms_open, cheer, clap,
  pointing_(right/left/up/down), thinking, shrug, thumbs_up, hands_on_hips,
  raising_hand, walking, running, jumping, sitting, tired_slump, holding_phone,
  presenting, writing, reading, bowing, listening.
- 영상 전용(한글 탄생·단모음): sejong, mouth_demo, holding_mirror, point_self.
- 소품(시계·책·거울·휴대폰·칠판·왕관·곤룡포·라디오 등)은 포즈 PNG에 포함하지 않고
  **장면 합성 시 별도 오브젝트 레이어**로 올린다(레퍼런스와 동일 분리). 기존
  `assets/graphics/obj_*.png` 및 `letters/` 재사용.

## 5. 함정 / 팁
- 표정 입모양 부호: happy=U(가운데 아래), sad=∩(가운데 위). `arc_mouth(smile +/-)`.
- 좌우 팔 대칭 확인은 알파 칼럼 분석(중심 기준 좌/우 폭). 썸네일 육안은 오인하기 쉽다.
- 한 장면에 같은 포즈가 여러 번이면 seed 를 바꿔 흔들림 패턴을 달리해 복붙 티를 없앤다.
