from sclib import SoundcloudAPI, Track, Playlist

def get_playlist_metadata(url: str) -> Playlist:
    api = SoundcloudAPI()
    playlist = api.resolve(url)

    assert type(playlist) is Playlist, "Expected a Playlist object"

    playlist_data = {
        "title": playlist.title,
        "tracks": [
            {
                "title": track.title,
                "author": track.user["username"],
                "duration": track.duration,
                "artwork_url": track.artwork_url,
            }
            for track in playlist.tracks
        ]
    }

    return playlist_data