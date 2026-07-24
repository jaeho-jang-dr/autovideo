#!/bin/bash
# W19 설악산 배경 23종 생성 — agy 나노바나나, 연속 풍경·왼편 덜 복잡·흰칸/글자 금지
# 사용: bash gen_w19_bg.sh [keys...]  (없으면 전체, 4개씩 병렬)
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
OUT='D:\Entertainments\DevEnvironment\autovideo\home_vocab\w19\bg'
SHEET="hangeul_birth_vowels/w19_bg_prompts.txt"
LOG="logs/gen_w19_bg.log"
mkdir -p home_vocab/w19/bg logs

PRE="한국 설악산의 가을 풍경 배경 일러스트. 플랫한 만화 배경 스타일, 부드러운 파스텔과 따뜻한 가을 색감, 은은한 외곽선, 밝고 맑은 분위기. 가로로 넓은 16:9 화면 전체를 하나의 연속된 자연 풍경으로 빈틈없이 꽉 채운다. 장면: "
SUF=". ⚠️화면 왼쪽 영역은 하늘이나 트인 공간처럼 풍경을 조금 덜 복잡하게(디테일 적게) 하되, 배경은 절대 끊기거나 나뉘지 말고 왼쪽부터 오른쪽까지 자연스럽게 하나로 이어져야 한다. 흰색 빈칸·세로 경계선·네모 박스·화면 분할 절대 금지. 사람·동물·글자·숫자·간판 글씨·로고·서명 없음. 오직 풍경 배경만."

declare -A WANT; FILTER=0
if [[ $# -gt 0 ]]; then FILTER=1; for k in "$@"; do WANT[$k]=1; done; fi

gen_one() {
  local key="$1" scene="$2"
  local save="${OUT}\\w19_bg_${key}.png"
  echo "[bg] $key -> $scene" >> "$LOG"
  agy -p "${PRE}${scene}${SUF} 결과 PNG를 '${save}' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
}

echo "=== W19 bg gen start $(date) (filter=$FILTER) ===" >> "$LOG"
running=0; n=0
while IFS='|' read -r key scene; do
  key=$(echo "$key" | xargs); case "$key" in ""|\#*) continue;; esac
  scene=$(echo "$scene" | xargs)
  if [[ $FILTER -eq 1 && -z "${WANT[$key]}" ]]; then continue; fi
  if [[ -f "home_vocab/w19/bg/w19_bg_${key}.png" ]]; then echo "[skip] $key" >> "$LOG"; continue; fi
  n=$((n+1)); gen_one "$key" "$scene" &
  running=$((running+1))
  if [[ $running -ge 4 ]]; then wait -n 2>/dev/null || wait; running=$((running-1)); fi
done < "$SHEET"
wait
echo "=== done $(date) : $n launched ===" >> "$LOG"
ls -1 home_vocab/w19/bg/*.png 2>/dev/null | wc -l
