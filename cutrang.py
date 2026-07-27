# -*- coding: utf-8 -*-
"""컷랑 (CutRang) — 프레임컷 애니메이션 엔진 (동작영상 → 투명 스틸컷 시퀀스).
걷기에서 검증된 파이프라인을 모든 동작으로 일반화:
  Flow/Veo 동작영상 → 프레임 분해 → "밝고 무채색(배경·그림자·틈) 아닌 것 = 캐릭터" 투명컷
  → 기준 포즈에서 잰 키·발끝·캔버스로 통일(비율유지 리사이즈) → N프레임 간격 시퀀스 → DB 등록.
배경은 렌더에서 따로 살아있고, 컷은 키가 통일돼 있어 멀리(작게)/가까이(크게) 자유 배치.
동작 예: sit_down, stand_up, jump, cry, angry, shout, lie_roll, touch_wall, walk_r …
비순환 동작(앉기·점프)은 그대로, 순환/방향 동작(걷기)은 --reverse로 좌우반전 세트도 생성.

[1단계] 프레임 번호 매겨 뷰어에 띄우고 사람에게 구간/프레임 고르게:
  python cutrang.py dump --video VID.mp4 --window 0.3:5.0 [--fps 24] [--port 8930]
[2단계] 고른 프레임으로 컷아웃·키통일·DB등록:
  python cutrang.py build --video VID.mp4 --char jieun_w19 --action sit_down \
     --base assets/graphics/poses/jieun_w19_smile_bright.png \
     --frames 5,9,13,17,21,25,29,33   (또는 --start 5 --interval 4 --count 8) \
     [--reverse] [--project W19] [--out-dir assets/graphics/poses]
"""
import sys, os, glob, argparse, subprocess, sqlite3
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
DB = "channel/content.db"


# ───────────────────── 검증된 컷아웃/정규화 (걷기와 동일) ─────────────────────
HOLE_FILL_MAX = 8000   # 이보다 작은 '완전히 둘러싸인' 구멍은 메운다.
# 흰 운동화·흰 소품은 '밝은 무채색'이라 배경으로 잘려 구멍이 된다(한 짝 ≈4~5천px²).
# 예전 1500px² 로는 신발이 뻥 뚫린 채 남았다. 발 사이·팔 사이 같은 '열린 틈'은
# 이미지 가장자리와 이어져 있어 구멍으로 잡히지 않으므로 이 값을 올려도 안전하다.


def cutout_char(arr):
    """밝고 무채색(배경·바닥그림자·발/팔 사이)이 아닌 것 = 캐릭터.
    최대덩어리만(워터마크 제거) + 둘러싸인 구멍 메움(얼굴 하이라이트·흰 운동화), 열린틈은 투명 유지."""
    arr = arr.copy()
    rgb = arr[:, :, :3].astype(int)
    lo = rgb.min(axis=2); hi = rgb.max(axis=2)
    bg = (lo > 168) & ((hi - lo) < 45)
    fg = ~bg
    lbl, n = ndimage.label(fg)
    if n == 0:
        return None
    sizes = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    char = lbl == (int(np.argmax(sizes)) + 1)
    filled = ndimage.binary_fill_holes(char)
    hl, hn = ndimage.label(filled & ~char)
    if hn:
        hsz = ndimage.sum(np.ones_like(hl), hl, range(1, hn + 1))
        small = {i + 1 for i, a in enumerate(hsz) if a < HOLE_FILL_MAX}
        if small:
            char |= np.isin(hl, list(small))
    arr[~char, 3] = 0; arr[char, 3] = 255
    ys, xs = np.where(char)
    if len(ys) == 0:
        return None
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def body_metrics(crop):
    """머리끝~발끝 몸높이(든 팔 제외) + 몸통중심 x."""
    alpha = crop[:, :, 3] > 0
    w = alpha.sum(axis=1).astype(float); H = len(w)
    torso = np.median(w[int(H * 0.42):int(H * 0.72)]) or w.max()
    thr = max(0.5 * torso, 0.12 * w.max())
    head_top = 0
    for y in range(H):
        if w[y] >= thr and np.mean(w[y:y + 22] >= thr * 0.6) > 0.6:
            head_top = y; break
    span = (H - 1) - head_top
    band = alpha[int(H * 0.42):int(H * 0.72)]
    bx = np.where(band.any(axis=0))[0]
    cx = int(bx.mean()) if len(bx) else crop.shape[1] // 2
    return span, cx


def measure_base(path):
    """기준 포즈에서 키(몸높이)·발끝 y·캔버스 크기 자동 측정 → 동작컷을 여기 맞춘다."""
    im = Image.open(path).convert("RGBA"); a = np.array(im)
    ys, xs = np.where(a[:, :, 3] > 0)
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    span, _ = body_metrics(crop)
    return span, int(ys.max()), im.width, im.height     # target_body, feet_y, canvas_w, canvas_h


def normalize(crop, target_body, feet_y, cw, ch, scale=None):
    """비율유지 리사이즈(크롭X)로 몸높이 통일 + 발끝 정렬 + 몸통중심 가로정중앙.
    scale 을 주면 그 배율을 그대로 쓴다 — 앉기·점프처럼 몸높이가 줄어드는 동작에서
    프레임마다 770px로 늘리면 앉을수록 캐릭터가 커지는 역효과가 나므로,
    첫 컷에서 잰 배율을 전 컷에 고정한다(--lock-scale)."""
    span, cx = body_metrics(crop)
    s = scale if scale else target_body / span
    nw, nh = max(1, round(crop.shape[1] * s)), max(1, round(crop.shape[0] * s))
    im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)
    cv = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cv.paste(im, (cw // 2 - round(cx * s), feet_y - nh), im)
    return cv, span


def grab(vid, t, tmp):
    p = f"{tmp}/_g.png"
    subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", vid, "-frames:v", "1", p],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return np.array(Image.open(p).convert("RGBA"))


# ───────────────────── 1단계: 프레임 덤프 + 번호 ─────────────────────
def cmd_dump(a):
    t0, t1 = (float(x) for x in a.window.split(":"))
    tmp = a.out or "scratch/cutrang/dump"
    seq = tmp + "/seq"; num = tmp + "/numbered"
    for d in (seq, num):
        os.makedirs(d, exist_ok=True)
        for f in glob.glob(f"{d}/*.png"): os.remove(f)
    subprocess.run(["ffmpeg", "-y", "-ss", str(t0), "-t", str(t1 - t0), "-i", a.video,
                    "-vsync", "0", "-start_number", "0", f"{seq}/%04d.png"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    frames = sorted(glob.glob(f"{seq}/*.png"))
    print(f"프레임 {len(frames)}개 (t={t0}~{t1}s, {a.fps}fps)")
    try: font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 60); fsm = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 26)
    except Exception: font = fsm = ImageFont.load_default()
    for i, fp in enumerate(frames):
        crop = cutout_char(np.array(Image.open(fp).convert("RGBA")))
        cv = Image.new("RGBA", (1024, 1280), (255, 255, 255, 255))
        if crop is not None:
            span, cx = body_metrics(crop); s = 770 / span
            nw, nh = max(1, round(crop.shape[1] * s)), max(1, round(crop.shape[0] * s))
            im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)
            cv.paste(im, (512 - round(cx * s), 1210 - nh), im)
        prev = cv.convert("RGB").resize((440, 550), Image.LANCZOS)
        d = ImageDraw.Draw(prev)
        d.rectangle([6, 6, 116, 78], fill=(255, 214, 0)); d.text((16, 4), f"{i:02d}", fill=(0, 0, 0), font=font)
        d.text((124, 26), f"t={t0 + i / a.fps:.3f}s", fill=(60, 60, 60), font=fsm)
        prev.save(f"{num}/f{i:03d}.png")
    print(f"번호 프리뷰 {len(frames)}개 → {num}")
    print(f"뷰어: python viewer.py --web --port {a.port} {num}")
    if not a.no_serve:
        subprocess.run([sys.executable, "viewer.py", "--web", "--port", str(a.port), num])


# ───────────────────── 2단계: 컷아웃·키통일·DB ─────────────────────
def cmd_build(a):
    if a.frames:
        picks = [int(x) for x in a.frames.split(",") if x.strip()]
    else:
        picks = [a.start + a.interval * i for i in range(a.count)]
    tmp = "scratch/cutrang/build"; os.makedirs(tmp, exist_ok=True)
    seq = "scratch/cutrang/dump/seq"
    tb, fy, cw, ch = measure_base(a.base)
    print(f"기준({os.path.basename(a.base)}): 몸높이 {tb}px · 발끝 y{fy} · 캔버스 {cw}x{ch} → 동작컷 이 규격으로 통일")
    out_dir = a.out_dir
    made = []

    crops = []
    for fno in picks:
        src = f"{seq}/{fno:04d}.png"
        arr = np.array(Image.open(src).convert("RGBA")) if os.path.exists(src) else grab(a.video, fno / a.fps, tmp)
        crops.append(cutout_char(arr))
    spans = [body_metrics(c)[0] for c in crops]

    # 자세별 키 규격(사장님 확정): 서기 100% · 웅크리기 70% · 의자앉기 60% · 땅에 주저앉기 50%.
    # 원본 몸높이를 프레임마다 100%로 늘리면 앉을수록 커지고, 원본배율 고정은 규격을 안 지킨다.
    # → 가장 큰(선) 컷을 100%, 가장 작은(앉은) 컷을 --pose-floor% 로 두고 그 사이를 선형 배분.
    targets = [tb] * len(picks)
    if a.pose_floor:
        lo, hi = min(spans), max(spans)
        fr = a.pose_floor / 100.0
        rng = (hi - lo) or 1
        targets = [round(tb * (fr + (1 - fr) * (s - lo) / rng)) for s in spans]
        print(f"  [POSE] 서기 100%({tb}px) ~ 최저자세 {a.pose_floor}%({round(tb*fr)}px) 선형 배분")

    for i, (fno, crop, tgt) in enumerate(zip(picks, crops, targets)):
        cv, span = normalize(crop, tgt, fy, cw, ch)
        op = f"{out_dir}/{a.char}_{a.action}_{i}.png"
        cv.save(op); made.append(op)
        print(f"  {a.char}_{a.action}_{i}  <- 프레임 {fno}  원본몸높이 {span}px → {tgt}px ({round(tgt/tb*100)}%)")
    rev = []
    if a.reverse:
        for i, p in enumerate(made):
            rp = f"{out_dir}/{a.char}_{a.action}_rev_{i}.png"
            Image.open(p).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT).save(rp); rev.append(rp)
        print(f"  리버스(좌우반전) {len(rev)}컷 생성")
    # DB 등록
    con = sqlite3.connect(DB); cur = con.cursor()
    def reg(name, paths):
        cur.execute("DELETE FROM asset_catalog WHERE project=? AND category='캐릭터동작컷' AND name=?", (a.project, name))
        loc = f"{out_dir}/{os.path.basename(paths[0]).rsplit('_', 1)[0]}_0..{len(paths)-1}.png"
        cur.execute("""INSERT INTO asset_catalog (project,category,name,location,kind,storage,count,bytes,db_table,note,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
            (a.project, '캐릭터동작컷', name, loc, 'png', 'local', len(paths),
             sum(os.path.getsize(p) for p in paths), None,
             f"컷랑: 동작영상→투명컷·키{tb}px통일(기준 {os.path.basename(a.base)}). 프레임 {picks}."))
    reg(f"{a.char} {a.action} 동작 투명컷 {len(made)}", made)
    if rev:
        reg(f"{a.char} {a.action} 리버스 투명컷 {len(rev)}", rev)
    con.commit(); con.close()
    print(f"DB 등록 완료 (asset_catalog {a.project}/캐릭터동작컷). 렌더에선 이 컷들을 순환/전개해 배치·스케일.")


def main():
    ap = argparse.ArgumentParser(prog="cutrang", description="컷랑 — 프레임컷 애니메이션 엔진")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump"); d.add_argument("--video", required=True); d.add_argument("--window", default="0.3:5.0")
    d.add_argument("--fps", type=float, default=24); d.add_argument("--out"); d.add_argument("--port", type=int, default=8930)
    d.add_argument("--no-serve", action="store_true"); d.set_defaults(func=cmd_dump)
    b = sub.add_parser("build"); b.add_argument("--video", required=True); b.add_argument("--char", required=True)
    b.add_argument("--action", required=True); b.add_argument("--base", required=True)
    b.add_argument("--frames"); b.add_argument("--start", type=int, default=0); b.add_argument("--interval", type=int, default=4)
    b.add_argument("--count", type=int, default=8); b.add_argument("--fps", type=float, default=24)
    b.add_argument("--reverse", action="store_true"); b.add_argument("--project", default="W19")
    b.add_argument("--pose-floor", type=int, default=0,
                   help="가장 낮은 자세의 키(%%). 서기 100%% 기준 — 웅크리기 70, 의자앉기 60, 땅에 주저앉기 50")
    b.add_argument("--out-dir", default="assets/graphics/poses"); b.set_defaults(func=cmd_build)
    a = ap.parse_args(); a.func(a)


if __name__ == "__main__":
    main()
