# YouTube 다국어 노출 — Data API 방식 (2026-07-13 확정, W12부터 표준)

> **한 줄 요약**: YouTube Studio "동영상 자막" 페이지가 신형 Polymer UI로 교체되면서 기존 브라우저
> 자동화(`tx_sub.py` / `cap_robust.py` / `yt_localize.py`)가 **전부 깨졌다**. 이제 자막·제목설명·태그·
> 공개전환·재생목록·댓글은 **YouTube Data API v3 (`yt_api.py`)** 로 처리한다. 핀·최종화면·카드만 UI.

---

## 1. 왜 바꿨나 (근본 원인, 실측)

W11 노출 작업 중 자막이 하나도 안 올라가서 조사한 결과:

- 자막 페이지 DOM이 신형 커스텀 엘리먼트로 교체됨:
  - `ytgn-video-translation-row` (행)
  - `ytgn-video-translation-cell-captions` (자막 셀)
  - `ytgn-video-translation-cell-metadata` (제목 및 설명 셀)
- 이 셀들 안에는 `<a>`·`<button>`이 **없다**(Polymer가 클릭을 자체 처리).
- 그래서 셀을 클릭해도 **행이 회색으로 선택만 되고 자막 편집기가 열리지 않는다**.
  `element.click` / `mouse.click` / pointer 이벤트 / Enter / 더블클릭 — **5가지 모두 URL 무변화**.
- 결과: `tx_sub.py`가 filechooser timeout으로 실패 → 자막 0개.

**결론: UI를 계속 뜯어고치는 건 또 깨진다. API가 정답.**

---

## 2. 인증 셋업 (1회, 이미 완료 — 재현용 기록)

### ❌ 안 되는 길: gcloud ADC
```
gcloud auth application-default login --scopes=...youtube.force-ssl
→ "차단된 앱" (Google이 공용 gcloud 클라이언트로 유튜브 민감 스코프 사용을 하드블록)
```
AI 감지 때문이 아니라 **구글 정책**. 우회 불가.

### ✅ 되는 길: 전용 OAuth 데스크톱 클라이언트
1. GCP 콘솔 → `https://console.cloud.google.com/auth/clients?project=miryangosweb`
2. **클라이언트 만들기 → 애플리케이션 유형 "데스크톱 앱"** → 만들기
   - 동의 화면 요구 시: External + 앱이름/지원이메일 본인 + **테스트 사용자에 drjang00@gmail.com 추가**
3. **JSON 다운로드** → 레포 루트에 `client_secret_*.json` 으로 저장 (이름 그대로 두면 됨, 스크립트가 glob으로 찾음)
4. `python yt_auth.py` 실행 → 브라우저 동의
   - "확인되지 않은 앱" 경고 → **고급 → 이동 → 허용** (소프트 경고일 뿐, 차단 아님)
5. `yt_token.json` 저장됨 (refresh_token 포함 → 이후 자동 갱신, 재로그인 불필요)

- YouTube Data API v3는 프로젝트 `miryangosweb`에 **활성화 완료**.
- Scope: `https://www.googleapis.com/auth/youtube.force-ssl`
- ⚠️ **`client_secret_*.json` / `yt_token.json` 은 .gitignore 됨 — 절대 커밋 금지.**

---

## 3. 도구 — `yt_api.py`

```bash
python yt_api.py test                          # 채널 인증 확인 (Dr jay-edu)
python yt_api.py captions <VID>                # 기존 자막 트랙 나열
python yt_api.py localize <VID> <manifest.json># ★자막+제목설명+태그+기본언어 일괄
python yt_api.py subs    <VID> <manifest.json> # 자막만
python yt_api.py meta    <VID> <manifest.json> # 제목설명+태그+기본언어만
python yt_api.py tags    <VID> <tags.txt>
python yt_api.py public  <VID>                 # 일부공개 → 공개
python yt_api.py playlists                     # 내 재생목록
python yt_api.py playlist_add <VID> "한국어 쉽게 배우기"
python yt_api.py comment <VID> <comment.txt>   # 고정댓글 "게시"(핀은 UI)
# 옵션: --force  (기존 자막 트랙 삭제 후 재업로드)
```

매니페스트는 **기존 `wNNpkg/*_manifest.json` 형식을 그대로 소비**한다(별도 변환 불필요).
행 이름(한국어) → BCP-47 매핑: 한국어=ko / 영어=en / 일본어=ja / **중국어(중국)=zh-Hans** / 스페인어=es.

### ⚠️ 함정 (겪은 것)
- **자동자막(ASR) 소문자 함정**: `captions.list`의 `trackKind`는 **소문자 `asr`**로 온다.
  대문자 `ASR`로 비교하면 못 걸러서, 자동자막이 있는 언어(보통 ko)의 **정확한 수동 자막이
  "이미 있음"으로 스킵**된다. → `(trackKind or "").lower() == "asr"` 로 제외해야 한다(수정 완료).
- 콘솔 출력은 `PYTHONIOENCODING=utf-8` 안 주면 cp949로 한글 깨짐/에러.

---

## 4. API로 되는 것 / 안 되는 것 ★

| 작업 | API | 도구 |
|---|---|---|
| 자막 5개국어 업로드 | ✅ `captions.insert` | `yt_api.py subs/localize` |
| 다국어 제목·설명 | ✅ `videos.update` (localizations) | `yt_api.py meta/localize` |
| 태그 | ✅ `snippet.tags` | `yt_api.py tags/localize` |
| 기본 언어 | ✅ `snippet.defaultLanguage` | `yt_api.py meta/localize` |
| **공개 전환** | ✅ `status.privacyStatus=public` | `yt_api.py public` |
| 재생목록 추가 | ✅ `playlistItems.insert` | `yt_api.py playlist_add` |
| 댓글 **게시** | ✅ `commentThreads.insert` | `yt_api.py comment` |
| **댓글 핀 고정** | ❌ **API 없음** | `pin_only.py` (watch 페이지 UI — 안정) |
| **최종화면** | ❌ **API 없음** | `endscreen.py` (Studio UI) |
| **카드** | ❌ **API 없음** | `card.py` (Studio UI) |
| 영상 업로드 | ✅ `videos.insert` (미적용) | 현재는 `upload_cdp.py` (4K>50MB CDP 우회) |
| AI '변경된 콘텐츠' 체크 | ❌ API 없음 | 업로드 시 UI |

> 핀·최종화면·카드는 유튜브가 API를 안 열어준다 → **UI 자동화 유지가 불가피**.
> 다행히 `pin_only.py`는 **공개 watch 페이지**를 쓰므로 Studio 신형화 영향이 없다(W11에서 정상 동작 검증).

---

## 5. W12부터 표준 순서

```bash
# 0) (최초 1회만) 인증: client_secret 배치 → python yt_auth.py
# 1) 업로드 (4K>50MB는 CDP 우회) → VID 확보
# 2) ★노출 일괄 (API — 자막5+제목설명4+태그+기본언어)
python yt_api.py localize <KO_VID> hangeul_birth_vowels/wNNpkg/wNN_ko_manifest.json
python yt_api.py localize <EN_VID> hangeul_birth_vowels/wNNpkg/wNN_en_manifest.json
# 3) 검증 (로그 못 믿음 — 실검증)
python scratch/verify_caps_api.py <KO_VID> <EN_VID>   # 자막 트랙 5개씩(standard)
python scratch/verify_meta_api.py <KO_VID> <EN_VID>   # 제목/기본언어/태그수/로컬라이제이션/공개상태
# 4) 재생목록
python yt_api.py playlist_add <VID> "한국어 쉽게 배우기"
# 5) 고정댓글: 게시(API) → 핀(UI)
python yt_api.py comment <VID> hangeul_birth_vowels/wNNpkg/{ko,en}_comment.txt
python pin_only.py <VID> "<댓글 앞부분 문자열>"        # verified=True 확인
# 6) 최종화면 · 카드 (Studio UI)
python endscreen.py <VID>
python card.py <VID> "한국어 쉽게 배우기"
# 7) 공개 전환 (노출 최적화 끝난 뒤 마지막)
python yt_api.py public <KO_VID> && python yt_api.py public <EN_VID>
# 8) 웹 임베드 (CurriculumView YT_VIDEOS + LessonsView YOUTUBE_MAP + 게이트 <=N) → 빌드 → wrangler 배포
```

---

## 6. W11 완주 실적 (이 방식으로 검증됨, 2026-07-13)

- KO `TJLaZH-ghC0` / EN `Ecv5l7aQHGE` (식당·맛표현 / 감천문화마을 / 마담제이)
- 자막 5개국어(ko/en/ja/zh-Hans/es) · 다국어 제목설명 · 태그 43개(~480자) · 기본언어 ·
  재생목록 · 고정댓글+핀(verified) · 최종화면 · 카드 · **공개 전환(public)** 전부 완료.
- DB `youtube_uploads.visibility='public'` 갱신.

관련 문서: `YOUTUBE_UPLOAD_TOOLCHAIN.md`(구 UI 툴체인·2패스 복구), `YOUTUBE_MULTILANG_PATTERN.md`(태그 원칙·노출 4대 작업).
**구 자막 도구(tx_sub/cap_robust/yt_localize)는 신형 UI에서 동작하지 않으므로 자막 용도로 쓰지 말 것.**
