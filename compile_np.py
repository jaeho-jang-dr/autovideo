# -*- coding: utf-8 -*-
"""한글강의 B규격(W2+) — 영/한 따로 영상(외국인 대상). 각 버전:
- 왼쪽 위 박스 = **그 버전 언어의 핵심 노트**(한국판=한글, 영어판=영어). 중앙 위 캡션 제거.
- 파라메트릭 글자 드로잉(scene_objects "write" 모션) compose에서 그대로 렌더.
- 각 영상에 **KO/EN 자막 둘 다**(선택형) + 그 버전 언어 오디오(선희/Emma).
- 씬 길이 = max(KO,EN)+여백 → 두 자막이 두 영상에 다 정렬.
사용: python compile_np.py KO-W02 hangeul_w2_stickman [4K|review] [ko,en|ko|en]
"""
import sys, os, re, subprocess
sys.path.insert(0, os.path.join(os.getcwd(), "hangeul_birth_vowels"))
import numpy as np
from PIL import ImageDraw
import compile_stickman as cs

if os.environ.get("USE_ELEVEN", "").strip().lower() not in ("1", "true", "yes"):
    os.environ["ELEVEN_API_KEY"] = ""   # 기본=ElevenLabs 끔(초안=edge/azure). USE_ELEVEN=1이면 유지(최종 Kanna/Alice).
os.environ.setdefault("EDGE_ACTIVE_VOICE", "sunhi")

EP = sys.argv[1] if len(sys.argv) > 1 else "KO-W02"
PREFIX = sys.argv[2] if len(sys.argv) > 2 else "hangeul_w2_stickman"
MODE = sys.argv[3] if len(sys.argv) > 3 else "4K"
LANGS = (sys.argv[4] if len(sys.argv) > 4 else "ko,en").split(",")
cs.EP = EP; cs.OUT_PREFIX = PREFIX
try: cs.PROJECT_NAME = PREFIX
except Exception: pass
PDIR = "hangeul_birth_vowels"
LEAD, TAIL = 0.0, 0.45   # 나레이션 앞 딜레이 0 (사장님 지시 2026-07-06)
RES = "1920:1080" if MODE == "review" else "3840:2160"
FF = cs._ff() if hasattr(cs, "_ff") else "ffmpeg"
def log(m): print(m, flush=True)

# ---------- 왼위 노트박스(그 버전 언어 단일) — 중앙캡션 대신 ----------
def draw_note_box(fr, cap):
    if not cap: return
    d = ImageDraw.Draw(fr)
    f = cs.get_font(cs.FONT_BD, 30)
    x, y = 26, 56
    rows = cs.wrap(d, cap, f, int(cs.W * 0.44))
    if not rows: return
    boxw = max(d.textlength(t, font=f) for t in rows)
    asc, desc = f.getmetrics()
    lh = asc + desc + 4                         # 실제 글자 높이 기준
    padx, pady = 12, 7                          # 글자 크기에 딱 맞는 작은 박스
    d.rounded_rectangle([x - padx, y - pady, x + boxw + padx, y + lh * len(rows) + pady - 4],
                        radius=12, fill=(255, 255, 255, 235))
    yy = y
    for t in rows:
        d.text((x, yy), t, font=f, fill=(28, 28, 40)); yy += lh

def srt_ts(t):
    h=int(t//3600); m=int((t%3600)//60); s=t%60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")
def build_srt(entries, path):
    with open(path, "w", encoding="utf-8") as f:
        for i,(t0,t1,txt) in enumerate([e for e in entries if e[2].strip()],1):
            f.write(f"{i}\n{srt_ts(t0)} --> {srt_ts(t1)}\n{txt.strip()}\n\n")

# ---------- 나레이션 + 공통 씬 길이 ----------
ko_scenes = cs.load_scenes("ko"); en_scenes = cs.load_scenes("en")
def _strip_rom(s):
    # ★나레이션에서만 로마자 발음기호 [..] 제거 — 외국인 나레이터가 발음기호를 읽지 않게(사장님 지시).
    #   자막(SRT)에는 그대로 남는다(별도 생성). 따옴표 한글·뜻(..)은 유지.
    s = re.sub(r"\s*\[[^\]]*\]", "", s)     # [bom], [han-ra-san] 등 제거
    return re.sub(r"\s{2,}", " ", s).strip()
meta=[]
for ko,en in zip(ko_scenes, en_scenes):
    ko_a, ko_dur, ko_js = cs.ensure_scene_audio(ko["seq"], _strip_rom(ko["script"]), "ko")
    en_a, en_dur, en_js = cs.ensure_scene_audio(en["seq"], _strip_rom(en["script"]), "en")
    dur = max(ko_dur, en_dur) + LEAD + TAIL
    meta.append(dict(ko=ko,en=en,ko_a=ko_a,en_a=en_a,ko_dur=ko_dur,en_dur=en_dur,ko_js=ko_js,en_js=en_js,dur=dur))
    log(f"  S{ko['seq']:>2}: KO={ko_dur:4.1f} EN={en_dur:4.1f} → {dur:4.1f}s")

# 공통 타임라인 srt(KO,EN)
def build_lang_srt(lang, out):
    entries=[]; start=0.0; scenes = ko_scenes if lang=="ko" else en_scenes
    for m,sc in zip(meta, scenes):
        narr = m["ko_dur"] if lang=="ko" else m["en_dur"]
        chunks = sc.get("chunks") or [sc["script"]]
        lens=[max(1,len(c)) for c in chunks]; tot=sum(lens); acc=LEAD
        for c,l in zip(chunks,lens):
            w=narr*l/tot; entries.append((start+acc, start+acc+w, c)); acc+=w
        start+=m["dur"]
    build_srt(entries, out)
KO_SRT=os.path.join(PDIR,f"{PREFIX}_np.ko.srt"); EN_SRT=os.path.join(PDIR,f"{PREFIX}_np.en.srt")
build_lang_srt("ko",KO_SRT); build_lang_srt("en",EN_SRT)

# ★★자막 표기 원칙(사장님 확정) — 렌더 때마다 자동 적용, 빼먹지 말 것:
#    자모  'ㅏ' [a]  /  단어 '오른쪽' [o-reun-jjok] (뜻)  /  문장 '어떻게 가요?' (뜻)
#    ⚠️SRT에만 넣는다(DB/나레이션에 넣으면 TTS가 로마자를 읽어버림) → 렌더 후처리로 고정.
#    ★한국인용 KO 자막에는 넣지 않는다(어색) — 외국어판(en/ja/zh/es)에만.
try:
    import add_pron_to_srt as _pron
    for _s in (EN_SRT,):
        _lines = []
        for _ln in open(_s, encoding="utf-8"):
            _t = _ln.rstrip("\n")
            if re.match(r"^\d+$", _t) or " --> " in _t or not _t.strip():
                _lines.append(_t)
            else:
                _t = _pron.process_line(_t)
                # ★고유명사 이중 대괄호 교정: '한라산' [han-ra-san] [Hallasan] → … (Hallasan)
                #   자막 원칙 = 단어 '한글' [로마자] (뜻). 뜻/영문명은 소괄호로.
                _t = re.sub(r"(\[[a-z][a-z\-]*\])\s*\[([A-Z][A-Za-z]*)\]", r"\1 (\2)", _t)
                _t = re.sub(r"\s+\)", ")", re.sub(r"\(\s+", "(", _t))   # "( " / " )" 정리
                _lines.append(_t)
        open(_s, "w", encoding="utf-8").write("\n".join(_lines) + "\n")
        _n = len(re.findall(r"\[[a-z\-]+\]", open(_s, encoding="utf-8").read()))
        log(f"[자막 발음기호] {os.path.basename(_s)}: [로마자] {_n}개")
except Exception as _e:
    log(f"[경고] 발음기호 후처리 실패 — 자막 원칙 위반 위험: {_e}")

# ★타임라인 저장 — patch_scene.py(부분 렌더)가 이 값을 그대로 써야 오디오가 안 어긋난다.
#   (TTS를 다시 생성하면 길이가 미세하게 달라지므로 렌더 시점의 길이를 고정 기록)
import json as _json
_tl = {"ep": EP, "prefix": PREFIX, "lead": LEAD, "tail": TAIL, "scenes": [
    {"seq": m["ko"]["seq"], "dur": m["dur"], "ko_dur": m["ko_dur"], "en_dur": m["en_dur"],
     "ko_a": m["ko_a"], "en_a": m["en_a"], "ko_js": [list(x) for x in m["ko_js"]]}
    for m in meta]}
open(os.path.join(PDIR, f"{PREFIX}_np_timeline.json"), "w", encoding="utf-8").write(
    _json.dumps(_tl, ensure_ascii=False))
log(f"[타임라인 저장] {PREFIX}_np_timeline.json ({len(meta)}씬) — 부분 렌더(patch_scene.py)용")

# ---------- 버전별 렌더(그 언어 박스 + 그 언어 오디오 + 양쪽자막 + 드로잉) ----------
from moviepy import VideoClip, concatenate_videoclips
def render_lang(lang):
    akey  = "ko_a"  if lang=="ko" else "en_a"
    ac    = "kor"   if lang=="ko" else "eng"
    log(f"[{lang}] 프레임(왼위 {lang} 박스 + KO드로잉 동일) …")
    clips=[]
    for m in meta:
        sc=m["ko"]                                        # ★ 시각·파라메트릭 드로잉은 항상 KO씬(두 판 완전 동일)
        dur=m["dur"]
        sc["sound_sched"]=[(j, LEAD+t0, LEAD+t1) for (j,t0,t1) in m["ko_js"]]   # ★ 드로잉 sync도 KO 고정
        cap=(m["ko"] if lang=="ko" else m["en"])["cap"]   # 박스만 버전 언어
        def mk(t, scene=sc, cam=sc.get("cam"), sdur=dur, cp=cap):
            fr=cs.compose(scene, t=t, lang="ko", overlay=False)    # ★ 항상 ko(드로잉 동일)
            fr=cs.apply_camera(fr, t, sdur, cam).convert("RGBA")
            draw_note_box(fr, cp)                         # ★ 왼위 그 언어 박스(중앙캡션 X)
            cs.draw_logo(fr); cs.draw_place(fr, scene.get("place_en"))
            return np.asarray(fr.convert("RGB"))
        clips.append(VideoClip(frame_function=mk, duration=dur))
    video=concatenate_videoclips(clips, method="compose")
    silent=os.path.join(PDIR,f"{PREFIX}_np_{lang}_silent.mp4")
    video.write_videofile(silent, fps=cs.FPS, codec="libx264", audio=False, threads=4, preset="medium", logger="bar")
    # 오디오 트랙(그 언어)
    segs=[]
    for i,m in enumerate(meta):
        seg=os.path.join(cs.TTS_DIR,f"_np2_{lang}_{i}.wav")
        subprocess.run([FF,"-y","-i",m[akey],"-af",
            f"adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{m['dur']:.3f}","-ar","24000","-ac","1",seg],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True); segs.append(seg)
    lst=os.path.join(cs.TTS_DIR,f"_np2_list_{lang}.txt")
    open(lst,"w",encoding="utf-8").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))
    track=os.path.join(PDIR,f"{PREFIX}_np_{lang}.m4a")
    subprocess.run([FF,"-y","-f","concat","-safe","0","-i",lst,"-c:a","aac","-b:a","160k",track],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    # mux: video + 그언어오디오 + KO/EN 자막 둘다
    final=os.path.join(PDIR,f"{PREFIX}_np_{lang}.mp4")
    ksd = "default" if lang=="ko" else "0"; esd = "default" if lang=="en" else "0"
    subprocess.run([FF,"-y","-i",silent,"-i",track,"-i",KO_SRT,"-i",EN_SRT,
        "-vf",f"scale={RES}:flags=lanczos",
        "-map","0:v","-map","1:a","-map","2:s","-map","3:s",
        "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","160k","-c:s","mov_text",
        "-metadata:s:a:0",f"language={ac}",
        "-metadata:s:s:0","language=kor","-metadata:s:s:1","language=eng",
        "-disposition:s:0",ksd,"-disposition:s:1",esd,
        final], check=True)
    log(f"### {lang.upper()}_DONE -> {final} (버전언어 박스 + 양쪽자막 + 드로잉) ###")

for lang in LANGS:
    render_lang(lang)
log("### NP_ALL_DONE ###")
