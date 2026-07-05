# -*- coding: utf-8 -*-
"""최면 영상 제목·설명(한/영) → content.db video_localizations + loc_*.txt (업로드 준비용).
video_id는 업로드 전이라 임시(hypnosis_pending), 업로드 후 실제 ID로 갱신."""
import os, sqlite3
ROOT = "D:/Entertainments/DevEnvironment/autovideo"; HS = os.path.join(ROOT, "hypnosis_science")
DB = os.path.join(ROOT, "channel", "content.db"); DATE = "2026-07-03"
PROJECT = "hypnosis_science"; VID = "hypnosis_pending"

LOC = {
"ko": {
"title": "최면, 과학일까 사기일까? | 메스머의 사기극부터 뇌과학까지 (플라시보·통증)",
"desc": """최면은 정말 우리 뇌와 몸에 효과가 있는 과학일까요? 18세기 메스머의 '동물 자기' 사기극부터, 벤자민 프랭클린의 세계 최초 맹검 실험, 그리고 fMRI로 밝혀낸 통증 완화의 뇌과학까지 — 다정한 의사의 시선으로 최면의 진실을 알기 쉽게 풀어드립니다. Dr.Jay-ed 교육 채널.

📖 챕터
0:00 최면, 마술일까 과학일까?
0:14 메스머와 '동물 자기'
0:36 프랭클린의 맹검 실험
1:01 플라시보 효과의 탄생
1:10 브레이드, 최면을 재정의하다
1:27 fMRI로 들여다본 최면의 뇌
1:45 무마취 수술과 의료 활용

🌐 한국어·English 나레이션과 자막을 지원합니다. (오디오·자막 트랙에서 선택)

⚠️ 본 영상의 시각 자료 중 일부는 Google Veo 및 Flow AI 기술을 활용하여 생성 및 연출되었습니다.
※ 본 영상은 일반적인 교육·정보 제공용이며, 개별 의학적 진단·처방을 대체하지 않습니다.

#최면 #최면과학 #플라시보 #뇌과학 #심리학 #Hypnosis #DrJayEd #건강상식""",
},
"en": {
"title": "Is Hypnosis Science or a Scam? | From Mesmer's Fraud to Brain Science (Placebo · Pain)",
"desc": """Is hypnosis really a science that affects our brain and body? From the 'animal magnetism' fraud of 18th-century Mesmer, to Benjamin Franklin's first-ever blind experiment, to the brain science of pain relief revealed by fMRI — a friendly doctor unpacks the truth about hypnosis in plain terms. Dr.Jay-ed educational channel.

📖 Chapters
0:00 Hypnosis: magic or science?
0:14 Mesmer and 'animal magnetism'
0:36 Franklin's blind experiment
1:01 The birth of the placebo effect
1:10 Braid redefines hypnosis
1:27 The hypnotized brain under fMRI
1:45 Anesthesia-free surgery & medical use

🌐 Korean & English narration and subtitles are available. (Choose from the audio / subtitle tracks)

⚠️ Some of the visuals in this video were generated and directed using Google Veo and Flow AI technology.
※ This video is for general educational and informational purposes only and is not a substitute for individual medical diagnosis or treatment.

#Hypnosis #HypnosisScience #Placebo #Neuroscience #Psychology #BrainScience #DrJayEd""",
},
}

c = sqlite3.connect(DB); cur = c.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS video_localizations(
  id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT, video_id TEXT, lang TEXT,
  title TEXT, description TEXT, updated_at TEXT, UNIQUE(video_id, lang))""")
for lang, m in LOC.items():
    open(os.path.join(HS, f"loc_{lang}.txt"), "w", encoding="utf-8").write(
        f"[제목 / TITLE] ({len(m['title'])}자)\n{m['title']}\n\n[설명 / DESCRIPTION]\n{m['desc']}\n")
    cur.execute("""INSERT INTO video_localizations(project,video_id,lang,title,description,updated_at)
      VALUES(?,?,?,?,?,?) ON CONFLICT(video_id,lang) DO UPDATE SET
      title=excluded.title,description=excluded.description,updated_at=excluded.updated_at""",
      (PROJECT, VID, lang, m["title"], m["desc"], DATE))
    print(f"{lang}: 제목 {len(m['title'])}자 → DB + loc_{lang}.txt")
c.commit(); c.close(); print("DONE")
