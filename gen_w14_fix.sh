#!/bin/bash
# W14 교정 자산 재생성 — 포즈2(sleep 누움, rest_sit 비치체어) + 배경2(TV거실, 침대없는밤방)
# ★agy 4개 병렬. 포즈=흰배경(컷아웃 대상)→home_vocab/w14, 배경→assets/graphics/bg
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
LOG="logs/gen_w14_fix.log"
mkdir -p logs
REF='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\poses\mj_w14_presenting.png'
OUTP='D:\Entertainments\DevEnvironment\autovideo\home_vocab\w14'
OUTB='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\bg'

# 옛 포즈 삭제(재생성/재컷아웃 위해) — 리터럴 경로
rm -f /d/Entertainments/DevEnvironment/autovideo/home_vocab/w14/mj_w14_sleep.png
rm -f /d/Entertainments/DevEnvironment/autovideo/home_vocab/w14/mj_w14_rest_sit.png
rm -f /d/Entertainments/DevEnvironment/autovideo/assets/graphics/poses/mj_w14_sleep.png
rm -f /d/Entertainments/DevEnvironment/autovideo/assets/graphics/poses/mj_w14_rest_sit.png

PRE="레퍼런스 캐릭터 이미지 '${REF}' 의 인물 '마담제이'를 100% 동일하게 유지하라: 갈색 번(위로 올려 묶은 동그란 올림머리)과 얼굴 옆으로 흘러내린 몇 가닥, 점 두 개로 표현한 검은 눈과 옅은 미소, 흰 피부, 연한 주황색(살몬) 조끼/베스트(가슴에 작은 명찰), 흰색 스커트, 크림색 신발, 굵은 검정 외곽선의 플랫 컬러 카툰 스타일. ⚠️얼굴·머리모양·머리색·옷의 색과 형태·신발·체형은 절대 바꾸지 말고 오직 자세와 표정만 바꿔라. 자세(pose): "

SLEEP="침대(낮은 매트리스)에 옆으로 누워 평온하게 자는 모습. ★머리는 화면 오른쪽, 발끝은 왼쪽을 향하게 옆으로 누움. 눈은 감고 편안한 표정, 베개를 베고 이불을 가슴까지 덮음. 몸 전체가 가로로 길게 누운 옆모습(옆에서 본 구도). 살몬 조끼와 흰 스커트가 보이게."
SLEEP_SUF=". ★전신이 머리끝부터 발끝까지 하나도 잘리지 않고 다 보이게, 누운 몸 전체가 캔버스 안에 여유있게 들어오도록 그려라(서 있을 때의 키 길이만큼 가로로 눕힌 크기). 낮은 침대/매트리스와 베개·이불만 함께 그리고 다른 가구는 없음. 단색 흰 배경, 그림자·텍스트·서명 없음."

REST="해변용 접이식 데크체어(비치 라운지 체어)에 비스듬히 기대 편히 쉬는 모습. 등을 뒤로 기대고 두 다리를 앞으로 자연스럽게 뻗음, 두 팔은 팔걸이에 편안히, 옅은 미소로 여유롭게 바다를 바라보는 표정. 의자는 튼튼하고 자연스러운 나무틀+천 데크체어로 또렷하게."
REST_SUF=". 전신이 머리끝부터 발끝까지 다 보이게, 중앙 배치, 데크체어는 자세에 맞게 함께 또렷이 그림. 단색 흰 배경, 그림자·텍스트·서명 없음."

COMMON="넓은 가로 16:9 구도. 플랫 카툰 일러스트, 굵은 검정 외곽선, 부드러운 파스텔. ⚠️화면에 어떤 글자·숫자·상표·간판 텍스트도 절대 넣지 마라. 사람은 배경에 실루엣으로 아주 적게."
BG_TV="해변 숙소 아늑한 거실 저녁. ★오른쪽 벽에 켜진 벽걸이 평면 TV(화면은 은은한 빛만, 글자·로고 없는 빈 화면). 그 앞에 러그와 낮은 협탁, 따뜻한 스탠드 조명. 왼쪽 큰 창밖으로 노을 지는 바다와 작은 섬(비양도). 캐릭터가 앉아 오른쪽 TV를 볼 수 있게 중앙·왼쪽 바닥은 넓게 비운다. ${COMMON}"
BG_NOBED="밤 침실인데 ★침대·매트리스·이불은 절대 그리지 마라(빈 바닥). 바닥에 러그, 오른쪽에 협탁과 스탠드 불빛·책·노트, 벽에 둥근 시계(문자판 빈칸), 왼쪽 큰 창밖으로 별이 가득한 밤하늘과 어두운 바다, 커튼. 캐릭터가 바닥에 누울 수 있게 중앙·왼쪽 바닥을 아주 넓게 비운다. ${COMMON}"

echo "=== W14 fix gen start $(date) ===" >> "$LOG"
agy -p "${PRE}${SLEEP}${SLEEP_SUF} 결과 PNG를 '${OUTP}\\mj_w14_sleep.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1 &
agy -p "${PRE}${REST}${REST_SUF} 결과 PNG를 '${OUTP}\\mj_w14_rest_sit.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1 &
agy -p "${BG_TV} 결과 PNG를 '${OUTB}\\bg_w14_livingroom_tv.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1 &
agy -p "${BG_NOBED} 결과 PNG를 '${OUTB}\\bg_w14_bedroom_nobed.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1 &
wait
echo "=== done $(date) ===" >> "$LOG"
ls -la home_vocab/w14/mj_w14_sleep.png home_vocab/w14/mj_w14_rest_sit.png assets/graphics/bg/bg_w14_livingroom_tv.png assets/graphics/bg/bg_w14_bedroom_nobed.png 2>&1 >> "$LOG"
echo "[files above]" >> "$LOG"
