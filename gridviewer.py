# -*- coding: utf-8 -*-
"""격자 뷰어(2분할) — 왼쪽에 작은 썸네일 전부(휠 스크롤), 오른쪽에 큰 미리보기 창이 함께.
사용:
  pythonw gridviewer.py 폴더 [폴더2 ...]
  pythonw gridviewer.py 이미지1 이미지2 ...
  pythonw gridviewer.py --glob "W22/clips/walk_frames/*.png"
  pythonw gridviewer.py --list 목록.txt
조작:
  썸네일 클릭/마우스오버 = 오른쪽 큰창에 표시 / 마우스휠 = 썸네일 스크롤
  ←/→ = 이전·다음 미리보기 / +,- = 썸네일 크기 / F = 전체화면 / ESC = 닫기
각 썸네일 아래에 파일명(프레임 번호)이 표시된다."""
import sys, os, glob
import tkinter as tk
from PIL import Image, ImageTk

EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")


def collect(args):
    files = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--glob":
            i += 1; files += sorted(glob.glob(args[i]))
        elif a == "--list":
            i += 1
            for ln in open(args[i], encoding="utf-8"):
                ln = ln.strip()
                if ln and os.path.isfile(ln):
                    files.append(ln)
        elif os.path.isdir(a):
            for e in EXT:
                files += sorted(glob.glob(os.path.join(a, f"*{e}")))
        elif os.path.isfile(a):
            files.append(a)
        i += 1
    seen = set(); out = []
    for f in files:
        if f not in seen:
            seen.add(f); out.append(f)
    return out


class GridViewer:
    def __init__(self, files, thumb=120):
        self.files = files
        self.thumb = max(60, min(360, int(thumb)))
        self.sel = 0
        self._thumbcache = {}
        self._btns = {}

        self.root = tk.Tk()
        self.root.title(f"격자 뷰어 — {len(files)}장  (클릭=오른쪽 큰창, +/- 크기, ←/→ 넘기기, F 전체화면, ESC)")
        self.root.configure(bg="#15171c")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{int(sw*0.94)}x{int(sh*0.92)}+{int(sw*0.03)}+{int(sh*0.03)}")

        # ── 왼쪽: 스크롤 썸네일 격자
        self.left = tk.Frame(self.root, bg="#15171c")
        self.left.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(self.left, bg="#15171c", highlightthickness=0, width=int(sw*0.5))
        self.vsb = tk.Scrollbar(self.left, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")
        self.inner = tk.Frame(self.canvas, bg="#15171c")
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._relayout)

        # ── 오른쪽: 큰 미리보기
        self.right = tk.Frame(self.root, bg="#0d0d0d", width=int(sw*0.44))
        self.right.pack(side="right", fill="both")
        self.right.pack_propagate(False)
        self.caption = tk.Label(self.right, text="", bg="#0d0d0d", fg="#ffd600",
                                font=("Malgun Gothic", 14, "bold"))
        self.caption.pack(side="top", fill="x", pady=6)
        self.preview = tk.Label(self.right, bg="#0d0d0d")
        self.preview.pack(side="top", fill="both", expand=True)

        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("f", lambda e: self._togglefull())
        self.root.bind("<F11>", lambda e: self._togglefull())
        self.root.bind("plus", lambda e: self._resize(20))
        self.root.bind("<KP_Add>", lambda e: self._resize(20))
        self.root.bind("minus", lambda e: self._resize(-20))
        self.root.bind("<KP_Subtract>", lambda e: self._resize(-20))
        self.root.bind("<Right>", lambda e: self._nav(1))
        self.root.bind("<Left>", lambda e: self._nav(-1))
        self.root.bind("<space>", lambda e: self._nav(1))
        self.full = False
        self._cols = 0
        self._build_grid()
        self.root.after(120, lambda: self._select(0))
        self.root.mainloop()

    def _thumb_img(self, path):
        key = (path, self.thumb)
        if key in self._thumbcache:
            return self._thumbcache[key]
        try:
            im = Image.open(path).convert("RGB")
        except Exception:
            im = Image.new("RGB", (self.thumb, self.thumb), (60, 30, 30))
        r = min(self.thumb / im.width, self.thumb / im.height)
        im = im.resize((max(1, int(im.width*r)), max(1, int(im.height*r))), Image.LANCZOS)
        canvas = Image.new("RGB", (self.thumb, self.thumb), (255, 255, 255))
        canvas.paste(im, ((self.thumb-im.width)//2, (self.thumb-im.height)//2))
        ph = ImageTk.PhotoImage(canvas)
        self._thumbcache[key] = ph
        return ph

    def _build_grid(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self._btns = {}
        self.root.update_idletasks()
        avail = max(self.canvas.winfo_width(), 400)
        cell = self.thumb + 16
        cols = max(1, avail // cell)
        self._cols = cols
        for idx, path in enumerate(self.files):
            r, c = divmod(idx, cols)
            cell_f = tk.Frame(self.inner, bg="#15171c")
            cell_f.grid(row=r, column=c, padx=4, pady=4)
            ph = self._thumb_img(path)
            btn = tk.Label(cell_f, image=ph, bg="#1b1e24", cursor="hand2", bd=2, relief="flat")
            btn.image = ph
            btn.pack()
            btn.bind("<Button-1>", lambda e, i=idx: self._select(i))
            btn.bind("<Enter>", lambda e, i=idx: self._select(i))
            name = os.path.basename(path).replace(".png", "")
            tk.Label(cell_f, text=name[:24], bg="#15171c", fg="#c8ccd4",
                     font=("Malgun Gothic", 9)).pack()
            self._btns[idx] = btn
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _relayout(self, e):
        avail = max(self.canvas.winfo_width(), 400)
        cols = max(1, avail // (self.thumb + 16))
        if cols != self._cols:
            self._build_grid()

    def _resize(self, d):
        self.thumb = max(60, min(360, self.thumb + d))
        self._thumbcache.clear()
        self._build_grid()

    def _select(self, i):
        if not self.files:
            return
        if i in self._btns and self.sel in self._btns:
            self._btns[self.sel].config(bg="#1b1e24", relief="flat")
        self.sel = i % len(self.files)
        if self.sel in self._btns:
            self._btns[self.sel].config(bg="#ffd600", relief="solid")
        self._render_preview()

    def _render_preview(self):
        path = self.files[self.sel]
        try:
            im = Image.open(path)
        except Exception as ex:
            self.caption.config(text=f"열기 실패: {ex}"); return
        ow, oh = im.size
        self.root.update_idletasks()
        cw = max(300, self.preview.winfo_width())
        ch = max(300, self.preview.winfo_height())
        r = min(cw/ow, ch/oh)
        disp = im.convert("RGB").resize((max(1, int(ow*r)), max(1, int(oh*r))), Image.LANCZOS)
        self._pimg = ImageTk.PhotoImage(disp)
        self.preview.config(image=self._pimg)
        self.caption.config(text=f"[{self.sel+1}/{len(self.files)}]  {os.path.basename(path)}  ({ow}x{oh})")

    def _nav(self, d):
        self._select((self.sel + d) % len(self.files))
        # keep selected thumb visible
        r, _ = divmod(self.sel, max(1, self._cols))
        frac = r / max(1, (len(self.files) // max(1, self._cols)))
        self.canvas.yview_moveto(max(0.0, frac - 0.1))

    def _togglefull(self):
        self.full = not self.full
        self.root.attributes("-fullscreen", self.full)
        self.root.after(80, self._render_preview)


if __name__ == "__main__":
    # --thumb N : 왼쪽 썸네일을 처음부터 크게 띄운다 (안 주면 120)
    argv, thumb = [], 120
    it = iter(range(len(sys.argv[1:])))
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--thumb" and i + 1 < len(args):
            thumb = int(args[i + 1]); i += 2; continue
        argv.append(args[i]); i += 1
    files = collect(argv)
    if not files:
        print("표시할 이미지 없음"); sys.exit(1)
    GridViewer(files, thumb)
