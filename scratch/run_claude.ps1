$p = @"
[프로젝트: autovideo, 스택: Python + MoviePy + gTTS]
[작업 목표]: /goal autoveo_flow.py를 실행하여 turtle_neck_science/turtle_neck_science_prompts.txt 내의 모든 28개 씬 비디오 클립을 구글 Flow를 제어해서 100% 생성하고 다운로드 완료해줘.
[성공 기준]: turtle_neck_science/ 디렉토리 내에 scene_0.mp4 ~ scene_27.mp4 가 누락 없이 100% 저장되는 것.
[제약 조건]:
- 만약 실행 도중 구글 로그인 화면(계정 선택, 패스워드 등)이 감지되면, 너(Claude Code)가 직접 셸에서 또는 Playwright 상에서 요소 클릭을 수행하거나, 혹은 필요시 사용자에게 비밀번호를 물어보는 프롬프트를 띄워서 적극적으로 세션을 획득하여 로그인을 돌파해야 함. (사용자 프로필은 assets/chrome_profile을 사용).
- 이미지 생성 시 최소 40초, 비디오 생성 시 최소 80초 대기 룰 및 실패 시 삭제 후 재시도 등의 룰 준수.
- 3회 연속 실패 시 브라우저 종료 후 5초 대기 후 재기동(Reboot)할 것.
- 씬별로 성공 여부를 turtle_neck_science/progress_scenes.json 에 영구 기록하여, 성공한 씬은 증분으로 스킵하고 실패/미생성된 씬만 타겟팅하여 재생성할 것.
[참조 파일]: .harness/context/principles.md
"@
claude --dangerously-skip-permissions -p $p
