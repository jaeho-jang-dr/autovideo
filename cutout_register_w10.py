# -*- coding: utf-8 -*-
"""W10 인준 35포즈: 흰배경 플러드필 컷아웃(신발 보존) → assets/graphics/poses/injun_w10_*.png
   → DB에 W10 전용 세트 등록(anim_characters 'injun_w10' + anim_char_poses 35 + assets 카탈로그)."""
import os, glob, sqlite3
import numpy as np
from scipy import ndimage
from PIL import Image

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
SRC = os.path.join(ROOT, "home_vocab/w10")
DST = os.path.join(ROOT, "assets/graphics/poses")
os.makedirs(DST, exist_ok=True)
DB = os.path.join(ROOT, "channel/content.db")

def cutout(src, out):
    arr = np.array(Image.open(src).convert("RGBA"))
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    white = (r > 235) & (g > 235) & (b > 230)
    lbl, n = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    bg = np.isin(lbl, list(border))
    arr[bg, 3] = 0
    ys, xs = np.where(arr[:, :, 3] > 0)
    crop = arr[ys.min():ys.max()+1, xs.min():xs.max()+1]
    Image.fromarray(crop).save(out)
    return crop.shape[1], crop.shape[0]

keys = sorted(os.path.splitext(os.path.basename(p))[0].replace("injun_w10_", "")
              for p in glob.glob(os.path.join(SRC, "injun_w10_*.png")))
print(f"컷아웃 대상: {len(keys)}개")
done = []
for k in keys:
    src = os.path.join(SRC, f"injun_w10_{k}.png")
    out = os.path.join(DST, f"injun_w10_{k}.png")
    w, h = cutout(src, out)
    done.append(k)
print(f"컷아웃 완료: {len(done)}개 → {DST}/injun_w10_*.png")

# DB 등록
db = sqlite3.connect(DB)
db.execute("DELETE FROM anim_char_poses WHERE char_key='injun_w10'")
db.execute("DELETE FROM anim_characters WHERE char_key='injun_w10'")
db.execute("""INSERT INTO anim_characters(char_key,korean_name,render_mode,features_json,pose_prefix,base_image,description,updated_at)
              VALUES('injun_w10','인준','cutout','{}','injun_w10_','injun_w10_base','W10 전용 인준 35포즈 세트(일관성 배치)',datetime('now'))""")
for k in done:
    fp = f"assets/graphics/poses/injun_w10_{k}.png"
    db.execute("INSERT INTO anim_char_poses(char_key,pose_name,file_path,flip,pen) VALUES('injun_w10',?,?,0,0)", (k, fp))
    # assets 카탈로그(중복 무시)
    ex = db.execute("SELECT 1 FROM assets WHERE file_path=?", (fp,)).fetchone()
    if not ex:
        db.execute("INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt,created_at) VALUES(?,?,?,?,?,datetime('now'))",
                   (f"인준W10_{k}", f"injun_w10_{k}", "pose", fp, ""))
db.commit()
n_ch = db.execute("SELECT COUNT(*) FROM anim_characters WHERE char_key='injun_w10'").fetchone()[0]
n_ps = db.execute("SELECT COUNT(*) FROM anim_char_poses WHERE char_key='injun_w10'").fetchone()[0]
print(f"DB 등록: anim_characters injun_w10={n_ch} / anim_char_poses={n_ps}")
db.close()
print("### 완료 ###")
