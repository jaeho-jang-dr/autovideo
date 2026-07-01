너는 한글 교육 영상 제작의 조감독이다. 아래 작업만 정확히 수행하고 결과 파일을 만들어라.

## 작업
훈민정음 앱 **초급 2주차 "기초 자음과 모아쓰기"** 영상용 예시 단어 12개를 만든다.
- 기초 자음 10자: ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅅ ㅇ ㅈ ㅎ
- 모음: ㅏ ㅓ ㅗ ㅜ ㅡ ㅣ ㅐ ㅔ
- 받침 없는(open-syllable) 1~3글자 단어만. 외국인 초급자도 아는 쉬운 단어.

## 출력 (정확히 이 경로에 JSON 파일로만 저장)
경로: `D:/Entertainments/DevEnvironment/autovideo/scratch/gemini_words.json`
형식 (JSON 배열 12개):
[
  {"word":"나","romaja":"na","meaning_en":"I/me","blocks":["ㄴ+ㅏ"]},
  {"word":"고기","romaja":"gogi","meaning_en":"meat","blocks":["ㄱ+ㅗ","ㄱ+ㅣ"]}
]

위 경로에 JSON 파일만 저장하라. 완료하면 "DONE: words saved" 한 줄만 출력하라.
