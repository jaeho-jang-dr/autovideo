# -*- coding: utf-8 -*-
"""재사용 이미지 뷰어. Read 인라인이 안 보일 때 이걸로 띄운다.
사용:
  pythonw viewer.py 이미지1 [이미지2 ...]        # 네이티브 tkinter 창(로컬)
  pythonw viewer.py 폴더                          # 폴더 내 이미지 전부
  python  viewer.py --web [폴더/이미지 ...]        # ★브라우저 갤러리(CRD/원격에서 이걸로!)
                                                   #   그리드 + 더블클릭 확대. --port N 지정 가능(기본 8901)
네이티브 조작: ←/→ 또는 Space=다음, PgUp/PgDn, F=전체화면, ESC=닫기, S=원본크기.
★CRD/원격 데스크톱에서는 네이티브 창이 1장만 보이는 문제가 있으니 반드시 --web 모드를 쓴다."""
import sys, os, glob

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")

def collect(args):
    files = []
    for a in args:
        if os.path.isdir(a):
            for e in EXT: files += sorted(glob.glob(os.path.join(a, f"*{e}")))
        elif os.path.isfile(a):
            files.append(a)
    return files


def serve_web(files, port=8901):
    """브라우저 갤러리로 서빙(CRD/원격용). 그리드+더블클릭 확대. 투명PNG는 체크무늬 배경."""
    import http.server, socketserver, webbrowser
    files = [f.replace("\\", "/") for f in files]
    cards = "".join(
        f'<figure><img src="/img?p={i}" loading="lazy" ondblclick="z(this)">'
        f'<figcaption>{os.path.basename(f)}</figcaption></figure>' for i, f in enumerate(files)
    ) or "<i>이미지 없음</i>"
    page = ("<!doctype html><meta charset=utf-8><title>viewer</title><style>"
            "body{background:#1a1a1a;color:#eee;font-family:system-ui,'Malgun Gothic';margin:0;padding:16px}"
            "h1{font-size:16px}.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:10px}"
            "figure{margin:0;background:#2a2a2a;border-radius:8px;padding:7px;text-align:center}"
            "img{width:100%;height:185px;object-fit:contain;cursor:zoom-in;border-radius:5px;"
            "background:conic-gradient(#6a6a6a 90deg,#8a8a8a 0 180deg,#6a6a6a 0 270deg,#8a8a8a 0) 0 0/18px 18px}"
            "figcaption{font-size:12px;color:#bbb;margin-top:4px;word-break:break-all}"
            "#lb{position:fixed;inset:0;background:rgba(0,0,0,.93);display:none;align-items:center;justify-content:center;z-index:9;cursor:zoom-out}"
            "#lb img{max-width:95vw;max-height:95vh;height:auto;background:conic-gradient(#6a6a6a 90deg,#8a8a8a 0 180deg,#6a6a6a 0 270deg,#8a8a8a 0) 0 0/26px 26px}</style>"
            f"<h1>이미지 {len(files)}장 <span style='color:#888'>(더블클릭=확대)</span></h1>"
            f"<div class=g>{cards}</div><div id=lb onclick=\"this.style.display='none'\"><img></div>"
            "<script>function z(im){var l=document.getElementById('lb');l.querySelector('img').src=im.src;l.style.display='flex'}</script>")

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def do_GET(self):
            if self.path.startswith("/img?p="):
                try: p = files[int(self.path.split("=")[1])]
                except Exception: self.send_error(404); return
                if not os.path.exists(p): self.send_error(404); return
                ct = "image/png" if p.lower().endswith(".png") else "image/jpeg"
                self.send_response(200); self.send_header("Content-Type", ct); self.end_headers()
                with open(p, "rb") as fh: self.wfile.write(fh.read())
            else:
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
                self.wfile.write(page.encode("utf-8"))
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", port), H)
    print(f"[viewer --web] http://127.0.0.1:{port}/  ({len(files)}장)  — Ctrl+C로 종료")
    try: webbrowser.open(f"http://127.0.0.1:{port}/")
    except Exception: pass
    srv.serve_forever()

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
    args = sys.argv[1:]
    web = "--web" in args
    if web: args.remove("--web")
    port = 8901
    if "--port" in args:
        k = args.index("--port"); port = int(args[k + 1]); del args[k:k + 2]
    files = collect(args)
    if not files:
        print("표시할 이미지 없음"); sys.exit(1)
    if web:
        serve_web(files, port)
    else:
        import tkinter as tk
        from PIL import Image, ImageTk
        Viewer(files)
