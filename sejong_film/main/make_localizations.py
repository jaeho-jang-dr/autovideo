# -*- coding: utf-8 -*-
"""세종 영상 다국어 제목·설명(로컬라이제이션) 생성 → pkg/loc_<lang>.txt + content.db(video_localizations).
사용: python sejong_film/main/make_localizations.py"""
import os, sqlite3

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
PKG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pkg")
DB = os.path.join(ROOT, "channel", "content.db")
PROJECT = "sejong_hangeul"; VIDEO_ID = "6lGedBJ5xx4"; DATE = "2026-07-03"

LOC = {}

LOC["ko"] = {
"title": "세종대왕과 한글 창제 이야기 | 훈민정음은 어떻게 태어났을까? (King Sejong & Hangeul · 5 languages)",
"desc": """세종대왕이 백성을 위해 만든 글자 '한글(훈민정음)'의 탄생 이야기입니다. 580년 전 조선, 한 임금이 어떻게 세상에서 가장 과학적인 문자를 창제했을까요?
한국어·English·中文·日本語·Español 5개 언어 나레이션과 자막으로 만나는 세종대왕과 한글 창제의 모든 것 — Dr.Jay-ed 교육 채널.

📖 챕터 (타임스탬프)
0:00 광화문, 그 임금님을 아세요?
0:15 책을 사랑한 어린 왕자
3:23 스물둘, 왕이 되다
4:28 백성의 삶을 살피다
6:17 훈민정음을 만들다
7:13 반대에 맞서다
8:18 글자의 비밀 (자음·모음의 원리)
9:23 세상에 온 선물
10:27 580년의 선물
10:59 세계가 인정한 한글

🌐 5개 언어 지원: 오디오 트랙과 자막을 한국어 / English / 中文 / 日本語 / Español 로 바꿔 보실 수 있습니다.

⚠️ 본 영상의 시각 자료 중 일부는 Google Veo 및 Flow AI 기술을 활용하여 생성 및 연출되었습니다.

🎵 배경음악: 국악연주곡 '여민락(與民樂)' — 출처: 한국저작권위원회 공유마당 (CC BY 4.0)
https://gongu.copyright.or.kr/gongu/wrt/wrt/view.do?wrtSn=13263216
※ 여민락은 세종대왕이 지은 '용비어천가'를 노랫말로 한 궁중음악입니다.

#한글창제 #세종대왕 #훈민정음 #한글 #Hangeul #KingSejong #한국사 #Korean #세종 #DrJayEd""",
}

LOC["en"] = {
"title": "The Story of King Sejong & the Creation of Hangeul | How Was Hunminjeongeum Born? (5 languages)",
"desc": """The birth story of 'Hangeul (Hunminjeongeum)', the alphabet King Sejong created for his people. In Joseon 580 years ago, how did one king invent the world's most scientific writing system?
Everything about King Sejong and the creation of Hangeul — with narration and subtitles in 5 languages: 한국어 · English · 中文 · 日本語 · Español. Dr.Jay-ed educational channel.

📖 Chapters (timestamps)
0:00 Gwanghwamun — do you know this king?
0:15 The little prince who loved books
3:23 At twenty-two, he becomes king
4:28 Looking into the people's lives
6:17 Creating Hunminjeongeum
7:13 Facing the opposition
8:18 The secret of the letters (how consonants & vowels work)
9:23 A gift to the world
10:27 A gift 580 years in the making
10:59 Hangeul, recognized by the world

🌐 5-language support: you can switch the audio track and subtitles between 한국어 / English / 中文 / 日本語 / Español.

⚠️ Some of the visuals in this video were generated and directed using Google Veo and Flow AI technology.

🎵 Background music: Korean classical instrumental piece 'Yeomillak (與民樂)' — Source: Korea Copyright Commission, Gongu-Madang (CC BY 4.0)
https://gongu.copyright.or.kr/gongu/wrt/wrt/view.do?wrtSn=13263216
※ Yeomillak is court music set to the lyrics of 'Yongbieocheonga', composed under King Sejong.

#Hangeul #KingSejong #Hunminjeongeum #Korean #KoreanHistory #LearnKorean #Sejong #DrJayEd""",
}

LOC["zh"] = {
"title": "世宗大王与韩文创制的故事 | 训民正音是如何诞生的？（5种语言）",
"desc": """这是世宗大王为百姓创造的文字"韩文（训民正音）"的诞生故事。580年前的朝鲜，一位君王是如何创造出世界上最科学的文字的？
用5种语言的旁白与字幕，讲述世宗大王与韩文创制的一切——한국어 · English · 中文 · 日本語 · Español。Dr.Jay-ed 教育频道。

📖 章节（时间戳）
0:00 光化门，你认识这位君王吗？
0:15 热爱读书的小王子
3:23 二十二岁，登上王位
4:28 体察百姓的生活
6:17 创制训民正音
7:13 面对反对
8:18 文字的秘密（辅音与元音的原理）
9:23 献给世界的礼物
10:27 历经580年的礼物
10:59 被世界认可的韩文

🌐 支持5种语言：可将音轨与字幕切换为 한국어 / English / 中文 / 日本語 / Español。

⚠️ 本视频的部分视觉素材使用了 Google Veo 及 Flow AI 技术生成与制作。

🎵 背景音乐：韩国传统器乐曲《与民乐（여민락）》——来源：韩国著作权委员会 共享广场（CC BY 4.0）
https://gongu.copyright.or.kr/gongu/wrt/wrt/view.do?wrtSn=13263216
※《与民乐》是以世宗大王所作《龙飞御天歌》为歌词的宫廷音乐。

#韩文 #世宗大王 #训民正音 #韩语 #韩国历史 #Hangeul #KingSejong #DrJayEd""",
}

LOC["ja"] = {
"title": "世宗大王とハングル創製の物語 | 訓民正音はどう生まれたのか？（5言語）",
"desc": """世宗大王が民のために作った文字「ハングル（訓民正音）」の誕生物語です。580年前の朝鮮、一人の王はどのようにして世界で最も科学的な文字を創り出したのでしょうか？
5言語のナレーションと字幕で贈る、世宗大王とハングル創製のすべて——한국어 · English · 中文 · 日本語 · Español。Dr.Jay-ed 教育チャンネル。

📖 チャプター（タイムスタンプ）
0:00 光化門、この王様をご存知ですか？
0:15 本を愛した幼い王子
3:23 二十二歳、王になる
4:28 民の暮らしに目を向ける
6:17 訓民正音を作る
7:13 反対に立ち向かう
8:18 文字の秘密（子音・母音のしくみ）
9:23 世界への贈り物
10:27 580年の贈り物
10:59 世界が認めたハングル

🌐 5言語対応：音声トラックと字幕を 한국어 / English / 中文 / 日本語 / Español に切り替えられます。

⚠️ 本動画の映像素材の一部は、Google Veo および Flow の AI 技術を用いて生成・演出されています。

🎵 BGM：韓国伝統器楽曲「与民楽（ヨミンナク）」——出典：韓国著作権委員会 共有マダン（CC BY 4.0）
https://gongu.copyright.or.kr/gongu/wrt/wrt/view.do?wrtSn=13263216
※「与民楽」は世宗大王が作った「龍飛御天歌」を歌詞とした宮廷音楽です。

#ハングル #世宗大王 #訓民正音 #韓国語 #韓国史 #Hangeul #KingSejong #DrJayEd""",
}

LOC["es"] = {
"title": "La historia del Rey Sejong y la creación del Hangeul | ¿Cómo nació el Hunminjeongeum? (5 idiomas)",
"desc": """La historia del nacimiento del 'Hangeul (Hunminjeongeum)', el alfabeto que el Rey Sejong creó para su pueblo. En la Joseon de hace 580 años, ¿cómo logró un rey inventar el sistema de escritura más científico del mundo?
Todo sobre el Rey Sejong y la creación del Hangeul, con narración y subtítulos en 5 idiomas: 한국어 · English · 中文 · 日本語 · Español. Canal educativo Dr.Jay-ed.

📖 Capítulos (marcas de tiempo)
0:00 Gwanghwamun, ¿conoces a este rey?
0:15 El pequeño príncipe que amaba los libros
3:23 A los veintidós, se convierte en rey
4:28 Observando la vida de su pueblo
6:17 La creación del Hunminjeongeum
7:13 Enfrentando la oposición
8:18 El secreto de las letras (cómo funcionan consonantes y vocales)
9:23 Un regalo para el mundo
10:27 Un regalo de 580 años
10:59 El Hangeul, reconocido por el mundo

🌐 Soporte en 5 idiomas: puedes cambiar la pista de audio y los subtítulos entre 한국어 / English / 中文 / 日本語 / Español.

⚠️ Algunos de los recursos visuales de este video fueron generados y dirigidos con la tecnología de IA de Google Veo y Flow.

🎵 Música de fondo: pieza instrumental tradicional coreana 'Yeomillak (與民樂)' — Fuente: Comisión de Derechos de Autor de Corea, Gongu-Madang (CC BY 4.0)
https://gongu.copyright.or.kr/gongu/wrt/wrt/view.do?wrtSn=13263216
※ Yeomillak es música cortesana basada en la letra del 'Yongbieocheonga', compuesta en la época del Rey Sejong.

#Hangeul #ReySejong #Hunminjeongeum #Coreano #HistoriaDeCorea #AprenderCoreano #DrJayEd""",
}

# 1) 파일로 저장 (복사·붙여넣기용)
os.makedirs(PKG, exist_ok=True)
for lang, d in LOC.items():
    p = os.path.join(PKG, f"loc_{lang}.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"[제목 / TITLE] ({len(d['title'])}자)\n{d['title']}\n\n[설명 / DESCRIPTION]\n{d['desc']}\n")
    print(f"파일 저장: pkg/loc_{lang}.txt (제목 {len(d['title'])}자)")

# 2) content.db 저장
c = sqlite3.connect(DB); cur = c.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS video_localizations(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project TEXT, video_id TEXT, lang TEXT,
  title TEXT, description TEXT, updated_at TEXT,
  UNIQUE(video_id, lang))""")
for lang, d in LOC.items():
    cur.execute("""INSERT INTO video_localizations(project,video_id,lang,title,description,updated_at)
      VALUES(?,?,?,?,?,?)
      ON CONFLICT(video_id,lang) DO UPDATE SET title=excluded.title,description=excluded.description,updated_at=excluded.updated_at""",
      (PROJECT, VIDEO_ID, lang, d["title"], d["desc"], DATE))
c.commit()
n = cur.execute("SELECT COUNT(*) FROM video_localizations WHERE video_id=?", (VIDEO_ID,)).fetchone()[0]
print(f"\ncontent.db video_localizations: {VIDEO_ID} 언어 {n}개 저장됨")
c.close()
print("DONE")
