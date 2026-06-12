"""
merge_clips.py — concatenate downloaded Flow clips into one video (MoviePy 2.x).

Usage:
  python merge_clips.py <output.mp4> <in1.mp4> <in2.mp4> [in3.mp4 ...]
"""
import sys
from moviepy import VideoFileClip, concatenate_videoclips


def main():
    if len(sys.argv) < 3:
        print("usage: python merge_clips.py <output.mp4> <in1.mp4> <in2.mp4> ...")
        sys.exit(1)
    out = sys.argv[1]
    ins = sys.argv[2:]
    clips = [VideoFileClip(p) for p in ins]
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(out, fps=24, codec="libx264", audio_codec="aac")
    for c in clips:
        c.close()
    final.close()
    print(f"[merged] {len(ins)} clips -> {out}")


if __name__ == "__main__":
    main()
