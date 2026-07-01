# -*- coding: utf-8 -*-
import os
import sys
import glob
import time
import sqlite3
import psycopg2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "scratch"))

# Force UTF-8 logging
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

import autoveo_flow as af
from scratch.flow_pose import make_one, fetch_ref, md5, SUFFIX

BUCKET = "character-base"
METHOD_DOC = "POSE_GENERATION_METHOD.md"
STYLE = ("minimalist 2D line art, thick clean black outlines, whiteboard marker style, "
         "light beige background (#F5F5F0)")
TECH_NAME = "이미지재생성"
TECH_DESC = ("DB의 캐릭터 베이스 사진을 레퍼런스로 같은 캐릭터의 새 동작 사진을 Google Flow로 생성하는 기법. "
             "순서: 새 프로젝트→베이스 사진 업로드→(~25초)타일 더보기(⋮)→'프롬프트에 추가'(입력창 삽입)→"
             "동작 스크립트 입력→ENTER→(~45초)→왼편 '새' 타일만 다운로드(md5 중복검증). "
             "측면 동작은 'EXACTLY ONE single figure' 강제. 크롬 프로필은 한 번에 하나씩 순차 실행.")
TECH_TEMPLATE = ('python scratch/flow_pose.py --ref-key <base_key> --out-key <pose_key> '
                 '--prompt "<action phrase in English>"')

KR_MAP = {
    "jieun_waking_up": "지은_기상",
    "jieun_packing": "지은_준비",
    "jieun_washing_face": "지은_세수",
    "jieun_eating": "지은_식사",
    "jieun_walking": "지은_걷기",
    "jieun_sleeping": "지은_취침",
    "jieun_brushing_teeth": "지은_양치",
    "jieun_studying": "지은_공부",
    "jieun_reading": "지은_독서",
    "jieun_sitting": "지은_휴식",
    "jieun_running": "지은_달리기",
    "jieun_pointing": "지은_지시",
    "jieun_cheering": "지은_환호",
    "jieun_bowing": "지은_인사",
    "jieun_thinking": "지은_생각",
    "jieun_raising_hand": "지은_질문",
    "jieun_drawing": "지은_그리기",
    "jieun_drinking": "지은_음용",
    "jieun_cleaning": "지은_청소",
    "jieun_opening_door": "지은_개문",
    "jieun_putting_on_shoes": "지은_신발신기",
    "jieun_waiting": "지은_대기",
    "jieun_waving": "지은_작별",
    "jieun_clapping": "지은_박수",
    "jieun_jumping": "지은_점프",
}

def load_env(p=None):
    p = p or os.path.join(ROOT, ".env")
    d = {}
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d

env_vars = load_env()

def register_pose(key, prompt):
    pose = key.replace("jieun_", "")
    if "side" in key or "walking" in key or "running" in key or "sleeping" in key:
        view = "side"
    elif "back" in key:
        view = "back"
    else:
        view = "front"
        
    kr = KR_MAP.get(key, f"지은_{pose}")
    file_path = f"home_vocab/{key}.png"
    
    # 1. Supabase Storage Upload & Database Upsert
    try:
        url = env_vars["SUPABASE_URL"]
        conn = psycopg2.connect(
            host=env_vars["SUPABASE_DB_HOST"], port=env_vars.get("SUPABASE_DB_PORT", "5432"),
            user=env_vars["SUPABASE_DB_USER"], password=env_vars["SUPABASE_DB_PASSWORD"],
            dbname=env_vars.get("SUPABASE_DB_NAME", "postgres"), sslmode="require", connect_timeout=20)
        cur = conn.cursor()
        
        from supabase import create_client
        sb = create_client(url, env_vars["SUPABASE_KEY"])
        
        local = os.path.join(ROOT, file_path)
        base = os.path.basename(file_path)
        public = f"{url}/storage/v1/object/public/{BUCKET}/{base}"
        
        try:
            sb.storage.from_(BUCKET).remove([base])
        except Exception:
            pass
            
        with open(local, "rb") as fh:
            sb.storage.from_(BUCKET).upload(
                path=base, file=fh.read(),
                file_options={"content-type": "image/png", "upsert": "true"})
        print(f"  [storage] Uploaded {base}")
        
        tags = sorted({"jieun", "female", "pose", TECH_NAME, view, pose, key})
        cur.execute("""
            INSERT INTO character_assets
              (key,character_id,view,pose,file_path,storage_url,method,style,tags,method_doc)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (key) DO UPDATE SET character_id=EXCLUDED.character_id,view=EXCLUDED.view,
              pose=EXCLUDED.pose,file_path=EXCLUDED.file_path,storage_url=EXCLUDED.storage_url,
              method=EXCLUDED.method,style=EXCLUDED.style,tags=EXCLUDED.tags,method_doc=EXCLUDED.method_doc;
        """, (key, "jieun", view, pose, file_path, public,
              "reference2img", STYLE, tags, METHOD_DOC))
        conn.commit()
        print(f"  [Supabase DB] Registered {key}")
        cur.close()
        conn.close()
    except Exception as ex:
        print(f"  [Supabase ERR] {key}: {ex}")
        
    # 2. SQLite local DB Upsert
    try:
        db = os.path.join(ROOT, "channel", "content.db")
        sqlite_conn = sqlite3.connect(db)
        sqlite_cur = sqlite_conn.cursor()
        
        sqlite_cur.execute("DELETE FROM assets WHERE name_en = ?", (key,))
        sqlite_cur.execute(
            "INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
            (kr, key, "character", os.path.basename(file_path), prompt))
        sqlite_conn.commit()
        sqlite_conn.close()
        print(f"  [SQLite] Registered {key}")
    except Exception as ex:
        print(f"  [SQLite ERR] {key}: {ex}")

def update_report_file():
    report_path = os.path.join(ROOT, "scratch", "gemini_report.md")
    
    lines = [
        "# 지은 일상생활 동작 생성 및 DB 등록 진행 보고서",
        f"- **보고서 갱신일시**: 2026-06-19",
        "- **대상 프로젝트**: `home_vocab` (한국어 어휘 학습 캐릭터 에셋)",
        "- **사용 기법**: `POSE_GENERATION_METHOD.md` (이미지재생성 - Google Flow)",
        "",
        "## 생성 및 등록 완료 에셋 목록",
        "| Key | Pose | View | Local File | MD5 | Status |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    
    png_files = sorted(glob.glob(os.path.join(ROOT, "home_vocab", "jieun_*.png")))
    for f in png_files:
        base = os.path.basename(f)
        key = base[:-4]
        pose = key.replace("jieun_", "")
        
        view = "front"
        if "side" in key or "walking" in key or "running" in key or "sleeping" in key:
            view = "side"
        elif "back" in key:
            view = "back"
            
        m = md5(f)
        size_kb = os.path.getsize(f) / 1024.0
        
        status_str = f"{size_kb:.1f} KB (Success)"
        if "casual" in key or "base" in key:
            status_str = f"{size_kb:.1f} KB (Base Registered)"
            
        lines.append(f"| `{key}` | `{pose}` | `{view}` | `home_vocab/{base}` | `{m}` | {status_str} |")
        
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write("\n".join(lines) + "\n")
    print(f"Report updated.")

def launch_chrome():
    af.force_kill_profile_chrome()
    lk = os.path.join(af.PROFILE, "SingletonLock")
    if os.path.exists(lk):
        try:
            os.remove(lk)
        except Exception:
            pass
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    ctx = pw.chromium.launch_persistent_context(
        af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
        no_viewport=True, accept_downloads=True, downloads_path=af.DL_DIR,
        ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--disable-blink-features=AutomationControlled",
              "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    return pw, ctx, page

def main():
    # 1. Parse prompts
    prompts_file = os.path.join(ROOT, "home_vocab", "jieun_pose_prompts.txt")
    tasks = []
    with open(prompts_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(":", 1)
            if len(parts) == 2:
                tasks.append((parts[0].strip(), parts[1].strip()))
                
    print(f"Loaded {len(tasks)} pose prompts.")
    
    # 2. Filter tasks and handle already generated files
    todo = []
    for key, prompt in tasks:
        out_path = os.path.join(ROOT, "home_vocab", f"{key}.png")
        if os.path.exists(out_path):
            print(f"File exists: {out_path}. Ensuring registered...")
            register_pose(key, prompt)
        else:
            todo.append((key, prompt))
            
    update_report_file()
    
    if not todo:
        print("No pending tasks. All poses generated and registered.")
        return
        
    print(f"Pending tasks to generate: {len(todo)}")
    
    pw = None
    ctx = None
    page = None
    
    try:
        pw, ctx, page = launch_chrome()
        
        # Pre-build existing MD5 dictionary for make_one
        existing = {}
        for f in glob.glob(os.path.join(ROOT, "home_vocab", "*.png")):
            try:
                existing[md5(f)] = os.path.basename(f)
            except Exception:
                pass
                
        for i, (key, prompt) in enumerate(todo):
            print(f"\nProcessing [{i+1}/{len(todo)}] {key}...")
            
            # Determine ref key
            if "side view" in prompt.lower() or "side profile view" in prompt.lower():
                ref_key = "jieun_casual_side"
            else:
                ref_key = "jieun_casual_front"
                
            try:
                ref_path = fetch_ref(ref_key)
            except Exception as e:
                print(f"Failed to fetch ref {ref_key}: {e}. Skipping.")
                continue
                
            # Construct full prompt (using clean "draw her " format)
            prefix_char = ("Using the uploaded reference image, keep the EXACT same Korean girl "
                           "character Jieun — same long brown hair, same face, same body build — "
                           "but now wearing casual everyday clothes (a simple casual t-shirt, casual pants, "
                           "and sneakers, NOT a school uniform), draw her ")
            full_prompt = prefix_char + prompt.strip() + SUFFIX
            
            out_file = os.path.join(ROOT, "home_vocab", f"{key}.png")
            
            success = False
            for attempt in range(1, 4):
                print(f"  Attempt {attempt}/3 for {key}...")
                try:
                    # Run make_one
                    if make_one(page, ref_path, full_prompt, out_file, existing, transparent=True):
                        success = True
                        break
                except Exception as ex:
                    print(f"  Exception in make_one: {ex}")
                
                # If fail, wait a bit
                time.sleep(5)
                
            if success:
                print(f"  Successfully generated {key}!")
                # Add to existing MD5 dict
                try:
                    existing[md5(out_file)] = os.path.basename(out_file)
                except Exception:
                    pass
                # Register
                register_pose(key, prompt)
                update_report_file()
            else:
                print(f"  [ERROR] Failed to generate {key} after 3 attempts.")
                # REBOOT CHROME logic as requested by user guidelines
                print("  Rebooting browser session...")
                try:
                    ctx.close()
                    pw.stop()
                except Exception:
                    pass
                time.sleep(5)
                pw, ctx, page = launch_chrome()
                
    finally:
        if ctx:
            try:
                ctx.close()
            except Exception:
                pass
        if pw:
            try:
                pw.stop()
            except Exception:
                pass
        print("Done.")

if __name__ == "__main__":
    main()
