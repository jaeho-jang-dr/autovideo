# -*- coding: utf-8 -*-
"""격자 뷰어 — 전체를 썸네일 격자로 보고, 클릭(또는 화살표)하면 확대해서 한 장씩 본다.
사용:
  pythonw gridviewer.py 폴더 [폴더2 ...]
  pythonw gridviewer.py 이미지1 이미지2 ...
  pythonw gridviewer.py --glob "home_vocab/w15/jieun_*.png"
조작:
  격자화면: 썸네일 클릭 = 확대 / 마우스휠 = 스크롤 / +,- = 썸네일 크기 / F = 전체화면 / ESC = 닫기
  확대화면: ←/→/Space = 이전·다음 / Enter·Backspace = 격자로 / F = 전체화면 / ESC = 격자로
파일명(라벨)이 각 썸네일 아래 표시된다."""
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
            i += 1
            files += sorted(glob.glob(args[i]))
        elif a == "--list":          # 파일 경로 목록이 담긴 텍스트 파일(한 줄에 하나)
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
    # 중복 제거(순서 유지)
    seen = set(); out = []
    for f in files:
        if f not in seen:
            seen.add(f); out.append(f)
    return out


class GridViewer:
    def __init__(self, files):
        self.files = files
        self.thumb = 180          # 썸네일 한 변
        self.mode = "grid"        # grid | zoom
        self.zoom_i = 0
        self._thumbcache = {}

        self.root = tk.Tk()
        self.root.title(f"격자 뷰어 — {len(files)}장  (클릭=확대, +/- 크기, F 전체화면, ESC 닫기)")
        self.root.configure(bg="#15171c")
        self.root.attributes("-topmost", True)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{int(sw*0.9)}x{int(sh*0.9)}+{int(sw*0.05)}+{int(sh*0.04)}")

        # ── 격자용 스크롤 캔버스
        self.canvas = tk.Canvas(self.root, bg="#15171c", highlightthickness=0)
        self.vsb = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.inner = tk.Frame(self.canvas, bg="#15171c")
        self.canvas_win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        # ── 확대용 라벨
        self.zoomlbl = tk.Label(self.root, bg="#0d0d0d")

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._relayout)
        self._bind_wheel(self.canvas)

        self.root.bind("<Escape>", self._esc)
        self.root.bind("f", lambda e: self._togglefull())
        self.root.bind("<F11>", lambda e: self._togglefull())
        self.root.bind("plus", lambda e: self._resize_thumb(20))
        self.root.bind("<KP_Add>", lambda e: self._resize_thumb(20))
        self.root.bind("minus", lambda e: self._resize_thumb(-20))
        self.root.bind("<KP_Subtract>", lambda e: self._resize_thumb(-20))
        self.root.bind("<Right>", lambda e: self._znav(1))
        self.root.bind("<Left>", lambda e: self._znav(-1))
        self.root.bind("<space>", lambda e: self._znav(1))
        self.root.bind("<Return>", lambda e: self._to_grid())
        self.root.bind("<BackSpace>", lambda e: self._to_grid())
        self.full = False
        self._cols = 0
        self._build_grid()
        self.root.mainloop()

    def _bind_wheel(self, w):
        w.bind_all("<MouseWheel>", self._on_wheel)
        w.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        w.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_wheel(self, e):
        if self.mode == "grid":
            self.canvas.yview_scroll(-1 if e.delta > 0 else 1, "units")

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
            btn = tk.Label(cell_f, image=ph, bg="#1b1e24", cursor="hand2", bd=1, relief="flat")
            btn.image = ph
            btn.pack()
            btn.bind("<Button-1>", lambda e, i=idx: self._open_zoom(i))
            name = os.path.basename(path).replace("jieun_", "").replace(".png", "")
            tk.Label(cell_f, text=name[:24], bg="#15171c", fg="#c8ccd4",
                     font=("Malgun Gothic", 9)).pack()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _relayout(self, e):
        if self.mode == "grid":
            avail = max(self.canvas.winfo_width(), 400)
            cell = self.thumb + 16
            cols = max(1, avail // cell)
            if cols != self._cols:
                self._build_grid()

    def _resize_thumb(self, d):
        self.thumb = max(80, min(360, self.thumb + d))
        self._thumbcache.clear()
        if self.mode == "grid":
            self._build_grid()

    def _show_grid_widgets(self):
        self.zoomlbl.pack_forget()
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")

    def _open_zoom(self, i):
        self.zoom_i = i
        self.mode = "zoom"
        self.canvas.pack_forget(); self.vsb.pack_forget()
        self.zoomlbl.pack(fill="both", expand=True)
        self._render_zoom()

    def _render_zoom(self):
        path = self.files[self.zoom_i]
        try:
            im = Image.open(path)
        except Exception as ex:
            self.zoomlbl.config(text=f"열기 실패: {ex}", fg="white"); return
        ow, oh = im.size
        self.root.update_idletasks()
        cw = max(300, self.zoomlbl.winfo_width()); ch = max(300, self.zoomlbl.winfo_height())
        r = min(cw/ow, ch/oh)
        disp = im.resize((max(1, int(ow*r)), max(1, int(oh*r))), Image.LANCZOS)
        self._zoomimg = ImageTk.PhotoImage(disp)
        self.zoomlbl.config(image=self._zoomimg, text="")
        name = os.path.basename(path)
        self.root.title(f"[{self.zoom_i+1}/{len(self.files)}]  {name}  ({ow}x{oh})  —  ←/→ 넘기기, Enter 격자로, ESC 격자로")

    def _znav(self, d):
        if self.mode != "zoom":
            return
        self.zoom_i = (self.zoom_i + d) % len(self.files)
        self._render_zoom()

    def _to_grid(self):
        if self.mode == "zoom":
            self.mode = "grid"
            self._show_grid_widgets()
            self._build_grid()
            self.root.title(f"격자 뷰어 — {len(self.files)}장  (클릭=확대, +/- 크기, F 전체화면, ESC 닫기)")

    def _esc(self, e):
        if self.mode == "zoom":
            self._to_grid()
        else:
            self.root.destroy()

    def _togglefull(self):
        self.full = not self.full
        self.root.attributes("-fullscreen", self.full)
        if self.mode == "zoom":
            self._render_zoom()


if __name__ == "__main__":
    files = collect(sys.argv[1:])
    if not files:
        print("표시할 이미지 없음"); sys.exit(1)
    GridViewer(files)
