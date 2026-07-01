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

def sync(target_notebook_title="Korea 168 Scenic Places for Foreign Visitors (drjayed)"):
    print(f"Checking NotebookLM integration for '{target_notebook_title}'...")
    # List notebooks
    notebooks_out = run_nlm_cmd(["notebook", "list", "--json"])
    if notebooks_out is None:
        print("NotebookLM CLI (nlm) is not logged in or not working properly. Please run 'nlm login' manually if needed.")
        return
        
    notebook_id = None
    try:
        notebooks = json.loads(notebooks_out)
        for nb in notebooks:
            if nb.get("title") == target_notebook_title:
                notebook_id = nb.get("id")
                break
    except Exception:
        # Fallback to string parsing
        if target_notebook_title in notebooks_out:
            for line in notebooks_out.splitlines():
                if target_notebook_title in line:
                    parts = line.split()
                    for p in parts:
                        if len(p) > 20 and not p.startswith("http"):
                            notebook_id = p
                            break
                            
    if not notebook_id:
        # Try finding autovideo as fallback
        print(f"Notebook '{target_notebook_title}' not found. Falling back to 'autovideo'...")
        target_notebook_title = "autovideo"
        try:
            notebooks = json.loads(notebooks_out)
            for nb in notebooks:
                if nb.get("title") == "autovideo":
                    notebook_id = nb.get("id")
                    break
        except Exception:
            if "autovideo" in notebooks_out:
                for line in notebooks_out.splitlines():
                    if "autovideo" in line:
                        parts = line.split()
                        for p in parts:
                            if len(p) > 20 and not p.startswith("http"):
                                notebook_id = p
                                break

    if not notebook_id:
        print(f"Creating new notebook '{target_notebook_title}'...")
        create_out = run_nlm_cmd(["notebook", "create", target_notebook_title])
        if not create_out:
            print("Failed to create notebook.")
            return
        for line in create_out.splitlines():
            if "ID:" in line:
                notebook_id = line.split("ID:")[-1].strip()
                break
                
    if not notebook_id:
        print("Could not retrieve notebook ID.")
        return
        
    print(f"Notebook Title: {target_notebook_title}")
    print(f"Notebook ID: {notebook_id}")
    
    # Set alias based on notebook title
    alias_name = "korea_places" if "Korea 168" in target_notebook_title else "autovideo"
    run_nlm_cmd(["alias", "set", alias_name, notebook_id])
    
    # Files to sync based on notebook title
    if alias_name == "korea_places":
        files_to_sync = ["korea_168_scenic_places_details.md"]
    else:
        files_to_sync = [
            "CLAUDE.md",
            "GEMINI.md",
            "영상제작.md",
            "FLOW_MANUAL.md",
            "VEO_WORKFLOW.md",
            "scenario.txt",
            "chiropractic_science_prompts.txt"
        ]
    
    # Get current sources to avoid duplicate uploads
    sources_out = run_nlm_cmd(["source", "list", alias_name, "--json"])
    existing_titles = []
    if sources_out:
        try:
            sources = json.loads(sources_out)
            existing_titles = [src.get("title") for src in sources if src.get("title")]
        except Exception:
            pass
            
    for filename in files_to_sync:
        if not os.path.exists(filename):
            print(f"File {filename} does not exist. Skipping.")
            continue
            
        title = f"{alias_name}_{filename}"
        if title in existing_titles:
            print(f"Source '{title}' already exists. Skipping upload.")
            continue
            
        print(f"Uploading '{filename}' as source '{title}' to notebook '{target_notebook_title}'...")
        # Add file source instead of raw text to avoid command-line length limits (WinError 206)
        run_nlm_cmd(["source", "add", alias_name, "--file", filename, "--title", title, "--wait"])
        
    print("NotebookLM Sync Completed Successfully!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--notebook", default="Korea 168 Scenic Places for Foreign Visitors (drjayed)",
                        help="Notebook title to sync with")
    args = parser.parse_args()
    sync(args.notebook)
