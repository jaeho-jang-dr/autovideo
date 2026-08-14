# -*- coding: utf-8 -*-
"""W1-2 (모음의 확장 · 광화문광장) 시나리오 → DB. 26씬.

원천 : `W1_2/W1_2_scenario.md`(나레이션·화면글자) · `W1_2/W1_2_motion.md`(동선·맞물림)
       · `W1_2/w12_manifest.py`(씬→자산) · `channel/content.db` `char_heights`(키)
출력 : `scenes` · `scene_objects`  (episode = 'KO-W1-2')

★[[build-script-edit-needs-db-rerun]] : 나레이션·자막을 고쳤으면 **이 스크립트를 다시
  돌려야** DB 에 반영된다. 순서 = 빌드 → DB 실측 → 캐시 삭제 → 렌더.

## 이 판의 규격 (2026-08-12 사장님 확정)
- 글자 : 화면 **상반부 · 가로 중앙 · 최대 세 줄**. 씬마다 옮기지 않는다
- 캐릭터 : 구역 제한 없음. 글자에 걸리면 아래로 지나가거나 굴러 빠지거나 멀어져 작아진다
- 큰 동작은 **멀리서 작게**(백플립 M2·앞구르기 D1)
- 키 : `char_heights.base_h`(스틱맨 700 · 졸라맨 711 · 졸라걸 651) × 깊이배율
- 배경 : 8초 클립을 **한 번만 재생하고 마지막 프레임을 붙든다**(loop 금지)

    python build_w12.py [--dry]
"""
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

import w12_manifest as MAN                               # noqa: E402

DB = "channel/content.db"
EP = "KO-W1-2"
PLACE = "Gwanghwamun Square, Seoul"
CANVAS_W, CANVAS_H = 1280, 720

# 깊이표 — 라벨: (화면 키, 발 y)
#
# ★★사장님 확정(2026-08-13) — 두 번 오해했다가 바로잡은 것이니 여기 적어 둔다.
#   "앞줄은 여태 캐릭터가 서서 설명하던 **자막 바로 위**에서 700 정도의 사이즈(스틱맨)로
#    하면 되고, 보조 캐릭터는 **그 뒤 어느 곳 600~1** 까지의 사이즈로 움직이면 된다."
#   "**기준 척도가 700**인데, 여태 **나레이터로 나오던 캐릭터의 사이즈** 대로 하면 된다."
#
#   → 700 은 **화면 픽셀이 아니라 척도**다. 스틱맨의 실물 키를 700 으로 삼는다.
#     화면 키 700 으로 그렸더니 캐릭터가 화면을 꽉 채우고 글자와 겹쳤다(확인 그림).
#
# ★앞줄 화면 키 = **400** (사장님 확정 2026-08-13 "앞줄 400으로 가자")
#   근거 — W19·W21·W22·W23 나레이터는 넷 다 몸높이 770 × scale 0.561 = **화면 432px**.
#   W24 도 같은 432(제일 큰 인준에 맞추고 나머지는 비율로). 스틱맨은 규격이 749→700 으로
#   낮아졌으므로 같은 배율이면 393. 그 사이에서 **400** 으로 확정했다.
#   → 발 y 는 F0(400, 668)에서 지평선 452.9 로 한 줄로 푼다: 발y = 452.9 + 키/1.860
#
# ★보조역(졸라맨·졸라걸)은 그 뒤로 **600 이하** 어디든. 작을수록 많이 움직여도 된다
#   ("작으면 많이 움직여도 표가 덜 난다"). 실제로는 앞줄 400보다 작은 자리에 세운다.
DEPTH = {"F0": (400, 668), "F1": (340, 636), "M": (280, 604),
         "M2": (220, 571), "D1": (170, 544), "D2": (120, 518), "V": (70, 491)}

# ★척도 — 스틱맨 실물 키. 머리의 아래위 높이가 비율을 정하는 척도다.
STD_H = 700
FRONT_H = 400                      # 앞줄(F0) 화면 키 — 나레이션 자리
# ★보조역(졸라맨·졸라걸) 화면 키 상한 — 600. 이보다 크면 주역과 헷갈린다.
SUB_MAX_H = 600

# 글자 자리 — 상반부 중앙 고정
TEXT_BOX = {"cx": 640, "cy": 200, "max_lines": 3, "max_w": 880, "side": "top-center"}

# (seq, 화면한글, KO 나레이션, EN 나레이션)
NARR = [
 (1, "ㅏ ㅓ ㅗ ㅜ ㅡ ㅣ ㅐ ㅔ",
  "안녕하세요! 지난 시간엔 단모음 여덟 개를 배웠죠. ㅏ, ㅓ, ㅗ, ㅜ, ㅡ, ㅣ, ㅐ, ㅔ.",
  "Hello! Last time we learned the eight simple vowels - ㅏ, ㅓ, ㅗ, ㅜ, ㅡ, ㅣ, ㅐ, ㅔ."),
 (2, "모음 + 모음 = 단어",
  "오늘은 그 모음만으로 단어를 만들어 볼 거예요. 자음은 하나도 쓰지 않습니다.",
  "Today we'll build whole words from those vowels alone. Not a single consonant."),
 (3, "아 = ㅇ + ㅏ",
  "글자를 쓸 때 앞자리에 동그라미 ㅇ이 앉지만, 소리는 나지 않아요. 자리만 지키는 빈 의자랍니다.",
  "When we write, a small circle ㅇ sits in front - but it makes no sound. It just holds the seat."),
 (4, "아이 이 오이 우유 오 아우 여우",
  "자, 광장으로 나가 볼까요? 오늘의 단어들이 이 광장 곳곳에 숨어 있어요.",
  "Shall we head out into the plaza? Today's words are hiding all around it."),
 (5, "아이",
  "첫 번째 단어, 아이. 어린아이를 뜻하는 말이에요. 받침 없이 ㅏ와 ㅣ, 모음 두 개로만 이루어졌어요.",
  "Our first word - 아이. It means a child. Just two vowels, ㅏ and ㅣ, and no batchim."),
 (6, "아 + 이 → 아이",
  "계단을 내려오듯 끊어서 두 번. 아 — 이. 이제 붙여서 한 번. 아이. 따라 해 보세요.",
  "Step down through it, one at a time. 아 - 이. Now together. 아이. Say it with me."),
 (7, "이",
  "두 번째, 이. 입을 옆으로 활짝 당겨 내는 ㅣ 하나면 단어가 돼요. 우리 몸의 이, 바로 치아를 뜻하지요.",
  "Second - 이. A single ㅣ, lips pulled wide, is already a word. It means a tooth."),
 (8, "오이",
  "어? 뭐가 굴러오네요. 세 번째 단어, 오이예요. 아삭아삭한 초록 채소죠. ㅗ와 ㅣ, 역시 모음 두 개예요.",
  "Oh - something's rolling this way. Our third word: 오이, a crunchy green cucumber. "
  "Again two vowels, ㅗ and ㅣ."),
 (9, "오 + 이 → 오이",
  "입술을 동그랗게 모았다가 옆으로 당기며. 오 — 이. 오이.",
  "Round your lips, then pull them wide. 오 - 이. 오이."),
 (10, "우유",
  "저건 놓치면 안 되겠네요! 네 번째, 우유. 하얗고 고소한 우유예요. "
  "ㅜ와 ㅠ, 둘 다 입술을 동그랗게 내미는 소리죠.",
  "Careful - don't let that one fall! Fourth: 우유, sweet white milk. "
  "Both ㅜ and ㅠ push the lips forward and round."),
 (11, "우 + 유 → 우유",
  "천천히. 우 — 유. 우유.",
  "Slowly now. 우 - 유. 우유."),
 (12, "아이 ↔ 오이",
  "아이와 오이. 뒷소리가 같지요? 둘 다 이로 끝나요. 앞소리 하나가 바뀌면 뜻이 달라집니다.",
  "아이 and 오이 - same ending, both end in 이. Change one sound in front and the meaning changes."),
 (13, "오",
  "우와! 다섯 번째, 오. 놀랄 때 오! 하고 내는 그 소리, 그대로 단어가 돼요.",
  "Whoa! Fifth - 오. The sound you make when you're surprised, 오!, is itself a word."),
 (14, "오 = 5",
  "그리고 오는 숫자 다섯이기도 해요. 하나, 둘, 셋, 넷, 다섯 — 오!",
  "And 오 also means the number five. One, two, three, four, five - 오!"),
 (15, "아우",
  "벤치에 누가 앉아 있네요. 여섯 번째 단어, 아우. 손아래 동생을 다정하게 부르는 말이에요.",
  "Someone's sitting on the bench. Sixth word - 아우, a warm word for a younger sibling."),
 (16, "아 + 우 → 아우",
  "ㅏ에서 ㅜ로. 입을 크게 열었다 동그랗게 모으며. 아 — 우. 아우.",
  "From ㅏ to ㅜ. Open wide, then round. 아 - 우. 아우."),
 (17, "ㅏ ㅗ / ㅓ ㅜ",
  "소리에도 온도가 있어요. ㅏ와 ㅗ는 밝고 따뜻한 소리, ㅓ와 ㅜ는 어둡고 차가운 소리랍니다.",
  "Sounds have a temperature too. ㅏ and ㅗ are bright and warm; ㅓ and ㅜ are dark and cool."),
 (18, "ㅏ+ㅣ · ㅗ+ㅣ · ㅜ+ㅣ",
  "그런데 ㅣ는 색이 없어요. 서 있는 사람을 본뜬 글자라서, "
  "따뜻한 소리와도 차가운 소리와도 사이좋게 어울립니다.",
  "But ㅣ has no colour. Shaped after a standing person, it gets along with warm and cool alike."),
 (19, "여우",
  "쉿… 덤불에 뭐가 있어요. 일곱 번째 단어, 여우. 숲에 사는 붉은 여우예요. "
  "여와 우, 이것도 모음뿐이랍니다.",
  "Shh... something's in the bush. Seventh word - 여우, the red fox of the forest. "
  "여 and 우 - vowels only again."),
 (20, "여 + 우 → 여우",
  "앗, 숨어 버렸네요. 여 — 우. 여우. 여는 ㅣ와 ㅓ가 빨리 이어진 소리예요. 지금은 한 소리로 익혀 두세요.",
  "Oh, it's gone. 여 - 우. 여우. 여 is ㅣ sliding quickly into ㅓ. For now, just learn it as one sound."),
 (21, "ㅗ+ㅏ = ㅘ / ㅜ+ㅓ = ㅝ",
  "같은 온도끼리 만나면 자석처럼 잘 붙어요. 따뜻한 소리는 따뜻한 소리끼리, 차가운 소리는 차가운 소리끼리.",
  "Same temperature, and they snap together like magnets - warm with warm, cool with cool."),
 (22, "ㅏ+ㅣ = ㅐ / ㅓ+ㅣ = ㅔ",
  "ㅣ만은 예외예요. 따뜻한 쪽에도, 차가운 쪽에도 스르륵 붙습니다. 떨어지는 잎을 잡듯이요.",
  "Only ㅣ is the exception - it slips in on the warm side and the cool side alike. "
  "Like catching a falling leaf."),
 (23, "오이 · 우유 · 여우",
  "이제 맞춰 볼까요? 그림을 보고 단어를 말해 보세요. 초록 채소는? 하얀 음료는? 붉은 짐승은?",
  "Now let's match. Look at the picture and say the word. The green vegetable? "
  "The white drink? The red animal?"),
 (24, "아이 이 오이 우유 오 아우 여우 · 야외",
  "오늘 배운 일곱 단어를 모아 볼까요? 아이, 이, 오이, 우유, 오, 아우, 여우. "
  "그리고 하나 더 — 우리가 하루 종일 있던 이곳, 야외. 이것도 모음뿐이에요!",
  "Let's gather today's seven words - 아이, 이, 오이, 우유, 오, 아우, 여우. "
  "And one more: the place we spent all day - 야외, \"outdoors\". Vowels only, again!"),
 (25, "아이 오이 우유",
  "오늘 배운 단어를 거울 앞에서 또박또박 말해 보세요. 입 모양이 보이면 소리도 또렷해집니다.",
  "Practice today's words clearly in front of a mirror. When you can see the shape, "
  "the sound gets clearer."),
 (26, "ㅇ + ㅏ = 아",
  "다음 시간엔 소리 없는 ㅇ에 모음을 붙여 글자 블록을 만들어 봐요. 또 만나요!",
  "Next time we'll join the silent ㅇ to a vowel and build syllable blocks. See you soon!"),
]

# ★나레이션 덧붙임 (사장님 지시 2026-08-12)
#   "심각하게 줄어드는 곳은 **동작을 다 할 수 있게** 나레이션과 자막을 적당한 길이로 추가하라."
#
#   씬 길이는 렌더러가 `max(KO,EN)+0.45s` 로 다시 잡는다(나레이션이 잘리지 않게).
#   그래서 대본이 짧으면 씬이 줄고 **동작이 끝나기 전에 다음 씬으로 넘어간다.**
#   1차 렌더 실측(2026-08-12)에서 계획의 절반 안팎으로 줄어든 씬들에 문장을 덧댔다.
#   ★채우는 말이 아니라 **교육 내용**으로 늘린다 — 뜻·쓰임·발음 요령을 한 겹 더 준다.
EXTRA = {
 1:  ("저 멀리서 제가 달려오고 있죠? 오늘은 광장을 한 바퀴 돌며 배워 볼 거예요.",
      "Can you see me running up from far away? Today we'll walk right around this plaza as we learn."),
 2:  ("자음 없이 모음만으로요. 믿기지 않으시죠? 제가 한 바퀴 돌아 보이면서 시작할게요. "
      "오늘 배울 단어는 모두 일곱 개입니다.",
      "Vowels only, no consonants at all. Hard to believe? Let me start with a flip. "
      "There are seven words waiting for us today."),
 4:  ("하나씩 찾을 때마다 같이 소리 내어 읽어 봐요. 준비되셨나요?",
      "Each time we find one, let's say it out loud together. Ready?"),
 5:  ("계단에 앉아서 천천히 볼까요? 아이의 아는 입을 크게 벌리는 소리, "
      "이는 입을 옆으로 당기는 소리예요.",
      "Shall we sit on the steps and take it slowly? The 아 in 아이 opens the mouth wide, "
      "and the 이 pulls it out to the sides."),
 6:  ("계단 한 칸이 소리 한 개예요. 아에서 한 칸, 이에서 또 한 칸. "
      "이렇게 음절을 하나씩 끊어 세면 어떤 단어든 읽을 수 있어요.",
      "One step is one sound. One step on 아, another on 이. "
      "Count the syllables one at a time like this and you can read any word."),
 8:  ("오이는 물이 많고 시원해서 여름에 많이 먹어요. "
      "쭈그려 앉아서 하나 주워 볼게요. 자, 잡았습니다!",
      "Cucumbers are juicy and cool, so we eat a lot of them in summer. "
      "Let me crouch down and pick one up. There - got it!"),
 9:  ("입술을 동그랗게 모았다가 옆으로 활짝. 오 — 이. 두 입 모양이 이어지는 게 보이시나요? "
      "한 번 더, 오 — 이. 오이.",
      "Round your lips, then pull them wide. 오 - 이. Can you see the two shapes joining? "
      "Once more: 오 - 이. 오이."),
 11: ("우유팩을 들고 다시 한 번. 우 — 유. 입술이 앞으로 나왔다가 그대로 머무르죠?",
      "Once more, holding the carton. 우 - 유. Your lips push forward and stay there, don't they?"),
 12: ("앞소리 하나만 바뀌었을 뿐인데 뜻이 아주 달라졌어요. 소리 하나의 힘이 이렇게 큽니다.",
      "Only the first sound changed, and yet the meaning is completely different. "
      "That's how much one sound can do."),
 13: ("놀랄 때 저절로 나오는 소리라서, 배우지 않아도 이미 알고 있는 단어예요.",
      "It's the sound that comes out by itself when you're startled - "
      "so you already knew this word before today."),
 14: ("손가락을 하나씩 펴 볼까요? 하나, 둘, 셋, 넷, 다섯. "
      "다섯 손가락을 다 펴면 그게 바로 오예요. 숫자도 되고 감탄도 되는 재미있는 소리죠.",
      "Shall we open our fingers one by one? One, two, three, four, five. "
      "All five fingers open - that's 오. It's a number and a cry of surprise at the same time."),
 16: ("ㅏ는 입을 크게, ㅜ는 입술을 동그랗게 모아서. 아 — 우. "
      "제 친구도 따라 하고 있네요. 여러분도 같이 해 보세요. 아 — 우. 아우.",
      "ㅏ opens wide, ㅜ rounds the lips. 아 - 우. "
      "My friend is copying me too. Try it with us: 아 - 우. 아우."),
 19: ("여우는 꾀가 많은 동물로 옛이야기에 자주 나와요. "
      "놀라지 않게 살금살금 다가가 볼게요. 쉿, 조용히…",
      "The fox is famous for being clever, and turns up often in old tales. "
      "Let me creep up so I don't startle it. Shh, quietly now..."),
 15: ("형이나 누나가 손아래 동생을 부를 때 쓰는 말이에요. "
      "요즘은 자주 쓰지 않지만 옛이야기에는 자주 나온답니다.",
      "It's what an older brother or sister calls a younger one. "
      "You don't hear it much these days, but it turns up often in old stories."),
 18: ("그래서 ㅣ는 어느 편도 들지 않아요. 늘 가운데에서 조용히 서 있습니다.",
      "So ㅣ never takes a side. It just stands quietly in the middle."),
 21: ("ㅗ와 ㅏ가 만나면 ㅘ, ㅜ와 ㅓ가 만나면 ㅝ가 돼요. 따뜻한 것끼리, 차가운 것끼리.",
      "ㅗ and ㅏ make ㅘ; ㅜ and ㅓ make ㅝ. Warm with warm, cool with cool."),
 22: ("ㅏ에 ㅣ를 더하면 ㅐ, ㅓ에 ㅣ를 더하면 ㅔ. 이렇게 새로운 소리가 태어납니다.",
      "Add ㅣ to ㅏ and you get ㅐ; add ㅣ to ㅓ and you get ㅔ. That's how a new sound is born."),
 23: ("잘 맞히셨나요? 그림과 소리를 함께 기억하면 훨씬 오래 남아요.",
      "Did you get them? When you remember the picture and the sound together, it stays with you much longer."),
 25: ("입 모양이 달라지면 소리도 달라져요. 오늘 배운 단어를 천천히 세 번씩 말해 보세요.",
      "When the shape of your mouth changes, the sound changes too. "
      "Say today's words slowly, three times each."),
 26: ("오늘 정말 잘하셨어요. 자음 하나 없이도 이렇게 많은 말을 할 수 있다니 놀랍지요? "
      "저는 이만 광장을 가로질러 가 볼게요. 다음 시간에 또 만나요!",
      "You did really well today. Isn't it surprising how much you can say without a single consonant? "
      "I'm off across the plaza now. See you next time!"),
}

# 씬별 캐릭터 배치 — (캐릭터, 포즈/컷, 깊이, cx)  ※깊이가 화면 키를 정한다
#   캐릭터 키는 char_heights 의 것을 쓴다: stickman / zolla_man / zolla_girl
#
# ★★사장님 확정 규격 (2026-08-13) — 이 판을 통째로 다시 짠 이유
#   ① "일단 **한 씬에 한 캐릭터는 하나만** 나온다" — 같은 캐릭터를 둘 세우지 않는다
#   ② "항상 **스틱맨이 주 캐릭터**" — 앞줄(F0/F1)에서 설명한다
#   ③ "보조로 졸라맨 졸라걸이 좀 작게 **600 이하**고 **백에** 나오고 **많이 움직여도 된다**"
#      → 졸라는 D1(320)·D2(220)·V(120) 뒷줄에만 세우고, 정지 포즈보다 **이동컷**을 준다
#   ④ "**뒷구르기 백플립은 없애자**" — back_flip·back_roll 은 한 줄도 쓰지 않는다
#      S2·S13 은 새로 만든 `forward_roll2`(38컷)와 `skid_stop` 으로 갈아 끼웠다
#   ⑤ 앞구르기는 새로 뽑은 **`forward_roll2`** 를 쓴다(옛 `forward_roll` 은 안 쓴다)
CHARS = {
 # ── 1막 광장 : 스틱맨이 저 멀리서 달려와 앞줄에 선다 ──────────────────
 1:  [("stickman", "run_front", "V→F0", 640)],
 2:  [("stickman", "sm_presenting", "F0", 430),
      ("zolla_man", "zman_run_side2", "D2", 980)],          # 뒤로 졸라맨이 달려 지나간다
 3:  [("stickman", "sm_pointing_left", "F0", 430),
      ("zolla_girl", "zgirl_run_side", "D1", 1000)],
 4:  [("stickman", "forward_roll2", "M→D1→M", 640)],        # ★새 앞구르기 38컷

 # ── 2막 계단 ────────────────────────────────────────────────────
 5:  [("stickman", "sit_stand", "M", 640),
      ("zolla_man", "zman_run_side2", "D2", 300)],
 6:  [("stickman", "hop_down", "M2→F1", 640)],
 7:  [("stickman", "stickman_w1d2_grab_rail_r", "M", 900)],

 # ── 3막 좌판 ────────────────────────────────────────────────────
 8:  [("stickman", "pick_up", "F1", 700)],
 9:  [("stickman", "stickman_w1d2_mouth_o", "F0", 430),
      ("zolla_girl", "zgirl_run_side_l", "D1", 1020)],
 10: [("stickman", "reach_catch", "F1", 760)],
 11: [("stickman", "stickman_w1d2_mouth_u", "F0", 430),
      ("zolla_man", "zman_run_side_l", "D2", 1000)],
 12: [("stickman", "stickman_w1d2_lean_rail_r", "M", 900)],

 # ── 4막 분수 : 백플립을 뺐다 → 급정지 + 앞구르기 ────────────────────
 13: [("stickman", "skid_stop", "D1→F1", 640)],
 14: [("stickman", "sm_counting_five", "F0", 430),
      ("zolla_girl", "zgirl_high_five2", "D1", 1020)],

 # ── 5막 벤치 : 한 씬에 졸라는 하나만 ────────────────────────────────
 15: [("stickman", "sit_stand", "M", 560),
      ("zolla_man", "zman_sit_stand", "D1", 900)],
 16: [("stickman", "stickman_w1d2_mouth_a", "F0", 430),
      ("zolla_man", "zman_head_tilt", "D1", 980)],
 17: [("stickman", "high_five", "M", 560),
      ("zolla_girl", "zgirl_high_five2", "D1", 880)],
 18: [("stickman", "sm_arms_out_wide", "F0", 430),
      ("zolla_man", "zman_attention", "D2", 1010)],

 # ── 6막 산책로 ──────────────────────────────────────────────────
 19: [("stickman", "tiptoe", "M", 760),
      ("zolla_girl", "zgirl_run_side", "D2", 260)],
 20: [("stickman", "butt_fall", "M", 760)],
 21: [("stickman", "sm_arms_out_wide", "F0", 430),
      ("zolla_man", "zman_run_side2", "D1", 1000)],
 22: [("stickman", "reach_catch", "M→M2→M", 700)],

 # ── 7막 해질녘 ──────────────────────────────────────────────────
 23: [("stickman", "stickman_w1d2_card_fan", "F0", 430),
      ("zolla_girl", "zgirl_card_hold", "D1", 1010)],
 24: [("stickman", "sm_greeting_wave", "F0", 430),
      ("zolla_man", "zman_hands_up", "D1", 1010)],
 25: [("stickman", "sm_holding_mirror", "F0", 430),
      ("zolla_girl", "zgirl_mirror", "D2", 1020)],
 26: [("stickman", "m6_run_exit_r", "F0→V", 500)],
}


# ★화면 글자 — 한 줄에 너무 길면 잘린다 (1차 렌더 실측 2026-08-12).
#   "모음 + 모음 = 단어" 가 "음 + 모음 = 단ㅇ" 로 양쪽이 잘려 나갔다.
#   사장님 규격: 상반부 중앙 · **최대 세 줄**. 한 줄에 8자를 넘으면 나눈다.
GLYPH_PER_LINE = 8
GLYPH_MAX_LINES = 3


def wrap_glyph(g):
    toks = g.split()
    if not toks:
        return g
    lines, cur = [], ""
    for t in toks:
        cand = (cur + " " + t).strip()
        if cur and len(cand.replace(" ", "")) > GLYPH_PER_LINE:
            lines.append(cur)
            cur = t
        else:
            cur = cand
    if cur:
        lines.append(cur)
    if len(lines) > GLYPH_MAX_LINES:                      # 세 줄을 넘으면 고르게 다시 나눈다
        per = -(-len(toks) // GLYPH_MAX_LINES)
        lines = [" ".join(toks[i:i + per]) for i in range(0, len(toks), per)][:GLYPH_MAX_LINES]
    return "\n".join(lines)


def base_h(con):
    return {k: h for k, h in con.execute("SELECT char_key, base_h FROM char_heights")}


def build(con, dry):
    heights = base_h(con)
    man = {s[0]: s for s in MAN.SCENES}
    rows, objs = [], []
    for seq, glyph, ko, en in NARR:
        if seq in EXTRA:                                  # ★동작이 다 나오도록 덧댄 문장
            ko = ko + " " + EXTRA[seq][0]
            en = en + " " + EXTRA[seq][1]
        glyph = wrap_glyph(glyph)                         # ★한 줄이 길면 줄바꿈(최대 세 줄)
        _, sec, bg, cuts, poses, cards, anchors = man[seq]
        bgp = os.path.join("W1_2/bg", bg + ".mp4")
        is_vid = os.path.exists(bgp)
        ev = MAN.BG_EVENTS.get(bg)

        chars = []
        for ck, pose, depth, cx in CHARS.get(seq, []):
            d0 = depth.split("→")[0]
            h_screen = DEPTH.get(d0, DEPTH["M"])[0]
            chars.append({
                "char": ck, "pose": pose, "depth": depth,
                "cx": cx, "foot_y": DEPTH.get(d0, DEPTH["M"])[1],
                # 화면 키 = 그 깊이의 키 × (그 캐릭터 기본키 / 스틱맨 기본키)
                "h": round(h_screen * heights.get(ck, 700) / float(heights.get("stickman", 700))),
            })

        ip = {
            "cap_ko": "", "cap_en": "",
            "bg": bg,
            "bg_video": ("W1_2/bg/%s.mp4" % bg) if is_vid else None,
            "bg_still": None if is_vid else ("W1_2/bg/%s.png" % bg),
            "bg_play": "once_hold",          # ★8초 클립을 한 번만 재생하고 마지막 프레임 유지
            "bg_event": {"what": ev[0], "t": ev[1]} if ev else None,
            "place_en": PLACE,
            "glyph": glyph,
            "text": dict(TEXT_BOX, text=glyph, lines=min(3, 1 + glyph.count("\n"))),
            "draw_font": "cafe24_dongdong", "draw_dur": 1.6,
            "draw_align": "center", "draw_text": glyph,
            "chars": chars,
            "cards": cards,
            "anchors": anchors,
        }
        rows.append((EP, seq, ko, en, json.dumps(ip, ensure_ascii=False), "", None, float(sec)))
        for i, c in enumerate(chars):
            objs.append((EP, seq, None, c["cx"], c["foot_y"], round(c["h"] / 740.0, 3),
                         5 + i, 0, "pose"))

    if dry:
        print("씬 %d · 오브젝트 %d (dry)" % (len(rows), len(objs)))
        for r in rows[:2]:
            print("   S%-2d %ds  %s" % (r[1], int(r[7]), r[2][:46]))
        return 0

    # ★★★ scene_objects 는 **건드리지 않는다** (2026-08-12 사고).
    #   예전 판은 여기서 지우고 asset_id 없이 다시 넣었다. 그 뒤 wire_w12.py 가 제대로
    #   채우는 구조였는데, 나레이션만 고치려고 build 를 다시 돌리자 배선이 **통째로 지워졌다**.
    #   `JOIN assets ON a.id=o.asset_id` 가 0행이 되어 **캐릭터도 파라메트릭 글자도
    #   조용히 사라진 채** 8분짜리가 렌더됐다([[precheck-asset-fidelity-before-render]]).
    #   → 이제 scene_objects 의 주인은 **wire_w12.py 하나뿐**이다.
    con.execute("DELETE FROM scenes WHERE episode=?", (EP,))
    con.executemany(
        "INSERT INTO scenes(episode,seq,script_kr,script_en,image_prompt,veo_prompt,sfx,"
        "duration_sec) VALUES(?,?,?,?,?,?,?,?)", rows)
    con.commit()
    n_obj = con.execute("SELECT COUNT(*) FROM scene_objects WHERE episode=?",
                        (EP,)).fetchone()[0]
    if n_obj == 0:
        print("  ★★scene_objects 가 비어 있다 — `python W1_2/wire_w12.py` 를 반드시 돌려라")
    return len(rows), n_obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    con = sqlite3.connect(DB)
    r = build(con, a.dry)
    if a.dry:
        return 0
    n, m = r
    tot = con.execute("SELECT SUM(duration_sec) FROM scenes WHERE episode=?", (EP,)).fetchone()[0]
    print("빌드 완료 — %s" % EP)
    print("  씬 %d개 · 오브젝트 %d개 · 총 %d초 (%d분 %d초)"
          % (n, m, tot, tot // 60, tot % 60))
    print("  기록 %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
