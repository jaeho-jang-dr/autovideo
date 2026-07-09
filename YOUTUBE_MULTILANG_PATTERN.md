# 유튜브 다국어 노출 표준 패턴 (재사용)

> 목표: 외국인 학습자에게 검색·추천 노출. **공개 + 영어우선 SEO + 다국어 자막·제목**.
> 검증됨: 2026-07-08 W1~W8 스페인어 완료, 일·중 진행. 이 순서 그대로 다음 영상·언어에 반복.

## 0. 대전제 (제일 큰 레버)
- **일부공개(unlisted) → 공개(public)** 로 전환해야 색인·검색·추천이 시작됨. 이게 1순위.
- 영어 제목은 **키워드 앞배치**(예: `Learn Korean: ... | ... for Beginners`). 한국어 제목만 있으면 한국인에게만 노출됨.

## 1. 영어 SEO (본 제목·설명·태그)
- 데이터: `youtube_meta.json` (video_id → title, tags[], description)
- 적용: `python yt_update_meta.py <video_id>` (Playwright, 로그인 프로필 `assets/chrome_profile`)
  - `--nosave` 로 먼저 채우기만 검증 → 저장 실행
- 태그: 총 **500자** 한도(개수 아님). 관련 영어 검색어 + 다국어 + 변형.

## 2. 다국어 자막·제목 (핵심 파이프라인) ★
### (a) 자막 SRT 번역 — Gemini 무료
```bash
cat hangeul_birth_vowels/hangeul_wN_stickman_np.en.srt | \
  gemini -m gemini-2.5-flash --yolo "Translate this SRT into natural <LANG>. \
  Keep EXACT same index numbers and timestamps unchanged. Translate ONLY the text lines. \
  Output ONLY the raw SRT, no code fences." | grep -v '^```' \
  > hangeul_birth_vowels/hangeul_wN_stickman_np.<code>.srt
```
- ⚠️ **Gemini가 타임스탬프를 망가뜨림**(끝<시작, `02:13:460` 형식깨짐 등). 번역 후 **반드시 재조립**:
  `python scratch/rebuild_srt.py` — 원본(en) SRT 타임스탬프 + 번역텍스트를 인덱스 매칭해 교체.
  이 오류가 있으면 유튜브 업로드 시 "N행 오류" 다이얼로그로 **자막이 안 올라감**.
### (b) 제목·설명 번역 → DB
- 테이블 `video_localizations (project, video_id, lang, title, description, updated_at)`
- lang 코드: es / ja / zh / pt …

### (c) 디버그 크롬 (CDP 9222) 기동 — 필수
```
run_debug_chrome.bat   # 로그인 프로필 + --remote-debugging-port=9222
```
- ⚠️ 기동 후 **크롬을 죽이거나 다른 CDP로 방해하지 말 것** (배치 중엔 read-only 조회도 자제)

### (d) 언어별 자막 업로드 → 제목·설명 (영상별 순서)
```bash
# 자막: cap_robust.py (★안정판, nav 내장). 마지막 인자 1 = 언어행 없으면 추가
python cap_robust.py <video_id> <UI언어명> hangeul_birth_vowels/hangeul_wN_stickman_np.<code>.srt [1]
# 제목·설명:
python meta_clean.py <video_id> <UI언어명> <code>
```
- **UI언어명**: 스페인어 / 일본어 / 중국어(간체) / 영어 / 포르투갈어(브라질)
- ★ **자막은 `cap_robust.py` 를 쓸 것** (cap_clean/cap_upload은 게시 실패 잦음). 핵심 3가지:
  1. 파일 로드는 **"파일 업로드" 클릭 → `#captions-file-loader` 직접 set** (`input[type=file].last`는 잘못된 input이라 로드 안 됨)
  2. **형식 다이얼로그**("업로드할 자막 파일 형식") 반드시 대기·처리(오류허용 체크 + 계속). 안 하면 빈 게시됨
  3. **게시 버튼 활성화 대기** 후 클릭 (여러 셀렉터). 성공 로그: `=== <언어>: 로드=True 계속=True 게시=OK ===`
  - 단, `게시=OK` 로그도 100% 신뢰금지 → 반드시 `scratch/verify_caps.py` 로 실제 게시 확인
- ★ **제목·설명은 `meta_robust.py`** (meta_clean은 `placeholder="제목*"` 검색 실패로 제목 못넣음). 사용: `python meta_robust.py <vid> <UI언어명> <code>`
  - 핵심: **위치로 번역칸 잡기**(오른쪽 x>900, y순 [0]=제목·[1]=설명) + **더블클릭 + 클립보드(pyperclip) Ctrl+V** + input_value 검증 + 재시도. 탭 없으면 new_page.
  - 성공 로그: `=== <언어>: 제목=True 설명=True 게시=OK (clip=True) ===`. 멱등(재실행 안전).
- DB 로컬 넣기: `scratch/build_ko_localizations.py`류(EN판 로컬 재사용 or 원본 번역). meta는 DB(video_localizations) 읽어 채움.

### (d-2) ★ 한글판(KO 오디오) 영상에도 다국어 자막 필수
- 학습자는 **한국어 오디오 들으며 자기 언어 자막**으로 공부 → KO판 자막이 EN판만큼 중요.
- KO판 자막은 **ko SRT를 번역**해야 함(EN판 타이밍과 다름): `scratch/translate_kosubs.sh`(ko→en/es/ja/zh) → `scratch/rebuild_kosub.py`(ko 타임스탬프 재조립) → `hangeul_wN_kosub.<code>.srt`
- 적용: `python cap_robust.py <KO판_video_id> <UI언어명> hangeul_wN_kosub.<code>.srt 1` (언어추가 포함). 배치=`scratch/ko_caps_batch.sh`

### (e) 배치 (여러 영상)
- `scratch/yt_es_batch.sh` 형태로 영상별 navigate→cap_clean→meta_clean 반복. `&` 없이 실행(추적).

## 3. 검증
```bash
python scratch/verify_es.py   # 각 영상 번역페이지 열어 '<언어>행' 존재 + '게시됨' 수 확인
```

## 4. 표준 언어 세트 (우선순위)
1. **es (스페인어)** — 성장 제일 빠름
2. **ja (일본어)** — 한국어 학습 수요 큼
3. **zh (중국어 간체)** — 수요 큼
4. pt (포르투갈어) 등

## 5. 다음에 쓸 때 (체크리스트)
- [ ] 영상 공개 확인 (unlisted면 공개 전환)
- [ ] 영어 제목·설명·태그 SEO (yt_update_meta)
- [ ] 각 언어: SRT 번역(Gemini)→재조립 → DB 제목·설명 → **cap_robust** → **meta_robust**
- [ ] KO판(한국어 오디오)에도 다국어 자막·제목 (ko SRT 번역)
- [ ] verify_caps / verify_meta 로 게시 확인
- [ ] 태그 500자 + 노출 4대 작업(아래 6·7)

## 6. 태그 500자 (다국어) ★
- 생성: `scratch/build_tags.py`류 — 공통 다국어 베이스 + **레슨/주제별 고유 키워드(앞에 배치)**. 트림은 공통을 뒤에서 제거해 고유 태그 보존.
- ⚠️ **YouTube 글자수 = Σ(len(태그) + 2 if 띄어쓰기 있음) + 쉼표(n-1)**. 한국어 띄어쓰기 태그 많으면 초과. 이 공식으로 **485 이하** 트림(따옴표 여유).
- 적용: `python tags_robust.py <vid> <tags.txt>` — **전체삭제 버튼**(aria-label "모든 태그 삭제") 클릭 or 백스페이스로 비우기 → 클립보드 Ctrl+V → 저장. 502(빨강) 되면 저장 안 됨. 쇼츠도 주제 태그 재사용.

## 7. 노출 4대 작업 (재생목록·고정댓글·최종화면·카드) ★
CDP 9222 + 각 도구. **⚠️ 배치 실행 중 절대 수동 조작 금지**(크롬 독점→충돌, 화면 튐). 배경 요소는 다이얼로그 스코프(y<520)로 회피.
1. **재생목록** `python playlist_add.py <vid> <재생목록명> [create]` — 생성=드롭다운 "새 재생목록"→하위메뉴 "새 재생목록"→`ytcp-dialog #textbox` 제목→만들기→저장. 추가=**검색 금지**(검색창은 전체 유튜브라 타채널 나옴), 다이얼로그 상단 **내 재생목록 카드 직접 클릭**.
2. **고정댓글** `python post_and_pin.py <vid> <comment.txt>` — 워치페이지 스크롤→`#contenteditable-root` 입력→`#submit-button`→`ytd-comment-thread` ⋮→"맨 위에 고정"→확인.
3. **최종화면** `python endscreen.py <vid>` — 세부정보 "엔딩 화면"→**"동영상 1개, 구독 1개" 템플릿 카드(ancestor 클릭)** →시청자맞춤 동영상+구독 자동배치→저장.
4. **카드** `python card.py <vid> <재생목록명>` — "카드"→재생목록 행 [+](모달 y<500 스코프)→**검색 금지** 상단 내 재생목록 카드 클릭→저장.
- 검증됨: 2026-07-09 훈민정음 16 + 과학 6 = 22영상 전부 4대 작업 완료. 배치=`scratch/*_batch.sh`.
