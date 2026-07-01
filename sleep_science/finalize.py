import os
import subprocess
import sys

TARGET_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TARGET_DIR)

SCENARIO = os.path.join(TARGET_DIR, "scenario.txt")
OUTPUT_VIDEO = os.path.join(TARGET_DIR, "sleep_science.mp4")

def main():
    compile_cmd = [
        "python", os.path.join(ROOT_DIR, "make_video.py"),
        "--scenario", SCENARIO,
        "--output", OUTPUT_VIDEO,
        "--intro", "assets/intro.mp4",
        "--outro", "assets/outro.mp4",
        "--outro-card", "assets/outro_template.png",
        "--no-burn-subs", "--embed-subs"
    ]
    
    print(f"Executing compilation command: {' '.join(compile_cmd)}")
    try:
        subprocess.run(compile_cmd, check=True)
        print("Compilation Successful!")
    except subprocess.CalledProcessError as e:
        print(f"Compilation Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
