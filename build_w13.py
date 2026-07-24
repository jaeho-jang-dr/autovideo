# -*- coding: utf-8 -*-
"""W13(길 찾기·위치 안내) 44씬 ~8분: 지은(리디자인 B), 성산일출봉.
★중간 포즈(_a)와 걷기 2프레임을 써서 동작이 자연스럽게 이어지게 beats를 세밀하게 구성."""
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
PLACE = "Seongsan Ilchulbong, Jeju"
EP = "KO-W13"

CO, FK, V1, V2, V3 = "bg_w13_coast", "bg_w13_fork", "bg_w13_village", "bg_w13_village2", "bg_w13_village3"
ST, CR, CN, JU, SR = "bg_w13_street", "bg_w13_crossing", "bg_w13_corner", "bg_w13_junction", "bg_w13_store"
FL, FL2, TK, EN = "bg_w13_field", "bg_w13_field2", "bg_w13_ticket", "bg_w13_entrance"
SA, SA2, SU, SU2 = "bg_w13_stairs", "bg_w13_stairs2", "bg_w13_summit", "bg_w13_summit2"
DH, SN = "bg_w13_downhill", "bg_w13_sunrise"

# (cap_ko, cap_en, glyph, script_kr, script_en, bg, beats[(pose, x_from, x_to, ratio)])
# ★beats에 중간 포즈(_a)를 넣어 동작 전환이 뚝 끊기지 않게 함. 걷기는 walk_*1/2 교대.
SC = [
 # ---- 1막 성산 도착 (S1~S6) ----
 ("성산일출봉에 왔어요!","At Seongsan Ilchulbong!","성산일출봉",
  "안녕하세요! 지난 시간에는 지하철과 버스를 배웠죠. 이제 목적지에 왔는데, 길을 못 찾으면 어떻게 하죠? 오늘은 제주 성산일출봉에서 길 찾기를 배워요!",
  "Hello! Last time we learned the subway and buses. But once you arrive, what if you can't find the way? Today we learn how to find your way, here at Seongsan Ilchulbong in Jeju!",
  CO,[("walk_right1",-120,180,0.25),("walk_right2",180,300,0.25),("presenting_a",300,300,0.15),("presenting",300,300,0.35)]),
 ("여기가 어디예요?","Where am I?","여기가 어디예요",
  "낯선 곳에 오면 제일 먼저 드는 생각. '여기가 어디예요?' 위치를 물을 때 쓰는 가장 기본 문장이에요.",
  "The first thought in an unfamiliar place: '여기가 어디예요?' (Where am I?). The most basic phrase for asking where you are.",
  CO,[("look_around",300,300,0.5),("speak_a",300,300,0.1),("speak",300,300,0.4)]),
 ("길을 잃었어요","I'm lost","길을 잃었어요",
  "지도를 봐도 모르겠어요. 이럴 때 '길을 잃었어요' 라고 해요. 걱정 마세요, 물어보면 되니까요!",
  "Even with a map, you're not sure. Then you say '길을 잃었어요' (I'm lost). Don't worry — just ask!",
  FK,[("map_look",300,300,0.30),("surprise_a",300,300,0.12),("surprise",300,300,0.23),
      ("walk_left1",300,250,0.175),("walk_left2",250,200,0.175)]),   # ★길 잘못 들어 왼쪽으로 되돌아감
 ("길","road, way","길",
  "'길'은 도로, 또는 가는 방향을 말해요. 길을 잃다, 길을 묻다, 길을 건너다. 오늘의 중심 단어예요.",
  "'길' means a road or a way. 길을 잃다 (get lost), 길을 묻다 (ask the way), 길을 건너다 (cross the road). Today's core word.",
  FK,[("presenting_a",300,300,0.2),("presenting",300,300,0.8)]),
 ("실례합니다","Excuse me","실례합니다",
  "모르는 사람에게 말을 걸 때는 '실례합니다' 로 시작해요. 이 한마디면 상대가 기분 좋게 들어줘요.",
  "To approach a stranger, start with '실례합니다' (Excuse me). This one word makes people happy to help.",
  FK,[("greeting",300,300,1.0)]),
 ("길 좀 물어봐도 돼요?","May I ask for directions?","길 좀 / 물어봐도 / 돼요?",
  "'길 좀 물어봐도 돼요?' 정중하게 물으면 한국 사람들은 아주 친절하게 알려줘요.",
  "'길 좀 물어봐도 돼요?' (May I ask for directions?). Ask politely and Koreans will gladly help you.",
  FK,[("speak_a",300,300,0.15),("speak",300,300,0.85)]),

 # ---- 2막 길 묻기 · 오른쪽/왼쪽 (S7~S14) ----
 ("어떻게 가요?","How do I get there?","어떻게 가요",
  "지난 시간에 배운 만능 문장이 또 나와요. '어떻게 가요?' 어디를 가든 이 문장 하나면 돼요.",
  "The magic phrase from last lesson returns: '어떻게 가요?' (How do I get there?). It works anywhere.",
  FK,[("speak",300,300,1.0)]),
 ("성산일출봉 어떻게 가요?","How do I get to Ilchulbong?","어떻게 가요",
  "가고 싶은 곳 이름을 넣어요. '성산일출봉 어떻게 가요?' 목적지만 바꾸면 어디서든 쓸 수 있어요.",
  "Add your destination: '성산일출봉 어떻게 가요?' Just swap the place name and it works anywhere.",
  V1,[("speak",280,280,0.6),("nod",280,280,0.4)]),
 ("오른쪽","right","오른쪽",
  "오늘의 핵심 단어! '오른쪽'. 이 손 방향이 오른쪽이에요. 길 안내에서 제일 많이 나와요.",
  "Today's key word: '오른쪽' — right. This direction is 오른쪽. It comes up constantly in directions.",
  V1,[("point_right_a",280,280,0.2),("point_right",280,280,0.8)]),
 ("왼쪽","left","왼쪽",
  "반대는 '왼쪽'. 오른쪽, 왼쪽. 짝으로 외우면 절대 안 헷갈려요.",
  "The opposite is '왼쪽' — left. 오른쪽 / 왼쪽. Learn them as a pair and you won't mix them up.",
  V2,[("point_left_a",280,280,0.2),("point_left",280,280,0.8)]),
 ("오른쪽으로 가세요","Go to the right","오른쪽으로",
  "'-으로'는 방향을 나타내요. '오른쪽으로 가세요.' '왼쪽으로 가세요.' 이렇게 안내를 받아요.",
  "'-으로' marks direction. '오른쪽으로 가세요' (Go right). '왼쪽으로 가세요' (Go left). That's how you'll be guided.",
  V2,[("point_right_a",280,280,0.15),("point_right",280,280,0.85)]),
 ("문제 발생!","A problem!","못 알아들었어요",
  "그런데 문제! 너무 빨리 말해서 못 알아들었어요. 이럴 때 그냥 넘어가면 또 길을 잃어요.",
  "But a problem! They spoke too fast and you didn't catch it. If you just nod and go, you'll get lost again.",
  V2,[("thinking_a",280,280,0.2),("thinking",280,280,0.8)]),
 ("다시 말해 주세요","Please say that again","다시 말해 주세요",
  "부끄러워하지 마세요! '다시 말해 주세요.' 이 문장이 오늘의 생명줄이에요.",
  "Don't be shy! '다시 말해 주세요' (Please say that again). This phrase is your lifeline today.",
  V3,[("speak_a",280,280,0.15),("speak",280,280,0.85)]),
 ("천천히 말해 주세요","Please speak slowly","천천히 / 말해 주세요",
  "더 좋은 문장! '천천히 말해 주세요.' 그러면 아주 천천히 또박또박 말해 줘요.",
  "Even better: '천천히 말해 주세요' (Please speak slowly). Then they'll speak nice and slow for you.",
  V3,[("speak",280,280,0.5),("listen",280,280,0.5)]),

 # ---- 3막 안내 듣기 · 똑바로/건너다 (S15~S24) ----
 ("똑바로 가세요","Go straight","똑바로 / 가세요",
  "핵심 단어! '똑바로'. 방향을 바꾸지 않고 앞으로 곧장 가는 거예요. '똑바로 가세요.'",
  "Key word! '똑바로' — straight. Keep going forward without turning. '똑바로 가세요' (Go straight).",
  ST,[("point_up_a",280,280,0.2),("point_up",280,280,0.8)]),
 ("쭉 가세요","Keep going straight","쭉 가세요",
  "'쭉 가세요'도 같은 뜻이에요. 실제로는 이 말을 더 많이 들어요.",
  "'쭉 가세요' means the same. In real life you'll hear this one even more often.",
  ST,[("point_forward",280,280,0.35),("walk_right1",280,380,0.3),("walk_right2",380,480,0.35)]),
 ("건너다","to cross","건너다",
  "핵심 단어! '건너다'. 길이나 다리의 반대편으로 가는 거예요.",
  "Key word! '건너다' — to cross. To go to the other side of a road or bridge.",
  CR,[("presenting_a",280,280,0.2),("presenting",280,280,0.8)]),
 ("길을 건너세요","Cross the road","길을 건너세요",
  "'길을 건너세요.' 횡단보도에서 초록불을 기다렸다가 건너요.",
  "'길을 건너세요' (Cross the road). Wait for the green light at the crosswalk, then cross.",
  CR,[("point_right",280,280,0.3),("walk_right1",280,400,0.35),("walk_right2",400,520,0.35)]),
 ("돌다","to turn","돌다",
  "'돌다'는 방향을 바꾸는 거예요. 모퉁이에서 방향을 트는 것.",
  "'돌다' means to turn — to change direction, like at a corner.",
  CN,[("turn_side",280,280,0.4),("point_right",280,280,0.6)]),
 ("오른쪽으로 도세요","Turn right","오른쪽으로 도세요",
  "'오른쪽으로 도세요.' 이제 방향 단어와 동사를 합쳐서 완전한 안내가 돼요.",
  "'오른쪽으로 도세요' (Turn right). Now you can combine direction words with verbs for full directions.",
  CN,[("point_right_a",280,280,0.15),("point_right",280,280,0.85)]),
 ("사거리","intersection","사거리",
  "'사거리'는 길이 넷으로 갈라지는 곳이에요. 길 안내의 기준점이 돼요.",
  "'사거리' is an intersection where four roads meet. It's a key landmark in directions.",
  JU,[("look_around",280,280,1.0)]),
 ("신호등","traffic light","신호등",
  "'신호등'도 좋은 기준점이에요. '신호등에서 왼쪽으로 가세요.' 이렇게 말해요.",
  "'신호등' (traffic light) is another great landmark. '신호등에서 왼쪽으로 가세요' — Turn left at the light.",
  JU,[("point_up_a",280,280,0.2),("point_up",280,280,0.8)]),
 ("편의점에서 오른쪽","Right at the store","편의점에서 / 오른쪽으로 / 가세요",
  "건물을 기준으로도 말해요. '편의점에서 오른쪽으로 가세요.' 실전에서 가장 많이 듣는 방식이에요.",
  "People also use buildings: '편의점에서 오른쪽으로 가세요' (Turn right at the convenience store). You'll hear this a lot.",
  SR,[("point_right_a",280,280,0.15),("point_right",280,280,0.85)]),
 ("알겠어요!","I got it!","알겠어요 / 감사합니다",
  "이해했으면 '알겠어요!' 라고 답해요. 고맙다는 인사도 잊지 마세요. '감사합니다!'",
  "When you understand, say '알겠어요!' (I got it!). And don't forget to say thank you — '감사합니다!'",
  SR,[("nod",280,280,0.5),("greeting",280,280,0.5)]),

 # ---- 4막 거리·위치 표현 (S25~S32) ----
 ("얼마나 멀어요?","How far is it?","얼마나 멀어요",
  "거리도 물어봐야죠. '얼마나 멀어요?' 걸어갈 수 있는지 알 수 있어요.",
  "You should also ask the distance: '얼마나 멀어요?' (How far is it?). Then you know if you can walk.",
  FL,[("speak_a",280,280,0.15),("speak",280,280,0.85)]),
 ("가까워요 / 멀어요","near / far","가까워요 멀어요",
  "대답은 둘 중 하나. '가까워요' 아니면 '멀어요'. 짝으로 외워요.",
  "The answer is one of two: '가까워요' (it's near) or '멀어요' (it's far). Learn them as a pair.",
  FL,[("presenting_a",280,280,0.2),("presenting",280,280,0.8)]),
 ("걸어서 10분","10 minutes on foot","걸어서 10분",
  "시간으로도 알려줘요. '걸어서 10분이에요.' 아, 가깝네요!",
  "They may answer with time: '걸어서 10분이에요' (10 minutes on foot). Oh, that's close!",
  FL,[("count_fingers",280,280,1.0)]),
 ("근처 / 이 근처에 / 있어요","nearby","근처",
  "'근처'는 가까운 곳이라는 뜻이에요. '이 근처에 있어요.'",
  "'근처' means nearby. '이 근처에 있어요' — It's near here.",
  FL2,[("look_around",280,280,1.0)]),
 ("앞 · 뒤","front · back","앞 뒤 / 건물 앞에 / 있어요",
  "위치를 말할 때 써요. '앞'은 front, '뒤'는 back. '건물 앞에 있어요.'",
  "For positions: '앞' is front, '뒤' is back. '건물 앞에 있어요' — It's in front of the building.",
  TK,[("point_center",280,280,1.0)]),
 ("옆 · 사이","beside · between","옆 사이 / 편의점 / 옆에 있어요",
  "'옆'은 beside, '사이'는 between. '편의점 옆에 있어요.'",
  "'옆' is beside, '사이' is between. '편의점 옆에 있어요' — It's next to the convenience store.",
  TK,[("point_right",280,280,1.0)]),
 ("매표소 앞에서 만나요","Meet in front of the ticket booth","매표소 앞에서",
  "위치 표현으로 약속도 해요. '매표소 앞에서 만나요.' 아주 유용하죠?",
  "Use position words to make plans: '매표소 앞에서 만나요' (Let's meet in front of the ticket booth).",
  TK,[("speak",280,280,1.0)]),
 ("저기 보여요!","I can see it!","저기 보여요",
  "드디어! 저기 성산일출봉이 보여요. 길을 제대로 찾아왔어요!",
  "Finally! There it is — Seongsan Ilchulbong. We found the way!",
  EN,[("point_up_a",280,280,0.15),("point_up",280,280,0.45),("cheering_a",280,280,0.1),("cheering",280,280,0.3)]),

 # ---- 5막 일출봉 오르기 (S33~S38) ----
 ("올라가다 / 내려가다","to go up","올라가다",
  "이제 정상까지 올라가요. '올라가다'는 위로 가는 거예요. 반대는 '내려가다'.",
  "Now let's go up to the top. '올라가다' means to go up. The opposite is '내려가다' (to go down).",
  SA,[("walk_stairs1",280,300,0.5),("walk_stairs2",300,320,0.5)]),
 ("계단","stairs","계단",
  "성산일출봉은 계단이 아주 많아요. '계단'을 하나씩 올라가요.",
  "Seongsan Ilchulbong has a LOT of stairs. Let's climb them one by one.",
  SA,[("walk_stairs2",300,330,0.5),("walk_stairs1",330,360,0.5)]),
 ("힘들어요","It's tough","힘들어요",
  "솔직히 힘들어요! 이럴 때 '힘들어요' 라고 해요. 잠깐 쉬어 가요.",
  "Honestly, it's tough! You can say '힘들어요' (It's hard). Let's take a short break.",
  SA2,[("tired_a",300,300,0.2),("tired",300,300,0.8)]),
 ("조금만 더","Just a little more","조금만 더",
  "'조금만 더!' 서로 힘을 줄 때 쓰는 말이에요. 거의 다 왔어요!",
  "'조금만 더!' (Just a little more!) — what you say to encourage each other. Almost there!",
  SA2,[("cheering_a",300,300,0.25),("cheering",300,300,0.75)]),
 ("다 왔어요!","We're here!","다 왔어요",
  "해냈어요! '다 왔어요!' 도착했다는 뜻이에요.",
  "We did it! '다 왔어요!' means we've arrived.",
  SU,[("cheering",300,300,1.0)]),
 ("경치가 좋아요","The view is beautiful","경치가 좋아요",
  "와, 분화구와 바다가 한눈에! '경치가 좋아요.' 이 말이 절로 나와요.",
  "Wow — the crater and the sea in one view! '경치가 좋아요' (The view is beautiful). It just comes out naturally.",
  SU,[("presenting_a",300,300,0.15),("presenting",300,300,0.45),
      ("presenting_alt",300,300,0.40)]),   # ★다른 손으로 경치 가리키는 변주(반복 방지)

 # ---- 6막 이번엔 내가 안내 ★역전 (S39~S44) ----
 ("이번엔 내가 안내!","Now I'll give directions!","안내",
  "그런데 이번엔 반대예요! 외국인 관광객이 저에게 길을 물어봐요. 배운 걸 써먹을 시간!",
  "But now it's reversed! A tourist is asking ME for directions. Time to use what we learned!",
  SU2,[("surprise_a",300,300,0.2),("surprise",300,300,0.5),("nod",300,300,0.3)]),
 ("저기로 똑바로 가세요","Go straight that way","똑바로 가세요",
  "자신 있게 말해요. '저기로 똑바로 가세요.' 오늘 배운 '똑바로'를 써요!",
  "Say it with confidence: '저기로 똑바로 가세요' (Go straight that way). Using today's word 똑바로!",
  SU2,[("point_up_a",300,300,0.15),("point_up",300,300,0.85)]),
 ("왼쪽으로 도세요","Turn left","왼쪽으로 도세요",
  "'그리고 왼쪽으로 도세요.' 방향 단어를 자유롭게 쓸 수 있게 됐어요!",
  "'그리고 왼쪽으로 도세요' (Then turn left). Now you can use direction words freely!",
  SU2,[("point_left_a",300,300,0.15),("point_left",300,300,0.85)]),
 ("다리를 건너세요","Cross the bridge","건너세요",
  "'다리를 건너세요.' 완벽해요! 이제 길을 묻는 것도, 안내하는 것도 다 할 수 있어요.",
  "'다리를 건너세요' (Cross the bridge). Perfect! Now you can both ask for AND give directions.",
  DH,[("point_right_a",300,300,0.15),("point_right",300,300,0.85)]),
 ("오늘의 표현","Today's phrases","오른쪽 왼쪽 / 똑바로 건너다 / 다시 말해 주세요",
  "오늘 배운 걸 정리해요. 오른쪽, 왼쪽, 똑바로, 건너다. 그리고 '다시 말해 주세요'. 이거면 어디서도 길을 잃지 않아요!",
  "Let's review: 오른쪽 (right), 왼쪽 (left), 똑바로 (straight), 건너다 (cross). And '다시 말해 주세요'. You'll never be lost again!",
  SN,[("presenting_a",300,300,0.15),("presenting",300,300,0.85)]),
 ("다음 시간에","See you next time","또 만나요",
  "성산일출봉의 일출이 정말 아름답죠? 오늘도 수고했어요. 다음 시간에 또 만나요!",
  "Isn't the sunrise at Seongsan beautiful? Great work today. See you next time!",
  SN,[("wave_hello_a",300,300,0.15),("wave_hello",300,300,0.45),("bow",300,300,0.4)]),
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
    return lines

con = sqlite3.connect(DB); cur = con.cursor()
BASEP = "assets/graphics/poses/jieun_w13_base.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r: JIEUN = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("지은W13base", "jieun_w13_base", "pose", BASEP, "W13 base")); JIEUN = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'jew13_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

for i, (ck, ce, gl, sk, se, bg, beats) in enumerate(SC, 1):
    sk = norm_quotes(sk); se = norm_quotes(se)
    rel = f"graphics/letters/w13_{i:02d}.png"; make_glyph(gl, f"assets/{rel}")
    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
    if r: gasset = r[0]
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (f"W13글자_{gl[:8]}", f"w13_{i:02d}", "letter", rel, "동동")); gasset = cur.lastrowid
    aseq = f"jew13_s{i:02d}"
    GCX = 560; WB = 1265 - GCX; HB = 340; CAP = 150
    best = None
    for _mc in range(4, 17):
        _ls = wrap_write(gl, _mc); _nl = len(_ls); _mx = max(len(l) for l in _ls)
        _f = min(WB / (_mx * 0.98), HB / (_nl * 1.18), CAP)
        if best is None or _f > best[0]: best = (_f, _ls, _nl)
    size_px, lines, nlines = best; size_px = max(52, size_px)
    draw_text = "\n".join(lines)
    gscale = round(size_px / 200, 3); blockH = nlines * size_px * 1.18; gcy = int(28 + blockH / 2)
    spec = {"cap_ko": ck, "cap_en": ce, "motion": "static", "char_key": "jieun_w13", "char_mode": "teacher",
            "draw_font": "cafe24_dongdong", "draw_dur": 3.0, "draw_text": draw_text, "draw_align": "left",
            "bg": bg, "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) VALUES (?,?,?,?,?,?,?)",
                (EP, i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                (EP, i, gasset, GCX, gcy, gscale, 3, "write", 0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                (EP, i, JIEUN, 300, 452, 0.655, 5, "gesture", 0))   # ★크기 40%(W12 확정값)
    bj = [{"name": p, "cycle": [p], "x_from": xf, "x_to": xt, "dur": d} for (p, xf, xt, d) in beats]
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols: fields["description"] = f"지은 W13 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
bgs = sorted({s[5] for s in SC}); poses = sorted({b[0] for s in SC for b in s[6]})
beats_total = sum(len(s[6]) for s in SC)
con.close()
print(f"완료: {EP} {n}씬 (~8분, 지은, 성산일출봉)")
print(f"배경 {len(bgs)}종 / 포즈 {len(poses)}종 / 총 비트 {beats_total}개 (씬당 평균 {beats_total/n:.1f})")
print(f"포즈: {', '.join(poses)}")
