import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hangeul_birth_vowels.compile_stickman as C
from PIL import Image
C.EP = "KO-W03"
scenes = C.load_scenes("ko")
sc = next(s for s in scenes if s["seq"] == 3)        # z_explain gesture + airpuff
ts = [0.4, 1.9, 3.6, 5.3]                            # HOLD=1.7 → 다른 제스처들
frames = [C.compose(sc, t=t, lang="ko").resize((420, 236)) for t in ts]
mon = Image.new("RGB", (420 * 2, 236 * 2), (30, 30, 30))
for i, f in enumerate(frames):
    mon.paste(f, ((i % 2) * 420, (i // 2) * 236))
mon.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_w3_gesture_check.png"))
print("frames:", ts, "-> scratch/_w3_gesture_check.png")
