# 핸드오프: drjay-ed 채널 구축 — Claude Code → Antigravity(Gemini)

> 작성: Claude Code (Opus) / 일시 기준: 2026-06-13 세션
> 목적: 지금까지 Claude가 단독 진행한 drjay-ed 채널·웹사이트 구축 상황을 Antigravity에 인계하고, **이후 작업을 50/50로 분담**한다.
> 참조: [GEMINI.md](./GEMINI.md) · [channel/channel_bible.md](./channel/channel_bible.md) · [channel/ROADMAP.md](./channel/ROADMAP.md)

---

## 🔴 최신 갱신 (2026-06-13): 인트로/아웃트로 완료 → 본편 제작 재개

이 프로시저를 Antigravity(Gemini)에서 다시 시작하기 위한 최신 인계. 아래 0~4를 먼저 읽을 것.

### 0. 지금 상태 (DONE)
- **인트로/아웃트로를 Flow(Veo) 모션 클립으로 새로 제작 완료.**
  - `assets/intro.mp4` = **8초** (`intro_outro/scene_1.mp4` 풀: 책+뇌+바늘/실 컷페이퍼)
  - `assets/outro.mp4` = **8초** (`scene_2` 데스크 4초 + `scene_3` 알림벨 4초)
  - Veo 워터마크는 **우하단 채널 로고로 가림**(크롭 없이 구도 100% 유지), 나레이션 gTTS KR 1.1배속, 자막+페이드.
  - 나레이션은 **영어 채널명을 한글로 읽지 않음**("닥터제이 에드" 금지) — 자연스러운 한국어.
- 재현 스크립트: `make_intro_outro.py` (+ 프롬프트 `intro_outro_prompts.txt`).
- `*.mp4`/`*.mp3` 는 .gitignore — **로컬 보관**(황금원칙 #2). Flow 원본 `intro_outro/scene_1..3.mp4` 는
  재합성 소스이므로 **삭제 금지**(없으면 Flow 재실행 = 크레딧 소모).

### 1. 역할 구분 (재개 시)
- **Antigravity(Gemini)=오케스트레이터**: 어떤 에피소드를 만들지 결정, 대본/프롬프트 초안 편집, 진행 추적·판단.
  실행은 Claude에 위임하되 **결과 검증을 건너뛰지 말 것**(과거 맹목 위임으로 시간 손실).
- **Claude Code(Opus)=실행자**: 코드 작성/수정, 셸 실행, **Flow 자동화·MoviePy 합성·인트로아웃트로**,
  에러 자가수정, **결과를 화면에 띄워 시각 검증**(웹=astro dev+Playwright, 영상=프레임+플레이어).
- **사용자**: 의도 설정, 최종 검증, Human Gate.

### 2. 본편 영상 제작 재개 절차 (Claude가 실행)
```bash
# (1) Flow 로 본편 씬 클립 생성/다운로드 — 하나씩(--scene N), 충분히 대기
python autoveo_flow.py --prompts <에피소드>_prompts.txt --scene 1
#   검증 수치: 이미지 ~40s / 동영상 ~70s, 한 씬 ~2.3분. 성급히 끊지 말 것.
#   다운로드는 '완성 영상 타일(play_circle+포스터, 이미지 왼쪽)'을 잡는다. 자세히는 .harness/skills/autoveo/SKILL.md.

# (2) 본편 합성 + 인트로/아웃트로 앞뒤 부착 (음성 자동 재컴파일)
python make_video.py --scenario <에피소드>.txt --output <에피소드>/<에피소드>.mp4 \
                     --intro assets/intro.mp4 --outro assets/outro.mp4
```
**★ 음성 재컴파일 규칙:** 새 본편을 만들 때마다 `make_video.py` 가 본편 각 씬 음성을 그 영상에 맞게
**자동 재생성+싱크**한다(기존 `assets/audio/scene_*.mp3` 캐시 강제 삭제 → 대본 TTS 새로 생성 → 1.1배속
→ Veo 클립을 나레이션 길이에 배속 싱크). 인트로/아웃트로는 자체 음성 완성품이라 그대로 붙고,
그 음성/문구를 바꾸려면 `make_intro_outro.py` 를 다시 실행한다.

### 3. 사용자 질문 답변
- **Q. Antigravity와 함께 도는 Claude Code CLI도 똑같이 영상을 만들 수 있나?** → **그렇다.**
  모든 작업이 재현 가능한 파이썬 스크립트(`autoveo_flow.py`·`make_intro_outro.py`·`make_video.py`)라,
  같은 환경(Chrome 프로필 로그인 + Playwright + MoviePy 2.x + ffmpeg)에서 동일 명령을 실행하면 동일하게 만든다.
  **핵심은 "Claude가 직접 실행하고 결과를 화면으로 검증"** — Gemini에 맹목 위임하지 않을 때 안정적.
- **Q. 웹사이트를 화면에 띄워놓고 하는 게 더 잘하더라.** → 표준 절차로 고정(아래 4).

### 4. "웹 띄워놓고 작업" 셋팅
- `web/` 미리보기: `cd web && npm run dev` → http://localhost:4321/ (ko `/`, en `/en/`, 레슨 `/lesson/<코드>/`).
- 원칙: 결과는 말로 보고하지 말고 **띄워서 보여줄 것**(웹=Playwright 스크린샷, 영상=플레이어 재생).
- 세션 시작 시 dev 서버 자동 기동: `.claude/settings.json` 의 SessionStart 훅에 설정됨(설정 시).

---

## 1. 한 줄 요약
정형외과 전문의(Dr. Jay)의 TED-Ed형 **이중언어(KR/EN) 지식 채널 `drjay-ed`** 를 구축 중. 정체성·콘텐츠 DB·로드맵은 완료, **웹사이트(Astro) 스캐폴드 직전**에서 인계.

## 2. 사용자/채널 핵심
- **사용자**: 66세 정형외과 전문의 "원장님"(Dr. Jay). 5살부터 만화 기질, 바이크·파크골프 취미. 페르소나 = **"다정한 의사 친구"**.
- **컨셉**: *"의사의 메스로 세상을 해부하고, 만화가의 상상력으로 꿰매다."*
- **벤치마크**: TED-Ed (분석: `.harness/context/ted_ed_benchmark_analysis.md`, 스타일 역공학: `ted_ed_reverse_engineering.md`)

## 3. 확정 사항 (변경 금지)
| 항목 | 값 |
| :--- | :--- |
| 도메인 | **drjayed.com** (Cloudflare 구매완료, moksu.com과 **같은 계정**, 하이픈 없음) |
| 유튜브 핸들 | **@drjay-ed** (`@drjayed`는 선점됨) |
| 브랜드 표기 | **drjay-ed** / 한글 "닥터제이에드" (기존 원형 로고와 일치) |
| 언어 | **한국어 + 영어 이중언어 필수** (모든 영상·사이트) |
| 웹 스택 | **Astro 정적 + Cloudflare Pages** (D1/검색·퀴즈는 후순위) |
| 기존 유튜브 채널 | `@drjay8889 (Drjay 산골목수)` 영상 0개 → **이름·핸들 바꿔 재활용 예정** |

## 4. Claude가 이미 만든 것 (DONE)
- `channel/content_db.py` — SQLite 콘텐츠 DB 매니저(init/seed/stats/list/show/set-status). **이중언어 스키마**, 5축 카테고리(CA/MD/IMP/LM/GEN), **에피소드 24편 시드**(1편 published=메스머, 23편 idea).
- `channel/content.db` — 위 데이터.
- `channel/channel_bible.md` — 정체성·시그니처 인트로/아웃트로·규격 **단일 원천**.
- `channel/ROADMAP.md` — 5단계 플랜 + Cloudflare 아키텍처 + **YouTube 개설법/주의점**.
- `channel/export_web.py` — content.db → `web/src/data/content.json` 익스포터.
- `.harness/context/ted_ed_benchmark_analysis.md` — TED-Ed 정량/운영 분석.
- `.gitignore` — `web/node_modules`·`dist`·`.astro` 추가.

## 5. 환경
- Windows 11 / PowerShell 7 / Python(content_db용) / **Node v22.17.1 · npm 10.9.2**
- GitHub: `https://github.com/jaeho-jang-dr/autovideo` (origin)
- Cloudflare: MCP 연결 확인됨(현재 D1 0개, Worker 0개 — 깨끗). 도메인 drjayed.com 구매완료.

## 6. 진행 중 / 다음 즉시 작업 (NEXT)
- **(중단 지점)** `web/` Astro 사이트 스캐폴드 — 아직 파일 미작성. 계획: content.json 읽어 `/ko`·`/en` 라우팅, 홈→카테고리(5축)→레슨(유튜브 임베드+한/영). GitHub→Cloudflare Pages 자동배포 → drjayed.com 연결.

## 7. 미결 결정 (사용자 판단 필요 — Antigravity 주도)
1. **나레이션 음성**: 본인 육성 / 본인 음성 클론(추천) / gTTS 여성. (영어는 동일 방식의 영어판)
2. **이중언어 산출 형식**: 한/영 분리 영상 2개(추천) / 1영상 다국어 오디오트랙.
3. **상시 스테이션**: 미래 M5 Mac Mini로 24/7 제작 자동화 (현 파이프라인 Windows 전용 → 포팅 필요).

---

## 8. 작업 분담 제안 (50/50)

### 🟦 Antigravity(Gemini) 담당 — 기획·콘텐츠·판단·검수
1. **에피소드 대본 작성** — 우선순위 1편부터(예: CA-001 피터팬, IMP-001 영구기관, LM-004 걷기). **KR/EN 이중언어**, 800~900단어/1,200~1,500자, 의학 렌즈 비유, 채널 바이블의 톤·구조(Hook→본론→통찰) 준수. 결과는 `channel/content_db.py`의 scenes 테이블 또는 대본 파일로.
2. **콘텐츠 캘린더/시리즈 기획** — 24편 백로그 우선순위 조정, 시리즈 묶음.
3. **브랜딩 카피** — 사이트 홈 카피, 유튜브 About, 인트로/아웃트로 최종 문구(한/영).
4. **사용자 판단 대화** — 7절 미결 결정 3가지를 사용자와 확정.
5. **콘텐츠 검수** — Claude가 만든 사이트의 한/영 카피·번역 감수.

### 🟥 Claude Code 담당 — 코드·셸·빌드·배포
1. **web/ Astro 사이트 스캐폴드 + 로컬 빌드 검증** (진행 예정).
2. **content_db 도구 확장** (대본 입력 CLI, 상태 전이 등).
3. **Cloudflare Pages 배포 연결** (GitHub 연동 + drjayed.com).
4. **영상 렌더 파이프라인** (이중언어 TTS·자막·렌더, 기존 make_video.py 확장).
5. **빌드/에러 자가수정**.

### 협업 인터페이스
- 단일 원천 = `channel/content.db` + `channel/channel_bible.md`. 양측 모두 여기에 기준을 둔다.
- Gemini가 대본을 채우면 → Claude가 `export_web.py`로 사이트 반영 + 영상 렌더.
- 상태 동기화: `.harness/loops/progress.json`.

---

## 9. Antigravity가 지금 시작하면 좋은 첫 액션
1. 7절 미결 결정 3가지를 사용자와 확정(특히 음성).
2. **첫 에피소드 1편 선정 후 KR/EN 대본 초안** 작성 → Claude가 사이트·영상에 투입.
3. (병행) Claude는 web/ 스캐폴드를 완성해 drjayed.com에 배포.
