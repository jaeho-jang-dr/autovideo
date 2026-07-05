# 유튜브 업로드 가이드 (@drjay-ed) — 표준 절차 + 제작정보 인덱스

> 채널: https://www.youtube.com/@drjay-ed (계정 drjang00). 모든 업로드는 로그인된 크롬 프로필(playwright)로 자동화.
> 제작정보·동영상 ID는 전부 `channel/content.db`에 기록. 태그 = **"내가 만든 내 동영상"**.

---

## 1. DB 구조 (제작정보 저장 위치)
- **`video_projects`** — 프로젝트 단위 (name, title_kr, status, youtube_url, **tags**, notes, runtime_sec, n_scenes, local_dir …)
- **`youtube_uploads`** — 업로드된 개별 영상 단위 (아래 컬럼). 조회: `SELECT * FROM youtube_uploads`.
  - `project, kind(main/short), lang, video_id, url, title, visibility, thumbnail_path, local_path, duration_sec, resolution, channel, ai_disclosure, category, tags, uploaded_at, notes`

### 현재 업로드된 영상 (전부 일부공개/Unlisted, 태그 "내가 만든 내 동영상")
| 프로젝트 | 종류 | video_id | URL |
|---|---|---|---|
| sejong_hangeul | main(다국어) | `6lGedBJ5xx4` | youtu.be/6lGedBJ5xx4 |
| sejong_hangeul | short KO | `5YXdG4OIiMQ` | youtube.com/shorts/5YXdG4OIiMQ |
| sejong_hangeul | short EN | `FtBFZGTojfY` | youtube.com/shorts/FtBFZGTojfY |
| child_growth | main | `vvHZ27l9jr4` | youtu.be/vvHZ27l9jr4 |
| child_growth | short KO | `OAnDgIm3M_g` | youtube.com/shorts/OAnDgIm3M_g |
| child_growth | short EN | `y2kJBfPV1AY` | youtube.com/shorts/y2kJBfPV1AY |

---

## 2. 업로드 절차 (10가지 가이드라인 반영)
1. **파일명** = 키워드 (예 `king_sejong_hangeul_4k.mp4`)
2. **제목** = 검색 키워드 앞배치
3. **4K 업스케일**(FFmpeg Lanczos) 후 업로드 → VP09 고화질 코덱
4. **설명 첫 3줄** 요약+키워드 + 챕터(타임스탬프) + AI 고지문 (+ 음악 출처 있으면)
5. **썸네일** 전용(로고 1개로 정리) — 커스텀 썸네일은 **채널 전화번호 인증 필요**(1회, 완료됨)
6. 업로드 기본설정 템플릿(스튜디오 설정)
7. **카테고리 = 교육**
8. **챕터** 8~10개
9. **AI 라벨링 "예"** (변경된 콘텐츠 = 예) — 필수 [[youtube-ai-disclosure]]
10. **일부공개(Unlisted)로 게시 → 2시간 후 4K 활성 확인 → 공개(Public)**

### AI 고지문 (설명란 필수)
> 본 영상의 시각 자료 중 일부는 Google Veo 및 Flow AI 기술을 활용하여 생성 및 연출되었습니다.

---

## 3. 자동화 스크립트 (로그인 프로필)
- `upload_one.py <video> <desc.txt> "<title>" <tag>` — 비공개 초안 업로드(제목·설명·아동용아님·AI예·교육)
- `set_thumbnail.py` / `set_thumb_cg.py` — 커스텀 썸네일 적용 (ytcp-thumbnail-uploader input)
- `set_visibility.py <video_id> <tag>` — 초안수정 마법사로 일부공개 전환
- `set_cg_unlisted.py` / `set_ko_short_vis.py` — 콘텐츠 목록에서 공개상태 텍스트 클릭 → 라디오 → 저장 (쇼츠/게시본 전환)
- `get_video_ids.py` — 업로드/쇼츠 목록의 video_id·제목·상태 수집
- 공통: 실행 전 프로필 크롬 종료 + SingletonLock 삭제. `af.PROFILE` 사용.

### 브라우저 셀렉터 요령
- 제목/설명: `[contenteditable='true'][aria-label*='제목']` / `[aria-label*='설명해']` (제목 aria-label에 "동영상을 설명하는"이 들어있어 혼동 주의)
- 라디오: `get_by_role("radio", name="아동용이 아닙니다")`, `name="AI가 사용되었습니다"`, 공개상태 `tp-yt-paper-radio-button[name='UNLISTED'|'PUBLIC']`
- 파일선택: 업로드 모달 열고 → `#select-files-button` 클릭 → `expect_file_chooser`
- 공개상태 셀 클릭 안 될 때: 목록 행에서 `text=비공개`(또는 `일부 공개`) 텍스트를 `force=True`로 클릭

---

## 4. 남은 작업 / 주의
- **공개 전환**: 업로드 2시간 후 각 영상 재생창 톱니바퀴에서 1080p/4K 옵션 활성 확인 후 Public. (세종은 트리거 예약됨)
- 세종 본편: **다국어 오디오 5 + 자막 5** 스튜디오 추가 남음(반자동/수동).
- 커밋/푸시는 사용자 승인 후에만. 영상 바이너리 Git 금지(로컬/유튜브/R2만).
