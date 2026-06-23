import re

file_path = r"d:\Entertainments\DevEnvironment\autovideo\web\src\components\GrooveBoard.astro"

new_css = """<style>
/* 화이트 테마 오염 방지 - .groove 스코프로 완전히 격리된 다크 네온 글래스 테마 */
.groove {
  --gv-bg-0: hsl(245 42% 6%);
  --gv-bg-1: hsl(245 35% 10%);
  --gv-surface: hsl(245 30% 15% / 0.55);
  --gv-surface-2: hsl(245 30% 22% / 0.7);
  --gv-border: hsl(255 60% 80% / 0.15);
  --gv-border-active: hsl(255 70% 85% / 0.35);
  --gv-text-0: hsl(250 30% 98%);
  --gv-text-1: hsl(250 18% 78%);
  --gv-text-2: hsl(250 14% 60%);
  
  --gv-neon-cho: hsl(325 100% 64%);
  --gv-neon-jung: hsl(182 100% 50%);
  --gv-neon-accent: hsl(268 100% 66%);
  --gv-grad: linear-gradient(135deg, var(--gv-neon-cho), var(--gv-neon-accent) 55%, var(--gv-neon-jung));
  
  --gv-glow-cho: 0 0 20px hsl(325 100% 64% / 0.45);
  --gv-glow-jung: 0 0 20px hsl(182 100% 50% / 0.45);
  --gv-radius: 20px;
  --gv-radius-sm: 12px;

  box-sizing: border-box;
  width: 100%;
  max-width: 540px; /* 오락기 콕핏 기기 느낌을 위한 컴팩트 가로폭 */
  min-height: 860px; /* 모바일 세로 비율의 긴 화면을 활용하여 상하 길이를 여유있게 늘림 */
  height: calc(100dvh - 32px); /* 모바일 긴 화면에 맞게 */
  margin: 0 auto;
  padding: 16px 12px;
  color: var(--gv-text-0);
  background: radial-gradient(120% 100% at 50% 0%, var(--gv-bg-1), var(--gv-bg-0));
  border: 2px solid var(--gv-border);
  border-radius: var(--gv-radius);
  font-family: 'Outfit', 'Inter', 'Noto Sans KR', sans-serif;
  text-align: left;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7), inset 0 1px 0 hsl(0 0% 100% / 0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.groove-cockpit {
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: space-between;
  gap: 12px;
}

.groove .glass {
  background: var(--gv-surface);
  border: 1px solid var(--gv-border);
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
  border-radius: var(--gv-radius-sm);
  box-shadow: inset 0 1px 0 hsl(0 0% 100% / 0.05);
}

/* 콕핏 헤더 */
.cockpit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--gv-border);
}

.header-main h2 {
  font-size: 1.15rem;
  font-weight: 800;
  margin: 0;
  background: var(--gv-grad);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: -0.02em;
}

.header-actions {
  display: flex;
  gap: 8px; /* 6px -> 8px 여유 */
  align-items: center;
}

.action-mini-btn {
  background: transparent;
  border: 1px solid var(--gv-border);
  color: var(--gv-text-1);
  font-size: 0.85rem; /* 0.7rem -> 0.85rem 누르기 쉽게 스케일 업 */
  padding: 6px 12px; /* 패딩 큼직하게 늘림 */
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-mini-btn:hover {
  color: var(--gv-text-0);
  background: hsl(0 100% 60% / 0.12);
  border-color: hsl(0 100% 60% / 0.3);
}

.home-btn {
  text-decoration: none;
  gap: 3px;
}

.home-btn:hover {
  color: var(--gv-text-0) !important;
  background: hsl(216 100% 50% / 0.15) !important;
  border-color: hsl(216 100% 50% / 0.4) !important;
}

/* 콕핏 모드 선택 스위처 바 */
.cockpit-mode-switcher {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  padding: 4px;
  border-radius: var(--gv-radius-sm);
}

.switcher-btn {
  background: transparent;
  border: none;
  color: var(--gv-text-2);
  font-size: clamp(10px, 2.5vw, 12px);
  font-weight: 800;
  padding: 8px 2px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.switcher-btn:hover {
  color: var(--gv-text-0);
  background: hsl(245 30% 16% / 0.5);
}

.switcher-btn.active {
  background: var(--gv-grad);
  color: #fff;
  box-shadow: 0 4px 12px hsl(268 100% 66% / 0.35);
}

/* 중앙 메인 HUD 모니터 */
.cockpit-main-monitor {
  width: 100%;
  padding: 10px;
  min-height: 160px; /* 세로로 늘림 */
  max-height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
  flex-grow: 1;
}

.monitor-view {
  display: none;
  width: 100%;
  height: 100%;
}

.monitor-view.active {
  display: block;
  animation: fadeInMonitor 0.25s ease-out;
}

@keyframes fadeInMonitor {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}

/* 1. 런치패드 모드 모니터 뷰 내부 display */
.center-display-monitor {
  width: 100%;
  background: radial-gradient(circle at center, hsl(245 40% 10%), hsl(245 50% 3%));
  border: 1.5px solid var(--gv-border-active);
  border-radius: var(--gv-radius-sm);
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 140px; /* 110px -> 140px로 넉넉하게 확장 */
  position: relative;
  box-shadow: inset 0 0 20px rgba(0,0,0,0.9);
}

.syllable-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120px;
}

.syllable {
  font-size: clamp(3.5rem, 12vw, 5.0rem); /* 한글 낱자 크게 스케일 업 */
  font-weight: 900;
  background: var(--gv-grad);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  transition: transform 0.15s cubic-bezier(.2, 1.4, .4, 1);
  filter: drop-shadow(0 0 15px hsl(266 100% 64% / 0.25));
}

.syllable.pop {
  transform: scale(1.15);
}

/* 조음 피드백 */
.anatomy-card {
  position: absolute;
  bottom: 6px;
  left: 6px;
  right: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: hsl(245 40% 6% / 0.95) !important;
  border-radius: 8px !important;
  border-color: var(--gv-border-active);
  z-index: 10;
}

.anatomy-avatar {
  font-size: 1rem;
  background: var(--gv-surface-2);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--gv-border);
}

.anatomy-text strong {
  display: block;
  font-size: 0.72rem;
  color: var(--gv-neon-cho);
}

.anatomy-text p {
  margin: 0;
  font-size: 0.62rem;
  color: var(--gv-text-1);
}

/* 2. 번역 모니터 뷰 */
.english-input-wrapper-card {
  padding: 10px;
  background: hsl(245 35% 8% / 0.5) !important;
  border-radius: var(--gv-radius-sm);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.input-card-title {
  font-size: 0.65rem;
  font-weight: 800;
  color: var(--gv-text-2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

.english-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 14px;
  font-size: 0.9rem;
  color: var(--gv-text-0);
  background: hsl(245 30% 6% / 0.8) !important;
  border: 1px solid var(--gv-border);
  border-radius: 8px;
  outline: none;
  font-family: inherit;
  transition: all 0.2s;
}

.english-input:focus {
  border-color: var(--gv-neon-jung);
  box-shadow: 0 0 10px hsl(182 100% 50% / 0.2);
}

/* 3. 상황 모니터 뷰 */
.situation-helper-section {
  padding: 8px;
  background: hsl(245 35% 8% / 0.5) !important;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.situation-tabs {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
}

.tab-btn {
  background: hsl(245 30% 12% / 0.6);
  border: 1px solid var(--gv-border);
  color: var(--gv-text-2);
  font-size: 0.62rem;
  font-weight: 700;
  padding: 4px 1px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--gv-text-0);
  background: hsl(245 30% 18% / 0.8);
}

.tab-btn.active {
  color: var(--gv-text-0);
  background: hsl(268 100% 66% / 0.15);
  border-color: var(--gv-neon-accent);
}

.phrase-list {
  max-height: 105px; /* 약간 여유 있게 */
  overflow-y: auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 4px;
  padding-right: 2px;
}

.phrase-list::-webkit-scrollbar {
  width: 3px;
}

.phrase-list::-webkit-scrollbar-thumb {
  background: var(--gv-border);
  border-radius: 1.5px;
}

.phrase-card {
  display: flex;
  flex-direction: column;
  padding: 6px 10px;
  background: hsl(245 30% 12% / 0.4);
  border: 1px solid var(--gv-border);
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
}

.phrase-card:hover {
  background: hsl(245 30% 18% / 0.6);
  border-color: var(--gv-neon-jung);
}

.phrase-ko {
  font-size: 1.05rem; /* 한글 텍스트 크게 */
  font-weight: 800;
  color: var(--gv-neon-jung);
}

.phrase-en {
  font-size: 0.72rem;
  color: var(--gv-text-2);
}

/* 4. 게임 모니터 뷰 */
.game-control-card {
  display: flex;
  justify-content: center;
  margin-bottom: 6px;
}

.game-toggle-btn {
  width: 100%;
  max-width: 150px;
  padding: 6px;
  font-size: 0.75rem;
  border-radius: 8px;
}

.game-hud-panel {
  padding: 8px 12px;
  background: hsl(245 40% 5% / 0.85) !important;
  border: 1.5px solid var(--gv-neon-cho);
  border-radius: var(--gv-radius-sm);
}

.game-hud-panel.hidden {
  display: none !important;
}

.hud-score-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}

.hud-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hud-label {
  font-size: 0.52rem;
  font-weight: 800;
  color: var(--gv-text-2);
}

.hud-val {
  font-size: 0.95rem;
  font-weight: 900;
  color: var(--gv-neon-cho);
  text-shadow: var(--gv-glow-cho);
}

.hud-timer-container {
  flex: 1;
  position: relative;
  height: 12px;
  background: hsl(245 35% 8%);
  border-radius: 6px;
  border: 1px solid var(--gv-border);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.timer-bar {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: var(--gv-grad);
  transition: width 0.2s linear;
}

.timer-text {
  font-size: 0.58rem;
  font-weight: 800;
  color: #fff;
  z-index: 2;
}

.hud-quiz-box {
  background: hsl(245 35% 8% / 0.8) !important;
  border-radius: 6px !important;
  padding: 6px 10px !important;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border: 1px solid var(--gv-border);
}

.quiz-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.q-badge {
  font-size: 0.5rem;
  font-weight: 800;
  padding: 1px 3px;
  border-radius: 3px;
}

.q-badge.eng {
  background: hsl(182 100% 50% / 0.15);
  color: var(--gv-neon-jung);
  border: 1px solid hsl(182 100% 50% / 0.3);
}

.q-badge.kor {
  background: hsl(325 100% 64% / 0.15);
  color: var(--gv-neon-cho);
  border: 1px solid hsl(325 100% 64% / 0.3);
}

.q-text {
  font-size: 0.75rem;
  color: var(--gv-text-1);
  margin: 0;
}

.q-target-ko {
  font-size: 1.1rem; /* 한글 퀴즈 텍스트 크게 */
  font-weight: 800;
  color: #fff;
  margin: 0;
}
/* 글로벌 단어 조립판 (세로 넉넉하게 확장하여 받침 짤림 해결 및 약간 상향 정렬) */
.word-board-section {
  display: flex;
  flex-direction: column;
  padding: 8px 14px 16px 14px; /* 위쪽 패딩은 8px로 좁혀 위로 올리고, 아래쪽 패딩은 16px로 넓혀 받침 공간 확보 */
  margin-bottom: 4px;
  background: hsl(245 35% 8% / 0.7) !important;
  border-color: var(--gv-border-active);
  min-height: 80px; /* 64px -> 80px로 넉넉하게 확장 */
  justify-content: flex-start; /* 글자를 그 칸의 약간 위로 쓰여지게 만듦 */
  overflow: visible; /* 잘림 원천 차단 */
}

.word-display-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 32px; /* 24px -> 32px로 높임 */
  transform: translateY(-2px); /* 글자를 약간 위로 들어올림 */
}

.lang-badge {
  font-size: 0.52rem;
  font-weight: 800;
  padding: 1px 4px;
  border-radius: 3px;
}

.lang-badge.eng {
  background: hsl(182 100% 50% / 0.15);
  color: var(--gv-neon-jung);
  border: 1px solid hsl(182 100% 50% / 0.3);
}

.lang-badge.kor {
  background: hsl(325 100% 64% / 0.15);
  color: var(--gv-neon-cho);
  border: 1px solid hsl(325 100% 64% / 0.3);
}

.word-text {
  font-size: clamp(1.35rem, 5.2vw, 1.8rem); /* 단어 조판 한글 크게 스케일 업 */
  font-weight: 900;
  color: var(--gv-text-0);
  word-break: break-all;
  line-height: 1.45; /* line-height를 충분히 주어 받침 짤림 해결 */
  text-shadow: 0 0 15px hsl(182 100% 50% / 0.25);
}

.english-text {
  font-size: clamp(0.85rem, 3.2vw, 1.05rem);
  font-weight: 700;
  color: var(--gv-text-1);
  word-break: break-all;
}

/* AI 에이전트 피드백 */
.agent-section {
  display: flex;
  gap: 8px;
  padding: 8px;
  margin-top: 4px;
  align-items: center;
  background: hsl(245 35% 10% / 0.6) !important;
}

.agent-avatar {
  font-size: 1.2rem;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--gv-surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--gv-border);
  flex-shrink: 0;
}

.agent-chat {
  flex: 1;
}

.chat-bubble {
  font-size: 0.72rem;
  line-height: 1.35;
  color: var(--gv-text-1);
  background: hsl(245 25% 15% / 0.7);
  padding: 6px 10px;
  border-radius: 4px 10px 10px 10px;
  border: 1px solid var(--gv-border);
}

/* 하단 2단 콕핏 키보드 독 */
.cockpit-keyboard-dock {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 8px;
}

.keyboard-pads-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px; /* 자음과 모음을 물리적으로 바짝 밀착 */
  width: 100%;
  margin-bottom: 2px;
}

.keyboard-group-panel {
  display: flex;
  flex-direction: column;
  padding: 6px;
  background: hsl(245 30% 12% / 0.45);
  border: 1px solid var(--gv-border);
  border-radius: var(--gv-radius-sm);
}

.left-pad-panel {
  padding-right: 2px; /* 자음 패널의 우측 패딩 축소로 자모 밀착 극대화 */
}

.right-pad-panel {
  padding-left: 2px; /* 모음 패널의 좌측 패딩 축소로 자모 밀착 극대화 */
}

.panel-label {
  font-size: 0.52rem;
  font-weight: 800;
  color: var(--gv-text-2);
  text-transform: uppercase;
  margin-bottom: 6px;
  letter-spacing: 0.03em;
  text-align: center;
  border-bottom: 1px dashed var(--gv-border);
  padding-bottom: 2px;
}

/* 좌하단 자음 D-pad (대형화) */
.dpad-layout {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 6px;
  width: 100%;
  aspect-ratio: 1;
  max-width: 170px; /* 자음 자판 140px -> 170px로 크게 확장 */
  margin: 0 auto;
  padding: 8px;
  background: hsl(245 35% 5% / 0.8);
  border-radius: 50%;
  border: 2px solid var(--gv-border);
  position: relative;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.9);
}

.dpad-layout button:nth-child(1) { grid-column: 2; grid-row: 1; }
.dpad-layout button:nth-child(2) { grid-column: 1; grid-row: 2; }
.dpad-layout button:nth-child(3) { grid-column: 2; grid-row: 2; }
.dpad-layout button:nth-child(4) { grid-column: 3; grid-row: 2; }
.dpad-layout button:nth-child(5) { grid-column: 2; grid-row: 3; }

/* 3D 기계식 네온 키캡 (키크기 & 한글 자모 초대형화) */
.pad {
  border-radius: 50% !important;
  font-weight: 900 !important;
  font-size: clamp(1.4rem, 5.5vw, 1.8rem) !important; /* 한글 자음/모음 키캡 낱자 크기 대폭 키움 */
  transition: all 0.08s ease !important;
  user-select: none;
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 1;
}

.pad.cho {
  background: linear-gradient(135deg, hsl(325 100% 64%), hsl(325 100% 42%)) !important;
  border: 1px solid hsl(325 100% 75% / 0.4) !important;
  color: #fff !important;
  box-shadow: 
    0 3px 0 hsl(325 100% 22%), 
    0 4px 6px rgba(0, 0, 0, 0.6),
    inset 0 1px 2px rgba(255, 255, 255, 0.4),
    inset 0 -1px 2px rgba(0, 0, 0, 0.3) !important;
}

.pad.cho:active {
  transform: translateY(2px) !important;
  box-shadow: 
    0 1px 0 hsl(325 100% 22%), 
    0 1px 2px rgba(0, 0, 0, 0.6),
    inset 0 1px 1px rgba(255, 255, 255, 0.2),
    inset 0 -1px 1px rgba(0, 0, 0, 0.3) !important;
}

.pad.jung {
  background: linear-gradient(135deg, hsl(182 100% 50%), hsl(182 100% 32%)) !important;
  border: 1px solid hsl(182 100% 75% / 0.4) !important;
  color: #fff !important;
  box-shadow: 
    0 3px 0 hsl(182 100% 16%), 
    0 4px 6px rgba(0, 0, 0, 0.6),
    inset 0 1px 2px rgba(255, 255, 255, 0.4),
    inset 0 -1px 2px rgba(0, 0, 0, 0.3) !important;
}

.pad.jung:active {
  transform: translateY(2px) !important;
  box-shadow: 
    0 1px 0 hsl(182 100% 16%), 
    0 1px 2px rgba(0, 0, 0, 0.6),
    inset 0 1px 1px rgba(255, 255, 255, 0.2),
    inset 0 -1px 1px rgba(0, 0, 0, 0.3) !important;
}

/* 우하단 모음 Action-pad */
.action-layout {
  display: flex;
  justify-content: space-around;
  gap: 6px;
  margin-bottom: 6px;
  padding: 10px 6px; /* 패딩 넓혀 키 크기 확보 */
  background: hsl(245 35% 6% / 0.5);
  border-radius: 8px;
}

/* BGM 플레이어 위젯 */
.music-player-widget {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  border-radius: 8px !important;
  background: hsl(245 35% 14% / 0.4) !important;
  border-color: var(--gv-border);
}

.music-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.disc-icon {
  font-size: 1.1rem;
  transform-origin: center;
}

.disc-icon.spinning {
  animation: spinDisc 3s linear infinite;
}

.track-details {
  display: flex;
  flex-direction: column;
}

.track-title {
  font-size: 0.58rem;
  font-weight: 700;
  color: var(--gv-text-0);
  white-space: nowrap;
}

.status-indicator {
  font-size: 0.52rem;
  color: var(--gv-text-2);
  font-family: monospace;
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.player-btn {
  background: var(--gv-grad);
  border: none;
  color: #fff;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
  transition: transform 0.1s;
}

.player-btn:active {
  transform: scale(0.9);
}

.player-btn .play-icon {
  font-size: 0.52rem;
}

/* 미니 이퀄라이저 */
.eq-container {
  display: flex;
  align-items: flex-end;
  gap: 1.5px;
  height: 10px;
  width: 14px;
}

.eq-bar {
  width: 2px;
  height: 1.5px;
  background-color: var(--gv-neon-jung);
  border-radius: 0.5px;
}

.eq-container.active .eq-bar {
  animation: bounceEq 0.8s ease-in-out infinite alternate;
}

.eq-container.active .eq-bar:nth-child(1) { animation-delay: 0.1s; animation-duration: 0.6s; }
.eq-container.active .eq-bar:nth-child(2) { animation-delay: 0.3s; animation-duration: 0.9s; }
.eq-container.active .eq-bar:nth-child(3) { animation-delay: 0.0s; animation-duration: 0.7s; }
.eq-container.active .eq-bar:nth-child(4) { animation-delay: 0.2s; animation-duration: 0.8s; }

@keyframes bounceEq {
  0% { height: 1.5px; }
  100% { height: 10px; }
}

/* 2단 하단 제어 패널 (중간 기능 키들 아래로 내리고 크기 대폭 확장) */
.bottom-controls-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px; /* 간격 확장 */
  width: 100%;
}

.mic-lang-row {
  grid-column: span 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 4px;
}

.control-btn {
  background: var(--gv-surface);
  border: 1px solid var(--gv-border);
  color: var(--gv-text-0);
  font-size: 1.05rem; /* 중간 기능 키 글자 키움 */
  font-weight: 800; /* 두껍게 */
  padding: 14px 4px; /* 터치하기 좋은 패딩 */
  border-radius: 12px; /* 둥글게 */
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  white-space: nowrap;
  height: 54px; /* 높이 확실히 늘림 */
}

.control-btn:hover {
  background: var(--gv-surface-2);
}

.control-btn:active {
  transform: scale(0.95);
}

.backspace-btn:hover {
  color: hsl(350, 100%, 65%);
  border-color: hsl(350 100% 65% / 0.3);
  background: hsl(350 100% 65% / 0.06);
}

.space-btn:hover {
  color: var(--gv-neon-jung);
  border-color: hsl(182 100% 50% / 0.3);
  background: hsl(182 100% 50% / 0.06);
}

.enter-btn {
  background: hsl(245 40% 16% / 0.6);
  border-color: var(--gv-border-active);
}

.enter-btn:hover {
  color: var(--gv-neon-cho);
  border-color: hsl(325 100% 64% / 0.4);
  background: hsl(325 100% 64% / 0.08);
}

.speak-btn {
  background: var(--gv-grad) !important;
  border: none !important;
  color: #fff !important;
}

.speak-btn:hover {
  filter: brightness(1.1);
}

/* 마이크 버튼 (알약형 캡슐 키우고 폰트 확대) */
.mic-btn-fab {
  position: relative;
  background: hsl(182 100% 50% / 0.08);
  border: 1px solid var(--gv-neon-jung);
  width: auto;
  flex: 1;
  height: 48px; /* 38px -> 48px */
  border-radius: 24px !important; /* 19px -> 24px */
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.4);
}

.mic-btn-fab:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
  border-color: var(--gv-border);
  background: var(--gv-surface);
}

.mic-btn-fab:not(:disabled):hover {
  background: hsl(182 100% 50% / 0.15);
  box-shadow: 0 4px 10px hsl(182 100% 50% / 0.3);
}

.mic-icon {
  font-size: 0.95rem; /* 글자 키움 */
  font-weight: 800;
  color: var(--gv-neon-jung);
  z-index: 2;
  white-space: nowrap;
}

.mic-glow-ring {
  position: absolute;
  inset: -1px;
  border-radius: 24px;
  border: 1.5px solid var(--gv-neon-jung);
  opacity: 0;
  pointer-events: none;
  z-index: 1;
}

.mic-btn-fab.recording {
  border-color: var(--gv-neon-cho) !important;
  background: hsl(325 100% 64% / 0.15) !important;
  box-shadow: 0 0 10px hsl(325 100% 64% / 0.4) !important;
}

.mic-btn-fab.recording .mic-glow-ring {
  border-color: var(--gv-neon-cho);
  animation: pulseRing 1.4s cubic-bezier(0.24, 0, 0.38, 1) infinite;
}

.mic-btn-fab.recording .mic-icon {
  color: var(--gv-neon-cho);
}

@keyframes pulseRing {
  0% { transform: scale(1); opacity: 0.8; }
  100% { transform: scale(1.4, 1.6); opacity: 0; }
}

.lang-selector-bar {
  display: flex;
  padding: 2px;
  background: hsl(245 30% 8% / 0.8) !important;
  border: 1px solid var(--gv-border);
  border-radius: 24px !important;
  gap: 2px;
  height: 48px; /* 38px -> 48px */
  align-items: center;
}

.lang-toggle-btn {
  background: transparent;
  border: none;
  color: var(--gv-text-2);
  font-size: 0.85rem; /* 0.65rem -> 0.85rem */
  font-weight: 800;
  padding: 6px 14px;
  border-radius: 22px;
  cursor: pointer;
  transition: all 0.15s;
  height: 100%;
  display: flex;
  align-items: center;
}

.lang-toggle-btn.active {
  background: var(--grad-neon);
  color: #fff;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>"""

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the style block
pattern = re.compile(r"<style>.*?</style>", re.DOTALL)
updated_content = pattern.sub(new_css, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(updated_content)

print("Style successfully replaced!")
