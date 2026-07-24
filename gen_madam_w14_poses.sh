#!/bin/bash
# W14 마담제이 포즈 생성 — ★agy 4개 병렬 (사장님 지시)
# ★외모 100% 고정(갈색 번+살몬 조끼+흰 스커트+크림 신발), 표정 풍부, 중간동작·앉기·책상동작 포함
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
BASE='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\poses\mj_presenting.png'
OUT='D:\Entertainments\DevEnvironment\autovideo\home_vocab\w14'
SHEET="hangeul_birth_vowels/w14_madam_pose_prompts.txt"
LOG="logs/gen_madam_w14.log"
mkdir -p home_vocab/w14 logs

PRE="레퍼런스 캐릭터 이미지 '$BASE' 의 인물 '마담제이'를 100% 동일하게 유지하라: 갈색 번(위로 올려 묶은 동그란 올림머리)과 얼굴 옆으로 흘러내린 몇 가닥, 점 두 개로 표현한 검은 눈과 옅은 미소, 흰 피부, **연한 주황색(살몬) 조끼/베스트(가슴에 작은 명찰)**, **흰색 스커트**, **크림색 신발**, 굵은 검정 외곽선의 플랫 컬러 카툰 스타일. ⚠️얼굴·머리모양·머리색·옷의 색과 형태·신발·체형·전체 키(머리끝에서 발끝까지의 비율)는 절대 바꾸지 말고 **오직 자세와 표정만** 바꿔라. 자세(pose): "
SUF=". 전신이 머리끝부터 발끝까지 다 보이게, 중앙 배치, 다른 포즈와 키가 똑같아 보이도록 같은 크기로, 단색 흰 배경, 그림자·텍스트·서명 없음, 소품은 자세에 꼭 필요한 것만(의자·책상·노트북·책 등은 자세에 필요하면 함께 그림)."

echo "=== W14 madam pose gen start $(date) ===" >> "$LOG"
MAX=4
i=0
while IFS='|' read -r key action; do
  key=$(echo "$key" | xargs)
  case "$key" in ""|\#*) continue;; esac
  action=$(echo "$action" | xargs)
  [ -f "home_vocab/w14/mj_w14_${key}.png" ] && { echo "[skip] $key" >> "$LOG"; continue; }
  save="${OUT}\\mj_w14_${key}.png"
  echo "[gen] $key" >> "$LOG"
  agy -p "${PRE}${action}${SUF} 결과 PNG를 '${save}' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1 &
  i=$((i+1))
  if (( i % MAX == 0 )); then wait; fi     # ★4개마다 수거(병렬)
done < "$SHEET"
wait
echo "=== done $(date) ===" >> "$LOG"
ls -1 home_vocab/w14/*.png 2>/dev/null | wc -l >> "$LOG"
