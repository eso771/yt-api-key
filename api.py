from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import os
import uuid

app = FastAPI()

DOWNLOAD_DIR = "downloads"
COOKIES_FILE = "cookies.txt"   # <- mütləq əlavə et

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def get_ydl_opts(is_audio: bool):
    base = {
        "quiet": True,
        "noplaylist": True,
        "cookiefile": COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "extractor_retries": 3,
    }

    if is_audio:
        base.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        base.update({
            "format": "best[height<=720]",
        })

    return base


@app.get("/")
async def root():
    return {"status": "OK"}


@app.get("/download")
async def download(url: str, type: str, api_key: str):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")

    uid = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_DIR, f"{uid}.%(ext)s")

    is_audio = type == "audio"

    ydl_opts = get_ydl_opts(is_audio)
    ydl_opts["outtmpl"] = output

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

    files = [f for f in os.listdir(DOWNLOAD_DIR) if uid in f]

    if not files:
        raise HTTPException(status_code=500, detail="File not found")

    return FileResponse(os.path.join(DOWNLOAD_DIR, files[0]))
