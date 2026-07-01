import os
import json
import sys

BRAIN_DIR = r"C:\Users\antigravity\.gemini\antigravity\brain"
sys.stdout.reconfigure(encoding='utf-8')

def main():
    if not os.path.exists(BRAIN_DIR):
        print(f"[ERR] Brain dir not found: {BRAIN_DIR}")
        return
        
    print(f"Scanning brain directories under {BRAIN_DIR}...")
    found_any = False
    
    for folder in os.listdir(BRAIN_DIR):
        folder_path = os.path.join(BRAIN_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
            
        logs_dir = os.path.join(folder_path, ".system_generated", "logs")
        if not os.path.exists(logs_dir):
            continue
            
        transcript_path = os.path.join(logs_dir, "transcript.jsonl")
        if not os.path.exists(transcript_path):
            continue
            
        # Scan transcript file
        try:
            with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_no, line in enumerate(f, 1):
                    if "jay_whiteboard_consonants" in line or "pose_jay_whiteboard_writing_side" in line:
                        print(f"\n[FOUND MATCH] Session: {folder} | Line: {line_no}")
                        try:
                            data = json.loads(line)
                            # Print key info
                            print(f"  Source: {data.get('source')}")
                            print(f"  Type: {data.get('type')}")
                            # Clean up content before printing to keep it readable
                            content = data.get('content', '')
                            if content:
                                print(f"  Content preview: {content[:400]}...")
                            # If tool calls are present, print them
                            tool_calls = data.get('tool_calls', [])
                            if tool_calls:
                                print(f"  Tool calls: {json.dumps(tool_calls, indent=2)}")
                        except Exception as parse_err:
                            print(f"  Raw match: {line[:500]}...")
                        found_any = True
        except Exception as e:
            # print(f"Error reading {transcript_path}: {e}")
            pass
            
    if not found_any:
        print("No matches found in logs.")

if __name__ == "__main__":
    main()
