# 작업 지시 — 감독(Claude) → 조감독(Gemini): 8주차 NotebookLM 산출물

## 컨텍스트
한글교육 초급 **8주차 = "숫자 표현과 날짜, 시간"**(Numbers, Dates & Time).
고유어 숫자(하나~열)와 한자어 숫자(일~십)의 쓰임 구분, 요일(월~일), 시간(시는 고유어·분은 한자어), 날짜 묻고 답하기.
NotebookLM 노트북 id: `cc6092e5-3322-44e8-b65e-dc0e85c2e3ed`. notebooklm-mcp 연결됨.

## 만들 산출물 (8주차 숫자·날짜·시간 주제로)
1. **팟캐스트 2개** (audio): 한국어판 1, 영어판 1. studio_create(artifact_type='audio') 로 주제·언어 명확히.
2. **스터디 리포트 2개**: ① 한국어 report, ② 영어 report. (한국어판 프롬프트도 한국어로.)

## 보고
- 생성한 모든 artifact_id(팟캐스트 ko/en, 리포트 ko/en)와 상태를 `scratch/gemini_w8_report.md` 에 기록.
- 다운로드·PDF·R2·노트는 감독(Claude)이 셸로 처리하니, 너는 아티팩트 생성(MCP)에 집중하고 artifact_id만 남겨라.
- `$env:PYTHONIOENCODING='utf-8'`.

## 작업 디렉터리
`D:\Entertainments\DevEnvironment\autovideo`
