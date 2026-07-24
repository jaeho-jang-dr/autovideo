# -*- coding: utf-8 -*-
"""★캐릭터 배치 가드 (사장님 최우선 원칙, 2026-07-14)
   "배경은 크나 작으나 상관없다. 캐릭터는 크기 일관성·방향·위치가 아주 중요하고 절대 잘리면 안 된다."

   렌더 전에 전 씬을 검사한다:
     ① 잘림 금지 — 인물이 화면(1280x720) 밖으로 1px도 나가면 FAIL
     ② 크기 일관성 — 서기끼리 같은 키, 앉기끼리 같은 크기(서기의 60%), 누움=길이 100%
   FAIL이 하나라도 있으면 exit 1 → 렌더하지 말 것.

사용: python check_char_fit.py [EPISODE]   (기본 KO-W14)
"""
import sys, os, json, sqlite3
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "hangeul_birth_vowels"))
import compile_stickman as cs   # noqa: E402

EP = sys.argv[1] if len(sys.argv) > 1 else "KO-W14"
cs.EP = EP
W, H = cs.W, cs.H

STAND_H = 432.0                 # 서기 인물 렌더 높이 = 100% 기준
TOL = 0.08                      # 크기 편차 허용 8%
# ★비율은 W11(감천 식당, 성공작) 실측값을 따른다 — 임의로 정하지 말 것.
#   W11: 서기 403~420px / 앉기 302~318px → 앉기 = 서기의 약 76%
RATIO = {"stand": 1.00, "sit": 0.76, "lying": 0.85, "crouch": 0.50}   # 누움=가로길이 / 쪼그림=서기 50%

SIT_POSES = {"eat_sit", "drink_sit", "sit_desk", "work_laptop", "work_laptop_a", "study_book",
             "study_book_a", "read_book", "write_note", "write_note_a", "rest_sit", "watch_tv",
             "write_diary", "wake_sit", "sit_stargaze",
             # W16(취미) 앉기 포즈 = 서기의 76%
             "piano", "reading_bench", "gaming", "watching_movie", "picnic_sit"}
CROUCH_POSES = {"winter_snowman", "snowman"}   # 쪼그려 앉는 자세 = 서기의 50% (사장님 지시)


def fig_box(path):
    im = Image.open(path).convert("RGBA")
    a = np.array(im)[:, :, 3]
    ys, xs = np.where(a > 20)
    return im.size, xs.min(), ys.min(), xs.max(), ys.max()


def rendered(path, cx, cy, sc):
    (Wc, Hc), x0, y0, x1, y1 = fig_box(path)
    L = cx - Wc * sc / 2 + x0 * sc
    R = cx - Wc * sc / 2 + x1 * sc
    T = cy - Hc * sc / 2 + y0 * sc
    B = cy - Hc * sc / 2 + y1 * sc
    return L, T, R, B


def main():
    con = sqlite3.connect(cs.DB)
    scenes = cs.load_scenes("ko")
    fails, rows = [], []
    for s in scenes:
        bj = con.execute("SELECT beats_json FROM anim_sequences WHERE seq_name=?",
                         (s.get("anim_seq"),)).fetchone()
        poses = [b["name"] for b in json.loads(bj[0])] if bj else []
        cobj = [o for o in s["objs"] if "/poses/" in o["path"].replace("\\", "/")]
        if not cobj or not poses:
            continue
        o = cobj[0]
        for pose in sorted(set(poses)):
            pp, flip, pen = cs.char_pose_info(s.get("char_key"), pose)
            if not pp or not os.path.exists(pp):
                fails.append(f"S{s['seq']:>2} {pose:<14} ★포즈 파일 없음")
                continue
            L, T, R, B = rendered(pp, o["cx"], o["cy"], o["scale"])
            kind = ("lying" if pose == "sleep" else "crouch" if pose in CROUCH_POSES
                    else "sit" if pose in SIT_POSES else "stand")
            size = (R - L) if kind == "lying" else (B - T)     # 누움=가로 길이
            want = STAND_H * RATIO[kind]
            cut = []
            if T < 0:    cut.append(f"위{-T:.0f}")
            if B > H:    cut.append(f"아래{B-H:.0f}")
            if L < 0:    cut.append(f"왼{-L:.0f}")
            if R > W:    cut.append(f"오른{R-W:.0f}")
            dev = abs(size - want) / want
            bad = []
            if cut:              bad.append("잘림:" + ",".join(cut) + "px")
            if dev > TOL:        bad.append(f"크기{size:.0f}px(목표{want:.0f}, {dev*100:.0f}%↔)")
            rows.append((s["seq"], pose, kind, size, T, B, bad))
            if bad:
                fails.append(f"S{s['seq']:>2} {pose:<14} {kind:<5} " + " / ".join(bad))
    con.close()

    print(f"=== 캐릭터 배치 검사 [{EP}] 화면 {W}x{H} | 서기기준 {STAND_H:.0f}px ===")
    print(f"검사 {len(rows)}건 (씬×포즈)\n")
    for kind in ("stand", "sit", "lying"):
        sizes = [r[3] for r in rows if r[2] == kind]
        if sizes:
            print(f"  {kind:<6} {len(sizes):>3}건  크기 {min(sizes):.0f}~{max(sizes):.0f}px "
                  f"(목표 {STAND_H*RATIO[kind]:.0f}) 편차 {max(sizes)-min(sizes):.0f}px")
    if fails:
        print(f"\n★★FAIL {len(fails)}건 — 렌더 금지:")
        for f in fails:
            print("   ", f)
        sys.exit(1)
    print("\n✅ 통과: 잘림 0, 크기 일관성 OK — 렌더해도 좋다")


if __name__ == "__main__":
    main()
