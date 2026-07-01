너는 조감독(Gemini)이다. notebooklm-mcp의 download_artifact 도구로 아래 4개 아티팩트를 정확히 다운로드하라. 먼저 refresh_auth() 호출.

notebook_id = cc6092e5-3322-44e8-b65e-dc0e85c2e3ed

1) artifact_id=d9ee3e54-6de9-4cb0-9cb5-287fc7b94baf  type=audio  → D:/Entertainments/DevEnvironment/autovideo/web/public/audio/podcasts/hangeul_week_1_podcast.m4a
2) artifact_id=35b45563-3803-4e02-ba87-955123818a84  type=audio  → D:/Entertainments/DevEnvironment/autovideo/web/public/audio/podcasts/hangeul_week_2_podcast.m4a
3) artifact_id=13092d99-f697-4f45-9125-032d371988bf  type=video  → D:/Entertainments/DevEnvironment/autovideo/web/public/docs/hangeul_week_1_video.mp4
4) artifact_id=1e8bde1c-358f-4ba5-89d3-b908077d1789  type=video  → D:/Entertainments/DevEnvironment/autovideo/web/public/docs/hangeul_week_2_video.mp4

각 파일 다운로드 후 크기를 확인하고, 결과를 scratch/gemini_report.md 에 (파일경로+크기) 기록하라. 완료하면 "DOWNLOADS DONE" 출력.
