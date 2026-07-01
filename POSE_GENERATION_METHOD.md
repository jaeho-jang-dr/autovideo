# 이미지재생성 (Image Regeneration) — 캐릭터 일관성 포즈 생성 방법

> **기법명: 「이미지재생성」**(image-based image regeneration의 줄임). DB의 캐릭터 **베이스 사진**을
> 레퍼런스로 써서 **같은 캐릭터의 새 동작 사진**을 Google Flow로 일관되게 만드는,
> **2026-06-19 실제 검증된** 방법. 조감독(Gemini)·감독(Claude) 공용 레시피.
> 도구: `scratch/flow_pose.py` (파라미터화). 베이스 제작법은 `CHARACTER_ASSET_METHOD.md` 참조.

---

## 한 줄 요약
DB 베이스 사진 → 새 Flow 프로젝트 → 업로드 → **타일 더보기(⋮)→"프롬프트에 추가"** → 스크립트 입력 →
ENTER → ~45초 → **왼편(최신) "새" 타일** 다운로드(md5 중복검증) → 저장.

## 실행 (한 동작당 한 줄)
```
python scratch/flow_pose.py --ref-key <베이스key> --out-key <동작key> --prompt "<동작 구절(영문)>"
```
- `--ref-key`: DB(`character_assets`) 베이스 사진 key. 정면 동작=`jieun_base_front`, 옆모습 동작(걷기·달리기 등)=`jieun_base_side`.
- `--out-key`: 결과 파일/등록 key (예: `jieun_walking`). 산출물 `home_vocab/<out-key>.png`.
- `--prompt`: 동작 구절만. 스크립트가 캐릭터-일관성 프리픽스/서픽스로 감싼다.
- `--transparent`: 배경 투명(레이어용). 기본은 불투명 원본.

### 검증된 예시
```
# 점프(정면 레퍼런스)
python scratch/flow_pose.py --ref-key jieun_base_front --out-key jieun_jumping \
  --prompt "doing an energetic STAR JUMP high in mid-air: both arms stretched out wide, both legs spread wide apart, both feet off the ground, dynamic symmetric star-shaped jumping pose, front view"

# 걷기(옆모습 레퍼런스, 단일 인물·왼쪽 방향)
python scratch/flow_pose.py --ref-key jieun_base_side --out-key jieun_walking \
  --prompt "walking toward the LEFT in a clear left side profile view, mid-stride with one foot forward, EXACTLY ONE single girl, NOT a walking sequence, no duplicate figure"
```

## 반드시 지킬 것 (실패 → 해결)
1. **업로드 후 타일을 그냥 클릭하면 입력창에 안 들어간다.** 반드시 타일의 **더보기(⋮ "옵션 더보기") → "프롬프트에 추가"** 를 눌러야 레퍼런스가 입력창(컴포저)에 붙는다. (스크립트가 처리)
2. **타이밍**: 업로드 후 사진이 타일로 뜨는 데 **~25초**, 생성은 **~45초**.
3. **다운로드는 "왼편(=최신) 새 타일"만.** 생성 전 타일 src 목록(known)을 기록해 두고, **known에 없는 새 타일**만 잡는다. (단순 leftmost를 믿으면 직전 작업물(예: sitting)을 잘못 잡는 버그가 있었다.)
4. **스테일 방지**: 받은 파일 md5가 기존 `home_vocab/*.png` 중 하나와 같으면 **잘못된 타일** → 저장 취소 후 재시도. (스크립트가 처리)
5. **단일 인물 강제**: 걷기·달리기 등 측면 동작은 모델이 워킹 시퀀스(2명)를 그리는 경향 → 프롬프트에 "EXACTLY ONE single girl, NOT a sequence, no duplicate figure" 를 강하게 넣는다.
6. **크롬 프로필은 한 번에 하나만**: `assets/chrome_profile` 은 한 프로세스만 점유 가능 → **포즈 생성은 동시에 돌리지 말고 순차** 실행(앞 작업 브라우저가 닫힌 뒤 다음).
7. **사용자 크롬 미간섭**: 실패해도 전체 chrome 강제종료 금지. `chrome_profile` 쓰는 크롬만.

8. **기본 이미지 이중화 규칙 (투명 & 불투명)**: Google Flow는 투명 배경 PNG를 인식하지 못하므로, 레퍼런스 참조용인 **불투명(Beige `#F5F5F0` 배경, `*_opaque`)** 이미지와 최종 비디오 합성용인 **로컬 투명 가공 PNG** 두 가지 버전을 한 세트로 생성하여 DB(character_assets)와 스토리지에 동시 등록합니다.

## 생성 후 DB 등록
- Supabase `character_assets` (+ 로컬 `content.db` 미러)에 등록: key, character_id, view, pose, method=`reference2img`, file_path, storage_url, style, tags.
- 등록 스크립트 예: `scratch/save_poses_all.py` (Supabase 업로드+upsert / 로컬 미러 / `techniques` 기록).
