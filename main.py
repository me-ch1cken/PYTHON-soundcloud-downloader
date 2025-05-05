from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from downloader import download_soundcloud_tracks, zip_tracks
from playlistcontent import get_playlist_metadata

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/download")
def download_as_zip(url: str = Query(..., description="SoundCloud track or playlist URL")):
    # Step 1: Download tracks
    track_paths = download_soundcloud_tracks(url)

    if not track_paths:
        return {"error": "No tracks downloaded."}

    # Step 2: Zip the tracks
    zip_path = zip_tracks(track_paths)

    # Step 3: Stream the ZIP file
    def iterfile():
        with open(zip_path, mode="rb") as f:
            yield from f

    return StreamingResponse(
        iterfile(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{zip_path.split("/")[-1]}"'
        }
    )

@app.get("/content")
def get_playlist_content(url: str = Query(..., description="SoundCloud track or playlist URL")):
    return get_playlist_metadata(url)