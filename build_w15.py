# -*- coding: utf-8 -*-
"""W15(날씨와 사계절) 76씬 ~10분: 지은, 한라산 사계절.
★계절별로 char_key(옷)가 바뀐다: jieun_w15 한 캐릭터, 포즈이름 앞에 계절 프리픽스.
★포즈 PNG는 발끝 y700 정규화됨 → 좌표 하나(CHAR_CX,CY,SCALE)로 통일(W11/W14 규격).
★자막의 한글을 화면 파라메트릭 드로잉으로도 최대한 렌더(draw_text) — 사장님 지시.
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
PLACE = "Hallasan, Jeju"
EP = "KO-W15"
CHAR = "jieun_w15"
CHAR_CX, CHAR_CY, CHAR_SCALE = 300, 452, 0.655   # 발끝 y700 정규화와 맞물림

# 포즈는 "계절_동작". 배경은 bg_w15_*.
# (cap_ko, cap_en, glyph(화면 큰 한글), script_kr, script_en, bg, [(pose, x_from, x_to, ratio)])
SC = [
 # ── 1막 도입 (봄옷) S1~S8 ──
 ("한라산에 왔어요!","At Hallasan!","한라산",
  "안녕하세요! 오늘은 한라산에 왔어요. 한라산은 사계절이 모두 아름다운 산이에요.",
  "Hello! Today we're at '한라산' [Hallasan]. It's a mountain beautiful in all four seasons.",
  "bg_w15_halla_view",[("spring_walk1",-120,180,0.2),("spring_walk2",180,300,0.2),("spring_greeting",300,300,0.25),("spring_presenting",300,300,0.35)]),
 ("날씨","weather","날씨",
  "'날씨'는 하늘의 상태예요. 맑음, 흐림, 비, 눈 — 매일 바뀌어요.",
  "'날씨' [nal-ssi] means the weather. Clear, cloudy, rain, snow — it changes every day.",
  "bg_w15_halla_view",[("spring_presenting_a",300,300,0.2),("spring_presenting",300,300,0.8)]),
 ("날씨가 어때요?","How's the weather?","날씨가 / 어때요?",
  "누군가를 만나면 물어봐요. '날씨가 어때요?' 대화를 여는 좋은 질문이에요.",
  "When you meet someone, ask: '날씨가 어때요?' (How's the weather?). A great way to start a chat.",
  "bg_w15_spring_sky",[("spring_speak" if False else "spring_presenting",300,300,0.3),("spring_point_right",300,300,0.7)]),
 ("사계절","four seasons","사계절",
  "한국에는 네 계절이 있어요. 이걸 '사계절'이라고 해요.",
  "Korea has four seasons. We call them '사계절' [sa-gye-jeol].",
  "bg_w15_halla_view",[("spring_presenting",300,300,0.5),("spring_cheering",300,300,0.5)]),
 ("봄 여름 가을 겨울","spring summer fall winter","봄 여름 / 가을 겨울",
  "봄, 여름, 가을, 겨울. 한라산은 계절마다 옷을 갈아입어요.",
  "'봄' (spring), '여름' (summer), '가을' (fall), '겨울' (winter). Hallasan changes clothes each season.",
  "bg_w15_halla_view",[("spring_presenting_a",300,300,0.2),("spring_presenting",300,300,0.8)]),
 ("오늘의 약속","today's promise","같이 봐요",
  "한라산의 사계절을 하나씩 만나 볼까요? 계절마다 날씨도, 풍경도 달라져요.",
  "Shall we meet Hallasan's four seasons one by one? The weather and scenery change each time.",
  "bg_w15_spring_sky",[("spring_point_right",300,300,0.4),("spring_presenting",300,300,0.6)]),
 ("-에는","in (a season)","봄에는",
  "'-에는'은 그 계절을 말해요. 봄에는, 여름에는, 가을에는, 겨울에는.",
  "'-에는' [-e-neun] marks a season: 봄에는 (in spring), 겨울에는 (in winter).",
  "bg_w15_spring_sky",[("spring_presenting",300,300,1.0)]),
 ("자, 봄부터!","Let's start with spring!","봄부터",
  "그럼 봄부터 시작해요. 한라산의 봄으로 가 볼까요?",
  "Let's start with spring. Shall we go to Hallasan in spring?",
  "bg_w15_spring_ridge",[("spring_excited",300,300,0.4),("spring_walk1",300,380,0.3),("spring_walk2",380,460,0.3)]),

 # ── 2막 봄 (봄옷) S9~S22 ──
 ("봄","spring","봄",
  "'봄'이에요. 겨우내 얼었던 땅이 녹고, 날이 따뜻해져요.",
  "It's '봄' [bom] — spring. The frozen ground melts and days grow warm.",
  "bg_w15_spring_ridge",[("spring_presenting_a",300,300,0.2),("spring_presenting",300,300,0.8)]),
 ("따뜻하다","to be warm","따뜻하다",
  "'따뜻하다.' 봄 날씨는 춥지도 덥지도 않아요. 딱 좋아요.",
  "'따뜻하다' [tta-tteut-ha-da] — to be warm. Spring isn't cold or hot. Just right.",
  "bg_w15_spring_ridge",[("spring_presenting",300,300,0.5),("spring_relax" if False else "spring_cheering",300,300,0.5)]),
 ("봄에는 따뜻해요","In spring it's warm","봄에는 / 따뜻해요",
  "'봄에는 따뜻해요.' 형용사에 '-아요/어요'를 붙여요.",
  "'봄에는 따뜻해요' (In spring, it's warm). Add '-아요/어요' to adjectives.",
  "bg_w15_spring_sky",[("spring_presenting",300,300,1.0)]),
 ("꽃이 피다","flowers bloom","꽃이 피다",
  "'꽃이 피다.' 봄이 되면 꽃이 펴요.",
  "'꽃이 피다' [kkoch-i-pi-da] — flowers bloom. In spring, flowers open up.",
  "bg_w15_jindallae",[("spring_point_up",300,300,0.5),("spring_look_up",300,300,0.5)]),
 ("선작지왓","Seonjakjiwat","선작지왓",
  "여기는 '선작지왓'이에요. 봄이면 산철쭉이 분홍 바다처럼 펴요. 산 위의 꽃밭이에요!",
  "This is '선작지왓' [Seonjakjiwat]. In spring, royal azaleas bloom like a pink sea — a garden in the sky!",
  "bg_w15_seonjakji",[("spring_cheering",300,300,1.0)]),
 ("벚꽃","cherry blossom","벚꽃",
  "'벚꽃'도 봄의 꽃이에요. 바람이 불면 꽃잎이 눈처럼 날려요.",
  "'벚꽃' [beot-kkot] — cherry blossom. When wind blows, petals fly like snow.",
  "bg_w15_cherry",[("spring_look_up",300,300,1.0)]),
 ("바람이 불다","wind blows","바람이 불다",
  "'바람이 불다.' 봄바람은 부드럽고 따뜻해요.",
  "'바람이 불다' [ba-ram-i-bul-da] — the wind blows. Spring wind is soft and warm.",
  "bg_w15_cherry",[("spring_presenting_a",300,300,0.3),("spring_presenting",300,300,0.7)]),
 ("봄바람이 불어요","Spring wind blows","봄바람이 / 불어요",
  "'봄바람이 불어요.' '-이/가 불다'는 바람에 써요.",
  "'봄바람이 불어요' (Spring wind blows). Use '-이/가 불다' for wind.",
  "bg_w15_cherry",[("spring_presenting",300,300,1.0)]),
 ("맑다","to be clear","맑다",
  "'맑다.' 하늘에 구름이 없고 파래요. '오늘은 맑아요.'",
  "'맑다' [mak-da] — to be clear. No clouds, blue sky. '오늘은 맑아요' (It's clear today).",
  "bg_w15_spring_ridge",[("spring_point_up",300,300,0.4),("spring_presenting",300,300,0.6)]),
 ("소풍","picnic","소풍",
  "따뜻하고 맑은 봄날엔 소풍을 가요. 지은이도 신났어요!",
  "On a warm, clear spring day, we go on a '소풍' [so-pung] (picnic). Jieun is excited!",
  "bg_w15_spring_ridge",[("spring_excited",300,300,1.0)]),
 ("얇은 옷","light clothes","얇은 옷",
  "봄에는 얇은 옷을 입어요. 카디건 하나면 충분해요.",
  "In spring, wear light clothes. A cardigan is enough.",
  "bg_w15_spring_sky",[("spring_presenting",300,300,0.5),("spring_point_right",300,300,0.5)]),
 ("봄 정리","spring review","봄 정리",
  "봄: 따뜻하다, 꽃이 피다, 바람이 불다. 기억하세요!",
  "Spring: 따뜻하다 (warm), 꽃이 피다 (bloom), 바람이 불다 (windy). Remember!",
  "bg_w15_spring_sky",[("spring_presenting_a",300,300,0.2),("spring_presenting",300,300,0.8)]),
 ("다음 계절","next season","다음 계절",
  "봄이 지나면? 점점 더워져요.",
  "After spring? It gets hotter and hotter.",
  "bg_w15_spring_ridge",[("spring_thinking" if False else "spring_presenting",300,300,0.4),("spring_point_right",300,300,0.6)]),
 ("여름으로!","To summer!","여름으로",
  "이제 여름이에요. 옷을 갈아입을게요!",
  "Now it's summer. Let me change clothes!",
  "bg_w15_seongpanak",[("spring_walk1",300,380,0.5),("spring_walk2",380,470,0.5)]),

 # ── 3막 여름 (여름옷→우비) S23~S37 ──
 ("여름","summer","여름",
  "이제 '여름'이에요. 한라산이 온통 초록으로 우거졌어요!",
  "Now it's '여름' [yeo-reum] — summer. Hallasan is lush and green all over!",
  "bg_w15_seongpanak",[("summer_base",300,300,0.3),("summer_presenting",300,300,0.7)]),
 ("덥다","to be hot","덥다",
  "'덥다.' 여름은 아주 더워요. '너무 더워요!'",
  "'덥다' [deop-da] — to be hot. Summer is very hot. '너무 더워요!' (So hot!)",
  "bg_w15_seongpanak",[("summer_fan",300,300,1.0)]),
 ("여름에는 더워요","In summer it's hot","여름에는 / 더워요",
  "'여름에는 더워요.' 반대말은 춥다예요.",
  "'여름에는 더워요' (In summer, it's hot). The opposite is 춥다 (cold).",
  "bg_w15_seongpanak",[("summer_presenting",300,300,1.0)]),
 ("습하다","to be humid","습하다",
  "'습하다.' 한국의 여름은 덥고 습해요. 끈적끈적해요.",
  "'습하다' [seup-ha-da] — to be humid. Korean summer is hot and humid. Sticky!",
  "bg_w15_1100_summer",[("summer_fan",300,300,0.5),("summer_presenting",300,300,0.5)]),
 ("장마 / 비가 오다","rainy season / it rains","장마",
  "여름에는 '장마'가 있어요. 비가 많이 와요. '비가 와요.'",
  "Summer has '장마' [jang-ma] — the rainy season. It rains a lot. '비가 와요' (It rains).",
  "bg_w15_1100_summer",[("summer_point_right",300,300,0.5),("summer_presenting",300,300,0.5)]),
 ("비가 오다","it rains","비가 오다",
  "'-이/가 오다.' 비가 오다, 눈이 오다. 하늘에서 내리는 건 '오다'를 써요.",
  "'-이/가 오다' — 비가 오다 (rain), 눈이 오다 (snow). Use 오다 for what falls from the sky.",
  "bg_w15_rainy",[("summer_presenting",300,300,1.0)]),
 ("우비 · 우산","raincoat · umbrella","우비 우산",
  "비가 오면 우비를 입고 우산을 써요. 노란 우비를 입은 지은이!",
  "When it rains, wear a '우비' [u-bi] (raincoat) and use a '우산' (umbrella). Jieun in a yellow raincoat!",
  "bg_w15_rainy",[("rain_umbrella",300,300,1.0)]),
 ("소나기","sudden shower","소나기",
  "여름엔 갑자기 '소나기'가 쏟아지기도 해요. 잠깐 세게 내리고 그쳐요.",
  "In summer, a '소나기' [so-na-gi] (sudden shower) can pour down — hard and brief.",
  "bg_w15_rainy",[("rain_surprise",300,300,0.5),("rain_umbrella",300,300,0.5)]),
 ("사라오름","Saraoreum","사라오름",
  "비가 온 뒤 '사라오름'에 오면 분화구에 호수가 생겨요. 신비로워요!",
  "After rain, '사라오름' [Saraoreum] forms a lake in its crater. So mystical!",
  "bg_w15_saraoreum",[("rain_walk1",280,320,0.3),("summer_relax",300,300,0.7)]),
 ("시원하다","to be cool","시원하다",
  "비가 그치고 그늘에 들어가면? '시원하다.' 아, 시원해요!",
  "Rain stops, step into shade — '시원하다' [si-won-ha-da] (cool). Ah, refreshing!",
  "bg_w15_saraoreum",[("summer_relax",300,300,1.0)]),
 ("돈내코","Donnaeko","돈내코",
  "더운 여름엔 '돈내코' 계곡으로! 에메랄드빛 물이 정말 시원해요.",
  "On a hot day, head to '돈내코' [Donnaeko] valley! Emerald water, so cool.",
  "bg_w15_donnaeko",[("summer_cheering",300,300,1.0)]),
 ("수박","watermelon","수박",
  "더운 여름엔 시원한 수박을 먹어요. 최고예요!",
  "In hot summer, eat cool '수박' [su-bak] (watermelon). The best!",
  "bg_w15_donnaeko",[("summer_eat",300,300,1.0)]),
 ("반팔 · 반바지","short sleeves · shorts","반팔 반바지",
  "여름에는 반팔과 반바지를 입어요. 시원하게!",
  "In summer, wear '반팔' (short sleeves) and '반바지' (shorts). Stay cool!",
  "bg_w15_seongpanak",[("summer_presenting",300,300,0.5),("summer_point_right",300,300,0.5)]),
 ("여름 정리","summer review","여름 정리",
  "여름: 덥다, 습하다, 비가 오다. 우산 잊지 마세요!",
  "Summer: 덥다 (hot), 습하다 (humid), 비가 오다 (rains). Don't forget your umbrella!",
  "bg_w15_seongpanak",[("summer_presenting_a",300,300,0.2),("summer_presenting",300,300,0.8)]),
 ("가을로!","To autumn!","가을로",
  "무더운 여름이 지나가면? 시원한 가을이 와요. 옷 갈아입을게요!",
  "After the hot summer? Cool autumn comes. Let me change clothes!",
  "bg_w15_eorimok_fall",[("summer_walk1",300,380,0.5),("summer_walk2",380,470,0.5)]),

 # ── 4막 가을 (가을옷) S38~S51 ──
 ("가을","autumn","가을",
  "이제 '가을'이에요. 한라산이 붉게 물들기 시작했어요!",
  "Now it's '가을' [ga-eul] — autumn. Hallasan is starting to turn red!",
  "bg_w15_eorimok_fall",[("autumn_base",300,300,0.3),("autumn_presenting",300,300,0.7)]),
 ("선선하다","to be cool/crisp","선선하다",
  "가을은 '선선해요.' 덥지도 춥지도 않아 딱 좋아요.",
  "Autumn is '선선하다' [seon-seon-ha-da] (crisp). Not hot, not cold. Just right.",
  "bg_w15_eorimok_fall",[("autumn_presenting",300,300,0.5),("autumn_happy",300,300,0.5)]),
 ("가을에는 시원해요","In autumn it's cool","가을에는 / 시원해요",
  "'가을에는 시원해요.' 산책하기 좋은 계절이에요.",
  "'가을에는 시원해요' (In autumn, it's cool). A great season for a walk.",
  "bg_w15_eorimok_fall",[("autumn_presenting",300,300,1.0)]),
 ("하늘이 높다","the sky is high","하늘이 높다",
  "'하늘이 높다.' 가을 하늘은 아주 높고 파래요.",
  "'하늘이 높다' [ha-neul-i-nop-da] — the sky is high. Autumn sky is high and blue.",
  "bg_w15_eorimok_fall",[("autumn_look_up",300,300,1.0)]),
 ("단풍","autumn leaves","단풍",
  "'단풍'이에요. 잎이 빨갛고 노랗게 물들어요.",
  "'단풍' [dan-pung] — autumn foliage. Leaves turn red and yellow.",
  "bg_w15_yeongsil",[("autumn_point_right",300,300,0.4),("autumn_presenting",300,300,0.6)]),
 ("영실기암","Yeongsil rocks","영실기암",
  "여기는 '영실기암'! 병풍 같은 절벽에 단풍이 들면 한라산 최고의 절경이에요!",
  "This is '영실기암' [Yeongsil]! Foliage on these screen-like cliffs — Hallasan's finest view!",
  "bg_w15_yeongsil",[("autumn_cheering",300,300,1.0)]),
 ("단풍이 들다","leaves turn color","단풍이 들다",
  "'단풍이 들다.' 한라산이 온통 빨강, 주황, 노랑으로 물들어요!",
  "'단풍이 들다' — leaves change color. Hallasan turns red, orange, and yellow!",
  "bg_w15_yeongsil",[("autumn_presenting",300,300,0.4),("autumn_cheering",300,300,0.6)]),
 ("사라오름 단풍","Saraoreum in fall","사라오름 / 단풍",
  "가을 '사라오름'은 산정호수에 단풍이 비쳐 그림 같아요.",
  "Autumn '사라오름' reflects foliage in its crater lake — like a painting.",
  "bg_w15_sara_fall",[("autumn_look_up",300,300,0.4),("autumn_happy",300,300,0.6)]),
 ("낙엽","fallen leaves","낙엽",
  "단풍잎이 떨어지면 '낙엽'이 돼요. 밟으면 바스락 소리가 나요.",
  "Fallen leaves are '낙엽' [nak-yeop]. Step on them — crunch, crunch!",
  "bg_w15_sara_fall",[("autumn_step_leaves",300,300,1.0)]),
 ("건조하다","to be dry","건조하다",
  "'건조하다.' 가을 공기는 건조해요. 촉촉하지 않아요.",
  "'건조하다' [geon-jo-ha-da] — to be dry. Autumn air is dry, not moist.",
  "bg_w15_sara_fall",[("autumn_presenting",300,300,1.0)]),
 ("억새","silver grass","억새",
  "'어리목'엔 은빛 억새가 바람에 흔들려요. 가을이 깊었어요.",
  "At '어리목' [Eorimok], silver '억새' [eok-sae] (grass) sways in the wind. Deep autumn.",
  "bg_w15_eogsae",[("autumn_point_right",300,300,0.4),("autumn_look_up",300,300,0.6)]),
 ("가을 음식","autumn food","가을 음식 / 감 밤 고구마",
  "가을엔 맛있는 게 많아요. '감', '밤', '고구마'! 배부른 계절이에요.",
  "Autumn has tasty food: '감' (persimmon), '밤' (chestnut), '고구마' (sweet potato)! A full-belly season.",
  "bg_w15_eogsae",[("autumn_happy",300,300,1.0)]),
 ("긴팔 · 겉옷","long sleeves · jacket","긴팔 겉옷",
  "가을에는 긴팔에 얇은 겉옷을 걸쳐요. 아침저녁으로 쌀쌀해요.",
  "In autumn, wear '긴팔' (long sleeves) with a light jacket. Chilly mornings and evenings.",
  "bg_w15_eogsae",[("autumn_presenting",300,300,0.5),("autumn_point_right",300,300,0.5)]),
 ("겨울로!","To winter!","겨울로",
  "가을이 깊어지면? 이제 추운 겨울이에요. 따뜻하게 입을게요!",
  "As autumn deepens? Now comes cold winter. Let me bundle up!",
  "bg_w15_witse_snow",[("autumn_walk1",300,380,0.5),("autumn_walk2",380,470,0.5)]),

 # ── 5막 겨울 (겨울옷→방한복→등산복) S52~S69 ──
 ("겨울","winter","겨울",
  "이제 '겨울'이에요. 한라산에 하얀 눈이 내리기 시작했어요!",
  "Now it's '겨울' [gyeo-ul] — winter. White snow begins to fall on Hallasan!",
  "bg_w15_witse_snow",[("winter_base",300,300,0.3),("winter_presenting",300,300,0.7)]),
 ("춥다","to be cold","춥다",
  "'춥다.' 겨울은 아주 추워요. '너무 추워요!'",
  "'춥다' [chup-da] — to be cold. Winter is very cold. '너무 추워요!' (So cold!)",
  "bg_w15_witse_snow",[("winter_shiver",300,300,1.0)]),
 ("겨울에는 추워요","In winter it's cold","겨울에는 / 추워요",
  "'겨울에는 추워요.' 봄의 따뜻하다와 반대예요.",
  "'겨울에는 추워요' (In winter, it's cold). The opposite of spring's 따뜻하다.",
  "bg_w15_witse_snow",[("winter_presenting",300,300,1.0)]),
 ("첫눈","first snow","첫눈",
  "겨울의 시작, 그해 처음 내리는 눈을 '첫눈'이라고 해요. 설레는 순간이에요!",
  "The season's first snow is '첫눈' [cheot-nun]. Such an exciting moment!",
  "bg_w15_firstsnow",[("winter_firstsnow",300,300,1.0)]),
 ("눈이 오다","it snows","눈이 오다",
  "'눈이 와요.' 하얀 눈이 펑펑 내려요.",
  "'눈이 와요' (It's snowing). White snow falls thick and fast.",
  "bg_w15_firstsnow",[("winter_catch_snow",300,300,1.0)]),
 ("눈이 오다 (문법)","it snows (grammar)","눈이 오다",
  "비가 오다, 눈이 오다. 똑같이 '-이/가 오다'예요.",
  "비가 오다 (rain), 눈이 오다 (snow) — both use '-이/가 오다'.",
  "bg_w15_firstsnow",[("winter_presenting_a",300,300,0.2),("winter_presenting",300,300,0.8)]),
 ("눈사람","snowman","눈사람",
  "눈이 쌓이면 '눈사람'을 만들어요. 지은이가 눈사람을 만들어요!",
  "When snow piles up, make a '눈사람' [nun-sa-ram] (snowman). Jieun is building one!",
  "bg_w15_snowfield",[("winter_snowman",300,300,1.0)]),
 ("눈싸움","snowball fight","눈싸움",
  "친구랑 '눈싸움'도 해요. 겨울의 즐거움이에요!",
  "Have a '눈싸움' [nun-ssa-um] (snowball fight) with friends. Winter fun!",
  "bg_w15_snowfield",[("winter_snowball",300,300,1.0)]),
 ("얼다","to freeze","얼다",
  "'얼다.' 너무 추우면 물이 얼어요. 강도 얼고, 손도 꽁꽁 얼어요.",
  "'얼다' [eol-da] — to freeze. When it's cold, water freezes. Rivers freeze, hands freeze!",
  "bg_w15_snowfield",[("winter_shiver",300,300,0.5),("winter_presenting",300,300,0.5)]),
 ("영하","below zero","영하",
  "온도가 0도 아래로 내려가면 '영하'예요. '오늘은 영하 5도예요.'",
  "Below zero is '영하' [yeong-ha]. '오늘은 영하 5도예요' (It's -5°C today).",
  "bg_w15_snowfield",[("winter_presenting",300,300,1.0)]),
 ("1100고지 상고대","1100 Godji frost","1100고지 / 상고대",
  "'1100고지'엔 나뭇가지에 얼음꽃이 펴요. '상고대'라고 해요. 보석처럼 반짝여요!",
  "At '1100고지', ice flowers bloom on branches — '상고대' [sang-go-dae]. Sparkling like jewels!",
  "bg_w15_1100_sanggodae",[("winter_cheering",300,300,1.0)]),
 ("두꺼운 옷","thick clothes","두꺼운 옷",
  "겨울엔 두꺼운 옷을 입어요. 스웨터에 코트, 목도리까지.",
  "In winter, wear thick clothes — sweater, coat, and a scarf.",
  "bg_w15_1100_sanggodae",[("winter_presenting",300,300,0.5),("winter_point_right" if False else "winter_presenting_a",300,300,0.5)]),
 ("너무 추워요!","So cold!","너무 추워요",
  "그런데 한라산 꼭대기는 더 추워요. 이 정도로는 부족해요!",
  "But Hallasan's peak is even colder. This isn't enough!",
  "bg_w15_byeongpung_snow",[("winter_shiver_hard",300,300,1.0)]),
 ("방한복","winter gear","방한복",
  "그래서 완벽하게 준비했어요! 두꺼운 롱패딩, 털모자, 목도리, 장갑까지!",
  "So I got fully ready! A thick long padded coat, fur hat, scarf, and gloves — '방한복' [bang-han-bok]!",
  "bg_w15_byeongpung_snow",[("winterpad_base",300,300,0.3),("winterpad_presenting",300,300,0.7)]),
 ("이제 따뜻해요","Now I'm warm","이제 / 따뜻해요",
  "이제 하나도 안 추워요. 방한복이 최고예요!",
  "Now I'm not cold at all. Winter gear is the best!",
  "bg_w15_byeongpung_snow",[("winterpad_warm",300,300,1.0)]),
 ("정상까지 올라가요!","Up to the top!","등산",
  "자, 이제 한라산 꼭대기 백록담까지 올라가요! '등산'을 시작해요. 영차영차!",
  "Now let's go up to Baengnokdam at the very top! Let's start our '등산' (hike). Up we go!",
  "bg_w15_byeongpung_snow",[("winterpad_walk1",250,300,0.3),("winterpad_walk2",300,340,0.3),("winterpad_presenting",340,340,0.4)]),
 ("백록담","Baengnokdam","백록담",
  "드디어 정상! 눈 덮인 '백록담'이에요. 하얀 분화구가 온 세상을 품었어요!",
  "The peak at last! Snow-covered '백록담' [Baengnokdam]. A white crater holding the whole world!",
  "bg_w15_baengnokdam",[("winterpad_amazed",300,300,1.0)]),
 ("눈 덮인 한라산","snowy Hallasan","눈 덮인 / 한라산",
  "눈 덮인 한라산은 정말 장관이에요. 하얀 세상이 펼쳐져요!",
  "Snowy Hallasan is truly magnificent. A white world unfolds!",
  "bg_w15_baengnokdam",[("winterpad_amazed",300,300,0.5),("winterpad_warm",300,300,0.5)]),
 ("겨울 정리","winter review","겨울 정리",
  "겨울: 춥다, 눈이 오다, 얼다, 첫눈, 상고대. 따뜻하게 입으세요!",
  "Winter: 춥다 (cold), 눈이 오다 (snows), 얼다 (freeze), 첫눈, 상고대. Bundle up!",
  "bg_w15_witse_snow",[("winter_presenting_a",300,300,0.2),("winter_presenting",300,300,0.8)]),

 # ── 6막 정리 (봄옷 복귀) S70~S76 ──
 ("한 바퀴!","Full circle!","한 바퀴",
  "봄, 여름, 가을, 겨울 — 한라산을 한 바퀴 돌았어요!",
  "Spring, summer, autumn, winter — we circled all of Hallasan!",
  "bg_w15_halla_view",[("spring_walk1",-100,180,0.25),("spring_cheering",300,300,0.75)]),
 ("날씨 복습","weather review","날씨 복습",
  "따뜻하다, 덥다, 시원하다, 춥다. 계절마다 날씨가 달라요.",
  "따뜻하다 (warm), 덥다 (hot), 시원하다 (cool), 춥다 (cold). Each season differs.",
  "bg_w15_halla_view",[("spring_presenting_a",300,300,0.2),("spring_presenting",300,300,0.8)]),
 ("오다 · 불다","falls · blows","비가 와요",
  "비가 와요, 눈이 와요, 바람이 불어요. 기억나죠?",
  "비가 와요 (rain), 눈이 와요 (snow), 바람이 불어요 (wind). Remember?",
  "bg_w15_spring_sky",[("spring_point_up",300,300,0.4),("spring_presenting",300,300,0.6)]),
 ("무슨 계절을 좋아해요?","Which season do you like?","무슨 계절을 / 좋아해요?",
  "여러분은 무슨 계절을 좋아해요? 저는… 다 좋아요!",
  "Which season do you like? Me… I like them all!",
  "bg_w15_halla_sunset",[("spring_cheering",300,300,1.0)]),
 ("한라산은 멋져요","Hallasan is wonderful","한라산은 / 멋져요",
  "한라산은 계절마다 다른 얼굴을 보여줘요. 정말 멋진 산이죠?",
  "Hallasan shows a different face each season. What a wonderful mountain!",
  "bg_w15_halla_sunset",[("spring_presenting",300,300,0.5),("spring_cheering",300,300,0.5)]),
 ("또 만나요","See you again","또 만나요",
  "다음 시간에 또 만나요. 안녕히 계세요!",
  "See you next time. Goodbye!",
  "bg_w15_halla_sunset",[("spring_wave",300,300,1.0)]),
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
# 캐릭터 asset(대표=봄 base) — 렌더러는 char_key로 포즈를 찾으니 asset은 자리표시
BASEP = "assets/graphics/poses/jieun_w15_spring_base.png"
r = cur.execute("SELECT id FROM assets WHERE file_path=?", (BASEP,)).fetchone()
if r: JI = r[0]
else:
    cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                ("지은W15base", "jieun_w15_spring_base", "pose", BASEP, "W15 base")); JI = cur.lastrowid

cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
cur.execute("DELETE FROM anim_sequences WHERE seq_name LIKE 'jiw15_s%'")
scols = [c[1] for c in cur.execute("PRAGMA table_info(anim_sequences)")]

for i, (ck, ce, gl, sk, se, bg, beats) in enumerate(SC, 1):
    sk = norm_quotes(sk); se = norm_quotes(se)
    rel = f"graphics/letters/w15_{i:02d}.png"; make_glyph(gl, f"assets/{rel}")
    r = cur.execute("SELECT id FROM assets WHERE file_path=?", (rel,)).fetchone()
    if r: gasset = r[0]
    else:
        cur.execute("INSERT INTO assets (name_kr,name_en,type,file_path,flow_prompt) VALUES (?,?,?,?,?)",
                    (f"W15글자_{gl[:8]}", f"w15_{i:02d}", "letter", rel, "동동")); gasset = cur.lastrowid
    aseq = f"jiw15_s{i:02d}"
    GCX = 560; WB = 1265 - GCX; HB = 340; CAP = 150
    best = None
    for _mc in range(4, 17):
        _ls = wrap_write(gl, _mc); _nl = len(_ls); _mx = max(len(l) for l in _ls)
        _f = min(WB / (_mx * 0.98), HB / (_nl * 1.18), CAP)
        if best is None or _f > best[0]: best = (_f, _ls, _nl)
    size_px, lines, nlines = best; size_px = max(52, size_px)
    draw_text = "\n".join(lines)
    gscale = round(size_px / 200, 3); blockH = nlines * size_px * 1.18; gcy = int(28 + blockH / 2)
    spec = {"cap_ko": ck, "cap_en": ce, "motion": "static", "char_key": CHAR, "char_mode": "teacher",
            "draw_font": "cafe24_dongdong", "draw_dur": 3.0, "draw_text": draw_text, "draw_align": "left",
            "bg": bg, "place_en": PLACE, "anim_seq": aseq}
    cur.execute("INSERT INTO scenes (episode,seq,script_kr,script_en,image_prompt,veo_prompt,duration_sec) VALUES (?,?,?,?,?,?,?)",
                (EP, i, sk, se, json.dumps(spec, ensure_ascii=False), "", 8.0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                (EP, i, gasset, GCX, gcy, gscale, 3, "write", 0))
    cur.execute("INSERT INTO scene_objects (episode,scene_seq,asset_id,cx,cy,scale,z_order,motion_type,is_point) VALUES (?,?,?,?,?,?,?,?,?)",
                (EP, i, JI, CHAR_CX, CHAR_CY, CHAR_SCALE, 5, "gesture", 0))
    bj = [{"name": p, "cycle": [p], "x_from": xf, "x_to": xt, "dur": d} for (p, xf, xt, d) in beats]
    fields = {"seq_name": aseq, "beats_json": json.dumps(bj, ensure_ascii=False)}
    if "description" in scols: fields["description"] = f"지은 W15 {aseq}"
    ks = ",".join(fields); qs = ",".join("?" * len(fields))
    cur.execute(f"INSERT INTO anim_sequences ({ks}) VALUES ({qs})", list(fields.values()))

con.commit()
n = cur.execute("SELECT COUNT(*) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
bgs = sorted({s[5] for s in SC}); poses = sorted({b[0] for s in SC for b in s[6]})
con.close()
print(f"완료: {EP} {n}씬 (~10분, 지은, 한라산 사계절)")
print(f"배경 {len(bgs)}종 / 포즈 {len(poses)}종 사용")
