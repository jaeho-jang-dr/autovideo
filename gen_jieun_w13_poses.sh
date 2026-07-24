#!/bin/bash
# W13 지은 포즈 세트 생성 (agy 나노바나나, 확정 리디자인 B를 레퍼런스로 외모 100% 고정)
# ★사장님 원칙: 얼굴·머리·옷·신발·체형·전체 키 절대 불변 — 자세만 변화
# ★중간 포즈(_a)까지 만들어 동작이 자연스럽게 이어지게 함
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
BASE='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\poses\jieun_w13_base.png'
OUT='D:\Entertainments\DevEnvironment\autovideo\home_vocab\w13'
SHEET="hangeul_birth_vowels/w13_jieun_pose_prompts.txt"
LOG="logs/gen_jieun_w13_poses.log"
mkdir -p home_vocab/w13 logs

PRE="레퍼런스 캐릭터 이미지 '$BASE' 의 인물 '지은'을 100% 동일하게 유지하라: 동그란 얼굴에 점 두 개 눈과 옅은 미소, **긴 웨이브 머리(밝은 갈색, 가슴까지)**, **연노랑 바탕에 작은 꽃무늬가 있는 민소매 롱원피스(종아리 중간 길이, 어깨끈 넓음)**, **베이지색 샌들**, 크림색 피부, 굵은 검정 외곽선의 플랫 컬러 카툰 스타일. ⚠️얼굴·머리모양·머리색·옷의 색과 무늬와 길이·신발·체형·전체 키(머리끝에서 발끝까지의 비율)는 절대 바꾸지 말고 **오직 자세만** 바꿔라. 자세(pose): "
SUF=". 전신이 머리끝부터 발끝까지 다 보이게, 중앙 배치, 다른 포즈와 키가 똑같아 보이도록 같은 크기로, 단색 흰 배경, 그림자·텍스트·서명 없음, 소품은 자세에 꼭 필요한 것만."

echo "=== W13 jieun pose gen start $(date) ===" >> "$LOG"
n=0
while IFS='|' read -r key action; do
  key=$(echo "$key" | xargs)
  case "$key" in ""|\#*) continue;; esac
  action=$(echo "$action" | xargs)
  if [[ -f "home_vocab/w13/jieun_w13_${key}.png" ]]; then echo "[skip] $key" >> "$LOG"; continue; fi
  n=$((n+1))
  save="${OUT}\\jieun_w13_${key}.png"
  echo "[gen $n] $key -> $action" >> "$LOG"
  agy -p "${PRE}${action}${SUF} 결과 PNG를 '${save}' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
  sleep 5
done < "$SHEET"
echo "=== done $(date) : $n generated ===" >> "$LOG"
ls -1 home_vocab/w13/*.png 2>/dev/null | wc -l >> "$LOG"
