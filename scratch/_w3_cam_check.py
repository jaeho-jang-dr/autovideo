import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hangeul_birth_vowels.compile_stickman as C
from PIL import Image
C.EP = "KO-W03"
scenes = C.load_scenes("ko")
g = {s["seq"]: s for s in scenes}


def frame(seq, t, dur):
    s = g[seq]
    fr = C.compose(s, t=t, lang="ko", overlay=False)
    fr = C.apply_camera(fr, t, dur, s["cam"]).convert("RGBA")
    C.draw_caption(fr, s["cap"]); C.draw_subtitle(fr, s["script"])
    return fr.convert("RGB").resize((400, 225))


imgs = [frame(1, 0.3, 11),    # cam 'in' 시작 + z_wave
        frame(1, 2.0, 11),    # z_jump (번쩍)
        frame(1, 10.5, 11),   # cam 'in' 줌인된 끝
        frame(13, 0.4, 12)]   # z_sit_think (앉아 생각)
mon = Image.new("RGB", (800, 450), (30, 30, 30))
for i, f in enumerate(imgs):
    mon.paste(f, ((i % 2) * 400, (i // 2) * 225))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_w3_cam_check.png")
mon.save(out)
print("cam check ->", out, "| S1.cam=", g[1]["cam"], "S13.cam=", g[13]["cam"])
