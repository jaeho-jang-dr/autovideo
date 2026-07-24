# -*- coding: utf-8 -*-
"""내 채널 최근 업로드 나열(비공개/일부공개 포함) — video_id 찾기용. 쿼터 ~2unit."""
import sys, os
sys.path.insert(0, os.getcwd())
from yt_api import yt

N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
y = yt()
ch = y.channels().list(part="contentDetails", mine=True).execute()
up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
items = y.playlistItems().list(part="snippet,contentDetails", playlistId=up, maxResults=N).execute()["items"]
vids = [it["contentDetails"]["videoId"] for it in items]
# privacyStatus 보강
det = y.videos().list(part="snippet,status,contentDetails", id=",".join(vids)).execute()["items"]
for v in det:
    s = v["snippet"]; st = v["status"]; cd = v["contentDetails"]
    print(f'{v["id"]} | {st["privacyStatus"]:<8} | {cd.get("duration",""):<8} | {s["publishedAt"][:16]} | {s["title"]}')
