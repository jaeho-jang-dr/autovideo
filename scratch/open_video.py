import os
video_path = os.path.abspath("line_craft/line_craft_final.mp4")
if os.path.exists(video_path):
    print(f"[Info] Opening video visibly in user session: {video_path}")
    os.startfile(video_path)
else:
    print(f"[Error] Video file not found: {video_path}")
