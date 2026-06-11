# autovideo — Claude Code 하네스 컨텍스트

> Claude Code (Opus)의 **행동 계약서**. 작업 위임 시 항상 컨텍스트에 포함됩니다.
> 이 파일은 사람(사용자)만 수정합니다.

---

## 역할 정의
- **Claude Code**: 코드 생성, 명령어 결정, 셸 실행, 에러 자가수정
- **Antigravity (Gemini)**: 고수준 계획, 파일 편집, 판단, 조율
- **사용자**: 의도 설정, 최종 검증, Human Gate 승인

---

## 빠른 참조 맵

| 필요할 때 | 읽을 파일 |
|-----------|-----------|
| 전체 아키텍처 | `.harness/context/architecture.md` |
| 절대 규칙 | `.harness/context/principles.md` |
| 자주 쓰는 패턴 | `.harness/context/patterns.md` |
| 기술 스택 | `.harness/context/stack.md` |
| 표준 작업 루프 | `.harness/loops/task_loop.md` |
| 현재 작업 상태 | `.harness/loops/progress.json` |
| 사람 개입 시점 | `.harness/human/review_gates.md` |

---

## 핵심 명령어

```bash
# 비디오 컴파일 실행
python make_video.py

# 검증 실행 (작업 완료 전 필수 — 2개 모두)
python .harness/verify/check_encoding.py
python .harness/verify/check_links.py
```

---

## 황금 원칙 (위반 절대 금지)

1. **인코딩**: 모든 파일 → UTF-8 without BOM 저장 (PowerShell Set-Content 사용 금지)
2. **대용량 파일**: 비디오(`output*.mp4`, `assets/videos/*.mp4`) 및 오디오(`assets/audio/*.mp3`) 파일 → Git 커밋 절대 금지 (.gitignore 준수)
3. **MoviePy API 버전**: 이 프로젝트 환경에는 **`moviepy==2.2.1`** (2.x 버전)이 설치되어 있습니다. v1.x의 `set_duration()`, `set_audio()`, `set_position()`, `fx(vfx.speedx)` 등은 동작하지 않거나 오류가 날 수 있으므로, 반드시 v2.x의 **`with_duration()`, `with_audio()`, `with_position()`, `with_effects()`** 함수 및 `moviepy.video.fx` 모듈을 사용해야 합니다.
4. **영상 무빙 규칙**: 단순 정적 이미지 줌인 효과(Ken Burns)는 사용이 **금지**됩니다. 비디오 생성 프롬프트 작성 시 단순 무빙을 넘어 3~4초 동안 다른 사물/장면 노출, 다차원 카메라 워킹, 오브젝트/인물 상호작용 등 실제 물리 동작 변화가 일어나도록 프롬프트를 상세하게 작성하십시오. 반드시 Veo 및 Google Flow를 통해 생성된 모션 비디오 클립(`assets/videos/scene_X.mp4`)을 사용하여 영상을 구성해야 합니다. (자세한 규격은 [VEO_WORKFLOW.md](file:///D:/Entertainments/DevEnvironment/autovideo/VEO_WORKFLOW.md) 참조)
5. **콘텐츠 수정**: 대본 데이터(`SCENES` 리스트) 수정 시 원본 의미 손실 방지를 위해 세부 확인 필요.
6. **리소스 삭제**: `assets/images/` 내 이미지 에셋 임의 삭제 금지.
7. **디폴트 렌더링 및 나레이션 규칙**:
   * **속도:** 나레이션 속도는 항상 **10% 빠르게 (1.1배속, `MultiplySpeed(1.1)` 적용)** 렌더링을 구성합니다.
   * **음성:** gTTS 한국어 기본 **여성 음성**을 디폴트로 사용합니다.
   * **캐시 관리:** 대본이 변경되었을 때 자막과의 불일치를 방지하기 위해 렌더링 시 기존 `assets/audio/scene_*.mp3` 캐시를 무조건 강제 삭제(또는 덮어쓰기)해야 합니다.
   * **자막 폰트:** 한국어 자막 깨짐(☒☒☒☒) 방지를 위해 폰트는 반드시 **`C:\Windows\Fonts\malgun.ttf`** 절대 경로를 하드코딩해 사용합니다.

---

## 작업 완료 체크리스트

```
[ ] 테스트 통과
[ ] python .harness/verify/check_encoding.py
[ ] python .harness/verify/check_links.py
[ ] 변경 파일 git diff 확인
[ ] .harness/loops/progress.json 업데이트
[ ] 사용자에게 완료 보고
```

---

## 기술 스택: Python + MoviePy + gTTS
