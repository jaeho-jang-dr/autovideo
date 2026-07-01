import os

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
OUT_DIR = os.path.join(ROOT, "prompts_for_veo")
DEST_DIR = os.path.join(ROOT, "korean_education")

def is_real_mp4(path):
    try:
        with open(path, "rb") as f:
            return b"ftyp" in f.read(16)
    except Exception:
        return False

def check():
    print("=== Checking prompts_for_veo ===")
    missing_out = []
    for i in range(90):
        p = os.path.join(OUT_DIR, f"scene_{i}.mp4")
        if not os.path.exists(p):
            missing_out.append((i, "not exists"))
        elif os.path.getsize(p) == 0:
            missing_out.append((i, "zero size"))
        elif not is_real_mp4(p):
            missing_out.append((i, "not real mp4"))
    print(f"Missing/Invalid in prompts_for_veo ({len(missing_out)}): {missing_out}")

    print("\n=== Checking korean_education ===")
    missing_dest = []
    for i in range(90):
        p = os.path.join(DEST_DIR, f"scene_{i}.mp4")
        if not os.path.exists(p):
            missing_dest.append((i, "not exists"))
        elif os.path.getsize(p) == 0:
            missing_dest.append((i, "zero size"))
        elif not is_real_mp4(p):
            missing_dest.append((i, "not real mp4"))
    print(f"Missing/Invalid in korean_education ({len(missing_dest)}): {missing_dest}")

if __name__ == "__main__":
    check()
