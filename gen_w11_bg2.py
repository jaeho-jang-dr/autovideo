# -*- coding: utf-8 -*-
"""W11 추가 배경: 의자 없는 식당 실내 2(sit_on_chair 놓을 자리) + 변화용 2."""
import subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed
ROOT="D:/Entertainments/DevEnvironment/autovideo"; BD=f"{ROOT}/assets/graphics/bg"
BG=("감천문화마을(부산) 식당 배경 그림을 그려서 {path} 에 저장해줘. 파스텔 스토리북 스타일, 따뜻한 조명. 16:9 가로. "
    "사람(캐릭터)은 절대 그리지 말 것. ⚠️절대 규칙: 화면 어디에도 글자·숫자·간판문구·상표 넣지 마라. 장면: {scene}")
ITEMS=[
 ("table_menu_nochair","식당 실내. 왼쪽~가운데는 손님이 의자를 놓고 앉을 빈 바닥 공간으로 비워두고(★의자와 사람은 절대 그리지 말 것), 그 오른쪽에 나무 식탁과 그 위 메뉴판 한 권·빈 반찬 접시 몇 개·물컵. 벽에 감천 벽화, 창밖 알록달록 큐브집 계단."),
 ("table_food_nochair","식당 실내. 왼쪽~가운데는 손님이 앉을 빈 바닥 공간으로 비우고(★의자·사람 절대 없음), 오른쪽 나무 식탁에 음식 가득 — 국그릇·밥공기·여러 반찬접시·작은 불판·물컵. 벽에 감천 벽화, 창밖 큐브집 계단."),
 ("interior_wide","식당 안을 조금 넓게 본 각도. 나무 기둥과 창, 벽에 감천 벽화, 창밖 큐브집. 오른쪽에 음식이 조금 있는 식탁 일부, 왼쪽~가운데는 캐릭터가 들어와 둘러볼 빈 공간(★의자·사람 없음). 아늑한 실내."),
 ("table_closeup","식당 나무 식탁 위를 가까이 본 클로즈업. 김이 나는 찌개·밥·색색 반찬접시·젓가락·물컵이 먹음직스럽게 놓임. 뒤로 창밖 감천 큐브집이 흐릿하게. 사람·의자 없음."),
]
def run(j):
    name,scene=j; path=f"{BD}/bg_w11_{name}.png"
    try:
        subprocess.run(["agy","-p",BG.format(path=path,scene=scene),"--dangerously-skip-permissions"],
                       capture_output=True,text=True,timeout=420,encoding="utf-8",errors="ignore")
        return f"{'OK' if os.path.exists(path) else 'MISS'} {name}"
    except Exception as e: return f"ERR {name}: {str(e)[:30]}"
print(f"{len(ITEMS)}개 배경 생성",flush=True)
with ThreadPoolExecutor(max_workers=4) as ex:
    for f in as_completed({ex.submit(run,j):j for j in ITEMS}): print(f.result(),flush=True)
print("DONE",flush=True)
