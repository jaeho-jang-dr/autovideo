#!/usr/bin/env bash
cd "D:/Entertainments/DevEnvironment/autovideo"
LOG=scratch/piano_seq.log
echo "[$(date +%H:%M:%S)] piano seq queued; waiting friends batch (32) to finish" > $LOG
# 1) 친구 32개 완료 + batch python idle 대기 (Chrome 단일세션 충돌 방지)
for i in $(seq 1 60); do
  fdone=$(ls home_vocab/injun_jieun_*.png 2>/dev/null | grep -vE "handshake|pair|_opaque|grand_piano" | wc -l)
  busy=$(grep -c "시도 [0-9]/3" scratch/batch_gen_friends.log 2>/dev/null)
  done_mark=$(grep -c "^Done\.$" scratch/batch_gen_friends.log 2>/dev/null)
  echo "[$(date +%H:%M:%S)] friends=$fdone done_marks=$done_mark" >> $LOG
  if [ "$fdone" -ge 32 ]; then echo "friends complete" >> $LOG; break; fi
  sleep 60
done
sleep 20
# 2) scene1: handshake_facing_opaque 레퍼런스
echo "[$(date +%H:%M:%S)] >>> SCENE1 start" >> $LOG
python scratch/batch_gen.py --prompts home_vocab/piano_scene1_prompts.txt --char injun_jieun --ref-key injun_jieun_handshake_facing_opaque >> $LOG 2>&1
# 3) scene2: scene1 결과를 레퍼런스로 (같은 그랜드피아노 유지)
if [ -f home_vocab/injun_jieun_grand_piano_standing.png ]; then
  echo "[$(date +%H:%M:%S)] >>> SCENE2 start (ref=grand_piano_standing)" >> $LOG
  python scratch/batch_gen.py --prompts home_vocab/piano_scene2_prompts.txt --char injun_jieun --ref-key injun_jieun_grand_piano_standing >> $LOG 2>&1
else
  echo "[$(date +%H:%M:%S)] SCENE1 missing -> skip scene2" >> $LOG
fi
echo "[$(date +%H:%M:%S)] PIANO SEQ DONE" >> $LOG
