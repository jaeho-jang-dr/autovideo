# -*- coding: utf-8 -*-
"""db_voice_gate.py — 렌더 전 DB 게이트. 에피소드의 스크립트/드로잉에 나오는 ' ' 한글을
전부 스캔해 DB(web/public/audio/jamo + hangeul_audio_assets, voice컬럼)에 없는 것을 선희로 생성.
원칙: 화면 한글은 자막+나레이션에 다 있어야 하고, DB에 없는 한글 예문은 렌더 전에 DB화.
사용: python db_voice_gate.py KO-W09
"""
import os, re, sys, sqlite3
os.environ.setdefault("EDGE_ACTIVE_VOICE", "sunhi"); os.environ["ELEVEN_API_KEY"] = ""
# TTS_ENGINE는 환경 그대로 존중(azure면 정식 라이선스 Azure로 생성). FORCE_REGEN=1이면 기존 클립도 덮어씀.
FORCE = bool(os.environ.get("FORCE_REGEN"))
sys.path.insert(0, os.getcwd())
from tts_manager import save_tts_edge_tts
EP = sys.argv[1] if len(sys.argv) > 1 else "KO-W09"
JAMO = "web/public/audio/jamo"; DB = "channel/content.db"; VOICE = "선희(ko-KR-SunHiNeural)"
KR = re.compile(r"[가-힣]")
def norm(s):                       # 따옴표 안 텍스트 정규화(파일명 안전: 앞뒤공백·끝문장부호 제거, ?/. 제거)
    s = s.strip().strip("?.!…").strip()
    return re.sub(r"[?/\:*\"<>|]", "", s)
con = sqlite3.connect(DB); cur = con.cursor()
cols = [r[1] for r in cur.execute("PRAGMA table_info(hangeul_audio_assets)")]
if "voice" not in cols: cur.execute("ALTER TABLE hangeul_audio_assets ADD COLUMN voice TEXT")
# 1) 스크립트(kr,en)의 ' ' 안 한글 + 2) scene_objects의 word/example 텍스트
texts = set()
for kr, en in cur.execute("SELECT script_kr, script_en FROM scenes WHERE episode=?", (EP,)):
    for s in (kr or "") + " " + (en or ""), :
        for m in re.findall(r"'([^']*)'", s):
            if KR.search(m): texts.add(norm(m))
for (nm, typ) in cur.execute("""SELECT a.name_kr, a.type FROM scene_objects o JOIN assets a ON a.id=o.asset_id
                                WHERE o.episode=? AND a.type IN ('word','example')""", (EP,)):
    if nm and KR.search(nm): texts.add(norm(nm))
texts = sorted(t for t in texts if t)
made, had = [], []
for t in texts:
    p = os.path.join(JAMO, t + ".mp3")
    if not FORCE and os.path.exists(p) and os.path.getsize(p) > 800:
        had.append(t)
    else:
        try: save_tts_edge_tts(t, p, lang="ko")
        except Exception as e: print("FAIL", t, str(e)[:50]); continue
        made.append(t)
    rel = "/audio/jamo/" + t + ".mp3"
    ex = cur.execute("SELECT id FROM hangeul_audio_assets WHERE text=?", (t,)).fetchone()
    if ex: cur.execute("UPDATE hangeul_audio_assets SET filepath=?, voice=? WHERE id=?", (rel, VOICE, ex[0]))
    else: cur.execute("INSERT INTO hangeul_audio_assets(text,filepath,voice,created_at) VALUES(?,?,?,datetime('now'))", (t, rel, VOICE))
con.commit(); con.close()
print(f"=== {EP} DB게이트 ===  총 {len(texts)}개 / 신규생성 {len(made)} / 기존 {len(had)}")
print("신규:", made)
print("기존:", had)
