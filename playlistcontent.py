import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

def get_playlist_metadata(playlist_url: str):
    access_token = os.getenv("SOUNDCLOUD_CLIENT_ID")
    if not access_token:
        raise ValueError("Missing SOUNDCLOUD_CLIENT_ID environment variable.")

    playlist_id = get_playlist_id_from_html(playlist_url)

    endpoint = f"https://api.soundcloud.com/playlists/{playlist_id}"
    endpoint = "https://api.soundcloud.com/playlists/soundcloud:playlists:1638270391?access=playable%2Cpreview&show_tracks=true"
    headers = {
        "Authorization": f"OAuth {access_token}"
    }

    res = requests.get(endpoint, headers=headers)
    res.raise_for_status()
    playlist = res.json()

    print(f"Playlist: {playlist['title']}")
    for track in playlist['tracks']:
        print(f"- {track['title']} by {track['user']['username']}")

    return "ok"

def get_playlist_id_from_html(playlist_url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(playlist_url, headers=headers)
    response.raise_for_status()
    html = response.text

    # Find playlist ID in HTML: look for "soundcloud://playlists:{id}"
    match = re.search(r'soundcloud://playlists:(\d+)', html)
    if not match:
        raise ValueError("Playlist ID not found in page HTML.")

    playlist_id = match.group(1)
    print(f"Playlist ID: {playlist_id}")
    return playlist_id
