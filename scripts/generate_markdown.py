#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_markdown.py — Generate detailed Markdown guide for 168 places.
Produces korea_168_scenic_places_details.md.
"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(ROOT, "web", "src", "data", "korea_places.json")
OUT_MD = os.path.join(ROOT, "korea_168_scenic_places_details.md")

def generate_md():
    if not os.path.exists(JSON_FILE):
        print(f"JSON file not found: {JSON_FILE}")
        return
        
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        places = json.load(f)
        
    print(f"Loaded {len(places)} places. Creating Markdown...")
    
    md_content = []
    md_content.append("# Korea 168 Scenic Places for Foreign Visitors — Detailed Travel Guide")
    md_content.append("\nThis document provides comprehensive details for 168 top travel destinations in South Korea, including bilingual descriptions, directions, map locations, visual prompts, and official reference websites.\n")
    
    for p in places:
        no = p["no"]
        name_en = p["name_en"]
        name_ko = p["name_ko"]
        reg_en = p["region_en"]
        reg_ko = p["region_ko"]
        cat = p["category"]
        leisure = p["leisure_ko"]
        why_en = p["why_en"]
        why_ko = p["why_ko"]
        motif = p["motif"]
        
        desc_en = p.get("description_en", "")
        desc_ko = p.get("description_ko", "")
        dir_en = p.get("directions_en", "")
        dir_ko = p.get("directions_ko", "")
        map_lnk = p.get("map_link", "")
        off_lnk = p.get("official_link", "")
        img_url = p.get("image_url", "")
        
        md_content.append(f"## #{no}. {name_en} ({name_ko})")
        md_content.append(f"- **Region / 지역**: {reg_en} ({reg_ko})")
        md_content.append(f"- **Category / 분류**: {cat}")
        md_content.append(f"- **Key Activities / 대표 레저**: {leisure}")
        md_content.append(f"- **Summary (EN)**: {why_en}")
        md_content.append(f"- **Summary (KO)**: {why_ko}")
        md_content.append(f"- **Detailed Description (EN)**: {desc_en}")
        md_content.append(f"- **Detailed Description (KO)**: {desc_ko}")
        md_content.append(f"- **How to Get There (EN)**: {dir_en}")
        md_content.append(f"- **How to Get There (KO)**: {dir_ko}")
        md_content.append(f"- **Map Location**: [View on Google Maps]({map_lnk})")
        md_content.append(f"- **Official Website / Reference**: [Travel Guide / Info]({off_lnk})")
        md_content.append(f"- **Image Link**: [View Photo]({img_url})")
        md_content.append(f"- **Visual Motif (Veo prompt)**: `{motif}`")
        md_content.append("\n" + "—" * 40 + "\n")
        
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))
        
    print(f"Successfully generated Markdown file at {OUT_MD}")

if __name__ == "__main__":
    generate_md()
