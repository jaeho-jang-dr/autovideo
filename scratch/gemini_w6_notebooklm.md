# 작업 지시 — 감독(Claude) → 조감독(Gemini): 6주차 NotebookLM 산출물

## 컨텍스트
한글교육 초급 **6주차 = "자연스러운 연음과 음운 변동"**(Liaison & Sound Rules).
받침이 다음 'ㅇ' 자리로 넘어가 소리 나는 연음(음악→[으막], 옷이→[오시], 꽃이→[꼬치]), ㅎ 약화(좋아요→[조아요]), 표기형 vs 발음형.
NotebookLM 노트북 id: `cc6092e5-3322-44e8-b65e-dc0e85c2e3ed`. notebooklm-mcp 연결됨.

## 만들 산출물 (6주차 연음·음운변동 주제로)
1. **팟캐스트 2개** (audio): 한국어판 1, 영어판 1. `studio_create(artifact_type='audio', ...)` 주제·언어 명확히 지정.
2. **스터디 리포트 2개**: ① 한국어 report, ② 영어 report. (한국어판은 프롬프트도 한국어로.)

## 보고
- 생성한 모든 artifact_id(팟캐스트 ko/en, 리포트 ko/en)와 상태를 `scratch/gemini_w6_report.md` 에 기록.
- **다운로드·PDF변환·R2업로드·노트작성은 감독(Claude)이 셸로 처리**하니, 너는 ① 아티팩트 생성(MCP)에 집중하고 artifact_id만 정확히 남겨라.
- 막히면 그 사실을 report에 적어라. `$env:PYTHONIOENCODING='utf-8'`.

## 작업 디렉터리
`D:\Entertainments\DevEnvironment\autovideo`
