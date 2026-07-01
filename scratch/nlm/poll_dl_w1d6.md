Use notebooklm-mcp on notebook id "6edfe103-763d-4049-bdc0-327926437436".
Artifacts: audio id "efd35a18-e070-46e6-9f2a-a8bbe74e2a6d", slide_deck id "70fd650c-f2ab-47bf-87ec-cae3c62b01a5".
1. Call studio_status. If an artifact is still in_progress, that's fine — report it.
2. For each artifact that is READY/completed, download_artifact:
   - audio  -> D:/Entertainments/DevEnvironment/autovideo/scratch/nlm/hangeul_w1d6_podcast.m4a
   - slide_deck (slide_deck_format='pdf') -> D:/Entertainments/DevEnvironment/autovideo/scratch/nlm/hangeul_w1d6_slides.pdf
3. Print final line: STATUS audio=<ready|in_progress|FAIL path-if-downloaded> slides=<...>
