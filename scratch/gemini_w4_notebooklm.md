# 작업 지시 — 감독(Claude) → 조감독(Gemini): 4주차 NotebookLM 산출물

## 컨텍스트
한글교육 초급 **4주차 = "받침과 대표 7음"**(받침의 구조 + 모든 받침이 ㄱㄴㄷㄹㅁㅂㅇ 7개 대표음으로 발음되는 규칙. 예: 부엌→[부억], 꽃→[꼳], 앞→[압]).
NotebookLM 노트북 id: `cc6092e5-3322-44e8-b65e-dc0e85c2e3ed` (한글교육, 74소스).
NotebookLM MCP/클라이언트는 이미 연결돼 있다(notebooklm-mcp). 다운로드는 **async(await 필수)** — `asyncio.run(c.download_audio/​download_video(...))`. (이미 검증된 패턴: download_en_podcasts.py 참고)

## 만들 산출물 (4주차 받침/대표7음 주제로)
1. **팟캐스트 2개** (audio): 한국어판 1, 영어판 1. `studio_create(artifact_type='audio', ...)` 주제·언어 지정.
2. **PDF 2개**: 스터디 리포트를 한국어 1, 영어 1. report 아티팩트(.md) 생성→`markdown`으로 HTML→`chrome --headless --print-to-pdf` 변환(메모리의 PDF 방식).
3. **노트 영/한**: 핵심 요약 노트를 한국어/영어 각각(.md 또는 .txt).

## 다운로드 & 배치
- 팟캐스트(.m4a): 용량 크므로 `scratch/web_media_offloaded/audio/podcasts/` 에 저장 + R2(`drjayed-media`) 키 `audio/podcasts/hangeul_week_4_podcast_{ko,en}.m4a` 업로드(boto3, 키=../parkgolftour/.env CF_R2_*; download_en_podcasts.py의 r2_client() 재사용).
- PDF: `web/public/docs/hangeul_week_4_guide_{ko,en}.pdf`
- 노트: `web/public/docs/hangeul_week_4_notes_{ko,en}.md`

## 절대 규칙
- 4주차 **영상/시나리오 소스는 건드리지 말 것**(그건 감독이 별도로 한다). 너는 NotebookLM 산출물만.
- 진행/결과를 `scratch/gemini_w4_report.md` 에 기록(생성한 artifact_id, 다운로드 경로, R2 키, 에러).
- 막히면(노트북 소스 부족 등) 그 사실을 report에 적고 가능한 데까지 진행.
- `$env:PYTHONIOENCODING='utf-8'`.

## 작업 디렉터리
`D:\Entertainments\DevEnvironment\autovideo`
