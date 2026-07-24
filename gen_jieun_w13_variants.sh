#!/bin/bash
# W13 지은 리디자인 후보 6종 (agy 나노바나나)
# ★사장님 지시: 얼굴은 그대로(점 두 눈·옅은 미소·플랫 카툰), 세라복(교복) 대신 예쁜 원피스,
#   구두도 바꾸고, 머리 스타일도 바꿔서 여러 장 → 그중 하나 선택
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
BASE='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\poses\jieun_base_front.png'
OUT='D:\Entertainments\DevEnvironment\autovideo\scratch\jieun_w13'
LOG="logs/gen_jieun_w13.log"
mkdir -p scratch/jieun_w13 logs

FACE="레퍼런스 이미지 '$BASE' 의 인물 '지은'의 **얼굴은 100% 그대로 유지**하라: 동그란 얼굴형, 점 두 개로 표현한 검은 눈, 작은 코, 옅은 미소, 크림색 피부, 굵은 검정 외곽선의 플랫 컬러 카툰 스타일. 얼굴 생김새·표정·화풍은 절대 바꾸지 마라."
POSE="정면을 보고 똑바로 서 있는 전신(머리끝부터 발끝까지 다 보이게), 팔은 자연스럽게 몸 옆에 내림, 중앙 배치."
SUF="단색 흰 배경, 그림자·텍스트·서명 없음. 전신이 잘리지 않게."

declare -A P
P[a_sundress_bob]="${FACE} ★바꿀 것 — 옷: 교복(세라복) 대신 **민트색 여름 원피스**(반팔, 무릎길이, 허리에 얇은 리본 벨트, 밑단이 살짝 퍼지는 A라인). 신발: **흰색 메리제인 구두**(발등에 스트랩). 머리: **단발 보브컷**(턱선 길이, 앞머리 있음, 짙은 갈색). ${POSE} ${SUF}"
P[b_floral_long]="${FACE} ★바꿀 것 — 옷: **연노랑 플라워 프린트 원피스**(민소매, 종아리 중간 길이 롱원피스, 어깨끈 넓음). 신발: **베이지 샌들 구두**(낮은 굽). 머리: **긴 웨이브 머리**(가슴까지 오는 물결 웨이브, 밝은 갈색). ${POSE} ${SUF}"
P[c_navy_ponytail]="${FACE} ★바꿀 것 — 옷: **네이비 셔츠 원피스**(칼라 달린 반팔, 앞 단추, 무릎 위 길이, 흰 벨트). 신발: **흰 스니커즈 대신 남색 로퍼 구두**. 머리: **높은 포니테일**(위로 묶어 흔들리는 꼬리, 짙은 갈색, 앞머리 없이 옆으로 넘김). ${POSE} ${SUF}"
P[d_pink_twintail]="${FACE} ★바꿀 것 — 옷: **연분홍 원피스**(퍼프 반팔, 무릎길이, 가슴 아래 리본, 하얀 레이스 카라). 신발: **분홍 스트랩 구두**(작은 리본 장식). 머리: **양갈래 트윈테일**(귀 옆에서 묶은 두 갈래, 부드러운 갈색). ${POSE} ${SUF}"
P[e_beige_bun]="${FACE} ★바꿀 것 — 옷: **베이지 니트 원피스**(긴팔, 무릎 아래 길이, 심플하고 단정, 얇은 갈색 벨트). 신발: **갈색 앵클 구두**(낮은 굽). 머리: **깔끔한 번 헤어**(뒤로 동그랗게 올려 묶음, 잔머리 조금, 짙은 갈색). ${POSE} ${SUF}"
P[f_skyblue_halfup]="${FACE} ★바꿀 것 — 옷: **하늘색 여름 원피스**(민소매, 무릎길이, 흰 물방울무늬, 어깨에 얇은 흰 가디건 걸침). 신발: **흰색 로우힐 구두**. 머리: **반묶음 하프업**(윗머리만 뒤로 묶고 나머지는 어깨까지 내림, 밝은 갈색, 옆머리 있음). ${POSE} ${SUF}"

echo "=== jieun W13 variants start $(date) ===" >> "$LOG"
for k in a_sundress_bob b_floral_long c_navy_ponytail d_pink_twintail e_beige_bun f_skyblue_halfup; do
  if [ -f "scratch/jieun_w13/${k}.png" ]; then echo "[skip] $k" >> "$LOG"; continue; fi
  echo "[gen] $k" >> "$LOG"
  agy -p "${P[$k]} 결과 PNG를 '${OUT}\\${k}.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
  sleep 5
done
echo "=== done $(date) ===" >> "$LOG"
ls -1 scratch/jieun_w13/*.png 2>/dev/null | wc -l >> "$LOG"
