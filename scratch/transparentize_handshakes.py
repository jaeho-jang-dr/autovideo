# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import shutil
from PIL import Image
from collections import deque
from supabase import create_client, Client

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Force UTF-8 stdout
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

def load_env(p=os.path.join(ROOT, ".env")):
    d = {}
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    d[k.strip()] = v.strip().strip('"').strip("'")
    return d

def transparentize(path, out_path, tol=28):
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]
    rgb = arr[:, :, :3].astype(int)
    
    corners = np.array([
        rgb[0, 0], rgb[0, w - 1], rgb[h - 1, 0], rgb[h - 1, w - 1]
    ])
    bg = np.median(corners, axis=0)
    
    seen = np.zeros((h, w), dtype=bool)
    out_alpha = arr[:, :, 3].copy()
    dq = deque([(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)])
    
    while dq:
        y, x = dq.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y, x]:
            continue
        seen[y, x] = True
        if np.abs(rgb[y, x] - bg).max() > tol:
            continue
        out_alpha[y, x] = 0
        dq.append((y + 1, x))
        dq.append((y - 1, x))
        dq.append((y, x + 1))
        dq.append((y, x - 1))
        
    arr[:, :, 3] = out_alpha
    Image.fromarray(arr, "RGBA").save(out_path)
    print(f"Transparentized: {path} -> {out_path}")

def upload_to_supabase(filename, local_path, env, supabase):
    try:
        try:
            supabase.storage.from_("character-base").remove([filename])
        except Exception:
            pass
        with open(local_path, "rb") as f:
            supabase.storage.from_("character-base").upload(
                path=filename,
                file=f.read(),
                file_options={"content-type": "image/png"}
            )
        print(f"Uploaded to Supabase Storage: {filename}")
    except Exception as e:
        print(f"Failed to upload {filename}: {e}")

def main():
    env = load_env()
    url = env.get("SUPABASE_URL")
    key = env.get("SUPABASE_KEY")
    if not url or not key:
        print("[ERR] SUPABASE_URL or SUPABASE_KEY not found in .env")
        return 1
    supabase: Client = create_client(url, key)
    
    ref_filename = "zolla_handshake_ref.png"
    ref_path = os.path.join(ROOT, "home_vocab", ref_filename)
    
    gen_filename = "zolla_handshake.png"
    gen_path = os.path.join(ROOT, "home_vocab", gen_filename)
    
    print("Transparentizing images...")
    transparentize(ref_path, ref_path, tol=28)
    transparentize(gen_path, gen_path, tol=28)
    
    print("Uploading transparentized images to Supabase Storage...")
    upload_to_supabase(ref_filename, ref_path, env, supabase)
    upload_to_supabase(gen_filename, gen_path, env, supabase)
    
    # Also copy to artifacts directory so the user can view the updated versions
    art_dir = "C:\\Users\\antigravity\\.gemini\\antigravity\\brain\\ea11ac2b-77b0-4d5a-98ea-c249b22ddb89"
    shutil.copy2(ref_path, os.path.join(art_dir, ref_filename))
    shutil.copy2(gen_path, os.path.join(art_dir, gen_filename))
    print("Copied transparentized images to artifacts directory.")
    
    print("[SUCCESS] All processes completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
