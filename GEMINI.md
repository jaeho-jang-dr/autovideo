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
- **영상 제작 워크플로우**: Veo 및 Google Flow 기반 비디오 클립 매칭 (자세한 내용은 [VEO_WORKFLOW.md](file:///D:/Entertainments/DevEnvironment/autovideo/VEO_WORKFLOW.md) 참조)
  - 정적 이미지 줌인 효과 연출(Ken Burns)은 **금지**하며, 5~6초 단위 대본마다 생성된 이미지를 Veo를 통해 4~5초 비디오 클립으로 만들고 이들을 합성하여 컴파일합니다.
- **하네스 버전**: 1.0 (생성: 2026-06-11)
- **비디오 오디오 및 렌더링 디폴트 (실수 방지 규칙)**:
  - **동적 폴더 격리:** 특정 프로젝트(예: `chiropractic_science`)의 영상을 제작할 경우, 관련 이미지/모션 비디오 클립/TTS/최종 합본 비디오 등 모든 결과물은 해당 전용 폴더 하위로 격리 저장해야 합니다.
  - **나레이션 속도:** 항상 나레이션 속도를 **1.1배속 (10% 빠르게, `MultiplySpeed(1.1)`)**으로 렌더링해 비디오와 싱크를 맞춥니다.
  - **나레이션 성별:** 명확한 전달력을 위해 항상 gTTS 기본 **여성 음성**을 디폴트로 사용합니다.
  - **캐시 갱신 강제화:** 대본 수정 시 오디오-자막 불일치 방지를 위해 실행 시마다 `assets/audio/scene_*.mp3` 캐시를 무조건 강제 삭제/갱신합니다.
  - **자막 폰트 절대 경로:** 윈도우 환경 한글 자막 깨짐을 막고자 폰트 경로를 **`C:\Windows\Fonts\malgun.ttf`** 절대 경로로 못박아 사용합니다.
  - **Claude CLI 대기 지시:** 백그라운드로 렌더링을 지시할 때 CLI가 조기 종료하여 렌더링 프로세스가 공중 파괴되지 않도록 렌더링 완료까지 대기(Wait)하라는 위임 프롬프트 지시를 강화합니다.
  - **배경 화면 캡처 및 자동 승인 매크로:** Antigravity CLI의 승인 팝업 우회를 위한 매크로(`scratch/auto_approve.py`)는 Windows Session 0 / Sandbox 격리 환경으로 인한 `screen grab failed` 에러를 피하기 위해 Pillow의 **`ImageGrab.grab(all_screens=True)`** 네이티브 API를 사용해야 하며, 블루 계열 버튼 스캔 범위를 넓게 보장해야 합니다.

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
