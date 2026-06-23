# Claude Code 작업 지시서: 단어 조립판 내 한글 복사/붙여넣기(Paste) 지원 및 성우 낭독 연동

> **감독(Claude Code) 귀하:**
> 조감독(Antigravity)이 설계한 단어 조립판 내 외부 한글 텍스트 복사/붙여넣기(Paste) 지원 및 렌더링 동기화 명세서입니다.
> 아래 설계를 바탕으로 `web/src/components/GrooveBoard.astro` 파일을 직접 편집하고 검증을 완수해 주십시오.

---

## 🛠 미션 목표

1. **HTML 마크업 수정**:
   - 기존 KOR `.word-display-row` 내부의 정적 텍스트 표시용 `<span id="word-text" class="word-text">—</span>`를 사용자 입력 및 페이스트가 가능한 `<input>` 박스로 대체합니다:
   - `<input type="text" id="word-text" class="word-text word-text-input" value="" placeholder="여기에 한글을 붙여넣으세요 (Paste Korean here)" />`
2. **CSS 스타일 정의**:
   - `<style>` 태그 하단에 `.word-text-input` 스타일을 추가합니다.
   - 배경 투명(`background: transparent`), 테두리 제거(`border: none; outline: none;`), 넓이 100% 채움.
   - 폰트 크기, 패밀리, 그림자(text-shadow) 효과는 기존 `.word-text` 스펙을 상속받아 이질감 없이 녹아들도록 처리합니다.
   - 플레이스홀더(`.word-text-input::placeholder`)는 가독성을 해치지 않도록 적절히 흐릿하게(`.opacity: 0.5`) 조율합니다.
3. **JavaScript 이벤트 바인딩 및 동기화**:
   - `updateWordDisplay()` 함수 내에서 `wordTextEl.textContent = ...` 대신 `wordTextEl.value = state.word;` 로 동기화하도록 수정합니다. (단어판이 비었을 땐 placeholder가 나오도록 빈 문자열을 셋합니다.)
   - `#word-text` input 엘리먼트에 `input` 및 `paste` 이벤트 리스너를 달아줍니다.
   - 사용자가 직접 타이핑하거나 텍스트를 붙여넣었을 때 `state.word = wordTextEl.value;` 로 상태를 업데이트합니다.
   - 상태 변경 즉시 `updatePhonetics()` 와 `checkGameAnswer()` 를 실행하여 발음 법칙 가이드 바 및 게임 정답 채점이 실시간으로 연동되어 갱신되도록 처리합니다.
   - 붙여넣은 텍스트가 존재하면 지우기 X 버튼(`btn-clear-all`)도 화면에 즉시 노출(`display: flex`)되도록 연동합니다.

---

## 📐 세부 설계 명세

### 1. CSS 스타일 추가
```css
.word-text-input {
  background: transparent;
  border: none;
  outline: none;
  color: var(--gv-neon-cho);
  width: 100%;
  font-family: inherit;
  font-size: inherit;
  font-weight: inherit;
  text-shadow: 0 0 6px hsl(160, 100%, 50%, 0.3);
}
.word-text-input::placeholder {
  color: var(--gv-text-3);
  font-size: 0.95rem;
  font-weight: 500;
  text-shadow: none;
  opacity: 0.6;
}
```

### 2. JS 붙여넣기 및 입력 리스너 바인딩
```javascript
const wordTextEl = document.getElementById('word-text') as HTMLInputElement;
if (wordTextEl) {
  const syncInput = () => {
    state.word = wordTextEl.value;
    updatePhonetics();
    checkGameAnswer();
    
    const btnClearAll = document.getElementById('btn-clear-all');
    if (btnClearAll) {
      btnClearAll.style.display = state.word ? 'flex' : 'none';
    }
  };
  
  wordTextEl.addEventListener('input', syncInput);
  wordTextEl.addEventListener('paste', () => {
    setTimeout(syncInput, 50); // 클립보드 텍스트가 입력창에 안착된 후 스캔하도록 딜레이
  });
}
```

---

## 🧪 검증 시나리오

1. **Astro 정적 빌드 검증**: `npm run build`를 구동하여 빌드 컴파일 오류가 없는지 점검하십시오.
2. **E2E 복사 붙여넣기 동작 검증**:
   - 조립판 KOR 영역에 마우스 포커스를 두고 외부 한글 텍스트(예: "값이 싸다" 등)를 직접 붙여넣기(`Ctrl+V` 또는 꾹 눌러 페이스트)합니다.
   - 붙여넣은 즉시 텍스트가 조립판에 출력되며, 우측에 `×` 버튼이 팝업되고, 하단에 발음 법칙 해설(`[갑시 싸다]` 및 해설)이 실시간 활성화되는지 확인합니다.
   - 이 상태에서 `🔊 전체 읽기` 버튼 클릭 시 기계음 없이 **2.5배속의 빠른 성우 연속 음성(갑-시-싸-다)**으로 올바르게 낭독되는지 검증하십시오.
