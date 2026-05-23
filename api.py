from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import yt_dlp
import os
import uuid
import glob

app = FastAPI()

API_KEY = os.getenv("API_KEY")

DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

cookies_file = "cookies.txt"


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

    output_template = os.path.join(
        DOWNLOAD_DIR,
        f"{unique_id}.%(ext)s"
    )

    ydl_opts = {
        "outtmpl": output_template,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "cookiefile": cookies_file,
        "prefer_ffmpeg": True,
        "concurrent_fragment_downloads": 5,
        "retries": 10,
        "fragment_retries": 10,
    }

    if type == "audio":

        ydl_opts.update({
            "format": "bestaudio/best",

            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        })

    else:

        ydl_opts.update({
            "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])/best[ext=mp4]/best",
            "merge_output_format": "mp4"
        })

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=False)

            expected_file = ydl.prepare_filename(info)

            if type == "audio":
                expected_file = os.path.splitext(expected_file)[0] + ".mp3"

            if os.path.exists(expected_file):

                return FileResponse(
                    expected_file,
                    filename=os.path.basename(expected_file)
                )

            ydl.download([url])

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    files = glob.glob(
        os.path.join(
            DOWNLOAD_DIR,
            f"{unique_id}*"
        )
    )

    if not files:

        raise HTTPException(
            status_code=500,
            detail="Downloaded file not found"
        )

    return FileResponse(
        files[0],
        filename=os.path.basename(files[0])
    )
