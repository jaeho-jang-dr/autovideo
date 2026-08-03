# -*- coding: utf-8 -*-
"""W23 인준 캐릭터 에셋 생성 드라이버 (동작 동영상 → 컷랑 프레임컷).

★사장님 확정 규칙 (2026-07-27)
  - 가이드 3종은 **기존 injun_w20 원본 그대로**(W23/guides/). 머리부터 신발까지 딱 이대로 뽑는다.
    → 프롬프트에 동일성 제약을 **엄격하게** 박는다(STRICT).
  - 오른걷기는 이미 프레임이 있고 왼걷기는 좌우반전으로 만들었다 → 걷기는 Flow 생성 제외.
  - Flow 운용: **계정 라운드로빈 0,1,0,2** · **클립마다 크롬 전부 kill 후 재기동으로 세션 리셋**
    · **옴니플러스 실패 시 Veo 3.1 - Lite**(이 스크립트는 처음부터 Lite로 간다).
  - 일반 동작 = 8초 전부 상영 → 컷랑 **3프레임 간격 64컷**.

사용:
  python gen_w23_assets.py --list                 # 작업 목록만 출력
  python gen_w23_assets.py --only greet_wave      # 하나만
  python gen_w23_assets.py --start 0 --count 3    # 앞에서 3개만
  python gen_w23_assets.py                        # 전부(이미 있는 mp4는 건너뜀)
"""
import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
# ★업로드는 불투명 흰배경 사본을 쓴다 — 투명 PNG(91% 투명)는 Flow 업로드 타일이 뜨지 않는다(2026-07-27 실측)
GUIDE_FRONT = "W23/guides/upload/injun_w23_guide_front.png"
GUIDE_3Q = "W23/guides/upload/injun_w23_guide_3q.png"
GUIDE_SIDE = "W23/guides/upload/injun_w23_guide_side.png"
CLIPS = "W23/clips"
PROMPTS = "W23/prompts"
PROFILE_CYCLE = [0, 1, 0, 2]          # ★사장님 확정 순환

CHAR = ("A simple 2D cartoon illustration of a young man drawn in a flat storybook style with clean "
        "black outlines: short black hair, small friendly smile, navy blue short-sleeve t-shirt, "
        "beige trousers, white sneakers, flat colour fill. This is an original cartoon drawing, "
        "not a real person.")
# ★사장님 지시(2026-07-27): 윈드밀에서 다리가 3개로 나왔다 → 팔·다리의 개수/크기/위치와
#   인체공학적 가동범위를 프롬프트에 못 박는다. 신발은 양쪽 다 순백.
ANATOMY = ("ANATOMY LOCK — this is the most important rule: the body structure must never deform. "
           "Exactly one head, two arms with two hands, and two legs with two feet in white sneakers are "
           "visible at every single moment — never a third arm or a third leg, never a duplicated, "
           "doubled or ghosted limb. Each arm and leg keeps the same length and thickness for the whole "
           "clip; no stretching, shrinking, melting, rubber-bending, merging into the torso or dissolving "
           "into a smear, and no limb is ever hidden behind or fused with the body. Every limb stays a "
           "clearly separated shape with its own clean black outline. Each hand always has exactly five "
           "clearly drawn fingers with outlines — never a fingerless stump, a mitten, a blurred paw or a "
           "hand with the wrong number of fingers. Joints move only the way a real "
           "human body can: elbows and knees hinge in one natural direction only, shoulders and hips stay "
           "inside a normal human range of motion, the neck and spine never twist past a natural angle. "
           "The torso, hips and legs always move together as one connected body: never hold the upper body "
           "still while the hips or legs spin around underneath it, and never wring or twist the waist — a "
           "real spine would break. When the body turns, the shoulders, chest, hips and legs all turn together. "
           "All movement must be anatomically correct and physically plausible, like a real trained "
           "gymnast filmed at normal speed. Both sneakers are pure white on both feet the whole time.")
STRICT = (ANATOMY + " "
          "Keep the same cartoon drawing style, outfit and colours as the picture: navy t-shirt, beige "
          "trousers, white sneakers, short black hair, clean black outlines, flat colours. Only the pose "
          "and movement change. Show the whole figure from head to shoes inside the frame the whole time, "
          "fixed camera, plain white background, no shadow, no ground line, no extra objects, "
          "no other characters, no text or lettering. Smooth continuous 8-second animation, 24fps, "
          "friendly and cheerful tone. Move the WHOLE body — torso, shoulders, hips, head and legs all take part; never animate only a hand or forearm while the rest stays frozen. Keep the motion lively and expressive "
          "from the first second to the last, with no long still hold at the end.")

# (키, 가이드, 동작 프롬프트)  ※걷기는 제외(이미 프레임 보유)
JOBS = [
    ("greet_wave", GUIDE_FRONT,
     "A lively full-body greeting: he steps forward with a bright smile, swings his right arm up high and waves "
     "with the whole arm and shoulder, his upper body leaning with the motion; then he bows forward from the waist "
     "with a warm smile, straightens back up, and finally opens both arms wide in a big welcoming gesture, "
     "shoulders and torso moving the whole time."),
    # ★windmill_up 폐기(2026-07-27): 하체 회전은 Veo가 다리를 3개로 그리고, 상체 고정+하체 회전 자체가
    #   척추가 못 버티는 동작이다(사장님 지적). → 회전 없는 **한 손 프리즈**로 단순화해 교체한다.
    ("onehand_freeze", GUIDE_FRONT,
     "A short and simple breakdance move, only four phases: stand, jump, freeze, stand up again. "
     "He starts standing straight. He bends his knees and jumps straight up once, both arms swinging upward. "
     "As he comes back down he drops onto ONE hand planted flat on the floor and stops there in a breakdance "
     "freeze — his weight held on that single arm, body tilted, one knee bent and the other leg lifted — and "
     "he holds that freeze completely still for about one second. Then he pushes off that hand, brings both "
     "feet back under him and stands straight up again with a bright smile. "
     "His legs never spin or rotate around his body: the whole body goes up and comes down as one piece, "
     "and he always has exactly two legs and two arms, each leg ending in one white sneaker."),
    ("backflip_land", GUIDE_FRONT,
     "He takes a short run-up, launches into a full backflip somersault in the air, lands cleanly on both feet and opens both arms wide in a finishing pose."),
    ("railing_vault", GUIDE_SIDE,
     "He places one hand down and vaults over an invisible waist-high railing, swinging both legs across, lands on his feet, then checks a wristwatch."),
    ("jump_highfive", GUIDE_3Q,
     "He jumps up and swings his right arm high for a high-five, lands, then extends his right hand forward for a handshake."),
    # ★'something' 이라고 두면 Veo 가 알아서 채운다 — 1차본에서 흰 배경에 자동차가 얼굴 앞을
    #   지나갔다(사장님 지적). 날아오는 물체는 **드론으로 지정**한다.
    ("lean_back_surprise", GUIDE_3Q,
     "A small four-rotor toy drone flies in fast from the right at head height: he leans his upper body back "
     "sharply with wide surprised eyes and both hands raised, the little drone buzzes past in front of his "
     "face and out of frame to the left, then he straightens up and smiles. The only extra object in the "
     "whole clip is that one small drone — no vehicles, no other objects, nothing else enters the frame."),
    ("point_far_follow", GUIDE_3Q,
     "He stretches his right arm out to point into the distance, and his head and eyes slowly follow something moving in a circle from right to left."),
    ("follow_parade", GUIDE_FRONT,
     "He follows something passing by with his eyes and turning head, tracing it with his right hand from right to left, smiling and slightly bouncing."),
    ("spin_phone", GUIDE_FRONT,
     "He spins once in place on the spot, pulls a phone from his pocket, holds it to his ear and talks, nodding twice."),
    ("board_write", GUIDE_3Q,
     "He holds a small notepad against an invisible board at chest height, writes on it with a pen, clicks the pen, then taps the note with his index finger."),
    ("run_slide_in", GUIDE_SIDE,
     "He runs in from the left and stops abruptly with a one-foot slide, arms swinging out for balance, then straightens up into a confident standing pose."),
    ("catch_petal", GUIDE_FRONT,
     "He looks up, reaches out and snatches a falling petal out of the air with one hand, looks at his closed hand, opens it and smiles."),
    ("check_ok", GUIDE_FRONT,
     "He draws a big circle in the air with his right index finger, then gives a clear thumbs-up with a bright smile."),
]


def log(m):
    print(m, flush=True)


def kill_chrome():
    """★클립마다 크롬 전부 종료 → 재기동으로 로그인 세션 리셋(사장님 확정 성공요인)."""
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
    time.sleep(3)


def gen(key, guide, motion, profile_idx):
    os.makedirs(CLIPS, exist_ok=True)
    os.makedirs(PROMPTS, exist_ok=True)
    out = f"{CLIPS}/injun_w23_{key}.mp4"
    if os.path.exists(out) and os.path.getsize(out) > 200_000:
        log(f"  [건너뜀] 이미 있음 {out}"); return True
    pf = f"{PROMPTS}/{key}.txt"
    with open(pf, "w", encoding="utf-8") as f:
        f.write(f"{CHAR}\n\nMOTION: {motion}\n\n{STRICT}\n")
    kill_chrome()
    profile = os.path.join(ROOT, "assets", f"chrome_profile_{profile_idx}")
    log(f"  [생성] {key}  프로필 {profile_idx}  가이드={os.path.basename(guide)}")
    r = subprocess.run([sys.executable, "flow_cdp_pipeline.py", "--image", guide,
                        "--prompt-file", pf, "--out", out, "--aspect", "9:16",   # ★캐릭터 클립은 9:16 (사장님 확정)
                        "--model", "Veo 3.1 - Lite", "--profile", profile],
                       cwd=ROOT)
    ok = os.path.exists(out) and os.path.getsize(out) > 200_000
    log(f"  [{'OK' if ok else '실패'}] {key}  rc={r.returncode}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=len(JOBS))
    a = ap.parse_args()
    jobs = [j for j in JOBS if (not a.only or j[0] == a.only)]
    jobs = jobs[a.start:a.start + a.count]
    if a.list:
        for i, (k, g, m) in enumerate(JOBS):
            mark = "有" if os.path.exists(f"{CLIPS}/injun_w23_{k}.mp4") else " "
            print(f"{i:2d} [{mark}] {k:20s} guide={os.path.basename(g):28s} {m[:60]}…")
        print(f"\n총 {len(JOBS)}개 (걷기는 기존 프레임 사용 → 생성 제외)")
        return
    done, fail = [], []
    for i, (k, g, m) in enumerate(jobs):
        p = PROFILE_CYCLE[i % len(PROFILE_CYCLE)]
        log(f"\n===== [{i+1}/{len(jobs)}] {k} =====")
        (done if gen(k, g, m, p) else fail).append(k)
    log(f"\n완료 {len(done)} / 실패 {len(fail)}")
    if fail:
        log("실패: " + ", ".join(fail))


if __name__ == "__main__":
    main()
