# 거북목 쇼츠 9:16 클립 생성 일임 (Google Flow 순환계정)

감독(Claude) → 조감독(제미나이). 아래를 **네가 전적으로 맡아서** 끝까지 완성하라.

## 목표
`turtle_short_v916_prompts.txt` 의 5개 씬을 **전부 9:16 세로 동영상 클립**으로 만든다.
- 이미 완성: scene_1.mp4, scene_3.mp4 (turtle_short_v916/ 폴더, 720x1280 확인됨) → 건드리지 말 것
- **만들 것: scene_2, scene_4, scene_5** (현재 없음)
- ★반드시 **9:16 (720x1280 세로)**. 아까 scene_2가 16:9로 잘못 나왔으니 aspect 9:16 확실히 적용할 것.

## 방법 (네가 만든 순환 시스템)
- `python autoveo_flow.py --prompts turtle_short_v916_prompts.txt --profiles-count 6 --aspect 9:16`
  (또는 확실히 로그인된 프로필로 `--profile-idx 1`)
- ⚠️ 프로필 2,4,5는 로그인이 약해 "프로젝트 진입 실패" 남 → 로그인된 프로필(0,1) 위주로.
- ⚠️ 오래 걸리니 **너의 async 환경에서 detached로 돌려** 완료까지 지켜라. 정적 이미지 fallback이 잡히면 재시도.
- 결과 검증: 각 scene_N.mp4 가 mp4 헤더(ftyp) + 720x1280 인지 확인.

## 완료 후
scene_2,4,5 (9:16) 저장되면 감독(Claude)에게 알려라. 그러면 감독이 5클립 연결 + 영어 나레이션/자막 + 썸네일로 마무리한다.
