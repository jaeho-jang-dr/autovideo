import re
import html
import os

def clean_html(html_content):
    # Remove script and style tags
    clean = re.sub(r'<(script|style)\b[^>]*>([\s\S]*?)<\/\1>', '', html_content, flags=re.IGNORECASE)
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', ' ', clean)
    # Unescape HTML entities
    clean = html.unescape(clean)
    # Normalize whitespaces
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()

def main():
    source_file = r"C:\Users\antigravity\.gemini\antigravity\brain\a005b0f1-e612-486b-aedc-4226f29cb2a8\.system_generated\steps\615\content.md"
    dest_file = r"d:\Entertainments\DevEnvironment\autovideo\scratch\cleaned_google_doc.txt"
    
    if not os.path.exists(source_file):
        print("Source file not found.")
        return
        
    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    cleaned = clean_html(content)
    
    # Let's save a structured version
    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(cleaned)
    print(f"Cleaned content saved to: {dest_file}")
    print("Length of cleaned content:", len(cleaned))
    print("Preview of cleaned content (first 1000 chars):")
    print(cleaned[:1000])

if __name__ == "__main__":
    main()
