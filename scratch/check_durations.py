import os
from moviepy import VideoFileClip

vdir = "assets/videos"
for f in os.listdir(vdir):
    if f.endswith(".mp4"):
        p = os.path.join(vdir, f)
        try:
            with VideoFileClip(p) as clip:
                print(f"{f}: {clip.duration}s, size={clip.size}")
        except Exception as e:
            print(f"Error reading {f}: {e}")
