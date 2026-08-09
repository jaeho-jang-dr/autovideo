# 다국어 교육영상 표준 제작 플레이북 (세종대왕과 한글 방식)

> 확정 표준. 이 순서를 그대로 따르면 어떤 주제든 동일 품질의 **다국어(1영상·5자막·5나레이션) 교육영상**을 만든다.
> 핵심 철학: **Gemini Notebook 딥리서치로 근거 확보 → 스팟 이미지(키프레임) 확정 → 거기서만 최소 모션(Veo) → 한 영상에 다국어**.
> 왜 스팟 이미지 방식? AI 풀생성은 왜곡·한글 깨짐·통제불가 → 정지 이미지를 먼저 확정하고 움직임만 입혀 **구도·인물·정확성 완전 제어**.
> 왜 한 영상? 관리 1회 + 4K 업스케일 1회.

---

## 0단계 · 자료·근거 (Gemini Notebook Deep Research)  ★앞부분
> 자료·아티팩트는 **Gemini Notebook이 자기 소스로** 만든다(내가 요약한 글을 떠먹이지 않는다 = 1주차 실패). nlm CLI(`~/AppData/Roaming/Python/Python313/Scripts/nlm`).
```bash
nlm notebook create "세종대왕과 한글 창제"          # 노트북 생성
nlm alias set sejong <notebook_id>
nlm research start --mode deep --auto-import --notebook sejong "훈민정음 창제 관련 모든 소스 …"   # ★deep research로 소스 자동수집
# (선택) 6아티팩트: nlm audio/slides/report create --notebook sejong --language ko|en --confirm
nlm download report --notebook sejong --out scratch/nlm/sejong/   # 리서치 결과 파일
```
- 산출: `scratch/nlm/<proj>/` 딥리서치 자료 → **1단계 시나리오의 근거**. 상세 [[nlm-slides-podcast-method]] · [[project-sejong-special-edition]].

## 1단계 · 시나리오·스크립트 (노트북 자료 기반)
- ★★ **분량 계획(제일 먼저)**: **목표 길이 ÷ 클립길이 = 필요 클립(=키프레임) 수.**
  - Flow/Veo 클립은 이제 **최대 10초** 지원(예전 8초). **10초 기준** 권장(클립을 덜 슬로우해서 자연스러움).
  - 예: **16분 = 960초 → 10초 클립 96개** (8초면 120개). (처음 48개는 너무 적었음 → 과도 슬로우·변화부족.)
  - 목표 분량 먼저 정하고 **샷 수를 그에 맞춰**(10초 기준 ≈ 분당 6샷) 시나리오를 잘게 쪼갠다.
- 0단계 딥리서치 자료를 참고해 **시나리오 + 샷 스크립트** 작성(내가 지어내지 않음).
- 톤: 다정한 이야기꾼·아이 친화·쉬운 말(TED-Ed 벤치마크). 무거운 소재는 덜어냄.
- **하이브리드**: 🎬실사(역사·현실) + ✏️애니(기억·개념·감정) 교차.
- 형식(`sejong_master_shotscript_48.md`): `**S## · 🎬/✏️(char) · S/M/L · →전환**` + `🎥 camera [visual]` + `- KO:` / `- EN:`. **사람 승인 후 진행.**

## 2단계 · 키프레임 = 샷당 스팟 이미지 1장 (Flow)
- 각 샷 키프레임을 **Google Flow(Nano Banana 이미지)** 로 생성. `gen_assets_flow.py --prompts <file> --outdir <dir> --no-transparent --yes --force [--aspect 9:16]` (레퍼런스 변형은 `--ref-jobs`, 1잡=1세션 독립).
- 실사=cinematic semi-realistic painterly / 애니=flat webtoon. 현대요소→조선시대 재생성(시대고증).
- ⚠️ AI는 정확한 한글을 못 그림 → **글자 중요한 장면은 빈 공간으로 생성 후 자모를 직접 오버레이**.

## 3단계 · 동영상 클립 = 스팟→모션 (Veo)
- ★★★ **클립 생성 전 필수 가드**: **먼저 Flow AI 크레딧 잔량을 확인**하고 **필요량을 계산**한다. `필요 크레딧 = 클립 수 × 클립당 크레딧`(Veo Fast ≈ 12·10, Lite ≈ 10, Quality = 100). **부족하면 생성 시작 금지** → 모델을 Fast/Lite로 낮추거나 충전 후 진행. (이전에 크레딧 소진으로 생산이 중단된 적 있음. 잔량은 Flow UI 프롬프트박스 우상단 설정/계정 크레딧에서 확인.)
- ★★ **크레딧 절약 대안(우선 고려)**: Veo 모션 클립은 **크레딧이 비싸다**. 많은 장면은 **이미지만 생성(싼 이미지 크레딧) + 파라메트릭 오토메이션 드로잉**(코드로 그리기·움직이기)으로 대체하면 크게 절약된다. 예: 스틱맨 팩토리(12관절 파라메트릭 [[stickman-factory-method]]), 한글 획순 오토드로우([[feedback-hangeul-stroke-order]]), PIL/moviepy 프로그래매틱 모션(플랫 레이어드 [[feedback-flat-layered-method]]). **Veo는 꼭 필요한 실사·복잡 모션에만** 쓰고 나머지는 파라메트릭으로.
- 각 키프레임을 **Flow(Veo)에 업로드 → "애니메이션 적용" → 최대 10초 모션 클립(1280×720)**. `autoveo_flow.py --prompts <name>_prompts.txt --scene N --upload <kf> --motion "<실제 물리 동작; 줌 금지>" --force`.
- 매 클립 전 프로필 크롬 정리 + timeout 캡(무한 리붓루프 방지). 봇/혼잡 "수요 많음"은 쿨다운·재시도.
- ⚠️ Veo 클립엔 ✦ 워터마크 고정삽입 → [[veo-watermark-position]] (로고로 덮음).

## 4단계 · 합성 렌더 (moviepy 2.x)
- `compile_main_hybrid.py`(단일) / `compile_main_multi.py`(다국어). 클립 speed를 슬롯에 맞춤 + 자막(무박스, malgunbd 외곽선+그림자) + 로고(워터마크 덮기, 96px) + **정확한 한글 자모 오버레이** + 전환(디졸브=크로스페이드/컷).
- **레이어 순서: 영상 → 자모 → 로고 → 타이틀 → 자막(맨 앞, 안 깨짐).**

## 5단계 · 나레이션 (gTTS 타이밍 → ElevenLabs)
- **먼저 무료 gTTS로 타이밍 확정** → OK 후 **ElevenLabs 원어민 교체**.
- 확정 보이스: KO=**Kanna** · EN=**Alice** · ZH=**Jackie**(베이징) · JA=**Kinako** · ES=**Valentina**(콜롬비아). 모델 `eleven_multilingual_v2`, KO/ZH/JA 1.1배속·EN/ES 1.05. (`i18n/make_narration_11.py`; 라이브러리 보이스는 `voices/add/{owner}/{vid}`로 계정 추가)
- 캐시 재사용으로 크레딧 절약. ⚠️ 자모·한글은 언어판 상관없이 정확발음 유지 [[feedback-korean-pronunciation-principle]].

## 6단계 · 다국어 A안 (한 영상 + 5나레이션 + 5자막)
- **씬 슬롯 = 5개 언어 씬별 최댓값 + 여백** → 전 언어 자연 속도(압축 0). (`compile_main_multi.py`, 슬롯 max-of-5, 데이터 `i18n/narration.json`+`timeline.json`)
- **가장 긴 언어(예 ES)가 영상 길이를 정함.** 그보다 긴 언어(ZH·JA)는 **텍스트를 간결하게 재작성**(`fill_short.py`)해 자연속도로 맞춤(억지 압축 X). 짧은 언어 **여백은 배경음악**.
- **배경음악 = 여민락**(용비어천가 궁중악, CC BY / 한국저작권위원회). **덕킹: 나레이션 중 볼륨 절반, 빈곳 full.** 출처는 `main/CREDITS_music.md` + 유튜브 설명란 표기 필수.

## 7단계 · 썸네일 (전용 스팟 이미지 + 자모 오버레이)
- **전용 스팟 이미지(빈 하늘)를 Flow로 생성** → **한글 자모는 직접 정자로 오버레이**(소용돌이 궤적 arc-length 배치, 겹침0, 아래작게→위크게). 5개 언어(타이틀만 교체)+4K. `scratch/thumb/make_final_A2.py`. 유튜브 메인=정지 1280×720 <2MB. [[thumbnail-method]].

## 8단계 · 마무리·업로드
- 최종 = **자막없는 마스터 영상 1개 + 오디오 5(나레이션+덕킹음악) + 자막 .srt 5** → **유튜브 다국어 오디오/자막** 업로드.
- ★★ **유튜브 업로드 필수 2가지**([[youtube-ai-disclosure]]): ①설명란 고지문 "본 영상의 시각 자료 중 일부는 Google Veo 및 Flow AI 기술을 활용하여 생성 및 연출되었습니다." ②스튜디오 세부설정 '실제처럼 합성/수정한 미디어인가요?'에 **예(Yes)**. 자료=`main/YOUTUBE_CREDITS.txt`.
- **공개 순서**: 항상 **일부공개(unlisted)로 먼저** 업로드 → **4K 업스케일 상영이 활성화된 것을 확인한 뒤 공개(public)로 전환.** (`upload_hyp.py <video> <desc> "<title>" <tag> <thumb> unlisted` → 확인 후 스튜디오 세부정보에서 공개 전환.)
- **4K 업스케일은 최종 확정 후 한 번만**(1080p로 검토·수정 반복 → 확정 후 4K 재렌더). 720p 소스라 4K 실이득은 유튜브 고비트레이트뿐.
- 제작정보는 `channel/content.db`에 링크 저장(영상 바이너리 Git 금지). 큰 파일 R2 [[r2-media-cdn]].

### 8-A · 자막·제목·설명 업로드 (검증 절차, 2026-07-03 최면 KO+EN 성공)
> 스튜디오 `/translations` 페이지 자동화. **오디오 다국어 트랙은 이 채널 아직 미개방** → 지금은 자막 5개 + 제목·설명 5개까지. 상세 [[youtube-multilang-upload]].
- **되는 방법(클린 플로우, `cap_clean.py`)**: ①새로고침으로 깨끗한 상태 → ②언어행×"자막" 셀 클릭(편집기 열림) → ③`파일 업로드` 클릭을 **`expect_file_chooser()`로 감싸** `fc.value.set_files(srt)` (사전지정 금지) → ④"타이밍 포함/제외" 다이얼로그 `계속`은 **Playwright 네이티브 `locator("#confirm-button").click()`** → ⑤우상단 `게시`. 새 언어는 add=1(언어추가→편집기, 한 세션 원자적: 빈 언어행은 새로고침 시 사라짐).
- **제목·설명(`meta_clean.py`)**: 언어행×"제목 및 설명" 셀 클릭 → 우측 `textarea[placeholder="제목*"]`+`설명`(x>900) fill → `게시`. 번역본은 `content.db video_localizations`(video_id,lang)에서 읽음.
- **★ 실패했던 이유(하지 말 것)**: `#captions-file-loader` 숨김 input에 **파일을 미리 set하면** "방법 선택" 화면의 input은 비활성이라 무시되고, 중복 set로 `계속`(#confirm-button) 핸들러가 **먹통**이 된다(마우스·JS·이벤트·Enter 다 안 먹힘). 버튼 위 리플 오버레이 `div.ytSpecTouchFeedbackShapeFill`가 raw 클릭을 가로채기 때문 → Playwright 네이티브 locator 클릭이라야 뚫림.
- **CDP 연결 필수**: 위 스크립트는 살아있는 크롬(`--remote-debugging-port=9222 --user-data-dir=assets/chrome_profile`)에 `connect_over_cdp`로 붙는다. 별도 `launch_persistent_context`로 같은 프로필을 또 열면 **프로필 락 충돌**. 디버그는 `cdp.py`(probe/atpoint/rowcell/uploadfile/smartclick).

---

### 핵심 도구/파일
- Flow 이미지 `gen_assets_flow.py` · Veo 클립 `autoveo_flow.py`
- 합성 `sejong_film/main/compile_main_hybrid.py`(단일) · `compile_main_multi.py`(다국어 A안)
- 나레이션 `i18n/make_narration_11.py`(ElevenLabs) · `make_narration_free.py`(gTTS)
- 다국어 데이터 `i18n/narration.json` · `timeline.json` · `fill_translations.py` · `fill_short.py`
- 썸네일 `scratch/thumb/make_final_A2.py` · 음악출처 `main/CREDITS_music.md`
