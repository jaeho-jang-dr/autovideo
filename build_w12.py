# -*- coding: utf-8 -*-
"""W12(교통·지하철 환승) 44씬 ~8분: 인준(injun_w12), 인천공항→강남역 여정. 배경 22종(2씬당 1개).
캐릭터 왼쪽/글자 오른쪽. 관광가이드 톤. 커리큘럼 핵심어: 버스·지하철·타다·환승."""
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
PLACE = "Incheon Airport → Gangnam, Seoul"
EP = "KO-W12"

# 배경 키 (22종)
AR, HA, SB, BS = "bg_w12_arrival", "bg_w12_hall", "bg_w12_signboard", "bg_w12_busstop"
TK, CH, CO, GA = "bg_w12_ticket", "bg_w12_charge", "bg_w12_counter", "bg_w12_gate"
PL, PL2, BO, TR = "bg_w12_platform", "bg_w12_platform2", "bg_w12_boarding", "bg_w12_train"
SS, TF, TF2, MP = "bg_w12_seoulstn", "bg_w12_transfer", "bg_w12_transfer2", "bg_w12_map"
MP2, ST, PL3, TR2 = "bg_w12_map2", "bg_w12_sign_transfer", "bg_w12_platform_line2", "bg_w12_train2"
GX, GS, GN = "bg_w12_gangnam_exit", "bg_w12_gangnam_street", "bg_w12_gangnam_night"

# (cap_ko, cap_en, glyph, script_kr, script_en, bg, beats[(pose, x_from, x_to, ratio)])
SC = [
 # ---- 1막 인천공항 도착 (S1~S5) ----
 ("인천공항 도착!","Arrived at Incheon!","인천공항",
  "안녕하세요! 오늘은 제가 여러분의 가이드예요. 인천공항에서 강남역까지 같이 가 봐요. 버스도 타고, 지하철도 타고, 환승도 해요. 이 영상 하나면 서울에서 길 잃지 않아요!",
  "Hello! Today I'm your guide. Let's travel together from Incheon Airport to Gangnam Station. We'll take a bus, ride the subway, and transfer. After this video, you won't get lost in Seoul!",
  AR,[("pull_suitcase",-120,300,0.5),("presenting",300,300,0.5)]),
 ("어떻게 가요?","How do I get there?","어떻게 가요",
  "공항에 내리면 제일 먼저 드는 생각. '서울까지 어떻게 가지?' 이럴 때 쓰는 만능 문장이 있어요. '어떻게 가요?' 이 한마디면 됩니다.",
  "The first thought when you land: 'How do I get to Seoul?' There's one magic phrase for this: '어떻게 가요?' — How do I get there?",
  AR,[("thinking",300,300,0.5),("speak",300,300,0.5)]),
 ("서울까지 어떻게 가요?","How do I get to Seoul?","서울까지",
  "목적지를 넣어서 말해 봐요. '서울까지 어떻게 가요?' '까지'는 목적지를 나타내요. '강남역까지 어떻게 가요?' 이렇게 바꿔 쓸 수 있어요.",
  "Add your destination: '서울까지 어떻게 가요?' The word '까지' marks the destination. You can swap it: '강남역까지 어떻게 가요?'",
  HA,[("speak",300,300,0.6),("nod",300,300,0.4)]),
 ("타다","to ride / to take","타다",
  "오늘의 핵심 동사예요. '타다'. 버스를 타요. 지하철을 타요. 택시를 타요. 무엇이든 이 동사 하나면 돼요.",
  "Today's key verb: '타다' — to ride, to take. 버스를 타요 (take a bus). 지하철을 타요 (take the subway). One verb covers them all.",
  HA,[("presenting",300,300,1.0)]),
 ("두 가지 방법","Two ways","버스 지하철",
  "공항에서 서울 가는 방법은 크게 두 가지예요. 버스와 지하철. 오늘은 둘 다 배워요.",
  "There are two main ways from the airport to Seoul: bus and subway. Today we'll learn both.",
  SB,[("look_up_sign",300,300,0.5),("point_up",300,300,0.5)]),

 # ---- 2막 공항버스 (S6~S12) ----
 ("버스","bus","버스",
  "먼저 버스예요. 공항버스는 짐이 많을 때 아주 편해요. 앉아서 편하게 갈 수 있고, 짐은 버스 아래 짐칸에 넣어요.",
  "First, the bus. The airport bus is great when you have luggage. You sit comfortably, and your bags go in the compartment below.",
  SB,[("point_right",300,300,0.5),("presenting",300,300,0.5)]),
 ("버스 정류장","bus stop","정류장",
  "버스를 타는 곳은 '정류장'이라고 해요. 공항 밖으로 나가면 버스 정류장이 있어요. '버스 정류장이 어디예요?' 하고 물어보세요.",
  "The place you catch a bus is '정류장' (bus stop). Just outside the airport you'll find them. Ask: '버스 정류장이 어디예요?'",
  BS,[("look_up_sign",280,280,0.5),("speak",280,280,0.5)]),
 ("몇 번 버스예요?","Which bus number?","몇 번 버스",
  "한국 버스는 번호로 구분해요. 그래서 이렇게 물어요. '몇 번 버스예요?' 번호만 알면 어디든 갈 수 있어요.",
  "Korean buses are identified by number. So you ask: '몇 번 버스예요?' (Which bus number?). Know the number, and you can go anywhere.",
  BS,[("speak",280,280,0.5),("count_fingers",280,280,0.5)]),
 ("얼마나 걸려요?","How long does it take?","얼마나 걸려요",
  "시간이 궁금하면 '얼마나 걸려요?' 하고 물어요. 버스는 길이 막히면 늦을 수 있어요. 그래서 시간을 꼭 물어보세요.",
  "To ask about time: '얼마나 걸려요?' (How long does it take?). Buses can be delayed by traffic, so always ask.",
  BS,[("thinking",280,280,0.5),("speak",280,280,0.5)]),
 ("요금이 얼마예요?","How much is the fare?","요금",
  "돈은 '요금'이라고 해요. '요금이 얼마예요?' 하고 물어요. 공항버스는 지하철보다 조금 비싸요.",
  "The fare is '요금'. Ask: '요금이 얼마예요?' (How much is the fare?). The airport bus costs a bit more than the subway.",
  BS,[("hold_cash",280,280,1.0)]),
 ("지하철이 더 빨라요","The subway is faster","빨라요",
  "그런데 오늘은 지하철로 가요. 왜냐하면 지하철은 길이 막히지 않아서 시간이 정확해요. '빨라요'는 시간이 적게 걸린다는 뜻이에요.",
  "But today we'll take the subway. Why? It never gets stuck in traffic, so the time is exact. '빨라요' means fast.",
  SB,[("thumbs_up",300,300,1.0)]),
 ("지하철로 가요","Let's take the subway","지하철",
  "'지하철'. 땅 아래로 다니는 기차예요. 공항에서 타는 지하철을 공항철도라고 해요. 자, 타러 가요!",
  "'지하철' — the subway, a train that runs underground. The one from the airport is called the Airport Railroad. Let's go!",
  SB,[("presenting",300,300,0.4),("walk_right",300,420,0.6)]),

 # ---- 3막 교통카드 (S13~S18) ----
 ("문제 발생!","A problem!","교통카드",
  "그런데 문제가 생겼어요! 지하철을 타려면 카드가 필요해요. 카드가 없으면 탈 수 없어요. 이 카드를 '교통카드'라고 해요.",
  "But there's a problem! To ride, you need a card. Without it you can't get in. This card is called '교통카드' (transit card).",
  TK,[("surprise",300,300,1.0)]),
 ("교통카드 주세요","A transit card, please","교통카드 주세요",
  "걱정 마세요. 편의점이나 판매기에서 살 수 있어요. '교통카드 주세요.' 이 한마디면 됩니다. '주세요'는 정중한 부탁이에요.",
  "Don't worry — you can buy one at a convenience store or machine. Just say: '교통카드 주세요' (A transit card, please).",
  TK,[("speak",300,300,1.0)]),
 ("충전","to charge / top up","충전",
  "카드를 샀으면 돈을 넣어야 해요. 이걸 '충전'이라고 해요. 카드에 돈을 채우는 거예요.",
  "Once you have the card, you must put money in. That's '충전' — to top up, to charge the card.",
  CH,[("point_center",300,300,1.0)]),
 ("만 원 충전해 주세요","Please top up 10,000 won","만 원 충전",
  "금액을 넣어서 말해요. '만 원 충전해 주세요.' 이 카드 하나로 지하철도 타고 버스도 타요. 아주 편해요.",
  "Say it with an amount: '만 원 충전해 주세요' (Please top up 10,000 won). One card works for both subway and bus. Very handy.",
  CO,[("hold_cash",300,300,1.0)]),
 ("카드를 대세요","Tap your card","대세요",
  "이제 개찰구예요. 카드를 단말기에 살짝 대요. 이걸 '대다'라고 해요. '카드를 대세요.'",
  "Now the gate. Lightly touch your card to the reader. That's '대다' — to tap. '카드를 대세요' (Tap your card).",
  GA,[("tap_card",300,300,1.0)]),
 ("삑! 통과","Beep! You're through","통과",
  "'삑!' 소리가 나면 통과예요. 문이 열려요. 성공! 이제 승강장으로 내려가요.",
  "'Beep!' — and you're through. The gate opens. Success! Now down to the platform.",
  GA,[("cheering",300,300,0.5),("walk_right",300,420,0.5)]),

 # ---- 4막 공항철도 (S19~S26) ----
 ("어느 쪽이에요?","Which way?","어느 쪽",
  "승강장에 오면 또 고민이 생겨요. 방향이 두 개예요. 왼쪽? 오른쪽? 어느 쪽으로 가야 할까요?",
  "On the platform, another puzzle: there are two directions. Left? Right? Which way do we go?",
  PL,[("look_around",300,300,1.0)]),
 ("문제 발생!","A problem!","반대 방향",
  "여기서 실수하는 사람이 정말 많아요. 반대 방향으로 타면 어떻게 될까요? 다시 돌아와야 해요. 시간을 많이 버려요.",
  "So many travelers make a mistake here. Take the wrong direction and you have to come all the way back. A big waste of time.",
  PL,[("surprise",300,300,1.0)]),
 ("~행","bound for ~","서울역행",
  "열차에는 '행'이 붙어요. '서울역행'은 서울역으로 가는 열차라는 뜻이에요. 가고 싶은 곳 이름을 찾아보세요.",
  "Trains are marked with '행' (bound for). '서울역행' means the train bound for Seoul Station. Look for your destination.",
  PL2,[("look_up_sign",300,300,1.0)]),
 ("이거 서울역 가요?","Does this go to Seoul Station?","서울역 가요",
  "그래도 헷갈리면 물어보세요. '이거 서울역 가요?' 이 문장이 오늘의 생명줄이에요. 한국 사람들은 친절하게 알려줘요.",
  "Still unsure? Just ask: '이거 서울역 가요?' (Does this go to Seoul Station?). This phrase is your lifeline — Koreans will gladly help.",
  PL2,[("speak",300,300,1.0)]),
 ("네, 맞아요","Yes, that's right","맞아요",
  "'네, 맞아요.' 이 대답을 들으면 안심이에요. 반대로 '아니요'라고 하면 반대편으로 가면 돼요.",
  "'네, 맞아요' — Yes, that's right. Now you can relax. If they say '아니요' (no), just go to the other side.",
  PL2,[("nod",300,300,1.0)]),
 ("지하철을 타요","Take the subway","타요",
  "문이 열리면 타요. 내리는 사람이 먼저예요. 다 내린 다음에 타는 게 예의예요.",
  "The doors open — get on. But let people off first; that's the polite way in Korea.",
  BO,[("walk_right",250,420,1.0)]),
 ("손잡이를 잡아요","Hold the strap","손잡이",
  "자리가 없으면 서서 가요. 천장에 있는 '손잡이'를 잡으세요. 열차가 흔들려도 안전해요.",
  "No seat? Stand and hold the '손잡이' (strap) hanging from the ceiling. You'll be steady even when the train rocks.",
  TR,[("hold_strap",300,300,1.0)]),
 ("몇 정거장이에요?","How many stops?","몇 정거장",
  "얼마나 가야 할까요? '몇 정거장이에요?' 하고 물어요. 그리고 안내방송을 잘 들으세요. 다음 역 이름을 말해 줘요.",
  "How far is it? Ask '몇 정거장이에요?' (How many stops?). And listen to the announcements — they call out the next station.",
  TR,[("count_fingers",300,300,0.5),("listen",300,300,0.5)]),

 # ---- 5막 서울역 환승 ★핵심 (S27~S36) ----
 ("서울역 도착","Seoul Station","서울역",
  "서울역에 도착했어요. 그런데 아직 강남역이 아니에요. 여기서 다른 열차로 바꿔 타야 해요.",
  "We've arrived at Seoul Station. But this isn't Gangnam yet — here we must change to a different train.",
  SS,[("walk_right",250,350,1.0)]),
 ("환승","transfer","환승",
  "오늘의 가장 중요한 단어예요. '환승'! 다른 노선으로 갈아타는 것을 환승이라고 해요. 이 단어를 꼭 기억하세요.",
  "Today's most important word: '환승' — transfer. Changing to a different line is called 환승. Remember this one!",
  SS,[("presenting",300,300,1.0)]),
 ("갈아타다","to change trains","갈아타다",
  "'환승하다'와 '갈아타다'는 같은 뜻이에요. '2호선으로 갈아타요.' 둘 다 자주 쓰니까 같이 외우세요.",
  "'환승하다' and '갈아타다' mean the same thing. '2호선으로 갈아타요' (Change to Line 2). Both are common — learn them together.",
  TF,[("speak",300,300,1.0)]),
 ("문제 발생!","A problem!","어디서 갈아타요",
  "환승통로는 정말 커요. 표지판도 많고 사람도 많아요. 어디로 가야 할지 헷갈려요. 그럴 땐 어떻게 할까요?",
  "Transfer corridors are huge — many signs, many people. It's easy to get confused. So what do we do?",
  TF,[("thinking",300,300,1.0)]),
 ("어디서 갈아타요?","Where do I transfer?","어디서",
  "물어보면 돼요! '어디서 갈아타요?' 아주 쉬운 문장이죠. 역무원이나 옆 사람에게 물어보세요.",
  "Just ask! '어디서 갈아타요?' (Where do I transfer?). Ask a station staff member or the person next to you.",
  TF2,[("speak",300,300,1.0)]),
 ("~호선","Line ~","2호선",
  "지하철 노선은 번호로 불러요. 1호선, 2호선, 3호선. '호선'은 노선 번호를 말해요.",
  "Subway lines are called by number: 1호선, 2호선, 3호선 (Line 1, 2, 3). '호선' means the line number.",
  MP,[("point_up",300,300,1.0)]),
 ("2호선으로 갈아타세요","Change to Line 2","2호선",
  "강남역은 2호선에 있어요. 그래서 '2호선으로 갈아타세요.' 우리도 2호선을 찾아가요.",
  "Gangnam Station is on Line 2. So: '2호선으로 갈아타세요' (Change to Line 2). Let's find it.",
  MP,[("point_right",300,300,1.0)]),
 ("초록색 2호선","The green Line 2","초록색",
  "꿀팁이에요! 노선은 색깔이 있어요. 2호선은 초록색이에요. 글자를 못 읽어도 색만 따라가면 돼요.",
  "Here's a tip! Each line has a color. Line 2 is green. Even if you can't read the letters, just follow the color.",
  MP2,[("presenting",300,300,1.0)]),
 ("표지판을 따라가요","Follow the signs","따라가요",
  "이제 초록색 표지판을 따라가요. 화살표가 길을 알려줘요. 표지판만 잘 보면 절대 안 헤매요.",
  "Now follow the green signs. The arrows show the way. Watch the signs and you'll never get lost.",
  ST,[("look_up_sign",250,250,0.4),("walk_right",250,420,0.6)]),
 ("환승 성공!","Transfer complete!","환승 성공",
  "해냈어요! 2호선 승강장에 도착했어요. 이게 바로 환승이에요. 어렵지 않죠?",
  "We did it! We've reached the Line 2 platform. That's what 환승 means. Not so hard, right?",
  PL3,[("cheering",300,300,1.0)]),

 # ---- 6막 강남역 + 시내버스 (S37~S44) ----
 ("강남역으로!","To Gangnam!","강남역",
  "이제 2호선을 타고 강남역으로 가요. 창밖으로 서울 도시가 보여요. 거의 다 왔어요!",
  "Now we ride Line 2 to Gangnam Station. You can see the city through the window. Almost there!",
  TR2,[("hold_strap",300,300,0.5),("presenting",300,300,0.5)]),
 ("내리다","to get off","내리다",
  "'타다'의 반대말은 '내리다'예요. 타다, 내리다. 짝으로 외우면 쉬워요. '여기서 내려요.'",
  "The opposite of '타다' is '내리다' (to get off). 타다 / 내리다 — learn them as a pair. '여기서 내려요' (I get off here).",
  TR2,[("speak",300,300,1.0)]),
 ("문제 발생!","A problem!","몇 번 출구",
  "마지막 문제예요! 강남역은 출구가 정말 많아요. 잘못 나가면 한참 걸어야 해요.",
  "One last problem! Gangnam Station has a LOT of exits. Take the wrong one and you'll walk a long way.",
  GX,[("surprise",300,300,1.0)]),
 ("몇 번 출구예요?","Which exit number?","몇 번 출구",
  "그래서 이렇게 물어요. '몇 번 출구예요?' 한국에서는 약속할 때 출구 번호로 만나요. '강남역 11번 출구에서 만나요.'",
  "So ask: '몇 번 출구예요?' (Which exit number?). In Korea, people meet by exit number: 'Let's meet at Gangnam Exit 11.'",
  GX,[("speak",300,300,1.0)]),
 ("11번 출구요","Exit 11","11번 출구",
  "'11번 출구요.' 번호로 대답해 줘요. 이제 계단을 올라가면 강남 거리예요!",
  "'11번 출구요' — Exit 11. They answer with a number. Climb the stairs and you're on the streets of Gangnam!",
  GX,[("count_fingers",300,300,0.4),("walk_stairs",300,380,0.6)]),
 ("버스로 갈아타요","Transfer to a bus","버스 갈아타요",
  "마지막 꿀팁! 지하철에서 내려서 버스로도 갈아탈 수 있어요. 같은 교통카드를 그냥 대면 돼요. 아주 편하죠?",
  "Final tip! You can also transfer from the subway to a bus. Just tap the same transit card. So convenient!",
  GS,[("tap_card",300,300,1.0)]),
 ("오늘의 표현","Today's phrases","타다 환승 내리다",
  "오늘 배운 걸 정리해요. 버스, 지하철, 타다, 환승, 내리다, 출구. 이 여섯 단어면 서울 어디든 갈 수 있어요.",
  "Let's review: 버스 (bus), 지하철 (subway), 타다 (ride), 환승 (transfer), 내리다 (get off), 출구 (exit). These six words take you anywhere in Seoul.",
  GS,[("presenting",300,300,1.0)]),
 ("다음 시간에","See you next time","길 찾기",
  "강남역 도착! 공항에서 여기까지 함께 왔어요. 다음 시간에는 길 찾기와 위치 안내를 배워요. 그때 또 만나요!",
  "We made it to Gangnam! We traveled all the way from the airport together. Next time: asking for directions. See you then!",
  GN,[("bow",300,300,1.0)]),
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
BASEP = "assets/graphics/poses/injun_w10_base.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r: INJUN = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("인준W12base", "injun_w12_base", "pose", BASEP, "W12 base")); INJUN = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'ijw12_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

for i, (ck, ce, gl, sk, se, bg, beats) in enumerate(SC, 1):
    sk = norm_quotes(sk); se = norm_quotes(se)
    rel = f"graphics/letters/w12_{i:02d}.png"; make_glyph(gl, f"assets/{rel}")
    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
    if r: gasset = r[0]
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (f"W12글자_{gl[:8]}", f"w12_{i:02d}", "letter", rel, "동동")); gasset = cur.lastrowid
    aseq = f"ijw12_s{i:02d}"
    GCX = 560; WB = 1265 - GCX; HB = 340; CAP = 150
    best = None
    for _mc in range(4, 17):
        _ls = wrap_write(gl, _mc); _nl = len(_ls); _mx = max(len(l) for l in _ls)
        _f = min(WB / (_mx * 0.98), HB / (_nl * 1.18), CAP)
        if best is None or _f > best[0]: best = (_f, _ls, _nl)
    size_px, lines, nlines = best; size_px = max(52, size_px)
    draw_text = "\n".join(lines)
    gscale = round(size_px / 200, 3); blockH = nlines * size_px * 1.18; gcy = int(28 + blockH / 2)
    spec = {"cap_ko": ck, "cap_en": ce, "motion": "static", "char_key": "injun_w12", "char_mode": "teacher",
            "draw_font": "cafe24_dongdong", "draw_dur": 3.0, "draw_text": draw_text, "draw_align": "left",
            "bg": bg, "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) VALUES (?,?,?,?,?,?,?)",
                (EP, i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                (EP, i, gasset, GCX, gcy, gscale, 3, "write", 0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                (EP, i, INJUN, 300, 452, 0.6, 5, "gesture", 0))
    bj = [{"name": p, "cycle": [p], "x_from": xf, "x_to": xt, "dur": d} for (p, xf, xt, d) in beats]
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols: fields["description"] = f"인준 W12 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
# 사용된 배경·포즈 집계(검증용)
bgs = sorted({s[5] for s in SC}); poses = sorted({b[0] for s in SC for b in s[6]})
con.close()
print(f"완료: {EP} {n}씬 (~8분, 인준, 인천공항→강남역)")
print(f"배경 {len(bgs)}종: {', '.join(b.replace('bg_w12_','') for b in bgs)}")
print(f"포즈 {len(poses)}종: {', '.join(poses)}")
