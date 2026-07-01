#!/usr/bin/env bash
cd "D:/Entertainments/DevEnvironment/autovideo"
LOG=scratch/fix2.log
echo "[$(date +%H:%M:%S)] START fix2 (snorkeling + piano_ready)" > $LOG
echo "[$(date +%H:%M:%S)] >>> snorkeling" >> $LOG
python scratch/batch_gen.py --prompts home_vocab/_snorkeling_one.txt --char injun_jieun --ref-key injun_jieun_handshake_facing_opaque >> $LOG 2>&1
echo "[$(date +%H:%M:%S)] >>> piano_ready (ref=grand_piano_standing)" >> $LOG
python scratch/batch_gen.py --prompts home_vocab/_piano_ready_one.txt --char injun_jieun --ref-key injun_jieun_grand_piano_standing >> $LOG 2>&1
echo "[$(date +%H:%M:%S)] FIX2 DONE" >> $LOG
