# -*- coding: utf-8 -*-
import os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT,"channel"))
import content_db as cdb
cdb.upsert_project("pianoduo",
    drive_url=r"G:\내 드라이브\AutoVideo\pianoduo\pianoduo.mp4",
    final_path=os.path.join(ROOT,"pianoduo","pianoduo.mp4"),
    runtime_sec=151.25, status="review",
    notes="v2 완성: 나란히/손은건반/진지/청크전환/seg2-3안정화/씬2부터BGM. 영상=로컬+드라이브, 정보=DB. 유튜브 업로드 대기.")
print("[OK] DB finalize")
