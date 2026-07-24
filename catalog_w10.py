# -*- coding: utf-8 -*-
"""W10 자산 카탈로그 → content.db. 이미지=로컬, 텍스트=로컬+DB(내용까지).
   asset_catalog(어떤 데이터가 어디에 얼마나) + project_texts(텍스트 자산 내용 저장)."""
import sqlite3, os, glob

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.chdir(ROOT)
DB = "channel/content.db"
PROJECT = "W10"; EPISODE = "KO-W10"

W10WORDS = ["얼마예요","이거 주세요","그거 주세요","저거 주세요","결제","할인","이거 얼마예요",
            "오천 원","오천 원이에요","지금 할인 중이에요","카드","현금","전부 얼마예요","한 개 주세요",
            "두 개 주세요","다른 거 있어요","더 큰 거","봉투 주세요","영수증 주세요","좀 깎아 주세요",
            "너무 비싸요","만 원이에요","숫자","가게"]
SCRIPTS = ["build_w10.py","gen_bg_w10.sh","gen_injun_w10_poses.sh","cutout_register_w10.py",
           "gen_db_azure.py","catalog_w10.py","review_lesson.py","compile_np.py"]

def dsize(paths):
    n = b = 0
    for p in paths:
        if os.path.exists(p): n += 1; b += os.path.getsize(p)
    return n, b

con = sqlite3.connect(DB); cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS asset_catalog(
  id INTEGER PRIMARY KEY, project TEXT, category TEXT, name TEXT, location TEXT,
  kind TEXT, storage TEXT, count INTEGER, bytes INTEGER, db_table TEXT, note TEXT, updated_at TEXT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS project_texts(
  id INTEGER PRIMARY KEY, project TEXT, name TEXT, path TEXT, kind TEXT, content TEXT, updated_at TEXT)""")
cur.execute("DELETE FROM asset_catalog WHERE project=?", (PROJECT,))
cur.execute("DELETE FROM project_texts WHERE project=?", (PROJECT,))

def cat(category, name, location, kind, storage, paths=None, count=None, bytes_=None, db_table="", note=""):
    if paths is not None: count, bytes_ = dsize(paths)
    cur.execute("""INSERT INTO asset_catalog(project,category,name,location,kind,storage,count,bytes,db_table,note,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
                (PROJECT, category, name, location, kind, storage, count or 0, bytes_ or 0, db_table, note))

def dbcount(sql, args=()):
    return cur.execute(sql, args).fetchone()[0]

# --- 이미지 (로컬) ---
cat("배경", "bg_w10 (해변/상점/계산대/세일)", "assets/graphics/bg/", "image", "local",
    glob.glob("assets/graphics/bg/bg_w10_*.png"), note="agy 생성, 광안리+객체, 글자없이 16:9")
cat("캐릭터정의", "injun_w10 (컷아웃)", "content.db", "db", "db",
    count=dbcount("SELECT COUNT(*) FROM anim_characters WHERE char_key='injun_w10'"),
    db_table="anim_characters", note="render_mode=cutout, pose_prefix=injun_w10_")
cat("캐릭터포즈", "injun_w10 투명 컷아웃", "assets/graphics/poses/", "image", "local+db",
    glob.glob("assets/graphics/poses/injun_w10_*.png"), db_table="anim_char_poses,assets",
    note="characterang 소스, 흰배경 플러드필 컷아웃")
cat("캐릭터포즈원본", "injun_w10 원본(흰배경)", "home_vocab/w10/", "image", "local",
    glob.glob("home_vocab/w10/injun_w10_*.png"), note="agy 생성 원본 백업")
cat("글자/카드", "w10 동동체 글리프+우상단 카드", "assets/graphics/letters/", "image", "local+db",
    glob.glob("assets/graphics/letters/w10_*.png"), db_table="assets", note="Cafe24Dongdong 글자 + 추천 카드")
# --- 모션·시나리오 (DB) ---
cat("캐릭터모션", "injun_w10_s01~30 안무", "content.db", "db", "db",
    count=dbcount("SELECT COUNT(*) FROM anim_sequences WHERE seq_name LIKE 'injun_w10_s%'"),
    db_table="anim_sequences", note="씬별 포즈 시퀀스 beats_json")
cat("씬객체", "KO-W10 scene_objects (글자·인준·카드 배치)", "content.db", "db", "db",
    count=dbcount("SELECT COUNT(*) FROM scene_objects WHERE episode=?", (EPISODE,)),
    db_table="scene_objects", note="cx/cy/scale/z_order/motion_type")
cat("시나리오", "KO-W10 30씬 대본(한/영)", "content.db + hangeul_birth_vowels/w10_scenario_expanded.md",
    "text", "local+db", count=dbcount("SELECT COUNT(*) FROM scenes WHERE episode=?", (EPISODE,)),
    db_table="scenes", note="script_kr/en, 내용 project_texts에도 저장")
# --- 오디오 (로컬) ---
cat("발음클립", "W10 인준 발음(Azure InJoon)", "web/public/audio/jamo_m/", "audio", "local",
    [f"web/public/audio/jamo_m/{w}.mp3" for w in W10WORDS], note="나레이션 사이 삽입, Azure 라이선스")
# --- 자막·영상 (로컬, 자막 내용은 DB에도) ---
cat("자막", "ko/en srt (5개국어는 업로드시)", "hangeul_birth_vowels/", "text", "local+db",
    ["hangeul_birth_vowels/hangeul_w10_injun_np.ko.srt", "hangeul_birth_vowels/hangeul_w10_injun_np.en.srt"],
    note="소프트자막, 내용 project_texts에 저장")
cat("영상", "4K ko/en mp4 (Kanna/Alice)", "hangeul_birth_vowels/", "video", "local",
    ["hangeul_birth_vowels/hangeul_w10_injun_np_ko.mp4", "hangeul_birth_vowels/hangeul_w10_injun_np_en.mp4"],
    note="3840x2160, ElevenLabs 나레이션")
# --- 스크립트 (로컬+DB 내용) ---
cat("스크립트", "W10 제작 스크립트", "(repo root)", "text", "local+db",
    [s for s in SCRIPTS], db_table="project_texts", note="내용 project_texts에 저장")

# project_texts: 텍스트 자산 내용 저장
def store_text(name, path, kind):
    if os.path.exists(path):
        try: content = open(path, encoding="utf-8").read()
        except Exception: content = open(path, encoding="utf-8", errors="ignore").read()
        cur.execute("INSERT INTO project_texts(project,name,path,kind,content,updated_at) VALUES(?,?,?,?,?,datetime('now'))",
                    (PROJECT, name, path, kind, content))
        return True
    return False
for s in SCRIPTS: store_text(s, s, "script")
store_text("w10_scenario_expanded.md", "hangeul_birth_vowels/w10_scenario_expanded.md", "scenario_doc")
store_text("w10_injun_pose_prompts.txt", "hangeul_birth_vowels/w10_injun_pose_prompts.txt", "pose_prompts")
store_text("hangeul_w10_injun_np.ko.srt", "hangeul_birth_vowels/hangeul_w10_injun_np.ko.srt", "subtitle")
store_text("hangeul_w10_injun_np.en.srt", "hangeul_birth_vowels/hangeul_w10_injun_np.en.srt", "subtitle")

con.commit()
# 요약
print("=== W10 asset_catalog ===")
tot = 0
for r in cur.execute("SELECT category,name,location,kind,storage,count,bytes,db_table FROM asset_catalog WHERE project=? ORDER BY id", (PROJECT,)):
    tot += r[6]
    print(f"  [{r[0]:8}] {r[1][:34]:34} | {r[3]:5}/{r[4]:8} | {r[5]:3}개 {r[6]//1024:6}KB | {r[2][:36]}")
print(f"  이미지/영상/오디오 로컬 합계: {tot/1e6:.1f} MB")
print("project_texts(텍스트 내용 DB저장):", dbcount("SELECT COUNT(*) FROM project_texts WHERE project=?", (PROJECT,)), "건")
con.close()
print("### 카탈로그 완료 ###")
