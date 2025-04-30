import subprocess
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# client configuration
client_id = os.getenv("SOUNDCLOUD_CLIENT_ID")
playlist_url = 'https://soundcloud.com/klofama/klofama-somebody-scream?si=b03425e8c0fc42bcb86c4eef95ba27bc&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing'
download_dir = './songs'

if not client_id:
    raise ValueError("❌ Missing SOUNDCLOUD_CLIENT_ID environment variable in your .env file.")

# create download directory if it doesn't exist
os.makedirs(download_dir, exist_ok=True)

# download the songs
command = [
    "scdl",
    "--path", download_dir,
    "-l", playlist_url,
    "--client-id", client_id,
    "--download-archive", os.path.join(download_dir, ".scdl-archive.txt")  # Prevent redownload
]

try:
    subprocess.run(command, check=True)
    print(f"✅ Download complete! Saved to: {download_dir}")
except subprocess.CalledProcessError as e:
    print("❌ Download failed:", e)