# -*- coding: utf-8 -*-
"""W23 DB 발음 클립을 Azure 선희(여성)로 생성 → web/public/audio/jamo/ (2026-07-28).

★함정: `save_tts_azure` 의 성별은 `EDGE_ACTIVE_VOICE` 로 결정된다. 낡은 클립이 남성으로
  들어가 있으면 여성 폴더에 있어도 남자 목소리가 난다 → **덮어써야** 한다.

대상 = W23_scenario.md 의 글리프(단어·표현) + '따라 해 보세요' 앞 발음 예문(온전한 문장만).
사용: python gen_w23_db_voice.py [--list]
"""
import os
import re
import sys

os.environ["TTS_ENGINE"] = "azure"
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"          # ★여성(선희)
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
import tts_manager as tm                            # noqa: E402
try:
    tm.load_env()
except Exception as e:
    print("load_env warn:", e)

OUT = "web/public/audio/jamo"                        # 여성 폴더
SCEN = "W23/W23_scenario.md"

# ★잘린 나레이션 조각 대신 손으로 확정한 온전한 발음 예문 (DB 클립은 다른 언어판에서도 재사용)
SENTENCES = [
    "약속이 있어요, 약속을 지켜요",
    "친구와 저녁 약속을 잡았어요",
    "다 같이 시간 조율이 필요해요",
    "금요일에 동아리 모임이 있어요",
    "다음 주에 회식이 있어요",
    "장소를 정해요, 장소가 어디예요",
    "찾기 쉬운 장소가 좋아요",
    "시간부터 정하면 장소는 금방이죠",
    "언제가 괜찮으세요?",
    "혹시 토요일 오후에 괜찮으세요?",
    "가능한 시간을 알려 주세요",
    "일요일 오전은 어떠세요?",
    "정문 앞에서 만나요",
    "그럼 그렇게 해요",
    "카페에서 만나요",
    "역에서 만나요",
]


def words_from_scenario():
    out = []
    for ln in open(SCEN, encoding="utf-8"):
        m = re.match(r"^- \*\*S\d+\*\*\s*(.*)$", ln.strip())
        if not m:
            continue
        parts = [p.strip() for p in m.group(1).split("|")]
        if len(parts) < 3:
            continue
        for g in parts[1].strip("`").split("·"):
            g = re.sub(r"\s*\(.*?\)", "", g.strip().strip("`")).strip()
            if g and re.fullmatch(r"[가-힣 ?]+", g):
                out.append(g)
        for q in re.findall(r"'([^']{1,20})'", parts[2].split("→")[0]):
            q = q.strip()
            if re.fullmatch(r"[가-힣 ?]+", q):
                out.append(q)
    seen, uniq = set(), []
    for w in out + SENTENCES:
        if w not in seen:
            seen.add(w); uniq.append(w)
    return uniq


def fname(w):
    """★파일명에서 물음표 등 금지문자를 뺀다(기존 DB 규칙: '괜찮으세요.mp3').
    말하는 텍스트에는 '?' 를 그대로 남겨 억양을 살린다."""
    return re.sub(r'[?*:"<>|/\\]', "", w).strip()


if __name__ == "__main__":
    words = words_from_scenario()
    if "--list" in sys.argv:
        for i, w in enumerate(words, 1):
            mark = "有" if os.path.exists(f"{OUT}/{fname(w)}.mp3") else " "
            print(f"{i:3d} [{mark}] {w}")
        print(f"\n총 {len(words)}개")
        sys.exit(0)
    os.makedirs(OUT, exist_ok=True)
    print(f"=== W23 DB 발음 클립 {len(words)}개 → Azure 선희(여성) → {OUT} ===", flush=True)
    ok = fail = 0
    for i, w in enumerate(words, 1):
        try:
            tm.save_tts_azure(w, f"{OUT}/{fname(w)}.mp3", "ko")
            ok += 1
            print(f"  [{i:3d}/{len(words)}] {w}", flush=True)
        except Exception as e:
            fail += 1
            print(f"  ★FAIL {w}: {str(e)[:80]}", flush=True)
    print(f"### 완료: 성공 {ok} / 실패 {fail} ###")
