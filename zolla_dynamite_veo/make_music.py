# -*- coding: utf-8 -*-
"""졸라 힙합 쇼츠 배경음악 — 자작 힙합/EDM 인스트루멘탈(무가사, 저작권 무관, 임시)."""
import os, sys, numpy as np
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _s in (sys.stdout,sys.stderr):
    try: _s.reconfigure(encoding="utf-8",errors="replace")
    except Exception: pass
OUT=os.path.join(ROOT,"zolla_dynamite_veo","bgm.wav")
PROMPT=("energetic modern k-pop hip hop dance instrumental, punchy boom-bap drums, deep 808 bass, "
        "bright synth stabs, crisp hi-hats, confident groovy beat, no vocals")
SECONDS=14
def main():
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    import scipy.io.wavfile as wav
    dev="cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={dev}; musicgen-small 로딩...")
    proc=AutoProcessor.from_pretrained("facebook/musicgen-small")
    model=MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to(dev)
    sr=model.config.audio_encoder.sampling_rate
    torch.manual_seed(11)
    inp=proc(text=[PROMPT],padding=True,return_tensors="pt").to(dev)
    with torch.no_grad():
        out=model.generate(**inp,max_new_tokens=SECONDS*50,do_sample=True,guidance_scale=3.0)
    a=out[0,0].cpu().numpy().astype(np.float32); a=a/(np.max(np.abs(a)) or 1.0)*0.95
    wav.write(OUT,sr,(a*32767).astype(np.int16))
    print(f"[OK] {OUT} ({len(a)/sr:.1f}s)")
if __name__=="__main__": main()
