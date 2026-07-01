# -*- coding: utf-8 -*-
"""졸라 한글 쇼츠용 배경음악 — 경쾌한 자작 인스트루멘탈(저작권 무관, 임시).
MusicGen-small로 ~28초 생성. 나중에 유튜브에서 공식 음원으로 교체 예정."""
import os, sys, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
OUT = os.path.join(ROOT, "zolla_hangul", "bgm.wav")
PROMPT = ("upbeat playful quirky electronic pop instrumental, bright bouncy synth marimba, "
          "cheerful kids educational, light claps, fun energetic, major key, no vocals")
SECONDS = 28

def main():
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    import scipy.io.wavfile as wav
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={dev}; musicgen-small 로딩...")
    proc = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to(dev)
    sr = model.config.audio_encoder.sampling_rate
    torch.manual_seed(7)
    inp = proc(text=[PROMPT], padding=True, return_tensors="pt").to(dev)
    with torch.no_grad():
        out = model.generate(**inp, max_new_tokens=SECONDS * 50, do_sample=True, guidance_scale=3.0)
    a = out[0, 0].cpu().numpy().astype(np.float32)
    a = a / (np.max(np.abs(a)) or 1.0) * 0.95
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wav.write(OUT, sr, (a * 32767).astype(np.int16))
    print(f"[OK] {OUT} ({len(a)/sr:.1f}s, {sr}Hz)")

if __name__ == "__main__":
    main()
