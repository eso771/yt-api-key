from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import yt_dlp
import os
import uuid

app = FastAPI()

API_KEY = os.getenv("API_KEY")

DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {"status": "API işləyir"}


@app.get("/download")
async def download(
    url: str,
    type: str,
    api_key: str
):

    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )

    unique_id = str(uuid.uuid4())

    filepath = os.path.join(
        DOWNLOAD_DIR,
        unique_id
    )

    ydl_opts = {
        "outtmpl": filepath + ".%(ext)s",
        "format": "bestaudio/best"
        if type == "audio"
        else "best"
    }

    if type == "audio":

        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    final_file = None

    for file in os.listdir(DOWNLOAD_DIR):

        if file.startswith(unique_id):

            final_file = os.path.join(
                DOWNLOAD_DIR,
                file
            )

            break

    if not final_file:

        raise HTTPException(
            status_code=500,
            detail="Download failed"
        )

    return FileResponse(final_file)
