from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import yt_dlp
import os
import uuid

app = FastAPI()

API_KEY = os.getenv("API_KEY")

DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


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

    ext = "mp3" if type == "audio" else "mp4"

    filename = f"{uuid.uuid4()}.{ext}"

    filepath = os.path.join(
        DOWNLOAD_DIR,
        filename
    )

    ydl_opts = {
        "outtmpl": filepath,
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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return FileResponse(filepath)
