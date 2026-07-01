# 작업 지시서 (감독 Claude → 조감독 Gemini) — 인준 활동 40 + 커플 25 이미지 생성

> 2026-06-20 · 기법: 이미지재생성(Google Flow) · 문서: `POSE_GENERATION_METHOD.md`

## 목표
검증된 단일세션 reference2img 방식으로 다음 65개 캐릭터 이미지를 **연속 생성**한다.
모든 이미지와 **생성에 쓴 프롬프트(flow_prompt)**를 Supabase + SQLite에 기록한다(러너가 자동 수행).

## 감독이 이미 준비해 둔 것 (그대로 실행만)
- 프롬프트(전부 G등급, 구글 정책 안전):
  - `home_vocab/injun_activities_prompts.txt` (인준 활동/야외 40개)
  - `home_vocab/injun_jieun_friends_prompts.txt` (인준+지은 **고등학생 친구** 활동 25개 — 연인 아님)
- 일반화 러너: `scratch/batch_gen.py` (단일세션 + md5 중복검증 + 3회 재시도/브라우저 리부트 + 양 DB에 flow_prompt 기록)
- 베이스 키(불투명베이지, 이미 DB 등록됨): 인준 `injun_navy_front_opaque` / `injun_navy_side_opaque`, 커플 `injun_jieun_handshake_facing_opaque`
- Supabase `character_assets.flow_prompt` 컬럼 추가 완료.

## 실행 (정확히 이 두 명령, 순서대로)
사전: Chrome 프로필이 Google Flow에 로그인돼 있어야 함. 한 번에 하나씩 순차.

```
# 1) 인준 활동 40개 (정면 베이스, 측면 동작은 측면 베이스 자동 라우팅)
python scratch/batch_gen.py --prompts home_vocab/injun_activities_prompts.txt --char injun --ref-key injun_navy_front_opaque --side-ref injun_navy_side_opaque

# 2) 인준+지은 고등학생 친구 25개 (마주보기 베이스)
python scratch/batch_gen.py --prompts home_vocab/injun_jieun_friends_prompts.txt --char injun_jieun --ref-key injun_jieun_handshake_facing_opaque
```

러너는 이미 만들어진 `home_vocab/<key>.png`는 건너뛰고 재등록만 하므로, 중단되면 같은 명령을 다시 실행하면 이어서 진행된다(resume).

## 검증·보고 (감독에게 돌려줄 것)
- 각 이미지: 좌측 '새' 타일만 다운로드, **md5 중복이면 재생성**(러너가 처리). 비어있거나 손상(수십 KB blob) 타일 받지 말 것.
- 생성 수: `ls home_vocab/injun_*.png | wc -l`, 커플 `ls home_vocab/injun_jieun_*.png | wc -l`.
- DB 기록 확인: Supabase `character_assets`(flow_prompt 채워졌는지), SQLite `assets`(flow_prompt).
- 실패/막힌 항목 목록과 로그를 보고. 못 하거나 미흡하면 감독(Claude)이 폴백 처리한다.

## 제약 (필수)
- **구글 Flow 콘텐츠 정책 안전 스크립트만** 사용(이미 프롬프트에 반영 — 손잡기/함께 활동 수준, 신체접촉·로맨스 표현 배제). 프롬프트 임의 변경 금지.
- 캐릭터 일관성 프리픽스/스타일/베이지배경은 러너가 자동 부착 — 프롬프트 파일엔 동작 구절만 둠.
- 불투명/투명 이중화 규칙 유지(러너 transparent=True로 투명 PNG 생성).
