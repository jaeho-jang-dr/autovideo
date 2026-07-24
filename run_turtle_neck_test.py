import subprocess
import os
import shutil
import sys

# Ensure UTF-8 output
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Paths
prompt_file = "temp_shorts_prompt.txt"
input_image = r"G:\내 드라이브\AutoVideo\shorts\turtle_neck_v2\kf3_60도_27kg_아이.png"
motion_prompt = (
    "Whiteboard hand-drawn animation. A man straining under the weight of a child sitting on his shoulders and neck, "
    "grimacing hard, sweat drops flying off, his legs trembling with visible motion lines. The child on top waves cheerfully. "
    "Energetic strain motion, static camera, marker-on-whiteboard art style, off-white background. No new text, no captions, no watermark, no logo."
)
output_dir = "temp_shorts_prompt"
expected_clip = os.path.abspath(os.path.join(output_dir, "scene_3.mp4"))
target_clip = r"G:\내 드라이브\AutoVideo\shorts\turtle_neck_v2\clip3_27kg.mp4"

print("=" * 60)
print("1. Running autoveo_flow.py with 6 cyclic accounts (using profile 3 for scene 3)")
print(f"   Input Image: {input_image}")
print(f"   Motion Prompt: {motion_prompt}")
print("=" * 60)

cmd = [
    "python", "autoveo_flow.py",
    "--prompts", prompt_file,
    "--scene", "3",
    "--upload", input_image,
    "--motion", motion_prompt,
    "--aspect", "9:16",
    "--profiles-count", "6",
    "--force"
]

print(f"Executing: {' '.join(cmd)}")
res = subprocess.run(cmd)

if res.returncode != 0:
    print(f"[ERROR] autoveo_flow.py failed with return code {res.returncode}")
    sys.exit(res.returncode)

if not os.path.exists(expected_clip) or os.path.getsize(expected_clip) == 0:
    print(f"[ERROR] Generated clip not found at expected path: {expected_clip}")
    sys.exit(1)

print(f"[SUCCESS] Video successfully generated at: {expected_clip}")
print(f"Moving to: {target_clip}")

try:
    os.makedirs(os.path.dirname(target_clip), exist_ok=True)
    shutil.move(expected_clip, target_clip)
    print(f"[SUCCESS] Moved clip to destination: {target_clip}")
except Exception as e:
    print(f"[ERROR] Failed to move generated file: {e}")
    sys.exit(1)

print("=" * 60)
print("Turtle Neck video clip generation completed successfully!")
print("=" * 60)
