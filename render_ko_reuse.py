# -*- coding: utf-8 -*-
"""W21 KO판 = EN판과 프레임 동일(노트박스 없음, 드로잉 sync는 원래 KO기준).
   EN final의 비디오 스트림 재사용 + 선희 KO 오디오(따옴표=선희 DB) + KO 자막(단어·짧은문장 로마자발음기호)만 붙임.
   → 프레임 재렌더 회피(빠름)."""
import sys, os, subprocess, json, re
sys.path.insert(0, os.path.join(os.getcwd(), "hangeul_birth_vowels"))
os.environ.setdefault("EDGE_ACTIVE_VOICE", "sunhi")
os.environ["ELEVEN_API_KEY"] = ""
import compile_stickman as cs

EP = "KO-W21"; PREFIX = "hangeul_w21_madam"; PDIR = "hangeul_birth_vowels"; FF = "ffmpeg"; AC = "kor"
LEAD, TAILPAD = 0.0, 0.45
cs.EP = EP; cs.OUT_PREFIX = PREFIX

def _sr(s): return re.sub(r"\s{2,}", " ", re.sub(r"\s*\[[^\]]*\]", "", s)).strip()
def _seg(s):
    s = re.sub(r"\s*\(([^()]*)\)", lambda m: "" if not re.search(r"[가-힣]", m.group(1)) else m.group(0), s)
    return re.sub(r"\s{2,}", " ", s).strip()
def _sb(s):
    s = s.replace("___을", "무엇을").replace("___를", "무엇을").replace("___", "something").replace("24시간", "이십사 시간")
    return re.sub(r"\s{2,}", " ", s).strip()

tl = json.load(open(os.path.join(PDIR, f"{PREFIX}_np_timeline.json"), encoding="utf-8"))
meta = tl["scenes"]                      # seq, dur, ko_dur, en_dur, ...
ko_scenes = cs.load_scenes("ko")
byseq = {s["seq"]: s for s in ko_scenes}

# KO 오디오(선희, 따옴표=DB클립) — ensure_scene_audio 캐시 사용
segs = []
for m in meta:
    seq = m["seq"]; sc = byseq[seq]
    ko_a, ko_dur, ko_js = cs.ensure_scene_audio(seq, _sb(_seg(_sr(sc["script"]))), "ko")
    seg = os.path.join(cs.TTS_DIR, f"_koedit_{seq}.wav")
    subprocess.run([FF, "-y", "-i", ko_a, "-af",
                    f"adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{m['dur']:.3f}", "-ar", "24000", "-ac", "1", seg],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    segs.append(seg)
lst = os.path.join(cs.TTS_DIR, "_koedit_list.txt")
open(lst, "w", encoding="utf-8").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))
track = os.path.join(PDIR, f"{PREFIX}_np_ko.m4a")
subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "aac", "-b:a", "160k", track], check=True)
print("KO 오디오 완료")

# KO 자막(발음기호 — 단어/짧은문장만) : compile_np와 동일 방식
def ts(t):
    h = int(t // 3600); mi = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{mi:02d}:{s:06.3f}".replace(".", ",")
entries = []; start = 0.0
for m in meta:
    sc = byseq[m["seq"]]; narr = m["ko_dur"]
    chunks = sc.get("chunks") or [sc["script"]]
    lens = [max(1, len(c)) for c in chunks]; tot = sum(lens); acc = LEAD
    for c, l in zip(chunks, lens):
        w = narr * l / tot; entries.append((start + acc, start + acc + w, c)); acc += w
    start += m["dur"]
KO_SRT = os.path.join(PDIR, f"{PREFIX}_np.ko.srt")
with open(KO_SRT, "w", encoding="utf-8") as f:
    idx = 1
    for t0, t1, txt in entries:
        if not txt.strip(): continue
        f.write(f"{idx}\n{ts(t0)} --> {ts(t1)}\n{txt.strip()}\n\n"); idx += 1
import add_pron_to_srt as _pron
lines = []
for ln in open(KO_SRT, encoding="utf-8"):
    t = ln.rstrip("\n")
    if re.match(r"^\d+$", t) or " --> " in t or not t.strip():
        lines.append(t)
    else:
        t = _pron.process_line(t)
        t = re.sub(r"(\[[a-z][a-z\-]*\])\s*\[([A-Z][A-Za-z]*)\]", r"\1 (\2)", t)
        t = re.sub(r"\s+\)", ")", re.sub(r"\(\s+", "(", t)); lines.append(t)
open(KO_SRT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
n = len(re.findall(r"\[[a-z\-]+\]", open(KO_SRT, encoding="utf-8").read()))
print(f"KO_SRT 완료 (로마자 {n}개)")

# EN final 비디오 재사용 + KO 오디오 + KO 자막
ENF = os.path.join(PDIR, f"{PREFIX}_np_en.mp4")
OUT = os.path.join(PDIR, f"{PREFIX}_np_ko.mp4")
subprocess.run([FF, "-y", "-i", ENF, "-i", track, "-i", KO_SRT,
                "-map", "0:v", "-map", "1:a", "-map", "2:s",
                "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
                "-metadata:s:a:0", f"language={AC}", "-metadata:s:s:0", f"language={AC}",
                "-disposition:s:0", "default", OUT], check=True)
print("### KO_DONE ###", OUT)
