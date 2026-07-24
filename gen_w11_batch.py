# -*- coding: utf-8 -*-
"""W11 에셋 일괄 생성: 마담제이 신규 포즈 18 + 배경 5 (agy 병렬 4). 검증된 방식(레퍼런스+고정 외형 스크립트)."""
import subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
REF = f"{ROOT}/assets/characters/cutouts/madam_jay_base_front.png"
POSE_DIR = f"{ROOT}/assets/graphics/poses"
BG_DIR = f"{ROOT}/assets/graphics/bg"

MJ = ("레퍼런스 이미지 " + REF + " 의 캐릭터(마담제이)와 외형이 똑같아야 한다: "
      "연한 코랄/살몬 V넥 선생님 조끼(왼가슴 작은 주머니에 펜 꽂힘, 조끼 아래 주름 니트 밴드 밑단, 흰 속옷), "
      "흰색 A라인 무릎길이 치마, 진갈색 위로 올린 탑번 쪽머리(가운데 가르마+얼굴 양옆 웨이브 잔머리 한 가닥), "
      "점 눈 두 개+작은 미소, 크림색 둥근 손, 크림색 슬립온 신발, 가는 스틱 팔다리, 굵고 부드러운 검정 외곽선 플랫 카툰, "
      "머리 크고 몸 작은 비율. 이 외형 그대로 포즈만 바꿔서 그려 {path} 에 저장해줘. "
      "순백색 배경, 전신, 캐릭터만(의자·테이블·소품·그림자·글자 전부 없음), 투명 컷아웃용, 몸은 오른쪽을 향함. 포즈: {pose}")

BG = ("감천문화마을(부산) 배경 그림을 그려서 {path} 에 저장해줘. 파스텔 스토리북 스타일, 따뜻한 조명, 부드러운 색. "
      "16:9 가로. 사람(캐릭터)은 절대 그리지 말 것. ⚠️절대 규칙: 화면 어디에도 글자·숫자·간판문구·상표를 넣지 마라. 장면: {scene}")

POSES = [
 ("enter", "오른쪽으로 걸어 들어가는 동작, 한 발 앞으로 내딛고 팔 자연스럽게, 옆모습, 걷는 느낌"),
 ("look_around", "서서 오른쪽을 두리번거리며 둘러보는, 한 손 이마에 살짝 얹고, 호기심 표정"),
 ("sit_plain", "의자 없이 무릎 굽혀 앉은 기본 자세, 오른쪽 향함, 두 손 무릎 위, 미소"),
 ("call_staff", "의자 없이 앉은 자세로 오른팔을 번쩍 위로 들어 점원을 부르는 손짓, 오른쪽 향함"),
 ("point_menu", "의자 없이 앉은 자세로 오른손 검지로 앞(오른쪽 아래) 메뉴를 가리키는"),
 ("lean_table", "의자 없이 앉은 자세로 상체를 앞(오른쪽)으로 기울여 들여다보는, 호기심 표정"),
 ("receive", "의자 없이 앉은 자세로 두 손을 앞으로 내밀어 무언가 받는, 오른쪽 향함"),
 ("chopsticks", "의자 없이 앉은 자세로 오른손에 젓가락을 들고 먹는 동작, 오른쪽 향함"),
 ("taste", "의자 없이 앉은 자세로 숟가락을 입에 가져가 맛보며 음미하는, 눈 살짝 감음, 오른쪽 향함"),
 ("thumbs_up", "의자 없이 앉은 자세로 오른손 엄지를 치켜세우는(맛있다), 활짝 미소, 오른쪽 향함"),
 ("fan_mouth", "의자 없이 앉은 자세로 매워서 입 앞에 손을 부채질하는, 놀란 표정, 오른쪽 향함"),
 ("drink_water", "의자 없이 앉은 자세로 물컵을 들어 마시는, 오른쪽 향함"),
 ("sip_soup", "의자 없이 앉은 자세로 숟가락으로 국물을 떠 후루룩 마시는, 만족 표정, 오른쪽 향함"),
 ("size_gesture", "의자 없이 앉은 자세로 두 손을 벌려 크기(양이 많다)를 표현하는, 오른쪽 향함"),
 ("pat_belly", "서서 한 손으로 배를 두드리며 배부른 만족 표정, 오른쪽 향함"),
 ("stand_up", "의자에서 막 일어서는 동작, 무릎 살짝 굽히고 상체 세움, 오른쪽 향함"),
 ("pay_card", "서서 오른손으로 카드를 앞으로 내미는 계산 동작, 오른쪽 향함"),
 ("receive_receipt", "서서 두 손으로 작은 영수증 종이를 받는, 오른쪽 향함"),
]
BGS = [
 ("alley", "감천문화마을 골목 전경. 알록달록 파스텔 큐브집들이 계단처럼 쌓인 언덕, 좁은 골목, 벽화, 소박한 식당들(간판은 글자 없이 그림만). 왼쪽은 캐릭터 걸을 공간으로 비우고 오른쪽에 골목과 식당."),
 ("entrance", "감천마을 작은 식당의 열린 출입문 앞. 나무문이 열려 안쪽 실내가 살짝 보이고, 문 옆에 화분. 오른쪽에 입구/문, 왼쪽은 캐릭터 설 공간으로 비움."),
 ("table_food", "식당 실내. 왼쪽~가운데에 빈 나무 의자(오른쪽 향함, 사람 없음), 그 오른쪽 나무 식탁에 음식이 가득 — 국그릇·밥공기·여러 반찬접시·작은 불판·물컵. 벽에 감천 벽화, 창밖 알록달록 큐브집 계단 풍경."),
 ("counter", "식당 계산대. 오른쪽에 나무 계산대와 카드 단말기·영수증 종이롤·작은 화분. 왼쪽은 캐릭터 설 공간으로 비움. 따뜻한 실내."),
 ("sunset", "감천문화마을 노을 골목. 주황빛 노을 하늘, 알록달록 큐브집들의 실루엣과 창문 불빛, 계단길. 왼쪽은 캐릭터 공간으로 비우고 오른쪽에 골목."),
]

jobs = []
for name, pose in POSES:
    path = f"{POSE_DIR}/madam_jay_w11_{name}.png"
    jobs.append((f"pose:{name}", MJ.format(path=path, pose=pose), path))
for name, scene in BGS:
    path = f"{BG_DIR}/bg_w11_{name}.png"
    jobs.append((f"bg:{name}", BG.format(path=path, scene=scene), path))

def run(job):
    tag, prompt, path = job
    try:
        r = subprocess.run(["agy", "-p", prompt, "--dangerously-skip-permissions"],
                           capture_output=True, text=True, timeout=420, encoding="utf-8", errors="ignore")
        ok = os.path.exists(path)
        return f"{'OK' if ok else 'MISS'} {tag} -> {os.path.basename(path)}"
    except Exception as e:
        return f"ERR {tag}: {str(e)[:40]}"

print(f"총 {len(jobs)}개 생성 시작 (병렬 4)", flush=True)
with ThreadPoolExecutor(max_workers=4) as ex:
    futs = {ex.submit(run, j): j for j in jobs}
    done = 0
    for f in as_completed(futs):
        done += 1
        print(f"[{done}/{len(jobs)}] {f.result()}", flush=True)
print("DONE", flush=True)
