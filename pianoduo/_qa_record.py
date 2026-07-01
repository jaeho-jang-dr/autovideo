# -*- coding: utf-8 -*-
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "channel"))
import content_db as cdb
for n in range(1, 26):
    cdb.log_clip("pianoduo", n, status="success", distortion_check="ok",
                 notes="v2 QA 통과: 나란히/손은건반/마주봄없음")
cdb.upsert_project("pianoduo", status="review")
print("[OK] QA 결과 DB 기록(25클립 ok, project=review)")
