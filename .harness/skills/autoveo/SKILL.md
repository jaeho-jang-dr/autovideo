---
name: autoveo
description: Generate motion video clips from a scenario in Google Flow (labs.google/fx/tools/flow) via Playwright over the logged-in Chrome profile — text→image (Nano Banana) → animate→video (Veo) → download → merge. Account login only; NO API keys, NO browser extension.
---

# AutoVeo — Google Flow 동영상 클립 자동 생성/다운로드

대본(장면 프롬프트)을 받아 **Google Flow** 웹에서 ① 텍스트→이미지 생성 →
② 이미지→동영상(애니메이션 적용) → ③ 다운로드 → ④ 합치기까지 **100% 브라우저
GUI 자동화**로 수행합니다. 로그인된 크롬 프로필(`assets/chrome_profile`)의
**계정 세션만** 사용하며, **API 키·유료 확장 프로그램을 일절 쓰지 않습니다.**

> 검증 완료(2026-06-12): 회중시계·마술사 2개 장면을 이미지 생성→영상화→다운로드
> →합치기까지 엔드투엔드로 성공. 각 클립 8초 1280×720 24fps, 합본 16초.

## 전제 조건
- 로컬 **Google Chrome** 설치 + Google 계정으로 Flow 로그인 (세션이
  `assets/chrome_profile`에 저장됨. 최초 1회만 수동 로그인).
- `pip install playwright` + `playwright`가 import 가능 (이 환경: 1.58).
- 계정에 Flow 크레딧(이미지=0크레딧, 동영상=클립당 크레딧 소모). 이 환경은 **ULTRA**.

## 실행 방법

### A. 자율 실행 (권장) — `autoveo_flow.py`
프롬프트 파일은 한 줄당 한 장면, `이미지프롬프트 :: 모션프롬프트` 형식:
```
[Scene 1] A glowing pocket watch ... No watermark, no text. :: The watch swings, camera pushes into the spiral ...
[Scene 2] A cartoon magician ... :: The magician taps the hat, a rabbit pops out ...
```
```bash
python autoveo_flow.py --prompts test_scene.txt          # 전체 장면
python autoveo_flow.py --prompts test_scene.txt --scene 1 # 한 장면
python autoveo_flow.py --prompts test_scene.txt --force    # 기존 mp4 무시하고 재생성
```
- 결과: `assets/videos/scene_<N>.mp4` (없으면 자동 스킵; 다운로드 전 대상 폴더 미리 생성).
- 장면마다 **새 프로젝트**를 열어 최신(맨 왼쪽) 타일이 항상 그 장면의 영상이 되게 함.

### B. 합치기 — `merge_clips.py`
```bash
python merge_clips.py output.mp4 assets/videos/scene_1.mp4 assets/videos/scene_2.mp4 ...
```

### C. 라이브 수동 조작/디버깅 — `flow_driver.py`
브라우저를 **계속 열어둔 채** 명령파일로 한 단계씩 조작(화면 보며 검증용).
`python flow_driver.py`로 띄운 뒤 `debug/cmd/<n>.txt`에 명령을 적으면 순서대로 실행되고
`debug/_live.png`(스크린샷)·`debug/_live.json`(요소 덤프)·`debug/_drv.log`가 갱신됨.
명령: `clicktext|텍스트|ymin`, `clickxy|x|y`, `hover|x|y`, `fillprompt|텍스트`,
`key|Escape`, `wait|초`, `imgstatus`, `vidstatus`, `dlvideo|절대경로(슬래시)`, `quit`.

## Flow Omni 에디터 조작 레시피 (유지보수용)
2026년 ko-KR 기준. UI가 바뀌면 `flow_driver.py`로 재탐색해 갱신할 것.

1. **에이전트 토글**: 하단 입력창의 `에이전트` 알약은 토글. 표준 모델 칩이 안 보이면
   Agent 모드 → `에이전트`를 한 번 눌러 끄면 표준 입력창(모델 칩) 복귀.
2. **모델 메뉴**: 모델 칩(예: `🍌 Nano Banana 2 · 16:9 · 1x` 또는 `동영상 · 8s · ...`)을
   클릭하면 메뉴가 열림 → 탭 `이미지`/`동영상`, 화면비(`16:9` 등), 개수(`1x` 등), 모델.
3. **이미지 생성**: 이미지 탭 + 16:9 + 1x + Nano Banana 2 → 프롬프트 입력 →
   `만들기`(아이콘 `arrow_forward`) → ~35-40초.
4. **이미지→동영상**: 생성된 이미지 타일에 **마우스 호버** → 우상단 `⋮ 더 생성하기`
   메뉴 → **`애니메이션 적용`**. 이미지가 동영상 **첫 번째 프레임**으로 들어가고
   모드가 `동영상 · 8s`로 전환됨 → 모션 프롬프트 입력 → `만들기`.
5. **완료 판정(중요)**: 동영상은 이미지보다 오래 걸리며, 렌더링 중에도 타일은
   첫 프레임 포스터를 보여줘 DOM만으로는 완료를 오판하기 쉬움. **가장 확실한 신호는
   다운로드 결과의 파일 헤더**다 — 렌더링 중엔 `원본 크기`가 JPEG 포스터를, 완료되면
   진짜 MP4(`ftyp`)를 준다. 엔진은 최소 대기 후 **다운로드→헤더검증→실패시 재시도**한다.
   (수동 확인 시: 타일을 클릭하면 `<video>` 플레이어 + `완료` 배지가 뜨면 완료.)
6. **다운로드**: 결과 타일 호버 → `⋮` → `다운로드` → **`720p 원본 크기`** (서브메뉴.
   `270p GIF`/`1080p 업스케일`/`4K(유료)`도 있음). 다운로드 전 대상 폴더를 미리 생성.

## 설계 원칙 / 제약
- **No API / No Extension**: `labs.google/fx/tools/flow` 웹 UI + 계정 OAuth만 사용.
- **이미지 생성도 Flow 안에서**(Nano Banana 2, 0크레딧) — 별도 이미지 API/CLI 불필요.
  (참고: `gemini` CLI는 이미지 파일 생성 기능이 없고, 이 머신의 `GEMINI_API_KEY`는 만료됨.)
- 다운로드 기본 포맷 = **720p 원본 MP4**. 기본 클립 길이 = **8초**(이후 make_video에서 배속 싱크 가능).
- 한 장면 = 한 새 프로젝트(타일 모호성 제거). 출력 존재 시 스킵(`--force`로 재생성).
- 영상 합본/자막/TTS 등 후속 렌더링은 기존 `make_video*.py` 파이프라인을 따른다.
- 프로필 잠금 주의: 같은 `chrome_profile`을 쓰는 크롬/드라이버가 이미 떠 있으면 실행 실패.
  잔류 프로세스와 `SingletonLock`/`lockfile`을 정리 후 재시도.
