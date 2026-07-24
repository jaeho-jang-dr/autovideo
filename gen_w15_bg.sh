#!/bin/bash
# W15 한라산 사계절 명소 배경 22종 — 제미나이 병렬
# ★규칙: 글자·숫자 절대 금지. 화면 왼쪽 아래는 캐릭터 자리(큰 사물 없이 비움). 배경 자체는 충실히.
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
OUT='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\bg'
LOG=logs/gen_w15_bg.log; mkdir -p assets/graphics/bg logs; : > $LOG

COMMON="가로 16:9 (1280x720). 플랫 카툰 일러스트, 굵은 검정 외곽선, 부드러운 파스텔. 아름답고 충실하게 그려라. ⚠️화면 왼쪽~중앙 아래쪽은 캐릭터가 서므로 큰 사물 없이 비교적 비워둔다. ⚠️⚠️그림 안에 글자·숫자·표지판 텍스트·간판을 단 하나도 넣지 마라(표지판·안내판은 빈칸). 사람은 배경에 아주 작은 실루엣으로만."

declare -A P
# 도입/정리
P[bg_w15_halla_view]="제주 들판 너머로 우뚝 솟은 한라산 전경. 완만한 능선의 큰 산, 넓은 초원과 돌담, 파란 하늘. $COMMON"
P[bg_w15_halla_sunset]="노을 지는 한라산 전경. 주황빛 하늘과 실루엣 능선, 평화로운 제주 들판. $COMMON"
# 봄
P[bg_w15_spring_sky]="봄날 한라산 산자락. 연둣빛 새싹, 파란 하늘, 멀리 한라산 능선, 따뜻한 봄 햇살. $COMMON"
P[bg_w15_jindallae]="한라산 진달래밭 대피소 부근. 분홍 진달래가 무리지어 핀 완만한 능선, 나무 대피소가 멀리. $COMMON"
P[bg_w15_seonjakji]="한라산 선작지왓 고원 초원. 봄이면 분홍 산철쭉이 초원을 뒤덮은 '산상 화원', 멀리 백록담 능선, 파란 하늘. $COMMON"
P[bg_w15_cherry]="제주 산자락 벚꽃길. 연분홍 벚꽃이 터널처럼 핀 길, 흩날리는 꽃잎, 봄 하늘. $COMMON"
P[bg_w15_spring_ridge]="맑은 봄날 한라산 능선길. 초록 풀밭과 야생화, 구름 없는 파란 하늘, 완만한 오솔길. $COMMON"
# 여름
P[bg_w15_seongpanak]="한라산 성판악 초록 숲길. 울창한 구상나무와 조릿대가 우거진 여름 숲, 나무 데크길, 녹음이 짙다. $COMMON"
P[bg_w15_1100_summer]="한라산 1100고지 여름 습지. 초록 습지와 나무 데크 산책로, 야생화, 물웅덩이, 파란 하늘. $COMMON"
P[bg_w15_rainy]="비 내리는 한라산 숲길. 회색 하늘에서 빗줄기가 내리고 나뭇잎이 젖어 반짝임, 물웅덩이. $COMMON"
P[bg_w15_saraoreum]="한라산 사라오름 산정호수. 오름 정상 분화구에 고인 맑은 호수, 물에 비친 하늘과 숲, 신비로운 분위기. $COMMON"
P[bg_w15_donnaeko]="한라산 돈내코 원앙폭포 계곡. 에메랄드빛 맑은 계곡물과 작은 폭포, 초록 숲, 시원한 여름. $COMMON"
# 가을
P[bg_w15_eorimok_fall]="한라산 어리목 가을 단풍길. 빨강·주황·노랑으로 물든 단풍나무 길, 파란 가을 하늘. $COMMON"
P[bg_w15_yeongsil]="한라산 영실기암과 오백나한. 병풍처럼 늘어선 거대한 수직 절벽 기암괴석에 단풍이 물든 최고의 절경, 파란 하늘. $COMMON"
P[bg_w15_sara_fall]="가을 사라오름 산정호수. 호수 둘레의 단풍이 물에 비쳐 그림 같은 풍경, 빨강 노랑 단풍. $COMMON"
P[bg_w15_eogsae]="한라산 어리목 만세동산 억새밭. 은빛 억새가 바람에 물결치는 가을 언덕, 높고 파란 하늘. $COMMON"
# 겨울
P[bg_w15_witse_snow]="한라산 윗세오름 눈꽃 능선. 구상나무에 눈이 소복이 쌓이고 눈 내리는 겨울 능선, 하얀 세상. $COMMON"
P[bg_w15_firstsnow]="첫눈 내리는 한라산 능선. 아직 초록이 남은 능선 위로 하얀 첫눈이 흩날리며 살짝 쌓임, 회백색 하늘. $COMMON"
P[bg_w15_snowfield]="눈 덮인 한라산 벌판. 온통 하얗게 눈 쌓인 넓은 설원, 눈사람 만들기 좋은 평평한 눈밭, 파란 겨울 하늘. $COMMON"
P[bg_w15_1100_sanggodae]="한라산 1100고지 상고대. 나뭇가지마다 얼음꽃(상고대)이 피어 보석처럼 반짝이는 겨울 숲, 하얀 서리 세상. $COMMON"
P[bg_w15_byeongpung_snow]="눈 덮인 한라산 영실 병풍바위. 하얀 눈이 쌓인 거대한 수직 절벽, 눈 내리는 겨울 정상부. $COMMON"
P[bg_w15_baengnokdam]="한라산 정상 백록담 설경. 눈 덮인 둥근 분화구 호수와 하얀 정상, 파란 하늘, 장엄한 겨울 절경. $COMMON"

echo "=== W15 배경 $(date) ===" >> $LOG
MAX=4; i=0
for k in "${!P[@]}"; do
  echo "[gen] $k" >> $LOG
  agy -p "${P[$k]} 결과 PNG를 '${OUT}\\${k}.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> $LOG 2>&1 &
  i=$((i+1)); if (( i % MAX == 0 )); then wait; fi
done
wait
echo "=== 결과 ==="; ls -1 assets/graphics/bg/bg_w15_*.png 2>/dev/null | wc -l