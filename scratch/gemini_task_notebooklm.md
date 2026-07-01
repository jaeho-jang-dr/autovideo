너는 한글 교육 영상 프로젝트의 조감독(Gemini)이다. `notebooklm-mcp` 서버를 사용한다. 인증이 방금 갱신되었으니 **먼저 `refresh_auth()`를 호출**해서 새 쿠키를 반영하라.

# 대상 노트북 (확정)
- notebook_id: `cc6092e5-3322-44e8-b65e-dc0e85c2e3ed`
- 제목: "한글 교육: 자음과 모음의 과학적 원리 및 발음법" (소스 74개)

# 목표
이 노트북에서 **초급 1주차(한글의 탄생과 단모음)** 와 **초급 2주차(기초 자음과 모아쓰기)** 두 주제에 대해 학습 자료를 생성·다운로드해서 웹 폴더에 넣는다. 자료 4종: ① 팟캐스트(audio) ② AI 동영상(video) ③ 스터디 가이드(report) ④ 노트(note).

# 절차
1. `refresh_auth()` 호출 → `notebook_list()` 또는 `notebook_get('cc6092e5-3322-44e8-b65e-dc0e85c2e3ed')` 로 접근 확인.
2. 각 주제별로 `studio_create()` 로 생성 (한국어 우선). focus 프롬프트 예:
   - 1주차 audio: "한글의 탄생 배경과 천지인 창제원리, 단모음 8개(ㅏㅓㅗㅜㅡㅣㅐㅔ)의 소릿값과 입모양을 초급 외국인 학습자에게 강의체로 설명"
   - 1주차 report: report_format="Study Guide", 같은 주제
   - 2주차 audio: "한글 기초 자음 10개(ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎ)의 발음기관 상형 원리와 모아쓰기(초성+중성) 구조, 받침 없는 단어 읽기를 강의체로 설명"
   - 2주차 report: report_format="Study Guide", 같은 주제
   - video: video_format="explainer", visual_style="whiteboard" 권장
   - note: 핵심 요약 노트
   - 팟캐스트 강의체는 1인/여성 선호.
3. 생성은 비동기다. `studio_status()` 로 완료를 확인하고, 완료분을 `download_artifact()` 로 받는다. (오디오는 보통 2~5분, 비디오는 5~10분 소요. in_progress면 status와 artifact id를 기록만 하고 넘어가라.)
4. 다운로드 파일을 아래 경로/이름으로 저장:
   - 팟캐스트: `D:/Entertainments/DevEnvironment/autovideo/web/public/audio/podcasts/hangeul_week_1_podcast.m4a`, `hangeul_week_2_podcast.m4a`
   - PDF/가이드: `D:/Entertainments/DevEnvironment/autovideo/web/public/docs/hangeul_week_1_guide.pdf` (PDF 안 되면 .md), `hangeul_week_2_guide.pdf`
   - 영상: `D:/Entertainments/DevEnvironment/autovideo/web/public/docs/hangeul_week_1_video.mp4`, `hangeul_week_2_video.mp4`
   - 노트: `D:/Entertainments/DevEnvironment/autovideo/web/public/docs/hangeul_week_1_notes.md`, `hangeul_week_2_notes.md`

# 보고 (필수)
`D:/Entertainments/DevEnvironment/autovideo/scratch/gemini_report.md` 에:
- refresh_auth 결과 / 노트북 접근 성공 여부
- 생성한 artifact 목록(type, artifact_id, status=완료/진행중)
- 다운로드 완료한 파일 경로·크기
- 아직 in_progress 라서 못 받은 것은 artifact_id 와 함께 "나중에 download_artifact 로 받을 것" 으로 명시
- 막힌 부분이 있으면 정확한 오류

추측으로 가짜 파일을 만들지 마라. 실제 결과만 보고. 완료하면 "REPORT WRITTEN" 한 줄 출력.
