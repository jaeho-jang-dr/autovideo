#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_w9_content.py — KO-W09 "위치·장소 표현" 교육 시나리오 2배 확장(20씬).
 - 오류 수정: '쪽라는'→'쪽이라는', '곳라는'→'곳이라는'
 - 위치어 확장: 앞 뒤 옆 위 밑 + 안 밖 사이 왼쪽 오른쪽
 - 장소어: 마트 학교 은행 카페 공원 / 예문·대화·연습 추가
재실행: python hangeul_birth_vowels/build_w9_content.py
"""
import os, sys, sqlite3
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "channel", "content.db")
EP = "KO-W09"

# (script_kr, script_en, duration_sec)  — 나레이션은 짧은 문장 위주(자막 청킹 좋게)
SCENES = [
 ("안녕하세요! 한국에서 살면 '어디에 있어요?'라는 질문을 정말 자주 들어요. 오늘은 위치를 말하는 표현을 배워요. 그러면 우리 동네를 자신 있게 안내할 수 있어요.",
  "Hello! Living in Korea, you'll often hear 'Where is it?'. Today we'll learn how to describe locations, so you can confidently guide people around your neighborhood.", 20),
 ("위치는 보통 '장소 + 위치말 + 에' 순서로 말해요. 예를 들어 '학교 앞에'처럼요. 오늘은 위치말을 하나씩 천천히 익혀 봐요.",
  "Location is usually said as 'place + position word + 에'. For example, '학교 앞에' (in front of the school). Let's learn the position words one by one.", 16),
 ("'앞'은 어떤 것의 정면 쪽이라는 뜻이에요. 예를 들어, '학교 앞에서 만나요.' 라고 말해요. 장소 뒤에 '앞에'를 붙이면 돼요. 자, 천천히 따라 하세요. '앞'.",
  "'앞' means the front. For example: 'Let's meet in front of the school.' Just add '앞에' after a place. Repeat slowly: '앞'.", 18),
 ("'뒤'는 정면의 반대, 등지는 쪽이라는 뜻이에요. 예를 들어, '집 뒤에 공원이 있어요.' 라고 말해요. 자, 천천히 따라 하세요. '뒤'.",
  "'뒤' means the back. For example: 'There's a park behind the house.' Repeat slowly: '뒤'.", 16),
 ("'옆'은 바로 곁, 나란한 쪽이라는 뜻이에요. 예를 들어, '은행 옆에 카페가 있어요.' 라고 말해요. 두 장소가 나란할 때 써요. 자, 따라 하세요. '옆'.",
  "'옆' means beside. For example: 'There's a cafe next to the bank.' Use it when two places are side by side. Repeat: '옆'.", 17),
 ("'위'는 더 높은 쪽이라는 뜻이에요. 예를 들어, '책상 위에 책이 있어요.' 라고 말해요. 표면 위에 무엇이 있는지 말할 때 써요. 자, 따라 하세요. '위'.",
  "'위' means above or on. For example: 'There's a book on the desk.' Repeat: '위'.", 17),
 ("'밑'은 더 낮은 쪽, 아래라는 뜻이에요. 예를 들어, '의자 밑에 가방이 있어요.' 라고 말해요. '밑'과 '아래'는 비슷해요. 자, 따라 하세요. '밑'.",
  "'밑' means under or below. For example: 'There's a bag under the chair.' '밑' and '아래' are similar. Repeat: '밑'.", 17),
 ("'안'은 어떤 공간의 속, 내부라는 뜻이에요. 예를 들어, '가방 안에 책이 있어요.' 라고 말해요. 무엇의 속을 말할 때 써요. 자, 따라 하세요. '안'.",
  "'안' means inside. For example: 'There's a book inside the bag.' Use it for the inside of something. Repeat: '안'.", 17),
 ("'밖'은 '안'의 반대, 바깥이라는 뜻이에요. 예를 들어, '집 밖에 자동차가 있어요.' 라고 말해요. '안'과 '밖'을 짝으로 기억하세요. 자, 따라 하세요. '밖'.",
  "'밖' means outside, the opposite of '안'. For example: 'There's a car outside the house.' Remember '안' and '밖' as a pair. Repeat: '밖'.", 17),
 ("'사이'는 두 것의 가운데라는 뜻이에요. 예를 들어, '은행과 카페 사이에 있어요.' 라고 말해요. 두 장소 가운데를 가리켜요. 자, 따라 하세요. '사이'.",
  "'사이' means between. For example: 'It's between the bank and the cafe.' It points to the middle of two places. Repeat: '사이'.", 17),
 ("'왼쪽'은 왼편이라는 뜻이에요. 예를 들어, '왼쪽에 학교가 있어요.' 라고 말해요. 방향을 가리킬 때 아주 자주 써요. 자, 따라 하세요. '왼쪽'.",
  "'왼쪽' means the left side. For example: 'The school is on the left.' Very common for giving directions. Repeat: '왼쪽'.", 17),
 ("'오른쪽'은 오른편이라는 뜻이에요. 예를 들어, '오른쪽에 마트가 있어요.' 라고 말해요. '왼쪽'과 '오른쪽'을 함께 기억하세요. 자, 따라 하세요. '오른쪽'.",
  "'오른쪽' means the right side. For example: 'The mart is on the right.' Remember '왼쪽' and '오른쪽' together. Repeat: '오른쪽'.", 17),
 ("이제 장소 이름도 배워요. '마트'는 물건을 파는 큰 가게라는 뜻이에요. '마트에서 우유를 사요.' 라고 말해요. 자, 따라 하세요. '마트'.",
  "Now let's learn place names. '마트' means a mart, a big store. 'I buy milk at the mart.' Repeat: '마트'.", 15),
 ("'학교'는 공부하는 곳이라는 뜻이에요. '학교에 걸어서 가요.' 라고 말해요. 장소 뒤 '에'는 방향을 나타내요. 자, 따라 하세요. '학교'.",
  "'학교' means a school. 'I walk to school.' The '에' after a place shows direction. Repeat: '학교'.", 15),
 ("'은행'과 '카페'와 '공원'도 자주 나와요. '은행 옆에 카페가 있어요.' '공원 안에서 산책해요.' 이렇게 위치말과 함께 쓰면 돼요.",
  "'은행' (bank), '카페' (cafe), and '공원' (park) also come up often. 'A cafe is next to the bank.' 'I take a walk in the park.' Use them with the position words.", 16),
 ("작은 규칙 하나 더요. 위치에는 '에', 행동에는 '에서'를 써요. '학교에 가요.'는 방향, '학교에서 공부해요.'는 그곳에서의 행동이에요.",
  "One more small rule. Use '에' for location, '에서' for actions. '학교에 가요.' shows direction; '학교에서 공부해요.' shows an action there.", 16),
 ("이제 실제 상황이에요. 누군가 '마트가 어디에 있어요?' 하고 물으면, '학교 앞에 있어요.' 하고 답해요. 함께 연습해 봐요.",
  "Now a real situation. If someone asks 'Where is the mart?', answer 'It's in front of the school.' Let's practice together.", 16),
 ("한 번 더요. '은행이 어디에 있어요?' 그러면 '카페 옆에 있어요.' 또는 '공원과 카페 사이에 있어요.' 라고 답할 수 있어요.",
  "One more. 'Where is the bank?' You can answer 'It's next to the cafe.' or 'It's between the park and the cafe.'.", 16),
 ("길 안내도 해 봐요. '왼쪽으로 가세요. 그리고 학교 앞에서 오른쪽이에요.' 위치말을 이으면 길을 안내할 수 있어요. 아주 잘하고 있어요!",
  "Let's give directions too. 'Go to the left. Then turn right in front of the school.' Chain the position words to guide someone. You're doing great!", 16),
 ("오늘 배운 위치말이에요. 앞, 뒤, 옆, 위, 밑, 안, 밖, 사이, 왼쪽, 오른쪽. 소리 내어 한 번 더 읽어 볼까요? 훌륭해요! 오늘 표현을 꼭 한 번 써 보세요. 다음 시간에 또 만나요!",
  "Here are today's position words: front, back, beside, above, under, inside, outside, between, left, right. Let's read them aloud once more. Wonderful! Try using them today. See you next time!", 20),
]

def main():
    con = sqlite3.connect(DB); cur = con.cursor()
    cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
    cur.execute("DELETE FROM scenes WHERE episode=?", (EP,))
    cols = [d[1] for d in cur.execute("PRAGMA table_info(scenes)").fetchall()]
    for i, (kr, en, dur) in enumerate(SCENES, 1):
        cur.execute(
            "INSERT INTO scenes (episode, seq, script_kr, script_en, image_prompt, veo_prompt, sfx, duration_sec) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (EP, i, kr, en, "", "", "", dur))
    con.commit()
    print(f"KO-W09 교육 시나리오 재작성: {len(SCENES)}씬 (기존 12 → {len(SCENES)}), scene_objects 초기화")
    con.close()

if __name__ == "__main__":
    main()
