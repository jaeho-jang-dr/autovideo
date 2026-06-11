# 표준 작업 루프 프로토콜

## 하네스 실행 루프

```
[사용자 요청]
     ↓
[1] RESEARCH  — Antigravity: 현재 상태 파악
     ↓
[2] PLAN      — Antigravity: 작업 계획 수립
     ↓
[3] EXECUTE   — Claude Code: 코드 생성 + 실행
     ↓
[4] VERIFY    — 자동 검증 스크립트 실행
     ↓
[5] GATE?     — Human Gate 필요 여부 판단
     ↓
[6] REPORT    — 사용자에게 결과 보고
```

---

## 단계별 상세

### [1] RESEARCH
- `.harness/loops/progress.json` 읽기
- `git log --oneline -5` 실행
- 관련 파일 상태 확인

### [2] PLAN
- WIP = 1 원칙: 한 번에 하나씩
- Claude Code 위임 여부 결정 (50줄+ → 위임)
- Human Gate 필요 여부 판단

### [3] EXECUTE (Claude Code)
```
위임 프롬프트 형식:
━━━━━━━━━━━━━━━━━━━━━━━━
작업 목표: [한 문장]
성공 기준: [측정 가능]
제약: UTF-8, 테스트 통과
참조: .harness/context/principles.md
━━━━━━━━━━━━━━━━━━━━━━━━

에러 처리:
  1회 실패 → 자동 재시도
  2회 실패 → Antigravity에게 보고
```

### [4] VERIFY
```bash
python .harness/verify/check_encoding.py
python .harness/verify/check_links.py
```

### [5] GATE
```
Gate #1: 비가역적 작업 → 사용자 승인
Gate #2: 배포 → 사용자 최종 확인
Gate #3: 대규모 삭제 → 계획 제시 후 승인
Gate #4: .env 변경 → 사용자 직접 수정
Gate #5: 연속 에러 → 즉시 중단·보고
```

### [6] REPORT
```
✅ 완료: [요약]
📁 변경: [파일 목록]
🔍 검증: [통과/실패]
📝 다음: [있다면]

+ progress.json 업데이트
```
