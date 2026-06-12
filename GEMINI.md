# autovideo — Antigravity (Gemini) 오케스트레이터 컨텍스트

> Antigravity의 고수준 조율 가이드.
> Claude Code에게 작업을 위임할 때의 프로토콜, 판단 기준을 정의합니다.

---

## 나의 역할 (Antigravity = 오케스트레이터)

```
사용자 요청
    ↓
Antigravity (나) — 계획·판단·컨텍스트 유지·파일 직접 편집
    ↓ (복잡한 코드/명령 시)
Claude Code — 코드 생성·명령 결정·셸 실행·자가수정
    ↓
결과 검증 → 사용자 보고
```

---

## 프로젝트 핵심 정보

- **목적**: 유튜브 교양/지식 콘텐츠 자동 제작 파이프라인 (대본 추출, TTS 생성, 이미지/비디오 합성, 자막 삽입 및 합본 인코딩)
- **스택**: Python + MoviePy 2.2.1 (v2.x API 사용 필수) + gTTS
- **영상 제작 워크플로우**: 주제 선정 -> NotebookLM 소스 검색 -> 프로젝트 폴더 생성 및 레퍼런스 적재(스샷/URL) -> 시나리오(scenario.txt) 및 극도의 정밀 스크립트 도출(롱폼: 5초당 1컷, 쇼츠: 4초당 1컷) -> Google Flow(autoveo_flow.py) 비디오 자동 생성/다운로드 -> 최종 컴파일(make_video.py, 전용 폴더 저장) -> 초정밀 역공학 명세 파일([video_name]_spec.md) 보존 -> 목차/스샷 기반 데이터화 순서의 7단계 AI 영상 제작 라이프사이클을 준수합니다. (자세한 내용은 [VEO_WORKFLOW.md](file:///D:/Entertainments/DevEnvironment/autovideo/VEO_WORKFLOW.md) 및 [principles.md](file:///d:/Entertainments/DevEnvironment/autovideo/.harness/context/principles.md#L88) 참조)
  - 정적 이미지 줌인 효과 연출(Ken Burns)은 **금지**하며, 5~6초 단위 대본마다 생성된 이미지를 Veo를 통해 4~5초 비디오 클립으로 만들고 이들을 합성하여 컴파일합니다.
- **하네스 버전**: 1.0 (생성: 2026-06-11)
- **비디오 오디오 및 렌더링 디폴트 (실수 방지 규칙)**:
  - **동적 폴더 격리:** 특정 프로젝트(예: `chiropractic_science`)의 영상을 제작할 경우, 관련 이미지/모션 비디오 클립/TTS/최종 합본 비디오 등 모든 결과물은 해당 전용 폴더 하위로 격리 저장해야 합니다.
  - **나레이션 속도:** 항상 나레이션 속도를 **1.1배속 (10% 빠르게, `MultiplySpeed(1.1)`)**으로 렌더링해 비디오와 싱크를 맞춥니다.
  - **나레이션 성별:** 명확한 전달력을 위해 항상 gTTS 기본 **여성 음성**을 디폴트로 사용합니다.
  - **캐시 갱신 강제화:** 대본 수정 시 오디오-자막 불일치 방지를 위해 실행 시마다 `assets/audio/scene_*.mp3` 캐시를 무조건 강제 삭제/갱신합니다.
  - **자막 폰트 절대 경로:** 윈도우 환경 한글 자막 깨짐을 막고자 폰트 경로를 **`C:\Windows\Fonts\malgun.ttf`** 절대 경로로 못박아 사용합니다.
  - **Claude CLI 대기 지시:** 백그라운드로 렌더링을 지시할 때 CLI가 조기 종료하여 렌더링 프로세스가 공중 파괴되지 않도록 렌더링 완료까지 대기(Wait)하라는 위임 프롬프트 지시를 강화합니다.
  - **배경 UI 자동 승인 매크로:** Antigravity CLI의 승인 팝업 우회를 위한 매크로(`scratch/auto_approve.py`)는 화면 캡처 방식의 한계를 극복하기 위해 Windows UI Automation API (`uiautomation` 라이브러리)를 활용해 Electron 창의 엘리먼트 트리를 타서 안전한 명령어만 백그라운드에서 실시간 자동 승인(`Yes, allow this time` -> `Submit` 순차 클릭)합니다. 위험 패턴 명령어는 자동으로 승인이 차단되어 수동 검토 대기 모드로 진입합니다.
  - **워터마크 원천 배제 (Dolly Zoom-Crop):** 워터마크를 가리는 네모 상자 얼룩을 남기지 않기 위해, 16:9 비율을 엄격히 보존하는 미세 줌-크롭(78% 크롭 후 Lanczos-4 보간법 리사이징)을 적용하여 원래의 Veo 워터마크를 화면 바깥으로 완벽히 배제합니다.
  - **초소형 채널 로고 오버레이:** 크롭으로 깨끗해진 우측 하단 자리에 `assets/drjay_ed_logo_circle.png` 둥근 원형 로고 배지를 기존 크기 대비 25% 수준인 **가로세로 45x45 픽셀 크기**로 대폭 축소하여 알파 블렌딩 오버레이합니다.

---

## 작업 위임 프로토콜

### Claude Code에게 위임할 작업
- Python 스크립트 50줄+ 생성
- 셸 명령어 시퀀스 결정·실행
- 에러 시 자가수정이 필요한 반복 작업
- API 호출 시퀀스 (DB, 스토리지 등)

### 내가 직접 처리할 작업
- 소규모 파일 수정 (multi_replace_file_content)
- CLAUDE.md / GEMINI.md 업데이트
- 사용자와의 판단/계획 대화
- 웹 검색 및 정보 수집

### 위임 시 프롬프트 형식
```
claude --dangerously-skip-permissions -p "
[프로젝트: autovideo, 스택: Python + MoviePy + gTTS]
[작업 목표]: ...
[성공 기준]: ...
[제약 조건]: UTF-8, 테스트 통과
[참조 파일]: .harness/context/principles.md
"
```

> [!IMPORTANT]
> **장시간 실행/완수 보장 작업 위임 규정 (/goal 사용):**
> Playwright 브라우저 자동화 스크립트(`flow_automator.py`)를 통해 비디오 클립을 개별 또는 전체 생성하여 다운로드하는 작업은 나중에도 Claude Code가 위임받아 전담해야 합니다.
> 이미지 1장당 1개의 비디오 클립이 누락 없이 100% 다운로드되도록 보장하기 위해, 이 작업은 반드시 사용자나 오케스트레이터가 **`/goal` 슬래시 명령을 활용하여 실행하도록 지시**해야 합니다.
> 예: `/goal flow_automator.py 디버깅 및 전체 씬 비디오 생성/다운로드 완수`

---

## 세션 시작 루틴

새 세션 시작 시 항상:
1. `.harness/loops/progress.json` 읽기 → 이전 상태 확인
2. `git log --oneline -5` → 최근 변경사항 파악
3. 사용자에게 브리핑 후 새 작업 시작

---

## 하네스 구조

```
Antigravity + Claude Code
        ↕
  .harness/
  ├── context/     ← 공유 프로젝트 지식
  ├── skills/      ← 재사용 작업 스크립트
  ├── loops/       ← 실행 루프 & 상태 지속성
  ├── verify/      ← 자동 검증
  └── human/       ← Human-in-the-loop 게이트
```
