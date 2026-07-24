#!/bin/bash
# W12 인준 교통 특화 신규 포즈 생성 (agy 나노바나나, W10 base 참조로 외모 100% 고정)
# ★사장님 원칙: 옷·신발·얼굴·체형·전체 크기 절대 불변 — 오직 자세만 변경
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
BASE='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\poses\injun_w10_base.png'
OUT='D:\Entertainments\DevEnvironment\autovideo\home_vocab\w12'
SHEET="hangeul_birth_vowels/w12_injun_pose_prompts.txt"
LOG="logs/gen_injun_w12.log"
mkdir -p home_vocab/w12 logs
PRE="레퍼런스 캐릭터 이미지 '$BASE' 의 인물 '인준'을 100% 동일하게 유지하라: 짧은 검은 머리, 점 두 개 눈과 옅은 미소, 남색(navy) 반팔 티셔츠, 베이지(탄색) 긴 바지, 흰색 운동화, 굵은 검정 외곽선의 플랫 컬러 카툰 스타일. ⚠️얼굴·머리모양·옷 색과 모양·신발·체형·전체 키(머리끝에서 발끝까지의 비율)는 절대 바꾸지 말고 오직 자세만 바꿔라. 자세(pose): "
SUF=". 전신이 머리끝부터 발끝까지 다 보이게, 중앙 배치, 다른 포즈와 키가 똑같아 보이도록 같은 크기로, 단색 흰 배경, 텍스트·서명 없음, 소품은 자세에 꼭 필요한 것만."
echo "=== W12 pose gen start $(date) ===" >> "$LOG"
n=0
while IFS='|' read -r key action; do
  key=$(echo "$key" | xargs)
  case "$key" in ""|\#*) continue;; esac
  action=$(echo "$action" | xargs)
  if [[ -f "home_vocab/w12/injun_w12_${key}.png" ]]; then echo "[skip] $key (exists)" >> "$LOG"; continue; fi
  n=$((n+1))
  save="${OUT}\\injun_w12_${key}.png"
  echo "[gen $n] $key -> $action" >> "$LOG"
  agy -p "${PRE}${action}${SUF} 결과 PNG를 '${save}' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
  sleep 6
done < "$SHEET"
echo "=== W12 pose gen done $(date) : $n generated ===" >> "$LOG"
ls -1 home_vocab/w12/*.png 2>/dev/null | wc -l >> "$LOG"
