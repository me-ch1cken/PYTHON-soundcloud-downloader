import subprocess
import os
import zipfile
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DOWNLOAD_DIR = './songs'

def download_soundcloud_tracks(playlist_url: str) -> list[str]:
    client_id = os.getenv("SOUNDCLOUD_CLIENT_ID")
    if not client_id:
        raise ValueError("Missing SOUNDCLOUD_CLIENT_ID environment variable.")
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    command = [
        "scdl",
        "--path", DOWNLOAD_DIR,
        "-l", playlist_url,
        "--client-id", client_id,
        "--download-archive", os.path.join(DOWNLOAD_DIR, ".scdl-archive.txt")
    ]

    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
        for line in proc.stdout:
            print(line, end='')

    # Collect downloaded .mp3 files
    downloaded_files = [
        os.path.join(DOWNLOAD_DIR, f)
        for f in os.listdir(DOWNLOAD_DIR)
        if not f.endswith(".txt")
    ]

    return downloaded_files

def zip_tracks(track_paths: list[str]) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    zip_path = os.path.join(DOWNLOAD_DIR, f"tracks_{timestamp}.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in track_paths:
            zipf.write(file_path, arcname=os.path.basename(file_path))  # Clean filename inside zip

    return zip_path
