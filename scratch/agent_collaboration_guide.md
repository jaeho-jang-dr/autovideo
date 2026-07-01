# Claude-Gemini 자동 협업 통신 프로토콜 가이드 (Protocol Guide)
이 문서는 사용자의 불필요한 개입 없이 Claude(감독)와 Gemini(조감독)가 터미널 CLI 연쇄 기동을 통해 스스로 상호작용하는 자동화 흐름 및 파일 기반 신호 프로토콜을 규정합니다.

---

## 1. 개요 및 통신 아키텍처

```
 [Claude (감독)]
     │
     ▼ (gemini_task.md 작성/수정)
 [agent_chain_runner.py (모니터)] ─── (변경 감지 시 gemini CLI 기동) ───▶ [Gemini (조감독)]
     ▲                                                                        │
     └──────── (변경 감지 시 claude CLI 기동) ─── (gemini_report.md 작성) ◄────┘
```

* **체인 모니터**: `scratch/agent_chain_runner.py`가 두 인터페이스 파일의 mtime(수정 시간)을 실시간 감시합니다.
* **자동 승인**: `scratch/auto_approve.py`가 백그라운드에서 Antigravity의 실행 승인 단계를 무인 통과(Yes -> Submit)시킵니다.

---

## 2. 파일 및 상태 제어 규약

### 1) 지시 파일: `scratch/gemini_task.md`
* **역할**: Claude가 Gemini에게 위임할 상세 코드 변경, CLI 명령어 실행 요구사항을 기재합니다.
* **상태 제어 규칙**:
  * 태스크가 유효할 때는 일반 내용을 적습니다.
  * 작업을 중단하거나 완료했음을 체인 러너에게 알릴 때는 파일 내에 `[STATUS] STOP` 혹은 `[STATUS] DONE` 문자열을 포함시켜야 합니다. (이 경우 체인 러너가 기동을 건너뜁니다.)

### 2) 보고 파일: `scratch/gemini_report.md`
* **역할**: Gemini가 지시받은 태스크를 수행한 후, 수정된 코드 차이(Diff)와 테스트 로그 등을 요약하여 작성합니다.
* **상태 제어 규칙**:
  * 수행이 성공하여 검수를 요청할 때는 수행 결과를 적습니다.
  * 치명적 실패, 3회 연속 타임아웃, 혹은 사용자의 즉각적 개입이 필요한 예외가 발생할 경우 `[STATUS] STOP` 또는 `[STATUS] ERROR`를 파일 내에 기재합니다. (이 경우 체인이 멈추고 사용자의 수동 개입을 대기합니다.)

---

## 3. 에이전트 행동 지침 (프롬프트 내재화)

### Claude (감독)의 행동 지침
1. 조감독에게 작업을 넘길 때는 반드시 `scratch/gemini_task.md`를 신규 작성하거나 갱신하여 지시 사항을 명시하십시오.
2. 검수 완료 후 최종 결과물이 완벽하다면, 무한 체인을 막기 위해 `scratch/gemini_task.md` 에 `[STATUS] DONE`을 기록하고 작업을 완료하십시오.

### Gemini (조감독)의 행동 지침
1. `scratch/gemini_task.md` 가 변경되어 강제 기동되면, 해당 파일의 지시 사항을 엄격히 해독하여 실행하십시오.
2. 작업 수행 후 반드시 `scratch/gemini_report.md`에 결과를 간결하게 기록하십시오.
3. 에러 발생 시 예외 사항을 보고서에 적고 `[STATUS] STOP` 태그를 달아 사용자 터미널을 잠그고 정지하십시오.

---

## 4. 모니터링 및 프로세스 제어 명령어

사용자는 아래 스크립트를 통해 에이전트 간의 자동 통신 환경을 통제할 수 있습니다.

* **자동 협업 시작 (백그라운드)**:
  ```powershell
  ./scratch/start_auto_collaboration.ps1
  ```
* **자동 협업 중단 및 프로세스 정리**:
  ```powershell
  ./scratch/stop_auto_collaboration.ps1
  ```
* **통신 모니터 로그 확인**:
  ```powershell
  Get-Content -Path scratch/agent_chain_runner.log -Wait
  ```
