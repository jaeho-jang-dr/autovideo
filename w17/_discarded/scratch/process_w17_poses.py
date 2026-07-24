# -*- coding: utf-8 -*-
import os
import shutil
import sqlite3
from PIL import Image
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(ROOT, "assets", "characters")
DB_PATH = os.path.join(ROOT, "channel", "content.db")

# 새로 생성된 이미지 타임스탬프 맵핑
POSES = {
    "explaining": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_explaining_1784522448121.png",
        "kr": "티쳐제이_설명", "en": "teacher_jay_explaining", "prompt": "Using the provided reference image, keep the EXACT same character design (circular head with two strands of white hair, facial features, proportions, and body shape of the male character), and keep the exact same outfit (blue-and-white checkered shirt, beige trousers, and white sneakers). He stands front view, but now making natural hand gestures with both hands as if explaining a lesson warmly, with a gentle friendly smile. Solid flat light beige background (#F5F5F0). No shadows, no gradients. ONE single figure, full body."
    },
    "pointing_left": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_pointing_left_1784522458647.png",
        "kr": "티쳐제이_가리키기_왼쪽", "en": "teacher_jay_pointing_left", "prompt": "Using the provided reference image, keep the EXACT same character design (circular head with two strands of white hair, facial features, proportions, and body shape of the male character), and keep the exact same outfit (blue-and-white checkered shirt, beige trousers, and white sneakers). He stands facing front, but now raises his left arm to point toward the LEFT side, with a warm smile on his face. Solid flat light beige background (#F5F5F0). No shadows, no gradients. ONE single figure, full body."
    },
    "pointing_right": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_pointing_right_1784522469683.png",
        "kr": "티쳐제이_가리키기_오른쪽", "en": "teacher_jay_pointing_right", "prompt": "Using the provided reference image, keep the EXACT same character design (circular head with two strands of white hair, facial features, proportions, and body shape of the male character), and keep the exact same outfit (blue-and-white checkered shirt, beige trousers, and white sneakers). He stands facing front, but now raises his right arm to point toward the RIGHT side, with a warm smile on his face. Solid flat light beige background (#F5F5F0). No shadows, no gradients. ONE single figure, full body."
    },
    "walk_left": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_walk_left_1784522481633.png",
        "kr": "티쳐제이_걷기_왼쪽", "en": "teacher_jay_walk_left", "prompt": "Using the provided reference image, keep the EXACT same character design (circular head with two strands of white hair, facial features, proportions, and body shape of the male character), and keep the exact same outfit (blue-and-white checkered shirt, beige trousers, and white sneakers). He is walking toward the LEFT side, shown in a clear left-profile side view, mid-stride with one foot forward and arms swinging naturally, with a friendly expression. Solid flat light beige background (#F5F5F0). No shadows, no gradients. ONE single figure, full body."
    },
    "walk_right": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_walk_right_1784522494322.png",
        "kr": "티쳐제이_걷기_오른쪽", "en": "teacher_jay_walk_right", "prompt": "Using the provided reference image, keep the EXACT same character design (circular head with two strands of white hair, facial features, proportions, and body shape of the male character), and keep the exact same outfit (blue-and-white checkered shirt, beige trousers, and white sneakers). He is walking toward the RIGHT side, shown in a clear right-profile side view, mid-stride with one foot forward and arms swinging naturally, with a friendly expression. Solid flat light beige background (#F5F5F0). No shadows, no gradients. ONE single figure, full body."
    },
    "cheering": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_cheering_1784522504547.png",
        "kr": "티쳐제이_환호", "en": "teacher_jay_cheering", "prompt": "Using the provided reference image, keep the EXACT same character design (circular head with two strands of white hair, facial features, proportions, and body shape of the male character), and keep the exact same outfit (blue-and-white checkered shirt, beige trousers, and white sneakers). He stands front view, but now raising both arms high in the air, cheering happily with a wide open smile. Solid flat light beige background (#F5F5F0). No shadows, no gradients. ONE single figure, full body."
    },
    "waving": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_waving_1784522515998.png",
        "kr": "티쳐제이_손인사", "en": "teacher_jay_waving", "prompt": "Using the provided reference image, keep the EXACT same character design (circular head with two strands of white hair, facial features, proportions, and body shape of the male character), and keep the exact same outfit (blue-and-white checkered shirt, beige trousers, and white sneakers). He stands front view, raising his left arm up to wave hello in a friendly greeting, smiling warmly. Solid flat light beige background (#F5F5F0). No shadows, no gradients. ONE single figure, full body."
    },
    "thinking": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_thinking_1784522539560.png",
        "kr": "티쳐제이_생각", "en": "teacher_jay_thinking", "prompt": "Using the provided reference image, keep the EXACT same character design (circular head with two strands of white hair, facial features, proportions, and body shape of the male character), and keep the exact same outfit (blue-and-white checkered shirt, beige trousers, and white sneakers). He stands front view, but now has one hand resting on his chin in a thoughtful thinking pose, looking up slightly with a curious smile. Solid flat light beige background (#F5F5F0). No shadows, no gradients. ONE single figure, full body."
    },
    "bowing": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_bowing_1784522550958.png",
        "kr": "티쳐제이_절인사", "en": "teacher_jay_bowing", "prompt": "Using the provided reference image, keep the EXACT same character design (circular head with two strands of white hair, facial features, proportions, and body shape of the male character), and keep the exact same outfit (blue-and-white checkered shirt, beige trousers, and white sneakers). He stands facing front, but now giving a polite, friendly little bow of greeting, with a warm smile on his face. Solid flat light beige background (#F5F5F0). No shadows, no gradients. ONE single figure, full body."
    }
}

def make_bg_transparent(raw_path, out_path, tol=35):
    try:
        img = Image.open(raw_path).convert("RGBA")
        w, h = img.size
        px = img.load()
        
        corners = [px[0, 0][:3], px[w - 1, 0][:3], px[0, h - 1][:3], px[w - 1, h - 1][:3]]
        bg_r = sorted([c[0] for c in corners])[2]
        bg_g = sorted([c[1] for c in corners])[2]
        bg_b = sorted([c[2] for c in corners])[2]
        
        seen = bytearray(w * h)
        dq = deque([(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)])
        while dq:
            x, y = dq.popleft()
            if x < 0 or y < 0 or x >= w or y >= h:
                continue
            idx = y * w + x
            if seen[idx]:
                continue
            seen[idx] = 1
            r, g, b, a = px[x, y]
            
            if abs(r - bg_r) > tol or abs(g - bg_g) > tol or abs(b - bg_b) > tol:
                continue
            
            px[x, y] = (r, g, b, 0)
            dq.append((x + 1, y)); dq.append((x - 1, y))
            dq.append((x, y + 1)); dq.append((x, y - 1))
        img.save(out_path)
        print(f"  [SUCCESS] Transparentized: {out_path}")
        return True
    except Exception as e:
        print(f"  [ERROR] transparentize fail {raw_path}: {e}")
        return False

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for pose_name, data in POSES.items():
        src = data["src"]
        if not os.path.exists(src):
            print(f"[WARN] Source file not found: {src}")
            continue

        opaque_dest = os.path.join(TARGET_DIR, f"teacher_jay_{pose_name}_opaque.png")
        transparent_dest = os.path.join(TARGET_DIR, f"teacher_jay_{pose_name}.png")

        # 1. Copy Opaque
        shutil.copy(src, opaque_dest)
        print(f"Copied Opaque: {opaque_dest}")

        # 2. Transparentize
        make_bg_transparent(opaque_dest, transparent_dest)

        # 3. SQLite content.db sync
        # Type is 'pose' or 'character'?
        # Standard poses registered as type 'pose' or 'character' per register_poses.py
        # Let's insert as type 'pose' for transparent, and 'pose_opaque' or similar?
        # Usually transparent = 'pose', opaque = 'pose_opaque' or just transparent
        # In register_poses: name_en = f"{char_id}_{pose}"
        cur.execute("DELETE FROM assets WHERE name_en IN (?, ?)", (data["en"], data["en"] + "_opaque"))
        
        # Insert transparent
        cur.execute(
            "INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
            (data["kr"], data["en"], "pose", f"teacher_jay_{pose_name}.png", data["prompt"])
        )
        # Insert opaque
        cur.execute(
            "INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
            (data["kr"] + "_불투명", data["en"] + "_opaque", "pose", f"teacher_jay_{pose_name}_opaque.png", data["prompt"])
        )

    conn.commit()
    conn.close()
    print("[OK] Poses processing & DB sync completed.")

if __name__ == "__main__":
    main()
