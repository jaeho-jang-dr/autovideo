# -*- coding: utf-8 -*-
"""W22 업로드 패키지 생성 — 제목/설명(5개국)·태그·고정댓글·매니페스트(ko/en).
   ★챕터는 렌더 후 타임라인(hangeul_w22_jieun_np_timeline.json)에서 실측 계산한다
     — Azure TTS는 edge와 길이가 달라 손으로 적으면 어긋난다.
   (make_w21_package.py 계승)"""
import os, json
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w22pkg"
os.makedirs(PKG, exist_ok=True)
def w(name, text): open(os.path.join(PKG, name), "w", encoding="utf-8").write(text.strip() + "\n")

# ── 챕터: 막 시작 씬의 누적 시각(실측) ──────────────────────────────
TL = "hangeul_birth_vowels/hangeul_w22_jieun_np_timeline.json"
ACTS = [(1, "도착 · 오늘의 두 표현", "Arrival · today's two patterns"),
        (4, "여행 어휘 (여행 · 경험 · 명소 · 예약 · 숙소 · 계획)", "Travel vocabulary"),
        (10, "경험 말하기 '가 본 적이 있어요'", "Past experience: 가 본 적이 있어요"),
        (15, "계획 말하기 '할 계획이에요'", "Future plans: 할 계획이에요"),
        (20, "실전 대화 · 복습 · 마무리", "Real conversation · review · wrap-up")]


def chapters():
    tl = json.load(open(TL, encoding="utf-8"))
    starts, acc = {}, 0.0
    for s in tl["scenes"]:
        starts[s["seq"]] = acc
        acc += s["dur"]
    def ts(t):
        return f"{int(t)//60}:{int(t)%60:02d}"
    ko = ["⏱️ 챕터 / Chapters"]
    en = ["⏱️ Chapters"]
    for seq, kt, et in ACTS:
        t = 0.0 if seq == 1 else starts[seq]      # 첫 챕터는 반드시 0:00
        ko.append(f"{ts(t)} {kt}")
        en.append(f"{ts(t)} {et}")
    return "\n".join(ko), "\n".join(en)


CHAP_KO, CHAP_EN = chapters()

TITLES = {
 "ko": "여행 한국어 - 경험 '가 본 적이 있어요' & 계획 '할 계획이에요' | 한글 배우기 W22 (하늘 전망대)",
 "en": "Travel Korean: Past Experience '가 본 적이 있어요' & Future Plans '할 계획이에요' | Learn Korean W22",
 "ja": "韓国語で旅行の話 - 経験「가 본 적이 있어요」と計画「할 계획이에요」| 韓国語を学ぶ W22 (展望台)",
 "zh": "用韩语聊旅行 - 经历「가 본 적이 있어요」和计划「할 계획이에요」| 学韩语 W22 (天空展望台)",
 "es": "Coreano para viajes: experiencias '가 본 적이 있어요' y planes '할 계획이에요' | Aprende coreano W22",
}

AI = ("🤖 제작 안내 / AI note\n"
      "배경 이미지는 Google Gemini(Nano Banana), 배경 영상은 Google Veo·Flow로 생성했고, "
      "캐릭터 애니메이션은 자체 엔진, 나레이션은 Microsoft Azure TTS(선희·Emma)로 만들었습니다. "
      "Backgrounds by Google Gemini and Veo/Flow, character animation by our own engine, "
      "narration by Azure TTS. AI-generated and AI-assisted content.")

KEYVOCAB = ("여행 · 경험 · 명소 · 예약 · 숙소 · 계획 · 가 본 적이 있어요 · 가 본 적이 없어요 · "
            "두 번 가 본 적이 있어요 · 할 계획이에요 · 갈 계획이에요 · 등산할 계획이에요 · "
            "예약할 계획이에요 · 언제 갈 계획이에요? · 제주도 · 부산")

DESC = {
 "ko": f"""높은 하늘 전망대에서 도시를 내려다보며, 다녀온 '여행 경험'과 앞으로의 '계획'을 한국어로 말하는 법을 배웁니다.

먼저 여행에 꼭 필요한 어휘 — '여행'·'경험'·'명소'·'예약'·'숙소'·'계획' — 을 하나씩 익혀요. 그다음 오늘의 두 문형입니다. 가 본 곳은 '가 본 적이 있어요', 안 가 본 곳은 '가 본 적이 없어요'. 앞으로 할 일은 '할 계획이에요' — '갈 계획이에요', '등산할 계획이에요', '예약할 계획이에요'처럼 하고 싶은 일을 앞에 붙이면 됩니다. 마지막엔 '어디에 가 본 적이 있어요?' → '언제 갈 계획이에요?'로 이어지는 실전 대화까지 연습해요.

초보자와 중급자 모두 환영합니다. 한글만으로 공부하는 분들을 위해 자막에 실제 발음을 로마자로 적어 두었어요(연음까지 반영).

📚 오늘 배우는 핵심 표현
{KEYVOCAB}

{CHAP_KO}

{AI}

🌐 drjayed.com""",

 "en": f"""From a high sky observatory looking out over the city, learn how to talk about trips you've taken (경험) and trips you're planning (계획) in Korean.

We start with the travel words you actually need — '여행' (travel), '경험' (experience), '명소' (famous spot), '예약' (reservation), '숙소' (accommodation), '계획' (plan). Then today's two patterns: use '가 본 적이 있어요' for places you've been and '가 본 적이 없어요' for places you haven't. For the future, use '할 계획이에요' — just put what you intend to do in front: '갈 계획이에요' (plan to go), '등산할 계획이에요' (plan to hike), '예약할 계획이에요' (plan to book). We finish with a real exchange: '어디에 가 본 적이 있어요?' → '언제 갈 계획이에요?'

Great for beginners and intermediate learners. Subtitles include romanization of the actual pronunciation (liaison included) for those studying with hangul only.

📚 Key expressions
{KEYVOCAB}

{CHAP_EN}

{AI}

🌐 drjayed.com""",

 "ja": f"""高い展望台から街を見下ろしながら、行ってきた「여행 경험(旅行の経験)」とこれからの「계획(計画)」を韓国語で話す方法を学びます。

まず旅行に必要な語彙 —「여행(旅行)」「경험(経験)」「명소(名所)」「예약(予約)」「숙소(宿)」「계획(計画)」— を一つずつ。そして今日の二つの文型です。行ったことがある場所は「가 본 적이 있어요」、行ったことがない場所は「가 본 적이 없어요」。これからの予定は「할 계획이에요」—「갈 계획이에요(行く予定です)」「등산할 계획이에요(登山する予定です)」「예약할 계획이에요(予約する予定です)」のように、したいことを前に付けるだけ。最後は「어디에 가 본 적이 있어요?」→「언제 갈 계획이에요?」の実践会話まで練習します。

初級・中級者歓迎。ハングルだけで学ぶ方のために、字幕には実際の発音(連音まで反映)をローマ字で入れました。

📚 主な表現
{KEYVOCAB}

{CHAP_EN}

{AI}

🌐 drjayed.com""",

 "zh": f"""从高高的天空展望台俯瞰城市，学习用韩语讲述去过的「여행 경험(旅行经历)」和未来的「계획(计划)」。

先掌握旅行必备词汇 —「여행(旅行)」「경험(经历)」「명소(名胜)」「예약(预约)」「숙소(住宿)」「계획(计划)」。然后是今天的两个句型：去过的地方用「가 본 적이 있어요」，没去过的用「가 본 적이 없어요」。未来的打算用「할 계획이에요」— 只要把想做的事放在前面，就是「갈 계획이에요(打算去)」「등산할 계획이에요(打算爬山)」「예약할 계획이에요(打算预订)」。最后练习实战对话：「어디에 가 본 적이 있어요?」→「언제 갈 계획이에요?」

欢迎初级和中级学习者。为只用韩文学习的朋友，字幕中标注了实际发音的罗马音(含连音)。

📚 核心表达
{KEYVOCAB}

{CHAP_EN}

{AI}

🌐 drjayed.com""",

 "es": f"""Desde un mirador en las alturas con vista a la ciudad, aprende a hablar en coreano de los viajes que ya hiciste (경험) y de los que estás planeando (계획).

Empezamos con el vocabulario que de verdad necesitas — '여행' (viaje), '경험' (experiencia), '명소' (lugar famoso), '예약' (reserva), '숙소' (alojamiento), '계획' (plan). Luego, los dos patrones de hoy: usa '가 본 적이 있어요' para los lugares que ya visitaste y '가 본 적이 없어요' para los que no. Para el futuro, usa '할 계획이에요' — solo pon delante lo que piensas hacer: '갈 계획이에요' (planeo ir), '등산할 계획이에요' (planeo hacer senderismo), '예약할 계획이에요' (planeo reservar). Terminamos con una conversación real: '어디에 가 본 적이 있어요?' → '언제 갈 계획이에요?'

Ideal para principiantes e intermedios. Los subtítulos incluyen la romanización de la pronunciación real (con enlace de sonidos) para quienes estudian solo con hangul.

📚 Expresiones clave
{KEYVOCAB}

{CHAP_EN}

{AI}

🌐 drjayed.com""",
}

TAGS = ("learn korean, korean for beginners, korean lesson, speak korean, korean language, study korean, "
        "travel korean, korean travel phrases, korean past experience, korean future plans, "
        "korean grammar, korean sentence patterns, korean phrases, korean conversation, "
        "한국어 배우기, 한국어 회화, 왕초보 한국어, 여행 한국어, 경험 표현, 계획 표현, 전망대, "
        "韓国語 旅行, 韓国語 学習, 学韩语, 韩语旅行, aprender coreano, coreano viajes, "
        "drjayed, TOPIK")

COMMENT = {
 "ko": ("오늘의 두 문형만 기억하세요! 👀 다녀온 곳은 '가 본 적이 있어요', 아직이면 '가 본 적이 없어요'. "
        "앞으로 할 일은 하고 싶은 걸 앞에 붙여서 '갈 계획이에요', '등산할 계획이에요'처럼요. "
        "여러분은 어디에 가 본 적이 있나요? 그리고 다음엔 어디에 갈 계획이에요? 댓글로 알려 주세요 😊 "
        "구독하고 다음 강의도 함께해요! 🌐 drjayed.com"),
 "en": ("Just remember today's two patterns! 👀 For places you've been: '가 본 적이 있어요'. "
        "Not yet? '가 본 적이 없어요'. For the future, put what you'll do in front: '갈 계획이에요', "
        "'등산할 계획이에요'. Where have you been, and where are you planning to go next? "
        "Tell us in the comments 😊 Subscribe for more! 🌐 drjayed.com"),
}

for lg in TITLES: w(f"{lg}_title.txt", TITLES[lg])
for lg in DESC:   w(f"{lg}_desc.txt", DESC[lg])
w("w22_tags.txt", TAGS)
for lg in COMMENT: w(f"{lg}_comment.txt", COMMENT[lg])


# 매니페스트(ko/en) — yt_api.py localize 소비 (langs 배열: row/srt/title/desc/add/do)
def manifest(video_lang, video_path):
    rows = [("한국어", "ko"), ("영어", "en"), ("일본어", "ja"), ("중국어(중국)", "zh"), ("스페인어", "es")]
    base = "ko" if video_lang == "한국어" else "en"
    langs = []
    for row, code in rows:
        add = code != base                      # 본언어 행은 add 없음
        e = {"row": row, "srt": f"{PKG}/hangeul_w22_jieun_np.{code}.srt", "add": add, "do": ["sub", "meta"]}
        e["title"] = f"{PKG}/{code}_title.txt"
        e["desc"] = f"{PKG}/{code}_desc.txt"
        langs.append(e)
    langs.sort(key=lambda e: e["add"])           # 본언어(add=False) 먼저 → do_meta의 기본언어 판정
    return {"week": "W22", "video_lang": video_lang, "video": video_path,
            "thumbnail": f"hangeul_birth_vowels/thumb_w22_{base}_1280x720.jpg",
            "langs": langs, "tags_file": f"{PKG}/w22_tags.txt",
            "privacyStatus": "unlisted", "video_id": "", "url": ""}


json.dump(manifest("한국어", "hangeul_birth_vowels/hangeul_w22_jieun_np_ko.mp4"),
          open(f"{PKG}/w22_ko_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(manifest("영어", "hangeul_birth_vowels/hangeul_w22_jieun_np_en.mp4"),
          open(f"{PKG}/w22_en_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("W22 패키지 생성:", sorted(os.listdir(PKG)))
print("태그 길이:", len(TAGS), "자")
for c in TITLES:
    print(f"  {c} 제목 {len(TITLES[c])}자")
print("\n" + CHAP_KO)
