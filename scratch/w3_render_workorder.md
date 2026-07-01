# 작업 지시 — 감독(Claude) → 조감독(Gemini/Antigravity)

## 컨텍스트
3주차(KO-W03, "거센소리와 된소리") 졸라맨 한글교육 영상 **재렌더링**.
감독(Claude)이 사용자 피드백(흔들림 제거·가리키기 제거·반복 축소·단어 띄어쓰기)을
반영해 소스 편집과 DB 재적재(scenario_db_w3.py / build_scene_objects_w3.py)를 **이미 완료**했다.

## 절대 규칙
1. **소스 파일(.py / .json) 수정 금지.** 감독이 이미 모든 편집을 마쳤다. 너는 렌더만 실행한다.
2. 아래 명령을 **순서대로** 실행하고, 각 산출물의 경로/길이/크기와 에러를 그대로 보고한다.
3. 인코딩 깨짐 방지: `$env:PYTHONIOENCODING='utf-8'`.

## 작업 디렉터리
`D:\Entertainments\DevEnvironment\autovideo`

## 실행 명령
```powershell
$env:PYTHONIOENCODING='utf-8'
Set-Location 'D:\Entertainments\DevEnvironment\autovideo'

# 1) 한국어 영상 재렌더
python hangeul_birth_vowels/compile_stickman.py --lang ko --episode KO-W03 --prefix hangeul_w3_stickman

# 2) 영어 영상 재렌더
python hangeul_birth_vowels/compile_stickman.py --lang en --episode KO-W03 --prefix hangeul_w3_stickman

# 3) 웹 미리보기 사본 갱신
Copy-Item hangeul_birth_vowels/hangeul_w3_stickman_ko.mp4 web/public/docs/hangeul_w3_stickman_ko.mp4 -Force
```

## 보고 형식
- `hangeul_w3_stickman_ko.mp4`: 경로 / 길이(초) / 크기(MB)
- `hangeul_w3_stickman_en.mp4`: 경로 / 길이(초) / 크기(MB)
- 에러가 있으면 전체 메시지. 없으면 "no errors".
