# -*- coding: utf-8 -*-
"""W10(상점·가격) 30씬 확장 빌드: injun_w10 안무(teacher, 동선 중앙까지) + 동동체 글자(상단) +
   배경 4종(해변/상점/계산대/세일, 광안리+객체) + 발음클립('..')."""
import sqlite3, json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.chdir(ROOT)
DB = "channel/content.db"
FONT = "assets/fonts/Cafe24Dongdong.ttf"
LET_DIR = "assets/graphics/letters"
PLACE = "Gwangalli & Diamond Bridge"
B, S, C, A = "bg_w10_beach", "bg_w10_shop", "bg_w10_counter", "bg_w10_sale"
CARD = {3: "숫자 영상", 28: "다음 영상"}   # 우상단 추천 영상 카드가 뜨는 씬

# (cap_ko, cap_en, glyph, script_kr('..'=클립), script_en, bg, beats[(pose,xf,xt,dur)])
# 캐릭터 동선: 좌260 ~ 중앙620 (50%). 글자=상단(cx640,cy155), 인준=바닥(cy460).
SC = [
 ("쇼핑 표현","Shopping words","쇼핑 표현",
  "안녕하세요! 훈민정음 방에 오신 걸 환영해요. 오늘은 가게에서 물건을 살 때 꼭 필요한 표현을 배워요. 광안리 바닷가 가게로 함께 가 볼까요?",
  "Hello! Welcome. Today we learn the phrases you need for shopping. Let's head to a shop by Gwangalli Beach!",
  B,[("walk_right",260,400,0.2),("wave_right",400,400,0.2),("greeting",400,400,0.2),("presenting",400,470,0.4)]),
 ("오늘의 흐름","Today's flow","얼마예요 이거 주세요 결제 할인",
  "쇼핑은 순서가 있어요. 가격 묻기 ‘얼마예요’, 고르기 ‘이거 주세요’, ‘결제’, 그리고 ‘할인’ 확인. 이 네 가지예요.",
  "Shopping has a flow: ask the price ‘얼마예요’, choose ‘이거 주세요’, pay ‘결제’, and check the discount ‘할인’. Just these four.",
  B,[("lean_in",400,400,0.3),("count_fingers",400,400,0.4),("nod",400,400,0.3)]),
 ("복습: 숫자","Review: numbers","숫자 복습",
  "가격을 알아들으려면 ‘숫자’가 중요해요. 숫자가 헷갈리면 오른쪽 위 카드의 지난 영상을 한 번 더 보세요.",
  "To catch prices, ‘숫자’ (numbers) matter. If numbers are tricky, watch our previous video in the top-right card.",
  B,[("thinking",400,400,0.4),("point_up",400,400,0.6)]),
 ("가게에 왔어요","At the shop","가게","‘가게’에 왔어요. 마음에 드는 물건을 봤네요. 가격이 궁금해요.",
  "We're at the ‘가게’ (shop). You spot something you like. You wonder about the price.",
  S,[("walk_right",380,560,0.35),("browse",560,560,0.3),("point_center",560,560,0.35)]),
 ("얼마예요 = 가격 묻기","= how much?","얼마예요",
  "가격을 물을 땐 ‘얼마예요’ 라고 해요. ‘얼마예요’는 가격을 묻는 말이에요.",
  "To ask a price, say ‘얼마예요’. ‘얼마예요’ means how much.",
  S,[("raising_hand",460,460,0.3),("presenting",460,460,0.3),("speak",460,460,0.4)]),
 ("이거 얼마예요?","How much is this?","이거 얼마예요",
  "물건을 가리키며 물어요. ‘이거 얼마예요’? 이렇게요.",
  "Point at the item and ask: ‘이거 얼마예요’?",
  S,[("point_right",520,600,0.4),("speak",600,600,0.6)]),
 ("따라 해 보세요","Repeat","얼마예요",
  "자, 천천히 따라 해 보세요. ‘얼마예요’.",
  "Now repeat slowly: ‘얼마예요’.",
  S,[("your_turn",460,460,0.4),("listen",460,460,0.6)]),
 ("전부 얼마예요?","How much in total?","전부 얼마예요",
  "여러 개를 한꺼번에 살 땐 ‘전부 얼마예요’ 라고 물어요.",
  "Buying several at once? Ask ‘전부 얼마예요’ (how much in total).",
  S,[("presenting",500,500,0.4),("count_fingers",500,500,0.3),("speak",500,500,0.3)]),
 ("물건 고르기","Choosing","이거 주세요",
  "살 물건을 정했어요. 이제 달라고 말해요.",
  "You've decided. Now ask for it.",
  S,[("pick_up",540,540,0.4),("offer_item",540,540,0.3),("speak",540,540,0.3)]),
 ("이거 주세요 = 주세요","This one, please","이거 주세요",
  "물건을 가리키며 ‘이거 주세요’ 라고 해요. ‘이거 주세요’는 이것을 달라는 말이에요.",
  "Point and say ‘이거 주세요’. It means 'this one, please'.",
  S,[("raising_hand",460,460,0.3),("presenting",460,460,0.3),("speak",460,460,0.4)]),
 ("이거·그거·저거","this · that · that","이거 그거 저거",
  "가까우면 ‘이거 주세요’, 조금 멀면 ‘그거 주세요’, 멀리 있으면 ‘저거 주세요’.",
  "Near: ‘이거 주세요’. A bit far: ‘그거 주세요’. Far: ‘저거 주세요’.",
  S,[("point_center",440,440,0.25),("point_right",440,600,0.25),("point_left",600,300,0.25),("offer_item",400,400,0.25)]),
 ("따라 해 보세요","Repeat","이거 주세요",
  "자, 따라 해 보세요. ‘이거 주세요’.",
  "Now repeat: ‘이거 주세요’.",
  S,[("your_turn",460,460,0.4),("listen",460,460,0.6)]),
 ("개수 말하기","Counting","한 개 두 개",
  "개수도 말해 봐요. 하나면 ‘한 개 주세요’, 둘이면 ‘두 개 주세요’.",
  "Say the count: one is ‘한 개 주세요’, two is ‘두 개 주세요’.",
  S,[("count_fingers",460,460,0.4),("speak",460,460,0.6)]),
 ("다른 것 찾기","Asking for others","다른 거/더 큰 거",
  "마음에 안 들면 물어봐요. ‘다른 거 있어요’? 더 크면 ‘더 큰 거’ 주세요.",
  "Not quite right? Ask ‘다른 거 있어요’ (any others)? Or ‘더 큰 거’ (a bigger one).",
  S,[("thinking",460,460,0.3),("presenting",460,560,0.4),("speak",560,560,0.3)]),
 ("계산할 차례","Time to pay","결제",
  "다 골랐으면 계산대로 가요. 이제 돈을 낼 차례예요.",
  "All chosen? Head to the counter. Time to pay.",
  C,[("walk_right",380,560,0.35),("offer_card",560,560,0.35),("presenting",560,560,0.3)]),
 ("결제 = 돈 내기","Payment","결제",
  "돈을 내는 것을 ‘결제’ 라고 해요.",
  "Paying is called ‘결제’ (payment).",
  C,[("raising_hand",460,460,0.3),("presenting",460,460,0.4),("speak",460,460,0.3)]),
 ("카드로 결제","By card","카드",
  "카드로 낼 땐 ‘카드’로 결제할게요, 라고 해요.",
  "By card: say ‘카드’로 결제할게요.",
  C,[("offer_card",540,540,0.5),("tap_card",540,540,0.5)]),
 ("현금으로 결제","By cash","현금",
  "현금으로 낼 땐 ‘현금’으로 결제할게요, 라고 해요.",
  "By cash: say ‘현금’으로 결제할게요.",
  C,[("hold_cash",540,540,0.5),("presenting",540,540,0.5)]),
 ("따라 해 보세요","Repeat","결제",
  "자, 따라 해 보세요. ‘결제’.",
  "Now repeat: ‘결제’.",
  C,[("your_turn",460,460,0.4),("listen",460,460,0.6)]),
 ("봉투 주세요","A bag, please","봉투 주세요",
  "봉투가 필요하면 ‘봉투 주세요’ 라고 해요.",
  "Need a bag? Say ‘봉투 주세요’.",
  C,[("offer_item",500,500,0.4),("speak",500,500,0.6)]),
 ("영수증 주세요","A receipt, please","영수증 주세요",
  "영수증이 필요하면 ‘영수증 주세요’ 라고 해요.",
  "Need a receipt? Say ‘영수증 주세요’.",
  C,[("presenting",500,500,0.4),("speak",500,500,0.6)]),
 ("세일 중이에요!","On sale!","할인",
  "어? 세일 중이네요! 값이 싸졌어요.",
  "Oh? It's on sale! The price dropped.",
  A,[("walk_right",380,540,0.3),("look_price",540,540,0.4),("surprise",540,540,0.3)]),
 ("할인 = 값 깎기","Discount","할인",
  "값을 깎아 주는 것을 ‘할인’ 이라고 해요.",
  "Lowering the price is ‘할인’ (discount).",
  A,[("raising_hand",460,460,0.3),("presenting",460,460,0.4),("speak",460,460,0.3)]),
 ("할인 돼요?","Is it discounted?","할인 돼요",
  "세일할 때 이렇게 물어요. 이거 ‘할인’ 돼요?",
  "During a sale, ask: 이거 ‘할인’ 돼요?",
  A,[("point_center",500,500,0.4),("speak",500,500,0.6)]),
 ("깎아 주세요","Please lower it","좀 깎아 주세요",
  "조금 비싸면 ‘좀 깎아 주세요’ 라고 부탁해요. 너무 비싸면 ‘너무 비싸요’.",
  "A bit pricey? Ask ‘좀 깎아 주세요’ (please lower it). Too pricey: ‘너무 비싸요’.",
  A,[("presenting",500,500,0.3),("lean_in",500,500,0.4),("speak",500,500,0.3)]),
 ("따라 해 보세요","Repeat","할인",
  "자, 따라 해 보세요. ‘할인’.",
  "Now repeat: ‘할인’.",
  A,[("your_turn",460,460,0.4),("thumbs_up",460,460,0.6)]),
 ("실전 대화","Real conversation","얼마예요/오천 원이에요",
  "이제 실제 상황이에요! 손님이 ‘이거 얼마예요’ 하고 물으면, 점원은 ‘오천 원이에요’, ‘지금 할인 중이에요’! 하고 답해요.",
  "Now, real life! A customer asks ‘이거 얼마예요’, and the clerk says ‘오천 원이에요’, ‘지금 할인 중이에요’!",
  A,[("point_center",440,440,0.2),("lean_in",440,440,0.2),("presenting",440,440,0.2),("cheering",440,440,0.2),("thumbs_up",440,440,0.2)]),
 ("더 알아보기","Learn more","더 알아보기",
  "가게에서 더 다양하게 말하고 싶으면, 오른쪽 위 카드의 이 영상을 보세요. 음식 주문과 시장 표현도 이어서 배워요.",
  "Want more shop phrases? See the video in the top-right card — next, ordering food and market talk.",
  B,[("lean_in",400,400,0.4),("point_up",400,400,0.6)]),
 ("정리해요","Recap","얼마예요 이거 주세요 결제 할인",
  "오늘 배운 표현이에요. ‘얼마예요’, ‘이거 주세요’, ‘결제’, ‘할인’. 소리 내어 한 번 더 읽어 볼까요? 아주 잘 하고 있어요!",
  "Today's phrases: ‘얼마예요’, ‘이거 주세요’, ‘결제’, ‘할인’. Read them aloud once more. You're doing great!",
  B,[("presenting",400,400,0.3),("point_center",400,400,0.3),("your_turn",400,400,0.2),("thumbs_up",400,400,0.2)]),
 ("다음 시간에 만나요!","See you next time!","다음 시간에 만나요",
  "훌륭해요! 오늘 표현을 하루에 한 번 꼭 써 보세요. 작은 연습이 큰 실력이 돼요. 다음 시간에 또 만나요!",
  "Wonderful! Use today's phrases at least once today. Small steps, big skills. See you next time!",
  B,[("cheering",400,400,0.3),("point_self",400,400,0.2),("presenting",400,400,0.2),("wave_left",400,280,0.3)]),
]

# ---------- 동동체 글리프(많으면 2줄) ----------
os.makedirs(LET_DIR, exist_ok=True)
def make_card(text, path):
    """우상단 추천 영상 카드(둥근 흰 박스 + 빨간 재생버튼 + 동동체 텍스트)."""
    W, H = 380, 120
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, W-4, H-4], radius=18, fill=(255, 255, 255, 245), outline=(30, 30, 30, 255), width=4)
    cx, cy, r = 54, H//2, 26
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(220, 50, 45, 255))
    d.polygon([(cx-9, cy-14), (cx-9, cy+14), (cx+16, cy)], fill=(255, 255, 255, 255))
    f = ImageFont.truetype(FONT, 44)
    d.text((94, H//2 - 30), text, font=f, fill=(30, 30, 30, 255))
    im.save(path)

def make_glyph(text, path):
    SZ = 128
    f = ImageFont.truetype(FONT, SZ)
    tmp = Image.new("RGBA", (10, 10)); dd = ImageDraw.Draw(tmp)
    if "/" in text:
        lines = [s.strip() for s in text.split("/")]
    else:
        toks = text.split()
        w1 = dd.textbbox((0, 0), text, font=f)[2]
        if len(toks) >= 4 or w1 > 880:
            h = (len(toks) + 1) // 2; lines = [" ".join(toks[:h]), " ".join(toks[h:])]
        else:
            lines = [text]
    maxw = max(dd.textbbox((0, 0), ln, font=f)[2] for ln in lines)
    if maxw > 980:
        SZ = int(SZ * 980 / maxw); f = ImageFont.truetype(FONT, SZ)
    asc, desc = f.getmetrics(); lh = asc + desc
    ws = [dd.textbbox((0, 0), ln, font=f)[2] for ln in lines]
    W = max(ws) + 30; H = lh * len(lines) + 24
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        w = dd.textbbox((0, 0), ln, font=f)[2]
        d.text(((W - w) // 2, 12 + i * lh), ln, font=f, fill=(35, 32, 40, 255))
    bb = im.getbbox(); im = im.crop(bb) if bb else im
    im.save(path); return len(lines)

con = sqlite3.connect(DB); cur = con.cursor()
INJUN = cur.execute("SELECT id FROM assets WHERE file_path='assets/graphics/poses/injun_w10_base.png'").fetchone()[0]
cur.execute("DELETE FROM scene_objects WHERE episode='KO-W10'")
cur.execute("DELETE FROM scenes WHERE episode='KO-W10'")
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'injun_w10_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

for i, (ck, ce, gl, sk, se, bg, beats) in enumerate(SC, 1):
    rel = f"graphics/letters/w10_{i:02d}.png"
    nlines = make_glyph(gl, f"assets/{rel}")
    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
    if r: gasset = r[0]
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (f"W10글자_{gl[:8]}", f"w10_{i:02d}", "letter", rel, "동동 글리프"))
        gasset = cur.lastrowid
    aseq = f"injun_w10_s{i:02d}"
    spec = {"cap_ko": ck, "cap_en": ce, "motion": "static", "char_key": "injun_w10", "char_mode": "teacher",
            "draw_font": "cafe24_dongdong", "draw_dur": 3.0, "bg": bg, "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) VALUES (?,?,?,?,?,?,?)",
                ("KO-W10", i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    # 글자=상단중앙(cx640,cy155), 인준=바닥(cy460)
    gcy = 150 if nlines == 2 else 165
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                ("KO-W10", i, gasset, 640, gcy, 0.42, 3, "fade_in", 0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                ("KO-W10", i, INJUN, 400, 460, 0.48, 5, "gesture", 0))
    # 우상단 추천 영상 카드
    if i in CARD:
        crel = f"graphics/letters/w10_card_{i:02d}.png"
        make_card(CARD[i], f"assets/{crel}")
        cr = cur.execute("SELECT id FROM assets WHERE file_path=?", (crel,)).fetchone()
        if cr: casset = cr[0]
        else:
            cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                        (f"W10카드_{i:02d}", f"w10_card_{i:02d}", "card", crel, "우상단 추천카드")); casset = cur.lastrowid
        cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                    ("KO-W10", i, casset, 1160, 90, 0.5, 6, "elastic_pop", 0))   # 우상단 코너(왼편 노트박스 대칭)
    bj = [{"name": p, "cycle": [p], "x_from": xf, "x_to": xt, "dur": d} for (p, xf, xt, d) in beats]
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols: fields["description"] = f"인준 W10 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode='KO-W10'").fetchone()[0]
no = cur.execute("SELECT COUNT(*) FROM scene_objects WHERE episode='KO-W10'").fetchone()[0]
con.close()
print(f"완료: KO-W10 {n}씬 / scene_objects {no} / anim_sequences injun_w10_s01~{n:02d} / 배경 4종")
