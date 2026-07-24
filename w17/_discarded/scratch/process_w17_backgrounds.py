# -*- coding: utf-8 -*-
import os
import shutil
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(ROOT, "w17", "backgrounds")
DB_PATH = os.path.join(ROOT, "channel", "content.db")

BACKGROUNDS = {
    "w17_bg_entrance": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_entrance_1784522577442.png",
        "kr": "불국사_입구", "en": "w17_bg_entrance", "prompt": "Minimalist 2D flat line-art scenic illustration of the traditional entrance gate of Bulguksa Temple, thick clean black outlines, storybook style, soft cream background (#F5F5F0), vibrant red and yellow autumn maple leaves around the gate. No watermark, no text. 16:9 aspect ratio."
    },
    "w17_bg_temple_valley": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_temple_valley_1784522601211.png",
        "kr": "불국사_전경_계곡", "en": "w17_bg_temple_valley", "prompt": "Minimalist 2D flat line-art scenic illustration of a traditional Korean Buddhist temple complex nested in a peaceful mountain valley with green pines and autumn maples, thick clean black outlines, storybook style, soft cream background (#F5F5F0), vibrant flat marker colors. No watermark, no text. 16:9 aspect ratio."
    },
    "w17_bg_stairs_far": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_stairs_far_1784522611536.png",
        "kr": "불국사_돌계단_원경", "en": "w17_bg_stairs_far", "prompt": "Minimalist 2D flat line-art scenic illustration of the double-tiered stone stairs (Cheongungyo and Baekungyo) of Bulguksa Temple, seen from a slightly distant front angle, leading up to a traditional wooden gate pavilion, thick clean black outlines, storybook style, soft cream background (#F5F5F0), vibrant flat marker coloring. No watermark, no text. 16:9 aspect ratio."
    },
    "w17_bg_stairs_close": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_stairs_close_1784522622193.png",
        "kr": "불국사_돌계단_근경", "en": "w17_bg_stairs_close", "prompt": "Minimalist 2D flat line-art scenic illustration focusing on the details of the stone staircase and the stone archway underneath the steps of Bulguksa Temple, thick clean black outlines, storybook style, soft cream background (#F5F5F0), vibrant flat marker coloring. No watermark, no text. 16:9 aspect ratio."
    },
    "w17_bg_courtyard": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_courtyard_1784522642636.png",
        "kr": "불국사_대웅전_마당", "en": "w17_bg_courtyard", "prompt": "Minimalist 2D flat line-art scenic illustration of the main courtyard of Daeungjeon hall in Bulguksa Temple, showing Seokgatap pagoda on the left and Dabotap pagoda on the right, thick clean black outlines, storybook style, soft cream background (#F5F5F0), vibrant flat marker coloring. No watermark, no text. 16:9 aspect ratio."
    },
    "w17_bg_seokgatap": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_seokgatap_1784522652888.png",
        "kr": "불국사_석가탑", "en": "w17_bg_seokgatap", "prompt": "Minimalist 2D flat line-art scenic illustration of Seokgatap pagoda of Bulguksa Temple, focusing on its simple, elegant, and geometric straight lines, thick clean black outlines, storybook style, soft cream background (#F5F5F0), vibrant flat marker coloring. No watermark, no text. 16:9 aspect ratio."
    },
    "w17_bg_dabotap": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_dabotap_1784522665347.png",
        "kr": "불국사_다보탑", "en": "w17_bg_dabotap", "prompt": "Minimalist 2D flat line-art scenic illustration of Dabotap pagoda of Bulguksa Temple, focusing on its highly ornate structure with square, octagonal, and circular stone details and pillars, thick clean black outlines, storybook style, soft cream background (#F5F5F0), vibrant flat marker coloring. No watermark, no text. 16:9 aspect ratio."
    },
    "w17_bg_garden": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_garden_1784522675938.png",
        "kr": "불국사_정원", "en": "w17_bg_garden", "prompt": "Minimalist 2D flat line-art scenic illustration of a cozy quiet traditional Korean temple garden courtyard, thick clean black outlines, storybook style, soft cream background (#F5F5F0), vibrant flat marker coloring. No watermark, no text. 16:9 aspect ratio."
    },
    "w17_bg_dancheong": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_dancheong_1784522686158.png",
        "kr": "불국사_단청", "en": "w17_bg_dancheong", "prompt": "Minimalist 2D flat line-art scenic illustration of traditional Korean hanok tile roof eaves and colorful Dancheong wood patterns, thick clean black outlines, storybook style, soft cream background (#F5F5F0), vibrant flat marker coloring. No watermark, no text. 16:9 aspect ratio."
    },
    "w17_bg_outro": {
        "src": r"C:\Users\antigravity\.gemini\antigravity\brain\d7ffa487-aa91-43dd-a0fa-c96e9ee39623\w17_bg_outro_1784522698746.png",
        "kr": "불국사_아웃트로", "en": "w17_bg_outro", "prompt": "Minimalist 2D flat line-art scenic illustration of Dabotap pagoda silhouette under a beautiful golden and purple autumn twilight sunset, thick clean black outlines, storybook style, soft cream background (#F5F5F0), vibrant flat marker coloring. No watermark, no text. 16:9 aspect ratio."
    }
}

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for bg_name, data in BACKGROUNDS.items():
        src = data["src"]
        if not os.path.exists(src):
            print(f"[WARN] Source file not found: {src}")
            continue

        dest_file_name = f"{bg_name}.png"
        dest_path = os.path.join(TARGET_DIR, dest_file_name)

        # Copy background
        shutil.copy(src, dest_path)
        print(f"Copied Background: {dest_path}")

        # Sync to assets DB (rel path = w17/backgrounds/w17_bg_name.png)
        rel_path = f"w17/backgrounds/{dest_file_name}"
        cur.execute("DELETE FROM assets WHERE name_en = ?", (data["en"],))
        cur.execute(
            "INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
            (data["kr"], data["en"], "background", rel_path, data["prompt"])
        )

    conn.commit()
    conn.close()
    print("[OK] Backgrounds processing & DB sync completed.")

if __name__ == "__main__":
    main()
