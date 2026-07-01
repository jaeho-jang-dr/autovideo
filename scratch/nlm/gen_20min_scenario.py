# -*- coding: utf-8 -*-
"""Generate the 20-minute '세종대왕과 한글' scenario act-by-act from the NotebookLM
notebook (130 sources). Each act -> scratch/nlm/sejong/act_N.md (raw answer)."""
import json, subprocess, os

NB = "sejong"
OUT = "scratch/nlm/sejong"
os.makedirs(OUT, exist_ok=True)

FMT = ("각 장면마다 정확히 이 형식으로: '[장면 N]' 줄, 그 아래 '* 캐릭터: <나이대>', "
       "'* 한국어 나레이션: <2~4문장>', '* English narration: <같은 의미>', "
       "'* VISUAL: <Google Flow Veo로 만들 구체적 동작·카메라워킹·등장요소, 단순 줌인 금지>'. "
       "반드시 이 노트북 소스에 근거한 역사적 사실만 쓰고 과장하지 말 것. 마크다운만 출력(인용표시 불필요).")

ACTS = [
    ("1", "어린시절 (약 10세 소년 충녕대군)", 5,
     "1막: 세종(이도)의 어린시절. 충녕대군 시절의 총명함과 지독한 독서 일화(아파도 책을 놓지 않음 등), 태종과 형 양녕·효령과의 관계, 학문을 좋아한 성품을 5개 장면으로."),
    ("2", "청년 (약 18세 학자 대군, 혼인기)", 5,
     "2막: 세종의 청년기. 대군 시절의 깊은 학문 정진, 소헌왕후 심씨와의 혼인과 자녀들, 겸손하고 어진 인품, 셋째 아들로서 왕위와 거리가 있던 시기를 5개 장면으로."),
    ("3", "청년왕 (약 22~28세, 즉위 직후)", 6,
     "3막: 1418년 태종의 양위로 22세에 즉위. 집현전 설치와 인재 등용, 초기 국정과 민생, 한문을 몰라 글을 못 읽는 백성들의 고통을 목격하고 삼강행실도를 펴냈으나 그림만으론 한계를 느낀 일을 6개 장면으로."),
    ("4", "장년 (약 40~47세, 훈민정음 창제기)", 15,
     "4막(가장 중요, 전체에서 가장 길게=영상 5분 이상 분량): 훈민정음 창제의 전 과정을 매우 자세히. (1)창제 동기와 애민정신, (2)신하 몰래 침전에서 홀로 진행한 비밀 친제, (3)1443년 28자 창제, (4)집현전 젊은 학자들의 해례 작업, (5)1444년 운회 언해 사업, (6)최만리 등의 반대 상소 전말과 논점(사대·이두 충분론 등)과 세종의 반박·하옥, (7)자음의 제자 원리(발음기관 상형 ㄱㄴㅁㅅㅇ + 가획), (8)모음의 천지인 삼재 원리, (9)1446년 훈민정음 해례본 편찬과 정인지 서문·반포. 이 과정을 15개 장면으로 풍부하게."),
    ("5", "노년 (약 50~53세, 말년)", 6,
     "5막: 훈민정음 반포 이후. 용비어천가·석보상절·월인천강지곡 등으로 보급, 하급 관리 시험 과목 채택, 안질 등 병환으로 쇠약해진 말년, 1450년 승하, 그리고 유산(1997 유네스코 세계기록유산, 세종대왕 문해상, 한글날, 남북이 함께 쓰는 오늘의 한글)을 6개 장면으로 감동적으로 마무리."),
]

for num, char, scenes, instr in ACTS:
    prompt = f"{instr} 캐릭터(화자/등장)는 '{char}'. 총 {scenes}개 장면. {FMT}"
    print(f"=== ACT {num} ({char}) {scenes} scenes 생성중 ... ===", flush=True)
    r = subprocess.run(f'nlm notebook query {NB} "{prompt}"', shell=True,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    raw = r.stdout or ""
    answer = raw
    try:
        j = json.loads(raw)
        answer = j.get("value", {}).get("answer", raw)
    except Exception:
        pass
    path = os.path.join(OUT, f"act_{num}.md")
    open(path, "w", encoding="utf-8").write(answer)
    print(f"  -> {path} ({len(answer)} chars)", flush=True)

print("ALL_ACTS_DONE", flush=True)
