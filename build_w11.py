# -*- coding: utf-8 -*-
"""W11 v3(식당·맛표현) 42씬 ~8분: madam_j_w11 전부 오른쪽 향함, 앉기=테이블 가까이. 선생님 설명(간결). 배경 오른쪽/캐릭터 왼쪽."""
import sqlite3, json, os, re as _re2
from PIL import Image, ImageDraw, ImageFont

def norm_quotes(s):
    """곡선따옴표→직선, 따옴표 안 끝의 ?!. 을 밖으로 빼 CLIP_QUOTED(선희 DB클립) 키와 매칭시킴."""
    s = s.replace("‘","'").replace("’","'")
    s = _re2.sub(r"'([^']*?)([?!.]+)'", r"'\1'\2", s)
    return s

def wrap_write(gl, maxch=7):
    """드로잉용 줄바꿈: 글자 많으면 여러 줄(줄당 ~maxch자). '/'는 강제 줄바꿈."""
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
DB = "channel/content.db"; FONT = "assets/fonts/Cafe24Dongdong.ttf"; LET_DIR = "assets/graphics/letters"
PLACE = "Gamcheon Culture Village"
AL1,AL2,EN,TB,FD,PP,CO,CU,SU = "bg_w11_alley1","bg_w11_alley2","bg_w11_entrance","bg_w11_table","bg_w11_food","bg_w11_people","bg_w11_counter","bg_w11_closeup","bg_w11_sunset"
SX = 640   # 앉은 캐릭터 x — 화면 정중앙(사장님 지시: 의자 앉은 캐릭터는 딱 중간)
# (cap_ko, cap_en, glyph, script_kr, script_en, bg, beats[(pose,xf,xt,dur)]) — 전부 오른쪽 향함
SC = [
 ("감천마을 도착","At Gamcheon","식당","안녕하세요! 오늘은 감천문화마을 골목 식당에서 쓰는 표현을 배워요. 한국 식당에서 무슨 말을 할지 막막하죠? 하나씩 배우면 어디서든 자신 있게 주문할 수 있어요. 함께 가 봐요!",
  "Hello! Today we learn phrases for a restaurant in Gamcheon Village. Not sure what to say at a Korean restaurant? Learn these one by one and order with confidence. Let's go!",AL1,[("walk_right",-120,300,0.5),("presenting",300,300,0.5)]),
 ("배고파요","I'm hungry","배고파요","골목을 걷다 보니 배가 고파지네요. 이럴 때 ‘배고파요’ 라고 해요. ‘배’는 배, ‘고파요’는 음식이 필요하다는 뜻이에요. 맛있는 식당을 찾아봐요.",
  "Walking around, we get hungry. We say ‘배고파요’. ‘배’ is your stomach, ‘고파요’ means you need food. Let's find a good restaurant.",AL1,[("hungry",300,300,0.5),("look_around",300,300,0.5)]),
 ("오늘의 흐름","Today's flow","찾기 주문 맛보기 계산","식당에는 순서가 있어요. 식당 ‘찾기’, ‘주문’, ‘맛’ 표현, ‘계산’. 오늘은 이 네 단계를 상황에 맞는 표현과 함께 배워요.",
  "A restaurant has a flow: find, order, taste, pay. Today we learn each step with the right phrase.",AL1,[("point_right",300,300,0.5),("presenting",300,300,0.5)]),
 ("맛있는 식당?","A good place?","맛있는 식당","낯선 동네에선 어디가 맛있는지 모르죠. 지나가는 사람에게 물어봐요. ‘이 근처에 맛있는 식당이 어디 있어요?’ 이 한마디면 친절히 알려줘요.",
  "In a new area, ask a passerby: ‘이 근처에 맛있는 식당이 어디 있어요?’ (Where's a good restaurant?). This line gets you kind help.",AL1,[("greeting",300,300,0.4),("point_right",300,300,0.6)]),
 ("추천해 주세요","Recommendation?","추천","고르기 어려우면 골라 달라고 해요. ‘추천할 만한 식당 있어요?’ ‘추천’은 좋은 걸 골라 알려주는 거예요.",
  "Hard to choose? Ask ‘추천할 만한 식당 있어요?’. ‘추천’ means suggesting something good.",AL2,[("greeting",280,280,0.4),("thinking",280,280,0.6)]),
 ("뭐가 유명해요?","What's famous?","유명해요","그 동네 인기 음식이 궁금하면 ‘여기 뭐가 유명해요?’ 하고 물어요. ‘유명해요’는 많은 사람이 좋아한다는 뜻이에요.",
  "For local specialties, ask ‘여기 뭐가 유명해요?’. ‘유명해요’ means well-loved by many.",AL2,[("walk_right",250,380,0.4),("point_right",380,380,0.6)]),
 ("어떤 걸 팔아요?","What do they sell?","팔아요","무엇을 파는지 궁금하면 ‘이 집은 어떤 걸 팔아요?’ 하고 물어요. ‘팔아요’는 파는 걸 말해요. 들어가기 전에 미리 물어볼 수 있어요.",
  "Ask ‘이 집은 어떤 걸 팔아요?’ (What do you sell?). ‘팔아요’ means to sell. Handy before going in.",AL2,[("look_around",300,300,0.4),("point_right",300,300,0.6)]),
 ("들어가요!","Let's go in!","맛있어 보여요","메뉴가 먹음직스러우면 ‘맛있어 보여요’ 라고 해요. ‘-어 보여요’는 보기에 그렇게 느껴진다는 뜻이에요. 이 식당으로 들어가요!",
  "When it looks tasty, say ‘맛있어 보여요’. ‘-어 보여요’ means it seems so by looking. Let's go in!",EN,[("presenting",280,280,0.4),("walk_right",280,420,0.6)]),
 ("몇 분이세요?","For how many?","몇 분이세요","들어가면 점원이 물어요. ‘몇 분이세요?’ ‘몇 명이에요?’라는 뜻이에요. 손님 수를 확인하는 거예요.",
  "The staff asks ‘몇 분이세요?’ — meaning ‘how many people?’ They're checking your group size.",EN,[("walk_right",250,400,0.5),("greeting",400,400,0.5)]),
 ("한 명이요","One, please","한 명이요 / 두 명이요","혼자면 ‘한 명이요’, 둘이면 ‘두 명이요’. ‘명’은 사람을 세는 말이에요. 손가락으로 수를 보여주면 더 확실해요.",
  "Alone? ‘한 명이요’. Two? ‘두 명이요’. ‘명’ counts people. Show fingers too for clarity.",PP,[("greeting",300,300,0.5),("point_right",300,300,0.5)]),
 ("앉아도 돼요?","May I sit?","앉아도 돼요","빈자리를 보면 ‘여기 앉아도 돼요?’ 하고 물어요. ‘-아도 돼요?’는 허락을 구하는 말이에요. ‘네’ 하면 앉으면 돼요.",
  "See a seat? Ask ‘여기 앉아도 돼요?’ (May I sit here?). ‘-아도 돼요?’ asks permission. When they say yes, sit.",TB,[("walk_right",380,SX,0.4),("sit_base",SX,SX,0.6)]),
 ("메뉴 주세요","Menu, please","메뉴 주세요","앉았으면 메뉴가 필요해요. ‘메뉴 주세요.’ ‘메뉴’는 음식 목록, ‘주세요’는 정중한 부탁이에요.",
  "Seated, you need the menu: ‘메뉴 주세요’. ‘메뉴’ is the list, ‘주세요’ is a polite request.",TB,[("sit_receive",SX,SX,1.0)]),
 ("뭐가 맛있어요?","What's good?","뭐가 맛있어요","뭘 고를지 막막하면 ‘여기 뭐가 맛있어요?’ 하고 물어요. 그 집에서 잘하는 걸 추천받을 수 있어요.",
  "Not sure what to pick? Ask ‘여기 뭐가 맛있어요?’. They'll tell you what they do best.",TB,[("sit_menu",SX,SX,1.0)]),
 ("인기 메뉴","Popular dish","인기 메뉴","많이 시키는 게 궁금하면 ‘인기 메뉴가 뭐예요?’ 하고 물어요. 인기 메뉴는 대개 실패가 없어요.",
  "Ask ‘인기 메뉴가 뭐예요?’ (What's popular?). The popular dish is usually a safe bet.",TB,[("sit_menu",SX,SX,0.6),("sit_point",SX,SX,0.4)]),
 ("추천해 주세요","Recommend?","추천해 주세요","고르기 어려우면 점원에게 ‘메뉴를 추천해 주세요’ 하고 부탁해요. ‘저 대신 골라 주세요’라는 뜻이에요.",
  "Ask the staff ‘메뉴를 추천해 주세요’ (Please recommend). It means ‘pick a good one for me.’",TB,[("sit_call",SX,SX,1.0)]),
 ("이건 뭐예요?","What is this?","이건 뭐예요","처음 보는 음식은 가리키며 ‘이건 뭐예요?’ 하고 물어요. ‘이건’은 ‘이것은’이에요. 궁금한 건 물어보세요.",
  "Point at a new dish: ‘이건 뭐예요?’ (What is this?). ‘이건’ is ‘this.’ Just ask!",TB,[("sit_point",SX,SX,1.0)]),
 ("무엇으로 만들었어요?","Made of what?","무엇으로 만들었어요","재료가 궁금하면 ‘이건 무엇으로 만들었어요?’ 하고 물어요. 못 먹는 재료가 있으면 꼭 확인하세요.",
  "Ask ‘무엇으로 만들었어요?’ (What's it made of?). Always check if you can't eat something.",TB,[("sit_point",SX,SX,0.5),("sit_menu",SX,SX,0.5)]),
 ("쌀 고기 채소 해물","ingredients","쌀 고기 채소 해물","재료는 보통 이래요. 밥이 되는 ‘쌀’, ‘고기’, ‘채소’, 생선 같은 ‘해물’. 이 네 가지면 대부분 알아들어요.",
  "Common ingredients: ‘쌀’ (rice), ‘고기’ (meat), ‘채소’ (vegetables), ‘해물’ (seafood). These four cover most.",TB,[("sit_receive",SX,SX,1.0)]),
 ("어떤 맛이에요?","How's the taste?","어떤 맛이에요","맛이 궁금하면 ‘이건 어떤 맛이에요?’ 하고 물어요. 미리 맛을 알면 고르기 쉬워요.",
  "Ask ‘어떤 맛이에요?’ (How does it taste?). Knowing helps you choose.",TB,[("sit_menu",SX,SX,1.0)]),
 ("매워요?","Is it spicy?","매워요","매운 걸 못 드시면 꼭 물어요. ‘이거 매워요?’ 한국 음식은 매운 게 많아 아주 중요한 질문이에요.",
  "Not into spicy? Ask ‘이거 매워요?’ (Is it spicy?). Korean food is often spicy — a key question.",TB,[("sit_taste",SX,SX,1.0)]),
 ("안 매운 거 있어요?","Non-spicy?","안 매운 거","매운 걸 피하려면 ‘안 매운 거 있어요?’ 하고 물어요. ‘안’은 ‘아니다’, 즉 맵지 않은 거예요.",
  "Ask ‘안 매운 거 있어요?’ (A non-spicy one?). ‘안’ means ‘not’ — something not spicy.",TB,[("sit_base",SX,SX,0.5),("sit_point",SX,SX,0.5)]),
 ("양이 많아요?","Big portion?","양이 많아요","나눠 먹거나 배고프면 ‘양이 많아요?’ 하고 물어요. ‘양’은 음식 분량이에요.",
  "Sharing or hungry? Ask ‘양이 많아요?’ (Big portion?). ‘양’ is the amount.",TB,[("sit_receive",SX,SX,1.0)]),
 ("이거 주세요","This, please","이거 주세요","골랐으면 가리키며 ‘이거 주세요’ 하면 주문 끝. ‘이거’는 ‘이것’, 가장 많이 쓰는 주문 표현이에요.",
  "Chose? Point and say ‘이거 주세요’ (This, please). The most-used ordering phrase.",TB,[("sit_point",SX,SX,0.6),("sit_base",SX,SX,0.4)]),
 ("하나 둘","one two","하나 둘","개수도 말해요. ‘이거 하나하고 저거 둘 주세요.’ 가까우면 ‘이거’, 멀면 ‘저거’예요.",
  "Say the count: ‘이거 하나하고 저거 둘 주세요’. Near is ‘이거,’ far is ‘저거.’",TB,[("sit_point",SX,SX,1.0)]),
 ("물 좀 주세요","Water, please","물 주세요","목마르면 ‘물 좀 주세요.’ 한국 식당은 물이 무료예요. ‘좀’을 넣으면 더 부드러워요.",
  "Thirsty? ‘물 좀 주세요’ (Water, please). Water is free. ‘좀’ makes it softer.",TB,[("sit_call",SX,SX,1.0)]),
 ("잘 먹겠습니다!","Let's dig in!","잘 먹겠습니다","음식이 나왔어요! 먹기 전에 ‘잘 먹겠습니다’ 하고 인사해요. 만든 사람에게 고마움을 담은 표현이에요.",
  "Food's here! Before eating, say ‘잘 먹겠습니다’ — a thank-you to whoever made it.",FD,[("sit_receive",SX,SX,0.5),("sit_eat",SX,SX,0.5)]),
 ("반찬 더 주세요","More banchan","반찬 더 주세요","반찬이 부족하면 ‘반찬 좀 더 주세요.’ ‘더’는 추가예요. 반찬은 대개 무료로 더 줘요.",
  "Out of side dishes? ‘반찬 좀 더 주세요’. ‘더’ means more. Refills are usually free.",FD,[("sit_call",SX,SX,1.0)]),
 ("젓가락 숟가락","utensils","젓가락 숟가락","수저가 없으면 ‘젓가락하고 숟가락 주세요.’ ‘젓가락’은 집는 것, ‘숟가락’은 뜨는 거예요.",
  "No utensils? ‘젓가락하고 숟가락 주세요’. ‘젓가락’ picks up, ‘숟가락’ scoops.",FD,[("sit_receive",SX,SX,1.0)]),
 ("리필 돼요?","Refill?","리필 돼요","더 먹고 싶으면 ‘이거 리필 돼요?’ ‘리필’은 다시 채워 준다는 뜻이에요.",
  "Want more? ‘이거 리필 돼요?’ (Refill?). ‘리필’ means refilling.",FD,[("sit_call",SX,SX,1.0)]),
 ("맛있어요!","Delicious!","맛있어요","맛을 표현해요. 맛있으면 ‘맛있어요!’ 엄지를 들면 마음이 더 전해져요. 만든 분에게 큰 칭찬이에요.",
  "Describe the taste. Good? ‘맛있어요!’ A thumbs-up helps. A big compliment to the cook.",FD,[("sit_eat",SX,SX,0.5),("sit_taste",SX,SX,0.5)]),
 ("매워요 · 짜요","spicy·salty","매워요 짜요","매운맛은 ‘매워요’, 짠맛은 ‘짜요.’ ‘조금’을 붙이면 부드러워요 — ‘조금 매워요.’",
  "Spicy is ‘매워요,’ salty is ‘짜요.’ Add ‘조금’ to soften: ‘조금 매워요.’",FD,[("sit_taste",SX,SX,0.5),("sit_drink",SX,SX,0.5)]),
 ("달아요 · 싱거워요","sweet·bland","달아요 싱거워요","단맛은 ‘달아요’, 간이 약하면 ‘싱거워요.’ 맛마다 표현이 달라요.",
  "Sweet is ‘달아요,’ bland is ‘싱거워요.’ Each taste has its word.",FD,[("sit_taste",SX,SX,0.5),("sit_base",SX,SX,0.5)]),
 ("담백해요 · 고소해요","light·savory","담백해요 고소해요","깔끔한 맛은 ‘담백해요’, 참기름처럼 고소하면 ‘고소해요.’ 국물 칭찬에 딱이에요.",
  "Clean is ‘담백해요,’ nutty is ‘고소해요.’ Perfect to praise the broth.",CU,[("sit_drink",SX,SX,0.5),("sit_eat",SX,SX,0.5)]),
 ("맛 표현 정리","Taste words","맵다 짜다 달다 시다 쓰다 담백 고소 느끼","맛 표현 정리! ‘맵다’, ‘짜다’, ‘달다’, ‘시다’, ‘쓰다’, ‘담백하다’, ‘고소하다’, ‘느끼하다.’ 상황에 맞게 쓰면 돼요.",
  "Let's review the taste words: spicy ‘맵다’, salty ‘짜다’, sweet ‘달다’, sour ‘시다’, bitter ‘쓰다’, light ‘담백하다’, savory ‘고소하다’, greasy ‘느끼하다’. Use the right one for each flavor!",CU,[("sit_point",SX,SX,0.5),("sit_taste",SX,SX,0.5)]),
 ("잘 먹었습니다!","Great meal!","잘 먹었습니다","다 먹었으면 ‘잘 먹었습니다.’ 먹기 전엔 ‘잘 먹겠습니다’, 먹은 뒤엔 ‘잘 먹었습니다.’ 짝으로 기억해요.",
  "Done? ‘잘 먹었습니다.’ Before eating ‘잘 먹겠습니다,’ after ‘잘 먹었습니다.’ Remember them as a pair.",FD,[("sit_receive",SX,SX,0.5),("sit_base",SX,SX,0.5)]),
 ("싸 주세요","Pack it","싸 주세요","남았으면 ‘남은 음식을 싸 주시겠어요?’ ‘싸다’는 포장한다는 뜻이에요.",
  "Leftovers? ‘남은 음식을 싸 주시겠어요?’ (Pack it?). ‘싸다’ means to wrap up.",FD,[("sit_receive",SX,SX,1.0)]),
 ("계산할게요","I'll pay","계산할게요","다 먹었으면 계산대로 가서 ‘계산할게요, 얼마예요?’ ‘계산’은 값 내기, ‘얼마예요?’는 가격 묻기예요.",
  "Go to the counter: ‘계산할게요, 얼마예요?’ ‘계산’ is paying, ‘얼마예요?’ asks the price.",CO,[("walk_right",300,440,0.5),("presenting",440,440,0.5)]),
 ("카드 · 현금","card·cash","카드 현금","카드면 ‘카드 돼요?’, 현금이면 ‘현금으로 할게요.’ 작은 가게는 현금만 받기도 해요.",
  "Card: ‘카드 돼요?’ Cash: ‘현금으로 할게요.’ Small shops may be cash-only.",CO,[("pay_card",440,440,0.5),("pay_cash",440,440,0.5)]),
 ("영수증 주세요","Receipt","영수증 주세요","영수증이 필요하면 ‘영수증 주세요.’ 얼마 냈는지 적힌 종이예요.",
  "Need a receipt? ‘영수증 주세요.’ It shows what you paid.",CO,[("get_receipt",440,440,1.0)]),
 ("또 오고 싶어요!","Come again!","또 오고 싶어요","맛있었으면 ‘여기 진짜 맛있었어요, 또 오고 싶어요!’ 따뜻한 한마디가 좋은 추억이 돼요.",
  "Loved it? ‘여기 진짜 맛있었어요, 또 오고 싶어요!’ A warm word makes a nice memory.",SU,[("walk_right",250,400,0.5),("wave",400,400,0.5)]),
 ("정리해요","Recap","찾기 주문 맛 계산","오늘 흐름을 볼까요? 찾기, 주문, 맛, 계산. 상황마다 어떤 말을 쓰는지 이제 아시죠? 정말 잘 하셨어요!",
  "Today's flow: find, order, taste, pay. You know the phrases now, right? Great job!",SU,[("point_right",300,300,0.5),("presenting",300,300,0.5)]),
 ("다음에 또 만나요!","See you!","다음에 또 만나요","오늘 배운 표현, 식당에서 꼭 써 보세요. 쓸수록 자연스러워져요. 다음엔 카페 표현을 배워요. 안녕!",
  "Use today's phrases at a restaurant. The more you use them, the more natural. Next: cafe expressions. Bye!",SU,[("presenting",300,300,0.4),("wave",300,300,0.6)]),
]

os.makedirs(LET_DIR, exist_ok=True)
def make_glyph(text, path):
    SZ=160; f=ImageFont.truetype(FONT,SZ); tmp=Image.new("RGBA",(10,10)); dd=ImageDraw.Draw(tmp)
    if "/" in text: lines=[s.strip() for s in text.split("/")]
    else:
        toks=text.split(); w1=dd.textbbox((0,0),text,font=f)[2]
        if len(toks)>=6 or w1>1080: t=(len(toks)+2)//3; lines=[" ".join(toks[i:i+t]) for i in range(0,len(toks),t)]
        elif len(toks)>=3 or w1>720: h=(len(toks)+1)//2; lines=[" ".join(toks[:h])," ".join(toks[h:])]
        else: lines=[text]
    maxw=max(dd.textbbox((0,0),ln,font=f)[2] for ln in lines)
    if maxw>1120: SZ=int(SZ*1120/maxw); f=ImageFont.truetype(FONT,SZ)
    asc,desc=f.getmetrics(); lh=asc+desc; ws=[dd.textbbox((0,0),ln,font=f)[2] for ln in lines]
    W=max(ws)+36; H=lh*len(lines)+28; im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    for i,ln in enumerate(lines):
        w=dd.textbbox((0,0),ln,font=f)[2]
        for ox,oy in [(-3,0),(3,0),(0,-3),(0,3)]: d.text(((W-w)//2+ox,14+i*lh+oy),ln,font=f,fill=(255,255,255,235))
        d.text(((W-w)//2,14+i*lh),ln,font=f,fill=(40,34,28,255))
    bb=im.getbbox(); im=im.crop(bb) if bb else im; im.save(path); return lines

con=sqlite3.connect(DB); cur=con.cursor()
BASEP="assets/graphics/poses/mj_presenting.png"
r=cur.execute("SELECT id FROM assets WHERE file_path=?",(BASEP,)).fetchone()
if r: MADAM=r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",("마담제이W11v3base","mj_base","pose",BASEP,"W11 v3 base")); MADAM=cur.lastrowid
cur.execute("DELETE FROM scene_objects WHERE episode='KO-W11'")
cur.execute("DELETE FROM scenes WHERE episode='KO-W11'")
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'mjw11_s%'")
scols=[c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]
for i,(ck,ce,gl,sk,se,bg,beats) in enumerate(SC,1):
    sk=norm_quotes(sk); se=norm_quotes(se)
    rel=f"graphics/letters/w11_{i:02d}.png"; make_glyph(gl,f"assets/{rel}")   # 자산 png(폴백; write는 안 씀)
    r=cur.execute("SELECT id FROM assets WHERE file_path=?",(rel,)).fetchone()
    if r: gasset=r[0]
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",(f"W11글자_{gl[:8]}",f"w11_{i:02d}","letter",rel,"동동")); gasset=cur.lastrowid
    aseq=f"mjw11_s{i:02d}"
    # ★글자=파라메트릭 필기(write), 중앙(GCX)~오른편 끝까지 크게. 줄수 자동선택으로 폰트 최대화(사장님: 글자 크게)
    GCX=560; WB=1265-GCX; HB=340; CAP=150     # 가로=중앙~오른끝, 세로=상단(캐릭터 머리 위)
    best=None
    for _mc in range(4,17):
        _ls=wrap_write(gl,_mc); _nl=len(_ls); _mx=max(len(l) for l in _ls)
        _f=min(WB/(_mx*0.98), HB/(_nl*1.18), CAP)
        if best is None or _f>best[0]: best=(_f,_ls,_nl)
    size_px,lines,nlines=best; size_px=max(52,size_px); draw_text="\n".join(lines)
    gscale=round(size_px/200,3); blockH=nlines*size_px*1.18; gcy=int(28+blockH/2)
    spec={"cap_ko":ck,"cap_en":ce,"motion":"static","char_key":"madam_j_w11","char_mode":"teacher",
          "draw_font":"cafe24_dongdong","draw_dur":3.0,"draw_text":draw_text,"draw_align":"left","bg":bg,"place_en":PLACE,"anim_seq":aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) VALUES (?,?,?,?,?,?,?)",
                ("KO-W11",i,sk,se,json.dumps(spec,ensure_ascii=False),"",8.0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                ("KO-W11",i,gasset,GCX,gcy,gscale,3,"write",0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                ("KO-W11",i,MADAM,300,452,0.6,5,"gesture",0))
    bj=[{"name":p,"cycle":[p],"x_from":xf,"x_to":xt,"dur":d} for (p,xf,xt,d) in beats]
    fields={"seq_name":aseq,"beats_json":json.dumps(bj,ensure_ascii=False)}
    if "description" in scols: fields["description"]=f"마담제이 W11v3 {aseq}"
    ks=",".join(fields); qs=",".join("?"*len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})",list(fields.values()))
con.commit()
n=cur.execute("SELECT COUNT(*) FROM scenes WHERE episode='KO-W11'").fetchone()[0]
con.close(); print(f"완료: KO-W11 v3 {n}씬 (~8분, 전부 오른쪽, 앉기 테이블근처 SX={SX})")
