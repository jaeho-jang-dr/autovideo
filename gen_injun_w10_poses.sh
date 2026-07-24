#!/bin/bash
# W10 인준 35포즈 일괄 생성 (agy 나노바나나, base 참조로 외모 고정)
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
BASE='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\poses\injun_base.png'
OUT='D:\Entertainments\DevEnvironment\autovideo\home_vocab\w10'
SHEET="hangeul_birth_vowels/w10_injun_pose_prompts.txt"
LOG="logs/gen_injun_w10.log"
mkdir -p home_vocab/w10 logs
PRE="레퍼런스 캐릭터 이미지 '$BASE' 의 인물 '인준'을 100% 동일하게 유지하라: 짧은 검은 머리, 점 두 개 눈과 옅은 미소, 남색(navy) 반팔 티셔츠, 베이지(탄색) 긴 바지, 흰색 운동화, 굵은 검정 외곽선의 플랫 컬러 카툰 스타일. 머리·옷·체형·신발은 절대 바꾸지 말고 오직 자세만 바꿔라. 자세(pose): "
SUF=". 전신이 다 보이게, 중앙 배치, 단색 흰 배경, 텍스트·서명 없음, 소품은 최소화(물건은 나중에 따로 얹음)."
echo "=== gen start $(date) ===" >> "$LOG"
n=0
while IFS='|' read -r key action; do
  key=$(echo "$key" | xargs)
  case "$key" in ""|\#*) continue;; esac
  action=$(echo "$action" | xargs)
  if [[ -f "home_vocab/w10/injun_w10_${key}.png" ]]; then echo "[skip] $key (exists)" >> "$LOG"; continue; fi
  n=$((n+1))
  save="${OUT}\\injun_w10_${key}.png"
  echo "[gen $n] $key -> $action" >> "$LOG"
  agy -p "${PRE}${action}${SUF} 결과 PNG를 '${save}' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
  sleep 6
done < "$SHEET"
echo "=== gen done $(date) : $n generated ===" >> "$LOG"
ls -1 home_vocab/w10/*.png | wc -l >> "$LOG"
