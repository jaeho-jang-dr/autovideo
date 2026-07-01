You have the `notebooklm-mcp` server. Use it to AUTOMATE creating a Korean podcast + slide deck for a Korean-language lesson, then DOWNLOAD both to local files. Execute all steps with the MCP tools (you are in --yolo, auto-approve). Poll async generation until ready.

STEPS (do them in order, actually calling the tools):
1. `notebook_create` with name: "drjayed 1-6 한국어".
2. `source_add` to that notebook, source_type='text', title "세종대왕과 한글 이야기", with this exact content:
---
세종대왕과 한글 이야기 (한국어 강의)

안녕하세요! 오늘은 한국 사람들이 매일 쓰는 특별한 글자, 한글이 어떻게 태어났는지 이야기를 들려드릴게요.
한글을 만든 분은 조선의 네 번째 임금, 세종대왕이에요. 세종대왕은 누구보다 백성을 사랑하는 따뜻한 마음을 가진 왕이었답니다.
그 시절 백성들은 어려운 한자를 써야 했어요. 글자가 너무 복잡해서 대부분의 백성은 글을 읽지도 쓰지도 못했지요.
글을 몰라 억울한 일을 당해도 하소연조차 못 하고, 백성들의 생활은 무척 힘들었어요. 세종대왕은 이런 백성들을 보며 마음 아파했답니다.
'백성 누구나 쉽게 배울 수 있는, 우리만의 글자가 필요하다!' 세종대왕은 직접 새 글자를 만들기로 결심했어요.
세종대왕은 집현전의 젊고 똑똑한 학자들과 함께 밤낮으로 소리와 글자를 연구했어요.
많은 신하들의 반대에도 불구하고, 세종대왕은 백성을 위해 끝까지 포기하지 않았답니다.
마침내 만들어진 한글은 정말 과학적이에요. 모음은 하늘과 땅과 사람, 바로 '천지인'을 본떠 만들었어요. '·'는 하늘을, 'ㅡ'는 땅을, 'ㅣ'는 사람을 뜻해요.
자음은 입술, 혀, 목구멍 같은 발음 기관의 모양을 본떠 만들었어요.
1446년, 세종대왕은 이 글자를 '훈민정음'이라는 이름으로 온 백성에게 반포했어요. '백성을 가르치는 바른 소리'라는 뜻이랍니다.
세종대왕은 측우기, 해시계, 물시계 같은 과학 기구도 만들고, 음악과 농사, 국방까지 백성을 위해 힘썼답니다.
오늘 우리가 한국어를 이렇게 쉽고 빠르게 배울 수 있는 것도 모두 세종대왕 덕분이에요.
---
3. `studio_create` an AUDIO overview (podcast) in KOREAN for this notebook. (Korean language audio.)
4. `studio_create` a SLIDE_DECK in KOREAN for this notebook.
5. Poll `studio_status` for BOTH artifacts until they are READY (this may take several minutes — keep polling).
6. `download_artifact` the AUDIO to: D:/Entertainments/DevEnvironment/autovideo/scratch/nlm/hangeul_w1d6_podcast.m4a
7. `download_artifact` the SLIDE_DECK as PDF (slide_deck_format='pdf') to: D:/Entertainments/DevEnvironment/autovideo/web/public/docs/hangeul_w1d6_slides.pdf
8. At the very end, print a final line exactly like: `RESULT audio=<path or FAIL> slides=<path or FAIL>` and the notebook id.

Do not ask me questions; just execute and report. If a tool needs auth, try `refresh_auth` first.
