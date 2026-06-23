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

## ★ 검증된 최선의 방법 (2026-06-17, 사용자 확정 — 제미나이가 영상제작을 위임하면 Claude는 반드시 이대로)
1. **단일 연속 세션**: `python autoveo_flow.py --prompts <project>_prompts.txt` 를 **딱 한 번** 통째로 실행한다.
   창 하나에서 프로젝트를 옮겨가며 이미 만든 씬은 자동 스킵(`progress_scenes.json` + 파일 존재). 실패해도 **같은 명령 재실행**하면 done 스킵·미완만 재시도.
   → **씬마다 `--scene N` 으로 쪼개 chrome 를 죽이고 새로 띄우지 말 것**: 창이 떴다 닫혔다 깜빡이고 생성 중 조기 종료를 부른다(사용자가 명시적으로 싫어함).
2. **프롬프트 입력 = 클립보드 붙여넣기(Ctrl+V)**: Flow 입력창은 Slate.js 라 `execCommand('insertText')` 는 DOM만 바꾸고 내부 모델 갱신에 실패 →
   "만들기" 버튼이 `aria-disabled=true` 로 **영구 비활성** → 이미지 0장 → **무한 재시도(과거 루프의 진짜 원인)**. **버튼 비활성 = 프롬프트 미등록이지 한도(quota) 아님.**
   `set_os_clipboard()` + Ctrl+V 로 Slate paste 핸들러가 모델을 갱신해 버튼이 활성화된다(코드 반영됨: `fill_prompt`).
3. **출력 폴더 = prompts 파일명으로 결정**: autoveo 는 basename 에서 `_prompts` 를 떼 OUT_DIR 을 정한다 → prompts 파일명을 **`<project>_prompts.txt`** 로 둬야 클립이 `<project>/` 로 직접 저장된다.
   → **generic `prompts_for_veo.txt` 금지**: 여러 프로젝트가 공용 `prompts_for_veo/` 에 섞여 오염된다(실사고: pet_family 0~19 클립이 korean_education 0~19 로 새어 들어가 영상이 잘못 만들어짐).
4. **죽이지 말고 기다려라**: 씬당 ~2.3분(이미지 ~40s, 영상 ~70s+다운로드). 일시 결함(다운로드 실패·브라우저 크래시)은 재실행으로 복구된다.

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

## ★ 한 씬씩 확실히 만드는 검증된 수동 레시피 → [SCENE_RECIPE.md](./SCENE_RECIPE.md)
autoveo_flow.py 자동화가 봇 감지/다운로드 타일 오인으로 막힐 때, `flow_driver.py`로 화면 보며
한 단계씩(이미지 모드→이미지 생성→다시시도→애니메이션→영상→왼쪽 타일 다운로드) 따라하면 확실하다.
**Claude Code CLI는 이 레시피를 그대로 재현**할 수 있다. binge scene 1·2·3 엔드투엔드 검증(2026-06-13).

## 검증된 운영 수치 & 다운로드 핵심 (2026-06-13 실측, 프로젝트 내내 적용)
- **이미지 ~40초**(Nano Banana 2, 0크레딧) · **동영상 ~70초**(Veo 8s). 부하 시 더 걸리므로
  이미지 대기는 **넉넉히(최대 ~10분)** — 과거 145초로 끊어 *생성 진행 중인 걸 죽이고* 다음 씬으로
  성급히 넘어간 게 실패 원인이었다. 한 씬 전체 사이클(이미지→애니메이션→영상→다운로드) ≈ **2.3분**.
- **다운로드 타일 선택 = 가장 중요한 함정.** 결과 캔버스에서 **동영상 타일은 이미지 타일의 "왼쪽"**
  (최신=좌측)에 생긴다. 그러나 *좌측 포스터를 무작정 받으면* 아직 렌더링 중일 때 **정지 이미지의
  JPEG 포스터**를 받아 무한 "아직 렌더링 중"에 빠진다(과거 4분+ 헛돎). → 반드시 **완성 영상 타일
  (`play_circle` 오버레이 + 실제 media 포스터 img)** 을 `VIDEO_DONE_JS`로 찾아, 그 타일의 ⋮ →
  `다운로드` → `720p 원본 크기`. 저장 파일 헤더가 `ftyp`(MP4)인지 검증하고 아니면 재시도.
- **autoveo_flow.py 반영분:** `wait_image(timeout=600)` + 8초 간격 로그, 영상 최소대기 65초,
  `try_download_video()`(VIDEO_DONE_JS 사용; 좌측-포스터 버그 폐기). 한 번에 **하나씩** `--scene N`.
- **★ 죽이지 말고 화면을 봐라 (반복 금지):** 다운로드가 안 된다고 **프로세스/chrome을 죽이지 말 것.**
  Flow 영상은 **클라우드(대시보드/프로젝트)에 저장**되므로 생성만 끝났으면 다운로드 실패는 복구 가능하다.
  죽이면 완성된 화면만 날린다. 순서: ① **스크린샷부터 찍어 화면을 직접 본다(추측 금지)** →
  ② **완성 영상 타일 = 결과 캔버스에서 이미지의 "왼쪽"**(`play_circle`+포스터) → ③ 호버→⋮→다운로드→720p 원본.
  안 보이면 대시보드로 돌아가 그 영상 썸네일을 다시 연다. 라이브 복구는 `flow_driver.py`로 화면 보며 조작.
- **프로필 락:** 실행 사이엔 `assets\chrome_profile`를 쓰는 chrome를 모두 종료하고
  `assets\chrome_profile\SingletonLock`을 삭제. 드라이버(autoveo/flow_driver)를 동시에 두 개 띄우지 말 것.
- **출력 네이밍:** `--prompts intro_outro_prompts.txt` → `intro_outro/scene_N.mp4`
  (`_prompts` 접미사 제거한 폴더명).

## 설계 원칙 / 제약
- **No API / No Extension**: `labs.google/fx/tools/flow` 웹 UI + 계정 OAuth만 사용.
- **이미지 생성도 Flow 안에서**(Nano Banana 2, 0크레딧) — 별도 이미지 API/CLI 불필요.
  (참고: `gemini` CLI는 이미지 파일 생성 기능이 없고, 이 머신의 `GEMINI_API_KEY`는 만료됨.)
- 다운로드 기본 포맷 = **720p 원본 MP4**. 기본 클립 길이 = **8초**(이후 make_video에서 배속 싱크 가능).
- 한 장면 = 한 새 프로젝트(타일 모호성 제거). 출력 존재 시 스킵(`--force`로 재생성).
- 영상 합본/자막/TTS 등 후속 렌더링은 기존 `make_video*.py` 파이프라인을 따른다.
- 프로필 잠금 주의: 같은 `chrome_profile`을 쓰는 크롬/드라이버가 이미 떠 있으면 실행 실패.
  잔류 프로세스와 `SingletonLock`/`lockfile`을 정리 후 재시도.
