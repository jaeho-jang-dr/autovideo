너는 조감독(Gemini)이다. 감독(Claude) 지시. 방금 확장한 `scratch/w3_scenario_v2.json` 이 **너무 길다(약 10분)**. 목표는 **약 7분**이다.

입력: `D:/Entertainments/DevEnvironment/autovideo/scratch/w3_scenario_v2.json`
출력(딱 1개): `D:/Entertainments/DevEnvironment/autovideo/scratch/w3_scenario_v3.json` — 같은 스키마, UTF-8(BOM 없음).

## 트림 규칙 (각 씬을 줄여라)
- **각 씬의 `script_kr` 를 공백 포함 약 120~150자로 줄여라.** (현재 평균 ~248자 → 절반 가까이 컷)
- 따라 읽기 반복은 **1번만** 남기고(2번 반복은 1번으로), 군더더기·중복 설명 제거. 핵심만 또박또박.
- `script_en` 도 그에 맞춰 비슷한 비율로 짧게.
- `duration_sec` 도 줄인 글에 맞게(합계 380~430).
- **16개 씬·순서·교육 사실·따옴표 토큰은 그대로 유지.** (거센=ㅋㅌㅍㅊ/가획, 된=ㄲㄸㅃㅆㅉ/쌍자음, 휴지실험, 개-캐-깨)
- 따옴표는 다음만 사용(새 단어 따옴표 금지): 낱자 'ㄱ'~'ㅉ'(ㄱㄷㅂㅈㅅㅋㅌㅍㅊㄲㄸㅃㅆㅉ), 단어 '코''타조''포도''치마''까치''꼬리''땅''빵''개''캐''깨''자''차''짜'.

## 보고
- `scratch/w3_scenario_v3.json` 만 저장, "W3 TRIM DONE" 출력. JSON 유효성 확인. 16씬 모두. 각 script_kr 가 대략 120~150자인지 스스로 확인.
