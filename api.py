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

    api = "https://api.cobalt.tools/api/json"

    payload = {
        "url": url,
        "isAudioOnly": type == "audio"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
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
            detail=str(data)
        )

    return RedirectResponse(data["url"])
