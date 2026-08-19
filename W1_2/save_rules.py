# -*- coding: utf-8 -*-
"""사장님이 정하신 **규격과 씬 계획**을 DB에 저장한다.

★사장님 지시(2026-08-13)
  "지금 내가 바꾼 것들은 **바꾼 상태로 다 기억·기록**되어 있어야 한다.
   나중에 그것을 렌더에서 써야 한다." / "**데이터베이스에도 저장**한다."

## 저장하는 것 둘

### ① `stage_rules` — 무대·캐릭터 규격 (렌더가 읽어 쓴다)
회차·항목마다 값 하나. 렌더러가 상수를 코드에 박지 않고 여기서 읽는다.

### ② `scene_plans` — 씬마다 짠 동작 계획 (비트 목록)
`steps_scene` · `road_scene` · `fox_scene` 이 계산해 낸 비트를 그대로 담는다.
나중에 전체 렌더를 돌릴 때 이 표를 읽어 그대로 그리면 된다.

    python W1_2/save_rules.py            # 저장
    python W1_2/save_rules.py --show     # 저장된 것 보기
"""
import json
import os
import sqlite3
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

DB = "channel/content.db"
EP = "KO-W1-2"

DDL = """
CREATE TABLE IF NOT EXISTS stage_rules (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  episode    TEXT NOT NULL,
  topic      TEXT NOT NULL,      -- 무엇에 대한 규격인가
  key        TEXT NOT NULL,      -- 항목
  value      TEXT NOT NULL,      -- 값
  said       TEXT,               -- 사장님 말씀 그대로
  note       TEXT,               -- 왜 이렇게 정했나
  updated_at TEXT,
  UNIQUE(episode, topic, key)
);
CREATE TABLE IF NOT EXISTS scene_plans (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  episode    TEXT NOT NULL,
  scene_key  TEXT NOT NULL,      -- steps_seat / path_leaves / path_fox …
  bg         TEXT NOT NULL,
  sec        REAL,
  beats_json TEXT NOT NULL,      -- 비트 목록 그대로
  note       TEXT,
  updated_at TEXT,
  UNIQUE(episode, scene_key)
);
"""

# ★사장님이 정하신 규격 — 말씀을 그대로 남긴다
RULES = [
 ("캐릭터 키", "척도", "700",
  "기준 척도가 700인데 여태 나레이터로 나오던 캐릭터의 사이즈대로 하면 된다",
  "스틱맨 실물 키. DB char_heights 의 base_h 와 같다"),
 ("캐릭터 키", "앞줄 화면키", "400",
  "앞줄 400으로 가자",
  "W19~W24 나레이터는 몸높이 770 × 0.561 = 화면 432. 스틱맨 규격이 749→700 이라 393. 그 사이 400"),
 ("캐릭터 키", "보조역 상한", "600",
  "보조 캐릭터는 그 뒤 어느 곳 600~1 까지의 사이즈로 움직이면 된다",
  "졸라맨·졸라걸. 작을수록 많이 움직여도 표가 덜 난다"),
 ("캐릭터 키", "하한", "1",
  "결론으로 하한은 1이다",
  "0은 무한대라 계산 못 한다. 얼마에서 사라지느냐는 배경의 땅이 정한다"),
 ("캐릭터 키", "축척 기준", "머리 지름",
  "자세에 따른 키 높이와 전체 비율이 어긋나지 않게",
  "잉크 높이가 아니라 머리 지름이 기준. 자세가 바뀌어도 머리는 안 변한다. "
  "실측 — 엉덩방아 203 · 놀람 204 · 쭈그림 171"),
 ("캐릭터 키", "놀람·쭈그림 보정", "1.20",
  "정면을 보고 놀란 표정, 쪼그려 앉기 더 키워줘 20%",
  "머리로 맞춘 뒤에도 눈으로 작아 보여 20% 더"),

 ("투명컷", "규칙", "얼굴·머리카락만 남기고 흰색 전부 제거",
  "얼굴을 빼고 팔 사이, 팔과 몸 사이, 다리와 다리 사이, 다리와 몸 사이 모두 다 투명하게",
  "W1_2/strip_white.py"),
 ("투명컷", "적용 범위", "졸라 삼총사 전용",
  "머리만 남기고 모든 흰색이란 것은 이 졸라 삼총사에만 해당되는 것이다. "
  "다른 캐릭터는 흰색 옷, 몸도 있다",
  "지은·인준·마담제이 등에는 쓰면 안 된다"),
 ("투명컷", "옷·신발·장갑", "흰색 말고 회색",
  "이제 옷 신발 손장갑 등을 흰색을 하지 말고 컷아웃 하기 힘드니 회색까지만 하자",
  "흰 신발은 흰 배경과 안 갈려 발 속이 뚫린다. motion6_defs.GREY_PARTS"),
 ("투명컷", "검사", "초록 바탕으로만",
  "투명컷은 하고 나서 내 검사를 받는다",
  "흰 바탕에 얹으면 안 뚫린 흰색과 뚫린 곳이 똑같이 보인다"),

 ("Flow", "클릭", "playwright locator.click()",
  "playwright locator.click() 사용하라",
  "좌표 클릭은 가로채여도 성공으로 찍히고 180초 뒤 조용히 죽는다"),
 ("Flow", "모델", "Omni Flash (동영상은 첫 클립만 바꾼다)",
  "그냥 항상 옴니 플래시로만 하자. 동영상 만들 때는 처음에만 바꾼다",
  "매번 바꾸면 패널이 닫혀 뒤 항목이 8초씩 타임아웃 — 클립당 40초 손해"),
 ("Flow", "구르기 3원칙", "해부학 · 팔다리 2개 · 얼굴은 도는 방향 고정",
  "해부학적으로 만들고 팔 다리 절대로 2개 2개 이상 나오게 하지 말고 "
  "얼굴 방향은 항상 회전하는 방향으로 고정한다",
  "motion6_defs.ROLL_HARD"),
 ("Flow", "구르기 길이", "8초 동안 천천히 한 번",
  "천천히 구르라 하고 일어서서 구르기 시작 다시 일어서기 총 8초 동안 천천히 한 번만",
  "빨리 구르면 프레임이 뭉개지고 팔다리가 터진다"),
 ("Flow", "손", "새로 만들지 않는다",
  "앞구르기 뒷구르기 스틱맨에 손을 만들지 마라. 발은 이미 있는 것이고 손은 새로 추가로 만들지 마",
  "손을 붙이면 검은 덩어리가 달려 다섯째 팔다리처럼 보인다"),

 ("씬 구성", "씬당 캐릭터", "스틱맨 1 + 졸라 1",
  "일단 한 씬에 한 캐릭터는 하나만 나오는데 항상 스틱맨이 주 캐릭터이고 "
  "보조로 졸라맨 졸라걸이 좀 작게 600 이하고 백에 나오고 많이 움직여도 된다",
  "build_w12.CHARS"),
 ("씬 구성", "백플립·뒷구르기", "쓰지 않는다",
  "어려운 것 같으니 뒷구르기 백플립은 없애자",
  "Flow 가 회전 구간에서 팔다리를 터뜨린다"),
 ("씬 구성", "앞구르기", "forward_roll2 38컷",
  "앞구르기는 내가 38씬 잘라서 만든 것 그것 써. 원본은 캐릭터 다 왜곡되어 못 쓴다",
  "192프레임에서 사장님이 직접 고른 33~169번"),
 ("씬 구성", "계단 오르내리기", "반스트라이드당 한 칸 · 그 안에서 크기 고정",
  "사이즈는 계단 한 칸마다 줄이면 되니 반스트라이드 컷 같은 사이즈, "
  "그다음 반스트라이드 컷 같은 사이즈로 한 칸 윗계단",
  "크기를 죽 보간하면 몸이 스멀스멀 줄어 어색하다"),
 ("씬 구성", "달리기 전환", "잠깐 서 있다가 휙 돌아서",
  "달려가기 달려오기의 전환은 잠깐 서 있다가 휙 돌아서 오면 된다",
  "달리기 첫 정지 프레임 한 장으로 대체"),
 ("씬 구성", "길에서 달리기", "뒷모습으로 멀어지고 앞모습으로 다가온다",
  "옆으로 달리지 말고 앞으로 보고 있다가 휙 돌아서 저 멀리 달려갔다가 "
  "잠깐 서 있다가 휙 돌아서 다시 앞으로 달려 나와서 나레이션 포지션까지",
  "옆달리기는 화면을 가로지를 때만"),

 ("무대", "걸을 수 있는 땅", "감독이 실측해 칠한다",
  "내가 붓으로 계단 평상을 칠하거나 지우는 것은 못 해. 그것을 네가 해라",
  "W1_2/paint_walk.py. 자동 측정은 색이 끊기는 계단을 못 잡는다"),
 ("무대", "원근 공식", "키 = K × (발y − 지평선)",
  "캐릭터가 어느 곳에 딱 서면 벌써 계산된 비율의 키로 서야 하는 것이다",
  "AGS·SCUMM·Sierra 가 다 쓰는 표준식. K = 400/(720−지평선)"),
 ("무대", "높아진 땅", "구역(zone)마다 키를 따로 준다",
  "",
  "계단은 오를수록 멀어지지만 올라간 만큼 화면에서 도로 내려온다. "
  "바닥 평면 공식이 안 들어 구역별 실측 키를 쓴다"),
 ("무대", "나무로 재는 원근", "밑동 y 가 곧 깊이",
  "나무 높이가 다 같다고 보았을 때 나무 높이의 차이가 원근의 차이이니 그것으로 재면 되겠다",
  "은행나무길 지평선 445"),
]


def save_plans(con, now):
    """씬 계획을 계산해 그대로 담는다."""
    n = 0
    for mod_name, key in (("steps_scene", "steps_seat"),
                          ("road_scene", "path_leaves"),
                          ("fox_scene", "path_fox")):
        try:
            mod = __import__(mod_name)
            out = mod.plan()
            if len(out) == 3:
                st, B, sec = out
                bg = mod.BG
            else:
                B, sec = out
                bg = "steps_seat"
            con.execute(
                "INSERT INTO scene_plans(episode,scene_key,bg,sec,beats_json,note,"
                "updated_at) VALUES(?,?,?,?,?,?,?) "
                "ON CONFLICT(episode,scene_key) DO UPDATE SET bg=excluded.bg,"
                "sec=excluded.sec, beats_json=excluded.beats_json,"
                "updated_at=excluded.updated_at",
                (EP, mod_name, bg, round(sec, 2),
                 json.dumps(B, ensure_ascii=False),
                 (mod.__doc__ or "").strip().split("\n")[0], now))
            n += 1
            print("  %-14s %-14s %5.1f초 · 비트 %d" % (mod_name, bg, sec, len(B)))
        except Exception as e:
            print("  ★%s 저장 실패: %s" % (mod_name, str(e)[:70]))
    return n


def main():
    con = sqlite3.connect(DB)
    con.executescript(DDL)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "--show" in sys.argv:
        print("%-12s %-18s %s" % ("항목", "키", "값"))
        for r in con.execute(
                "SELECT topic,key,value,said FROM stage_rules WHERE episode=? "
                "ORDER BY topic,key", (EP,)):
            print("  %-10s %-16s %s" % (r[0], r[1], r[2]))
            if r[3]:
                print("      \"%s\"" % r[3][:90])
        print()
        for r in con.execute(
                "SELECT scene_key,bg,sec,length(beats_json) FROM scene_plans "
                "WHERE episode=?", (EP,)):
            print("  씬 %-14s %-14s %5.1f초 · %d바이트" % r)
        return 0

    print("규격 저장")
    for topic, key, value, said, note in RULES:
        con.execute(
            "INSERT INTO stage_rules(episode,topic,key,value,said,note,updated_at)"
            " VALUES(?,?,?,?,?,?,?) ON CONFLICT(episode,topic,key) DO UPDATE SET"
            " value=excluded.value, said=excluded.said, note=excluded.note,"
            " updated_at=excluded.updated_at",
            (EP, topic, key, value, said, note, now))
    print("  %d개" % len(RULES))

    print("\n씬 계획 저장")
    n = save_plans(con, now)
    con.commit()
    con.close()
    print("\n✅ stage_rules %d · scene_plans %d → %s" % (len(RULES), n, DB))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
