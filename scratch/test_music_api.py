import sys
import subprocess

try:
    from gradio_client import Client
except ImportError:
    print("Installing gradio_client...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio_client"])
    from gradio_client import Client

print("Connecting to facebook/MusicGen Space...")
client = Client("facebook/MusicGen")
print("\n--- API VIEW ---")
client.view_api()
