# -*- coding: utf-8 -*-
"""
지은 일상생활 동작 24종을 '이미지재생성'으로 순차 생성 및 DB 등록.
- home_vocab/jieun_pose_prompts.txt의 각 동작을 순차 처리.
- 멱등성: 이미 생성되어 DB에 casual 태그가 등록된 경우 skip.
- 레퍼런스: 정면(front) -> jieun_casual_front, 측면(side) -> jieun_casual_side
- 도구: scratch/flow_pose.py 호출 (subprocess)
- 등록: Supabase character_assets 업로드/upsert 및 로컬 content.db assets 테이블 upsert

사용: python scratch/generate_casual_poses.py
"""
import os
import sys
import sqlite3
import subprocess
import hashlib
import psycopg2

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKET = "character-base"
METHOD_DOC = "POSE_GENERATION_METHOD.md"
STYLE = ("minimalist 2D line art, thick clean black outlines, whiteboard marker style, "
         "light beige background (#F5F5F0)")

def load_env(p=None):
    p = p or os.path.join(ROOT, ".env")
    d = {}
    if not os.path.exists(p):
        print(f"[WARN] .env 파일이 없습니다: {p}")
        return d
    with open(p, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                d[k.strip()] = v.strip().strip('"').strip("'")
    return d

def get_registered_casual_keys(env):
    """이미 DB에 casual 태그와 함께 등록 완료된 key 목록 반환"""
    try:
        conn = psycopg2.connect(
            host=env["SUPABASE_DB_HOST"], port=env.get("SUPABASE_DB_PORT", "5432"),
            user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
            dbname=env.get("SUPABASE_DB_NAME", "postgres"), sslmode="require", connect_timeout=20)
        cur = conn.cursor()
        cur.execute("SELECT key FROM character_assets WHERE character_id='jieun' AND 'casual'=ANY(tags)")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {r[0] for r in rows}
    except Exception as ex:
        print(f"[WARN] DB 연동 중 오류 발생 (진행 상태 우선): {ex}")
        return set()

def register_asset(env, key, pose, view, file_path, prompt):
    url = env.get("SUPABASE_URL")
    if not url:
        print("[FAIL] SUPABASE_URL가 정의되어 있지 않습니다.")
        return False

    local_path = os.path.join(ROOT, file_path)
    if not os.path.exists(local_path):
        print(f"[FAIL] 로컬 파일이 존재하지 않습니다: {file_path}")
        return False

    base = os.path.basename(file_path)
    public_url = f"{url}/storage/v1/object/public/{BUCKET}/{base}"

    # 1. Supabase Storage 업로드
    try:
        from supabase import create_client
        sb = create_client(url, env["SUPABASE_KEY"])
        try:
            sb.storage.from_(BUCKET).remove([base])
        except Exception:
            pass
        with open(local_path, "rb") as fh:
            sb.storage.from_(BUCKET).upload(
                path=base, file=fh.read(),
                file_options={"content-type": "image/png", "upsert": "true"})
        print(f"  [storage] {base} 업로드 완료")
    except Exception as ex:
        print(f"  [ERR] Storage 업로드 실패 ({base}): {ex}")
        return False

    # 2. Supabase DB upsert
    try:
        conn = psycopg2.connect(
            host=env["SUPABASE_DB_HOST"], port=env.get("SUPABASE_DB_PORT", "5432"),
            user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
            dbname=env.get("SUPABASE_DB_NAME", "postgres"), sslmode="require", connect_timeout=20)
        cur = conn.cursor()
        tags = sorted({"jieun", "female", "pose", "casual", "평상복", "이미지재생성", view, pose, key})
        cur.execute("""
            INSERT INTO character_assets
              (key,character_id,view,pose,file_path,storage_url,method,style,tags,method_doc)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (key) DO UPDATE SET character_id=EXCLUDED.character_id,view=EXCLUDED.view,
              pose=EXCLUDED.pose,file_path=EXCLUDED.file_path,storage_url=EXCLUDED.storage_url,
              method=EXCLUDED.method,style=EXCLUDED.style,tags=EXCLUDED.tags,method_doc=EXCLUDED.method_doc;
        """, (key, "jieun", view, pose, file_path, public_url,
              "reference2img", STYLE, tags, METHOD_DOC))
        conn.commit()
        cur.close()
        conn.close()
        print(f"  [character_assets] {key} Supabase 등록 완료")
    except Exception as ex:
        print(f"  [ERR] Supabase DB 등록 실패 ({key}): {ex}")
        return False

    # 3. 로컬 SQLite upsert
    try:
        db_path = os.path.join(ROOT, "channel", "content.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("DELETE FROM assets WHERE name_en = ?", (key,))
            # kr mapping (임시로 key를 이용하거나 정성 한글 맵핑)
            kr_name = key.replace("jieun_", "지은_")
            cur.execute(
                "INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                (kr_name, key, "character", base, prompt))
            conn.commit()
            conn.close()
            print(f"  [local assets] {key} SQLite 등록 완료")
    except Exception as ex:
        print(f"  [ERR] SQLite 등록 실패 ({key}): {ex}")
        return False

    return True

def parse_prompts_file(p):
    poses = []
    with open(p, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#") or ":" not in ln:
                continue
            k, pr = ln.split(":", 1)
            k = k.strip()
            pr = pr.strip()
            poses.append((k, pr))
    return poses

def write_report(completed_list):
    """scratch/gemini_report.md 파일 생성/갱신"""
    report_path = os.path.join(ROOT, "scratch", "gemini_report.md")
    
    # Existing report read if any
    existing_content = ""
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

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

    for item in completed_list:
        local_file = os.path.join(ROOT, item["file"])
        file_md5 = ""
        size_str = "0 bytes"
        if os.path.exists(local_file):
            h = hashlib.md5()
            with open(local_file, "rb") as f:
                for b in iter(lambda: f.read(65536), b""):
                    h.update(b)
            file_md5 = h.hexdigest()
            size_str = f"{os.path.getsize(local_file) / 1024:.1f} KB"
            
        lines.append(f"| `{item['key']}` | `{item['pose']}` | `{item['view']}` | `{item['file']}` | `{file_md5}` | {size_str} ({item['status']}) |")

    new_report = "\n".join(lines) + "\n"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(new_report)
    print(f"[REPORT] 보고서가 {report_path} 에 갱신되었습니다.")

def main():
    env = load_env()
    prompts_path = os.path.join(ROOT, "home_vocab", "jieun_pose_prompts.txt")
    if not os.path.exists(prompts_path):
        print(f"[FAIL] 프롬프트 파일이 없습니다: {prompts_path}")
        return 1

    poses_to_gen = parse_prompts_file(prompts_path)
    registered_keys = get_registered_casual_keys(env)
    print(f"[INFO] 총 {len(poses_to_gen)}개 동작 중 {len(registered_keys)}개 이미 DB 등록됨 (casual 태그 기준)")

    completed_list = []
    # 1단계에서 등록한 casual base 3종 정보 추가
    for base_key, view in [("jieun_casual_front", "front"), ("jieun_casual_side", "side"), ("jieun_casual_back", "back")]:
        completed_list.append({
            "key": base_key,
            "pose": "standing",
            "view": view,
            "file": f"home_vocab/{base_key}.png",
            "status": "Base Registered"
        })

    for key, prompt in poses_to_gen:
        # Determine view and reference key
        prompt_lower = prompt.lower()
        if "side profile view" in prompt_lower or "side view" in prompt_lower:
            if "side-front" not in prompt_lower:
                ref_key = "jieun_casual_side"
                view = "side"
            else:
                ref_key = "jieun_casual_front"
                view = "front"
        else:
            ref_key = "jieun_casual_front"
            view = "front"

        # Determine pose name from key
        pose_name = key.replace("jieun_", "")

        file_path = f"home_vocab/{key}.png"

        # 멱등성 체크: DB에 casual로 이미 등록되어 있고, 로컬 파일도 존재한다면 Skip
        if key in registered_keys and os.path.exists(os.path.join(ROOT, file_path)):
            print(f"[{key}] 이미 생성 및 등록 완료되어 건너뜁니다.")
            completed_list.append({
                "key": key,
                "pose": pose_name,
                "view": view,
                "file": file_path,
                "status": "Skipped (Already Registered)"
            })
            continue

        print(f"\n==========================================")
        print(f"시작: {key} (Ref: {ref_key}, View: {view})")
        print(f"Prompt: {prompt}")
        print(f"==========================================")

        # flow_pose.py subprocess 실행
        cmd = [
            sys.executable, "scratch/flow_pose.py",
            "--ref-key", ref_key,
            "--out-key", key,
            "--prompt", prompt,
            "--casual"
        ]
        
        try:
            res = subprocess.run(cmd, cwd=ROOT)
            if res.returncode != 0:
                print(f"[FAIL] {key} 생성 중 에러 발생 (returncode={res.returncode})")
                completed_list.append({
                    "key": key,
                    "pose": pose_name,
                    "view": view,
                    "file": file_path,
                    "status": "Generation Failed"
                })
                write_report(completed_list)
                continue
        except Exception as e:
            print(f"[FAIL] {key} 실행 에러: {e}")
            completed_list.append({
                "key": key,
                "pose": pose_name,
                "view": view,
                "file": file_path,
                "status": f"Exec Error: {e}"
            })
            write_report(completed_list)
            continue

        # DB 등록
        if register_asset(env, key, pose_name, view, file_path, prompt):
            completed_list.append({
                "key": key,
                "pose": pose_name,
                "view": view,
                "file": file_path,
                "status": "Success"
            })
        else:
            completed_list.append({
                "key": key,
                "pose": pose_name,
                "view": view,
                "file": file_path,
                "status": "DB Registration Failed"
            })
        
        write_report(completed_list)

    print("\n[COMPLETE] 모든 동작 순차 생성 및 등록 처리 루프 완료!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
