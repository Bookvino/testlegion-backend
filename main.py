from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

class AnalyseInput(BaseModel):
    url: str

@app.post("/analyse")
async def analyse(input: AnalyseInput):
    api_key = os.getenv("PAGESPEED_API_KEY")  # <- henter nøglen som miljøvariabel
    if not api_key:
        return {"error": "API-nøgle mangler"}

    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": input.url,
        "key": api_key,
        "strategy": "desktop"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=params)
        data = response.json()

    try:
        score = data["lighthouseResult"]["categories"]["performance"]["score"]
        return {
            "status": "ok",
            "url": input.url,
            "performance_score": score * 100
        }
    except Exception as e:
        return {"error": "Kunne ikke læse score", "details": str(e)}

