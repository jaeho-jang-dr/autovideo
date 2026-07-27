# -*- coding: utf-8 -*-
"""W21 EN 4K판 = KO 4K판과 프레임 동일 → KO 4K의 비디오 스트림 재사용 + Emma(Azure) 오디오 + EN 자막.
   프레임 재렌더 없이 mux만(빠름)."""
import os, subprocess, json, re
import sys
sys.path.insert(0, os.path.join(os.getcwd(), "hangeul_birth_vowels"))
os.environ["TTS_ENGINE"] = "azure"; os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"; os.environ["ELEVEN_API_KEY"] = ""
import compile_stickman as cs

EP = "KO-W21"; PREFIX = "hangeul_w21_madam"; PDIR = "hangeul_birth_vowels"; FF = "ffmpeg"; AC = "eng"
LEAD, TAILPAD = 0.0, 0.45
cs.EP = EP; cs.OUT_PREFIX = PREFIX

def _sr(s): return re.sub(r"\s{2,}", " ", re.sub(r"\s*\[[^\]]*\]", "", s)).strip()
def _sb(s):
    s = s.replace("___을", "무엇을").replace("___를", "무엇을").replace("___", "something").replace("24시간", "이십사 시간")
    return re.sub(r"\s{2,}", " ", s).strip()

tl = json.load(open(os.path.join(PDIR, f"{PREFIX}_np_timeline.json"), encoding="utf-8"))
meta = tl["scenes"]
en_scenes = {s["seq"]: s for s in cs.load_scenes("en")}

# EN(Emma Azure) 오디오 트랙
segs = []
for m in meta:
    seq = m["seq"]
    en_a, en_dur, _ = cs.ensure_scene_audio(seq, _sb(_sr(en_scenes[seq]["script"])), "en")
    seg = os.path.join(cs.TTS_DIR, f"_enedit_{seq}.wav")
    subprocess.run([FF, "-y", "-i", en_a, "-af",
                    f"adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{m['dur']:.3f}", "-ar", "24000", "-ac", "1", seg],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    segs.append(seg)
lst = os.path.join(cs.TTS_DIR, "_enedit_list.txt")
open(lst, "w", encoding="utf-8").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))
track = os.path.join(PDIR, f"{PREFIX}_np_en.m4a")
subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "aac", "-b:a", "160k", track], check=True)
print("EN(Emma) 오디오 완료")

# KO 4K 비디오 재사용 + EN 오디오 + EN 자막
KO4K = os.path.join(PDIR, f"{PREFIX}_np_ko.mp4")
EN_SRT = os.path.join(PDIR, "w21pkg", f"{PREFIX}_np.en.srt")
OUT = os.path.join(PDIR, f"{PREFIX}_np_en.mp4")
subprocess.run([FF, "-y", "-i", KO4K, "-i", track, "-i", EN_SRT,
                "-map", "0:v", "-map", "1:a", "-map", "2:s",
                "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
                "-metadata:s:a:0", f"language={AC}", "-metadata:s:s:0", f"language={AC}",
                "-disposition:s:0", "default", OUT], check=True)
print("### EN_4K_DONE ###", OUT)
