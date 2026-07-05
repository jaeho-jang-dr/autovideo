# 최면 영상 — 업로드 준비 완료 (아침 검토용)

작업일: 2026-07-03 밤샘 / 검토: 아침

## ✅ 완료한 재작업
1. **인트로(씬1 회중시계)·아웃트로(씬16 결론) 제거** → 씬 2~15 (14씬) 사용
2. **나레이션 재생성**: Azure **선희(KO)** / **Emma(EN)**, 1.1배속, 씬별 슬롯 맞춤
3. **자막 새로 생성**: `hypnosis_science.ko.srt` · `hypnosis_science.en.srt`
4. **재합성**: 1080p 멀티트랙 — 오디오 한/영 2트랙 + 자막 한/영 소프트 2트랙, 로고+워터마크 커버, BGM 없음
5. **쇼츠 한/영** (크롭+자막 아래로): `hypnosis_short_ko.mp4` · `hypnosis_short_en.mp4`
6. **썸네일 한/영**: `thumb_ko.jpg` · `thumb_en.jpg` (1280×720, <100KB)

## 📦 산출물 (파일)
| 용도 | 파일 |
|------|------|
| 본편(업로드용, SEO명) | `hypnosis_science/hypnosis_brain_science_truth.mp4` (1080p) |
| 본편 4K | `hypnosis_science/hypnosis_brain_science_truth_4k.mp4` |
| 쇼츠 KO/EN | `hypnosis_short_ko.mp4` · `hypnosis_short_en.mp4` |
| 자막 | `hypnosis_science.ko.srt` · `hypnosis_science.en.srt` |
| 썸네일 | `thumb_ko.jpg` · `thumb_en.jpg` |
| 제목·설명(한/영) | `loc_ko.txt` · `loc_en.txt` (DB `video_localizations` 저장됨) |

## 📋 업로드 전 10가지 선행작업 상태
1. ✅ **파일명 SEO** — `hypnosis_brain_science_truth.mp4`
2. ✅ **제목 키워드 앞** — 아래 참조
3. ✅ **4K 업스케일** — `_4k.mp4` 생성 (원본 클립 720p라 화질은 1080p 수준, 코덱버프용)
4. ✅ **설명 첫 3줄 요약** — 아래 참조
5. ✅ **썸네일** — 전용 이미지+제목+로고
6. ⏳ **업로드 기본설정** — 채널 설정(기존)
7. ✅ **카테고리=교육** — 업로드 시 지정
8. ✅ **챕터 7개** — 설명란에 포함
9. ⚠️ **AI 라벨=예** — 업로드 시 반드시: 설명 고지문(포함됨) + 세부설정 "변경된 콘텐츠=예" 체크
10. ⏳ **일부공개→2h후 4K확인→공개** — 업로드 후

## 📝 제목·설명 (붙여넣기용 — loc_*.txt 전문)
**KO 제목**: 최면, 과학일까 사기일까? | 메스머의 사기극부터 뇌과학까지 (플라시보·통증)
**EN 제목**: Is Hypnosis Science or a Scam? | From Mesmer's Fraud to Brain Science (Placebo · Pain)
→ 설명 전문은 `loc_ko.txt` / `loc_en.txt`

## 🎬 아침 업로드 순서 (검토 후)
1. 본편(`_4k.mp4` 또는 1080p) 업로드 → 제목(KO) + 설명(`loc_ko.txt`) + 썸네일(`thumb_ko.jpg`)
2. 카테고리 **교육**, 아동용 아님, **AI="예"**(변경된 콘텐츠) 체크
3. **일부공개**로 게시 → 2h 후 화질 확인 → 공개
4. **자막 업로드**: 동영상 언어=한국어 설정 → KO 자막(`.ko.srt`) → 언어추가 영어 → EN 자막(`.en.srt`)  (제목·설명 영어는 자동입력 스크립트 재사용 가능)
5. **쇼츠 한/영** 별도 업로드
6. 업로드 후 `youtube_uploads` DB 기록 (video_id, url, 태그 "내가 만든 내 동영상") + `video_localizations`의 video_id 갱신

## ⚠️ 참고
- **다국어 오디오 트랙**: 계정에 기능 미개방 → 오디오는 본편 KO만 노출, **영어권은 EN 자막으로 커버**. (파일엔 EN 오디오 임베드돼 있어 기능 열리면 추가 가능)
- **BGM 없음** (원본도 나레이션만). 필요하면 앰비언트 추가 가능.
- 설명의 "오디오·자막 트랙 선택" 문구는 자막 위주로 조정 여지 있음(검토 시 결정).
