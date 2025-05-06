import os, uuid
from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
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

# Track jobs in memory (use Redis or DB in production)
download_jobs = {}

@app.post("/prepare-download")
def prepare_download(url: str = Query(...), background_tasks: BackgroundTasks = None):
    download_id = str(uuid.uuid4())
    download_jobs[download_id] = {"status": "preparing", "path": None}

    def process():
        try:
            clear_downloads()
            track_paths = download_soundcloud_tracks(url)
            if not track_paths:
                download_jobs[download_id] = {"status": "error", "path": None}
                return
            zip_path = zip_tracks(track_paths)
            download_jobs[download_id] = {"status": "ready", "path": zip_path}
        except Exception:
            download_jobs[download_id] = {"status": "error", "path": None}

    background_tasks.add_task(process)

    return {"downloadId": download_id}

@app.get("/download-status/{download_id}")
def download_status(download_id: str):
    job = download_jobs.get(download_id)
    if not job:
        return JSONResponse(status_code=404, content={"status": "not_found"})
    return {"status": job["status"]}

@app.get("/download/{download_id}")
def download_file(download_id: str):
    job = download_jobs.get(download_id)
    if not job or job["status"] != "ready":
        return JSONResponse(status_code=404, content={"error": "Download not ready"})
    
    file_path = job["path"]
    return FileResponse(
        path=file_path,
        media_type="application/zip",
        filename=os.path.basename(file_path)
    )

@app.get("/content")
def get_playlist_content(url: str = Query(...)):
    return get_playlist_metadata(url)
