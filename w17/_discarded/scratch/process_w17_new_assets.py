# -*- coding: utf-8 -*-
import os
import shutil
import sqlite3
from PIL import Image
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR_DIR = os.path.join(ROOT, "assets", "characters")
BG_DIR = os.path.join(ROOT, "w17", "backgrounds")
DB_PATH = os.path.join(ROOT, "channel", "content.db")

# 신규 포즈 5종 정보
NEW_POSES = {
    "explain_polite": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_explain_polite_1784532284592.png",
        "kr": "티쳐제이_정중히설명", "en": "teacher_jay_explain_polite",
        "prompt": "Flat 2D storybook illustration of a slim 30-something Korean man with gray-white hair strands, wearing a blue checkered long-sleeve shirt, beige cotton pants, and white sneakers. Full body. The man is standing, placing one hand politely on his chest and gesturing with the other hand to explain polite speech. Plain solid beige cream #F5F5F0 background. Clean black outlines. Marker colored pastel tone."
    },
    "comparing": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_comparing_1784532296817.png",
        "kr": "티쳐제이_대조비교", "en": "teacher_jay_comparing",
        "prompt": "Flat 2D storybook illustration of a slim 30-something Korean man with gray-white hair strands, wearing a blue checkered long-sleeve shirt, beige cotton pants, and white sneakers. Full body. The man is standing, holding both hands open to the sides as if comparing two things left and right. Plain solid beige cream #F5F5F0 background. Clean black outlines. Marker colored pastel tone."
    },
    "slang_phone": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_slang_phone_1784532313483.png",
        "kr": "티쳐제이_휴대폰설명", "en": "teacher_jay_slang_phone",
        "prompt": "Flat 2D storybook illustration of a slim 30-something Korean man with gray-white hair strands, wearing a blue checkered long-sleeve shirt, beige cotton pants, and white sneakers. Full body. The man is standing, holding a modern smartphone in one hand and pointing to it with the other hand, explaining text slang. Plain solid beige cream #F5F5F0 background. Clean black outlines. Marker colored pastel tone."
    },
    "study_book": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_study_book_1784532325303.png",
        "kr": "티쳐제이_책낭독", "en": "teacher_jay_study_book",
        "prompt": "Flat 2D storybook illustration of a slim 30-something Korean man with gray-white hair strands, wearing a blue checkered long-sleeve shirt, beige cotton pants, and white sneakers. Full body. The man is standing, holding a thin Hangeul textbook open in one hand and pointing to the page with the other, explaining pronunciation. Plain solid beige cream #F5F5F0 background. Clean black outlines. Marker colored pastel tone."
    },
    "bowing_advanced": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\teacher_jay_bowing_advanced_1784532337062.png",
        "kr": "티쳐제이_정중절인사", "en": "teacher_jay_bowing_advanced",
        "prompt": "Flat 2D storybook illustration of a slim 30-something Korean man with gray-white hair strands, wearing a blue checkered long-sleeve shirt, beige cotton pants, and white sneakers. Full body. The man is standing, bowing slightly forward with both hands gathered politely in front, giving a formal respectful bow. Plain solid beige cream #F5F5F0 background. Clean black outlines. Marker colored pastel tone."
    }
}

# 신규 배경 3종 정보
NEW_BACKGROUNDS = {
    "w17_bg_tohamsan_trail": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_tohamsan_trail_1784532349781.png",
        "kr": "토함산_등산로", "en": "w17_bg_tohamsan_trail",
        "prompt": "Flat 2D storybook illustration of a beautiful mountain trail on Tohamsan mountain in Gyeongju, with lush green trees, stone pathways, and gentle sunlight filtering through the leaves. 16:9 aspect ratio landscape view. Clean black outlines, marker colored pastel tone, traditional illustration."
    },
    "w17_bg_seokguram_entrance": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_seokguram_entrance_1784532372495.png",
        "kr": "석굴암_입구전경", "en": "w17_bg_seokguram_entrance",
        "prompt": "Flat 2D storybook illustration of the traditional Korean wooden pavilion gate entrance to Seokguram Grotto, surrounded by green pine trees and autumn leaves under a clear sky. 16:9 aspect ratio landscape view. Clean black outlines, marker colored pastel tone, traditional illustration."
    },
    "w17_bg_seokguram_grotto": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_seokguram_grotto_1784532383513.png",
        "kr": "석굴암_본존불", "en": "w17_bg_seokguram_grotto",
        "prompt": "Flat 2D storybook illustration of the interior stone chamber of Seokguram Grotto in Gyeongju, depicting the large stone Buddha statue seated on a lotus pedestal, surrounded by stone reliefs on the circular chamber walls. 16:9 aspect ratio landscape view. Clean black outlines, marker colored pastel tone, traditional illustration."
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
    os.makedirs(CHAR_DIR, exist_ok=True)
    os.makedirs(BG_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. 신규 포즈 처리
    print("Processing new poses...")
    for pose_name, data in NEW_POSES.items():
        src = data["src"]
        if not os.path.exists(src):
            print(f"  [WARN] Source file not found: {src}")
            continue
            
        opaque_dest = os.path.join(CHAR_DIR, f"teacher_jay_{pose_name}_opaque.png")
        transparent_dest = os.path.join(CHAR_DIR, f"teacher_jay_{pose_name}.png")
        
        # 복사 및 컷아웃
        shutil.copy(src, opaque_dest)
        make_bg_transparent(src, transparent_dest)
        
        # DB 동기화 (Opaque)
        opaque_rel = f"assets/characters/teacher_jay_{pose_name}_opaque.png"
        cur.execute("DELETE FROM assets WHERE name_en = ?", (f"{data['en']}_opaque",))
        cur.execute(
            "INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?, ?, ?, ?, ?)",
            (f"{data['kr']}_불투명", f"{data['en']}_opaque", "character", opaque_rel, data["prompt"])
        )
        
        # DB 동기화 (Transparent)
        transparent_rel = f"assets/characters/teacher_jay_{pose_name}.png"
        cur.execute("DELETE FROM assets WHERE name_en = ?", (data["en"],))
        cur.execute(
            "INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?, ?, ?, ?, ?)",
            (data["kr"], data["en"], "character", transparent_rel, data["prompt"])
        )
        conn.commit()
        print(f"  [DB Sync] Registered pose {pose_name} to DB.")

    # 2. 신규 배경 처리
    print("Processing new backgrounds...")
    for bg_name, data in NEW_BACKGROUNDS.items():
        src = data["src"]
        if not os.path.exists(src):
            print(f"  [WARN] Source file not found: {src}")
            continue
            
        dest = os.path.join(BG_DIR, f"{bg_name}.png")
        shutil.copy(src, dest)
        
        # DB 동기화
        bg_rel = f"w17/backgrounds/{bg_name}.png"
        cur.execute("DELETE FROM assets WHERE name_en = ?", (data["en"],))
        cur.execute(
            "INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?, ?, ?, ?, ?)",
            (data["kr"], data["en"], "background", bg_rel, data["prompt"])
        )
        conn.commit()
        print(f"  [DB Sync] Registered background {bg_name} to DB.")
        
    conn.close()
    print("[OK] All new assets processed and registered successfully.")

if __name__ == "__main__":
    main()
