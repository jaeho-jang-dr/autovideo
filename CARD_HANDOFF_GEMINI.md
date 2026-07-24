# 온스크린 동영상 카드 삽입 — 제미나이 인계 문서

> Claude(감독)가 수 시간 씨름한 내용 총정리. **카드 추가는 됨, 저장(Save)만 막힘.** 조감독(Gemini)이 마지막 저장 단계를 뚫어 완성할 것.

## 목표
YouTube 두 영상에 **타임드 동영상 정보카드 2장씩**을 실제 클릭 가능하게 삽입 + 저장.
영상 내 우상단 온스크린 그래픽(0:30 "숫자 영상", 3:45 "다음 영상")과 매칭되는 실제 유튜브 카드.

## 대상 (언어 매칭: 한글판→한글영상, 영어판→영어영상)
| 대상영상 | 카드1 (숫자, ~0:30) | 카드2 (다음=저조회 한글교육, ~3:45) |
|---|---|---|
| **KO** `YTex0QGe17o` | `xp9ktV7zOYY` (W8 한국어 숫자·날짜·시간) | `zVVrm8De8QY` (W7 한국어 인사말과 자기소개, 2회) |
| **EN** `HhSRarWJS0E` | `xgEedO2aFnk` (W8 Numbers Dates) | `KrHzUwFQ0XI` (W2 Basic Consonants, 3회) |

검색어(내 동영상 검색창): KO는 "한국어 숫자" / "한국어 인사말". EN은 각 영어 제목 일부.

## 환경
- 디버그 크롬 CDP: `http://localhost:9222` (로그인된 drjang00 프로필). **크롬 죽이지 말 것.**
- Playwright over CDP: `connect_over_cdp("http://localhost:9222")`, `ctx=b.contexts[0]`, `/video/<VID>/edit` 페이지.
- 뷰포트↔스크린샷 배율 ≈ dpr 1.35~1.5 (좌표 혼동 주의: Playwright 클릭·bbox는 **뷰포트 CSS px**, CDP 스샷은 device px).

## ✅ 되는 것 (Playwright, 검증 완료 — card_video_ui.py)
편집기 열기~카드 추가까지 100% 재현됨. `저장전 동영상카드수=2` 확인.
1. 편집기 열기: `pg.get_by_role("button", name="카드", exact=True).first.click()`  ← Polymer지만 Playwright 로케이터 클릭은 됨
2. 카드 추가: `pg.get_by_role("button", name="카드 추가").first.click()`
3. 동영상 타입: `pg.mouse.click(272, 134)`  (드롭다운 '동영상' 실측 뷰포트 좌표)
4. 검색: `pg.get_by_placeholder("내 동영상 검색").first.fill("<검색어>")`
5. 결과선택: `hit=pg.get_by_text("<제목조각>", exact=False)` → bbox 얻어 `pg.mouse.click(bb.x+bb.w/2, bb.y-40)` (썸네일=제목 위 40px). → "동영상 카드" 추가됨.
6. 카드2도 2~5 반복.

## ❌ 막힌 것: **저장(Save)**
카드 2장 추가 후 모달 상단의 검은 **"저장"** 버튼 클릭이 안 먹음.
- `get_by_role("button", name="저장")`가 5개 매칭(대부분 페이지레벨/숨김). 활성 후보 3개: 대략 @(960,60),(1114,60),(1130,60) 뷰포트. **인덱스·좌표가 실행마다 흔들림.**
- 하나(@960,60) 클릭하면 성공하지만 **모달만 닫힘(저장 아님)** → 나머지 저장버튼 사라져 timeout.
- 오른쪽 것들은 `Locator.click Timeout`(actionable 아님).
- **결정적 진단: 저장 클릭 동안 어떤 `/youtubei/v1/` 저장 POST도 안 나감** (오직 list_creator_videos/get_creator_videos = 피커 검색만). 즉 진짜 모달 저장버튼을 못 누르고 있음.
- 순수 CDP `Input.dispatchMouseEvent` 클릭 = Polymer 버튼 **포커스만** 되고 활성화 안 됨. JS `element.click()`도 무시됨(연구로 확인 — Polymer는 synthetic click 무시).
- ⚠️ `ctx.close()`는 미저장 모달을 **닫아 변경 폐기**함. 저장이 서버에 커밋된 뒤에만 close 안전.

## 인계 지점 = 제미나이가 할 일
**"카드 추가"까지는 card_video_ui.py 그대로 쓰고, 진짜 모달 저장버튼만 정확히 눌러 edit_video POST를 발생**시키면 끝.
추천 접근(택1):
1. **모달 저장버튼 정확 식별**: 카드 편집기 모달(`ytve-info-cards-editor` 계열 shadow) 안의 "저장"만 스코프. 예: 모달 다이얼로그 요소를 찾고 그 안 `get_by_role("button",name="저장")` 또는 검은버튼(primary/filled ytcp-button)만. is_visible()+is_enabled() 필터 후 **딱 그것만** 클릭. 클릭 성공 판정 = `/youtubei/v1/.../edit_video` POST 발생(리스너로 확인).
2. **수동-1클릭 하이브리드**: Claude/스크립트가 카드 추가까지 하고(모달 열린 채 유지, ctx.close 금지), 사장님이 "저장" 한 번만 손으로 클릭.
3. **내부 API 재도전**: `POST https://studio.youtube.com/youtubei/v1/video_editor/edit_video?alt=json&key=AIzaSyBUPetSUmoZL-OhlxA7wSac5XinrygCqMo`. 바디 `{"context":<ctx>, "externalVideoId":VID, "infoCardEdit":{"infoCards":[card...]}}`. **카드 필드명 확정**(Studio 번들 vme.js 실제 코드): `videoInfoCard:{videoId:"<target>"}` + `teaserStartMs`(ms) + `teaserText` + `customMessage` + `infoCardEntityId`. 재생목록은 `playlistInfoCard:{fullPlaylistId}`. 인증=SAPISIDHASH 헤더 + 쿠키(브라우저 fetch면 자동). context는 `scratch/yt/ctx.json`에 캡처됨(sessionInfo.token 만료 가능 → 재캡처). ⚠️ 이전 API POST는 HTTP200이지만 카드 persist 안 됐음(페이로드/세션 불완전 추정) → **UI 저장이 더 확실**. 가장 확실한 확정법은 **UI로 카드 하나 수동 저장 시 실제 edit_video 요청 바디를 캡처**(cap_editvideo.py/cdp_ws.py 방식)해 그대로 replay.

## 검증법
편집기 재오픈 후: `pg.get_by_text("동영상 카드", exact=True).count()` == 2 여야 성공. (지금은 저장 실패라 0, 재생목록 카드만 1.)
또는 시청 페이지 `ytInitialPlayerResponse.cards.cardCollectionRenderer.cards`(전파 수 분 지연).

## 관련 스크립트(레포 루트)
- `card_video_ui.py` — Playwright 카드 추가(검증됨)+저장(막힘). `python card_video_ui.py <VID> "<검색>" "<제목조각>" "<시각>" [...반복] --save`
- `cdp_final.py` — 순수 CDP 전과정(편집기 열기 Polymer 클릭 문제로 실패)
- `yt_infocard.py` — 내부 API 카드 쓰기(200이나 persist X)
- `cap_editvideo.py` / `cdp_ws.py` — 실제 edit_video 요청 캡처 시도(websocket-client, `suppress_origin=True` 필수)
- `scratch/yt/ctx.json` — 캡처된 youtubei context

## ⚠️ 함정 정리
- 스크린샷은 프리뷰 플레이어 때문에 Playwright `pg.screenshot` **hang** → CDP `Page.captureScreenshot`만, 그마저 세션 불안정 시 hang. card_video_ui는 스샷 no-op 처리해 hang 제거함.
- 좀비 프로세스: hung python 반복 kill 필요. `Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? {$_.CommandLine -match 'card_|cdp_'} | Stop-Process -Force`
- 시각(teaserStartMs) 설정 UI 필드는 hang 유발 → 일단 0:00로 두고 링크만 먼저. (SET_TIME env 가드)

## 시간 예산
사장님: "둘 다 저장돼야 성공. 안되면 영상 폐기·재렌더." → **저장 한 방만 뚫으면 됨.**
