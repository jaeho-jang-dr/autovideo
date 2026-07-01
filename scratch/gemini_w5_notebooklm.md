# 작업 지시 — 감독(Claude) → 조감독(Gemini): 5주차 NotebookLM 산출물

## 컨텍스트
한글교육 초급 **5주차 = "이중모음과 반모음 활주"**(Double Vowels & Semivowel Glides).
단모음의 결합으로 만들어지는 이중모음(야 여 요 유 와 워 위 외 의 얘 예)과 반모음 활주(y-활음 ㅣ계, w-활음 ㅗ/ㅜ계) 조음 원리.
NotebookLM 노트북 id: `cc6092e5-3322-44e8-b65e-dc0e85c2e3ed` (한글교육, 74소스). notebooklm-mcp 연결됨.

## 만들 산출물 (5주차 이중모음·반모음활주 주제로)
1. **팟캐스트 2개** (audio): 한국어판 1, 영어판 1. `studio_create(artifact_type='audio', ...)` 로 주제·언어를 명확히 지정.
2. **스터디 리포트 2개**: **반드시 언어를 분리** — ① 한국어로 작성된 report, ② 영어로 작성된 report. (지난 4주차 때 둘 다 영어로 만든 실수 반복 금지. 한국어판은 프롬프트도 한국어로.)
3. **핵심 요약 노트 영/한**: `web/public/docs/hangeul_week_5_notes_ko.md`, `hangeul_week_5_notes_en.md` (write_file 로 직접 작성).

## 보고
- 생성한 모든 artifact_id(팟캐스트 ko/en, 리포트 ko/en)와 상태를 `scratch/gemini_w5_report.md` 에 기록.
- **다운로드·PDF변환·R2업로드는 셸이 필요해 너(헤드리스)는 막힐 수 있다. 그 부분은 감독(Claude)이 처리하니, 너는 ① 아티팩트 생성(MCP)과 ② 노트 md 작성(write_file)에 집중**하고 artifact_id만 정확히 남겨라.
- 막히면 그 사실을 report에 적어라. `$env:PYTHONIOENCODING='utf-8'`.

## 작업 디렉터리
`D:\Entertainments\DevEnvironment\autovideo`
