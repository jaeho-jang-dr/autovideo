# -*- coding: utf-8 -*-
"""컷랑 모션시퀀스 — 8초 동작영상 → 매 step번째 프레임 N장 투명컷 → 고정배율·발고정 정규화 → DB.
걷기(사이클)와 달리 숙이기/가리키기 등 포즈변화 동작용: 프레임별 키정규화(X) → 고정배율(첫 서있는 프레임 기준)로
전체 동일 배율, 발끝 y고정, 발 중심 x고정 → 숙이면 자연히 낮아지고 발은 planted.
사용: python cut_motion_seq.py --video V.mp4 --char jieun_w22 --action look_out --project W22 [--step 3 --count 64]
"""
import sys, os, glob, subprocess, sqlite3, argparse, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import numpy as np
from PIL import Image
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
import cutrang  # cutout_char, body_metrics
DB = "channel/content.db"
DN = subprocess.DEVNULL


def feet_cx(crop):
    a = crop[:, :, 3] > 0
    H = crop.shape[0]
    ys, xs = np.where(a[int(H*0.86):])
    if len(xs) == 0:
        ys, xs = np.where(a)
    return float(xs.mean()) if len(xs) else crop.shape[1]/2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--char", required=True)
    ap.add_argument("--action", required=True)
    ap.add_argument("--project", default="W22")
    ap.add_argument("--step", type=int, default=3)
    ap.add_argument("--count", type=int, default=64)
    ap.add_argument("--target-body", type=int, default=770)
    ap.add_argument("--feet-y", type=int, default=1209)
    ap.add_argument("--canvas", default="1024x1280")
    ap.add_argument("--out-dir", default="assets/graphics/poses")
    ap.add_argument("--preview", default="scratch/flow")
    a = ap.parse_args()
    cw, ch = (int(x) for x in a.canvas.split("x"))
    fy = a.feet_y

    tmp = "scratch/cutrang/motion"
    os.makedirs(tmp, exist_ok=True)
    for f in glob.glob(tmp+"/*.png"):
        os.remove(f)
    subprocess.run(["ffmpeg", "-y", "-i", a.video, "-vsync", "0", f"{tmp}/f%03d.png"], stdout=DN, stderr=DN)
    frames = sorted(glob.glob(f"{tmp}/f*.png"))
    picks = frames[0::a.step][:a.count]
    print(f"프레임 {len(frames)}개 → 매 {a.step}번째 {len(picks)}장 선택 (1,{1+a.step},...)")

    crops = []
    for p in picks:
        c = cutrang.cutout_char(np.array(Image.open(p).convert("RGBA")))
        crops.append(c)
    # ★고정배율: 서있는 키(첫 프레임=가이드 서기 포즈)의 머리~발 높이를 정확히 target_body에 맞춘다.
    #  bounding-box 높이(팔/머리카락 포함) 아님 → body_metrics(머리끝~발끝)로 측정. 서기 여러 프레임 중 최대.
    ref_spans = []
    for c in crops[:5]:
        try:
            sp, _ = cutrang.body_metrics(c)
            ref_spans.append(sp)
        except Exception:
            pass
    ref = max(ref_spans) if ref_spans else max(c.shape[0] for c in crops)
    S = a.target_body / ref
    print(f"고정배율 S={S:.3f} (서기 머리~발 {ref}px → 정확히 {a.target_body}px). 발끝 y{fy}, 발중심 x고정")

    made = []
    prev_dir = f"{a.preview}/{a.action}_seq"
    os.makedirs(prev_dir, exist_ok=True)
    for f in glob.glob(prev_dir+"/*.png"):
        os.remove(f)
    BG = (232, 232, 235)
    for i, crop in enumerate(crops):
        nh = max(1, round(crop.shape[0]*S)); nw = max(1, round(crop.shape[1]*S))
        im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)
        fcx = feet_cx(crop)*S
        cv = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        px = cw//2 - round(fcx); py = fy - nh
        cv.paste(im, (px, py), im)
        op = f"{a.out_dir}/{a.char}_{a.action}_{i}.png"
        cv.save(op); made.append(op)
        # preview frame on gray
        bg = Image.new("RGBA", (cw, ch), BG+(255,))
        Image.alpha_composite(bg, cv).convert("RGB").save(f"{prev_dir}/{i:03d}.png")
    print(f"투명컷 {len(made)}장 저장 → {a.out_dir}/{a.char}_{a.action}_0..{len(made)-1}.png")

    # DB
    con = sqlite3.connect(DB); cur = con.cursor()
    name = f"{a.char} {a.action} 동작 투명컷 {len(made)}"
    cur.execute("DELETE FROM asset_catalog WHERE project=? AND category='캐릭터동작컷' AND name=?", (a.project, name))
    loc = f"{a.out_dir}/{a.char}_{a.action}_0..{len(made)-1}.png"
    cur.execute("""INSERT INTO asset_catalog(project,category,name,location,kind,storage,count,bytes,db_table,note,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
        (a.project, '캐릭터동작컷', name, loc, 'png', 'local', len(made),
         sum(os.path.getsize(p) for p in made), None,
         f"컷랑 모션시퀀스: 매{a.step}째 {len(made)}장, 고정배율 발고정(키{a.target_body}). 8초 {len(made)/8:.0f}fps 상영. 창 등 배경 제거."))
    con.commit(); con.close()
    print(f"DB 등록: asset_catalog {a.project}/캐릭터동작컷/{name}")

    # 8초 프리뷰 (count/8 fps)
    fps = len(made)/8.0
    outmp4 = f"{a.preview}/{a.action}.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", f"{fps}", "-i", f"{prev_dir}/%03d.png",
                    "-pix_fmt", "yuv420p", "-vf", "scale=512:-2", "-r", f"{fps}", outmp4], stdout=DN, stderr=DN)
    print(f"프리뷰(8초 {fps:.1f}fps): {outmp4}")


if __name__ == "__main__":
    main()
