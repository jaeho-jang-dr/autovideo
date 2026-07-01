#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""최면술 비디오 썸네일 수동 빌드 및 구글 드라이브 복사 스크립트."""
import os
import sys
import shutil

ROOT = r"d:\Entertainments\DevEnvironment\autovideo"
sys.path.append(ROOT)

from make_video import generate_thumbnail

def main():
    print("=" * 60)
    print("  최면술 비디오 썸네일 수동 생성 및 드라이브 복사 시작")
    print("=" * 60)

    bg_image = os.path.join(ROOT, "hypnosis_science", "scene_0.png")
    output_path = os.path.join(ROOT, "hypnosis_science", "scene_0_thumbnail_korean.png")
    
    title = "천천히 회전하는 회중시계를 바라봅니다."
    subtitle = "최면술사의 부드러운 목소리를 따라가다 보면, 어느새 깊은 몰입 상태에 빠집게 됩니다."
    
    print(f"Generating thumbnail: {bg_image} -> {output_path}")
    generate_thumbnail(bg_image, title, subtitle, output_path)
    
    if os.path.exists(output_path):
        print("Thumbnail generated successfully in local folder.")
        # 구글 드라이브 복사
        drive_dst = r"G:\내 드라이브\AutoVideo\hypnosis_science_thumbnail.png"
        print(f"Copying to Google Drive: {drive_dst}")
        if os.path.exists(drive_dst):
            try: os.remove(drive_dst)
            except Exception: pass
            
        shutil.copy2(output_path, drive_dst)
        ok = os.path.exists(drive_dst) and os.path.getsize(output_path) == os.path.getsize(drive_dst)
        if ok:
            print(f"[SUCCESS] Drive copy verified: {drive_dst} ({os.path.getsize(drive_dst)} bytes)")
        else:
            print("[ERR] Drive copy failed or size mismatch!")
    else:
        print("[ERR] Failed to generate local thumbnail!")

if __name__ == "__main__":
    main()
