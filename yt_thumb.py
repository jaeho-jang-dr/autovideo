# -*- coding: utf-8 -*-
"""yt_thumb.py — 커스텀 썸네일 업로드(thumbnails.set). 쿼터 50unit/건.
사용: python yt_thumb.py <VID> <image.png>  [추가로 <VID> <image> ... 쌍 반복 가능]"""
import sys, os
sys.path.insert(0, os.getcwd())
from yt_api import yt
from googleapiclient.http import MediaFileUpload

args = sys.argv[1:]
if len(args) < 2 or len(args) % 2:
    raise SystemExit("사용: python yt_thumb.py <VID> <image> [<VID> <image> ...]")

y = yt()
for i in range(0, len(args), 2):
    vid, img = args[i], args[i+1]
    if not os.path.exists(img):
        print(f"!! 파일 없음: {img}"); continue
    mb = os.path.getsize(img) / 1024 / 1024
    if mb > 2:
        print(f"!! {img} {mb:.2f}MB > 2MB — 유튜브 한도 초과, 스킵"); continue
    r = y.thumbnails().set(videoId=vid, media_body=MediaFileUpload(img)).execute()
    url = r.get("items", [{}])[0].get("default", {}).get("url", "(ok)")
    print(f"OK {vid} ← {os.path.basename(img)} ({mb:.2f}MB)  {url}")
print("THUMB_DONE")
