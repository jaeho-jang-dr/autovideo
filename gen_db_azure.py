# -*- coding: utf-8 -*-
"""DB 발음 클립을 Azure TTS 인준(ko-KR-InJoonNeural)으로 생성 → web/public/audio/jamo_m/.
사용: python gen_db_azure.py w10        # W10 대사 표현만(검증용)
      python gen_db_azure.py full       # jamo/(여성) 전체 이름 + W10신규를 인준으로 미러(있어도 덮어씀=Azure로 통일)
      python gen_db_azure.py full_fill   # jamo_m 에 없는 것만 채움(빠른 완비)
"""
import os, sys, glob
# 성별: argv[2]='female'/'f'/'선희' → 선희(jamo/), 아니면 인준(jamo_m)
GENDER = (sys.argv[2] if len(sys.argv) > 2 else "male").strip().lower()
FEMALE = GENDER in ("female", "f", "선희", "sunhi", "여")
os.environ["TTS_ENGINE"] = "azure"
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi" if FEMALE else "injoon"
sys.path.insert(0, os.getcwd())
import tts_manager as tm
try:
    tm.load_env()
except Exception as e:
    print("load_env warn:", e)

JD = "web/public/audio/jamo"      # 여성(선희)
JM = "web/public/audio/jamo_m"    # 남성(인준)
TARGET = JD if FEMALE else JM     # 생성 타깃 폴더
os.makedirs(TARGET, exist_ok=True)

W10 = ["얼마예요", "이거 주세요", "그거 주세요", "저거 주세요", "결제", "할인",
       "이거 얼마예요", "오천 원", "오천 원이에요", "지금 할인 중이에요", "카드", "현금",
       # 확장(30씬)
       "전부 얼마예요", "한 개 주세요", "두 개 주세요", "다른 거 있어요", "더 큰 거",
       "봉투 주세요", "영수증 주세요", "좀 깎아 주세요", "너무 비싸요", "만 원이에요",
       "숫자", "가게"]

# W12 교통·지하철 환승 (인천공항→강남역). scratch/w12_need_words.txt 에서 로드
def load_w12():
    p = "scratch/w12_need_words.txt"
    if not os.path.exists(p):
        print("w12 단어파일 없음:", p); sys.exit(1)
    return [l.strip() for l in open(p, encoding="utf-8") if l.strip()]

def load_w14():
    p = "scratch/w14_need_words.txt"
    if not os.path.exists(p):
        print("w14 단어파일 없음:", p); sys.exit(1)
    return [l.strip() for l in open(p, encoding="utf-8") if l.strip()]

def load_w13():
    p = "scratch/w13_need_words.txt"
    if not os.path.exists(p):
        print("w13 단어파일 없음:", p); sys.exit(1)
    return [l.strip() for l in open(p, encoding="utf-8") if l.strip()]

def load_w15():
    p = "scratch/w15_need_words.txt"
    if not os.path.exists(p):
        print("w15 단어파일 없음:", p); sys.exit(1)
    return [l.strip() for l in open(p, encoding="utf-8") if l.strip()]

def load_w22():
    p = "scratch/w22_need_words.txt"
    if not os.path.exists(p):
        print("w22 단어파일 없음:", p); sys.exit(1)
    return [l.strip() for l in open(p, encoding="utf-8") if l.strip()]

mode = sys.argv[1] if len(sys.argv) > 1 else "w10"
if mode == "w22":
    words = load_w22()
elif mode == "w22_fill":
    words = [w for w in load_w22() if not os.path.exists(f"{TARGET}/{w}.mp3")]
elif mode == "w15":
    words = load_w15()
elif mode == "w15_fill":
    words = [w for w in load_w15() if not os.path.exists(f"{TARGET}/{w}.mp3")]
elif mode == "w14":
    words = load_w14()
elif mode == "w14_fill":
    words = [w for w in load_w14() if not os.path.exists(f"{TARGET}/{w}.mp3")]
elif mode == "w13":
    words = load_w13()
elif mode == "w13_fill":
    words = [w for w in load_w13() if not os.path.exists(f"{TARGET}/{w}.mp3")]
elif mode == "w12":
    words = load_w12()
elif mode == "w12_fill":                       # 이미 있는 건 건너뛰고 없는 것만
    words = [w for w in load_w12() if not os.path.exists(f"{TARGET}/{w}.mp3")]
elif mode == "w10":
    words = W10
elif mode in ("full", "full_fill"):
    fem = [os.path.splitext(os.path.basename(p))[0] for p in glob.glob(f"{JD}/*.mp3")]
    words = sorted(set(fem) | set(W10))
    if mode == "full_fill":
        words = [w for w in words if not os.path.exists(f"{TARGET}/{w}.mp3")]
else:
    print("unknown mode"); sys.exit(1)

VOICE = "선희(SunHi)" if FEMALE else "인준(InJoon)"
print(f"=== mode={mode} gender={GENDER} : 대상 {len(words)}개 (Azure {VOICE} → {TARGET}) ===", flush=True)
ok = fail = 0
for i, w in enumerate(words):
    out = f"{TARGET}/{w}.mp3"
    try:
        tm.save_tts_azure(w, out, "ko")
        ok += 1
        if mode != "w10" and ok % 100 == 0:
            print(f"  …{ok}/{len(words)}", flush=True)
    except Exception as e:
        fail += 1
        print("  FAIL:", w, str(e)[:80], flush=True)
print(f"### 완료: 성공 {ok} / 실패 {fail} / 총 {len(words)} (Azure 인준 → {JM}) ###", flush=True)
