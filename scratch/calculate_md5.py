# -*- coding: utf-8 -*-
import os
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    for name in ["zollaman_pointing.png", "zollaman_thinking.png"]:
        p = os.path.join(ROOT, "home_vocab", name)
        if os.path.exists(p):
            print(f"File: {name}")
            print(f"  Size: {os.path.getsize(p)} bytes")
            print(f"  MD5: {get_md5(p)}")
        else:
            print(f"File: {name} not found!")

if __name__ == "__main__":
    main()
