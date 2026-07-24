# -*- coding: utf-8 -*-
"""render_parallel.py — ★4개 프로세스로 씬을 나눠 병렬 렌더 → 합쳐서 하나의 영상으로.

사용:
  python render_parallel.py <EP> <PREFIX> [ko|en] [워커수]
예:
  python render_parallel.py KO-W13 hangeul_w13_jieun ko 4

원리:
  렌더는 씬 단위로 독립적이고, 씬 길이는 TTS로 미리 확정된다 → 씬 구간을 4덩이로 쪼개
  각각 무음 mp4로 렌더한 뒤 concat, 오디오·자막을 얹으면 순차 렌더와 결과가 동일하다.

안전장치:
  ① ★TTS 캐시 워밍 — 나레이션을 **먼저 한 번에** 다 생성해 캐시에 넣는다.
     (안 하면 4개가 동시에 같은 tts_cache에 써서 세그먼트가 깨진다 — KO/EN 병렬 금지와 같은 이유)
  ② 타임라인·SRT는 부모가 한 번만 계산 → 조각들은 그 값만 읽는다(어긋남 방지)
"""
import sys, os, json, subprocess, tempfile, math, time

sys.path.insert(0, os.path.join(os.getcwd(), "hangeul_birth_vowels"))
EP     = sys.argv[1] if len(sys.argv) > 1 else "KO-W13"
PREFIX = sys.argv[2] if len(sys.argv) > 2 else "hangeul_w13_jieun"
LANG   = sys.argv[3] if len(sys.argv) > 3 else "ko"
NW     = int(sys.argv[4]) if len(sys.argv) > 4 else 4
PDIR   = "hangeul_birth_vowels"
FF     = "ffmpeg"
RES    = "1920:1080"
LEAD, TAIL = 0.35, 0.35

def log(m): print(m, flush=True)

# ---------- 워커 모드: 지정 구간만 무음 렌더 ----------
if os.environ.get("RP_WORKER"):
    import numpy as np
    import compile_stickman as cs
    import compile_np as _cnp                     # note box 등 그리기 재사용
    from moviepy import VideoClip, concatenate_videoclips
    cs.EP = EP
    lo, hi = int(os.environ["RP_LO"]), int(os.environ["RP_HI"])   # 1-based, 포함
    out = os.environ["RP_OUT"]
    tl = json.load(open(os.path.join(PDIR, f"{PREFIX}_np_timeline.json"), encoding="utf-8"))
    ko_scenes = cs.load_scenes("ko"); en_scenes = cs.load_scenes("en")
    clips = []
    for i in range(lo - 1, hi):
        s = tl["scenes"][i]
        sc = ko_scenes[i]                                   # 시각은 항상 KO씬(compile_np 규칙)
        dur = s["dur"]
        sc["sound_sched"] = [(j, LEAD + t0, LEAD + t1) for (j, t0, t1) in s["ko_js"]]
        cap = (ko_scenes[i] if LANG == "ko" else en_scenes[i])["cap"]
        def mk(t, scene=sc, cam=sc.get("cam"), sdur=dur, cp=cap):
            fr = cs.compose(scene, t=t, lang="ko", overlay=False)
            fr = cs.apply_camera(fr, t, sdur, cam).convert("RGBA")
            _cnp.draw_note_box(fr, cp)
            cs.draw_logo(fr); cs.draw_place(fr, scene.get("place_en"))
            return np.asarray(fr.convert("RGB"))
        clips.append(VideoClip(frame_function=mk, duration=dur))
    video = concatenate_videoclips(clips, method="compose")
    video.write_videofile(out, fps=cs.FPS, codec="libx264", audio=False,
                          threads=2, preset="medium", logger=None)
    sys.exit(0)

# ---------- 부모 모드 ----------
t0 = time.time()
log(f"=== 병렬 렌더 {EP} / {PREFIX} / {LANG} / 워커 {NW}개 ===")

# 1) ★TTS 캐시 워밍 + 타임라인·SRT 생성 (부모가 한 번만)
#    compile_np를 '타임라인만' 만들게 할 수는 없으니, 나레이션 생성 로직만 여기서 먼저 돌린다.
import compile_stickman as cs
cs.EP = EP
ko_scenes = cs.load_scenes("ko"); en_scenes = cs.load_scenes("en")
meta = []
log("[1/4] 나레이션 생성(캐시 워밍) — 병렬 렌더 중 TTS 레이스 방지")
for ko, en in zip(ko_scenes, en_scenes):
    ko_a, ko_dur, ko_js = cs.ensure_scene_audio(ko["seq"], ko["script"], "ko")
    en_a, en_dur, en_js = cs.ensure_scene_audio(en["seq"], en["script"], "en")
    dur = max(ko_dur, en_dur) + LEAD + TAIL
    meta.append(dict(ko=ko, en=en, ko_a=ko_a, en_a=en_a, ko_dur=ko_dur, en_dur=en_dur,
                     ko_js=ko_js, en_js=en_js, dur=dur))
N = len(meta)
TOTAL = sum(m["dur"] for m in meta)
log(f"   씬 {N}개 / 총 {TOTAL:.1f}s")

# 타임라인 저장(patch_scene / 워커가 읽음)
tl = {"ep": EP, "prefix": PREFIX, "lead": LEAD, "tail": TAIL, "scenes": [
    {"seq": m["ko"]["seq"], "dur": m["dur"], "ko_dur": m["ko_dur"], "en_dur": m["en_dur"],
     "ko_a": m["ko_a"], "en_a": m["en_a"], "ko_js": [list(x) for x in m["ko_js"]]} for m in meta]}
open(os.path.join(PDIR, f"{PREFIX}_np_timeline.json"), "w", encoding="utf-8").write(
    json.dumps(tl, ensure_ascii=False))

# SRT (compile_np와 동일 규칙)
def srt_ts(t):
    h = int(t // 3600); mnt = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{mnt:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"

def build_srt(entries, out):
    with open(out, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate([e for e in entries if e[2].strip()], 1):
            f.write(f"{i}\n{srt_ts(a)} --> {srt_ts(b)}\n{txt.strip()}\n\n")

def build_lang_srt(lang, out):
    entries = []; start = 0.0
    scenes = ko_scenes if lang == "ko" else en_scenes
    for m, sc in zip(meta, scenes):
        narr = m["ko_dur"] if lang == "ko" else m["en_dur"]
        chunks = sc.get("chunks") or [sc["script"]]
        lens = [max(1, len(c)) for c in chunks]; tot = sum(lens); acc = LEAD
        for c, l in zip(chunks, lens):
            w = narr * l / tot
            entries.append((start + acc, start + acc + w, c)); acc += w
        start += m["dur"]
    build_srt(entries, out)

KO_SRT = os.path.join(PDIR, f"{PREFIX}_np.ko.srt")
EN_SRT = os.path.join(PDIR, f"{PREFIX}_np.en.srt")
build_lang_srt("ko", KO_SRT); build_lang_srt("en", EN_SRT)
log("[2/4] 타임라인·자막 생성 완료")

# 2) 씬을 NW 덩이로 나눠 병렬 렌더
chunk = math.ceil(N / NW)
ranges = [(i * chunk + 1, min((i + 1) * chunk, N)) for i in range(NW) if i * chunk < N]
tmpd = tempfile.mkdtemp(prefix="rp_")
procs, parts = [], []
log(f"[3/4] 병렬 렌더 시작: {[(lo, hi) for lo, hi in ranges]}")
for k, (lo, hi) in enumerate(ranges):
    out = os.path.join(tmpd, f"part{k}.mp4")
    env = dict(os.environ, RP_WORKER="1", RP_LO=str(lo), RP_HI=str(hi), RP_OUT=out,
               PYTHONIOENCODING="utf-8")
    p = subprocess.Popen([sys.executable, os.path.abspath(__file__), EP, PREFIX, LANG],
                         env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    procs.append((p, lo, hi, out)); parts.append(out)
for p, lo, hi, out in procs:
    rc = p.wait()
    if rc != 0 or not os.path.exists(out):
        err = p.stderr.read().decode("utf-8", "ignore")[-500:]
        log(f"   ✗ S{lo}~S{hi} 실패\n{err}"); sys.exit(1)
    log(f"   ✓ S{lo}~S{hi} 완료")

# 3) 조각 합치기 → 무음 전체 영상
lst = os.path.join(tmpd, "list.txt")
open(lst, "w", encoding="utf-8").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
silent = os.path.join(PDIR, f"{PREFIX}_np_{LANG}_silent.mp4")
subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# 4) 오디오 트랙 + 자막 mux (compile_np와 동일)
akey = "ko_a" if LANG == "ko" else "en_a"
segs = []
for i, m in enumerate(meta):
    seg = os.path.join(cs.TTS_DIR, f"_rp_{LANG}_{i}.wav")
    subprocess.run([FF, "-y", "-i", m[akey], "-af",
                    f"adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{m['dur']:.3f}",
                    "-ar", "24000", "-ac", "1", seg],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    segs.append(seg)
alst = os.path.join(cs.TTS_DIR, f"_rp_list_{LANG}.txt")
open(alst, "w", encoding="utf-8").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))
track = os.path.join(PDIR, f"{PREFIX}_np_{LANG}.m4a")
subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", alst, "-c:a", "aac", "-b:a", "160k", track],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

final = os.path.join(PDIR, f"{PREFIX}_np_{LANG}.mp4")
ac = "kor" if LANG == "ko" else "eng"
ksd = "default" if LANG == "ko" else "0"
esd = "default" if LANG == "en" else "0"
subprocess.run([FF, "-y", "-i", silent, "-i", track, "-i", KO_SRT, "-i", EN_SRT,
                "-vf", f"scale={RES}:flags=lanczos",
                "-map", "0:v", "-map", "1:a", "-map", "2:s", "-map", "3:s",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "160k", "-c:s", "mov_text",
                "-metadata:s:a:0", f"language={ac}",
                "-metadata:s:s:0", "language=kor", "-metadata:s:s:1", "language=eng",
                "-disposition:s:0", ksd, "-disposition:s:1", esd,
                final], check=True)

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", final], capture_output=True, text=True).stdout.strip())
log(f"[4/4] ### {LANG.upper()}_DONE -> {final} ({dur:.1f}s, 계산 {TOTAL:.1f}s) ###")
log(f"소요: {(time.time()-t0)/60:.1f}분 (워커 {len(ranges)}개)")
