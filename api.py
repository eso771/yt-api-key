from fastapi import FastAPI, HTTPException
import yt_dlp
import os
import uuid

app = FastAPI()

API_KEY = os.getenv("API_KEY")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def get_cookie():
    cookie_dir = "cookies"
    try:
        files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
        if not files:
            return None
        return os.path.join(cookie_dir, files[0])
    except:
        return None


@app.get("/download")
async def download(url: str, type: str, api_key: str):

    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    uid = str(uuid.uuid4())
    output = os.path.join(DOWNLOAD_DIR, f"{uid}.%(ext)s")

    cookie_file = get_cookie()

    ydl_opts = {
        "outtmpl": output,
        "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        }
    }

    if cookie_file:
        ydl_opts["cookiefile"] = cookie_file

    try:
        if type == "audio":
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }],
                "prefer_ffmpeg": True,
            })
        else:
            ydl_opts.update({
                "format": "bv*+ba/best[ext=mp4]/best"
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    files = [f for f in os.listdir(DOWNLOAD_DIR) if uid in f]

    if not files:
        raise HTTPException(status_code=500, detail="File not found")

    return os.path.join(DOWNLOAD_DIR, files[0])
