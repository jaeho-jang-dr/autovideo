import os
import glob
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(ROOT_DIR, "reverse_engineering_catalog.md")

# Gather files
md_files = glob.glob(os.path.join(ROOT_DIR, "**", "*.md"), recursive=True)

# List of files we care about (excluding node_modules and .git)
filtered_files = []
for f in md_files:
    if "node_modules" in f or ".git" in f or ".gemini" in f or "CLAUDE.md" in f or "GEMINI.md" in f:
        continue
    if os.path.basename(f) == "reverse_engineering_catalog.md" or os.path.basename(f) == "autovideo_assets.md":
        continue
    filtered_files.append(f)

# Helper to read title from md file
def get_title_and_summary(file_path):
    title = ""
    summary = ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line_strip = line.strip()
                if not title and line_strip.startswith("#"):
                    title = line_strip.replace("#", "").strip()
                elif title and line_strip and not line_strip.startswith("#") and not line_strip.startswith("-") and not line_strip.startswith("*"):
                    summary = line_strip
                    if len(summary) > 200:
                        summary = summary[:197] + "..."
                    break
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return title or os.path.basename(file_path), summary or "No summary available."

catalog = []

for path in filtered_files:
    rel_path = os.path.relpath(path, ROOT_DIR)
    abs_path = os.path.abspath(path)
    title, summary = get_title_and_summary(path)
    
    # Categorize
    category = "General Reference"
    basename = os.path.basename(path).lower()
    
    if "deep_research" in basename:
        category = "Video & Topic Deep Research (딥리서치 소스 자료)"
    elif "spec" in basename:
        category = "Video & Platform Reverse Engineering (역공학 명세서)"
    elif "manual" in basename or "workflow" in basename:
        category = "Workflow & Automation Guidelines (가이드라인)"
    elif "planning" in basename or "roadmap" in basename or "bible" in basename:
        category = "Project Planning & Channel Strategy (기획/로드맵)"
        
    catalog.append({
        "category": category,
        "filename": os.path.basename(path),
        "path": rel_path,
        "abs_path": abs_path,
        "title": title,
        "summary": summary
    })

# Group
grouped = {}
for item in catalog:
    cat = item["category"]
    if cat not in grouped:
        grouped[cat] = []
    grouped[cat].append(item)

# Build Markdown
md = []
md.append("# AutoVideo Reverse Engineering & Research Index")
md.append("\n> **오토비디오 프로젝트 내 동영상 분석, 벤치마킹 채널 역공학 및 딥리서치 지식 자원 인덱스**")
md.append("> ")
md.append("> *본 명세서는 조감독(Gemini)이 작성하여 감독(Claude)에게 전달하는 자료입니다.*")
md.append("> *새 비디오 기획 및 컴파일 렌더링 설계 시 아래 인덱스의 역공학 구조와 기획 원칙을 최우선으로 준수해 주십시오.*")
md.append("\n---\n")

for cat, items in sorted(grouped.items()):
    md.append(f"## {cat}")
    md.append("")
    md.append("| 파일명 (Filename) | 주제 및 제목 (Title) | 파일 절대 경로 (Absolute File Path) | 설명 및 개요 (Summary) |")
    md.append("| :--- | :--- | :--- | :--- |")
    for item in sorted(items, key=lambda x: x["filename"]):
        clean_abs_path = item['abs_path'].replace('\\', '/')
        if not clean_abs_path.startswith('/'):
            clean_abs_path = '/' + clean_abs_path
        path_link = f"[{item['filename']}](file://{clean_abs_path})"
        md.append(f"| `{item['filename']}` | {item['title']} | {path_link} | {item['summary']} |")
    md.append("")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Catalog successfully written to {OUTPUT_FILE}")
