# 실행 보고서 — Hangeul Curriculum Integration

- **작업자**: Claude Code (감독)
- **일자**: 2026-06-25
- **지시 출처**: Assistant Director Directive (Hangeul 36-week Curriculum Integration)
- **상태**: ✅ 완료 (빌드·인코딩·E2E 검증 통과)

---

## 1. 데이터베이스 스키마 & 마이그레이션

| 항목 | 결과 |
|---|---|
| `supabase/migrations/202606250000_create_hangeul_curriculum.sql` | 기존 파일 검증 후 사용 — 테이블 + `UNIQUE(level,week)` 인덱스 + RLS `read-all` 정책 포함 |
| Supabase Postgres 적용 | psycopg2(`SUPABASE_DB_*`)로 마이그레이션 실행 + **36행 upsert 완료** |
| `channel/content.db` (SQLite 패리티) | 동일 스키마로 `hangeul_curriculum` 생성 + **36행 upsert 완료** |

- 컬럼: `id, level, week, title_ko/en, concept_ko/en, practice_ko/en, application_ko/en, target_letters, created_at` (지시서 스펙 그대로).
- 재실행 안전: 양쪽 모두 `ON CONFLICT(level, week) DO UPDATE` 업서트 → 멱등.

## 2. 시딩 스크립트 — `scripts/seed_curriculum.py`

- 소스 플랜 `scratch/found_curriculum_073ae673-...md`에서 **레벨별 12개 주차 제목을 파싱**해 36주 존재를 교차 검증(초급/중급/고급 각 12개 확인).
- 소스가 제공하는 주차 제목·학습 초점에, **하루 1시간 = 개념(20분)+연습(20분)+적용(20분)** 구조에 맞춘 3단계 본문 + 영문 번역 + `target_letters`를 보강해 36행으로 구성.
- Supabase(베스트에포트) + SQLite(항상) + 정적 JSON 덤프(`web/src/data/curriculum_fallback.json`)를 한 번에 생성.
- 실행 로그(요약):
  ```
  [Build] 36 rows (3 levels x 12 weeks)
  [Parse] 초급/중급/고급: 소스에서 각 12개 주차 제목 추출
  [SQLite]  upserted 36 rows | total 36 (12/12/12)
  [Supabase] migration applied + upserted 36 rows | total 36 (12/12/12)
  [JSON] web/src/data/curriculum_fallback.json (36 weeks)
  ```

## 3. 백엔드 API — `web/src/pages/api/curriculum.ts`

- `GET /api/curriculum` — **Supabase 우선 → 정적 JSON 폴백**.
  - `PUBLIC_SUPABASE_URL/ANON_KEY`가 실제로 설정된 경우에만 Supabase `hangeul_curriculum` 조회.
  - 자격증명이 없거나(정적 빌드 기본) 조회 실패 시 `curriculum_fallback.json`으로 폴백.
- **정적 빌드 안전**: 어댑터가 없는 이 프로젝트 특성상 `prerender=false`를 쓰지 않아 빌드가 깨지지 않음(빌드 시 1회 실행되어 정적 응답으로 산출). 자격증명이 없으면 네트워크 호출 없이 즉시 폴백 → 빌드 행(hang) 방지.
- 응답: `{ source, count, levels:{beginner,intermediate,advanced}, weeks, rewards }`.

## 4. 프런트엔드 대시보드

- `web/src/lib/curriculum.ts` — JSON 로더 + 타입 + 언어 헬퍼(`content.ts`와 동일 패턴).
- `web/src/components/CurriculumView.astro` — 핵심 뷰.
- 페이지: `/curriculum`(ko), `/ko/curriculum`(ko), `/en/curriculum`(en) — 홈 라우팅 패턴과 일치.
- **GNB/푸터**: BaseLayout에 `커리큘럼/Curriculum` 링크 + `active` 상태 추가, `nav_curriculum` i18n 추가.

### UI/UX 구현 체크
- ✅ **Warm Beige & Ink Black** 스코프 테마 (Outfit/Inter 유지, 글래스 패널, 네온 글로우 hover).
- ✅ **탭**: Beginner(초급)/Intermediate(중급)/Advanced(고급).
- ✅ **주차 카드 그리드**: 레벨별 12장 — 주차 번호 + 현지화 제목 + `target_letters`.
- ✅ **잠금/해금**: 해금 카드는 클릭 가능·완전 불투명, 잠금 카드는 opacity 0.5 + 🔒 + 비활성(클릭 무시).
- ✅ **상세 모달**: 3단계 가이드(개념 20m / 연습 20m / 적용 20m) + **레벨별 보상**
  (초급: 획순·연음 발음 애니메이션 / 중급: K-컬처 웹툰·영상 해금 / 고급: TOPIK 모의고사 무료 응시권·뽐내기 대회).

### 게이미피케이션 시뮬레이션 패널
- ✅ 슬라이더: 학습 시간 달성률(0–100%), 주간 게임 점수(0–1000).
- ✅ 해금 판정(클라이언트 계산):
  - 일반 통과: `(학습×0.5) + (점수/1000×100×0.5) ≥ 70%`
  - 우수 프리패스: 점수 ≥ 900
  - 완벽 프리패스: 점수 = 1000
- ✅ 어뷰즈 방지: `localStorage`에 연속 프리패스 카운트, **5회째(>4) → 48시간 쿨다운 락아웃** 타이머(실시간 카운트다운).
- ✅ 샌드박스용 **수동 해금** 버튼 + 진도 초기화 버튼.

## 5. 검증

| 검증 | 결과 |
|---|---|
| `npm run build` (web/) | ✅ **67 페이지** 빌드 성공 (커리큘럼 3 라우트 + `/api/curriculum` + CSS 산출 확인) |
| `python .harness/verify/check_encoding.py` | ✅ 통과 (BOM 0 / 오류 0). 신규·수정 11개 파일 타깃 UTF-8/BOM 스캔도 전부 OK |
| `python .harness/verify/check_links.py` | ⚠️ **파일 부재** — CLAUDE.md가 참조하나 디스크에 존재하지 않음. 추측 실행 금지 규칙에 따라 스킵 |
| 라이브 라우트(dev :4321) | ✅ `/curriculum/`·`/ko/curriculum/`·`/en/curriculum/`·`/api/curriculum` 모두 200, API `source=static count=36 (12/12/12)` |
| Playwright 헤드리스 E2E | ✅ **12/12 통과** (그리드 12장, 초기 1주 해금·2주 잠금, 잠금 카드 모달 차단, 해금 카드 3단계+보상 모달, 가중점수 55.0 공식, 일반통과 해금·스트릭 0 유지, 프리패스 5연속 → 48h 쿨다운) |

## 6. 변경/생성 파일

```
신규  scripts/seed_curriculum.py
신규  web/src/lib/curriculum.ts
신규  web/src/components/CurriculumView.astro
신규  web/src/pages/curriculum.astro
신규  web/src/pages/ko/curriculum.astro
신규  web/src/pages/en/curriculum.astro
신규  web/src/pages/api/curriculum.ts
신규  web/src/data/curriculum_fallback.json        (시드 스크립트 산출)
신규  supabase/migrations/202606250000_create_hangeul_curriculum.sql  (검증)
수정  web/src/layouts/BaseLayout.astro             (GNB/푸터 링크 + active 타입)
수정  web/src/lib/i18n.ts                          (nav_curriculum)
수정  channel/content.db                           (hangeul_curriculum 테이블 + 36행)
수정  .harness/loops/progress.json                 (gitignored — 추적 안 됨)
```

## 7. 참고 / 후속

- 웹 빌드는 정적(어댑터 없음). `/api/curriculum`은 빌드 시점에 **정적 JSON으로 산출**되며, `web/.env`에 `PUBLIC_SUPABASE_URL/ANON_KEY`를 넣으면 라이브 Supabase 조회로 전환됨(코드 변경 불필요).
- 프런트 페이지는 빌드 안정성을 위해 정적 덤프(`curriculum_fallback.json`)를 직접 import(레포의 `content.json` 패턴과 동일). 대본/커리큘럼 변경 시 `python scripts/seed_curriculum.py` 재실행 → 자동 동기화.
- `.harness/verify/check_links.py` 부재는 별도 이슈로 보고함(자동 생성하지 않음).
- 커밋은 `feat/hangeul-curriculum` 브랜치에 로컬로 수행. **푸시/배포는 사용자 확인 후 진행**(기본 브랜치 직접 푸시·외부 배포는 보류).

---
---

# 실행 보고서 — 라우팅 Swap(EN 기본) + 이중언어 토글 강제 + 프로덕션 배포

- **작업자**: Claude Code (감독)
- **일자**: 2026-06-25
- **지시 출처**: Assistant Director Directive — "Hangeul Curriculum Deploy & Bilingual Toggle Enforcement"
- **상태**: ✅ 완료 (빌드·인코딩 검증 통과 + 두 프로덕션 호스트 라이브 검증 완료)

> ⚠️ 협업 참고: 본 디렉티브는 조감독(Gemini)에게도 동시에 지시되어, Gemini가 같은 작업트리에서 라우팅 swap·grammar 페이지·그루브 토글을 병행 실행하고 커밋·머지까지 완료했습니다. Claude(감독)의 편집은 동일 작업트리를 공유했기에 Gemini의 커밋 `7cb9880`에 함께 포함되었으며, **미실행 상태였던 프로덕션 배포(4단계)를 Claude가 마무리**했습니다.

## 1. 라우팅 재구성 (EN 루트 / KO `/ko/`)

| 변경 | 내용 |
|---|---|
| `web/astro.config.mjs` | `defaultLocale: 'ko' → 'en'` (prefixDefaultLocale:false 유지 → en은 접두사 없음, ko는 `/ko`) |
| `web/src/lib/content.ts` | `homeUrl/categoryUrl/lessonUrl` 반전 — en=접두사 없음, ko=`/ko/...` |
| 루트 페이지 → EN | `index / curriculum / groove / lesson/[code] / category/[category]` 를 `lang='en'`, `altUrl="/ko/..."` 로 전환 |
| `ko/` 페이지 → KO | `ko/index`·`ko/curriculum` altUrl을 루트로 수정 + **신규 생성** `ko/groove`, `ko/lesson/[code]`, `ko/category/[category]` (`altUrl="/..."`) |
| `web/src/pages/en/` | **완전 삭제** (라우트 충돌 방지) |
| `BaseLayout` / `HomeView` | 하드코딩된 `/en/...` 네비/푸터 링크를 swap에 맞춰 반전 |

- 빌드 결과: **67 페이지** 생성, `/`(EN)·`/ko/`(KO)·`/curriculum/`·`/ko/curriculum/`·`/groove/`·`/ko/groove/`·`/lesson/*`·`/ko/lesson/*`·`/grammar/`·`/ko/grammar/` 모두 정상. 산출물에 잔존 `/en/` 링크 0건.

## 2. 이중언어 토글 가시성 강제

- **GNB 토글 (`global.css`의 `.lang-switch`)**: 글래스모피즘 캡슐(blur+saturate, 알약형 999px, 활성=네온 그라데이션+글로우, hover=보라 틴트+살짝 떠오름)로 리디자인. BaseLayout 헤더·푸터가 이 스타일을 소비하므로 GNB 노출 모든 화면에 적용.
- **소리 한글(그루브) 플로팅 토글**: GNB가 숨겨지는(`hideHeaderFooter`) 그루브 단독 뷰를 위해 `GrooveBoard.astro` 콕핏 헤더 우측(컨트롤 패널 옆)에 네온 아케이드 테마의 알약형 `KO | EN` 토글(`.gv-lang-switch`) 추가 — `/groove/` ↔ `/ko/groove/` 전환, 현재 언어 active. 홈 버튼도 `homeUrl(lang)` 기반으로 언어 인식화(EN→`/`, KO→`/ko/`). 좁은 화면 대비 `header-actions`에 `flex-wrap` 적용. 중복 없이 정확히 1개.

## 3. 커밋 · 인코딩 검증 · 머지

- 커밋/머지: 조감독이 `7cb9880`(feat: 24-week curriculum + grammar + routing swap + bilingual toggles)로 커밋 → **main에 fast-forward 머지** → `2badcb5`(progress 갱신). Claude 편집(global.css 41줄 diff, `en→ko` groove 리네임, content.ts 등)이 해당 커밋에 포함됨을 `git show --stat`으로 확인.
- 인코딩: `python .harness/verify/check_encoding.py` → **BOM 0 / 오류 0**(스캔 대상 *.html 1건). 추가로 수정/신규 `.astro/.ts/.css` 16개 파일을 직접 BOM 스캔 → 전부 UTF-8 no-BOM. *(`.harness/verify/check_links.py`는 디스크에 존재하지 않아 스킵 — 추측 실행 금지 규칙)*

## 4. 프로덕션 배포 (Claude가 마무리)

| 호스트 | 명령 | 결과 |
|---|---|---|
| **Vercel** | `vercel deploy --prod --yes` (web/) | ✅ 원격 빌드 67페이지, READY → https://drjayed.vercel.app |
| **Cloudflare Pages** | `wrangler pages deploy dist --project-name=drjayed --branch=main` | ✅ 배포 완료(1146 파일) → https://drjayed.com |

## 5. 프로덕션 URL 검증 (두 호스트 동일)

| 경로 | HTTP | html lang | 비고 |
|---|---|---|---|
| `/` | 200 | `en` | EN 기본 — "The World Through a Doctor's Eyes", GNB 토글 EN active / KO→`/ko/` |
| `/ko/` | 200 | `ko` | "의사의 시선으로 해부하는 세상" |
| `/curriculum/` | 200 | `en` | Hunminjeongeum · 12-Week Hangeul Roadmap |
| `/ko/curriculum/` | 200 | `ko` | 훈민정음 · 12주 한글 학습 로드맵 |
| `/groove/` | 200 | `en` | 플로팅 토글 EN active / KO→`/ko/groove/` |
| `/ko/groove/` | 200 | `ko` | 플로팅 토글 KO active / EN→`/groove/` |
| `/lesson/MD-000/`·`/ko/lesson/MD-000/` | 200 | en/ko | |
| `/grammar/`·`/ko/grammar/` | 200 | en/ko | |

## 6. 관찰/권고 사항

- **CF Pages catch-all 200**: `drjayed.com`은 미존재 경로(구 `/en/*`, 임의 경로)를 root `index.html`로 **200 fallback** 서빙 (`/en/`·`/zzz-nope/`·`/` 응답 md5 동일). 이는 **기존 CF Pages 프로젝트 설정**이며 이번 swap과 무관 — Vercel은 동일 경로를 정상적으로 **404** 처리. 새 dist에는 `/en/`이 없음.
- (선택) 구 영어 URL의 SEO-clean 처리를 원하면 `web/public/_redirects`(`/en/* /:splat 301`) + `vercel.json` redirects 추가 후 재배포 권장. 본 디렉티브 범위 밖이라 미적용.
- 커리큘럼 주차 수치(소스 36주 → 화면 타이틀 "12주")는 조감독의 콘텐츠 결정으로 보이며, 데이터-타이틀 정합성은 별도 확인 권장.
