# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Force UTF-8 stdout
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    target_dir = os.path.join(ROOT, "assets", "audio")
    os.makedirs(target_dir, exist_ok=True)
    output_path = os.path.join(target_dir, "waltz_bgm.wav")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    print("Loading MusicGen model (facebook/musicgen-small)...")
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to(device)
    
    prompt = ("Classical romantic waltz, elegant strings and grand piano, 3/4 time signature, "
              "majestic ballroom dance rhythm, Versailles palace style, 90 bpm, beautiful melody, "
              "high quality audio")
              
    print(f"Generating 30s waltz loop for prompt: '{prompt}'...")
    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt",
    ).to(device)
    
    with torch.inference_mode():
        # max_new_tokens=1500 generates exactly 30s (50 tokens per second)
        audio_values = model.generate(**inputs, max_new_tokens=1500)
        
    sampling_rate = model.config.audio_encoder.sampling_rate
    audio_data = audio_values[0, 0].cpu().numpy().astype("float32")
    
    # Peak normalize
    peak = float(np.max(np.abs(audio_data))) or 1.0
    audio_data = audio_data / peak * 0.95
    
    # Loop it 5 times to make it 150 seconds (2m 30s)
    looped_audio = np.tile(audio_data, 5)
    
    # Convert to PCM 16-bit
    pcm16 = np.int16(np.clip(looped_audio, -1.0, 1.0) * 32767)
    
    print(f"Saving looped WAV to {output_path} (length: {len(pcm16)/sampling_rate:.2f}s)...")
    wavfile.write(output_path, rate=sampling_rate, data=pcm16)
    print("AI Waltz Music generation complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
