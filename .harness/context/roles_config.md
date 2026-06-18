# AutoVideo AI Roles Configurations & History

본 문서는 오토비디오 프로젝트에서 개발을 진행하는 두 인공지능(Claude, Gemini)의 역할 구성(Role Configurations) 및 히스토리를 기록하여, 향후 역할이 유동적으로 바뀔 때 빠른 참조 및 세팅 전환을 가능하게 하기 위해 작성되었습니다.

---

## 1. 현재 활성 역할 모드 (Active Configuration)
> **모드 명칭**: **Claude-Led Director Mode (클로드 감독 모드)**
> **활성 일자**: 2026-06-18 ~ 현재

```
제작자 (사용자) — 기획 및 승인, 요구사항 정의
    ↓
감독 (Claude Code) — 고수준 설계 및 전체 조율, 조감독에게 직접 지시
    ↓
조감독 (Antigravity / Gemini) — 감독 지시 수령, 파일 편집 및 세부 실행, 진행 보고
```

### 1) 상세 분담 역할
*   **감독 (Claude Code / Opus)**:
    *   대본 기획, 이미지/동영상 연출 프롬프트 설계, 전체 아키텍처 조율.
    *   오류 발생 시 디버깅 방향 수립 및 조감독에게 구체적인 수정/실행 태스크 하달.
    *   `scratch/gemini_task.md`를 통해 조감독에게 상세 지시사항 전달.
*   **조감독 (Antigravity / Gemini)**:
    *   Playwright 브라우저 GUI 자동화(`autoveo_flow.py`, `flow_automator.py`) 직접 실행 및 실시간 모니터링/수동 승인.
    *   `make_video.py`, `finalize.py` 컴파일러 구동 및 동적 캐시 삭제/갱신 등 기계적 수행.
    *   작업 완료 후 결과 리포트(`scratch/gemini_report.md`, `walkthrough.md`)를 작성하여 감독에게 보고.
    *   프로젝트 전반의 지식 맵(`CLAUDE.md`, `GEMINI.md`, 에셋 카탈로그 등) 관리.

---

## 2. 과거/대안 역할 모드 (Alternative Configurations)

### 모드 A: Gemini-Led Orchestrator Mode (제미나이 조율자 모드)
> **사용 일자**: 2026-06-11 ~ 2026-06-17

```
사용자 요청
    ↓
오케스트레이터 (Antigravity / Gemini) — 계획·판단·컨텍스트 유지·파일 직접 편집
    ↓ (복잡한 작업 시 위임)
작업자 (Claude Code) — 코드 생성·명령 결정·셸 실행·자가수정
```
*   **주요 특징**:
    *   Gemini가 최상위 조율자로서 프로젝트 전체 흐름과 컨텍스트를 주도적으로 통제하고 계획을 설계함.
    *   Claude는 로컬 셸 실행 및 대량 코드 작성, 자가 수정을 위한 기능적 Subagent/Worker로서 활용됨.
    *   조율자(Gemini)가 `claude -p` 명령어 파라미터를 통해 클로드에게 비대화형(non-interactive)으로 명령 시퀀스를 지시하여 처리하게 함.

---

## 3. 역할 전환 시 세팅 체크리스트

역할이 바뀔 경우 다음 파일을 해당 모드의 프로토콜에 맞추어 즉시 갱신해야 합니다.
1.  **[GEMINI.md](file:///D:/Entertainments/DevEnvironment/autovideo/GEMINI.md)**: `## 나의 역할` 및 `## 하이브리드 파이프라인 조율 역할 정의` 섹션 갱신.
2.  **[CLAUDE.md](file:///D:/Entertainments/DevEnvironment/autovideo/CLAUDE.md)**: `## 역할 정의` 섹션 갱신.
3.  **컨텍스트 공유 파일**: `scratch/gemini_task.md` 및 `scratch/gemini_report.md` 사용 여부 설정.
