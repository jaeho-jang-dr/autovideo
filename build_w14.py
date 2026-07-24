# -*- coding: utf-8 -*-
"""W14(나의 하루 일과와 동작) 46씬 ~8분: 마담제이, 협재해수욕장.
★사장님 지시 반영:
  - 감정 표현·특이 포즈(노을·별·기지개·놀람 등)는 **테이크를 길게**
  - 만든 포즈는 **전부 사용**(미사용 0)
  - 앉기 씬은 **고정 좌표**(scale=0.946, cx=470, cy=700) + 의자 없는 배경(_fit)
  - 중간동작(_a)으로 부드럽게 이어짐
"""
import sqlite3, json, os, re as _re2
from PIL import Image, ImageDraw, ImageFont

def norm_quotes(s):
    s = s.replace("‘", "'").replace("’", "'")
    s = _re2.sub(r"'([^']*?)([?!.]+)'", r"'\1'\2", s)
    return s

def wrap_write(gl, maxch=7):
    parts = [p.strip() for p in gl.split("/")] if "/" in gl else [gl]
    lines = []
    for part in parts:
        cur = ""
        for tok in part.split():
            if not cur: cur = tok
            elif len(cur) + 1 + len(tok) <= maxch: cur += " " + tok
            else: lines.append(cur); cur = tok
        if cur: lines.append(cur)
    return lines or [gl]

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"; FONT = "assets/fonts/Cafe24Dongdong.ttf"
PLACE = "Hyeopjae Beach, Jeju"
EP = "KO-W14"

# 배경
DAWN, BEDR, BEDS, WIN = "bg_w14_dawn", "bg_w14_bedroom", "bg_w14_bedside", "bg_w14_window"
BATH, ROOM, KIT, KIT2, DOOR = "bg_w14_bath", "bg_w14_room", "bg_w14_kitchen", "bg_w14_kitchen2", "bg_w14_door"
CAFE_F, DESK_F, BTBL_F, NDSK_F = "bg_w14_cafe_fit", "bg_w14_desk_fit", "bg_w14_beachtable_fit", "bg_w14_nightdesk_fit"
BEACH, BWALK, SEA, SEA2 = "bg_w14_beach", "bg_w14_beach_walk", "bg_w14_sea", "bg_w14_sea2"
SUNB, DIN, TERR, SUN = "bg_w14_sunset_beach", "bg_w14_dinner", "bg_w14_terrace", "bg_w14_sunset"
BATHN, BEDN, NIGHT = "bg_w14_bath_night", "bg_w14_bed_night", "bg_w14_night_sky"
TVROOM, BEDNOBED = "bg_w14_livingroom_tv", "bg_w14_bedroom_nobed"   # ★교정: TV거실 / 침대없는 밤방

# ★★★W11(감천 식당, 성공작) 규격 — 좌표는 전 씬 '하나'만 쓴다.
#    비결: 포즈 PNG를 560x860 캔버스에 **인물 맨아래 = y700** 으로 정규화(normalize_w14_w11style.py).
#          → 같은 좌표로 얹어도 서기(432px)·앉기(328px)·누움 모두 바닥이 맞고 안 잘린다.
#    앉기/서기용 좌표를 따로 만들면 반드시 사고 난다(W14 1차: 앉기 370px 잘림).
CHAR_CX, CHAR_CY, CHAR_SCALE = 300, 452, 0.655      # ★전 포즈 공통 (W11 = 300,452,0.6)

# 앉기 씬 표시(고정 좌표 적용)
SIT_BG = {CAFE_F, DESK_F, BTBL_F, NDSK_F, BEACH, DIN, TERR, BEDN, BEDR, NIGHT}
SIT_POSES = {"eat_sit","drink_sit","sit_desk","work_laptop","work_laptop_a","study_book","study_book_a",
             "read_book","write_note","write_note_a","rest_sit","watch_tv","write_diary","wake_sit",
             "sit_stargaze","sleep","sleep_a"}

# (cap_ko, cap_en, glyph, script_kr, script_en, bg, beats[(pose, x_from, x_to, ratio)])
# ★감정/특이 포즈는 ratio를 크게(0.5~0.75) — 테이크를 길게 잡아 관객이 볼 시간을 준다
SC = [
 # ── 1막 새벽·아침: 일어나다 (S1~S8) ──
 ("협재 바다의 아침","Morning at Hyeopjae","협재 해수욕장",
  "안녕하세요! 오늘은 제주 협재 바다에서 하루를 보내요. 아침에 일어나서 밤에 잠들 때까지, 나의 하루를 한국어로 말해 봐요!",
  "Hello! Today we spend a day at Hyeopjae Beach in Jeju. From waking up in the morning to falling asleep at night — let's describe our day in Korean!",
  DAWN,[("walk_right1",-120,200,0.2),("walk_right2",200,300,0.2),("presenting_a",300,300,0.12),("presenting",300,300,0.28),
        ("look_sky_a",300,300,0.05),("look_sky",300,300,0.15)]),   # ★하늘 보기(캐릭터성)
 ("하루 일과","Daily routine","하루 일과",
  "'일과'는 매일 하는 일이에요. 오늘은 하루의 일과를 순서대로 배워요.",
  "'일과' means daily routine — the things you do every day. Today we learn them in order.",
  DAWN,[("presenting_a",300,300,0.2),("presenting",300,300,0.8)]),
 ("일어나다","to wake up","일어나다",
  "핵심 단어! '일어나다'. 잠에서 깨어 몸을 일으키는 거예요.",
  "Key word! '일어나다' — to wake up, to get up from sleep.",
  BEDR,[("wake_sit",300,300,1.0)]),
 ("아침에 일어나요","I wake up in the morning","아침에 / 일어나요",
  "'아침에 일어나요.' '-에'는 시간을 나타내요. 아침에, 저녁에, 밤에.",
  "'아침에 일어나요' (I wake up in the morning). '-에' marks time: 아침에 (in the morning), 밤에 (at night).",
  BEDS,[("stretch_a",300,300,0.28),("stretch",300,300,0.72)]),   # ★기지개 = 특이 포즈, 길게
 ("몇 시에 일어나요?","What time do you wake up?","몇 시에 / 일어나요",
  "'몇 시에 일어나요?' 하고 물어봐요. 대화의 좋은 시작이에요.",
  "Ask '몇 시에 일어나요?' (What time do you get up?). A great conversation starter.",
  BEDS,[("speak_a",300,300,0.15),("speak",300,300,0.85)]),
 ("일곱 시에 일어나요","I get up at seven","일곱 시에 / 일어나요",
  "'일곱 시에 일어나요.' 시간을 넣어서 대답해요.",
  "'일곱 시에 일어나요' (I get up at seven). Answer with the time.",
  BEDS,[("count_fingers",300,300,1.0)]),
 ("일찍 / 늦게","early / late","일찍 늦게",
  "'일찍'과 '늦게'. 짝으로 외우면 쉬워요. 일찍 일어나요, 늦게 자요.",
  "'일찍' (early) and '늦게' (late). Learn them as a pair: 일찍 일어나요, 늦게 자요.",
  WIN,[("presenting_a",300,300,0.2),("presenting",300,300,0.8)]),
 ("창문을 열어요","I open the window","창문을 / 열어요",
  "'창문을 열어요.' 와, 협재 바다가 보여요! 하늘도 정말 예뻐요.",
  "'창문을 열어요' (I open the window). Wow — the sea at Hyeopjae! And what a beautiful sky.",
  # ★교정: 배경에 창문이 이미 열려 있으니 창문 잡는 포즈 대신 '손 들고 오른쪽 보기'
  WIN,[("hand_up_right",300,300,0.55),
       ("look_sky_a",300,300,0.08),("look_sky",300,300,0.37)]),   # ★하늘 감탄, 길게

 # ── 2막 아침 준비 (S9~S16) ──
 ("세수하다","to wash your face","세수하다",
  "'세수하다'는 얼굴을 씻는 거예요. 아침에 제일 먼저 하는 일이죠.",
  "'세수하다' means to wash your face — the first thing in the morning.",
  BATH,[("wash_face",560,560,1.0)]),   # ★교정: 중앙으로 이동(세면대에 맞춤)
 ("이를 닦다","to brush your teeth","이를 닦다",
  "'이를 닦다.' 칫솔로 이를 깨끗하게 닦아요.",
  "'이를 닦다' (to brush your teeth). Clean them well with a toothbrush.",
  BATH,[("brush_teeth",560,560,1.0)]),   # ★교정: 중앙으로 이동(세면대에 맞춤)
 ("옷을 입다","to get dressed","옷을 입다 / 옷을 벗다",
  "'옷을 입다.' 반대말은 '옷을 벗다'예요. 입다, 벗다. 짝으로 기억해요.",
  "'옷을 입다' (to put on clothes). The opposite is '옷을 벗다' (to take off). Learn them as a pair.",
  ROOM,[("dress",300,300,1.0)]),
 ("그리고 / 그다음에","and / then","그리고 / 그다음에",
  "일과를 이어서 말할 때 써요. '세수하고 그다음에 아침을 먹어요.' 이렇게 연결해요.",
  "Use these to connect your routine: '세수하고 그다음에 아침을 먹어요' (I wash my face and then eat breakfast).",
  ROOM,[("presenting_a",300,300,0.2),("presenting",300,300,0.5),("smile_big",300,300,0.3)]),
 ("아침을 먹다","to eat breakfast","아침을 먹다",
  "'아침을 먹다.' 아침, 점심, 저녁 + 먹다. 하루 세 끼예요.",
  "'아침을 먹다' (to eat breakfast). 아침/점심/저녁 + 먹다 — three meals a day.",
  KIT,[("eat_sit",470,470,1.0)]),
 ("커피를 마시다","to drink coffee","커피를 / 마시다",
  "'마시다'는 액체를 먹는 거예요. 먹다와 마시다, 구분해서 써요.",
  "'마시다' is for liquids. Korean distinguishes 먹다 (eat) from 마시다 (drink).",
  KIT2,[("drink_sit",470,470,1.0)]),
 ("문제 발생!","A problem!","늦었어요",
  "어? 시계를 보니 늦었어요! 오늘은 카페에 가야 하는데!",
  "Uh-oh — look at the clock! '늦었어요' (We're late). And we have to get to the cafe!",
  KIT2,[("surprise_a",300,300,0.25),("surprise",300,300,0.75)]),   # ★놀람, 길게
 ("서두르다","to hurry","서두르다",
  "'서두르다'는 빨리 움직이는 거예요. 서둘러요!",
  "'서두르다' means to hurry. Let's move quickly!",
  DOOR,[("hurry_a",250,300,0.25),("hurry",300,480,0.75)]),

 # ── 3막 낮: 일하다·공부하다 (S17~S24) ──
 ("일하다","to work","일하다",
  "핵심 단어! '일하다'. 직장이나 카페에서 하는 일이에요.",
  "Key word! '일하다' — to work.",
  CAFE_F,[("work_laptop_a",470,470,0.2),("work_laptop",470,470,0.8)]),
 ("카페에서 일해요","I work at a cafe","카페에서 / 일해요",
  "'-에서'는 장소를 나타내요. 행동이 일어나는 곳이에요. 카페에서, 집에서, 학교에서.",
  "'-에서' marks the place where an action happens: 카페에서 (at a cafe), 집에서 (at home).",
  CAFE_F,[("work_laptop",470,470,1.0)]),
 ("공부하다","to study","공부하다",
  "핵심 단어! '공부하다'. 저는 매일 한국어를 공부해요.",
  "Key word! '공부하다' — to study. I study Korean every day.",
  DESK_F,[("study_book_a",470,470,0.2),("study_book",470,470,0.8)]),
 ("한국어를 공부해요","I study Korean","한국어를 / 공부해요",
  "'을/를'은 목적어를 나타내요. 한국어를 공부해요. 책을 읽어요.",
  "'을/를' marks the object: 한국어를 공부해요 (I study Korean), 책을 읽어요 (I read a book).",
  DESK_F,[("study_book",470,470,1.0)]),
 ("책을 읽다","to read a book","책을 읽다",
  "'책을 읽다.' 조용히 앉아서 책을 읽어요.",
  "'책을 읽다' (to read a book). Sit quietly and read.",
  DESK_F,[("read_book",470,470,1.0)]),
 ("쓰다","to write","쓰다",
  "'쓰다'는 글씨를 적는 거예요. 노트에 써요.",
  "'쓰다' means to write. Write it in your notebook.",
  DESK_F,[("write_note_a",470,470,0.2),("write_note",470,470,0.8)]),
 ("점심을 먹다","to eat lunch","점심을 먹다",
  "'점심을 먹다.' 바다를 보면서 점심을 먹어요. 최고예요!",
  "'점심을 먹다' (to eat lunch). Eating lunch with a sea view — the best!",
  BTBL_F,[("eat_sit",470,470,1.0)]),
 ("구름을 봐요","Look at the clouds","구름",
  "잠깐! 하늘 좀 보세요. 구름이 정말 예뻐요.",
  "Wait — look at the sky! '구름' (clouds). They are beautiful.",
  BTBL_F,[("look_cloud",470,470,1.0)]),   # ★구름 보기(캐릭터성), 한 씬 통째로

 # ── 4막 오후: 쉬다·산책·수영 (S25~S32) ──
 ("쉬다","to rest","쉬다",
  "'쉬다'는 일을 멈추고 편히 있는 거예요. 잠깐 쉬어요.",
  "'쉬다' means to rest — to stop working and relax.",
  BEACH,[("rest_sit",470,470,1.0)]),
 ("-고 나서","after doing","-고 나서",
  "일하고 나서 쉬어요. '-고 나서'는 순서를 나타내요.",
  "'일하고 나서 쉬어요' (I rest after working). '-고 나서' shows the order of actions.",
  BEACH,[("presenting_a",300,300,0.2),("presenting",300,300,0.8)]),
 ("산책하다","to take a walk","산책하다",
  "'산책하다'는 천천히 걷는 거예요. 바닷가를 산책해요.",
  "'산책하다' — to take a leisurely walk. Let's walk along the beach.",
  BWALK,[("walk_right1",250,350,0.5),("walk_right2",350,450,0.5)]),
 ("해변을 걸어요","I walk on the beach","해변을 / 걸어요",
  "'해변을 걸어요.' 협재의 하얀 모래가 정말 부드러워요.",
  "'해변을 걸어요' (I walk on the beach). The white sand at Hyeopjae is so soft.",
  BWALK,[("walk_right2",250,380,0.5),("walk_right1",380,500,0.5)]),
 ("수영하다","to swim","수영하다",
  "'수영하다.' 에메랄드빛 바다에서 수영해요!",
  "'수영하다' (to swim). Let's swim in the emerald water!",
  SEA,[("swim",300,300,1.0)]),
 ("사진을 찍다","to take a photo","사진을 / 찍다",
  "'사진을 찍다.' 저기 비양도를 배경으로 한 장!",
  "'사진을 찍다' (to take a photo). One shot with Biyangdo Island behind us!",
  SEA2,[("photo_a",300,300,0.2),("photo",300,300,0.8)]),
 ("재미있어요","It's fun","재미있어요",
  "'재미있어요!' 정말 즐거운 하루예요.",
  "'재미있어요!' (It's fun!). What a great day.",
  SEA2,[("cheering_a",300,300,0.25),("cheering",300,300,0.75)]),   # ★환호, 길게
 ("피곤해요","I'm tired","피곤해요",
  "많이 놀았더니 '피곤해요.' 몸이 지쳤어요.",
  "After all that play — '피곤해요' (I'm tired).",
  SUNB,[("tired_a",300,300,0.25),("tired",300,300,0.75)]),         # ★지침, 길게

 # ── 5막 저녁 (S33~S39) ──
 ("저녁을 먹다","to eat dinner","저녁을 먹다",
  "'저녁을 먹다.' 하루의 마지막 식사예요.",
  "'저녁을 먹다' (to eat dinner) — the last meal of the day.",
  DIN,[("eat_sit",470,470,1.0)]),
 ("-기 전에","before doing","-기 전에",
  "'자기 전에 씻어요.' '-기 전에'는 그 일보다 먼저 하는 걸 말해요.",
  "'자기 전에 씻어요' (I wash before sleeping). '-기 전에' = before doing something.",
  DIN,[("presenting_a",470,470,0.2),("presenting",470,470,0.8)]),
 ("-ㄴ 후에","after doing","-ㄴ 후에",
  "'저녁을 먹은 후에 산책해요.' '-ㄴ 후에'는 그 일 다음이에요.",
  "'저녁을 먹은 후에 산책해요' (I walk after dinner). '-ㄴ 후에' = after doing something.",
  DIN,[("presenting",470,470,0.5),("nod",470,470,0.5)]),
 ("전화하다","to make a call","전화하다",
  "'전화하다.' 가족에게 전화해요. 오늘 하루를 이야기해요.",
  "'전화하다' (to call). Call your family and tell them about your day.",
  TERR,[("phone_a",300,300,0.2),("phone",300,300,0.8)]),
 ("텔레비전을 보다","to watch TV","텔레비전을 / 보다",
  "'보다'는 눈으로 보는 거예요. 텔레비전을 봐요.",
  "'보다' means to watch/see. 텔레비전을 봐요 (I watch TV).",
  TVROOM,[("watch_tv",470,470,1.0)]),
 ("노을을 보다","to watch the sunset","노을을 / 보다",
  "'노을을 보다.' 협재의 노을은 정말 아름다워요.",
  "'노을을 보다' (to watch the sunset). The sunset at Hyeopjae is stunning.",
  SUN,[("watch_sunset_a",300,300,0.2),("watch_sunset",300,300,0.8)]),   # ★노을(캐릭터성), 길게
 ("아름다워요","It's beautiful","아름다워요",
  "'아름다워요.' 이 말이 저절로 나와요. 하늘이 온통 주황색이에요.",
  "'아름다워요' (It's beautiful). The whole sky turns orange.",
  SUN,[("watch_sunset",300,300,0.6),("smile_big",300,300,0.4)]),

 # ── 6막 밤: 자다 (S40~S46) ──
 ("샤워하다","to take a shower","샤워하다",
  "'샤워하다.' 자기 전에 깨끗이 씻어요.",
  "'샤워하다' (to take a shower). Wash up before bed.",
  BATHN,[("shower",300,300,1.0)]),
 ("일기를 쓰다","to write a diary","일기를 / 쓰다",
  "'일기를 쓰다.' 오늘 하루를 적어요. 좋은 습관이에요.",
  "'일기를 쓰다' (to write a diary). Write about your day — a great habit.",
  NDSK_F,[("write_diary",470,470,1.0)]),
 ("별을 봐요","Look at the stars","별",
  "잠깐! 창밖에 별이 가득해요.",
  "Wait — the sky is full of '별' (stars)!",
  NIGHT,[("stargaze_a",300,300,0.2),("stargaze",300,300,0.8)]),      # ★별 보기(캐릭터성), 길게
 ("모래에 앉아서","Sitting on the sand","모래에 앉아서",
  "모래에 앉아서 별을 봐요. 오늘 하루가 참 좋았어요.",
  "Sitting on the '모래' (sand), watching the stars. What a lovely day it's been.",
  NIGHT,[("sit_stargaze",470,470,1.0)]),                             # ★앉아서 별 보기
 ("자다","to sleep","자다",
  "핵심 단어! '자다'. 하루의 끝이에요.",
  "Key word! '자다' — to sleep. The end of the day.",
  BEDNOBED,[("sleep",560,560,1.0)]),
 ("열한 시에 자요","I sleep at eleven","열한 시에 / 자요",
  "'열한 시에 자요.' 시간 + 자다. 이제 하루가 끝났어요.",
  "'열한 시에 자요' (I sleep at eleven). Time + 자다. The day is done.",
  BEDNOBED,[("sleep",560,560,1.0)]),
 ("여러분의 하루는요?","How about your day?","여러분의 하루는 / 어때요?",
  "오늘 배운 걸 정리해요. 일어나다, 일하다, 공부하다, 자다. 여러분의 하루는 어때요? 댓글로 알려주세요. 잘 자요!",
  "Let's review: 일어나다 (wake up), 일하다 (work), 공부하다 (study), 자다 (sleep). How about your day? Tell us in the comments. Good night!",
  NIGHT,[("presenting_a",300,300,0.12),("presenting",300,300,0.33),
         ("wave_a",300,300,0.1),("wave",300,300,0.25),("bow",300,300,0.2)]),
]

def make_glyph(gl, path):
    lines = wrap_write(gl, 7)
    f = ImageFont.truetype(FONT, 150)
    W = max(int(f.getlength(l)) for l in lines) + 40
    H = int(len(lines) * 150 * 1.2) + 40
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((20, 20 + i * int(150 * 1.2)), l, font=f, fill=(30, 30, 30, 255))
    bb = im.getbbox(); im = im.crop(bb) if bb else im
    os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path)

con = sqlite3.connect(DB); cur = con.cursor()
BASEP = "assets/graphics/poses/mj_w14_base.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r: MJ = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("마담제이W14base", "mj_w14_base", "pose", BASEP, "W14 base")); MJ = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'mjw14_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

for i, (ck, ce, gl, sk, se, bg, beats) in enumerate(SC, 1):
    sk = norm_quotes(sk); se = norm_quotes(se)
    rel = f"graphics/letters/w14_{i:02d}.png"; make_glyph(gl, f"assets/{rel}")
    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
    if r: gasset = r[0]
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (f"W14글자_{gl[:8]}", f"w14_{i:02d}", "letter", rel, "동동")); gasset = cur.lastrowid
    aseq = f"mjw14_s{i:02d}"
    GCX = 560; WB = 1265 - GCX; HB = 340; CAP = 150
    best = None
    for _mc in range(4, 17):
        _ls = wrap_write(gl, _mc); _nl = len(_ls); _mx = max(len(l) for l in _ls)
        _f = min(WB / (_mx * 0.98), HB / (_nl * 1.18), CAP)
        if best is None or _f > best[0]: best = (_f, _ls, _nl)
    size_px, lines, nlines = best; size_px = max(52, size_px)
    draw_text = "\n".join(lines)
    gscale = round(size_px / 200, 3); blockH = nlines * size_px * 1.18; gcy = int(28 + blockH / 2)
    spec = {"cap_ko": ck, "cap_en": ce, "motion": "static", "char_key": "madam_j_w14", "char_mode": "teacher",
            "draw_font": "cafe24_dongdong", "draw_dur": 3.0, "draw_text": draw_text, "draw_align": "left",
            "bg": bg, "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) VALUES (?,?,?,?,?,?,?)",
                (EP, i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                (EP, i, gasset, GCX, gcy, gscale, 3, "write", 0))
    # ★누운 포즈(sleep)=길이 기준 커스텀 배치 / 앉기=고정(0.946,470,700) / 서기=(0.655,300,452)
    # ★W11 규격: 포즈 PNG가 이미 바닥(y700) 정규화돼 있으므로 좌표는 전부 동일
    ccx, ccy, csc = CHAR_CX, CHAR_CY, CHAR_SCALE
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                (EP, i, MJ, ccx, ccy, csc, 5, "gesture", 0))
    bj = [{"name": p, "cycle": [p], "x_from": xf, "x_to": xt, "dur": d} for (p, xf, xt, d) in beats]
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols: fields["description"] = f"마담제이 W14 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
bgs = sorted({s[5] for s in SC}); poses = sorted({b[0] for s in SC for b in s[6]})
beats_total = sum(len(s[6]) for s in SC)
con.close()
print(f"완료: {EP} {n}씬 (~8분, 마담제이, 협재해수욕장)")
print(f"배경 {len(bgs)}종 / 포즈 {len(poses)}종 / 총 비트 {beats_total}개 (씬당 {beats_total/n:.1f})")
