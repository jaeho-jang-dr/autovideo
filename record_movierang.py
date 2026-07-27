# -*- coding: utf-8 -*-
"""★무비랑(MovieRang) — 통합 영상 생성 엔진을 DB에 등록한다 (사장님 지시 2026-07-27).

W22에서 처음으로 6개 기술이 하나의 타임라인에 물려 돌아갔다. 그 성과를
**앱 이름(무비랑) · 에이전트 이름**으로 content.db에 남겨, 다음 회차와 다른 에이전트
(유튜브랑·컷랑·글씨랑·캐릭터랑)가 같은 기록을 보고 이어서 만들 수 있게 한다.

기록 위치(기존 테이블 재사용 — 새 테이블 만들지 않음):
  engine_recipes      : 무비랑 엔진 1행 (요약·단계·스크립트·기술스택)
  techniques          : 6개 돌파 기술 (category='movierang')
  project_techniques  : 무비랑 ↔ 기술, hangeul_w22_travel ↔ 기술 연결
  video_projects      : W22 프로젝트 행(무비랑으로 제작했다는 표시)

사용: python record_movierang.py        (몇 번 돌려도 같은 상태 — 갱신형)
"""
import os, sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")
APP = "무비랑(MovieRang)"
W22 = "hangeul_w22_travel"

# ── 6개 돌파 기술 (W22에서 처음 통합) ────────────────────────────────
TECHS = [
    ("컷랑 동작 컷아웃 애니메이션",
     "Flow/Veo로 만든 8초 동작 영상을 프레임 분해→'밝고 무채색=배경' 투명 컷아웃→기준 캐릭터와 "
     "몸높이 통일(자세별 pose-floor)→DB 포즈 시퀀스로 등록. 재생은 비트 구간 동안 처음~끝 1회(oneshot).",
     "캐릭터가 실제로 '연기'해야 하는 씬(가리키기·팔벌리기·회상·돋보기)",
     "cutrang.py dump/build --pose-floor → anim_char_poses(char_key,pose_name) → "
     "build_wXX MOTION_ACTS → compile_stickman.seq_state() oneshot 분기"),

    ("배경 동영상 + 정지 스틸 하이브리드",
     "배경을 전 씬 영상으로 깔지 않는다. 지정한 소수 씬만 동영상(각 1회)이고 나머지는 그 영상이 멈춘 "
     "정지 스틸. 영상은 길이를 넘기면 마지막 프레임에서 자동 정지(freeze)해 씬 길이에 안전하게 맞는다.",
     "도입·전환처럼 공간감이 필요한 씬만 살리고, 설명 씬은 정적으로 두어 글자·캐릭터에 시선을 모을 때",
     "build_wXX VIDEO_SCENES/BGVID → scenes.image_prompt의 bg/bg_video → "
     "compile_stickman.bg_video_frame(freeze+커버+하단 스크림)"),

    ("파라메트릭 한글 드로잉 좌우 가변 배치",
     "화면에 쓰는 한글을 이미지가 아니라 폰트에서 파라메트릭으로 그린다. 키워드 줄 수·최대 폭에 맞춰 "
     "글자 크기(scale)와 블록 크기를 계산하고, 그 블록을 좌/우 어느 쪽에 놓을지 씬마다 다르게 정한다.",
     "씬마다 핵심 한글을 크게 노출하되 매번 같은 자리에 박히지 않게 할 때",
     "build_wXX keyword_layout() → scene_objects(motion='write', cx=write_cx, scale) → "
     "compile_stickman 'write' 모션(획순 드로잉)"),

    ("캐릭터–글자 상호 배치(빈 쪽에 서기)",
     "글자 위치를 먼저 정하고 캐릭터를 끼워 넣는 게 아니라, 그 씬에서 캐릭터가 **가장 오래 말하는 지점**을 "
     "구한 뒤 그 반대편에 글자 블록을 놓는다. 걷기 비트와 화면 밖 도착점은 계산에서 뺀다 — 얼굴이 안 가린다.",
     "캐릭터가 씬마다 다른 위치에 서는데 글자와 겹치면 안 될 때(= 항상)",
     "build_wXX: _talk=걷기 아닌 비트 중 dur 최대 → stop_x → "
     "write_cx = 반대편(CANVAS_W-여백-blk_w 또는 여백)"),

    ("캐릭터 좌우 자유 이동(스트라이드 절대시간 걷기)",
     "시나리오에 Z좌표(0~100%)로 '어디서 어디로'를 적으면 픽셀로 환산해 비트의 x_from→x_to로 보간한다. "
     "걷기 사이클은 비트 길이에 비례해 늘어나지 않고 WALK_STRIDE_SEC(1스트라이드=1.08초) 절대시간으로 "
     "돌아 걸음걸이가 씬 길이와 무관하게 자연스럽다.",
     "캐릭터가 화면을 가로질러 이동하며 설명해야 할 때",
     "W22_motion.md Z표기 → build_wXX z2x()/parse_motion() → anim_sequences.beats_json → "
     "compile_stickman.seq_state() WALK_STRIDE_SEC 분기 + walk_r/walk_l 10프레임"),

    ("나레이션·자막·동작 3중 동기",
     "씬 길이를 KO/EN 나레이션 중 긴 쪽 + 여백으로 잡아 한 벌의 타임라인이 두 언어판에 다 맞는다. "
     "그 길이를 비트 가중치(걷기 0.9 / 동작 2.0 / 정지 1.0)로 나눠 동작이 배분되므로, "
     "나레이션이 길어지면 동작도 같이 늘어나 어긋나지 않는다.",
     "한 벌 렌더로 KO/EN 두 판을 뽑고 자막까지 정렬해야 할 때(=한글강의 표준)",
     "compile_np.py 씬길이=max(ko_dur,en_dur)+TAIL → timeline.json → "
     "build_wXX make_beats() 가중 배분 → compile_stickman.seq_state()"),
]

STEPS = (
    "■ 0. 시나리오(WXX_scenario.md) + 동작표(WXX_motion.md, Z좌표·동작 토큰) 작성\n"
    "■ 1. 배경: agy 나노바나나 스틸 + Flow/Veo 8초 영상(지정 씬만) → assets/graphics/bg\n"
    "■ 2. 캐릭터: 정지 포즈(agy) + 동작 영상(flow_cdp_pipeline.py CDP9222)\n"
    "■ 3. 컷랑: cutrang.py build --pose-floor → 투명컷 시퀀스 → anim_char_poses 등록\n"
    "■ 4. build_wXX.py: 시나리오·동작표 파싱 → scenes/scene_objects/anim_sequences 기록\n"
    "     (글자 블록 크기 계산 → 캐릭터 반대편 배치, 걷기 Z→픽셀 보간)\n"
    "■ 5. 렌더: final_render_wXX.py(Azure 선희/Emma) → compile_np.py 4K, SUB_LANGS=판별 1개\n"
    "■ 6. 자막: add_pron_to_srt(실제 발음 로마자) → translate_srt_wXX.py(ja/zh/es) → pack_subs.py\n"
    "■ 7. 패키지: make_wXX_package.py(제목·설명·태그·매니페스트, 챕터는 타임라인 실측)\n"
    "■ 8. 검수: precheck_wXX.py 10개 조항 전부 OK\n"
    "■ 9. 업로드: yt_upload_api_wXX.py → yt_api.py subs → playlist_add/comment\n"
    "■ 10. 노출: pin_only.py · card_video_ui.py · endscreen_video_ui.py (CDP 9222 UI)\n"
    "■ 11. 공개: yt_publish_wXX.py(4K 게이트) → 웹 임베드(LessonsView/CurriculumView) → CF Pages+Vercel"
)

SCRIPTS = ("cutrang.py, flow_cdp_pipeline.py, build_wXX.py, compile_np.py, "
           "hangeul_birth_vowels/compile_stickman.py, add_pron_to_srt.py, refresh_pron_srt.py, "
           "translate_srt_wXX.py, pack_subs.py, make_wXX_package.py, precheck_wXX.py, "
           "yt_upload_api_wXX.py, yt_api.py, pin_only.py, card_video_ui.py, endscreen_video_ui.py, "
           "yt_publish_wXX.py")

STACK = ("[생성] Google Veo·Flow(배경/동작 영상, CDP 9222 Playwright) · Google Gemini 나노바나나(agy, 스틸) | "
         "[합성] Python + MoviePy 2.2.1 + Pillow + NumPy/SciPy(ndimage 컷아웃) + ffmpeg/libx264 | "
         "[음성] Azure Speech TTS 최종(ko-KR-SunHiNeural 선희 / en-US-EmmaMultilingualNeural) · "
         "edge-tts 초안 · 발음클립 web/public/audio/jamo | "
         "[데이터] SQLite content.db(scenes·scene_objects·anim_sequences·anim_char_poses·assets) | "
         "[자막] 자체 표준발음 로마자 변환기(add_pron_to_srt) + Gemini CLI 번역(ja/zh/es) | "
         "[배포] YouTube Data API v3 + Studio UI 자동화(Playwright CDP) + Astro/Cloudflare Pages/Vercel")

NOTES = ("★W22(여행 경험·계획, 지은/하늘 전망대)에서 6개 기술이 처음으로 한 타임라인에 통합됐다. "
         "이전에는 각각 따로 굴러가 서로 어긋났다(글자가 얼굴을 가리거나, 걷기가 씬 길이에 늘어지거나, "
         "동작이 나레이션과 따로 놀거나). 무비랑은 이 6개를 '시나리오 → 비트 → 합성' 한 줄기로 묶은 "
         "이름이며, 하위 엔진 컷랑·글씨랑·캐릭터랑·유튜브랑을 오케스트레이션한다. "
         "현재는 스크립트 모음 상태 — 다음 단계는 이것을 단일 CLI(movierang.py)로 통합하는 것.")


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # 1) engine_recipes — 무비랑 엔진 1행 (있으면 갱신)
    row = cur.execute("SELECT id FROM engine_recipes WHERE name LIKE ?", (f"{APP}%",)).fetchone()
    if row:
        cur.execute("UPDATE engine_recipes SET summary=?, steps=?, scripts=?, notes=?, "
                    "updated_at=datetime('now') WHERE id=?",
                    (f"통합 영상 생성 엔진. {STACK}", STEPS, SCRIPTS, NOTES, row[0]))
        eid = row[0]
        print(f"engine_recipes 갱신 (id={eid})")
    else:
        cur.execute("INSERT INTO engine_recipes (name, summary, steps, scripts, notes, updated_at) "
                    "VALUES (?,?,?,?,?,datetime('now'))",
                    (f"{APP} — 통합 영상 생성 엔진", f"통합 영상 생성 엔진. {STACK}", STEPS, SCRIPTS, NOTES))
        eid = cur.lastrowid
        print(f"engine_recipes 신규 (id={eid})")

    # 2) techniques — 6개 (name 기준 갱신)
    tids = []
    for name, desc, when, ours in TECHS:
        r = cur.execute("SELECT id FROM techniques WHERE name=?", (name,)).fetchone()
        if r:
            cur.execute("UPDATE techniques SET description=?, category=?, when_to_use=?, "
                        "our_application=?, benchmark=? WHERE id=?",
                        (desc, "movierang", when, ours, APP, r[0]))
            tids.append(r[0])
        else:
            cur.execute("INSERT INTO techniques (name, description, category, when_to_use, "
                        "our_application, benchmark, created_at) VALUES (?,?,?,?,?,?,datetime('now'))",
                        (name, desc, "movierang", when, ours, APP))
            tids.append(cur.lastrowid)
    print(f"techniques {len(tids)}건 기록 (category=movierang)")

    # 3) project_techniques — 무비랑 ↔ 기술, W22 ↔ 기술
    cur.execute("DELETE FROM project_techniques WHERE project IN (?,?)", (APP, W22))
    for name, _, _, _ in TECHS:
        cur.execute("INSERT INTO project_techniques (project, technique, applied, notes, created_at) "
                    "VALUES (?,?,?,?,datetime('now'))",
                    (APP, name, 1, "무비랑 표준 구성요소"))
        cur.execute("INSERT INTO project_techniques (project, technique, applied, notes, created_at) "
                    "VALUES (?,?,?,?,datetime('now'))",
                    (W22, name, 1, "W22에서 최초 통합 적용 (2026-07-27)"))
    print(f"project_techniques {len(TECHS)*2}건 연결 ({APP} / {W22})")

    # 4) episode_techniques — 에피소드 코드로도 연결
    cur.execute("DELETE FROM episode_techniques WHERE episode_code=?", ("KO-W22",))
    for tid in tids:
        cur.execute("INSERT INTO episode_techniques (episode_code, technique_id) VALUES (?,?)",
                    ("KO-W22", tid))
    print(f"episode_techniques {len(tids)}건 연결 (KO-W22)")

    # 5) video_projects — W22 프로젝트 행(무비랑 제작 표시)
    vp = cur.execute("SELECT name FROM video_projects WHERE name=?", (W22,)).fetchone()
    vals = dict(
        title_kr="W22 여행 경험·미래 계획 (지은 · 하늘 전망대)",
        description="가 본 적이 있어요 / 할 계획이에요. 무비랑 6개 기술 최초 통합 회차.",
        local_dir="hangeul_birth_vowels",
        youtube_url="https://youtu.be/CZMYZUehC7k",
        n_scenes=24, runtime_sec=315, status="published",
        notes=f"제작 엔진={APP}. KO=CZMYZUehC7k / EN=XI9cmlczbkw · 4K · 5개국어 자막 · 노출4단계·임베드 완료.",
        tags="무비랑,MovieRang,컷랑,한글강의,W22,여행,경험,계획",
        np_final_path="hangeul_birth_vowels/hangeul_w22_jieun_np_ko.mp4",
        np_ko_srt="hangeul_birth_vowels/hangeul_w22_jieun_np.ko.srt",
        np_en_srt="hangeul_birth_vowels/hangeul_w22_jieun_np.en.srt",
        narr_voice_ko="Azure ko-KR-SunHiNeural (선희)",
        narr_voice_en="Azure en-US-EmmaMultilingualNeural (Emma)",
    )
    if vp:
        sets = ",".join(f"{k}=?" for k in vals) + ", updated_at=datetime('now')"
        cur.execute(f"UPDATE video_projects SET {sets} WHERE name=?", list(vals.values()) + [W22])
        print("video_projects 갱신")
    else:
        ks = ",".join(["name"] + list(vals))
        qs = ",".join("?" * (len(vals) + 1))
        cur.execute(f"INSERT INTO video_projects ({ks}, created_at, updated_at) "
                    f"VALUES ({qs}, datetime('now'), datetime('now'))", [W22] + list(vals.values()))
        print("video_projects 신규")

    con.commit()

    # 확인 출력
    print(f"\n=== {APP} 등록 확인 ===")
    for r in cur.execute("SELECT name, category, benchmark FROM techniques WHERE category='movierang' ORDER BY id"):
        print(f"  · {r[0]}")
    print(f"  engine_recipes: {cur.execute('SELECT name FROM engine_recipes WHERE id=?', (eid,)).fetchone()[0]}")
    print(f"  W22 연결 기술: {cur.execute('SELECT COUNT(*) FROM project_techniques WHERE project=?', (W22,)).fetchone()[0]}건")
    con.close()


if __name__ == "__main__":
    main()
