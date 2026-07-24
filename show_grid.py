# -*- coding: utf-8 -*-
"""여러 이미지를 화면에 3xN 타일로 동시에 띄운다(각각 별도 창).
사용: pythonw show_grid.py <img1> <img2> ... [--cols N]"""
import sys, os
import tkinter as tk
from PIL import Image, ImageTk

args = [a for a in sys.argv[1:]]
cols = 3
if "--cols" in args:
    i = args.index("--cols"); cols = int(args[i+1]); del args[i:i+2]
imgs = args
n = len(imgs)
rows = (n + cols - 1) // cols

root = tk.Tk(); root.withdraw()
sw = root.winfo_screenwidth(); sh = root.winfo_screenheight()
cw = sw // cols
ch = sh // rows
photos = []
for i, p in enumerate(imgs):
    r, c = divmod(i, cols)
    win = tk.Toplevel(); win.configure(bg="#15181d")
    win.title(f"[{i+1}/{n}] {os.path.basename(p)}")
    ww = cw - 8; wh = ch - 48
    try:
        im = Image.open(p); im.thumbnail((ww, wh))
        ph = ImageTk.PhotoImage(im); photos.append(ph)
        tk.Label(win, image=ph, bg="#15181d").pack(padx=2, pady=2)
    except Exception as e:
        tk.Label(win, text=f"ERR {os.path.basename(p)}\n{e}", fg="#f66", bg="#15181d").pack()
    win.geometry(f"+{c*cw}+{r*ch}")
    win.attributes("-topmost", True)
    win.bind("<Escape>", lambda e: root.destroy())
# 첫 창 하나에 전체 닫기 안내
root.bind_all("<Escape>", lambda e: root.destroy())
root.mainloop()
