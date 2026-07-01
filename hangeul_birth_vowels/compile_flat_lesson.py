#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
compile_flat_lesson.py — 플랫 캔버스 레슨 렌더러 (Flow 배경 + 파라메트릭 스틱맨 + 글자 오토드로우).

기존 compile_stickman.py 의 검증된 기계(TTS·자막·제스처·합성)를 재사용하되, 차이점:
 1) 배경: 씬마다 Flow 파스텔 풍경 PNG(assets/graphics/bg/<bg>.png)를 1280x720 cover-fit + 흰 베일(투명도)로
    살짝 밝게 깔아 글자/캐릭터가 도드라지게. 없으면 절차적 파스텔 배경으로 폴백.
 2) 우측 글자: motion="draw" → 단어 잉크 글리프(word_<text>.png)를 좌→오 점진 리빌(펜촉) 오토드로우.
 3) 좌측 스틱맨: motion="gesture" 포즈 순환(파라메트릭).
 4) 배경 귀퉁이에 아주 작은 새/벌/나비가 살짝 — 강의 방해 안 되게(주체는 글자·캐릭터).

사용:
  python hangeul_birth_vowels/compile_flat_lesson.py --episode KO-W01D2 --prefix hangeul_w1d2_flat --preview
  python hangeul_birth_vowels/compile_flat_lesson.py --episode KO-W01D2 --prefix hangeul_w1d2_flat --lang ko
"""
import os
import sys
import json
import math
import argparse
import sqlite3

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PDIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(PDIR)
sys.path.insert(0, ROOT)
sys.path.insert(0, PDIR)

import compile_stickman as cs           # 검증된 헬퍼/ TTS 재사용
from compile_stickman import (W, H, FPS, FONT, get_font, load_img, paste, get_tile,
                              draw_caption, draw_subtitle, split_chunks, subtitle_text,
                              gesture_layers, ensure_scene_audio, make_bg, _smooth,
                              draw_logo, draw_place)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = os.path.join(ROOT, "channel", "content.db")
BG_DIR = os.path.join(ROOT, "assets", "graphics", "bg")
EP = "KO-W01D2"
OUT_PREFIX = "hangeul_w1d2_flat"

# 배경 흰 베일(투명도) — 풍경을 살짝 밝게 눌러 전경(글자·캐릭터) 가독성↑
BG_VEIL = 0.30


# ---------- 배경: Flow 풍경 cover-fit + 흰 베일 (씬별 캐시) ----------
_BGC = {}
def _avail_bgs():
    """이 에피소드용으로 실제 생성된 Flow 배경 PNG 목록(정렬)."""
    pref = EP.lower().replace("-", "_").replace("ko_w01d2", "bg_w1d2")
    out = []
    if os.path.isdir(BG_DIR):
        for f in sorted(os.listdir(BG_DIR)):
            if f.startswith("bg_w1d2_") and f.endswith(".png"):
                out.append(os.path.join(BG_DIR, f))
    return out


def scene_bg(bg_key):
    if bg_key in _BGC:
        return _BGC[bg_key].copy()
    p = os.path.join(BG_DIR, f"{bg_key}.png") if bg_key else None
    if not (p and os.path.exists(p)):
        # 특정 씬 배경이 아직 없으면 → 생성된 다른 Flow 풍경을 순환 재사용(평면 그라데이션 회피)
        avail = _avail_bgs()
        if avail:
            try:
                idx = int("".join(ch for ch in (bg_key or "") if ch.isdigit())[-2:] or "1")
            except ValueError:
                idx = 1
            p = avail[(idx - 1) % len(avail)]
    if p and os.path.exists(p):
        im = Image.open(p).convert("RGB")
        # cover-fit 1280x720
        s = max(W / im.width, H / im.height)
        nw, nh = int(im.width * s + 0.5), int(im.height * s + 0.5)
        im = im.resize((nw, nh), Image.LANCZOS).crop(
            ((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
        base = im.convert("RGBA")
        veil = Image.new("RGBA", (W, H), (255, 255, 255, int(255 * BG_VEIL)))
        base.alpha_composite(veil)
    else:
        base = make_bg().copy()        # Flow 배경 아직 없으면 절차적 파스텔로 폴백
    _BGC[bg_key] = base.copy()
    return base


# ---------- 글자 오토드로우: 완성 글리프를 좌→오 점진 리빌(+펜촉) ----------
_GLYPH_NP = {}
def _glyph_np(path):
    if path not in _GLYPH_NP:
        im = load_img(path)
        _GLYPH_NP[path] = (im, np.asarray(im).copy())
    return _GLYPH_NP[path]


def reveal_glyph(path, scale, p):
    """word PNG 를 progress p(0..1)까지 좌→오로 그려진 것처럼 리빌한 RGBA 타일 반환."""
    im, arr = _glyph_np(path)
    w = max(1, int(im.width * scale))
    h = max(1, int(im.height * scale))
    if p >= 1.0:
        return get_tile(im, w, h, 0, 1.0)
    a = arr.copy()
    H0, W0 = a.shape[0], a.shape[1]
    # 잉크가 있는 x 범위에서 진행 — 글리프 좌우 여백 무시
    cols = np.where(a[:, :, 3].max(axis=0) > 16)[0]
    if len(cols):
        x0, x1 = int(cols[0]), int(cols[-1])
    else:
        x0, x1 = 0, W0 - 1
    edge = x0 + (x1 - x0) * max(0.0, min(1.0, p))
    feather = max(6, (x1 - x0) * 0.04)
    xs = np.arange(W0)
    m = np.clip((edge - xs) / feather + 1.0, 0.0, 1.0)        # edge 이후로 0
    a[:, :, 3] = (a[:, :, 3].astype(np.float32) * m[None, :]).astype(np.uint8)
    # 펜촉: 진행 위치에 작은 잉크 점
    rev = Image.fromarray(a, "RGBA")
    if 0.02 < p < 0.99:
        pd = ImageDraw.Draw(rev)
        yc = int(H0 * 0.62)
        r = max(3, int(H0 * 0.05))
        pd.ellipse([edge - r, yc - r, edge + r, yc + r], fill=(34, 31, 28, 235))
    return rev.resize((w, h), Image.LANCZOS)


# ---------- 작은 코너 크리터 (절차적, 살짝만) ----------
def draw_critter(base, kind, t):
    if not kind:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ink = (70, 70, 70, 210)
    if kind == "bird":
        # 우상단을 가로지르며 천천히, 날갯짓
        x = 980 + 180 * math.sin(t * 0.5)
        y = 95 + 14 * math.sin(t * 0.9)
        flap = 10 * math.sin(t * 7)
        s = 1.0
        d.line([(x - 16 * s, y), (x, y - flap * 0.6 - 4)], fill=ink, width=3)
        d.line([(x, y - flap * 0.6 - 4), (x + 16 * s, y)], fill=ink, width=3)
        d.line([(x + 2, y - 2), (x + 30 * s, y - 10 - flap * 0.3)], fill=ink, width=3)   # 둘째 새
        d.line([(x + 30 * s, y - 10 - flap * 0.3), (x + 58 * s, y - 2)], fill=ink, width=3)
    elif kind == "bee":
        x = 1090 + 26 * math.sin(t * 2.0)
        y = 150 + 22 * math.sin(t * 3.1)
        d.ellipse([x - 11, y - 8, x + 11, y + 8], fill=(245, 205, 70, 230), outline=(60, 50, 20, 230))
        for sx in (-4, 2):
            d.line([(x + sx, y - 7), (x + sx, y + 7)], fill=(60, 50, 20, 230), width=2)
        wf = 6 * math.sin(t * 18)
        d.ellipse([x - 6, y - 16 - wf, x + 6, y - 6], fill=(255, 255, 255, 150), outline=(120, 120, 120, 150))
    elif kind == "butterfly":
        x = 1080 + 30 * math.sin(t * 1.3)
        y = 150 + 26 * math.sin(t * 1.9)
        wf = abs(math.sin(t * 8))
        wx = 9 + 5 * wf
        for sgn in (-1, 1):
            ax0, ax1 = sorted([x + sgn * 2, x + sgn * (2 + wx)])
            d.ellipse([ax0, y - 12, ax1, y + 2], fill=(240, 150, 190, 200), outline=(140, 80, 120, 200))
            bx0, bx1 = sorted([x + sgn * 2, x + sgn * (2 + wx * 0.8)])
            d.ellipse([bx0, y - 2, bx1, y + 12], fill=(245, 200, 130, 200), outline=(150, 110, 70, 200))
        d.line([(x, y - 12), (x, y + 12)], fill=(60, 50, 50, 220), width=2)
    elif kind == "dragonfly":          # 잠자리 — 빠르게 까딱이며 떠다님(우상단)
        x = 1040 + 70 * math.sin(t * 0.8) + 8 * math.sin(t * 9)
        y = 130 + 30 * math.sin(t * 1.3) + 5 * math.sin(t * 11)
        body = (90, 140, 150, 230)
        d.line([(x, y - 4), (x, y + 26)], fill=body, width=3)              # 긴 몸통
        d.ellipse([x - 4, y - 10, x + 4, y - 2], fill=(120, 180, 190, 235))  # 머리
        wf = 8 * math.sin(t * 22)
        for sgn in (-1, 1):                                                # 4장 투명 날개
            ax0, ax1 = sorted([x + sgn * 2, x + sgn * (2 + 22)])
            d.ellipse([ax0, y - 6 - abs(wf), ax1, y - 2], fill=(200, 230, 235, 120), outline=(140, 180, 190, 150))
            bx0, bx1 = sorted([x + sgn * 2, x + sgn * (2 + 18)])
            d.ellipse([bx0, y + 2, bx1, y + 6 + abs(wf)], fill=(200, 230, 235, 110), outline=(140, 180, 190, 140))
    elif kind == "rabbit":             # 토끼 — 좌하단 구석에서 깡총깡총
        period = 2.6
        ph = (t % period) / period
        hop = math.sin(ph * math.pi)                                       # 0→1→0 포물선
        x = 120 + (t * 14) % 180
        y = 650 - 60 * hop
        bod = (245, 240, 236, 235); out = (90, 80, 78, 235)
        d.ellipse([x - 16, y - 12, x + 16, y + 14], fill=bod, outline=out, width=2)   # 몸
        d.ellipse([x + 8, y - 24, x + 26, y - 4], fill=bod, outline=out, width=2)     # 머리
        for ex in (12, 20):                                                # 귀 두 개
            d.ellipse([x + ex, y - 40, x + ex + 6, y - 22], fill=bod, outline=out, width=2)
        d.ellipse([x + 22, y - 16, x + 26, y - 12], fill=(60, 50, 50, 235))           # 눈
    base.alpha_composite(layer)


# ---------- 씬 로드 ----------
def load_scenes(lang="ko"):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    scenes = []
    for s in con.execute("SELECT * FROM scenes WHERE episode=? ORDER BY seq", (EP,)):
        spec = json.loads(s["image_prompt"])
        objs = []
        for o in con.execute(
            "SELECT a.file_path fp, a.name_en nm, o.cx, o.cy, o.scale, o.z_order, o.is_point, o.motion_type "
            "FROM scene_objects o JOIN assets a ON a.id=o.asset_id "
            "WHERE o.episode=? AND o.scene_seq=? ORDER BY o.z_order", (EP, s["seq"])):
            p = cs.resolve_path(o["fp"])
            if p:
                objs.append(dict(path=p, name=o["nm"], cx=o["cx"], cy=o["cy"], scale=o["scale"],
                                 z=o["z_order"], is_point=o["is_point"], motion=o["motion_type"]))
        # 단어 오토드로우 순서(스태거)
        di = 0
        for o in objs:
            if o["motion"] == "draw":
                o["draw_i"] = di; di += 1
        gpaths = []
        for nm in (spec.get("gesture_seq") or []):
            # 졸라맨(home_vocab/zollaman_*)·스틱맨(poses/stickman_*) 등 여러 경로 탐색
            gp = (cs.resolve_path(f"assets/graphics/poses/{nm}.png")
                  or cs.resolve_path(f"home_vocab/{nm}.png")
                  or cs.resolve_path(f"assets/graphics/poses/stickman_{nm}.png"))
            if gp:
                gpaths.append(gp)
        _script = s["script_kr"] if lang == "ko" else s["script_en"]
        scenes.append(dict(
            seq=s["seq"], dur=s["duration_sec"], script=_script, chunks=split_chunks(_script),
            cap=spec["cap_ko"] if lang == "ko" else spec["cap_en"],
            words=spec.get("words") or [],
            gestures=gpaths, bg=spec.get("bg"), critter=spec.get("critter"),
            place_en=spec.get("place_en", ""), objs=objs))
    con.close()
    return scenes


DRAW_DELAY = 0.5     # 단어별 시작 지연(스태거)
DRAW_DUR = 1.1       # 한 단어 그려지는 시간


def compose(scene, t=None, lang="ko", overlay=True):
    base = scene_bg(scene.get("bg"))
    final = t is None
    tt = scene["dur"] if final else t
    gestures = scene.get("gestures")
    # 배경 크리터(맨 뒤, 풍경 위·전경 아래)
    if not final and scene.get("critter"):
        draw_critter(base, scene["critter"], tt)
    for o in sorted(scene["objs"], key=lambda x: x["z"]):
        if o["motion"] == "draw":
            di = o.get("draw_i", 0)
            start = 0.3 + di * DRAW_DELAY
            p = 1.0 if final else max(0.0, min(1.0, (tt - start) / DRAW_DUR))
            if p <= 0.0:
                continue
            tile = reveal_glyph(o["path"], o["scale"], p)
            ox, oy = int(o["cx"] - tile.width / 2), int(o["cy"] - tile.height / 2)
            # 소프트 흰 후광 — 풍경 위에서도 글자가 또렷이(배경은 그대로 보임)
            al = tile.split()[3]
            halo = Image.new("RGBA", tile.size, (255, 255, 255, 0))
            halo.putalpha(al)
            halo = Image.composite(Image.new("RGBA", tile.size, (255, 255, 255, 255)),
                                   Image.new("RGBA", tile.size, (255, 255, 255, 0)), al)
            halo = halo.filter(ImageFilter.GaussianBlur(max(4, int(tile.height * 0.05))))
            for _ in range(3):
                base.alpha_composite(halo, (ox, oy))
            base.alpha_composite(tile, (ox, oy))
            continue
        is_pose = "/poses/" in o["path"].replace("\\", "/")
        im = load_img(o["path"])
        a = 1.0 if final else min(1.0, tt / 0.4)     # 등장 페이드
        if a <= 0.01:
            continue
        if is_pose:
            # 바닥 그림자
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sd = ImageDraw.Draw(sh)
            sw = int(150 * o["scale"]); shy = o["cy"] + int(300 * o["scale"])
            sd.ellipse([o["cx"] - sw, shy - 16, o["cx"] + sw, shy + 16], fill=(0, 0, 0, 40))
            base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
            glayers, pop = (gesture_layers(gestures, tt) if (gestures and not final) else ([(o["path"], 1.0)], 1.0))
            for gp, ga in glayers:
                paste(base, load_img(gp), o["cx"], o["cy"], o["scale"] * pop, 0.0, a * ga)
        else:
            paste(base, im, o["cx"], o["cy"], o["scale"], 0.0, a)
    if overlay:
        draw_caption(base, scene["cap"])
        draw_subtitle(base, subtitle_text(scene, tt, final))
        draw_logo(base)                                  # 좌상단 로고(모든 동영상 공통)
        draw_place(base, scene.get("place_en"))          # 우하단 장소 영문명
    return base.convert("RGB")


def preview(lang="ko"):
    scenes = load_scenes(lang)
    outdir = os.path.join(PDIR, "preview_flat")
    os.makedirs(outdir, exist_ok=True)
    cols, rows = 3, 3
    cw, ch = W // 2, H // 2
    sheet = Image.new("RGB", (cw * cols, ch * rows), (220, 220, 215))
    for i, sc in enumerate(scenes):
        # 프리뷰: 단어 절반쯤 그려진 중간 프레임 + 제스처 중간
        fr = compose(sc, t=sc["dur"] * 0.6, lang=lang)
        fr.save(os.path.join(outdir, f"s{sc['seq']:02d}.png"))
        r, c = divmod(i, cols)
        if r < rows:
            sheet.paste(fr.resize((cw, ch), Image.LANCZOS), (c * cw, r * ch))
    out = os.path.join(outdir, f"_sheet_{lang}.png")
    sheet.save(out)
    print("preview ->", out)


def render_video(lang="ko"):
    from moviepy import VideoClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
    from moviepy.audio.fx import MultiplyVolume
    scenes = load_scenes(lang)
    clips = []
    print(f"[render:{lang}] {len(scenes)} scenes…")
    for sc in scenes:
        # 영어판: 한글 단어를 선희 발음으로 들려주기 위해 나레이션 끝에 따옴표 친 단어 추가(자막엔 영향 없음)
        _ascript = sc["script"]
        if lang == "en" and sc.get("words"):
            _ascript = _ascript + "  " + "  ".join(f"'{w}'" for w in sc["words"])
        audio_path, narr_dur, _ = ensure_scene_audio(sc["seq"], _ascript, lang)
        narr = AudioFileClip(audio_path)
        LEAD, TAIL = 0.25, 0.55
        dur = narr.duration + LEAD + TAIL
        sc["_t0"] = LEAD
        # 자막 청크 시간창
        _chunks = sc.get("chunks") or [sc["script"]]
        _lens = [max(1, len(c)) for c in _chunks]; _tot = sum(_lens)
        _acc, _sched = LEAD, []
        for _i, _l in enumerate(_lens):
            _w = narr.duration * _l / _tot
            _sched.append((_i, round(_acc, 3), round(_acc + _w, 3))); _acc += _w
        sc["sub_sched"] = _sched

        def mk(t, scene=sc, sdur=dur, _lead=LEAD):
            tt = max(0.0, t - _lead)                          # 배경/애니는 나레이션 시작 기준
            fr = compose(scene, t=tt, lang=lang, overlay=False).convert("RGBA")
            draw_caption(fr, scene["cap"])
            draw_subtitle(fr, subtitle_text(scene, t, False))
            draw_logo(fr)                                     # 좌상단 로고(모든 영상 공통)
            draw_place(fr, scene.get("place_en"))             # 우하단 장소 영문명
            return np.asarray(fr.convert("RGB"))

        clip = VideoClip(frame_function=mk, duration=dur)
        clip = clip.with_audio(CompositeAudioClip([narr.with_start(LEAD)]).with_duration(dur))
        clips.append(clip)
        print(f"  S{sc['seq']:>2}: dur={dur:4.1f}s  narr={narr.duration:4.1f}s")

    video = concatenate_videoclips(clips, method="compose")
    bgm_path = os.path.join(ROOT, "assets", "audio", "lofi_bgm.mp3")
    if os.path.exists(bgm_path):
        try:
            from moviepy import concatenate_audioclips
            bgm = AudioFileClip(bgm_path)
            loops = int(video.duration // bgm.duration) + 1
            bed = concatenate_audioclips([bgm] * loops).subclipped(0, video.duration).with_effects([MultiplyVolume(0.06)])
            video = video.with_audio(CompositeAudioClip([video.audio, bed]))
        except Exception as e:
            print("  (BGM skipped:", e, ")")
    out = os.path.join(PDIR, f"{OUT_PREFIX}_{lang}.mp4")
    video.write_videofile(out, fps=FPS, codec="libx264", audio_codec="aac",
                          threads=4, preset="medium", logger="bar")
    print("video ->", out)

    con = sqlite3.connect(DB)
    con.execute("UPDATE video_projects SET final_path=?, status='rendered', runtime_sec=?, updated_at=datetime('now') WHERE name=?",
                (out, round(video.duration), OUT_PREFIX))
    con.execute("UPDATE episodes SET status='rendered' WHERE code=?", (EP,))
    con.commit(); con.close()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--lang", default="ko")
    ap.add_argument("--episode", default="KO-W01D2")
    ap.add_argument("--prefix", default="hangeul_w1d2_flat")
    args = ap.parse_args()
    EP = args.episode
    cs.EP = args.episode
    OUT_PREFIX = args.prefix
    if args.preview:
        preview(args.lang)
    else:
        render_video(args.lang)
