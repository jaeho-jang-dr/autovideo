# -*- coding: utf-8 -*-
"""patch_scene.py — ★부분 렌더: 고친 씬만 다시 렌더해서 기존 영상에 끼워넣는다(전체 재렌더 금지).

사용:
  python patch_scene.py <EP> <PREFIX> <씬번호,…> [ko|en]
예:
  python patch_scene.py KO-W12 hangeul_w12_injun 24        # S24만 다시 렌더해 교체
  python patch_scene.py KO-W12 hangeul_w12_injun 24,25,30  # 여러 씬

동작:
  1) DB에서 씬 타임라인(각 씬 길이)을 compile_np와 똑같이 계산 → 교체할 구간의 정확한 시작/끝 확보
  2) 지정 씬만 렌더(무음) + 그 씬 오디오 → 조각 mp4
  3) 기존 최종본을 [앞부분 | 새 조각 | 뒷부분] 으로 concat (스트림 복사 위주 → 1~2분)
  4) 자막(SRT)은 길이 불변이면 그대로 재사용, 바뀌면 경고

⚠️ 나레이션 문구를 바꿔 **씬 길이가 달라지면** 뒤 타임라인이 밀린다 → 이 도구가 감지해서
   "전체 렌더 필요"라고 알려준다(무리하게 붙이지 않는다).
"""
import sys, os, json, subprocess, tempfile
sys.path.insert(0, os.path.join(os.getcwd(), "hangeul_birth_vowels"))
# ★발음 클립은 기본 여성(선희) 폴더. 남성 캐릭터 강의는 호출 시 JAMO_DIR=jamo_m 환경변수로 오버라이드.
#   (예전 기본값이 jamo_m 이라 여성 강의 부분렌더에서 남자 목소리가 들어갔다 — W15에서 발견)
os.environ.setdefault("JAMO_DIR", os.path.join(os.getcwd(), "web", "public", "audio", "jamo"))
import numpy as np
import compile_stickman as cs
from moviepy import VideoClip

EP     = sys.argv[1]
PREFIX = sys.argv[2]
SEQS   = sorted({int(x) for x in sys.argv[3].split(",") if x.strip()})
LANG   = sys.argv[4] if len(sys.argv) > 4 else "ko"
FF     = "ffmpeg"
PDIR   = "hangeul_birth_vowels"
RES    = "1920:1080"
LEAD, TAIL = 0.0, 0.45           # ★compile_np와 동일해야 함(2026-07-06 이후 0.0/0.45). 예전 0.35/0.35는 밀림 버그
cs.EP  = EP

def log(m): print(m, flush=True)

# ★compile_np 의 note box 를 그대로 복사(★★import compile_np 금지 —
#   import 하면 compile_np 최상위의 전체 렌더 코드가 실행돼 76씬을 통째로 렌더한다.
#   이게 patch_scene 이 여태 부분렌더가 안 되고 전체를 그리던 근본 버그였다. W15에서 발견).
from PIL import ImageDraw
def draw_note_box(fr, cap):
    if not cap: return
    d = ImageDraw.Draw(fr)
    f = cs.get_font(cs.FONT_BD, 30)
    x, y = 26, 56
    rows = cs.wrap(d, cap, f, int(cs.W * 0.44))
    if not rows: return
    boxw = max(d.textlength(t, font=f) for t in rows)
    asc, desc = f.getmetrics()
    lh = asc + desc + 4
    padx, pady = 12, 7
    d.rounded_rectangle([x - padx, y - pady, x + boxw + padx, y + lh * len(rows) + pady - 4],
                        radius=12, fill=(255, 255, 255, 235))
    yy = y
    for t in rows:
        d.text((x, yy), t, font=f, fill=(28, 28, 40)); yy += lh

# ---------- 1) 타임라인 (★렌더 때 저장해 둔 타임라인을 그대로 사용) ----------
# compile_np 가 렌더하며 <PREFIX>_np_timeline.json 에 씬별 길이·오디오 경로를 저장한다.
# TTS를 다시 생성하면 길이가 미세하게 달라져 오디오가 어긋나므로, 부분 렌더는 반드시 저장본을 쓴다.
TL = os.path.join(PDIR, f"{PREFIX}_np_timeline.json")
ko_scenes = cs.load_scenes("ko"); en_scenes = cs.load_scenes("en")

if os.path.exists(TL):
    saved = json.load(open(TL, encoding="utf-8"))
    meta = []
    for i, (ko, en) in enumerate(zip(ko_scenes, en_scenes)):
        s = saved["scenes"][i]
        meta.append(dict(ko=ko, en=en, ko_a=s["ko_a"], en_a=s["en_a"],
                         ko_dur=s["ko_dur"], en_dur=s["en_dur"],
                         ko_js=[tuple(x) for x in s["ko_js"]], dur=s["dur"]))
    log(f"타임라인 로드: {TL} ({len(meta)}씬)")
else:
    log(f"⚠️ 타임라인 파일이 없습니다: {TL}")
    log("   (이 영상은 타임라인 저장 기능 추가 전에 렌더된 것)")
    log("   → 한 번만 전체 렌더하면 이후부터 부분 렌더가 가능합니다:")
    log(f"   python compile_np.py {EP} {PREFIX} review {LANG}")
    sys.exit(2)

starts, t = [], 0.0
for m in meta:
    starts.append(t); t += m["dur"]
TOTAL = t

FINAL = os.path.join(PDIR, f"{PREFIX}_np_{LANG}.mp4")
if not os.path.exists(FINAL):
    log(f"기존 영상 없음: {FINAL} → 전체 렌더가 먼저 필요합니다."); sys.exit(1)

cur = float(subprocess.run([("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", FINAL], capture_output=True, text=True).stdout.strip())
# ★각 조각은 timeline dur로 렌더하고 오디오도 atrim=0:dur 로 고정하므로 미세 차이는 안전.
#   2초 넘게 벌어지면(나레이션 대폭 변경) 그때만 전체 렌더로.
if abs(cur - TOTAL) > 2.0:
    log(f"⚠️ 저장 타임라인({TOTAL:.1f}s)과 기존 영상({cur:.1f}s)이 2초 이상 다릅니다.")
    log("   나레이션이 크게 바뀐 수정입니다 → 부분 교체 불가, **전체 렌더**로 가세요:")
    log(f"   python compile_np.py {EP} {PREFIX} review {LANG}")
    sys.exit(2)

# ---------- 2) 지정 씬만 렌더 ----------
tmpd = tempfile.mkdtemp(prefix="patch_")
parts = []          # (start, end, 조각파일)  — 교체 구간
for q in SEQS:
    i = q - 1
    if i < 0 or i >= len(meta):
        log(f"씬 {q} 없음 — 건너뜀"); continue
    m = meta[i]
    sc = m["ko"]                                          # 시각은 항상 KO씬(compile_np 규칙)
    dur = m["dur"]
    sc["sound_sched"] = [(j, LEAD + t0, LEAD + t1) for (j, t0, t1) in m["ko_js"]]
    cap = (m["ko"] if LANG == "ko" else m["en"])["cap"]

    # ★그 씬 오디오를 '지금' 다시 생성한다(발음 클립·나레이션 변경 반영).
    #   나레이션 텍스트가 그대로면 길이 동일 → 타임라인 안 밀림. 발음기호는 나레이션에서 제거.
    import re as _re_ps
    def _strip_rom_ps(s):
        return _re_ps.sub(r"\s{2,}", " ", _re_ps.sub(r"\s*\[[^\]]*\]", "", s)).strip()
    _sc_lang = m["ko"] if LANG == "ko" else m["en"]
    _new_a, _new_dur, _new_js = cs.ensure_scene_audio(q, _strip_rom_ps(_sc_lang["script"]), LANG)
    # 오디오는 아래 ffmpeg에서 apad,atrim=0:dur 로 씬 길이(dur)에 고정 → 타임라인 안 밀림.
    m["ko_a" if LANG == "ko" else "en_a"] = _new_a   # 새 오디오로 교체
    if LANG == "ko":                                  # 드로잉 sync 재계산(선희 클립 시각)
        sc["sound_sched"] = [(j, LEAD + t0, LEAD + t1) for (j, t0, t1) in _new_js]

    def mk(tt, scene=sc, cam=sc.get("cam"), sdur=dur, cp=cap):
        fr = cs.compose(scene, t=tt, lang="ko", overlay=False)
        fr = cs.apply_camera(fr, tt, sdur, cam).convert("RGBA")
        draw_note_box(fr, cp)
        cs.draw_logo(fr); cs.draw_place(fr, scene.get("place_en"))
        return np.asarray(fr.convert("RGB"))

    log(f"[S{q}] 렌더 ({dur:.1f}s) …")
    silent = os.path.join(tmpd, f"s{q}_silent.mp4")
    VideoClip(frame_function=mk, duration=dur).write_videofile(
        silent, fps=cs.FPS, codec="libx264", audio=False, threads=4, preset="medium", logger=None)

    # 그 씬 오디오
    akey = "ko_a" if LANG == "ko" else "en_a"
    seg = os.path.join(tmpd, f"s{q}.m4a")
    subprocess.run([FF, "-y", "-i", m[akey], "-af",
                    f"adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{dur:.3f}",
                    "-c:a", "aac", "-b:a", "160k", seg],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    piece = os.path.join(tmpd, f"s{q}.mp4")
    subprocess.run([FF, "-y", "-i", silent, "-i", seg, "-vf", f"scale={RES}:flags=lanczos",
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                    "-r", str(cs.FPS), piece],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    parts.append((starts[i], starts[i] + dur, piece))
    log(f"[S{q}] 조각 완성 → {starts[i]:.1f}~{starts[i]+dur:.1f}s")

if not parts:
    log("교체할 씬이 없습니다."); sys.exit(1)

# ---------- 3) 원본에서 남길 구간 잘라 concat ----------
parts.sort()
segments = []   # 순서대로 이어붙일 파일들
cursor = 0.0
n = 0
for (s, e, piece) in parts:
    if s - cursor > 0.05:                                  # 앞 구간(원본 유지)
        keep = os.path.join(tmpd, f"keep{n}.mp4"); n += 1
        subprocess.run([FF, "-y", "-ss", f"{cursor:.3f}", "-to", f"{s:.3f}", "-i", FINAL,
                        "-map", "0:v", "-map", "0:a", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                        "-r", str(cs.FPS), keep],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        segments.append(keep)
    segments.append(piece)                                 # 새 조각
    cursor = e
if TOTAL - cursor > 0.05:                                  # 뒤 구간(원본 유지)
    keep = os.path.join(tmpd, f"keep{n}.mp4")
    subprocess.run([FF, "-y", "-ss", f"{cursor:.3f}", "-i", FINAL,
                    "-map", "0:v", "-map", "0:a", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                    "-r", str(cs.FPS), keep],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    segments.append(keep)

lst = os.path.join(tmpd, "concat.txt")
open(lst, "w", encoding="utf-8").write("".join(f"file '{os.path.abspath(p)}'\n" for p in segments))
merged = os.path.join(tmpd, "merged.mp4")
subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", merged],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# ---------- 4) 자막 다시 얹기(타임라인 불변이므로 기존 SRT 그대로) ----------
KO_SRT = os.path.join(PDIR, f"{PREFIX}_np.ko.srt")
EN_SRT = os.path.join(PDIR, f"{PREFIX}_np.en.srt")
ac  = "kor" if LANG == "ko" else "eng"
ksd = "default" if LANG == "ko" else "0"
esd = "default" if LANG == "en" else "0"
out = FINAL
subprocess.run([FF, "-y", "-i", merged, "-i", KO_SRT, "-i", EN_SRT,
                "-map", "0:v", "-map", "0:a", "-map", "1:s", "-map", "2:s",
                "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
                "-metadata:s:a:0", f"language={ac}",
                "-metadata:s:s:0", "language=kor", "-metadata:s:s:1", "language=eng",
                "-disposition:s:0", ksd, "-disposition:s:1", esd,
                out + ".tmp.mp4"], check=True)
os.replace(out + ".tmp.mp4", out)

dur2 = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip())
log(f"### PATCH_DONE -> {out}  (씬 {SEQS} 교체, 길이 {dur2:.1f}s / 기존 {cur:.1f}s) ###")
log("   자막은 타임라인 불변이라 기존 SRT 그대로 유지됨.")
