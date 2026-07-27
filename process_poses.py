# -*- coding: utf-8 -*-
"""정지 포즈 raw(agy) → 컷아웃 + 키770px 통일(motion컷과 동일) + 살색 + DB.
사용: python process_poses.py"""
import sys, os, glob, io, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import numpy as np
from PIL import Image
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
import cutrang  # cutout_char, body_metrics, normalize
DB = "channel/content.db"
TARGET_BODY, FEET_Y, CW, CH = 770, 1209, 1024, 1280
SKIN_TARGET = np.array([243, 198, 163])


def skin_recolor(rgba):
    a = rgba[:, :, 3] > 0
    rgb = rgba[:, :, :3].astype(int)
    R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    m = a & (R >= 198) & (R <= 250) & (G >= 178) & (G <= 238) & (B >= 150) & (B <= 225) & (R >= G) & (G > B) & ((G - B) >= 5) & ((R - B) >= 12) & ((R - B) <= 62) & ~((R > 245) & (G > 245) & (B >= 240))
    if m.sum() == 0:
        return rgba
    mean = rgb[m].mean(0)
    delta = (SKIN_TARGET - mean).round().astype(int)
    rgba[:, :, :3][m] = np.clip(rgba[:, :, :3][m].astype(int) + delta, 0, 255)
    return rgba


def shoe_white(rgba, feet_y=FEET_Y, body=TARGET_BODY):
    """발 영역의 회색 신발 본체를 가이드 흰색으로. 검정 외곽선·유채색(옷)은 보존."""
    a = rgba[:, :, 3] > 0
    rgb = rgba[:, :, :3].astype(int)
    R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    lo = rgb.min(2); hi = rgb.max(2)
    yy = np.arange(rgba.shape[0])[:, None]
    foot = a & (yy > (feet_y - 0.12 * body))          # 아래 신발 영역
    shoe = foot & (lo > 118) & ((hi - lo) < 34)        # 밝은~중간 무채색(신발), 검정외곽선(lo<=118) 제외
    rgba[:, :, 0][shoe] = 250; rgba[:, :, 1][shoe] = 250; rgba[:, :, 2][shoe] = 250
    return rgba


def main():
    raws = sorted(glob.glob("W22/poses/jieun_w22_*_raw.png"))
    con = sqlite3.connect(DB); cur = con.cursor()
    made = []
    for r in raws:
        pose = os.path.basename(r).replace("jieun_w22_", "").replace("_raw.png", "")
        arr = np.array(Image.open(r).convert("RGBA"))
        crop = cutrang.cutout_char(arr)
        if crop is None:
            print("SKIP no char", pose); continue
        cv, span = cutrang.normalize(crop, TARGET_BODY, FEET_Y, CW, CH)
        out = np.array(cv)   # ★색 변경 안 함(agy 원본 그대로). 컷아웃+키770 정규화(스케일)만.
        op = f"assets/graphics/poses/jieun_w22_{pose}.png"
        Image.fromarray(out).save(op); made.append((pose, op))
        print(f"  {pose}: 원몸높이 {span}px → 770px  → {op}")
        # DB
        name = f"jieun_w22 {pose} 정지포즈 투명컷"
        cur.execute("DELETE FROM asset_catalog WHERE project='W22' AND category='캐릭터정지포즈' AND name=?", (name,))
        cur.execute("""INSERT INTO asset_catalog(project,category,name,location,kind,storage,count,bytes,db_table,note,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
            ('W22', '캐릭터정지포즈', name, op, 'png', 'local', 1, os.path.getsize(op), None,
             f'정지포즈 {pose}. agy생성→컷아웃→키770px통일(발끝1209,캔버스1024x1280,motion컷과 동일)→살색. Teacher JY.'))
    con.commit(); con.close()
    print(f"\n총 {len(made)} 포즈 처리+DB 등록")
    for p, o in made: print(" ", p)


if __name__ == "__main__":
    main()
