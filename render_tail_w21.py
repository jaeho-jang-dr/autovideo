# -*- coding: utf-8 -*-
"""W21 EN판: S18~26만 새 나레이션으로 렌더 → 기존 S1~17 뒤에 이어붙임(전체 재렌더 회피).
   앞부분(S1~17) 길이 불변 → 기존 final을 S17끝까지 트림한 head + 새로 렌더한 tail concat + full SRT 재mux."""
import sys, os, subprocess, json, re
sys.path.insert(0, os.path.join(os.getcwd(), "hangeul_birth_vowels"))
os.environ.setdefault("EDGE_ACTIVE_VOICE", "sunhi")
os.environ["ELEVEN_API_KEY"] = ""
import numpy as np
import compile_stickman as cs
from moviepy import VideoClip, concatenate_videoclips

EP = "KO-W21"; PREFIX = "hangeul_w21_madam"; PDIR = "hangeul_birth_vowels"; LANG = "en"; AC = "eng"
TAIL = set(range(18, 27)); LEAD, TAILPAD = 0.0, 0.45; RES = "1920:1080"; FF = "ffmpeg"
cs.EP = EP; cs.OUT_PREFIX = PREFIX

ko_scenes = cs.load_scenes("ko"); en_scenes = cs.load_scenes("en")

def _sr(s): return re.sub(r"\s{2,}", " ", re.sub(r"\s*\[[^\]]*\]", "", s)).strip()
def _seg(s):
    s = re.sub(r"\s*\(([^()]*)\)", lambda m: "" if not re.search(r"[가-힣]", m.group(1)) else m.group(0), s)
    return re.sub(r"\s{2,}", " ", s).strip()
def _sb(s):
    s = s.replace("___을", "무엇을").replace("___를", "무엇을").replace("___", "something").replace("24시간", "이십사 시간")
    return re.sub(r"\s{2,}", " ", s).strip()

saved = json.load(open(os.path.join(PDIR, f"{PREFIX}_np_timeline.json"), encoding="utf-8"))
meta = []
for i, (ko, en) in enumerate(zip(ko_scenes, en_scenes)):
    seq = ko["seq"]
    if seq in TAIL:
        ko_a, ko_d, ko_js = cs.ensure_scene_audio(seq, _sb(_seg(_sr(ko["script"]))), "ko")
        en_a, en_d, en_js = cs.ensure_scene_audio(seq, _sb(_sr(en["script"])), "en")
        dur = max(ko_d, en_d) + LEAD + TAILPAD
        meta.append(dict(seq=seq, ko=ko, en=en, ko_a=ko_a, en_a=en_a, ko_dur=ko_d, en_dur=en_d, ko_js=ko_js, dur=dur))
        print(f"  S{seq}: KO={ko_d:.1f} EN={en_d:.1f} -> {dur:.1f}s (신규)")
    else:
        s = saved["scenes"][i]
        meta.append(dict(seq=seq, ko=ko, en=en, ko_a=s["ko_a"], en_a=s["en_a"],
                         ko_dur=s["ko_dur"], en_dur=s["en_dur"], ko_js=[tuple(x) for x in s["ko_js"]], dur=s["dur"]))

# 새 타임라인 저장(다음 부분렌더 대비)
open(os.path.join(PDIR, f"{PREFIX}_np_timeline.json"), "w", encoding="utf-8").write(json.dumps(
    {"ep": EP, "prefix": PREFIX, "lead": LEAD, "tail": TAILPAD, "scenes": [
        {"seq": m["seq"], "dur": m["dur"], "ko_dur": m["ko_dur"], "en_dur": m["en_dur"],
         "ko_a": m["ko_a"], "en_a": m["en_a"], "ko_js": [list(x) for x in m["ko_js"]]} for m in meta]}, ensure_ascii=False))

# full EN SRT 재생성 + 발음기호
def ts(t):
    h = int(t // 3600); mi = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{mi:02d}:{s:06.3f}".replace(".", ",")
entries = []; start = 0.0
for m in meta:
    narr = m["en_dur"]; chunks = m["en"].get("chunks") or [m["en"]["script"]]
    lens = [max(1, len(c)) for c in chunks]; tot = sum(lens); acc = LEAD
    for c, l in zip(chunks, lens):
        w = narr * l / tot; entries.append((start + acc, start + acc + w, c)); acc += w
    start += m["dur"]
EN_SRT = os.path.join(PDIR, f"{PREFIX}_np.en.srt")
with open(EN_SRT, "w", encoding="utf-8") as f:
    idx = 1
    for t0, t1, txt in entries:
        if not txt.strip(): continue
        f.write(f"{idx}\n{ts(t0)} --> {ts(t1)}\n{txt.strip()}\n\n"); idx += 1
import add_pron_to_srt as _pron
lines = []
for ln in open(EN_SRT, encoding="utf-8"):
    t = ln.rstrip("\n")
    if re.match(r"^\d+$", t) or " --> " in t or not t.strip():
        lines.append(t)
    else:
        t = _pron.process_line(t)
        t = re.sub(r"(\[[a-z][a-z\-]*\])\s*\[([A-Z][A-Za-z]*)\]", r"\1 (\2)", t)
        t = re.sub(r"\s+\)", ")", re.sub(r"\(\s+", "(", t)); lines.append(t)
open(EN_SRT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("SRT 재생성 완료")

# head 트림 (기존 EN final을 S17끝까지)
head_end = sum(m["dur"] for m in meta if m["seq"] <= 17)
FINAL = os.path.join(PDIR, f"{PREFIX}_np_en.mp4")
head = os.path.join(PDIR, "_tail_head.mp4")
subprocess.run([FF, "-y", "-i", FINAL, "-t", f"{head_end:.3f}", "-map", "0:v", "-map", "0:a", "-c", "copy", head], check=True)
print(f"head 트림 {head_end:.1f}s")

# tail 렌더 (S18~26)
clips = []
for m in meta:
    if m["seq"] not in TAIL: continue
    sc = m["ko"]; dur = m["dur"]
    sc["sound_sched"] = [(j, LEAD + t0, LEAD + t1) for (j, t0, t1) in m["ko_js"]]
    def mk(t, scene=sc, cam=sc.get("cam"), sdur=dur):
        fr = cs.compose(scene, t=t, lang="ko", overlay=False)
        fr = cs.apply_camera(fr, t, sdur, cam).convert("RGBA")
        cs.draw_logo(fr); cs.draw_place(fr, scene.get("place_en"))
        return np.asarray(fr.convert("RGB"))
    clips.append(VideoClip(frame_function=mk, duration=dur))
tsilent = os.path.join(PDIR, "_tail_silent.mp4")
concatenate_videoclips(clips, method="compose").write_videofile(
    tsilent, fps=cs.FPS, codec="libx264", audio=False, threads=4, preset="medium", logger="bar")

# tail 오디오(en)
segs = []
for m in meta:
    if m["seq"] not in TAIL: continue
    seg = os.path.join(cs.TTS_DIR, f"_tail_en_{m['seq']}.wav")
    subprocess.run([FF, "-y", "-i", m["en_a"], "-af",
                    f"adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{m['dur']:.3f}", "-ar", "24000", "-ac", "1", seg],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); segs.append(seg)
tlst = os.path.join(cs.TTS_DIR, "_tail_list.txt")
open(tlst, "w", encoding="utf-8").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))
ttrack = os.path.join(PDIR, "_tail.m4a")
subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", tlst, "-c:a", "aac", "-b:a", "160k", ttrack], check=True)
tail = os.path.join(PDIR, "_tail_tail.mp4")
subprocess.run([FF, "-y", "-i", tsilent, "-i", ttrack, "-vf", f"scale={RES}:flags=lanczos",
                "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", tail], check=True)

# concat head+tail → mux full en srt
clst = os.path.join(PDIR, "_tail_concat.txt")
open(clst, "w", encoding="utf-8").write(f"file '{os.path.abspath(head)}'\nfile '{os.path.abspath(tail)}'\n")
combined = os.path.join(PDIR, "_tail_combined.mp4")
subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", clst, "-c", "copy", combined], check=True)
subprocess.run([FF, "-y", "-i", combined, "-i", EN_SRT, "-map", "0:v", "-map", "0:a", "-map", "1:s",
                "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
                "-metadata:s:a:0", f"language={AC}", "-metadata:s:s:0", f"language={AC}",
                "-disposition:s:0", "default", FINAL], check=True)
for f in [head, tsilent, ttrack, tail, combined]:
    try: os.remove(f)
    except Exception: pass
print("### TAIL_DONE ###", FINAL)
