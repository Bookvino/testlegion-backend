from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os
from httpx import ReadTimeout

app = FastAPI()

class AnalyseInput(BaseModel):
    url: str

@app.post("/analyse")
async def analyse(input: AnalyseInput):
    api_key = os.getenv("PAGESPEED_API_KEY")
    if not api_key:
        return {"error": "API-nøgle mangler"}

    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": input.url,
        "key": api_key,
        "strategy": "desktop"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params, timeout=60.0)
            data = response.json()

        # DEBUG: Print hele svaret til Render-log
        print(f"✅ PageSpeed data for {input.url}:\n{data}")

        # Træk performance score ud
        score = data["lighthouseResult"]["categories"]["performance"]["score"]

        # Træk forbedringsforslag ud
        forbedringer = []
        audits = data.get("lighthouseResult", {}).get("audits", {})

        for audit_id, audit in audits.items():
            audit_score = audit.get("score")
            title = audit.get("title")
            description = audit.get("description")
            display_value = audit.get("displayValue")

            if audit_score is not None and audit_score < 1:
                forbedringer.append({
                    "title": title,
                    "description": description,
                    "display_value": display_value
                })

        return {
            "status": "ok",
            "url": input.url,
            "performance_score": score * 100,
            "forbedringer": forbedringer
        }

    except ReadTimeout:
        return {"error": "Google PageSpeed API svarede ikke i tide."}
    except Exception as e:
        print(f"❌ Fejl i analyse-funktionen: {e}")
        return {"error": "Uventet fejl i analysen", "details": str(e)}
