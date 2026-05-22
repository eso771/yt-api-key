from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

import aiohttp
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY")


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

    api = "https://co.wuk.sh/api/json"

    payload = {
        "url": url,
        "isAudioOnly": type == "audio"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:

        async with session.post(
            api,
            json=payload,
            headers=headers
        ) as r:

            data = await r.json()

    if data.get("status") != "stream":

        raise HTTPException(
            status_code=500,
            detail="Download failed"
        )

    return RedirectResponse(data["url"])
