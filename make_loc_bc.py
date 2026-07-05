# -*- coding: utf-8 -*-
"""정주행(binge)·아이키성장(child_growth) 다국어 제목·설명(한/영) → content.db(video_localizations) + 파일."""
import os, sqlite3
ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")
DATE = "2026-07-03"

DATA = {
 "binge_watching": {"vid": "wJUAiZW5fW0", "dir": "binge_watching", "loc": {
  "ko": {
   "title": "밤샘 정주행, 내 몸의 경고 | 몰아보기의 과학 (수면·도파민·건강)",
   "desc": open(os.path.join(ROOT, "binge_watching", "yt_desc_ko.txt"), encoding="utf-8").read().strip().strip('"'),
  },
  "en": {
   "title": "Binge-Watching & Your Body's Warning | The Science of Bingeing (Sleep · Dopamine · Health)",
   "desc": """Have you ever pulled an all-nighter thinking "just one more episode…"? A friendly doctor breaks down what binge-watching actually does to your brain and body, in plain terms.
From dopamine addiction to muscles, joints, sleep and appetite — plus how to enjoy it healthily. Dr.Jay-ed educational channel.

📖 Chapters
0:00 Another binge tonight?
0:47 Does it really harm your health?
1:36 Dopamine and the brain's temptation
2:26 Leg muscles that stop moving
3:40 Stiffening joints
4:55 Blue light and disrupted sleep
6:07 The runaway appetite hormones
7:22 How to enjoy it healthily

🌐 Korean & English narration and subtitles are available. (Choose from the audio / subtitle tracks)

⚠️ Some of the visuals in this video were generated and directed using Google Veo and Flow AI technology.
※ This video is for general educational and informational purposes only and is not a substitute for individual medical diagnosis or treatment.

#BingeWatching #Netflix #SleepHealth #Dopamine #HealthTips #Wellness #DrJayEd""",
  },
 }},
 "child_growth": {"vid": "Mo1AIPoLjhU", "dir": "child_growth_science", "loc": {
  "ko": {
   "title": "우리 아이 키 얼마나 클까? | 소아 성장·키 크는 과학 (부모 필독)",
   "desc": open(os.path.join(ROOT, "child_growth_science", "yt_desc_ko.txt"), encoding="utf-8").read().strip().strip('"'),
  },
  "en": {
   "title": "How Tall Will My Child Grow? | The Science of Child Growth & Height (A Must for Parents)",
   "desc": """Just how many centimeters will your child grow? Going beyond the myth that height is decided by genes alone, we break down the science of how sleep, nutrition and exercise shape a child's growth.
The essentials of child growth every parent should know — from the mid-parental height formula to growth plates, growth hormone and key nutrients. From the Dr.Jay-ed educational channel.

📖 Chapters
0:00 How much will they grow?
0:30 The mid-parental height formula
1:03 Beyond genes: the factors you can control
2:37 Growth plates and bone age
4:07 Sleep and growth hormone
5:43 Nutrition: protein, vitamin D, zinc
7:09 Exercise and good posture
8:58 A summary for your child

🌐 Korean & English narration and subtitles are available. (Choose from the audio / subtitle tracks)

⚠️ Some of the visuals in this video were generated and directed using Google Veo and Flow AI technology.
※ This video is for general educational and informational purposes only and is not a substitute for individual medical diagnosis or treatment.

#ChildGrowth #ChildHeight #GrowthPlate #GrowTaller #Parenting #KidsHealth #DrJayEd""",
  },
 }},
}

c = sqlite3.connect(DB); cur = c.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS video_localizations(
  id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT, video_id TEXT, lang TEXT,
  title TEXT, description TEXT, updated_at TEXT, UNIQUE(video_id, lang))""")
for proj, info in DATA.items():
    vid = info["vid"]; d = os.path.join(ROOT, info["dir"])
    for lang, m in info["loc"].items():
        # 파일
        with open(os.path.join(d, f"loc_{lang}.txt"), "w", encoding="utf-8") as f:
            f.write(f"[제목 / TITLE] ({len(m['title'])}자)\n{m['title']}\n\n[설명 / DESCRIPTION]\n{m['desc']}\n")
        # DB
        cur.execute("""INSERT INTO video_localizations(project,video_id,lang,title,description,updated_at)
          VALUES(?,?,?,?,?,?) ON CONFLICT(video_id,lang) DO UPDATE SET
          title=excluded.title,description=excluded.description,updated_at=excluded.updated_at""",
          (proj, vid, lang, m["title"], m["desc"], DATE))
        print(f"{proj}/{lang}: 제목 {len(m['title'])}자 → DB + {info['dir']}/loc_{lang}.txt")
c.commit(); c.close()
print("DONE")
