import os
import sys
import json
import subprocess

def run_nlm_cmd(args):
    # Run nlm command and return stdout
    cmd = ["nlm"] + args
    # Ensure UTF-8 output on Windows
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        shell=True
    )
    if result.returncode != 0:
        print(f"nlm command failed: {' '.join(cmd)}")
        print(f"Error: {result.stderr}")
        return None
    return result.stdout.strip()

def sync():
    print("Checking NotebookLM integration...")
    # List notebooks
    notebooks_out = run_nlm_cmd(["notebook", "list", "--json"])
    if notebooks_out is None:
        print("NotebookLM CLI (nlm) is not logged in or not working properly. Please run 'nlm login' manually if needed.")
        return
        
    notebook_id = None
    try:
        notebooks = json.loads(notebooks_out)
        for nb in notebooks:
            if nb.get("title") == "autovideo":
                notebook_id = nb.get("id")
                break
    except Exception:
        # Fallback to string parsing if not JSON (though CLI specifies --json)
        if "autovideo" in notebooks_out:
            for line in notebooks_out.splitlines():
                if "autovideo" in line:
                    # Parse ID from line like "ID: abc123... Title: autovideo"
                    parts = line.split()
                    for p in parts:
                        if len(p) > 20 and not p.startswith("http"):
                            notebook_id = p
                            break
                            
    if not notebook_id:
        print("Creating new notebook 'autovideo'...")
        create_out = run_nlm_cmd(["notebook", "create", "autovideo"])
        if not create_out:
            print("Failed to create notebook.")
            return
        # Parse ID from output: "ID: abc123..."
        for line in create_out.splitlines():
            if "ID:" in line:
                notebook_id = line.split("ID:")[-1].strip()
                break
                
    if not notebook_id:
        print("Could not retrieve notebook ID.")
        return
        
    print(f"Notebook ID: {notebook_id}")
    # Set alias
    run_nlm_cmd(["alias", "set", "autovideo", notebook_id])
    
    # Files to sync
    files_to_sync = [
        "CLAUDE.md",
        "GEMINI.md",
        "영상제작.md",
        "FLOW_MANUAL.md",
        "VEO_WORKFLOW.md"
    ]
    
    # Get current sources to avoid duplicate uploads
    sources_out = run_nlm_cmd(["source", "list", "autovideo", "--json"])
    existing_titles = []
    if sources_out:
        try:
            sources = json.loads(sources_out)
            existing_titles = [src.get("title") for src in sources if src.get("title")]
        except Exception:
            pass
            
    for filename in files_to_sync:
        if not os.path.exists(filename):
            continue
            
        title = f"autovideo_{filename}"
        if title in existing_titles:
            print(f"Source '{title}' already exists. Skipping upload.")
            continue
            
        print(f"Uploading '{filename}' as source '{title}'...")
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Add text source
        run_nlm_cmd(["source", "add", "autovideo", "--text", content, "--title", title])
        
    print("NotebookLM Sync Completed Successfully!")

if __name__ == "__main__":
    sync()
