# -*- coding: utf-8 -*-
"""pianoduo BGM — 점점 어려워지는 피아노 연탄곡 아크 (총 150초).
MusicGen-small로 5개 30초 세그먼트(젓가락행진곡→경쾌→빠름→리스트급→라흐마니노프 피날레)를
생성해 짧은 크로스페이드로 이어붙여 pianoduo/pianoduo_bgm.wav 저장."""
import os, sys, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

OUT = os.path.join(ROOT, "pianoduo", "pianoduo_bgm.wav")
SEG = 30  # 초/세그먼트 × 5 = 150
# seg1=좋았음(유지). seg2·3=너무 불안(anxious)했다는 피드백 → 안정적·따뜻·해소되는 화성으로 교체.
PROMPTS = [
    "simple cheerful Chopsticks waltz piano duet, playful nursery melody, easy, light, gentle slow tempo, solo grand piano",
    "warm cheerful piano four-hands duet, gentle major key, steady comfortable medium tempo, smooth singing melody, calm and stable, well resolved consonant harmony, solo grand piano",
    "bright graceful classical piano duet, flowing steady rhythm, joyful harmonious melody, clear resolved phrasing, elegant relaxed and stable, solo grand piano",
    "very fast dramatic romantic piano, Liszt style etude, furious cascading arpeggios, powerful and intense, solo grand piano",
    "explosive virtuosic Rachmaninoff style piano finale, thunderous fortissimo chords, climactic dramatic ending, solo grand piano",
]
# 세그먼트별 캐시 파일(부분 재생성용). 비우면 전체 재생성.
SEG_DIR = os.path.join(ROOT, "pianoduo", "_bgm_segments")

def main():
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    import scipy.io.wavfile as wav
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={dev}; loading musicgen-small ...")
    proc = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to(dev)
    sr = model.config.audio_encoder.sampling_rate
    tok_per_sec = 50  # musicgen ~50 tokens/sec
    max_new = SEG * tok_per_sec

    os.makedirs(SEG_DIR, exist_ok=True)
    only = [int(x) for x in sys.argv[1:] if x.isdigit()]  # 예: ... 2 3  → seg2,3만 재생성
    segs = []
    for i, pr in enumerate(PROMPTS, 1):
        segp = os.path.join(SEG_DIR, f"seg_{i}.wav")
        if os.path.exists(segp) and only and i not in only:
            sr2, pcm = wav.read(segp)
            a = (pcm.astype(np.float32) / 32767.0)
            segs.append(a); print(f"   seg {i}: 캐시 사용 ({len(a)/sr:.1f}s)")
            continue
        print(f"[{i}/5] {pr[:60]}...")
        torch.manual_seed(1000 + i)  # 재현성(부분 재생성 시 다른 세그먼트 불변)
        inp = proc(text=[pr], padding=True, return_tensors="pt").to(dev)
        with torch.no_grad():
            wavout = model.generate(**inp, max_new_tokens=max_new, do_sample=True, guidance_scale=3.0)
        a = wavout[0, 0].cpu().numpy().astype(np.float32)
        peak = float(np.max(np.abs(a))) or 1.0
        a = a / peak * 0.95
        wav.write(segp, sr, (a * 32767).astype(np.int16))  # 세그먼트 캐시 저장
        segs.append(a)
        print(f"   seg {i}: {len(a)/sr:.1f}s -> {os.path.basename(segp)}")

    # 0.6s 크로스페이드로 이어붙이기
    xf = int(0.6 * sr)
    out = segs[0]
    for a in segs[1:]:
        if len(out) > xf and len(a) > xf:
            fade = np.linspace(1, 0, xf)
            out[-xf:] = out[-xf:] * fade + a[:xf] * (1 - fade)
            out = np.concatenate([out, a[xf:]])
        else:
            out = np.concatenate([out, a])
    peak = float(np.max(np.abs(out))) or 1.0
    out = out / peak * 0.95
    pcm16 = (out * 32767).astype(np.int16)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wav.write(OUT, sr, pcm16)
    print(f"[OK] {OUT}  ({len(out)/sr:.1f}s, {sr}Hz)")

if __name__ == "__main__":
    main()
