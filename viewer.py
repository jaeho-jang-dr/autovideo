# -*- coding: utf-8 -*-
"""재사용 이미지 뷰어 (네이티브 tkinter 창). Read 인라인이 안 보일 때 이걸로 띄운다.
사용:
  pythonw viewer.py 이미지1 [이미지2 ...]        # 지정 이미지들
  pythonw viewer.py 폴더                          # 폴더 내 이미지 전부
조작: ←/→ 또는 Space=다음, PgUp/PgDn, F=전체화면 토글, ESC=닫기, S=원본크기.
창 제목에 파일명·해상도 표시. 창은 항상 위(topmost)로 뜬다."""
import sys, os, glob
import tkinter as tk
from PIL import Image, ImageTk

EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")

def collect(args):
    files = []
    for a in args:
        if os.path.isdir(a):
            for e in EXT: files += sorted(glob.glob(os.path.join(a, f"*{e}")))
        elif os.path.isfile(a):
            files.append(a)
    return files

class Viewer:
    def __init__(self, files):
        self.files = files; self.i = 0
        self.root = tk.Tk()
        self.root.configure(bg="#111")
        self.root.attributes("-topmost", True)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{int(sw*0.8)}x{int(sh*0.85)}+{int(sw*0.1)}+{int(sh*0.05)}")
        self.lbl = tk.Label(self.root, bg="#111"); self.lbl.pack(fill="both", expand=True)
        self.fit = True
        self.root.bind("<Right>", lambda e: self.nav(1)); self.root.bind("<Left>", lambda e: self.nav(-1))
        self.root.bind("<space>", lambda e: self.nav(1)); self.root.bind("<Next>", lambda e: self.nav(1))
        self.root.bind("<Prior>", lambda e: self.nav(-1))
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("f", lambda e: self.togglefull()); self.root.bind("s", lambda e: self.togglefit())
        self.root.bind("<Configure>", lambda e: self.show(resize_only=True))
        self.full = False
        self.show()
        self.root.mainloop()

    def togglefull(self):
        self.full = not self.full; self.root.attributes("-fullscreen", self.full); self.show(resize_only=True)
    def togglefit(self):
        self.fit = not self.fit; self.show(resize_only=True)
    def nav(self, d):
        if not self.files: return
        self.i = (self.i + d) % len(self.files); self.show()

    def show(self, resize_only=False):
        if not self.files:
            self.root.title("이미지 없음"); return
        p = self.files[self.i]
        try:
            im = Image.open(p)
        except Exception as ex:
            self.lbl.config(text=f"열기 실패: {ex}", fg="white"); return
        ow, oh = im.size
        self.root.update_idletasks()
        cw = max(200, self.lbl.winfo_width()); ch = max(200, self.lbl.winfo_height())
        if self.fit:
            r = min(cw/ow, ch/oh)
            nw, nh = max(1, int(ow*r)), max(1, int(oh*r))
            disp = im.resize((nw, nh), Image.LANCZOS)
        else:
            disp = im
        self.tkimg = ImageTk.PhotoImage(disp)
        self.lbl.config(image=self.tkimg, text="")
        self.root.title(f"[{self.i+1}/{len(self.files)}]  {os.path.basename(p)}  ({ow}x{oh})  —  ←/→ 넘기기, F 전체화면, ESC 닫기")

if __name__ == "__main__":
    files = collect(sys.argv[1:])
    if not files:
        print("표시할 이미지 없음"); sys.exit(1)
    Viewer(files)
