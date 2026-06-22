#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""벤치마크(TED-Ed, English-class) 연출 기법 역공학 → 데이터화 → content.db 저장.
+ 우리가 제작한 콘텐츠를 기법별로 분석·태깅(적용/미적용=개선포인트).
출처: .harness/context/ted_ed_reverse_engineering.md, scratch/korean_education_deep_research.md(레퍼런스 역공학),
      도메인 지식(영어 교육 영상 explainer 문법).
사용: python channel/benchmark_db.py build   # 스키마+데이터 적재
      python channel/benchmark_db.py report  # 기법 카탈로그 + 콘텐츠 분석 출력
"""
import os, sqlite3, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
DB=os.path.join(os.path.dirname(os.path.abspath(__file__)),"content.db")

# (name, benchmark, category, description, when_to_use, our_application)
TECHNIQUES=[
# ── TED-Ed ──
("훅 질문 오프닝","ted_ed","structure","기괴·호기심 자극 예화+질문으로 도입(0~12%)","영상 도입부","졸라 프리젠터가 질문 던지고 핵심 오브젝트 줌인"),
("스토리텔링 내레이션 130-140WPM","ted_ed","audio","차분·학구적 톤, 핵심어만 강세, 130~140WPM","내레이션 속도","TTS 속도 1.0~1.1, 핵심어 강조"),
("문장 간 0.3-0.5s 휴지","ted_ed","audio","문장 사이 무음으로 비주얼이 먼저 움직일 호흡","오디오 편집","자막/씬 전환에 0.3~0.5s 갭"),
("어쿠스틱 미니멀 BGM 덕킹(-18~-22dB)","ted_ed","audio","재즈 베이스/피아노/피치카토, 내레이션 대역 비우고 -18~-22dB","BGM 믹스","MusicGen 어쿠스틱+사이드체인 덕킹"),
("디지털 컷페이퍼+소프트 드롭섀도","ted_ed","visual","종이 오린 질감 레이어+미세 그림자=평면에 깊이","아트 스타일","PIL 레이어에 soft drop shadow"),
("오프화이트/파스텔 배경·4색 이하","both","color","순백 배제, 미색/파스텔 배경 60%+, 주색 4개 이하","팔레트","make_bg 파스텔, 색 수 제한"),
("아날로그 거친 얇은 선·면대비","ted_ed","visual","외곽선 최소·연필/목탄 질감, 면 대비로 형태","라인아트","졸라 손그림 선 유지"),
("12fps 온투 캐릭터+24fps 카메라","ted_ed","motion","동작은 12fps 스톱모션 손맛, 카메라는 24fps 부드럽게","모션 리듬","오버레이 동작 12fps 스텝(snap), 카메라 무빙 부드럽게"),
("모핑 트랜지션(오브젝트 변형)","ted_ed","motion","중앙 오브젝트가 다음 맥락으로 유기적 변형 — TED-Ed 시그니처","씬 전환","레이어 모프/형태 전환으로 컷 대체"),
("연속 패럴럭스 패닝","ted_ed","motion","카메라 끊임없이 이동+전경/배경 속도차로 입체감","장면 연결","다층 레이어 속도차 스크롤"),
("정밀 폴리 SFX 0.1s 싱크","ted_ed","sfx","모션에 0.1s 단위 장난기 효과음(툭/착/팅)","사운드","동작 키프레임에 SFX 배치"),
("사운드 원근(롱샷 리버브)","ted_ed","sfx","근경 크게, 롱샷은 리버브로 작게","사운드 믹스","샷 스케일별 SFX 볼륨/리버브"),
("자막: 박스없음·얇은스트로크·넓은마진·구절줄바꿈","ted_ed","typography","검은박스 금지, 테두리/소프트섀도, 하단 마진 큼, 구·절 단위 줄바꿈","자막","MoviePy TextClip 템플릿(create_ted_subtitle)"),
("스토리 아크 12/85/100","ted_ed","structure","훅0-12% → 본론(시간/인과순)12-85% → 통찰 아웃트로85-100%","전체 구성","씬 타임라인 비율 설계"),
# ── English-class (explainer) ──
("미니멀 라인아트(오프화이트 #F5F5F0)","english_class","visual","단색 미색 배경+단순 검은 외곽선, 음영 배제","아트 스타일","졸라/오브젝트 플랫 PNG 그대로"),
("포인트 컬러 스포트라이트(#FFD700)","english_class","highlight","핵심 부분만 파스텔 노랑으로 강조","핵심 강조","콜아웃 요소에 노랑 글로우(make_final GLOW)"),
("부드러운 Pan&Zoom·디테일 줌인","english_class","motion","툭 끊김 없이 줌인/팬, 전체→디테일로 이동","전환/강조","프로그램 줌/팬, 디테일 클로즈업"),
("획순 펜 따라 카메라 패닝","english_class","motion","쓰기 1획→2획 펜끝 따라 화면 흐름","쓰기 교육","create_extreme_close_up_writing_clip"),
("단어/문장 타이포 콜아웃(타이핑·팝)","english_class","typography","핵심 단어가 타이핑되듯/팝업, 색·크기 강조","단어 제시","글자 애니(자모 조립 엔진 응용)"),
("하이라이트 문법(밑줄·동그라미·체크·화살표·번호배지)","english_class","highlight","밑줄·원·✓·화살표·①②③로 단계·강조","강조/단계","whiteboard_animator: underline/checkmark/badge"),
("단어-이미지 연상+반복","english_class","pedagogy","단어+그림 연결, 반복 노출로 각인","어휘 교육","오브젝트 PNG+단어 동시 노출"),
("프리젠터 포인팅·반응","english_class","presenter","캐릭터가 가리키고 반응(끄덕·박수·놀람)","진행/주의환기","졸라 포즈 PNG 교체로 연기"),
("예문 단어별 빌드업+색코딩","english_class","pedagogy","문장 단어 하나씩 등장+품사/요소 색 구분","문법 설명","타이포 시퀀스+색코딩"),
("많은 짧은 컷+빠른 페이싱","english_class","pacing","컷 수 많이, 빠른 호흡으로 몰입 유지","편집","씬 다수·짧게(3~5s)"),
("퀴즈/체크 모먼트","english_class","pedagogy","✓ 퀴즈로 참여·복습 유도","복습/참여","체크마크 클립+퀴즈 텍스트"),
]

# 우리 제작 콘텐츠 분석: (project, technique_name, applied, notes)
ANALYSIS=[
("zolla_dynamite","미니멀 라인아트(오프화이트 #F5F5F0)",1,"졸라 플랫 라인아트"),
("zolla_dynamite","오프화이트/파스텔 배경·4색 이하",1,"파스텔(중앙 흰+분홍·파랑)"),
("zolla_dynamite","포인트 컬러 스포트라이트(#FFD700)",1,"ㄴ 줍기 노란 글로우"),
("zolla_dynamite","단어/문장 타이포 콜아웃(타이핑·팝)",1,"자모 비정형 조립(힙합맨/힙합걸)"),
("zolla_dynamite","프리젠터 포인팅·반응",1,"졸라 듀오 모션캡처 댄스(50% 배경)"),
("zolla_dynamite","많은 짧은 컷+빠른 페이싱",0,"현재 단일 롱컷 — 컷 분할 필요"),
("zolla_dynamite","스토리텔링 내레이션 130-140WPM",0,"내레이션 없음 — 추가 시 교육성↑"),
("zolla_dynamite","모핑 트랜지션(오브젝트 변형)",0,"미적용 — 자모↔이미지 모프 도입 여지"),
("zolla_dynamite","자막: 박스없음·얇은스트로크·넓은마진·구절줄바꿈",0,"자막 없음"),
("korean_education","미니멀 라인아트(오프화이트 #F5F5F0)",1,"한글 라인아트"),
("korean_education","획순 펜 따라 카메라 패닝",1,"쓰기 획순 연출"),
("korean_education","단어/문장 타이포 콜아웃(타이핑·팝)",1,"자모 조립"),
("korean_education","스토리텔링 내레이션 130-140WPM",1,"이중언어 내레이션(KR/EN)"),
("korean_education","모핑 트랜지션(오브젝트 변형)",0,"미적용"),
("korean_education","정밀 폴리 SFX 0.1s 싱크",0,"보강 여지"),
("pianoduo","어쿠스틱 미니멀 BGM 덕킹(-18~-22dB)",1,"피아노 BGM 아크(음악 영상)"),
("pianoduo","12fps 온투 캐릭터+24fps 카메라",1,"Veo 모션 클립(지미집 카메라)"),
("pianoduo","스토리텔링 내레이션 130-140WPM",0,"내레이션 없음(연주 영상)"),
("pet_family","스토리텔링 내레이션 130-140WPM",1,"다큐 내레이션"),
("pet_family","훅 질문 오프닝",0,"강화 여지"),
]

def conn():
    c=sqlite3.connect(DB); c.execute("PRAGMA foreign_keys=ON"); return c

def build(_=None):
    c=conn(); cur=c.cursor()
    for col in ("benchmark","category","when_to_use","our_application"):
        try: cur.execute(f"ALTER TABLE techniques ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError: pass
    cur.execute("""CREATE TABLE IF NOT EXISTS project_techniques(
        project TEXT NOT NULL, technique TEXT NOT NULL, applied INTEGER DEFAULT 0,
        notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(project,technique))""")
    cur.execute("DELETE FROM techniques")  # 기존 깨진 1행 정리 후 재적재
    for n,b,cat,d,w,o in TECHNIQUES:
        cur.execute("""INSERT INTO techniques(name,benchmark,category,description,when_to_use,our_application)
            VALUES(?,?,?,?,?,?)""",(n,b,cat,d,w,o))
    for p,t,ap,nt in ANALYSIS:
        cur.execute("INSERT OR REPLACE INTO project_techniques(project,technique,applied,notes) VALUES(?,?,?,?)",(p,t,ap,nt))
    c.commit()
    nt=cur.execute("SELECT COUNT(*) FROM techniques").fetchone()[0]
    na=cur.execute("SELECT COUNT(*) FROM project_techniques").fetchone()[0]
    c.close(); print(f"[OK] 기법 {nt}개, 콘텐츠 분석 {na}건 저장 → content.db")

def report(_=None):
    c=conn(); cur=c.cursor()
    print("\n===== 벤치마크 연출 기법 카탈로그 =====")
    for bm in ("ted_ed","english_class","both"):
        rows=cur.execute("SELECT category,name,description FROM techniques WHERE benchmark=? ORDER BY category",(bm,)).fetchall()
        if not rows: continue
        print(f"\n■ {bm} ({len(rows)})")
        for cat,n,d in rows: print(f"  [{cat:10s}] {n}\n        ↳ {d}")
    print("\n===== 우리 콘텐츠 기법 분석 =====")
    projs=[r[0] for r in cur.execute("SELECT DISTINCT project FROM project_techniques").fetchall()]
    for p in projs:
        ap=cur.execute("SELECT technique,notes FROM project_techniques WHERE project=? AND applied=1",(p,)).fetchall()
        gp=cur.execute("SELECT technique,notes FROM project_techniques WHERE project=? AND applied=0",(p,)).fetchall()
        print(f"\n● {p}  (적용 {len(ap)} / 개선 {len(gp)})")
        for t,nt in ap: print(f"   ✔ {t} — {nt}")
        for t,nt in gp: print(f"   ✗(보강) {t} — {nt}")
    c.close(); print()

if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "build"
    {"build":build,"report":report}.get(cmd,build)(None)
