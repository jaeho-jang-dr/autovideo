import os
import sys
import subprocess

# Auto-install dependencies if missing
try:
    import scipy
    import transformers
    import accelerate
except ImportError:
    print("Installing PyTorch audio dependencies (transformers, scipy, accelerate)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers", "scipy", "accelerate"])
    import scipy
    import transformers
    import accelerate

import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
from scipy.io import wavfile

# Setup paths
target_dir = r"d:\Entertainments\DevEnvironment\autovideo\assets\audio"
os.makedirs(target_dir, exist_ok=True)
output_path = os.path.join(target_dir, "kpop_song_1.wav")

print("Checking PyTorch GPU acceleration status...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device} (GPU: {torch.cuda.get_device_name(0) if device == 'cuda' else 'None'})")

print("Loading Meta's MusicGen model (facebook/musicgen-small)...")
try:
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to(device)
except Exception as e:
    print(f"Error loading model: {e}")
    sys.exit(1)

prompt = "90s K-Pop dance pop, retro synthwave, energetic beats, catchy hook, bright 808 bass, upbeat tempo 120bpm, educational fun, crisp production"
print(f"Generating music for prompt: '{prompt}'...")

try:
    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt",
    ).to(device)

    # max_new_tokens=1500 triggers exactly 30 seconds of generation (50 frames per sec)
    with torch.inference_mode():
        audio_values = model.generate(**inputs, max_new_tokens=1500)

    sampling_rate = model.config.audio_encoder.sampling_rate
    audio_data = audio_values[0, 0].cpu().numpy().astype("float32")

    # MusicGen can output samples beyond [-1, 1]; peak-normalize and write as
    # 16-bit PCM so the WAV plays cleanly (no clipping) in every browser's
    # HTML5 Audio engine (float32 WAV is not universally supported).
    import numpy as np
    peak = float(np.max(np.abs(audio_data))) or 1.0
    audio_data = audio_data / peak * 0.95
    pcm16 = np.int16(np.clip(audio_data, -1.0, 1.0) * 32767)

    print(f"Saving generated WAV audio to {output_path}...")
    wavfile.write(output_path, rate=sampling_rate, data=pcm16)

    # Write a status JSON for the web interface
    import json
    status_path = os.path.join(target_dir, "song_status.json")
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump({"status": "loaded", "filename": "kpop_song_1.wav"}, f)

    print("Success! AI Song generated locally using RTX 5070 GPU.")
except Exception as e:
    print(f"Error generating music: {e}")
    sys.exit(1)
