#!/usr/bin/env bash
# 남은 작업 단일 순차 체인 (Chrome 단일세션) — 2026-06-20
#  1) 친구 누락 8개 생성 (셀피 재생성 + 추가 7개: snorkeling/hiking/swimming_pool/roller_coaster/skiing/motorcycle/piano)
#  2) 그랜드피아노 시퀀스 scene1 -> scene2(scene1 참조)
#  3) 기존 커플 이미지 Supabase 백필(FK 고친 뒤 누락분 재등록)
cd "D:/Entertainments/DevEnvironment/autovideo"
LOG=scratch/run_remaining.log
echo "[$(date +%H:%M:%S)] START remaining chain" > $LOG

run(){ echo "[$(date +%H:%M:%S)] >>> $*" >> $LOG; "$@" >> $LOG 2>&1; }

# 1) 친구 누락분 (selfie_fix 먼저: 명확한 셀피 프롬프트로 교체)
run python scratch/batch_gen.py --prompts home_vocab/selfie_fix_prompts.txt --char injun_jieun --ref-key injun_jieun_handshake_facing_opaque
# 추가 7개 + 혹시 남은 친구분
run python scratch/batch_gen.py --prompts home_vocab/injun_jieun_friends_prompts.txt --char injun_jieun --ref-key injun_jieun_handshake_facing_opaque --side-ref injun_navy_side_opaque

# 2) 그랜드피아노 시퀀스
run python scratch/batch_gen.py --prompts home_vocab/piano_scene1_prompts.txt --char injun_jieun --ref-key injun_jieun_handshake_facing_opaque
if [ -f home_vocab/injun_jieun_grand_piano_standing.png ]; then
  run python scratch/batch_gen.py --prompts home_vocab/piano_scene2_prompts.txt --char injun_jieun --ref-key injun_jieun_grand_piano_standing
else
  echo "[$(date +%H:%M:%S)] scene1 missing -> skip scene2" >> $LOG
fi

# 3) 기존 커플 이미지 Supabase 백필 (FK 고친 뒤 재등록)
run python scratch/backfill_couple_supabase.py

echo "[$(date +%H:%M:%S)] ALL REMAINING DONE" >> $LOG
