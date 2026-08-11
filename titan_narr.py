# -*- coding: utf-8 -*-
"""titan_science 나레이션 — 시나리오에서 KO/EN 을 뽑아 edge-tts 로 만든다.

★사장님 지시(2026-08-10): 이번 판은 **edge-tts** 로 간다(초안 등급).
  최종 4K 판을 낼 때는 Azure(선희/Emma)로 다시 뽑아야 한다.

    python titan_narr.py            # KO·EN 전부
    python titan_narr.py --lang ko  # 한쪽만
    python titan_narr.py --report   # 만들지 않고 길이만 본다
"""
import argparse
import asyncio
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
SCEN = os.path.join(ROOT, "titan_science", "titan_scenario_v2.md")
CLIP_DIR = os.path.join(ROOT, "titan_science", "keyframes")
AUD_DIR = os.path.join(ROOT, "titan_science", "audio")

VOICE = {"ko": "ko-KR-SunHiNeural", "en": "en-US-EmmaMultilingualNeural"}
RATE = "+10%"          # ★디폴트 — 나레이션은 항상 10% 빠르게


def scenes():
    """시나리오에서 씬 번호별 KO/EN 나레이션을 뽑는다."""
    txt = open(SCEN, encoding="utf-8").read()
    out = {}
    # '### S1 — …' 로 잘라서 그 안의 **KO** / **EN** 줄을 찾는다
    parts = re.split(r"^### S(\d+)\s*—", txt, flags=re.M)
    for i in range(1, len(parts), 2):
        n = int(parts[i])
        body = parts[i + 1]
        ko = re.search(r"^\*\*KO\*\*\s*(.+)$", body, re.M)
        en = re.search(r"^\*\*EN\*\*\s*(.+)$", body, re.M)
        if ko and en:
            out[n] = {"ko": clean(ko.group(1)), "en": clean(en.group(1))}
    return dict(sorted(out.items()))


def clean(s):
    """마크다운 강조를 걷어낸다 — TTS 가 별표를 읽으면 안 된다."""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def scene_lengths():
    """씬별 영상 길이(초) — 클립 개수 × 실측 길이."""
    import collections
    per = collections.defaultdict(float)
    for f in os.listdir(CLIP_DIR):
        if not f.endswith(".mp4"):
            continue
        m = re.match(r"^s(\d\d)_", f)
        if not m:
            continue
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-of", "csv=p=0",
                            os.path.join(CLIP_DIR, f)],
                           capture_output=True, text=True).stdout.strip()
        per[int(m.group(1))] += float(d)
    return dict(sorted(per.items()))


def dur(path):
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return float(d) if d else 0.0


async def synth_edge(text, voice, out):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=RATE).save(out)


def synth_azure(text, lang, out):
    """★최종본용 — 공식 Azure(선희/Emma). 상업 라이선스가 명확하다.
    save_tts_azure 에는 속도 조절이 없어서 만든 뒤 atempo 로 1.1배속을 맞춘다."""
    from dotenv import load_dotenv
    load_dotenv()
    import tts_manager
    raw = out + ".raw.mp3"
    tts_manager.save_tts_azure(text, raw, lang=lang)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw,
                    "-filter:a", "atempo=1.1", "-c:a", "libmp3lame",
                    "-b:a", "192k", out], check=True)
    os.remove(raw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["ko", "en"], help="한쪽만")
    ap.add_argument("--report", action="store_true", help="만들지 않고 길이만")
    ap.add_argument("--engine", choices=["edge", "azure"], default="edge",
                    help="azure = 최종본(선희/Emma, 상업 라이선스)")
    ap.add_argument("--force", action="store_true", help="캐시 무시하고 다시 만든다")
    a = ap.parse_args()

    sc = scenes()
    vid = scene_lengths()
    langs = [a.lang] if a.lang else ["ko", "en"]
    os.makedirs(AUD_DIR, exist_ok=True)

    print("씬 %d개 · 영상 총 %.1f초" % (len(sc), sum(vid.values())))
    print("%-4s %7s %8s %8s %6s" % ("씬", "영상", "KO", "EN", "여유"))
    over = []
    for n in sc:
        row = {}
        for lg in langs:
            out = os.path.join(AUD_DIR, "s%02d_%s.mp3" % (n, lg))
            if not a.report and (a.force or not os.path.exists(out)):
                if a.engine == "azure":
                    synth_azure(sc[n][lg], lg, out)
                else:
                    asyncio.run(synth_edge(sc[n][lg], VOICE[lg], out))
            row[lg] = dur(out) if os.path.exists(out) else 0.0
        v = vid.get(n, 0.0)
        longest = max(row.values()) if row else 0.0
        slack = v - longest
        print("S%02d %7.1f %8.1f %8.1f %6.1f%s" %
              (n, v, row.get("ko", 0), row.get("en", 0), slack,
               "  ★초과" if slack < 0 else ""))
        if slack < 0:
            over.append((n, -slack))
    print("-" * 40)
    if over:
        print("★영상보다 긴 씬 %d개:" % len(over),
              ", ".join("S%02d(+%.1f초)" % (n, x) for n, x in over))
    else:
        print("전 씬 나레이션이 영상 안에 들어간다")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
