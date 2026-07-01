import os
import json
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
OUTPUT_FILE = os.path.join(ROOT_DIR, "autovideo_assets.md")

# Load assets map if it exists
assets_map_path = os.path.join(ASSETS_DIR, "graphics", "assets_map.json")
assets_map = {}
if os.path.exists(assets_map_path):
    try:
        with open(assets_map_path, "r", encoding="utf-8") as f:
            assets_map = json.load(f)
    except Exception as e:
        print(f"Failed to load assets map: {e}")

# Helper to find description from map
def get_desc(rel_path, category=None):
    norm_path = rel_path.replace("\\", "/")
    if category:
        cat_data = assets_map.get(category, {})
        for k, v in cat_data.items():
            if v.get("file") == norm_path:
                return v.get("description", "")
    else:
        for cat, cat_data in assets_map.items():
            for k, v in cat_data.items():
                if v.get("file") == norm_path:
                    return v.get("description", "")
    return ""

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

catalog = []

# Scan profiles
profiles_dir = os.path.join(ASSETS_DIR, "profiles")
if os.path.exists(profiles_dir):
    for f in os.listdir(profiles_dir):
        if f.endswith(".json"):
            path = os.path.join(profiles_dir, f)
            rel_path = os.path.relpath(path, ROOT_DIR)
            abs_path = os.path.abspath(path)
            size = os.path.getsize(path)
            catalog.append({
                "category": "Rendering & Style Profiles",
                "filename": f,
                "path": rel_path,
                "abs_path": abs_path,
                "size": size,
                "usage": f"Subtitle style and rendering configuration preset ({f[:-5]} style)."
            })

# Scan root assets (logos, intros, outros)
for f in os.listdir(ASSETS_DIR):
    path = os.path.join(ASSETS_DIR, f)
    if os.path.isfile(path):
        rel_path = os.path.relpath(path, ROOT_DIR)
        abs_path = os.path.abspath(path)
        size = os.path.getsize(path)
        
        usage = ""
        category = ""
        
        if "logo" in f:
            category = "Core Visual Assets (Logos & Badges)"
            if "circle" in f:
                usage = "Circular channel logo badge overlayed directly over Veo watermark in bottom-right corner (45x45 or 76x76 size)."
            elif "capsule" in f:
                usage = "Capsule-shaped logo overlay for annotations or intro templates."
            else:
                usage = "Main logo graphic used for channel branding."
        elif f.startswith("intro"):
            category = "Intro & Outro Templates"
            if f.endswith(".mp4"):
                usage = "Intro video clip (approx. 2 seconds) merged at the very beginning of the video."
            elif f.endswith(".wav"):
                usage = "Intro sound effect/music wave file."
            elif f.endswith(".png"):
                usage = "Intro graphic template/backdrop."
        elif f.startswith("outro"):
            category = "Intro & Outro Templates"
            if f.endswith(".mp4"):
                usage = "Outro video clip with chime/metal chimes ending animation (approx. 4 seconds) to prompt likes/subscribes."
            elif f.endswith(".wav"):
                usage = "Outro chime sound effect audio file."
            elif f.endswith(".png"):
                usage = "Outro graphic template/backdrop (10-second silent cards for YouTube recommendations)."
        else:
            category = "Miscellaneous Assets"
            usage = "Project asset file."
            
        catalog.append({
            "category": category,
            "filename": f,
            "path": rel_path,
            "abs_path": abs_path,
            "size": size,
            "usage": usage
        })

# Scan graphics
graphics_dir = os.path.join(ASSETS_DIR, "graphics")
if os.path.exists(graphics_dir):
    for f in os.listdir(graphics_dir):
        path = os.path.join(graphics_dir, f)
        if os.path.isfile(path):
            rel_path = os.path.relpath(path, ROOT_DIR)
            abs_path = os.path.abspath(path)
            size = os.path.getsize(path)
            
            category = "Graphics & Characters"
            usage = get_desc(rel_path)
            
            if "stickman" in f:
                usage = usage or f"Stickman illustration representing characters in scenarios ({f.replace('.png', '').replace('stickman_', '')})."
            elif "obj_" in f:
                category = "Graphics & Scene Props"
                usage = usage or f"Scene prop outline used in drawings ({f.replace('.png', '').replace('obj_', '')})."
            elif "animal_" in f:
                category = "Graphics & Scene Props"
                usage = usage or f"Animal outline illustration ({f.replace('.png', '').replace('animal_', '')})."
            elif "effect_" in f or "badge_" in f:
                category = "Visual Highlights & Badges"
                usage = usage or f"Visual annotation effect overlay ({f.replace('.png', '')})."
                
            catalog.append({
                "category": category,
                "filename": f,
                "path": rel_path,
                "abs_path": abs_path,
                "size": size,
                "usage": usage
            })

# Scan graphics/letters
letters_dir = os.path.join(ASSETS_DIR, "graphics", "letters")
if os.path.exists(letters_dir):
    for f in os.listdir(letters_dir):
        if f.endswith(".png"):
            path = os.path.join(letters_dir, f)
            rel_path = os.path.relpath(path, ROOT_DIR)
            abs_path = os.path.abspath(path)
            size = os.path.getsize(path)
            
            category = "Korean Alphabet & Words (Overlay PNGs)"
            usage = ""
            if f.startswith("letter_"):
                char = f.replace("letter_", "").replace(".png", "")
                usage = f"High-quality line art overlay card for the Korean letter '{char}'."
            elif f.startswith("word_"):
                word = f.replace("word_", "").replace(".png", "")
                usage = f"High-quality line art overlay card for the Korean word '{word}'."
                
            catalog.append({
                "category": category,
                "filename": f,
                "path": rel_path,
                "abs_path": abs_path,
                "size": size,
                "usage": usage
            })

# Scan audio (excluding scene cache)
audio_dir = os.path.join(ASSETS_DIR, "audio")
if os.path.exists(audio_dir):
    for f in os.listdir(audio_dir):
        if f.endswith(".wav") or f.endswith(".mp3"):
            if f.startswith("scene_") or f.startswith("intro_narration") or f.startswith("outro_narration"):
                # Skip scene caches to keep catalog clean, as they are generated dynamically
                continue
            path = os.path.join(audio_dir, f)
            rel_path = os.path.relpath(path, ROOT_DIR)
            abs_path = os.path.abspath(path)
            size = os.path.getsize(path)
            
            category = "Audio & Sound Effects"
            usage = ""
            if "bell" in f or "chime" in f:
                usage = "Bell chime sound effect played during transitions or outro chimes."
            elif "whoosh" in f:
                usage = "Whoosh sound effect played during fast transitions."
            elif "pop" in f:
                usage = "Pop/click sound effect played when badge highlights or words pop in."
            elif "kpop" in f or "song" in f:
                usage = "Background music (BGM) track for the video assembly."
                
            catalog.append({
                "category": category,
                "filename": f,
                "path": rel_path,
                "abs_path": abs_path,
                "size": size,
                "usage": usage
            })

# Scan images
images_dir = os.path.join(ASSETS_DIR, "images")
if os.path.exists(images_dir):
    for f in os.listdir(images_dir):
        if f.endswith(".png"):
            path = os.path.join(images_dir, f)
            rel_path = os.path.relpath(path, ROOT_DIR)
            abs_path = os.path.abspath(path)
            size = os.path.getsize(path)
            catalog.append({
                "category": "Prepared Base Images",
                "filename": f,
                "path": rel_path,
                "abs_path": abs_path,
                "size": size,
                "usage": f"Pre-prepared base image used for scene {f[:-4]} generation."
            })

# Group catalog by category
grouped = {}
for item in catalog:
    cat = item["category"]
    if cat not in grouped:
        grouped[cat] = []
    grouped[cat].append(item)

# Build markdown
md = []
md.append("# AutoVideo Asset Specification & Catalog")
md.append("\n> **오토비디오 프로젝트 내 공용 비디오/오디오/이미지/프로필 에셋 목록 데이터베이스**")
md.append("> ")
md.append("> *본 명세서는 조감독(Gemini)이 작성하여 감독(Claude)에게 전달하는 자료입니다.*")
md.append("> *MoviePy 합본 렌더러와 구글 플로우 Playwright 자동화 스크립트 작성 시 해당 파일 주소(Path)와 사용 목적을 반드시 준수해 주십시오.*")
md.append("\n---\n")

for cat, items in sorted(grouped.items()):
    md.append(f"## {cat}")
    md.append("")
    md.append("| 파일명 (Filename) | 파일 절대 경로 (Absolute File Path) | 파일 크기 (Size) | 용도 및 사용처 (Usage) |")
    md.append("| :--- | :--- | :--- | :--- |")
    for item in sorted(items, key=lambda x: x["filename"]):
        # Format Windows absolute file paths with file:/// and forward slashes
        clean_abs_path = item['abs_path'].replace('\\', '/')
        if not clean_abs_path.startswith('/'):
            clean_abs_path = '/' + clean_abs_path
        path_link = f"[{item['filename']}](file://{clean_abs_path})"
        size_str = format_size(item['size'])
        md.append(f"| `{item['filename']}` | {path_link} | {size_str} | {item['usage']} |")
    md.append("")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Asset catalog written to {OUTPUT_FILE}")
