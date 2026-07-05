# 유튜브 업로드 완전 플레이북 (@drjay-ed)

> 동영상을 유튜브에 올리기 전 **사전 준비**부터 **업로드 클릭 순서**까지 전부. 사람·Gemini·Claude 공용.
> 채널: https://www.youtube.com/@drjay-ed (계정 drjang00, 채널ID UC6KCrgUSdSVUd97b7ltJK_g).
> 요약 인덱스·DB구조는 `YOUTUBE_UPLOAD_GUIDE.md`, 이 문서는 **실행 절차 상세판**.

---

# PART A. 업로드 전 사전 준비 (10가지)

## ① 파일명을 검색 키워드로 바꾸기
- 유튜브는 업로드되는 **파일명**을 1차 주제 신호로 읽는다. `output.mp4`, `final_v2.mp4` 금지.
- **영문 소문자 + 언더바 + 핵심 키워드**로 복사해서 올린다.
  - 예: `king_sejong_hangeul_4k.mp4`, `child_height_growth_science_4k.mp4`, `binge_watching_science_4k.mp4`
- 방법: `cp 원본.mp4 키워드파일명.mp4` 후 그 파일을 업로드.

## ② 제목 — 핵심 키워드를 맨 앞에
- 사람도 검색엔진도 제목 앞부분을 가장 중요하게 본다. 흥미유발 문구는 뒤로.
  - 나쁨: "이것만 알면 끝! 키 크는 기적의 방법"
  - 좋음: "우리 아이 키 얼마나 클까? | 소아 성장·키 크는 과학 (부모 필독)"
- 다국어면 제목에 대표 언어들 병기(예 `… (King Sejong & Hangeul · 5 languages)`).

## ③ 4K 업스케일 상태로 올리기
- 720/1080p 그대로면 화질 낮은 AVC1 코덱 배정. **4K(3840×2160)로 올려야** VP09 고화질 코덱 버프.
- 렌더는 1080p로 검토 반복 → 확정 후 **FFmpeg Lanczos로 4K 업스케일 1회**:
  `ffmpeg -i master.mp4 -vf "scale=3840:2160:flags=lanczos" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -c:a copy out_4k.mp4`

## ④ 설명란 — 첫 3줄에 요약+키워드 (검색 가중치 최고)
- 미리보기·검색에 첫 3줄(약 150자)만 노출된다. 여기에 제목 키워드를 자연스러운 문장으로.
- 구조: **요약 2~3줄 → 챕터 → 다국어 안내 → AI 고지문 → (음악출처) → 해시태그**.
- 텍스트는 `<proj>/yt_desc_ko.txt` 파일로 저장해두고 붙여넣기.

## ⑤ 썸네일 (전용 이미지 + 정확한 오버레이)
- 클립 프레임이 아니라 **주제를 담은 프레임/전용 이미지** + 큰 텍스트 + 로고 1개(원본에 로고 겹치면 배경색으로 덮고 하나만).
- 규격: **1280×720, 2MB 미만, jpg**. A/B 시안 2~3개 만들면 유튜브가 자동 테스트.
- ⚠️ **커스텀 썸네일 업로드는 채널 전화번호 인증 필요**(1회, 이미 완료됨).

## ⑥ 업로드 기본 설정 템플릿 (한 번만)
- 스튜디오 → ⚙설정 → 업로드 기본 설정 → 기본 설명/태그/카테고리/시청자층 저장 → 매 업로드 자동적용.

## ⑦ 카테고리 = 교육 (Education)
- 알고리즘이 교육 시청자 그룹에 우선 노출. 반드시 **교육**으로.

## ⑧ 타임스탬프(챕터) 8~10개
- 설명란에 `0:00 인트로` 형식으로 넣으면 재생바에 챕터 생성 + 구글 검색 Key Moments 노출.
- 실제 씬 시작 시각을 srt/타임라인에서 계산해 논리적 구간으로.

## ⑨ ★ AI 생성 라벨링 = "예" (필수) ★
- AI(Veo/Flow 등)로 만든 시각자료가 있으면 **반드시** 고지. 안 하면 정책 위반 소지.
- **두 가지 모두**:
  1. **설명란 고지문**: `본 영상의 시각 자료 중 일부는 Google Veo 및 Flow AI 기술을 활용하여 생성 및 연출되었습니다.`
  2. **업로드 세부설정**: "자세히 보기" → **변경된 콘텐츠(합성/수정된 미디어)** 질문 = **예(Yes)**.
     (질문 원문: "실제 인물, 장소, 사건을 모방하거나 실제처럼 보이게 합성/수정한 미디어인가요?")

## ⑩ 일부공개(Unlisted)로 게시 → 인코딩 대기 → 공개
- 올리자마자 공개하면 4K 인코딩 전이라 첫 시청자가 저화질을 본다(유지율↓).
- **일부공개로 게시 → 최소 1~2시간 후** 재생창 톱니바퀴에서 **1080p HD / 2160p 4K 옵션이 완전 활성화**됐는지 확인 → 그때 **공개(Public)** 전환.

### 추가(우리 채널 전용)
- 다국어 영상은 업로드 후 **오디오 트랙 다중 + 자막(.srt) 다중** 추가 가능(반자동/수동).
- 모든 업로드 정보를 `channel/content.db` `youtube_uploads`에 태그 **"내가 만든 내 동영상"**과 함께 기록.

---

# PART B. 업로드 클릭 순서 (스튜디오 UI, 수동 기준)

1. **studio.youtube.com** → 우상단 **"만들기" → "동영상 업로드"** → 모달의 **"파일 선택"** → 키워드 파일명 mp4 선택.
2. **세부정보** 화면:
   - **제목**: ②의 제목 붙여넣기.
   - **설명**: ④의 `yt_desc_ko.txt` 내용 붙여넣기.
   - **썸네일**: "썸네일 업로드"(파일 업로드) → `thumb_ko_1280x720.jpg`. (전화인증 필요)
   - **시청자층**: **"아니요, 아동용이 아닙니다"** 선택.
   - **"자세히 보기"** 펼치기 →
     - **변경된 콘텐츠** = **"예, AI가 사용되었습니다"** (⑨)
     - **카테고리** = **교육** (⑦)
     - (태그: 세종대왕, 한글 … 등 선택)
3. **"다음"** ×3 (동영상 요소·검토·공개 상태로 이동).
4. **공개 상태** → **"일부 공개"** 선택 → **저장/게시**.
5. (업로드/처리 진행 — 브라우저 유지) 완료되면 초안이 일부공개로 게시됨.
6. **2시간 후** → 영상 재생창 톱니바퀴에서 4K 활성 확인 → 콘텐츠 목록에서 공개상태 → **공개**로 전환.

---

# PART C. 자동화(playwright, 로그인 크롬 프로필) — Gemini/Claude용

> 스크립트는 레포 루트. 실행 전 **반드시** 프로필 크롬 종료 + `assets/chrome_profile/Singleton*` 삭제. `af.PROFILE` 사용.

| 스크립트 | 역할 |
|---|---|
| `upload_one.py <video> <desc.txt> "<title>" <tag>` | 비공개 초안 업로드(제목·설명·아동용아님·AI예·교육 자동) |
| `set_thumbnail.py` (ID·THUMB경로 수정해 사용) | 커스텀 썸네일 적용 (`ytcp-thumbnail-uploader input[type=file]`) |
| `set_visibility.py <video_id> <tag>` | 초안수정 마법사로 일부공개 전환 |
| `set_cg_unlisted.py` / `set_ko_short_vis.py` | 콘텐츠 목록 상태텍스트 클릭 → 라디오 → 저장(게시본 전환용) |
| `set_public.py` / `set_sejong_shorts_public.py` | 공개 전환 |
| `get_video_ids.py` | 업로드/쇼츠 목록의 video_id·제목·상태 수집 |
| `check_quality.py` | 재생창 화질 옵션(2160p 4K 등) 활성 확인 |

### 핵심 셀렉터 요령
- 제목/설명: `[contenteditable='true'][aria-label*='제목']` / `[aria-label*='설명해']`
  (⚠️ 제목 aria-label에 "동영상을 설명하는"이 포함돼 있어 '설명' 매칭이 제목을 잡는 버그 주의 → aria-label에 '설명해' 포함으로 구분)
- 라디오: `get_by_role("radio", name="아동용이 아닙니다")`, `name="AI가 사용되었습니다"`.
- 공개상태: `tp-yt-paper-radio-button[name='UNLISTED'|'PUBLIC'|'PRIVATE']`.
- 파일 선택: 업로드 모달 열고 → `#select-files-button` 클릭 → `expect_file_chooser`.
- 목록 상태셀 클릭 안 되면: 행에서 `text=비공개`(또는 `일부 공개`)를 `force=True`로 클릭 → 라디오 → `#save-button`.
- 제목 입력 시 공백 보존: `pg.keyboard.insert_text(TITLE)` (type은 개행/공백 이슈 가능).

### DB 기록 (업로드 후 필수)
```sql
-- youtube_uploads: project,kind(main/short),lang,video_id,url,title,visibility,thumbnail_path,
--   local_path,duration_sec,resolution,channel,ai_disclosure(=1),category('교육'),tags('내가 만든 내 동영상'),uploaded_at,notes
-- video_projects: youtube_url, tags='내가 만든 내 동영상' upsert
```

---

# PART D. 안전·주의
- **.env의 AZURE/ELEVEN 키는 절대 로그·터미널·커밋에 노출 금지.**
- 커밋/푸시는 **사용자 승인 후에만**. 영상 바이너리 Git 금지(로컬/유튜브/R2만).
- 공개(Public)는 되돌리기 어려운 외부공개 → 4K 인코딩 확인 후, 사용자 확인 하에.
- 인코딩 UTF-8 no BOM.
