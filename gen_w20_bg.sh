#!/bin/bash
# W20 이태원 배경 23종 생성 — agy 나노바나나, 연속 도시 풍경·왼편 덜 복잡·흰칸/글자 금지
# 사용: bash gen_w20_bg.sh [keys...]  (없으면 전체, 4개씩 병렬)
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
OUT='D:\Entertainments\DevEnvironment\autovideo\home_vocab\w20\bg'
SHEET="hangeul_birth_vowels/w20_bg_prompts.txt"
LOG="logs/gen_w20_bg.log"
mkdir -p home_vocab/w20/bg logs

PRE="한국 서울 이태원 거리 배경 일러스트. 플랫한 만화 배경 스타일, 부드러운 파스텔과 따뜻한 색감, 은은한 외곽선, 밝고 맑은 분위기, 다국적이고 이국적인 거리 느낌. 가로로 넓은 16:9 화면 전체를 하나의 연속된 도시 풍경으로 빈틈없이 꽉 채운다. 장면: "
SUF=". ⚠️화면 왼쪽 영역(등장인물이 설 자리)은 하늘·벽·트인 공간처럼 풍경을 조금 덜 복잡하게(디테일 적게) 하되, 배경은 절대 끊기거나 나뉘지 말고 왼쪽부터 오른쪽까지 자연스럽게 하나로 이어져야 한다. 흰색 빈칸·세로 경계선·네모 박스·화면 분할 절대 금지. **글자·숫자·간판 글씨·상표·로고·서명 절대 없음**(약국·병원·112·119 등은 초록 십자·빨간 십자·파란 표지등 같은 색과 기호로만 암시). 사람은 아주 멀리 흐릿한 실루엣으로만 있고 왼쪽 인물 자리엔 사람 없음. 오직 배경 풍경만."

declare -A WANT; FILTER=0
if [[ $# -gt 0 ]]; then FILTER=1; for k in "$@"; do WANT[$k]=1; done; fi

gen_one() {
  local key="$1" scene="$2"
  local save="${OUT}\\w20_${key}.png"
  echo "[bg] $key -> $scene" >> "$LOG"
  agy -p "${PRE}${scene}${SUF} 결과 PNG를 '${save}' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
}

echo "=== W20 bg gen start $(date) (filter=$FILTER) ===" >> "$LOG"
running=0; n=0
while IFS='|' read -r key scene; do
  key=$(echo "$key" | xargs); case "$key" in ""|\#*) continue;; esac
  scene=$(echo "$scene" | xargs)
  if [[ $FILTER -eq 1 && -z "${WANT[$key]}" ]]; then continue; fi
  if [[ -f "home_vocab/w20/bg/w20_${key}.png" ]]; then echo "[skip] $key" >> "$LOG"; continue; fi
  n=$((n+1)); gen_one "$key" "$scene" &
  running=$((running+1))
  if [[ $running -ge 4 ]]; then wait -n 2>/dev/null || wait; running=$((running-1)); fi
done < "$SHEET"
wait
echo "=== done $(date) : $n launched ===" >> "$LOG"
ls -1 home_vocab/w20/bg/*.png 2>/dev/null | wc -l
