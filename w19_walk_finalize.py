# -*- coding: utf-8 -*-
"""지은 걷기 최종화: 오른쪽 8투명컷 → 좌우반전 왼쪽(돌아오기) 8컷 생성,
   오른쪽/왼쪽 걷기 영상(느린 속도) 조립, 모든 컷·영상 DB 저장.
"""
import os, glob, subprocess, sqlite3
from PIL import Image
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
POSE = "assets/graphics/poses"
OUT = "scratch/w19_walk"
os.makedirs("assets/videos", exist_ok=True)

# 1) 왼쪽(돌아오기) 컷 = 오른쪽 컷 좌우반전
rights = sorted(glob.glob(f"{POSE}/jieun_w19_walk_r_*.png"), key=lambda p: int(p.split("_")[-1].split(".")[0]))
lefts = []
for p in rights:
    i = int(p.split("_")[-1].split(".")[0])
    im = Image.open(p).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
    op = f"{POSE}/jieun_w19_walk_l_{i}.png"
    im.save(op); lefts.append(op)
print(f"왼쪽(돌아오기) 컷 {len(lefts)}개 생성")


def make_walk(cut_paths, out_mp4, direction="right"):
    frs = [Image.open(c).convert("RGBA") for c in cut_paths]
    CW, CH = frs[0].size
    BW, BH = 1280, 720
    bg = Image.new("RGB", (BW, BH), (224, 232, 240))
    scale = int(BH * 0.62) / CH
    cw2, ch2 = int(CW * scale), int(CH * scale)
    regr = [f.resize((cw2, ch2)) for f in frs]
    FPS, HOLD = 12, 4
    cyc = len(regr) * HOLD; stride = cw2 * 0.55
    if direction == "right":
        x0, x1 = -cw2, BW
    else:
        x0, x1 = BW, -cw2
    nframes = int(abs(x1 - x0) / stride * cyc)
    foot_y = int(BH * 0.965) - ch2
    tmp = f"{OUT}/_seqfin"; os.makedirs(tmp, exist_ok=True)
    for fn in os.listdir(tmp): os.remove(os.path.join(tmp, fn))
    for k in range(nframes):
        fr = bg.copy(); x = int(x0 + (x1 - x0) * (k / max(1, nframes - 1)))
        pose = regr[(k // HOLD) % len(regr)]; fr.paste(pose, (x, foot_y), pose); fr.save(f"{tmp}/f{k:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_mp4],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return nframes / FPS


dr = make_walk(rights, "assets/videos/jieun_w19_walk_right_slow.mp4", "right")
dl = make_walk(lefts, "assets/videos/jieun_w19_walk_left_slow.mp4", "left")
print(f"오른쪽 걷기 {dr:.1f}초 / 왼쪽(돌아오기) 걷기 {dl:.1f}초")

# 2) DB 저장(모든 컷 + 영상)
con = sqlite3.connect("channel/content.db"); cur = con.cursor()
cur.execute("DELETE FROM asset_catalog WHERE project='W19' AND category IN ('캐릭터걷기컷','캐릭터걷기영상')")
def reg(name, loc, kind, cnt, note):
    b = os.path.getsize(loc) if os.path.isfile(loc) else 0
    cur.execute("""INSERT INTO asset_catalog (project,category,name,location,kind,storage,count,bytes,db_table,note,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
        ('W19', '캐릭터걷기컷' if kind == 'png' else '캐릭터걷기영상', name, loc, kind, 'local', cnt, b, None, note))
reg("지은 오른쪽 걷기 투명컷 8", f"{POSE}/jieun_w19_walk_r_0..7.png", "png", 8,
    "Veo 걷기영상에서 추출·흰배경 border컷+엉덩이정합. 순환+우측이동=걷기. 497x736.")
reg("지은 왼쪽(돌아오기) 걷기 투명컷 8", f"{POSE}/jieun_w19_walk_l_0..7.png", "png", 8,
    "오른쪽컷 좌우반전(돌아오기). 순환+좌측이동.")
reg("지은 오른쪽 걷기 영상(느림)", "assets/videos/jieun_w19_walk_right_slow.mp4", "mp4", 1, "8투명컷 순환 HOLD4 느린속도.")
reg("지은 왼쪽 걷기 영상(느림)", "assets/videos/jieun_w19_walk_left_slow.mp4", "mp4", 1, "반전 8컷 순환 좌측이동.")
reg("지은 오른쪽 걷기 원본(Veo 8초)", "assets/videos/jieun_w19_walk_right.mp4", "mp4", 1, "Veo 원본. autoveo_flow --upload cut1 --motion 'walk right side view' --profile-idx 0 (검증).")
con.commit(); con.close()
print("DB 저장 완료 (asset_catalog: 걷기컷 16 + 영상 3)")
