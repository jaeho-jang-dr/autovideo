# 캐릭터 에셋 제작 방법 (일관된 캐릭터) — 재현용 매뉴얼

> 같은 캐릭터(지은·인준 등)를 다양한 포즈로, **머리·얼굴·옷을 일관**되게 그리는 검증된 방법.
> 작성: 감독(Claude). 다음에 또 할 때 이 문서를 그대로 따른다.

---

## 1. 핵심 전략 — "베이스 3장 + 레퍼런스 변형"
1. **베이스 3장 생성**: 캐릭터의 **정면·측면·뒷면 서있는 전신**. 텍스트→이미지로 생성.
   - 캐릭터 식별의 핵심은 **머리카락 색**(지은 = 갈색 긴 머리 + 네이비 세일러 교복).
   - 프롬프트에 `ONE single figure, no character sheet` 를 넣어 **한 명만** 그리게 한다(안 넣으면 여러 figure가 섞임).
2. **레퍼런스 변형**: 그 베이스 3장을 **Flow에 업로드(프롬프트에 추가)** 하고, 포즈 프롬프트
   (`Using the uploaded reference image, keep the EXACT same character … but now …`)를 넣어
   **같은 캐릭터로 모든 포즈**를 생성한다. (정면 포즈→front 레퍼런스, 옆모습→side, 뒷모습→back)

## 2. 도구 — `gen_assets_flow.py` (프로젝트 루트)
- **텍스트→이미지(베이스/사물)**:
  `python gen_assets_flow.py --prompts <key:prompt 파일> --outdir <폴더>`
  - 프롬프트 파일 형식: 한 줄당 `key: 영문 프롬프트`
- **레퍼런스 기반 포즈**:
  `python gen_assets_flow.py --ref-jobs <jobs 파일> --outdir <폴더>`
  - jobs 파일 형식: `outkey | 레퍼런스이미지경로 | 포즈프롬프트`
- 공통: `--force`(기존 덮어쓰기), `--only key1,key2`(특정 것만). 멱등(존재하면 스킵). 헤드드(화면 보임).

## 3. 검증된 세부 기법 (실패 → 해결, 반드시 지킬 것)
- **프롬프트 입력 = 클립보드 붙여넣기(Ctrl+V)**: Flow는 Slate.js 라 타이핑/execCommand 는 모델 갱신 실패 →
  "만들기" 버튼 영구 비활성. `autoveo_flow.fill_prompt` 가 OS클립보드+Ctrl+V 로 해결.
- **캡처 = 타일 다운로드(원본)**: DOM 스크린샷은 *잘못된 타일/렌더 전 프레임/배경 노이즈*를 잡는다 →
  ① **새 타일이 뜰 때까지 대기**(`POSTERS_JS` 개수가 증가할 때까지) → ② **가장 좌측(=최신) 타일의
  ⋮메뉴 → 다운로드 → 원본 크기**. 이게 off-by-one(직전 타일 캡처) 버그의 해결책.
- **투명화 = 가장자리 flood-fill**: 임계값 전체 제거(`make_white_transparent`)는 **캐릭터의 흰옷·얼굴까지
  지운다**. `gen_assets_flow.make_bg_transparent` 가 4모서리에서 연결된 배경만 투명화하고 내부 흰색은 보존.
- **새 프로젝트**: 씬/에셋마다 `open_new_project`(누적 캔버스에서 최신=좌측 타일을 잡음).
- **사용자 크롬 미간섭**: 실패해도 전체 chrome 강제종료/재부팅 금지. `chrome_profile` 쓰는 크롬만 정리.

## 4. 지은(여자아이) 베이스 6장 — 현재 산출물
| 키 | 뷰 | 방식 | 파일 |
|---|---|---|---|
| jieun_base_front | 서있는 정면 | 텍스트→이미지 | home_vocab/jieun_base_front.png |
| jieun_base_side | 서있는 측면(좌) | 텍스트→이미지 | home_vocab/jieun_base_side.png |
| jieun_base_back | 서있는 뒷면 | 텍스트→이미지 | home_vocab/jieun_base_back.png |
| jieun_sitting_front | 의자 정면 | 레퍼런스(front) | home_vocab/jieun_sitting_front.png |
| jieun_sitting_side | 의자 측면 | 레퍼런스(side) | home_vocab/jieun_sitting_side.png |
| jieun_sitting_back | 의자 뒷면 | 레퍼런스(back) | home_vocab/jieun_sitting_back.png |

- 캐릭터 스펙: **Korean schoolgirl Jieun, 갈색 긴 머리, 네이비/화이트 세일러 교복(빨간 스카프, 네이비 주름치마)**.
- 인준(남자아이)도 동일 방법: 베이스 3장(짧은 검은 머리) → 레퍼런스 변형. 프롬프트는 `home_vocab/injun_prompts.txt` 기반.

## 5. 다음 단계
- 이 6장(특히 베이스 3장)을 레퍼런스로 써서 나머지 포즈(eating·reading·running … 25종)를 일관 생성.
- "서있는 중립 포즈"는 지은+인준 함께(both), "동작 포즈"는 각자 단독(solo).
