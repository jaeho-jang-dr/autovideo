# -*- coding: utf-8 -*-
"""기존 커플(injun_jieun_*) 이미지를 Supabase character_assets에 백필 등록.
characters 테이블에 injun_jieun FK가 없어 초기 배치 때 Supabase 등록이 실패했던 분들 복구.
flow_prompt 는 SQLite content.db(assets) 또는 친구 프롬프트 파일에서 가져온다."""
import os, glob, sqlite3
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

def le(p=None):
    p = p or os.path.join(ROOT, ".env"); d={}
    for ln in open(p, encoding="utf-8"):
        ln=ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k,v=ln.split("=",1); d[k.strip()]=v.strip().strip('"').strip("'")
    return d
E=le()
BUCKET="character-base"; STYLE=("minimalist 2D line art, thick clean black outlines, whiteboard marker style, "
                                "light beige background (#F5F5F0)"); METHOD_DOC="POSE_GENERATION_METHOD.md"

# prompt 사전: SQLite assets.flow_prompt + 프롬프트 파일들
prompts={}
for pf in ("injun_jieun_friends_prompts.txt","piano_scene1_prompts.txt","piano_scene2_prompts.txt","selfie_fix_prompts.txt"):
    fp=os.path.join(ROOT,"home_vocab",pf)
    if os.path.exists(fp):
        for ln in open(fp,encoding="utf-8"):
            ln=ln.strip()
            if ln and not ln.startswith("#") and ":" in ln:
                k,v=ln.split(":",1); prompts[k.strip()]=v.strip()
try:
    sc=sqlite3.connect(os.path.join(ROOT,"channel","content.db")); scur=sc.cursor()
    for k,fpr in scur.execute("SELECT name_en,flow_prompt FROM assets WHERE name_en LIKE 'injun_jieun_%'"):
        if fpr: prompts.setdefault(k,fpr)
    sc.close()
except Exception as ex: print("[sqlite read warn]",ex)

import psycopg2
from supabase import create_client
url=E["SUPABASE_URL"]; sb=create_client(url,E["SUPABASE_KEY"])
conn=psycopg2.connect(host=E["SUPABASE_DB_HOST"],port=E.get("SUPABASE_DB_PORT","5432"),
    user=E["SUPABASE_DB_USER"],password=E["SUPABASE_DB_PASSWORD"],
    dbname=E.get("SUPABASE_DB_NAME","postgres"),sslmode="require",connect_timeout=20)
cur=conn.cursor()

files=sorted(glob.glob(os.path.join(ROOT,"home_vocab","injun_jieun_*.png")))
files=[f for f in files if not os.path.basename(f).startswith("_") and "handshake" not in f and "_opaque" not in f and "pair" not in os.path.basename(f)]
ok=0
for f in files:
    key=os.path.basename(f)[:-4]
    pose=key.replace("injun_jieun_","")
    view="pair"
    public=f"{url}/storage/v1/object/public/{BUCKET}/{os.path.basename(f)}"
    fpr=prompts.get(key)
    try:
        try: sb.storage.from_(BUCKET).remove([os.path.basename(f)])
        except Exception: pass
        with open(f,"rb") as fh:
            sb.storage.from_(BUCKET).upload(path=os.path.basename(f),file=fh.read(),
                file_options={"content-type":"image/png","upsert":"true"})
        tags=sorted({"injun_jieun","pair","friends","reference2img",view,pose,key})
        cur.execute("""INSERT INTO character_assets
              (key,character_id,view,pose,file_path,storage_url,method,style,tags,method_doc,flow_prompt)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (key) DO UPDATE SET character_id=EXCLUDED.character_id,view=EXCLUDED.view,
              pose=EXCLUDED.pose,file_path=EXCLUDED.file_path,storage_url=EXCLUDED.storage_url,
              method=EXCLUDED.method,style=EXCLUDED.style,tags=EXCLUDED.tags,method_doc=EXCLUDED.method_doc,
              flow_prompt=EXCLUDED.flow_prompt;""",
            (key,"injun_jieun",view,pose,f"home_vocab/{key}.png",public,"reference2img",STYLE,tags,METHOD_DOC,fpr))
        conn.commit(); ok+=1
        print(f"  [backfill] {key} (prompt={'Y' if fpr else 'N'})")
    except Exception as ex:
        conn.rollback(); print(f"  [ERR] {key}: {ex}")
print(f"backfilled {ok}/{len(files)} couple assets to Supabase.")
cur.close(); conn.close()
