import os
import requests

def get_keys():
    # Load env file manually
    env_vars = {}
    env_path = "D:/Entertainments/DevEnvironment/autovideo/.env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        env_vars[parts[0].strip()] = parts[1].strip()

    token = env_vars.get("SUPABASE_ACCESS_TOKEN")
    if not token:
        print("SUPABASE_ACCESS_TOKEN not found in .env")
        return

    project_ref = "dggxjxgnsecspiubaeie"
    url = f"https://api.supabase.com/v1/projects/{project_ref}/api-keys"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    print(f"Fetching keys for project {project_ref}...")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        keys = response.json()
        for key in keys:
            name = key.get("name")
            api_key = key.get("api_key")
            print(f"Key Name: {name}")
            print(f"API Key: {api_key[:15]}...{api_key[-15:] if len(api_key) > 30 else ''}")
            # print the full key for debugging (we can write it to a local temporary file or use it directly)
            with open("scratch/supabase_keys_full.txt", "a") as out:
                out.write(f"{name}={api_key}\n")
        print("Keys saved to scratch/supabase_keys_full.txt")
    else:
        print(f"Failed to fetch keys: {response.status_code} - {response.text}")

if __name__ == "__main__":
    get_keys()
