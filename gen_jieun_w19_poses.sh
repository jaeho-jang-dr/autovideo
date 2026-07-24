#!/bin/bash
# W19 지은(등산복) 포즈 생성 — agy 나노바나나, jieun_hiking_base 레퍼런스로 외형 100% 고정
# ★걷기 캐릭터와 크기·옷·얼굴·신발·배낭색 완전 동일. 자세·표정만 변화.
# 사용: bash gen_jieun_w19_poses.sh [keys...]   (키 지정 없으면 시트 전체, 4개씩 병렬)
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
BASE='D:\Entertainments\DevEnvironment\autovideo\home_vocab\w15\jieun_hiking_base.png'
OUT='D:\Entertainments\DevEnvironment\autovideo\home_vocab\w19'
SHEET="hangeul_birth_vowels/w19_jieun_pose_prompts.txt"
LOG="logs/gen_jieun_w19_poses.log"
mkdir -p home_vocab/w19 logs

PRE="레퍼런스 캐릭터 이미지 '$BASE' 의 인물 '지은'을 100% 동일하게 유지하라: 동그란 얼굴에 점 두 개 눈과 옅은 미소, 크림색 피부, 긴 웨이브 머리(밝은 갈색, 가슴까지), **빨강과 검정 배색의 등산 재킷(가슴 부분은 빨강, 어깨와 소매는 검정, 앞지퍼, 세운 옷깃)**, **검정 등산 배낭(어깨끈이 앞으로 보이고 옆주머니 있음)**, **진회색 등산 바지(무릎 부분이 약간 진함)**, **갈색 등산화**, 굵은 검정 외곽선의 플랫 컬러 카툰 스타일. ⚠️얼굴형·이목구비 스타일·머리모양·머리색·재킷의 색과 배색·배낭·바지색·신발·체형·전체 키(머리끝에서 발끝까지의 비율)는 절대 바꾸지 말고 오직 자세와 표정만 바꿔라. 표정(눈·입 모양)은 아래 자세의 감정에 맞게 자연스럽게 바꿔도 된다. 자세(pose): "
SUF=". 전신이 머리끝부터 발끝(등산화까지) 다 보이게, 화면 중앙 배치, 다른 포즈와 키가 똑같아 보이도록 같은 크기로, 순백색 단색 배경, 그림자·텍스트·서명·로고 없음, 소품은 자세에 꼭 필요한 최소한만. 배낭은 항상 메고 있다."

# 필터(인자로 준 키만) 준비
declare -A WANT; FILTER=0
if [[ $# -gt 0 ]]; then FILTER=1; for k in "$@"; do WANT[$k]=1; done; fi

gen_one() {
  local key="$1" action="$2"
  local save="${OUT}\\jieun_w19_${key}.png"
  echo "[gen] $key -> $action" >> "$LOG"
  agy -p "${PRE}${action}${SUF} 결과 PNG를 '${save}' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
}

echo "=== W19 jieun pose gen start $(date) (filter=$FILTER) ===" >> "$LOG"
running=0; n=0
while IFS='|' read -r key action; do
  key=$(echo "$key" | xargs); case "$key" in ""|\#*) continue;; esac
  action=$(echo "$action" | xargs)
  if [[ $FILTER -eq 1 && -z "${WANT[$key]}" ]]; then continue; fi
  if [[ -f "home_vocab/w19/jieun_w19_${key}.png" ]]; then echo "[skip] $key" >> "$LOG"; continue; fi
  n=$((n+1)); gen_one "$key" "$action" &
  running=$((running+1))
  if [[ $running -ge 4 ]]; then wait -n 2>/dev/null || wait; running=$((running-1)); fi
done < "$SHEET"
wait
echo "=== done $(date) : $n launched ===" >> "$LOG"
ls -1 home_vocab/w19/*.png 2>/dev/null | wc -l
