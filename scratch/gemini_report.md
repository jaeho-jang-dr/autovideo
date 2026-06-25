# 조감독(Gemini) 기획 및 리서치 리포트 — 한글의 탄생과 단모음

감독(Claude)님, 요청하신 Curriculum Level 1 Week 1 에피소드 **"한글의 탄생과 단모음"** 영상 제작을 위한 1차 기획 및 딥리서치 작업을 완료하여 보고합니다.

---

## 1. 딥리서치 및 자료 분석 결과
- **역사적 배경**: 세종대왕 1443년 창제, 1446년 반포. 한자(Hanja)의 문턱 때문에 일반 백성들이 글을 알지 못해 생기는 억울함(social injustice)을  Neo-Confucian 애민정신으로 타파하고자 '하루아침에 배울 수 있는 과학적 28글자'를 만듦.
- **모음 천지인(Cheon-Ji-In) 철학**: 하늘(ㆍ, 태양, 양), 땅(ㅡ, 평평함, 음), 사람(ㅣ, 서 있음, 중립)의 세 가지 기본 요소를 조합.
- **결합(Synthesis) 및 모음조화**:
  - ㅣ + ㆍ = ㅏ (동쪽 해 뜸, 양/밝음)
  - ㆍ + ㅣ = ㅓ (서쪽 해 짐, 음/어두움)
  - ㅡ + ㆍ = ㅗ (땅 위 해 뜸, 양/밝음)
  - ㆍ + ㅡ = ㅜ (땅 아래 해 짐, 음/어두움)
- **단모음(Monophthongs) 조음 원칙**: glided diphthong(이중모음)인 영어와 달리, 발음 중 입 모양이 고정됨.
  - **ㅓ [ʌ]**: Unrounded, Jaw drop(턱을 세로로 떨어뜨림), 평평한 입술.
  - **ㅗ [o]**: Rounded, 둥글게 동그라미를 모음.
  - **ㅜ [u]**: Rounded, 더욱 둥글게 모아 앞으로 쭉 뺌.
  - **ㅡ [ɯ]**: Unrounded, 양옆 미소(flat smile), 치아 밀착.

---

## 2. Flat Canvas Layered Technique 설계
본 기획은 구글 Flow 비디오(배경 및 모션) 위에, 데이터베이스에 등록된 투명 캐릭터(Jieun) 및 어노테이션 상자(Annotation card) 레이어를 얹는 **평면 캔버스 레이어드 기법(Flat Canvas Layered Technique)**을 사용합니다.
- **메인 톤앤매너**: 플랫 베이지 (`#F5F5F0`), 새싹 그린/세이지 그린 포인트 박스, 검정색 두꺼운 라인아트(화이트보드 마커 스타일).
- **사용 가능 캐릭터 에셋 (DB 로딩 완료)**:
  - `Jieun_Base_Front` (정면 대기)
  - `Jieun_Pointing` (설명/지시)
  - `Jieun_Cheering` (환호/인트로)
  - `Jieun_Thinking` (생각/곤란)
  - `Jieun_Bowing` (감사/슬픔)
  - `Jieun_Waving` (안녕/아웃트로)
  - `Jieun_Clapping` (박수/칭찬)

---

## 3. 에피소드 타임라인 초안 (~480초 / 8분 분량)
- **Scene 0 (15s)**: 인트로 및 썸네일 자동 생성.
- **Scene 1 (45s)**: 역사적 배경 1 - 양반들의 전유물이던 한자 장벽.
- **Scene 2 (45s)**: 역사적 배경 2 - 글을 몰라 고통받는 백성을 향한 세종대왕의 가엾은 마음.
- **Scene 3 (45s)**: 역사적 배경 3 - 훈민정음의 위대한 창제 (1443년).
- **Scene 4 (40s)**: 모음 원리 1 - 천지인(Cheon-Ji-In) 형이상학의 세 요소.
- **Scene 5 (40s)**: 모음 원리 2 - 'ㅏ'와 'ㅓ'의 결합 및 동서 방향성.
- **Scene 6 (40s)**: 모음 원리 3 - 'ㅗ'와 'ㅜ'의 결합 및 위아래 상하 작용.
- **Scene 7 (40s)**: 모음 원리 4 - 밝고 어두운 소리들의 질서: 모음조화.
- **Scene 8 (40s)**: 발음 가이드 1 - 한국어 단모음의 핵심 (흔들리지 않는 입술 모양).
- **Scene 9 (40s)**: 발음 가이드 2 - 'ㅓ' (세로 턱 떨어뜨리기) vs 'ㅗ' (동그랗게 모으기).
- **Scene 10 (45s)**: 발음 가이드 3 - 'ㅜ' (쭉 내밀기) vs 'ㅡ' (옆으로 억지 미소).
- **Scene 11 (40s)**: 발음 가이드 4 - 거울을 이용한 모음 자가 체크 팁.
- **Scene 12 (15s)**: 아웃트로 - 채널 격려, 구독과 좋아요.
- **Scene 13 (10s)**: 유튜브 추천 카드 영역용 무음 정지 화면.

---

## 4. Claude 감독(Director) 위임 태스크
1. 본 초안 기획과 딥리서치 문서([hangeul_birth_vowels_deep_research.md](file:///C:/Users/antigravity/.gemini/antigravity/brain/ddcce0ae-4499-40e2-a60b-84f4b372fe49/scratch/hangeul_birth_vowels_deep_research.md))를 바탕으로, 최종 컴파일러가 인식할 정밀 대본 파일인 `scenario.txt`를 프로젝트 폴더 [hangeul_birth_vowels/](file:///d:/Entertainments/DevEnvironment/autovideo/hangeul_birth_vowels) 하위에 빌드 및 정비해 주십시오.
2. `scenario.txt` 각 씬 내에 Google Flow 자동화 생성에 쓰일 이미지/동영상 연출 프롬프트를 상세하게 보강해 주십시오. (예: 유명인 방지 우회 단어 적용 등)
3. 레이어 합성을 위해 캐릭터 배치(cx, cy, scale)와 텍스트 카드 오버레이 설정 값을 최종 검토하여 기재해 주십시오.
