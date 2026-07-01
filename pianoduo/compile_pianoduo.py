# -*- coding: utf-8 -*-
"""pianoduo 컴파일 v2 — 25 클립 → 720p mp4 (2분30초). 워터마크 줌크롭 + 로고 + BGM.
연결: 청크 내부는 무이음 하드컷(last-frame transition), 청크 경계는 빠른 크로스페이드(0.25s).
청크: [1] [2-6] [7-11] [12-15] [16-18] [19-20] [21-24] [25]  (scenario.txt 와 동일)
완료 시 제작정보(최종본 경로/런타임/상태)를 content.db 에 기록(영상 바이너리는 저장 안 함)."""
import os, sys
import numpy as np, cv2
from moviepy import (VideoFileClip, AudioFileClip, CompositeVideoClip,
                     CompositeAudioClip, concatenate_videoclips)
import moviepy.video.fx as fx
from moviepy.video.fx import CrossFadeIn
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path: sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "channel"))
try:
    import content_db as cdb
except Exception as _e:
    cdb = None
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

PROJECT = "pianoduo"
PDIR = os.path.join(ROOT, "pianoduo")
LOGO = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
OUT = os.path.join(PDIR, "pianoduo.mp4")
DUR = [8,7,6,6,5,5,6,6,7,6,  6,5,7,5,6,5,6,7,5,7,  5,6,6,7,8]  # 씬별 길이(총 150초)
CHUNKS = [[1], [2,3,4,5,6], [7,8,9,10,11], [12,13,14,15],
          [16,17,18], [19,20], [21,22,23,24], [25]]
XF = 0.25  # 청크 경계 빠른 화면전환(크로스페이드) 길이(초)


def find_bgm():
    for ext in ("wav","mp3","m4a"):
        p = os.path.join(PDIR, f"pianoduo_bgm.{ext}")
        if os.path.exists(p): return p
    return None


def zoom_crop(clip):
    def eff(gf, t):
        f = gf(t); h, w = f.shape[:2]
        ch, cw = int(h*0.80), int(w*0.80)
        y1, x1 = (h-ch)//2, (w-cw)//2
        return cv2.resize(f[y1:y1+ch, x1:x1+cw], (w, h), interpolation=cv2.INTER_LANCZOS4)
    return clip.transform(eff)


def logo_overlay(clip, rgb, alpha):
    def eff(gf, t):
        f = gf(t).copy(); h, w = f.shape[:2]
        x0, y0 = w-45-20, h-45-20
        roi = f[y0:y0+45, x0:x0+45]
        f[y0:y0+45, x0:x0+45] = ((1-alpha)*roi + alpha*rgb).astype(np.uint8)
        return f
    return clip.transform(eff)


def load_clip(i, have_logo, logo_rgb, logo_a):
    cp = os.path.join(PDIR, f"scene_{i}.mp4")
    if not os.path.exists(cp):
        raise FileNotFoundError(cp)
    c = VideoFileClip(cp).without_audio()
    c = zoom_crop(c)
    if have_logo: c = logo_overlay(c, logo_rgb, logo_a)
    tgt = DUR[i-1]
    c = c.with_effects([fx.MultiplySpeed(c.duration/tgt)]).with_duration(tgt)
    c = c.resized(height=720) if hasattr(c, "resized") else c.resize(height=720)
    return c


def crossfade_concat(segs, d):
    """청크-슈퍼세그먼트들을 d초 크로스페이드로 이어 붙임(경계=빠른 화면전환)."""
    out = segs[0]
    for s in segs[1:]:
        s = s.with_effects([CrossFadeIn(d)]).with_start(out.duration - d)
        out = CompositeVideoClip([out, s])
    return out


def main():
    have_logo = os.path.exists(LOGO); logo_rgb = logo_a = None
    if have_logo:
        li = cv2.imread(LOGO, cv2.IMREAD_UNCHANGED)
        if li is not None and li.shape[2] == 4:
            lr = cv2.resize(cv2.cvtColor(li, cv2.COLOR_BGRA2RGBA), (45,45), interpolation=cv2.INTER_AREA)
            logo_rgb, logo_a = lr[:,:,:3], lr[:,:,3:4]/255.0
        else:
            have_logo = False

    # 1) 청크별 슈퍼세그먼트(내부 무이음 하드컷)
    supers = []
    for ci, grp in enumerate(CHUNKS):
        members = []
        for i in grp:
            members.append(load_clip(i, have_logo, logo_rgb, logo_a))
            print(f"  scene_{i} -> {DUR[i-1]}s (chunk {ci})")
        seg = members[0] if len(members) == 1 else concatenate_videoclips(members, method="chain")
        supers.append(seg)

    # 2) 청크 경계는 빠른 크로스페이드(0.25s)
    video = crossfade_concat(supers, XF)
    print(f"  청크 {len(supers)}개 · 경계 크로스페이드 {XF}s · 총 {video.duration:.1f}s")

    # 3) BGM — 피드백⑤⑥: 인사(씬1)는 무음, 첫 음은 손이 건반에 올라가는 씬2부터.
    #    음악은 마지막 연주(씬24) 끝에서 정확히 끝나고, 인사(씬25)는 완전 무음.
    #    BGM이 연주 구간보다 길면 '앞부분'을 잘라 후반 피날레를 씬24 끝에 정렬한다.
    bgm = find_bgm()
    if bgm:
        music_start = max(0.0, DUR[0] - XF)                    # 씬2 시작(손 시작) ≈ 7.75s
        scene25_start = video.duration - supers[-1].duration   # 인사(씬25) 시작 = 음악 끝
        window = scene25_start - music_start
        a = AudioFileClip(bgm)
        if a.duration > window:
            a = a.subclipped(a.duration - window, a.duration)  # 앞을 잘라 피날레를 끝에 맞춤
        else:
            from moviepy.audio.fx import AudioLoop
            a = a.with_effects([AudioLoop(duration=window)])
        a = a.with_effects([AudioFadeIn(0.4), AudioFadeOut(0.3)]).with_start(music_start)
        video = video.with_audio(CompositeAudioClip([a]))
        print(f"  BGM: {os.path.basename(bgm)} | 음악 {music_start:.2f}s~{scene25_start:.2f}s "
              f"(씬25 {video.duration-scene25_start:.1f}s 무음)")
    else:
        print("  [WARN] BGM 없음 — 무음으로 컴파일")

    threads = os.cpu_count() or 4
    print(f"렌더링 720p, {threads} threads, {video.duration:.1f}s ...")
    video.write_videofile(OUT, codec="libx264", audio_codec="aac", threads=threads,
                          preset="medium", bitrate="4000k", fps=24)
    print(f"[SUCCESS] {OUT}")

    # 4) DB 기록(최종본은 경로 링크만 — 바이너리 저장 안 함)
    if cdb:
        try:
            cdb.upsert_project(PROJECT, final_path=OUT, bgm_path=bgm,
                               runtime_sec=round(float(video.duration), 2),
                               status="compiled", local_dir=PDIR)
            print("  [DB] video_projects 갱신 완료")
        except Exception as e:
            print(f"  [WARN] DB 기록 실패: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
