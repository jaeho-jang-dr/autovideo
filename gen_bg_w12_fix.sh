#!/bin/bash
# W12 배경 교정 재생성 — 사장님 지시(2026-07-13):
#   bg_w12_boarding: 열차 '뒷문/정면'이 열린 잘못된 구도 → **열차가 오른편에 옆으로 서고 옆문이 열려야**,
#   왼편(캐릭터 자리)에서 오른편 열차 옆문으로 걸어 들어갈 수 있는 그림.
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
OUT='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\bg'
LOG="logs/gen_bg_w12_fix.log"
mkdir -p logs

COMMON="넓은 가로 16:9 구도. 플랫 카툰 일러스트, 굵은 검정 외곽선, 부드러운 파스텔(하늘색·베이지·연회색·민트). ⚠️화면에 어떤 글자·숫자·상표·간판 텍스트도 절대 넣지 마라(표지판·전광판은 빈칸, 픽토그램/화살표만 허용). 사람은 배경에 실루엣으로 적게."

P_BOARDING="지하철 승강장에서 열차에 타는 장면. ★열차는 화면 오른쪽 절반에 **옆면(측면)이 보이도록 가로로 길게** 서 있고, 그 **옆문(슬라이딩 도어) 하나가 활짝 열려** 열차 내부(좌석·손잡이)가 살짝 보인다. 열차의 앞면이나 뒷면(정면 얼굴)은 절대 보이지 않게, 오직 옆구리만 보이게 그려라. ★화면 왼쪽 절반은 승강장 바닥으로 완전히 비워둔다(캐릭터가 왼쪽에서 오른쪽 열린 옆문 쪽으로 걸어 들어갈 수 있게). 승강장 바닥에 노란 안전선, 천장 조명. $COMMON"

echo "=== bg fix start $(date) ===" >> "$LOG"
rm -f assets/graphics/bg/bg_w12_boarding.png
echo "[gen] bg_w12_boarding (열차 옆문·왼편 비움)" >> "$LOG"
agy -p "${P_BOARDING} 결과 PNG를 '${OUT}\\bg_w12_boarding.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
echo "=== bg fix done $(date) ===" >> "$LOG"
ls -la assets/graphics/bg/bg_w12_boarding.png >> "$LOG" 2>&1
