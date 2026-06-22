#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
drjay-ed 채널 콘텐츠 데이터베이스 매니저 (SQLite)

이중언어(한국어/영어) 나레이션·자막을 전제로 한 에피소드 제작 파이프라인 트래커.
시각 프롬프트(image/veo)는 언어 중립(영어)이라 언어별로 공유하고,
나레이션 텍스트/오디오/자막/최종 렌더만 언어별로 분리한다.

사용법:
    python channel/content_db.py init        # 스키마 생성
    python channel/content_db.py seed         # 카테고리 + 에피소드 백로그 시드
    python channel/content_db.py stats        # 현황 요약
    python channel/content_db.py list [--status idea] [--category CA] [--priority 1]
    python channel/content_db.py show CA-001  # 에피소드 상세
    python channel/content_db.py set-status CA-001 scripted
    python channel/content_db.py reset        # DROP 후 재생성(주의)

제작 상태: idea -> scripted -> prompts_ready -> assets -> rendering -> published
"""
import argparse
import os
import sqlite3
import sys

# 한글 콘솔 출력 안전장치
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content.db")

STATUS_FLOW = ["idea", "scripted", "prompts_ready", "assets", "rendering", "published"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    code        TEXT PRIMARY KEY,
    name_kr     TEXT NOT NULL,
    name_en     TEXT NOT NULL,
    medical_lens TEXT,            -- 이 축의 시그니처 의학 앵글
    priority    INTEGER DEFAULT 2 -- 1=Tier1, 2=Tier2, 3=Tier3
);

CREATE TABLE IF NOT EXISTS episodes (
    code        TEXT PRIMARY KEY,        -- 예: CA-001
    category    TEXT NOT NULL REFERENCES categories(code),
    title_kr    TEXT NOT NULL,
    title_en    TEXT NOT NULL,
    hook_kr     TEXT,                    -- 오프닝 호기심 질문(한)
    logline_kr  TEXT,                    -- 의학 렌즈 한 줄 요약(내부용)
    status      TEXT DEFAULT 'idea',
    priority    INTEGER DEFAULT 2,
    target_chars_kr INTEGER DEFAULT 1300,-- 한국어 목표 글자수
    target_words_en INTEGER DEFAULT 850, -- 영어 목표 단어수(TED-Ed 800~900)
    runtime_sec INTEGER,
    -- 언어별 산출물 경로
    narration_kr TEXT,
    narration_en TEXT,
    render_kr    TEXT,                    -- 한국어 자막/음성 최종 mp4
    render_en    TEXT,                    -- 영어 자막/음성 최종 mp4
    youtube_kr   TEXT,
    youtube_en   TEXT,
    publish_date TEXT,
    views        INTEGER DEFAULT 0,
    reverse_spec TEXT,                    -- 연출 역공학 명세 (JSON/Text)
    style_profile TEXT,                   -- 디자인 스타일 프로필 (JSON/Name)
    notes        TEXT,
    created_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scenes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    episode     TEXT NOT NULL REFERENCES episodes(code) ON DELETE CASCADE,
    seq         INTEGER NOT NULL,
    script_kr   TEXT,                     -- 이 컷의 나레이션(한)
    script_en   TEXT,                     -- 이 컷의 나레이션(영)
    image_prompt TEXT,                    -- 언어 중립 이미지 프롬프트(영문)
    veo_prompt  TEXT,                     -- 언어 중립 모션 프롬프트(영문)
    sfx         TEXT,
    duration_sec REAL,
    UNIQUE(episode, seq)
);

CREATE TABLE IF NOT EXISTS techniques (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT UNIQUE NOT NULL,
    description     TEXT,
    reference_url   TEXT,
    python_template TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS episode_techniques (
    episode_code TEXT REFERENCES episodes(code) ON DELETE CASCADE,
    technique_id INTEGER REFERENCES techniques(id) ON DELETE CASCADE,
    PRIMARY KEY (episode_code, technique_id)
);

CREATE TABLE IF NOT EXISTS assets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name_kr     TEXT NOT NULL,
    name_en     TEXT NOT NULL,
    type        TEXT NOT NULL, -- 'character', 'object', 'animal', 'bgm', 'sfx', 'background'
    file_path   TEXT,
    flow_prompt TEXT,
    embedding   TEXT,          -- SQLite 임베딩 (텍스트/JSON으로만 저장)
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scene_objects (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    episode    TEXT NOT NULL,
    scene_seq  INTEGER NOT NULL,
    asset_id   INTEGER REFERENCES assets(id) ON DELETE SET NULL,
    cx         INTEGER NOT NULL,
    cy         INTEGER NOT NULL,
    scale      REAL DEFAULT 1.0,
    z_order    INTEGER DEFAULT 3,
    is_point   BOOLEAN DEFAULT 0,
    motion_type TEXT,
    FOREIGN KEY(episode, scene_seq) REFERENCES scenes(episode, seq) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scene_transitions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    episode             TEXT NOT NULL REFERENCES episodes(code) ON DELETE CASCADE,
    from_scene_seq      INTEGER NOT NULL,
    to_scene_seq        INTEGER NOT NULL,
    transition_type     TEXT NOT NULL,
    exported_frame_path TEXT,
    created_at          TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS web_lessons (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    episode_code   TEXT UNIQUE NOT NULL REFERENCES episodes(code) ON DELETE CASCADE,
    quiz_question  TEXT,
    quiz_options   TEXT,
    quiz_answer    TEXT,
    dig_deeper_doc TEXT
);

CREATE TABLE IF NOT EXISTS channel_meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

-- 영상 제작 트래커: 용량 큰 영상 바이너리는 DB에 넣지 않는다.
-- 영상은 로컬(또는 나중에 유튜브)에 두고, DB에는 '이름 + 링크(경로/URL) + 모든 제작정보'만 연결 저장.
CREATE TABLE IF NOT EXISTS video_projects (
    name        TEXT PRIMARY KEY,        -- 예: 'pianoduo'
    title_kr    TEXT,
    description TEXT,
    local_dir   TEXT,                    -- 클립/최종본이 있는 로컬 폴더(링크)
    final_path  TEXT,                    -- 최종 컴파일 mp4 로컬 경로(링크, 바이너리 아님)
    youtube_url TEXT,                    -- 나중에 유튜브 업로드 시 URL
    drive_url   TEXT,                    -- 구글 드라이브 링크(있으면)
    bgm_path    TEXT,
    n_scenes    INTEGER,
    runtime_sec REAL,
    status      TEXT DEFAULT 'generating', -- generating / compiled / review / published
    notes       TEXT,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS video_clips (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project       TEXT NOT NULL REFERENCES video_projects(name) ON DELETE CASCADE,
    scene_no      INTEGER NOT NULL,
    scene_name    TEXT,                  -- 영상(클립) 이름 = 항상 연결 저장
    chunk         INTEGER,               -- 청크 번호(빠른전환 경계 그룹)
    ref_anchor    TEXT,                  -- piano_stand/back/front/side 또는 PREV
    base_image    TEXT,                  -- 사용한 기본/이전프레임 이미지 경로(링크)
    image_prompt  TEXT,
    motion_prompt TEXT,
    transition_in TEXT,                  -- 'fast'(청크경계) / 'last_frame'(청크내부)
    duration_sec  REAL,
    file_path     TEXT,                  -- 클립 mp4 로컬 경로(링크, 바이너리 저장 안 함)
    youtube_url   TEXT,                  -- 개별 공개 시 URL(옵션)
    last_frame_path TEXT,                -- 마지막 프레임 png(다음 씬 연장용)
    status        TEXT,                  -- success / fail / needs_redo
    distortion_check TEXT,               -- ok / distorted / facing / hands_off / redo
    notes         TEXT,
    created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project, scene_no)
);
"""

CATEGORIES = [
    # code, name_kr, name_en, medical_lens, priority
    ("CA",  "상상력 해부학", "Comic Anatomy",
     "만화·영화 캐릭터를 성장판·골강도·근건·역학으로 해부", 1),
    ("MD",  "닥터 제이의 시선", "World Through MD's Eyes",
     "역사·예술·사회 현상을 정렬·하중·병리의 눈으로 재해석", 1),
    ("IMP", "절대 불가능·영원한 난제", "The Impossible & The Unsolvable",
     "물리/수학/철학 난제에 항상성·진단 불확실성 등 의학 다리 연결", 1),
    ("LM",  "라이프 메카닉스", "Life Mechanics",
     "바이크·파크골프·걷기로 풀어내는 균형·체중이동·자율신경", 2),
    ("GEN", "3대가 함께 보는 계몽 노트", "Enlightenment for All",
     "신경가소성·영양·회복으로 세대 공감과 건강을 잇기", 2),
]

# code, category, title_kr, title_en, hook_kr, logline_kr, priority, status
EPISODES = [
    # --- MD: 이미 제작된 1편 ---
    ("MD-000", "MD", "메스머와 최면술의 탄생", "Mesmer and the Birth of Hypnosis",
     "회중시계가 흔들리면 정말 마음이 움직일까?",
     "암시·자율신경 반응으로 본 최면의 의학사 (회중시계 오프닝)", 1, "published"),

    # --- CA: 상상력 해부학 (최강 해자) ---
    ("CA-001", "CA", "피터팬은 왜 늙지 않을까?", "Why Doesn't Peter Pan Age?",
     "영원히 어린아이인 피터팬, 그의 성장판은 어떻게 되어 있을까?",
     "성장판 폐쇄와 성장호르몬으로 본 '영원한 어린이'의 불가능", 1, "idea"),
    ("CA-002", "CA", "진격의 거인이 실존한다면?", "If Titans Were Real",
     "50m 거인은 한 걸음 떼는 순간 제 뼈에 으스러진다?",
     "제곱-세제곱 법칙과 골강도 한계 (스케일의 저주)", 1, "idea"),
    ("CA-003", "CA", "아이언맨 슈트를 입으면 척추는 무사할까?", "Would Iron Man's Spine Survive?",
     "초음속으로 날아오를 때, 슈트 속 사람의 척추에 무슨 일이?",
     "G포스·추간판 압박·충격흡수의 역학", 1, "idea"),
    ("CA-004", "CA", "헐크처럼 근육이 폭발하면 힘줄은 버틸까?", "Could Tendons Survive the Hulk?",
     "근육이 10배 커지면 가장 먼저 찢어지는 곳은?",
     "건·인대 인장강도와 근력의 불균형", 2, "idea"),
    ("CA-005", "CA", "스파이더맨처럼 벽을 오르려면?", "What It Takes to Climb Like Spider-Man",
     "사람이 손끝으로 벽에 붙으려면 몸이 어떻게 바뀌어야 할까?",
     "체중 대비 접착력·관절 부하의 생체역학", 2, "idea"),

    # --- MD: 닥터 제이의 시선 ---
    ("MD-001", "MD", "나폴레옹의 손은 왜 늘 옷 속에 있었나", "Why Napoleon Hid His Hand",
     "초상화 속 그 손, 멋인가 병의 흔적인가?",
     "역사 인물의 자세·습관에서 읽는 숨은 질병", 1, "idea"),
    ("MD-002", "MD", "도시도 척추측만증에 걸린다", "Cities Get Scoliosis Too",
     "꼬불꼬불 잘못 깔린 도로망과 휜 척추는 같은 병을 앓는다?",
     "정렬·하중분산 원리의 도시-인체 평행이론", 2, "idea"),
    ("MD-003", "MD", "스마트폰과 거북목, 인류의 다음 진화?", "Text Neck: A New Human Spine?",
     "고개 숙인 현대인의 목, 진화일까 퇴화일까?",
     "경추 전만 소실과 하중 증가의 미래", 1, "idea"),
    ("MD-004", "MD", "명화 속 자세가 말해주는 그 시대의 병", "Disease Hidden in Masterpieces",
     "거장이 그린 인물의 비틀린 자세, 우연이 아니다?",
     "미술 속 자세 진단학(고병리)", 2, "idea"),

    # --- IMP: 절대 불가능·영원한 난제 (조회수 치트키) ---
    ("IMP-001", "IMP", "공짜 에너지가 불가능한 이유", "Why Free Energy Is Impossible",
     "넣지 않아도 영원히 도는 바퀴, 왜 한 번도 성공 못 했나?",
     "열역학 제2법칙 ↔ 인체 항상성·대사의 비유", 1, "idea"),
    ("IMP-002", "IMP", "빛보다 빠를 수 없는 이유", "Why Nothing Can Outrun Light",
     "시속 300km 바이크와 광속은 왜 차원이 다른 이야기일까?",
     "상대성 질량 증가 ↔ 신경전달 속도 비유", 1, "idea"),
    ("IMP-003", "IMP", "할아버지 역설, 시간여행과 인과율", "The Grandfather Paradox",
     "과거로 가 할아버지를 막으면 지금의 나는?",
     "인과율과 기억의 의학적 비유", 2, "idea"),
    ("IMP-004", "IMP", "괴델의 불완전성, AI도 못 푸는 문제", "Godel's Incompleteness",
     "아무리 똑똑한 AI도 절대 못 푸는 수학 문제가 있다?",
     "'참이나 증명 불가' ↔ 진단의 본질적 불확실성", 2, "idea"),
    ("IMP-005", "IMP", "튜링 정지문제, 완벽한 백신은 불가능", "Turing's Halting Problem",
     "무한루프를 미리 알려주는 완벽한 프로그램은 왜 못 만드나?",
     "정지 문제 ↔ 만성통증 악순환의 비유", 3, "idea"),
    ("IMP-006", "IMP", "트롤리 딜레마와 자율주행", "The Trolley Problem & Self-Driving Cars",
     "5명을 살릴까 1명을 살릴까, 답이 없는 문제를 기계가 푼다?",
     "의사의 생명윤리 관점에서 본 알고리즘의 벽", 1, "idea"),

    # --- LM: 라이프 메카닉스 ---
    ("LM-001", "LM", "바이크의 바람을 뇌는 왜 '치유'로 느낄까", "Why the Wind Feels Like Healing",
     "달릴 때의 그 해방감, 뇌 속에선 무슨 일이?",
     "자율신경·도파민·전정감각의 치유 메커니즘", 2, "idea"),
    ("LM-002", "LM", "파크골프 18홀과 인생의 사계절", "18 Holes and Four Seasons of Life",
     "한 라운드를 도는 동안 우리는 인생을 한 번 산다?",
     "균형·체중이동에 담긴 삶의 리듬", 3, "idea"),
    ("LM-003", "LM", "인간이 두 발로 선 날, 역사가 바뀐 이유", "The Day We Stood Upright",
     "직립보행 한 번이 인류의 운명을 바꿨다?",
     "척추 S커브와 직립의 인류학", 2, "idea"),
    ("LM-004", "LM", "하루 8천보, 무릎은 정말 닳을까?", "Do 8,000 Steps Wear Out Your Knees?",
     "많이 걸으면 무릎이 닳는다는 말, 사실일까?",
     "연골 영양·관절 부하의 과학 (TED-Ed '1만보' 정면 대결)", 1, "idea"),

    # --- GEN: 3대 세대 공감 ---
    ("GEN-001", "GEN", "5살 손주의 뇌와 60대 할아버지의 뇌가 만날 때", "When Two Brains, 60 Years Apart, Meet",
     "어린 뇌와 나이 든 뇌가 대화하면 어떤 기적이 일어날까?",
     "신경가소성과 시냅스로 본 세대 간 학습", 2, "idea"),
    ("GEN-002", "GEN", "뼈와 관절을 살리는 밥상", "The Dinner-Table Orthopedist",
     "오늘 식탁이 10년 뒤 내 무릎을 결정한다?",
     "칼슘·비타민D·단백질의 정형외과", 2, "idea"),
    ("GEN-003", "GEN", "나이 듦은 퇴화가 아니라 완숙기다", "Aging Is Ripening, Not Decline",
     "늙는다는 건 정말 무너지는 걸까?",
     "노화를 적응·완숙으로 재정의", 3, "idea"),
    ("GEN-004", "GEN", "잠은 왜 최고의 명약인가", "Why Sleep Is the Best Medicine",
     "밤사이 우리 몸은 어떤 수리를 할까?",
     "수면 중 회복·성장호르몬·조직 재생", 2, "idea"),
]


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---- 영상 제작 기록 API (다른 스크립트에서 import 해서 사용) ----------------

def upsert_project(name, **fields):
    """video_projects 행을 생성/갱신. 영상 바이너리는 저장하지 않고 경로/URL만 링크."""
    conn = connect()
    conn.executescript(SCHEMA)
    cols = ["title_kr", "description", "local_dir", "final_path", "youtube_url",
            "drive_url", "bgm_path", "n_scenes", "runtime_sec", "status", "notes"]
    data = {k: fields[k] for k in cols if k in fields}
    conn.execute("INSERT OR IGNORE INTO video_projects(name) VALUES (?)", (name,))
    if data:
        sets = ", ".join(f"{k}=?" for k in data) + ", updated_at=CURRENT_TIMESTAMP"
        conn.execute(f"UPDATE video_projects SET {sets} WHERE name=?",
                     (*data.values(), name))
    conn.commit()
    conn.close()


def log_clip(project, scene_no, **fields):
    """씬 클립 1개의 모든 제작정보를 DB에 upsert. file_path/youtube_url 은 링크만 저장."""
    conn = connect()
    conn.executescript(SCHEMA)
    conn.execute("INSERT OR IGNORE INTO video_projects(name) VALUES (?)", (project,))
    cols = ["scene_name", "chunk", "ref_anchor", "base_image", "image_prompt",
            "motion_prompt", "transition_in", "duration_sec", "file_path",
            "youtube_url", "last_frame_path", "status", "distortion_check", "notes"]
    data = {k: fields[k] for k in cols if k in fields}
    row = conn.execute(
        "SELECT id FROM video_clips WHERE project=? AND scene_no=?",
        (project, scene_no)).fetchone()
    if row:
        if data:
            sets = ", ".join(f"{k}=?" for k in data) + ", updated_at=CURRENT_TIMESTAMP"
            conn.execute(f"UPDATE video_clips SET {sets} WHERE id=?",
                         (*data.values(), row[0]))
    else:
        keys = ["project", "scene_no"] + list(data.keys())
        ph = ", ".join("?" * len(keys))
        conn.execute(f"INSERT INTO video_clips({', '.join(keys)}) VALUES ({ph})",
                     (project, scene_no, *data.values()))
    conn.commit()
    conn.close()


def cmd_init(_):
    conn = connect()
    conn.executescript(SCHEMA)
    # 기존 DB 컬럼 마이그레이션 안전장치
    for col in ["reverse_spec", "style_profile"]:
        try:
            conn.execute(f"ALTER TABLE episodes ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()
    print(f"[OK] 스키마 생성 완료 -> {DB_PATH}")


def cmd_reset(_):
    conn = connect()
    for t in ("scenes", "episodes", "categories", "channel_meta"):
        conn.execute(f"DROP TABLE IF EXISTS {t}")
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print("[OK] 전체 재생성 완료 (DROP -> CREATE)")


def cmd_seed(_):
    conn = connect()
    conn.executescript(SCHEMA)
    cur = conn.cursor()
    cur.executemany(
        "INSERT OR IGNORE INTO categories(code,name_kr,name_en,medical_lens,priority) "
        "VALUES (?,?,?,?,?)", CATEGORIES)
    cur.executemany(
        "INSERT OR IGNORE INTO episodes"
        "(code,category,title_kr,title_en,hook_kr,logline_kr,priority,status) "
        "VALUES (?,?,?,?,?,?,?,?)", EPISODES)
    meta = [
        ("channel_handle", "drjay-ed"),
        ("domain", "drjayed.com"),
        ("youtube_handle", "@drjay-ed"),
        ("concept", "의사의 메스로 세상을 해부하고, 만화가의 상상력으로 꿰매다."),
        ("languages", "kr,en"),
        ("benchmark", "TED-Ed"),
    ]
    cur.executemany(
        "INSERT OR REPLACE INTO channel_meta(key,value) VALUES (?,?)", meta)
    conn.commit()
    c_cat = cur.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    c_ep = cur.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
    conn.close()
    print(f"[OK] 시드 완료: 카테고리 {c_cat}개, 에피소드 {c_ep}개 (이중언어 KR/EN)")


def cmd_stats(_):
    conn = connect()
    cur = conn.cursor()
    total = cur.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
    print(f"\n=== drjay-ed 콘텐츠 현황 (총 {total}편) ===")
    print("\n[ 상태별 ]")
    rows = cur.execute(
        "SELECT status, COUNT(*) FROM episodes GROUP BY status").fetchall()
    order = {s: i for i, s in enumerate(STATUS_FLOW)}
    for st, n in sorted(rows, key=lambda r: order.get(r[0], 99)):
        print(f"  {st:14s} {n:2d}편")
    print("\n[ 카테고리별 ]")
    rows = cur.execute(
        "SELECT c.code, c.name_kr, COUNT(e.code) "
        "FROM categories c LEFT JOIN episodes e ON e.category=c.code "
        "GROUP BY c.code ORDER BY c.priority, c.code").fetchall()
    for code, name, n in rows:
        print(f"  {code:4s} {name:16s} {n:2d}편")
    print("\n[ 우선순위 1 (다음 제작 후보) ]")
    rows = cur.execute(
        "SELECT code, title_kr FROM episodes "
        "WHERE priority=1 AND status='idea' ORDER BY code").fetchall()
    for code, title in rows:
        print(f"  {code}  {title}")
    conn.close()
    print()


def cmd_list(args):
    conn = connect()
    q = "SELECT code, category, status, priority, title_kr, title_en FROM episodes WHERE 1=1"
    params = []
    if args.status:
        q += " AND status=?"; params.append(args.status)
    if args.category:
        q += " AND category=?"; params.append(args.category)
    if args.priority:
        q += " AND priority=?"; params.append(args.priority)
    q += " ORDER BY priority, code"
    rows = conn.execute(q, params).fetchall()
    print(f"\n{'CODE':9s} {'CAT':4s} {'STATUS':12s} P  TITLE")
    print("-" * 72)
    for code, cat, status, pr, t_kr, t_en in rows:
        print(f"{code:9s} {cat:4s} {status:12s} {pr}  {t_kr}")
    print(f"\n총 {len(rows)}편\n")
    conn.close()


def cmd_show(args):
    conn = connect()
    row = conn.execute("SELECT * FROM episodes WHERE code=?",
                       (args.code,)).fetchone()
    if not row:
        print(f"[!] 에피소드 없음: {args.code}")
        return
    cols = [d[0] for d in conn.execute(
        "SELECT * FROM episodes WHERE code=?", (args.code,)).description]
    print(f"\n=== {args.code} ===")
    for k, v in zip(cols, row):
        if v not in (None, "", 0):
            print(f"  {k:16s}: {v}")
    scenes = conn.execute(
        "SELECT seq, script_kr FROM scenes WHERE episode=? ORDER BY seq",
        (args.code,)).fetchall()
    if scenes:
        print(f"\n  -- 씬 {len(scenes)}개 --")
        for seq, sk in scenes:
            print(f"  [{seq}] {sk}")
    conn.close()
    print()


def cmd_set_status(args):
    if args.status not in STATUS_FLOW:
        print(f"[!] 잘못된 상태. 허용: {', '.join(STATUS_FLOW)}")
        return
    conn = connect()
    cur = conn.execute("UPDATE episodes SET status=? WHERE code=?",
                       (args.status, args.code))
    conn.commit()
    if cur.rowcount:
        print(f"[OK] {args.code} -> {args.status}")
    else:
        print(f"[!] 에피소드 없음: {args.code}")
    conn.close()


def cmd_projects(_):
    conn = connect()
    conn.executescript(SCHEMA)
    rows = conn.execute(
        "SELECT name, title_kr, status, n_scenes, runtime_sec, final_path, youtube_url "
        "FROM video_projects ORDER BY updated_at DESC").fetchall()
    print(f"\n{'NAME':14s} {'STATUS':12s} {'SCN':>3s} {'SEC':>6s}  LINK")
    print("-" * 78)
    for name, t, st, n, sec, fp, yt in rows:
        link = yt or fp or "-"
        print(f"{name:14s} {st or '-':12s} {n or 0:3d} {sec or 0:6.1f}  {link}")
    print(f"\n총 {len(rows)}개 프로젝트\n")
    conn.close()


def cmd_clips(args):
    conn = connect()
    conn.executescript(SCHEMA)
    q = ("SELECT scene_no, scene_name, ref_anchor, transition_in, duration_sec, "
         "status, distortion_check, file_path FROM video_clips")
    params = []
    if args.project:
        q += " WHERE project=?"; params.append(args.project)
    q += " ORDER BY project, scene_no"
    rows = conn.execute(q, params).fetchall()
    print(f"\n{'#':>3s} {'NAME':18s} {'REF':11s} {'TRANS':10s} {'SEC':>4s} "
          f"{'STATUS':8s} {'CHECK':10s} PATH")
    print("-" * 100)
    for no, nm, ref, tr, sec, st, ck, fp in rows:
        print(f"{no:3d} {nm or '-':18s} {ref or '-':11s} {tr or '-':10s} "
              f"{sec or 0:4.1f} {st or '-':8s} {ck or '-':10s} {fp or '-'}")
    print(f"\n총 {len(rows)}개 클립\n")
    conn.close()


def main():
    p = argparse.ArgumentParser(description="drjay-ed 콘텐츠 DB 매니저")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(func=cmd_init)
    sub.add_parser("reset").set_defaults(func=cmd_reset)
    sub.add_parser("seed").set_defaults(func=cmd_seed)
    sub.add_parser("stats").set_defaults(func=cmd_stats)
    lp = sub.add_parser("list")
    lp.add_argument("--status")
    lp.add_argument("--category")
    lp.add_argument("--priority", type=int)
    lp.set_defaults(func=cmd_list)
    sp = sub.add_parser("show"); sp.add_argument("code"); sp.set_defaults(func=cmd_show)
    ss = sub.add_parser("set-status")
    ss.add_argument("code"); ss.add_argument("status")
    ss.set_defaults(func=cmd_set_status)
    sub.add_parser("projects").set_defaults(func=cmd_projects)
    cl = sub.add_parser("clips"); cl.add_argument("--project")
    cl.set_defaults(func=cmd_clips)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
