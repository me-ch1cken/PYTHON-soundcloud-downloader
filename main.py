import os
from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from downloader import download_soundcloud_tracks, zip_tracks, clear_downloads
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
def download_as_zip(
    url: str = Query(..., description="SoundCloud track or playlist URL"),
    background_tasks: BackgroundTasks = None
):
    
    clear_downloads()  # Clear old downloads before starting a new one

    # Step 1: Download tracks
    track_paths = download_soundcloud_tracks(url)
    if not track_paths:
        return {"error": "No tracks downloaded."}

    # Step 2: Zip the tracks
    zip_path = zip_tracks(track_paths)

    # Register cleanup to happen after response
    background_tasks.add_task(clear_downloads)

    # Step 3: Define a generator that closes the file after use
    def file_iterator(path: str):
        with open(path, "rb") as f:
            yield from f
        # Cleanup only after streaming is fully done
        background_tasks.add_task(clear_downloads)

    # Step 4: Return streaming response
    return StreamingResponse(
        file_iterator(zip_path),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{os.path.basename(zip_path)}"'
        },
        background=background_tasks
    )

@app.get("/content")
def get_playlist_content(url: str = Query(..., description="SoundCloud track or playlist URL")):
    return get_playlist_metadata(url)