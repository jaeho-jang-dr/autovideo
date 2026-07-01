너는 조감독(Gemini)이다. 감독(Claude)이 NotebookLM에서 영어 팟캐스트(초급 1·2주차)를 생성해 두었다.
지금 **생성 완료를 기다렸다가 다운로드 → R2 저장 → drjayed.com 배포**까지 한다.

## 배운 핵심 (다운로드 방법)
NotebookLM python 클라이언트의 `download_audio` 는 **async(코루틴)** 라서 반드시 `asyncio.run(...)` 으로 await 해야 한다.
이 로직은 이미 `download_en_podcasts.py` 에 구현돼 있다. 너는 그 스크립트를 실행만 하면 된다.
(영어 팟캐스트 artifact_id: W1=fb575a24-63cc-49aa-8971-1f5859d1bacf, W2=dc3173d8-e056-4b1b-aa4a-d124f247550d / 노트북 cc6092e5-3322-44e8-b65e-dc0e85c2e3ed)

## 작업 (순서대로 쉘에서 실행)
작업 디렉터리: `D:/Entertainments/DevEnvironment/autovideo`

### 1단계: 생성 완료 폴링 + 다운로드 + R2 업로드
```
set PYTHONUTF8=1
python download_en_podcasts.py
```
- 이 스크립트가 두 영어 팟캐스트가 `completed` 될 때까지 30초마다 폴링하고(최대 ~35분),
  완료되면 비동기 다운로드 후 R2 버킷 `drjayed-media` 에 `audio/podcasts/hangeul_week_1_podcast_en.m4a`, `..._2_..._en.m4a` 로 업로드한다.
- 출력에 `OK wk1 ...` `OK wk2 ...` `DONE` 이 보이면 성공. `TIMEOUT` 이면 아직 생성 안 끝난 것 → 5분 뒤 다시 실행.

### 2단계: drjayed.com 배포 (영어 팟캐스트 웹 연결 반영)
```
cd web
call .cf_token.env  (또는 .cf_token.env 의 export 값을 환경변수로 로드)
npm run build
npx wrangler pages deploy dist --project-name drjayed --branch main --commit-dirty=true
```
- `.cf_token.env` 에 `CLOUDFLARE_API_TOKEN`(Pages용)·`CLOUDFLARE_ACCOUNT_ID` 가 있다. PowerShell이면 그 값을 `$env:CLOUDFLARE_API_TOKEN` 등으로 설정 후 실행.
- 배포 성공 시 "Deployment complete" 가 나온다.
- 주의: 영어 팟캐스트(.m4a)는 25MB가 넘어 web/public 에 두면 안 된다. 스크립트가 R2와 scratch에만 저장하므로 build/deploy에는 포함되지 않는다. 절대 web/public/audio/podcasts 로 옮기지 마라.

## 검증
- `https://pub-a8312324e7b445f8a1985f759cddeff7.r2.dev/audio/podcasts/hangeul_week_2_podcast_en.m4a` 가 200/audio 로 열리는지 확인.

## 보고 (필수)
`D:/Entertainments/DevEnvironment/autovideo/scratch/gemini_report.md` 에:
- 다운로드 성공 여부·파일 크기(MB), R2 업로드 키
- 배포 결과(URL)
- 막힌 부분 있으면 정확한 오류
추측으로 가짜로 보고하지 마라. 끝나면 "PODCAST EN DONE" 출력.
