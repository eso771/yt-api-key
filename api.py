from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import asyncio
import os
import re
import uuid
import glob

app = FastAPI()

API_KEY = os.getenv("API_KEY")

DOWNLOAD_DIR = "downloads"
COOKIES_FILE = "cookies.txt"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def ydl_opts_audio(output):
    return {
        "format": "bestaudio/best",
        "outtmpl": output,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "cookiefile": COOKIES_FILE,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        }
    }


def ydl_opts_video(output):
    return {
        "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
        "outtmpl": output,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "cookiefile": COOKIES_FILE,
        "merge_output_format": "mp4",
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        }
    }


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    out, err = await proc.communicate()

    if err:
        return err.decode()

    return out.decode()


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

    output = os.path.join(
        DOWNLOAD_DIR,
        f"{unique_id}.%(ext)s"
    )

    try:

        if type == "audio":

            opts = ydl_opts_audio(output)

        else:

            opts = ydl_opts_video(output)

        loop = asyncio.get_running_loop()

        def run_download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, run_download)

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
