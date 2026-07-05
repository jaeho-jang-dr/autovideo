# 정주행(binge_watching) 영상 유튜브 업로드 — Gemini 인계서

> 작성: Claude(감독) → Gemini(조감독). 정주행 영상을 유튜브 업로드까지 완성하는 작업.
> 작업 폴더: `D:/Entertainments/DevEnvironment/autovideo` / 프로젝트 폴더: `binge_watching/`

---

## 1. 프로젝트 개요
- **제목**: "밤샘 정주행, 내 몸의 경고" (정주행/몰아보기가 몸·뇌에 미치는 영향, 화이트보드 손그림 스타일)
- **본편**: `binge_watching/binge_azure.mp4` — **4K(3840×2160), 8:15, 24fps**
  - 오디오 2트랙: a:0=한국어(Azure 선희 SunHi, 기본), a:1=English(Azure Emma)
  - 자막 2트랙: 한/영 (mov_text)
- 나레이션은 **Azure TTS로 재생성 완료**(합법). KO=`ko-KR-SunHiNeural`, EN=`en-US-EmmaMultilingualNeural`.
  - 키는 `.env`의 `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION=koreacentral` (⚠️절대 로그/커밋 노출 금지)
- 씬 97개, KO/EN 슬롯 타이밍 동일, srt 끝 477.4초.

## 2. 완료된 것 ✅
- Azure 나레이션 재생성 + 본편 재먹싱 (`binge_azure.mp4`)
- **썸네일 영/한** 완성: `binge_watching/thumb_ko_1280x720.jpg`(+_4k), `thumb_en_1280x720.jpg`(+_4k)
  - 스크립트 `binge_watching/make_thumb_binge.py` (30초 프레임=뇌+척추 인체 베이스)
- **설명 파일** 완성: `yt_desc_ko.txt`(챕터8개 포함), `desc_short_ko.txt`, `desc_short_en.txt`

## 3. ★ 지금 막힌 것 (Gemini가 해결할 것) ★
**쇼츠(9:16) 렌더가 FFMPEG write 에러로 실패** — `OSError: [Errno 22] Invalid argument`, moviepy `ffmpeg_write_video → write_frame`.
- 스크립트: `binge_watching/make_binge_short.py` (child_growth 쇼츠 스크립트를 복제·수정한 것)
- 구성: 씬0(훅)+씬2+씬20, 9:16 캔버스(1080×1920)에 본편 클립(중앙)+제목(상단)+자막(하단)+로고, Azure 오디오(`_ko_sunhi`/`_en_emma`의 `{scene:03d}.mp3`) 사용
- **원인 추정**: 4K(3840×2160) 소스를 `resized(width=1080)` 하면 높이 607.5→홀수(607)가 되어 H.264 write 실패 가능성 큼. (child_growth는 됐지만 binge 원본 특성 차이일 수 있음)
- **해결 방향(택1)**:
  1. `make_binge_short.py`의 비디오 클립 리사이즈 후 **높이를 짝수로 강제**: `v=v.resized(width=W); if v.h%2: v=v.resized((W, v.h+1))` 또는 `.cropped`로 짝수 맞춤. 최종 캔버스(1080×1920)는 짝수라 OK.
  2. 또는 소스를 먼저 **짝수 해상도로 재인코딩**한 뒤 subclip: `ffmpeg -i binge_azure.mp4 -vf scale=1920:1080 -c:v libx264 -crf 20 -an -sn binge_watching/_src_shorts.mp4` 만들고 MASTER를 그걸로.
  3. 또는 write_videofile에 `ffmpeg_params=["-vf","scale=trunc(iw/2)*2:trunc(ih/2)*2"]` 추가.
- 검증: `python binge_watching/make_binge_short.py ko` → `binge_short_ko.mp4` 생성(약 2~4MB, 1080×1920, ~20초)되면 성공. 그다음 `en`.
- ⚠️ moviepy 2.x API (with_duration/with_position/resized/subclipped/CompositeVideoClip). 실행 전 프로필 크롬 안 띄워도 됨(로컬 렌더).

## 4. 남은 작업 (쇼츠 해결 후, 순서대로)
### A. 사용자에게 보여주기
- 본편(`binge_azure.mp4`), 썸네일 2개, 쇼츠 2개(`binge_short_ko.mp4`, `binge_short_en.mp4`)를 사용자에게 확인받는다.
- 쇼츠 미리보기 시트: 첫 프레임 몇 장을 PIL로 합쳐 보여주면 좋음.

### B. 유튜브 업로드 (★ 반드시 레포 `YOUTUBE_UPLOAD_PLAYBOOK.md` 전체 정독 — 사전작업 10가지 + 클릭순서 + AI'예' + 파일명SEO + 셀렉터 요령 다 있음)
채널 @drjay-ed (drjang00, 채널ID UC6KCrgUSdSVUd97b7ltJK_g). 로그인된 크롬 프로필로 자동화.
- 자동화 스크립트 재사용: 레포 루트 `upload_one.py`, `set_thumbnail.py`(→ID·THUMB경로만 수정), `set_visibility.py`, `set_cg_unlisted.py`, `get_video_ids.py`.
  - 실행 전 반드시: 프로필 크롬 종료 + `assets/chrome_profile/Singleton*` 삭제.
- 업로드 대상 3개: **본편 `binge_azure.mp4`**(키워드 파일명으로 복사해 올릴 것, 예 `binge_watching_science_4k.mp4`) + **쇼츠 KO/EN 2개**.
- 각각: 제목(키워드 앞배치)·설명(위 txt 파일)·**아동용 아님**·**AI 사용 예**(변경된 콘텐츠)·**카테고리 교육**·**커스텀 썸네일**·**일부공개(Unlisted)로 게시**.
  - 제목 예 KO: `밤샘 정주행, 내 몸의 경고 | 몰아보기의 과학 (수면·도파민·건강)`
- 본편은 4K라 업로드 후 인코딩 시간 필요 → 일부공개로 두고, 사용자 확인 후 공개.

### C. DB 기록 (필수 — 레포 `channel/content.db`)
- `youtube_uploads` 테이블에 3개 영상 INSERT (project='binge_watching', kind=main/short, lang, video_id, url, title, visibility='unlisted', thumbnail_path, local_path, duration_sec, resolution, channel, ai_disclosure=1, category='교육', **tags='내가 만든 내 동영상'**, uploaded_at, notes).
- `video_projects`에도 binge_watching 프로젝트 upsert (youtube_url, tags='내가 만든 내 동영상').
- 컬럼 구조는 기존 sejong_hangeul/child_growth 레코드 참고.

## 5. 참고 (검증된 방식·주의)
- 교정앱: `review_growth.py` 패턴(좌 영상+자막, 우 메모). 정주행용은 `review_binge.py`(포트 8905) 이미 있음. 필요시 사용.
- Azure TTS 재생성 스크립트: `binge_watching/make_binge_azure.py` (참고용, 이미 실행 완료).
- 인코딩 UTF-8 no BOM. 커밋/푸시 금지(사용자 승인 필요). 큰 영상 Git 금지.
- 완료되면 Claude(감독) 또는 사용자에게 결과 보고(각 영상 video_id·링크).
