# -*- coding: utf-8 -*-
"""W11 v2 배경 재생성: 의자 없이 테이블까지만, 오른쪽 50% 장면 / 왼쪽 넉넉한 캐릭터 공간, 사람 OK, 다양하게."""
import subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed
ROOT="D:/Entertainments/DevEnvironment/autovideo"; BD=f"{ROOT}/assets/graphics/bg"
BG=("감천문화마을(부산) 배경 그림을 {path} 에 저장해줘. 파스텔 스토리북, 따뜻한 조명, 부드러운 색. 16:9 가로. "
    "★구도 규칙: 화면 **오른쪽 절반**에 장면(식당/테이블/골목 등)을 두고, **왼쪽 절반은 캐릭터가 걸어다닐 넉넉한 빈 공간**(단순한 골목길/바닥/은은한 벽)으로 비운다. "
    "★의자는 절대 그리지 말 것. ⚠️화면에 글자·숫자·간판문구·상표 절대 없음. 장면: {scene}")
ITEMS=[
 ("alley1","오른쪽에 감천마을 골목과 소박한 식당 외관(간판은 그림 아이콘만), 알록달록 큐브집·계단·벽화. 왼쪽은 넓은 돌바닥 골목길."),
 ("alley2","오른쪽에 다른 골목의 식당 앞(화분·등불·차양), 큐브집 언덕과 바다 전망. 왼쪽은 넉넉한 골목길."),
 ("entrance","오른쪽에 식당의 열린 나무문(안이 살짝 보임)과 화분. 왼쪽은 넓은 돌바닥 입구 공간."),
 ("table","식당 실내. 오른쪽에 나무 식탁과 그 위 메뉴판·빈 반찬접시·물컵(★의자 없음). 벽에 감천 벽화, 창밖 큐브집. 왼쪽은 넉넉한 실내 바닥 공간."),
 ("food","식당 실내. 오른쪽 나무 식탁에 음식 가득(국·밥·반찬·작은 불판·물컵, ★의자 없음). 창밖 큐브집. 왼쪽은 넉넉한 실내 바닥."),
 ("people","식당 실내, 오른쪽에 나무 식탁과 저 뒤로 식사하는 다른 손님 몇 명(작게). 왼쪽은 넉넉한 통로 공간. 의자 없음(테이블만)."),
 ("counter","식당 계산대. 오른쪽에 나무 계산대와 카드 단말기·영수증 종이롤·작은 화분. 왼쪽은 넉넉한 실내 바닥."),
 ("closeup","오른쪽에 나무 식탁 위 음식 클로즈업(김 나는 찌개·밥·색색 반찬·젓가락), 뒤로 창밖 감천 큐브집 흐릿. 왼쪽은 부드러운 실내 여백. 의자 없음."),
 ("sunset","감천마을 노을. 오른쪽에 알록달록 큐브집 언덕과 노을 하늘·계단길, 왼쪽은 넉넉한 골목길."),
]
def run(j):
    name,scene=j; path=f"{BD}/bg_w11_{name}.png"
    try:
        subprocess.run(["agy","-p",BG.format(path=path,scene=scene),"--dangerously-skip-permissions"],capture_output=True,text=True,timeout=440,encoding="utf-8",errors="ignore")
        return f"{'OK' if os.path.exists(path) else 'MISS'} {name}"
    except Exception as e: return f"ERR {name}: {str(e)[:30]}"
print(f"{len(ITEMS)}개 배경 생성(병렬4)",flush=True)
with ThreadPoolExecutor(max_workers=4) as ex:
    d=0
    for f in as_completed({ex.submit(run,j):j for j in ITEMS}):
        d+=1; print(f"[{d}/{len(ITEMS)}] {f.result()}",flush=True)
print("DONE",flush=True)
