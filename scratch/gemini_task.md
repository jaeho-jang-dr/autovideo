# Claude Code 작업 지시서: 기계음 전체 읽기 제거 및 한글 발음 법칙 적용 gTTS 연음 재생 큐 구현

> **감독(Claude Code) 귀하:**
> 조감독(Antigravity)이 설계한 전체 읽기 엔진 개편(기계음 TTS 제거 및 gTTS 낱자 결합 재생)과 한글 발음 오독 수정 명세서입니다.
> 아래 설계를 바탕으로 `web/src/components/GrooveBoard.astro` 파일을 직접 편집하고 검증을 완수해 주십시오.

---

## 🛠 미션 목표

1. **기계음(SpeechSynthesis) 전체 읽기 제거**:
   - `btnSpeakWord` (전체 읽기) 클릭 시 기존의 브라우저 기계음 `speakSentenceNatural(text)` 호출을 비활성화(또는 제거)합니다.
   - 대신 로컬 gTTS 음원(`/audio/jamo/*.mp3`) 낱자들을 연음 법칙대로 순차 재생하는 새로운 E2E 재생 큐 엔진을 연동합니다.
2. **한글 발음 법칙 사전 업데이트 및 발음 가이드 바 반영**:
   - 사용자가 지적한 한글 발음 법칙을 `LOCAL_PHONETIC_MAP`에 보강 반영합니다.
     - `값이 싸다` / `값이`: 발음 `[갑시 싸다]` / `[갑시]` (사용자의 피드백을 반영하여 [갑씨] 대신 [갑시]로 표기 및 매칭).
     - `읽는다`: 발음 `[익는다]` (기존의 잘못된 발음 [일는다] 대신 [익는다]로 교정 및 겹받침 자음 단순화 법칙 해설 추가).
3. **연음/자음접변 gTTS 낱자 결합 재생 큐 구현**:
   - 전체 읽기 시 텍스트 전체를 한글 법칙 치환 맵에 따라 연음화된 발음 텍스트로 1차 치환합니다. (예: `값이 싸다` -> `갑시 싸다`, `읽는다` -> `익는다`, `굳이` -> `구지`).
   - 치환된 발음 텍스트를 낱자 단위로 분해하고, 공백은 350ms 무음, 일반 글자는 80ms 간격으로 gTTS 성우 음성 파일들을 연속 재생시킵니다.
   - 이를 통해 전체 낭독 시 기계음을 원천 배제하고 100% 성우 발음으로 부드럽게 이어서 읽어주는 시스템을 완성합니다.

---

## 📐 세부 설계 명세

### 1. `LOCAL_PHONETIC_MAP` 수정
`web/src/components/GrooveBoard.astro` 파일 내 사전을 다음과 같이 갱신합니다.
- `값이 싸다`: `pron: '[갑시 싸다]'`, `ruleKo: '연음 법칙: 겹받침 ㅄ에서 ㅅ이 뒤의 이로 연음되어 [갑시]로 발음되고, 싸다와 연결됩니다.'`
- `값이`: `pron: '[갑시]'`, `ruleKo: '연음 법칙: 겹받침 ㅄ 뒤에 모음 이가 오면, 뒷자음 ㅅ이 다음 첫소리로 넘어가 [갑시]로 발음됩니다.'`
- `읽는다`: `pron: '[익는다]'`, `ruleKo: '자음 단순화 및 비음화: 겹받침 ㄺ 뒤에 ㄴ이 오면 ㄹ이 탈락하고, ㄱ이 ㄴ을 만나 비음 [ㅇ]으로 변하여 최종적으로 [익는다] 또는 [잉는다]로 발음됩니다.'`

### 2. 발음 치환 및 낱자 연속 재생 큐 연동
- 기존 `playSentence(text)` 함수는 텍스트를 한 글자씩 쪼개 재생하는 로직을 이미 가지고 있습니다.
- `btnSpeakWord` (전체 읽기 버튼) 클릭 핸들러를 수정합니다:
  ```javascript
  if (btnSpeakWord) {
    btnSpeakWord.addEventListener('click', () => {
      const currentText = renderSyllable();
      const finalSyllable = (currentText !== '—') ? currentText : '';
      const fullText = state.word + finalSyllable;
      
      if (fullText.trim()) {
        // 1. 기계음 speakSentenceNatural(fullText) 호출을 제거합니다.
        // 2. 발음 치환 헬퍼 getPhoneticSubstitute(fullText)를 돌려 발음 텍스트를 얻습니다.
        const phoneticText = getPhoneticSubstitute(fullText);
        // 3. 치환된 발음 텍스트로 playSentence를 가동하여 성우 음성 결합 낭독을 진행합니다.
        playSentence(phoneticText);
      }
    });
  }
  ```

---

## 🧪 검증 시나리오

1. **Astro 정적 빌드 검증**: `npm run build`를 구동하여 빌드 타입 오류가 없는지 점검하십시오.
2. **E2E 낭독 및 가이드 검증**:
   - `값이 싸다` 입력 후 `🔊 전체 읽기` 클릭 시 기계음 speechSynthesis 대신 로컬의 `갑.mp3`, `시.mp3`, `싸.mp3`, `다.mp3` 성우 음원 파일들이 연음 규칙을 지키며 차례대로 스피커로 출력되는지 청음하십시오.
   - 화면 하단 발음 설명 바에 `[갑시 싸다]` 및 연음 설명이 나타나는지 시각적으로 확인하십시오.
   - `읽는다` 입력 시에도 `[익는다]` 발음 가이드가 정상 작동하는지 확인하십시오.
