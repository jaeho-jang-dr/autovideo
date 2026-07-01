#!/usr/bin/env bash
cd "D:/Entertainments/DevEnvironment/autovideo"
LOG=scratch/pianorot.log
echo "[$(date +%H:%M:%S)] START piano rotation x2 (ref=grand_piano_ready)" > $LOG
echo "[$(date +%H:%M:%S)] >>> rear180" >> $LOG
python scratch/batch_gen.py --prompts home_vocab/_piano_rot1.txt --char injun_jieun --ref-key injun_jieun_grand_piano_ready >> $LOG 2>&1
echo "[$(date +%H:%M:%S)] >>> rearleft135" >> $LOG
python scratch/batch_gen.py --prompts home_vocab/_piano_rot2.txt --char injun_jieun --ref-key injun_jieun_grand_piano_ready >> $LOG 2>&1
echo "[$(date +%H:%M:%S)] PIANO ROT DONE" >> $LOG
