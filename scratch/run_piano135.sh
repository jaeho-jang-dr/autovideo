#!/usr/bin/env bash
cd "D:/Entertainments/DevEnvironment/autovideo"
LOG=scratch/piano135.log
echo "[$(date +%H:%M:%S)] waiting for front_concert to finish" > $LOG
for i in $(seq 1 40); do
  if [ -f home_vocab/injun_jieun_piano_front_concert.png ] && grep -q "Done\." scratch/piano_front.log 2>/dev/null; then echo "front done" >> $LOG; break; fi
  sleep 20
done
sleep 8
echo "[$(date +%H:%M:%S)] >>> cw135 (ref=front_concert)" >> $LOG
python scratch/batch_gen.py --prompts home_vocab/_piano_front135.txt --char injun_jieun --ref-key injun_jieun_piano_front_concert >> $LOG 2>&1
echo "[$(date +%H:%M:%S)] PIANO 135 DONE" >> $LOG
