#!/bin/bash
# W20 인준(캐주얼) 포즈 생성 — agy 나노바나나, injun_w16_camping 레퍼런스로 외형 100% 고정
# ★걷기 캐릭터(injun_w20_walk_*)와 크기·옷·얼굴·신발 완전 동일. 자세·표정만 변화.
# 사용: bash gen_injun_w20_poses.sh [keys...]   (키 지정 없으면 시트 전체, 4개씩 병렬)
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
BASE='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\poses\injun_w16_camping.png'
OUT='D:\Entertainments\DevEnvironment\autovideo\home_vocab\w20'
SHEET="hangeul_birth_vowels/w20_injun_pose_prompts.txt"
LOG="logs/gen_injun_w20_poses.log"
mkdir -p home_vocab/w20 logs

PRE="레퍼런스 캐릭터 이미지 '$BASE' 의 인물 '인준'(앳된 남자 대학생)을 100% 동일하게 유지하라: 짧은 검정 머리, 순하고 앳된 둥근 얼굴에 점 두 개 눈과 옅은 미소, 밝은 살구색 피부, **네이비(짙은 남색) 반팔 티셔츠**, **카키(연한 베이지) 긴 바지**, **흰색 운동화**, 굵은 검정 외곽선의 플랫 컬러 카툰 스타일. ⚠️얼굴형·이목구비 스타일·머리모양·머리색·티셔츠 색·바지 색·신발·체형·전체 키(머리끝에서 발끝까지의 비율)는 절대 바꾸지 말고 오직 자세와 표정만 바꿔라. 표정(눈·입·눈썹 모양)은 아래 자세의 감정에 맞게 자연스럽게 바꿔도 된다. 레퍼런스에 있는 텐트 등 소품은 절대 그리지 마라. 자세(pose): "
SUF=". 전신이 머리끝부터 발끝(운동화까지) 다 보이게, 화면 중앙 배치, 다른 포즈와 키가 똑같아 보이도록 같은 크기로, 순백색 단색 배경, 그림자·텍스트·서명·로고 없음, 소품은 자세에 꼭 필요한 최소한(예: 휴대폰)만."

# 필터(인자로 준 키만) 준비
declare -A WANT; FILTER=0
if [[ $# -gt 0 ]]; then FILTER=1; for k in "$@"; do WANT[$k]=1; done; fi

gen_one() {
  local key="$1" action="$2"
  local save="${OUT}\\injun_w20_${key}.png"
  echo "[gen] $key -> $action" >> "$LOG"
  agy -p "${PRE}${action}${SUF} 결과 PNG를 '${save}' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
}

echo "=== W20 injun pose gen start $(date) (filter=$FILTER) ===" >> "$LOG"
running=0; n=0
while IFS='|' read -r key action; do
  key=$(echo "$key" | xargs); case "$key" in ""|\#*) continue;; esac
  action=$(echo "$action" | xargs)
  if [[ $FILTER -eq 1 && -z "${WANT[$key]}" ]]; then continue; fi
  if [[ -f "home_vocab/w20/injun_w20_${key}.png" ]]; then echo "[skip] $key" >> "$LOG"; continue; fi
  n=$((n+1)); gen_one "$key" "$action" &
  running=$((running+1))
  if [[ $running -ge 4 ]]; then wait -n 2>/dev/null || wait; running=$((running-1)); fi
done < "$SHEET"
wait
echo "=== done $(date) : $n launched ===" >> "$LOG"
ls -1 home_vocab/w20/injun_w20_*.png 2>/dev/null | wc -l
