import json
import os

transcript_path = r"C:\Users\antigravity\.gemini\antigravity\brain\e238b903-9194-42e1-9d1d-887a758c491e\.system_generated\logs\transcript_full.jsonl"
out_path = r"d:\Entertainments\DevEnvironment\autovideo\scratch\extracted_script_raw.txt"

def extract():
    if not os.path.exists(transcript_path):
        print("Transcript file not found!")
        return
        
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            # Find planner response or tool call send_message
            if data.get("type") == "PLANNER_RESPONSE" and "tool_calls" in data:
                for tc in data["tool_calls"]:
                    if tc.get("name") == "send_message":
                        msg = tc["args"].get("Message")
                        if "Updated Script" in msg or "Scene 96" in msg:
                            print("Found target message!")
                            with open(out_path, "w", encoding="utf-8") as out:
                                out.write(msg)
                            print(f"Extracted to {out_path}")
                            return

if __name__ == "__main__":
    extract()
