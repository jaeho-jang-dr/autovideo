# 세종대왕과 한글 — 표준 제작 플레이북 (웹페이지 전체 표준)

> 2026-06-30 확정. "세종대왕과 한글" 특별판으로 검증한 **앞으로 이 웹페이지 전체를 만드는 표준 방식**.
> 핵심 원칙: 자료·아티팩트는 **NotebookLM이 자기 소스로** 만든다(내가 정리한 글을 떠먹이지 않는다).
> 영상만 내가(감독) 제작한다. 사람(제작자) 확인 후 진행.

---

## 0. 한 줄 요약 파이프라인
**제목 정함 → NotebookLM 노트북 생성 → 딥리서치로 소스 수집 → 그 소스로 6아티팩트(팟캐스트·슬라이드·노트 ×한/영) → 다운로드 → 웹 업로드 → 같은 소스에서 영상 시나리오 도출 → Flow로 가이드 이미지 → Veo 모션 클립 → moviepy 렌더(한/영) → R2/유튜브 업로드 → DB 기록.**

---

## 1. NotebookLM (6 아티팩트) — `nlm` CLI v0.5.19
도구: `~/AppData/Roaming/Python/Python313/Scripts/nlm`. 로그인 확인 = `nlm notebook list --title`.

```bash
# 1) 노트북 생성 + 별칭
nlm notebook create "세종대왕과 한글"
nlm alias set sejong <notebook_id>
# 2) 딥리서치로 소스 자동 수집(= 노트북 자기 데이터). 필요시 --force(이전 미임포트 태스크 충돌 시)
nlm research start --mode deep --auto-import --notebook sejong "훈민정음 창제 …"
# 3) 6 아티팩트 — 전부 NotebookLM이 자기 소스로 생성. 나는 제목·명령·언어만 준다.
nlm audio  create --notebook sejong --language ko --confirm   # 팟캐스트 한
nlm audio  create --notebook sejong --language en --confirm   # 팟캐스트 영
nlm slides create --notebook sejong --language ko --confirm   # 슬라이드 한
nlm slides create --notebook sejong --language en --confirm   # 슬라이드 영
nlm report create --notebook sejong --language ko --confirm   # 노트 한
nlm report create --notebook sejong --language en --confirm   # 노트 영
nlm studio status --notebook sejong                            # 완성 대기
# 4) 다운로드
nlm download audio|slide-deck|report --notebook sejong --out scratch/nlm/sejong/
```
- ★ 절대 금지: 내가 요약·정리한 텍스트를 1회용 노트북에 떠먹여 아티팩트를 뽑는 짓(=1주차 실패). 반드시 **실제 소스가 든 노트북**이 자기 데이터로 생성.
- 산출물: `scratch/nlm/<proj>/` (팟캐스트 mp3 한/영, 슬라이드 pdf 한/영, 노트 md 한/영) → 웹 업로드(R2+public/docs).

## 2. 영상 시나리오 — 같은 노트북 소스에서 도출
- `nlm research import` 로 추가 딥리서치를 같은 노트북에 누적 → 메모로 묶어 소스로 재투입.
- 시나리오는 **노트북 소스 기반**으로 작성. 톤 = 다정한 이야기꾼·아이 친화·쉬운 말·재미·신기한 지식(TED-Ed 벤치마크). 무거운 소재(살해·중병·죽음)는 덜어냄.
- 산출: `sejong_film/sejong_scenario_light.md`(5막 37장면, KO+EN). **사람 검토/승인 후에만 클립 제작.**

## 3. 영상 제작 — 플랫 레이어드 + Flow/Veo 모션 (★ 검증된 v2 방식)
> AI 풀생성은 왜곡·한글 깨짐 → **가이드 이미지(Flow) + Veo 모션 클립 + moviepy 합성**. 한글 글자/자모는 절대 AI에 안 맡김(정확한 malgun 폰트로 합성).

### 3-1. 가이드(기본) 이미지 — `gen_assets_flow.py`
```bash
# 텍스트→이미지 (배경/장면). 세로 쇼츠는 --aspect 9:16, 본편(유튜브)은 기본 16:9.
python gen_assets_flow.py --prompts <key:prompt파일> --outdir <dir> --no-transparent --yes --force [--aspect 9:16]
# 레퍼런스 변형 (캐릭터 정체성 유지: 같은 인물 다른 동작/구도). ★ 1잡=1세션 독립 실행(배치는 좌측타일 중복버그)
python gen_assets_flow.py --ref-jobs <outkey|ref|prompt파일> --outdir <dir> --no-transparent --yes --force [--aspect 9:16]
```
- `--aspect` 는 Flow UI 비율칩(`9:16`/`crop_9_16`)을 클릭(2026-06-30 추가). 세로 쇼츠 기본 이미지는 9:16로 뽑아야 잘림 없음.
- 캐릭터 정체성: 베이스(real/mid 등)를 ref로 → 5나이대·다양한 구도 변형. 인물은 **중앙 밴드**, 위/아래는 비워 글자·자막 자리 확보.

### 3-2. 모션 클립 — `autoveo_flow.py` (이미지→첫프레임→Veo)
```bash
# 기존 가이드 이미지를 첫 프레임으로 업로드 → '애니메이션 적용' → 모션 프롬프트 → 다운로드
python autoveo_flow.py --prompts <name>_prompts.txt --scene N \
  --upload <이미지.png> --motion "<실제 물리 동작: 붓·손·호흡·빛·연기. 줌 금지, 카메라 고정>"
# 출력: <name>/scene_N.mp4  (9:16 업로드면 9:16 클립). 봇감지 '다시 시도'로 풀림(크롬 죽이지 말 것)
```
- ★ 규칙: 단순 줌인(Ken Burns) 금지. **Veo 모션 클립** 필수. 모션 프롬프트는 실제 동작 변화로 상세히.

### 3-3. 합성·렌더 — moviepy 2.x (`compile_short_v2.py` 패턴)
- **비트마다 움직이는 클립 배정**(정지 프레임 방지) → 비트 길이에 맞춰 미세 슬로우(`MultiplySpeed`). 클립 부족 시 클립 재사용(예: beat4=clip2).
- **떠다니는 한글 자모**: 정확한 malgun 자모를 머리 위·주변 **불규칙 경로**(이중 사인파)로 드리프트, 70% 반투명 금색 글로우.
- **서가/배경 은은하게**: 소프트 베일(약 27% 화이트) 오버레이 → 글자·자모 가독성↑.
- **자막**: 박스 없이 흰 글자 + 테두리 + 드롭섀도. 폰트 `C:\Windows\Fonts\malgunbd.ttf`.
- **로고**: 우하단 워터마크 자리(= Veo 워터마크를 로고로 덮음). 100px.
- **나레이션(★고정)**: 한국어=**Kanna**, 영어=**Alice**(차분). 모델 `eleven_multilingual_v2`, 1.05~1.1배속. ElevenLabs Creator 계정.
- ★ **나레이션 캐시 재사용 = 토큰/크레딧 절약**: mp3는 `audio/*.mp3`에 캐시 → 영상 재렌더는 그대로 재사용(ElevenLabs 호출 0). 대본 줄이 바뀐 비트만 재생성.
- 한글 발음: 자모·단어는 영어판이라도 한국어(ko) 음성 유지(영어성우 한글 금지).

## 4. 산출 규격
- **쇼츠**: 9:16, 강력한 훅("와 신기해"), 애니 스타일, ~20초. KO/EN 각각.
- **본편(유튜브)**: 16:9, ~16분, 광화문 동상 오프닝, 로고 우하단(워터마크 덮기). KO/EN.
- **썸네일**: 한/영, 애니 히어로.

## 5. 배포·기록
- 큰 영상·팟캐스트 → R2 버킷 `drjayed-media`(업로드 전 90% 가드 `r2_guard.py`). 웹은 R2 공개 URL 참조.
- 제작정보는 항상 `channel/content.db`(video_projects/video_clips)에 링크 저장. 영상 바이너리는 로컬/유튜브/R2에만(Git 커밋 금지).

---

## 진행 상황 (2026-06-30)
- 노트북 `sejong`(130 소스), 6아티팩트 다운로드 완료(`scratch/nlm/sejong/`) — 웹 업로드 대기.
- 시나리오 라이트(37장면) 승인. 5나이대 캐릭터 real/anim 완비.
- **쇼츠 KO/EN 완성**(서가 모션 3클립 + 떠다니는 자모 + Kanna/Alice). `sejong_film/shorts/sejong_short_{ko,en}.mp4`, 컴포지터 `compile_short_v2.py`.
- **다음: 본편 16분** — 기본 이미지 10개(16:9) → Veo 클립 → 렌더(Kanna/Alice).
