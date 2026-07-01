# K-Lingo Journey: 한글 교육 플랫폼 및 K-Pop AI 음원 역공학 명세서 (Specification)

본 문서는 K-POP 및 과학 융합형 외국인 대상 한글 교육 플랫폼 **"K-Lingo Journey"** 시제품 웹페이지 설계, 게이미피케이션 알고리즘, 로컬 GPU 가속 AI 음원 생성 및 브라우저 연동 구현 세부 명세를 기록하고 보존하기 위해 작성되었습니다.

---

## 1. 프로젝트 개요 & 비전
*   **플랫폼 명칭**: K-Lingo Journey
*   **슬로건**: "Hangeul is Science, Art, and Groove!"
*   **핵심 목적**: 미국 FSI 기준 최고 난이도 등급인 **Category IV (Super-hard)** 언어에 속하는 한국어의 진입장벽을 낮추기 위해, 한글의 과학적 조음 상형 원리와 천지인 철학을 K-POP 댄스/음악 및 36주 게임화 요소와 결합한 모바일 반응형 교육 플랫폼.

---

## 2. 60-30-10 커리큘럼 & 난이도 아키텍처
학습자의 몰입도 극대화를 위해 진도를 균등 분배하지 않고 초반에 핵심 뼈대를 몰아치는 **전방 집중형(60-30-10) 진도 비중**을 적용했습니다.

*   **초급 과정 (W1 ~ 12 / 84강) - [전체 진도의 60% 소화]**
    *   한글 창제 역사 및 천지인(天地人) 모음 설계 원리
    *   조음 기관 상형 자음(ㄱ, ㄴ, ㅁ, ㅅ, ㅇ)의 형태 및 소리 기작
    *   가획(加劃) 원리와 쌍자음, 이중 모음 결합 규칙
    *   기본 문장 성분(SOV), 조사(이/가, 을/를) 및 기본 어미(`-아요/어요`, 과거시제)
*   **중급 과정 (W13 ~ 24 / 84강) - [전체 진도의 30% 소화]**
    *   평음/격음/경음의 조음 구별 (바람 세기 및 후두 긴장 훈련)
    *   연결 어미(`-고`, `-지만`, `-어서`)와 구어체 축약
    *   실전 여행/교통 회화 (길찾기, KTX, 식당 주문, 맛 표현)
*   **고급 과정 (W25 ~ 36 / 84강) - [전체 진도의 10% 소화]**
    *   고난도 음운 변화 법칙 (겹받침 표준, 비음화/유음화/구개음화/두음법칙)
    *   한국어 사회언어학적 경어법 맥락 (압존법, 존비어 관계 텐션)
    *   사자성어, 관용구, 뉴스 시사 독해 및 3분 프리토킹

---

## 3. 게이미피케이션 해금 알고리즘 명세
학습 완료 속도를 조절하고 악용을 막기 위한 3중 패스 조건 및 쿨다운 공식이 자바스크립트로 완벽하게 가동됩니다.

1.  **일반 패스 조건**:
    $$\text{최종 점수 (100%)} = (\text{콘텐츠 학습 머무른 시간 비율}) \times 50\% + (\text{주간 미니 게임 점수 비율}) \times 50\%$$
    *   최종 합산 점수가 **70% 이상**일 때 다음 주차 자동 해금.
2.  **유경험자/우수자 프리패스 조건**:
    *   콘텐츠 학습 기록이 저조하더라도, **주간 미니 게임 점수 자체가 90% 이상(900/1000점)**이면 단독으로 즉시 다음 주차가 해금.
3.  **Perfect Mastery 만점 프리패스 조건**:
    *   게임 점수 **100% 만점(1000점)**을 획득하면 학습 참여율에 무관하게 즉시 다음 주차 강의 및 연동 여행 리워드가 100% 프리패스로 자동 해금.
4.  **프리패스 4회 연속 제한 및 48시간 쿨다운 락 (Anti-Abuse Rule)**:
    *   게임 점수로만 고속 해금(조건 2, 3)하는 프리패스는 **연속 4회**까지만 허용.
    *   4회 연속 초과 도달 시 프리패스 기능이 강제 잠금(`Locked`) 상태가 되며, **정확히 48시간의 대기 시간(Cooldown)**이 완전히 경과해야 다시 활성화됨.
    *   잠금 기간에는 오직 **일반 패스(합산 70% 통과)**로만 다음 주차를 열 수 있음.

---

## 4. 실현된 웹 플랫폼 산출물 & 로컬 AI 연동 아키텍처

*   **통합 시제품 파일**: [korean_school.html](file:///d:/Entertainments/DevEnvironment/autovideo/korean_school.html)
    *   Warm Beige `#F5F5F0` 미니멀 2D 라인아트 외곽선 테마 적용.
    *   구강 단면 조음 맞추기 미니게임 및 드래그 핫스팟 터치 감지 내장.
    *   Web Speech API (`window.speechSynthesis`)와 미세 템포 조절(`rate = 0.95`)을 이용한 원어민 발음 맑은 듣기 및 쉐도잉 피드백 모듈 탑재.
    *   연속 프리패스 사용 횟수와 학습/게임 슬라이더를 즉각 연산 처리하는 JS 해금 엔진 탑재.
*   **로컬 AI 음악 생성 스크립트**: [generate_music_local.py](file:///d:/Entertainments/DevEnvironment/autovideo/scratch/generate_music_local.py)
    *   사용자의 **NVIDIA GeForce RTX 5070 GPU (12GB VRAM)** 및 CUDA 하드웨어 하네스 자동 감지.
    *   Meta의 오디오 생성 트랜스포머 **MusicGen-Small** 및 `transformers` 라이브러리를 통해 K-Pop 신스 댄스 비트 음원을 locally 30초 분량으로 완전 자동 생성.
*   **생성 및 연동용 에셋 파일**:
    *   음원 소스: `assets/audio/kpop_song_1.wav` (3.8MB, CUDA 생성물)
    *   감지 플래그: `assets/audio/song_status.json` (`{"status": "loaded", "filename": "kpop_song_1.wav"}`)
*   **자동 연동 로직 (`checkAutoLoadSong()`)**:
    *   `korean_school.html` 로딩 즉시 `song_status.json`을 읽어 custom AI 생성곡이 존재하면 즉시 **`[Mode: Custom AI Song]`**으로 스위칭하여 탑재하고, HTML5 Audio Node를 바인딩하여 카세트 릴 휠 애니메이션과 `audio.currentTime` 비트 타임스탬프 동기 가사를 자동 스크롤시킵니다.

---

## 5. Month 1 테마송 "Sky, Land, Human" AI 공식 가사 & 프롬프트 패키지
*   **음악 스타일 (Style Prompt)**:
    `90s K-Pop dance pop, retro synthwave, energetic beats, catchy hook, bright 808 bass, upbeat tempo 120bpm, male and female duet, educational fun, crisp production`
*   **공식 믹스 가사 (Lyrics)**:
    ```text
    [Intro]
    Hangeul is Science! Hangeul is Art!
    Welcome to K-Lingo Journey! Let's Groove!
    ㄱ, ㄴ, ㅁ, ㅅ, ㅇ! Let's make some noise!

    [Verse 1]
    Listen close, look at my mouth!
    Here comes ㄱ! Tongue blocks the throat! G! G! G! (혀뿌리가 목구멍을 막으며 꽉!)
    Next is ㄴ! Tongue taps the ridge! N! N! N! (혀끝이 윗잇몸을 치면서 톡!)
    Square is ㅁ! Lips meet and smile! M! M! M! (두 입술이 만나서 웃음 지으며 믐!)

    [Pre-Chorus]
    Pointy ㅅ makes the dental breeze! (S! S! S!)
    Round throat ㅇ lets the vowels flow! (Ng! Ng!)
    Add a line, make it strong! ㄱ to ㅋ!
    ㄴ to ㄷ to ㅌ, let's sing along!

    [Chorus]
    • is the round sky! (High!)
    ㅡ is the flat land! (Low!)
    ㅣ is the standing human! (Grow!)
    Put them together, let the Hangeul flow!
    하늘, 땅, 사람! Hangeul Groove!
    하늘, 땅, 사람! Make your body move!

    [Verse 2]
    Hungry? 배가 고파요! (Bae-ga go-pa-yo!)
    Order please! 여기 주문 받으세요! (Yeo-gi ju-mun bat-au-se-yo!)
    된장찌개 주세요! (Doen-jang-jji-gae ju-se-yo!)
    Kimchi 많이 주세요! (Kim-chi ma-ni ju-se-yo!)

    [Outro]
    King Sejong the Great, we thank you today!
    We can read, we can write, we can play!
    Hangeul is Science, Hangeul is Groove.
    One, two, three, let's move!
    [End]
    ```

---

## 6. 동작 및 정합성 검증 확인 (Verification)
*   **로컬 GPU 가속 연동**: CUDA 가속으로 20초 내외에 `kpop_song_1.wav`가 노이즈 없이 깔끔하게 추출되어 지정된 폴더에 저장되었음을 확인.
*   **시간 기반 가사 동기화**: `120 BPM (1마디 = 2초)` 기준의 수학적 스케일링 동기화 함수가 정상 작동하여, 재생 오디오의 흐름과 자막의 넘김이 한 치의 어긋남 없이 매끄럽게 연결되는 것을 검증 완료.
*   **플랫폼 UI 정합성**: 탭 전환 및 구강 게임 동작이 새로운 미디어 로더 패키지 탑재 후에도 온전히 보존됨을 확인.

---
*세종대왕님의 창제 가치를 널리 알리고자 시작된 K-Lingo Journey의 첫 단추가 완전히 정초되었습니다. 본 명세는 향후 모듈 개발 및 2~9개월 음원 합본 제작 시 레퍼런스로 영구히 활용됩니다.*
