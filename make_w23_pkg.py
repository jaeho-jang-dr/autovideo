# -*- coding: utf-8 -*-
"""W23 업로드 패키지 생성 — 제목·설명·태그·고정댓글 5개국어 (2026-07-28).

챕터 타임코드는 렌더 후 타임라인에서 자동 계산해 설명에 끼워 넣는다.
출력: hangeul_birth_vowels/w23pkg/
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PKG = "hangeul_birth_vowels/w23pkg"
os.makedirs(PKG, exist_ok=True)
TL = "hangeul_birth_vowels/hangeul_w23_injun_np_timeline.json"

# 막 구분(시나리오 기준) — 씬 번호 → 챕터 제목
CHAPTERS = [
    (1,  "도착 · 오늘의 세 표현", "Arrival · Today's three expressions"),
    (6,  "어휘 7 (약속 · 약속을 잡다 · 시간 조율 · 모임 · 회식 · 장소 · 시간 정하다)",
         "7 words (약속 · 약속을 잡다 · 시간 조율 · 모임 · 회식 · 장소 · 시간 정하다)"),
    (14, "시간 조율 표현 (언제가 괜찮으세요? · 혹시 · 가능한 시간)",
         "Coordinating times (언제가 괜찮으세요? · 혹시 · 가능한 시간)"),
    (22, "장소 정하기 · 확정 표현", "Deciding the place · confirming"),
    (29, "실전 대화 · 역할극 · 복습", "Real conversation · role-play · review"),
]


def chapter_lines():
    if not os.path.exists(TL):
        return ["0:00 도착 · 오늘의 세 표현"], ["0:00 Arrival · Today's three expressions"]
    tl = json.load(open(TL, encoding="utf-8"))
    start, t = {}, 0.0
    for s in tl["scenes"]:
        start[s["seq"]] = t
        t += s["dur"]
    ko, en = [], []
    for seq, k, e in CHAPTERS:
        sec = int(start.get(seq, 0))
        ts = f"{sec//60}:{sec%60:02d}"
        ko.append(f"{ts} {k}")
        en.append(f"{ts} {e}")
    return ko, en


KO_CH, EN_CH = chapter_lines()
CH_KO = "\n".join(KO_CH)
CH_EN = "\n".join(EN_CH)

AI_KO = ("🤖 제작 안내 / AI note\n"
         "배경 이미지는 Google Gemini(Nano Banana), 배경 영상은 Google Veo·Flow로 생성했고, "
         "캐릭터 애니메이션은 자체 엔진, 나레이션은 Microsoft Azure TTS(선희·Emma)로 만들었습니다. "
         "Backgrounds by Google Gemini and Veo/Flow, character animation by our own engine, "
         "narration by Azure TTS. AI-generated and AI-assisted content.")
AI_EN = ("🤖 AI note\n"
         "Backgrounds were generated with Google Gemini (Nano Banana) and Google Veo/Flow, "
         "character animation with our own engine, and narration with Microsoft Azure TTS "
         "(SunHi / Emma). AI-generated and AI-assisted content.")
WEB = "🌐 drjayed.com"

KEY_KO = ("약속 · 약속을 잡다 · 시간 조율 · 모임 · 회식 · 장소 · 시간 정하다 · "
          "언제가 괜찮으세요? · 혹시 · 가능한 시간 · 언제든 괜찮아요 · 어려울 것 같아요 · "
          "어떠세요? · 정문 앞에서 만나요 · 만나기로 해요 · 그럼 그렇게 해요 · 확정")

FILES = {}

FILES["ko_title.txt"] = "모임 약속 잡기 - '약속을 잡다' & '시간 조율' | 한글 배우기 W23 (에버랜드)"
FILES["en_title.txt"] = ("Making Plans in Korean: '약속을 잡다' & '시간 조율' "
                         "| Learn Korean W23")
FILES["ja_title.txt"] = "韓国語で約束を取りつける -「약속을 잡다」と「시간 조율」| 韓国語を学ぶ W23"
FILES["zh_title.txt"] = "用韩语约见面 -「약속을 잡다」和「시간 조율」| 学韩语 W23"
FILES["es_title.txt"] = ("Quedar en coreano: '약속을 잡다' y '시간 조율' "
                         "| Aprende coreano W23")

FILES["ko_desc.txt"] = f"""놀이공원을 함께 걸으며, 여러 사람과 만날 날을 정하고 서로 시간을 맞추는 한국어를 배웁니다.

먼저 모임에 꼭 필요한 어휘 — '약속'·'약속을 잡다'·'시간 조율'·'모임'·'회식'·'장소'·'시간 정하다' — 를 하나씩 익혀요. 그다음은 조율하는 말입니다. 먼저 묻고('언제가 괜찮으세요?'), 조심스럽게 덧붙이고('혹시'), 되면 '언제든 괜찮아요', 안 되면 '어려울 것 같아요'로 부드럽게 답한 뒤 '어떠세요?'로 상대에게 되물어요. 마지막엔 장소를 정하고('정문 앞에서 만나요') 확정하는('그럼 그렇게 해요') 실전 대화까지 연습합니다.

초보자와 중급자 모두 환영합니다. 한글만으로 공부하는 분들을 위해 자막에 실제 발음을 로마자로 적어 두었어요(연음·경음화까지 반영).

📚 오늘 배우는 핵심 표현
{KEY_KO}

⏱️ 챕터 / Chapters
{CH_KO}

{AI_KO}

{WEB}
"""

FILES["en_desc.txt"] = f"""Walk through a theme park and learn the Korean you need to set up a group meetup and coordinate everyone's schedules.

We start with the words a gathering needs — '약속' (appointment), '약속을 잡다' (make plans), '시간 조율' (coordinating times), '모임' (gathering), '회식' (company dinner), '장소' (place) and '시간 정하다' (decide the time). Then the coordinating phrases: ask first with '언제가 괜찮으세요?' (when works for you?), soften it with '혹시' (by any chance), answer '언제든 괜찮아요' (any time works) or, if it won't work, '어려울 것 같아요' (that may be hard) — then hand it back with '어떠세요?' (how about it?). We finish by settling the place ('정문 앞에서 만나요') and confirming ('그럼 그렇게 해요') in a full conversation.

Beginners and intermediate learners are both welcome. Subtitles show the real pronunciation in roman letters (including liaison and tensing) for learners studying in Hangul only.

📚 Key expressions
{KEY_KO}

⏱️ Chapters
{CH_EN}

{AI_EN}

{WEB}
"""

FILES["ja_desc.txt"] = f"""遊園地を歩きながら、みんなで会う日を決めて予定を合わせる韓国語を学びます。

まずは集まりに欠かせない語彙 —「약속」(約束)・「약속을 잡다」(約束を取りつける)・「시간 조율」(時間の調整)・「모임」(集まり)・「회식」(会食)・「장소」(場所)・「시간 정하다」(時間を決める)。次に調整の言い方です。まず「언제가 괜찮으세요?」(いつがよろしいですか)と尋ね、「혹시」(もしかして)で控えめに添え、大丈夫なら「언제든 괜찮아요」、難しければ「어려울 것 같아요」とやわらかく断ってから「어떠세요?」で相手に返します。最後は場所を決めて（「정문 앞에서 만나요」）確定する（「그럼 그렇게 해요」）実践会話まで練習します。

初級・中級どちらの方も歓迎です。ハングルだけで学ぶ方のために、字幕には実際の発音をローマ字で記しています（連音・濃音化も反映）。

📚 今日の重要表現
{KEY_KO}

⏱️ チャプター
{CH_EN}

{AI_EN}

{WEB}
"""

FILES["zh_desc.txt"] = f"""一边逛游乐园，一边学习用韩语约定见面的日子、协调大家的时间。

先掌握聚会必备词汇 —「약속」(约定)、「약속을 잡다」(约时间)、「시간 조율」(协调时间)、「모임」(聚会)、「회식」(聚餐)、「장소」(地点)、「시간 정하다」(定时间)。接着是协调用语：先问「언제가 괜찮으세요?」(您什么时候方便)，用「혹시」(或许) 委婉铺垫，可以就说「언제든 괜찮아요」，不方便就用「어려울 것 같아요」婉拒，再用「어떠세요?」把话题交回对方。最后练习定地点(「정문 앞에서 만나요」)并确认(「그럼 그렇게 해요」)的完整对话。

欢迎初学者和中级学习者。为了只用韩文学习的朋友，字幕里标注了实际发音的罗马字（含连音和紧音化）。

📚 今天的核心表达
{KEY_KO}

⏱️ 章节
{CH_EN}

{AI_EN}

{WEB}
"""

FILES["es_desc.txt"] = f"""Recorré un parque de diversiones y aprendé el coreano que se necesita para organizar una reunión y coordinar los horarios de todos.

Empezamos con el vocabulario indispensable: '약속' (cita), '약속을 잡다' (concertar una cita), '시간 조율' (coordinar horarios), '모임' (reunión), '회식' (cena de trabajo), '장소' (lugar) y '시간 정하다' (fijar la hora). Después vienen las frases para coordinar: primero preguntá con '언제가 괜찮으세요?' (¿cuándo le viene bien?), suavizá con '혹시' (por casualidad), respondé '언제든 괜찮아요' si te sirve cualquier momento o '어려울 것 같아요' si no podés, y devolvé la palabra con '어떠세요?' (¿qué le parece?). Cerramos fijando el lugar ('정문 앞에서 만나요') y confirmando ('그럼 그렇게 해요') en una conversación completa.

Principiantes e intermedios son bienvenidos. Los subtítulos incluyen la pronunciación real en letras romanas (con enlace y tensión) para quienes estudian solo con hangul.

📚 Expresiones clave
{KEY_KO}

⏱️ Capítulos
{CH_EN}

{AI_EN}

{WEB}
"""

FILES["w23_tags.txt"] = (
    "learn korean, korean for beginners, korean lesson, speak korean, korean language, "
    "study korean, korean conversation, making plans in korean, korean appointment, "
    "schedule in korean, korean grammar, korean sentence patterns, korean phrases, "
    "korean politeness, 한국어 배우기, 한국어 회화, 왕초보 한국어, 약속 잡기, 시간 조율, 모임 표현, "
    "에버랜드, 韓国語 約束, 韓国語 学習, 学韩语, 韩语约会, aprender coreano, coreano quedar, "
    "drjayed, TOPIK")

FILES["ko_comment.txt"] = f"""오늘의 핵심 표현이에요 👇
{KEY_KO}

'언제가 괜찮으세요?' 하나만 외워도 모임 잡기가 훨씬 수월해집니다. 여러분은 친구들과 약속 잡을 때 주로 뭐라고 하시나요? 댓글로 알려 주세요 🙂

⏱️ 챕터
{CH_KO}
"""

FILES["en_comment.txt"] = f"""Today's key expressions 👇
{KEY_KO}

Even just '언제가 괜찮으세요?' (when works for you?) makes setting up a meetup far easier. How do you usually make plans with friends? Tell me in the comments 🙂

⏱️ Chapters
{CH_EN}
"""

for name, body in FILES.items():
    open(f"{PKG}/{name}", "w", encoding="utf-8").write(body)
print(f"패키지 {len(FILES)}개 파일 → {PKG}")
for k in sorted(FILES):
    print(f"  {k:18s} {len(FILES[k]):5d}자")
print()
print("챕터(KO):"); [print("  ", c) for c in KO_CH]
