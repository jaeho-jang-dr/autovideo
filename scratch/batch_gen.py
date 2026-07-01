# -*- coding: utf-8 -*-
"""
batch_gen.py — 일반화 캐릭터 동작 배치 생성기 (이미지재생성 / Google Flow)

기존 scratch/batch_poses.py(지은 전용)를 임의 캐릭터로 일반화하고,
★ 생성에 쓴 프롬프트(스크립트)를 이미지와 함께 DB에 기록한다 (사용자 요청 2026-06-20):
  - Supabase character_assets.flow_prompt
  - SQLite  channel/content.db  assets.flow_prompt

검증된 단일세션 방식: 베이스 업로드 → 더보기(⋮)→'프롬프트에 추가' → 동작 스크립트 → ENTER
→ 왼편 '새' 타일만 다운로드(md5 중복검증). 측면 동작은 측면 베이스를 레퍼런스로.
3회 재시도 + 실패 시 브라우저 리부트.

사용법:
  python scratch/batch_gen.py --prompts home_vocab/injun_activities_prompts.txt \
      --char injun --ref-key injun_navy_front_opaque --side-ref injun_navy_side_opaque
  python scratch/batch_gen.py --prompts home_vocab/injun_jieun_couple_prompts.txt \
      --char injun_jieun --ref-key injun_jieun_handshake_facing_opaque
"""
import os, sys, glob, time, argparse, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "scratch"))

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

# 캐릭터별 일관성 프리픽스 (flow_pose.py 와 동일 문구). "draw him/them " 로 끝나야 동작 구절이 자연스럽게 이어진다.
PREFIXES = {
    "injun": ("Using the uploaded reference image, keep the EXACT same Korean boy character Injun "
              "— same short neat black hair, same face, same casual short-sleeve navy t-shirt and pants "
              "— but now draw him "),
    "injun_jieun": ("Using the uploaded reference image, keep the EXACT same two Korean characters "
                    "standing side-by-side — Injun (a Korean boy with short neat black hair, wearing a simple "
                    "casual short-sleeve navy t-shirt and pants) and Jieun (a Korean schoolgirl with long brown "
                    "hair, wearing a navy and white sailor school uniform with a red neckerchief and a navy "
                    "pleated skirt) — but now draw them "),
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

def view_of(key, prompt):
    s = (key + " " + prompt).lower()
    if "side view" in s or "side profile" in s:
        return "side"
    if "back" in s:
        return "back"
    return "front"

def register(key, action_prompt, char_id):
    """이미지 + 프롬프트를 Supabase / SQLite 양쪽에 기록."""
    pose = key
    for p in ("injun_jieun_", "injun_", char_id + "_"):
        if pose.startswith(p):
            pose = pose[len(p):]; break
    view = "pair" if char_id == "injun_jieun" else view_of(key, action_prompt)
    file_path = f"home_vocab/{key}.png"

    # 1) Supabase Storage + DB (flow_prompt 포함)
    try:
        import psycopg2
        from supabase import create_client
        url = env_vars["SUPABASE_URL"]
        sb = create_client(url, env_vars["SUPABASE_KEY"])
        base = os.path.basename(file_path)
        local = os.path.join(ROOT, file_path)
        public = f"{url}/storage/v1/object/public/{BUCKET}/{base}"
        try:
            sb.storage.from_(BUCKET).remove([base])
        except Exception:
            pass
        with open(local, "rb") as fh:
            sb.storage.from_(BUCKET).upload(
                path=base, file=fh.read(),
                file_options={"content-type": "image/png", "upsert": "true"})
        conn = psycopg2.connect(
            host=env_vars["SUPABASE_DB_HOST"], port=env_vars.get("SUPABASE_DB_PORT", "5432"),
            user=env_vars["SUPABASE_DB_USER"], password=env_vars["SUPABASE_DB_PASSWORD"],
            dbname=env_vars.get("SUPABASE_DB_NAME", "postgres"), sslmode="require", connect_timeout=20)
        cur = conn.cursor()
        tags = sorted({char_id, "pose", "reference2img", view, pose, key})
        cur.execute("""
            INSERT INTO character_assets
              (key,character_id,view,pose,file_path,storage_url,method,style,tags,method_doc,flow_prompt)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (key) DO UPDATE SET character_id=EXCLUDED.character_id,view=EXCLUDED.view,
              pose=EXCLUDED.pose,file_path=EXCLUDED.file_path,storage_url=EXCLUDED.storage_url,
              method=EXCLUDED.method,style=EXCLUDED.style,tags=EXCLUDED.tags,method_doc=EXCLUDED.method_doc,
              flow_prompt=EXCLUDED.flow_prompt;
        """, (key, char_id, view, pose, file_path, public,
              "reference2img", STYLE, tags, METHOD_DOC, action_prompt))
        conn.commit(); cur.close(); conn.close()
        print(f"  [Supabase] {key} (flow_prompt 기록)")
    except Exception as ex:
        print(f"  [Supabase ERR] {key}: {ex}")

    # 2) SQLite content.db (flow_prompt 포함)
    try:
        db = os.path.join(ROOT, "channel", "content.db")
        c = sqlite3.connect(db); cu = c.cursor()
        cu.execute("DELETE FROM assets WHERE name_en = ?", (key,))
        cu.execute("INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                   (key, key, "character", os.path.basename(file_path), action_prompt))
        c.commit(); c.close()
        print(f"  [SQLite] {key} (flow_prompt 기록)")
    except Exception as ex:
        print(f"  [SQLite ERR] {key}: {ex}")

def launch_chrome():
    af.force_kill_profile_chrome()
    lk = os.path.join(af.PROFILE, "SingletonLock")
    if os.path.exists(lk):
        try: os.remove(lk)
        except Exception: pass
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", required=True, help="key: action 프롬프트 파일")
    ap.add_argument("--char", required=True, help="character_id (injun | injun_jieun)")
    ap.add_argument("--ref-key", required=True, help="기본(정면) 레퍼런스 베이스 key")
    ap.add_argument("--side-ref", default=None, help="측면 동작용 레퍼런스 베이스 key (옵션)")
    ap.add_argument("--retries", type=int, default=3)
    args = ap.parse_args()

    prefix_char = PREFIXES.get(args.char)
    if not prefix_char:
        print(f"[FATAL] 알 수 없는 char: {args.char} (지원: {list(PREFIXES)})"); return

    tasks = []
    with open(os.path.join(ROOT, args.prompts), encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#"): continue
            if ":" in ln:
                k, v = ln.split(":", 1)
                tasks.append((k.strip(), v.strip()))
    print(f"Loaded {len(tasks)} prompts from {args.prompts}")

    todo = []
    for key, prompt in tasks:
        out = os.path.join(ROOT, "home_vocab", f"{key}.png")
        if os.path.exists(out):
            print(f"이미 존재: {key} → 재등록만 수행")
            register(key, prompt, args.char)
        else:
            todo.append((key, prompt))
    if not todo:
        print("모든 항목 생성/등록 완료."); return
    print(f"생성 대상: {len(todo)}개")

    pw = ctx = page = None
    try:
        pw, ctx, page = launch_chrome()
        existing = {}
        for f in glob.glob(os.path.join(ROOT, "home_vocab", "*.png")):
            try: existing[md5(f)] = os.path.basename(f)
            except Exception: pass

        for i, (key, prompt) in enumerate(todo):
            print(f"\n[{i+1}/{len(todo)}] {key}")
            ref_key = args.side_ref if (args.side_ref and view_of(key, prompt) == "side") else args.ref_key
            try:
                ref_path = fetch_ref(ref_key)
            except Exception as e:
                print(f"  ref fetch 실패 {ref_key}: {e} → skip"); continue
            full_prompt = prefix_char + prompt.strip() + SUFFIX

            out_file = os.path.join(ROOT, "home_vocab", f"{key}.png")
            ok = False
            for attempt in range(1, args.retries + 1):
                print(f"  시도 {attempt}/{args.retries}")
                try:
                    if make_one(page, ref_path, full_prompt, out_file, existing, transparent=True):
                        ok = True; break
                except Exception as ex:
                    print(f"  make_one 예외: {ex}")
                time.sleep(5)
            if ok:
                print(f"  ✅ {key} 생성")
                try: existing[md5(out_file)] = os.path.basename(out_file)
                except Exception: pass
                register(key, prompt, args.char)
            else:
                print(f"  ❌ {key} 3회 실패 → 브라우저 리부트")
                try: ctx.close(); pw.stop()
                except Exception: pass
                time.sleep(5)
                pw, ctx, page = launch_chrome()
    finally:
        if ctx:
            try: ctx.close()
            except Exception: pass
        if pw:
            try: pw.stop()
            except Exception: pass
        print("Done.")

if __name__ == "__main__":
    main()
