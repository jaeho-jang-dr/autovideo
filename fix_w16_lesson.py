# -*- coding: utf-8 -*-
"""W16 영어판 교정 — ★한글 교육 원칙: 모든 운동 이름·빈도는 '한글'(뜻)로.
 문제: 영어판 나레이션이 사진·프리스비·배드민턴·낚시·캠핑·짚와이어·피아노·요리·영화·게임 등을
       영어로만 말해 학습이 안 됨 → W15 표준('한글' (뜻), 발음기호는 add_pron이 자막에 자동)으로 교정.
 방식: W16_scenario.md(원천)의 각 씬 glyph·EN 나레이션을 아래 CORR로 교체 → build_w16 재실행 → 재렌더.
 사장님 피드백 반영: S17 빈도사다리 6개 3줄 글자, 프리스비·배드민턴 한글+발음, 일주일에 한 번 뜻까지.
"""
import re, os
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
SCN = "W16_scenario.md"

# seq -> {"glyph": 새 화면글자(선택), "en": 새 영어 나레이션(선택)}
# ★EN엔 한글 단어를 넣는다(한글은 ko음성으로 발음, [발음]은 자막에 자동). 뜻은 (괄호).
CORR = {
 9:  {"en": "Let's tour '남이섬' (Nami Island) and see my hobbies one by one. Let's go — 갈까요? (Shall we go?)"},
 17: {"glyph": "항상 보통 / 자주 가끔 / 거의 안 전혀 안",
      "en": "Let's review, most to least: '항상' (always) - '보통' (usually) - '자주' (often) - '가끔' (sometimes) - '거의 안' (rarely) - '전혀 안' (never)."},
 21: {"en": "Some things I do '매일' (every day), some '전혀 안 해요' (never do). Everyone's different — how about you?"},
 23: {"en": "You've learned the '빈도' (frequency) words — great job! Now let's practice with my hobbies. Follow me!"},
 24: {"en": "When you think of '남이섬', you think '자전거' (cycling)! Riding in the cool breeze — my favorite hobby."},
 26: {"en": "Look at this metasequoia road! I love '산책' (walking) here. '저는 매일 산책해요' (I walk every day)."},
 27: {"en": "In the morning I do '조깅' (jogging) by the river. '저는 매일 아침에 조깅해요' (I jog every morning). So refreshing!"},
 28: {"en": "On these pretty lanes I love '사진' (photos). '저는 사진 찍는 것을 좋아해요' (I like taking photos), so I do it '자주' (often)."},
 30: {"en": "On nice days I enjoy a '피크닉' (picnic) on the lawn — I even pack '김밥' (gimbap). I do it '자주' (often) on weekends."},
 31: {"en": "On the wide lawn I fly a '연' (kite). It's a '가끔' (sometimes) hobby — perfect when it's windy."},
 32: {"en": "I also play '프리스비' (frisbee) with a friend — throw and catch, so fun. Also '가끔' (sometimes)."},
 33: {"en": "I like '배드민턴' (badminton) too — hitting the shuttlecock back and forth. About '일주일에 한 번' (once a week)."},
 34: {"en": "By the river I do '낚시' (fishing) — the charm is waiting quietly. '가끔' (sometimes), when I want to relax."},
 35: {"en": "I also do '강아지 산책' (dog-walking). Dogs need daily walks, so '하루에 두 번' (twice a day)."},
 36: {"en": "Nami has ostriches and rabbits. I love '동물 구경' (animal-watching), so I do it '자주' (often)."},
 37: {"en": "This one's special — '짚와이어' (zip-wire)! Like flying. It's scary, so '일 년에 한 번' (once a year)."},
 38: {"en": "For morning exercise I do '줄넘기' (jump rope) — hop hop hop! '저는 매일 줄넘기해요' (I jump rope every day)."},
 39: {"en": "Sometimes I go '캠핑' (camping) — pitch a tent, spend the night. About '한 달에 한 번' (once a month)."},
 41: {"en": "It's an art island, so I do '그림 그리기' (drawing) — sketching scenery. About '한 달에 두 번' (twice a month)."},
 42: {"en": "My new hobby lately is '스케이트보드' (skateboarding)! Still clumsy, but '자주' (often) these days."},
 43: {"en": "Wow, so many hobbies on '남이섬'! We've seen the active ones — now let's see what I do at '집' (home)."},
 44: {"en": "At home I play the '피아노' (piano) — my favorite songs lift my mood. '매일' (every day) I practice a little."},
 45: {"en": "Sometimes I do '요리' (cooking) — apron on, making something tasty. A wonderful hobby too."},
 47: {"en": "Every weekend I do '영화 보기' (watching movies) at home — sofa and popcorn. '주말마다' (every weekend)."},
 48: {"en": "I '가끔' (sometimes) do '노래' (singing) — I love karaoke! Grab the mic and I light up."},
 49: {"en": "'게임' (games)… um… '매일' (every day) a little? Okay, honestly, a bit more. Haha, it's a secret."},
 50: {"en": "Every vacation I go on a '여행' (trip) — new places thrill me. This trip's destination? '남이섬'!"},
 51: {"en": "'남이섬' changes by season. In '봄' (spring) I walk the '벚꽃' (cherry-blossom) lane — the pink is gorgeous."},
 52: {"en": "In '가을' (autumn) I take '사진' at the '단풍' (autumn-leaves) tunnel — yellow and red, the best backdrop."},
 53: {"en": "In '겨울' (winter) I walk the snowy lane — the whole world turns white, so romantic."},
 54: {"en": "In '여름' (summer) I enjoy '물놀이' (water play) — so cool. '일주일에 두 번' (twice a week) every summer."},
 55: {"en": "At '밤' (night) I '캠핑' and watch '별' (stars) — full of stars you can't see in the city. A special '가끔' hobby."},
 56: {"en": "See? So many hobbies — outdoors, at '집' (home), every season. What hobbies do YOU have?"},
 57: {"en": "Finally, let's count '얼마나 자주' (how often) exactly with numbers — super useful."},
 66: {"en": "Well done! Now you can confidently say '얼마나 자주' (how often). Amazing!"},
 69: {"en": "A confession, everyone: the '야구' (baseball) and '게임' (games) I bragged about? Haha… I actually '거의 안 해요' (rarely do them). Sorry!"},
 70: {"en": "So what do I REALLY do '매일' (every day), without fail? Take a guess."},
 71: {"en": "It's studying '한국어' (Korean) every day! Just like you, watching right now. That's my real daily hobby."},
 72: {"en": "What's YOUR '취미' (hobby)? And '얼마나 자주' (how often)? Please tell me in the comments!"},
 73: {"en": "Today we learned hobby names and '빈도' (frequency): '매일' (every day), '자주' (often), '가끔' (sometimes), '일주일에 세 번' (three times a week), '한 달에 한 번' (once a month)!"},
 74: {"en": "Enjoy your hobbies! And don't forget to study '한국어' '매일'. See you next time — 안녕히 계세요! (Goodbye!)"},
}

lines = open(SCN, encoding="utf-8").read().splitlines()
out = []; changed = 0
for ln in lines:
    m = re.match(r"^- \*\*S(\d+)\*\*\s*(.*)$", ln)
    if not m or int(m.group(1)) not in CORR:
        out.append(ln); continue
    seq = int(m.group(1)); c = CORR[seq]
    parts = ln.split(" | ")
    if len(parts) < 5:
        out.append(ln); continue
    # glyph = parts[1] (백틱), 나레이션 = parts[2] ("KO..." → (EN...))
    if "glyph" in c:
        parts[1] = f"`{c['glyph']}`"
    if "en" in c:
        # "KO..." → (EN...) 에서 KO 유지, (EN) 교체
        mm = re.match(r'^(.*?→\s*)\(.*\)\s*$', parts[2])
        if mm:
            parts[2] = mm.group(1) + f"({c['en']})"
        else:
            # → 없으면 뒤에 붙임
            parts[2] = parts[2].rstrip() + f" → ({c['en']})"
    out.append(" | ".join(parts)); changed += 1

open(SCN, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"시나리오 교정 완료: {changed}/{len(CORR)}씬 반영")
