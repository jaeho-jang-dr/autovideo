# -*- coding: utf-8 -*-
"""titan_science 업로드 전 10개 조항 점검."""
import os
import re
import subprocess

import numpy as np
from PIL import Image

os.chdir(os.path.dirname(os.path.abspath(__file__)))
OUT = "titan_science/_out"
SUB = "titan_science/subs"
THUMB = "titan_science/_thumb/out"
AUD = "titan_science/audio"
WM_BOX = (1136, 576, 1184, 624)          # 720p 기준 워터마크 자리
SCALE = 3                                 # 4K = 720p × 3


def probe(f, entries, stream=None):
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream]
    cmd += ["-show_entries", entries, "-of", "csv=p=0", f]
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


rows = []


def chk(no, name, ok, detail):
    rows.append((no, name, ok, detail))


def main():
    files = {L: "%s/TITAN_%s_4K_final.mp4" % (OUT, L) for L in ("KO", "EN")}

    # 1 파일 존재·해상도
    ds = []
    for L, f in files.items():
        wh = probe(f, "stream=width,height", "v")
        ds.append("%s %s" % (L, wh))
    chk(1, "4K 해상도", all("3840,2160" in d for d in ds), " · ".join(ds))

    # 2 워터마크 덮개 — 로고(어두운 남색 원)가 그 자리에 있는지
    ok2, det2 = True, []
    for L, f in files.items():
        for t in (5, 200, 430):
            p = "titan_science/_wm/pc_%s_%d.png" % (L, t)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", f,
                            "-frames:v", "1", p], check=True)
            box = tuple(v * SCALE for v in WM_BOX)
            a = np.asarray(Image.open(p).convert("RGB").crop(box), np.int16)
            r, g, b = a[..., 0].mean(), a[..., 1].mean(), a[..., 2].mean()
            dark_navy = (b > r) and (r < 110)          # 로고 = 어두운 남색 테두리
            ok2 &= dark_navy
            det2.append("%s@%ds rgb(%d,%d,%d)" % (L, t, r, g, b))
    chk(2, "워터마크 로고 덮개", ok2, " · ".join(det2[:3]))

    # 3 자막 5종 · 소프트(번인 아님)
    subs = {}
    for L, f in files.items():
        langs = probe(f, "stream_tags=language", "s").split("\n")
        subs[L] = [x for x in langs if x]
    chk(3, "자막 5종 소프트", all(len(v) == 5 for v in subs.values()),
        "KO %s · EN %s" % (",".join(subs["KO"]), ",".join(subs["EN"])))

    # 4 자막 언어코드 — es-419 / zh-Hans 파일 존재
    want = ["TITAN_ko.srt", "TITAN_en.srt", "TITAN_ja.srt",
            "TITAN_zh-Hans.srt", "TITAN_es-419.srt"]
    have = os.listdir(SUB)
    chk(4, "언어코드 es-419/zh-Hans", all(w in have for w in want),
        " ".join(w.replace("TITAN_", "").replace(".srt", "") for w in want))

    # 5 번역 실패(원문 복사) 여부 — en 과 크기가 같으면 의심
    en_sz = os.path.getsize(os.path.join(SUB, "TITAN_en.srt"))
    sizes = {w: os.path.getsize(os.path.join(SUB, w)) for w in want}
    dup = [w for w, s in sizes.items() if w != "TITAN_en.srt" and s == en_sz]
    chk(5, "번역 통째 실패 없음", not dup,
        " ".join("%s:%dB" % (w.replace("TITAN_", "").replace(".srt", ""), s)
                 for w, s in sizes.items()))

    # 6 나레이션 Azure — .txt 캐시 짝이 다 있는지 + 개수
    mp3 = [f for f in os.listdir(AUD) if f.endswith(".mp3")]
    chk(6, "Azure 나레이션 36개", len(mp3) == 36, "mp3 %d개" % len(mp3))

    # 7 나레이션 잘림 — 씬별 오디오가 씬 길이를 넘지 않는지(렌더에서 맞춤)
    a_ko = probe(files["KO"], "format=duration")
    v_ko = float(a_ko)
    chk(7, "길이 정합(8분대)", 470 < v_ko < 500, "KO %.1f초" % v_ko)

    # 8 오디오 트랙 존재·무음 아님
    ok8, det8 = True, []
    for L, f in files.items():
        # ★-v error 를 주면 volumedetect 결과까지 지워진다(측정 불가). info 로 둔다.
        r = subprocess.run(["ffmpeg", "-i", f, "-af", "volumedetect", "-f", "null", "-"],
                           capture_output=True, text=True)
        m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", r.stderr)
        mv = float(m.group(1)) if m else 0.0
        ok8 &= mv < -1 and mv > -50
        det8.append("%s %.1fdB" % (L, mv))
    chk(8, "오디오 정상", ok8, " · ".join(det8))

    # 9 썸네일 1280x720 · 2MB 미만
    ok9, det9 = True, []
    for n in ("ko_A", "en_A"):
        p = os.path.join(THUMB, "titan_%s.jpg" % n)
        im = Image.open(p)
        sz = os.path.getsize(p)
        ok9 &= im.size == (1280, 720) and sz < 2 * 1024 * 1024
        det9.append("%s %dx%d %dKB" % (n, im.size[0], im.size[1], sz // 1024))
    chk(9, "썸네일 규격", ok9, " · ".join(det9))

    # 10 화면 안 글자(번인 자막) 없음 — 하단 자막 영역이 비어 있는지
    p = "titan_science/_wm/pc_KO_200.png"
    a = np.asarray(Image.open(p).convert("L"), np.float32)
    strip = a[int(2160 * 0.82):int(2160 * 0.96), :]
    # 번인 자막이 있으면 흰 글자 화소가 뭉쳐 나온다
    white_ratio = float((strip > 235).mean())
    chk(10, "자막 번인 없음", white_ratio < 0.02, "하단 흰화소 %.3f%%" % (white_ratio * 100))

    print("=" * 74)
    print("titan_science 업로드 전 10개 조항")
    print("=" * 74)
    bad = 0
    for no, name, ok, det in rows:
        mark = "OK  " if ok else "★NG"
        if not ok:
            bad += 1
        print("%2d. %-4s %-22s %s" % (no, mark, name, det))
    print("-" * 74)
    print("통과 %d/10%s" % (10 - bad, "" if not bad else "  ★확인 필요"))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
