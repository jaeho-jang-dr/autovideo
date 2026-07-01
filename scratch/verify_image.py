# -*- coding: utf-8 -*-
import os
from PIL import Image

def verify_image(path):
    if not os.path.exists(path):
        print(f"Error: {path} does not exist!")
        return
    img = Image.open(path)
    print(f"File: {path}")
    print(f"Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
    if img.mode == "RGBA":
        alphas = list(img.getdata(3)) # 0:R, 1:G, 2:B, 3:A
        total = len(alphas)
        transparent = sum(1 for a in alphas if a == 0)
        pct = 100.0 * transparent / total
        print(f"Transparency: {transparent}/{total} pixels ({pct:.2f}%)")
    else:
        print("No alpha channel found!")

if __name__ == "__main__":
    verify_image("home_vocab/clock.png")
