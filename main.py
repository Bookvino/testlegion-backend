from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

class AnalyseInput(BaseModel):
    url: str

from httpx import ReadTimeout

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

        print(f"PageSpeed raw data for {input.url}:")
        print(data)

        # Udtræk og print forslag til forbedringer
        audits = data.get("lighthouseResult", {}).get("audits", {})
        print("\n🔍 Forslag til forbedringer:\n")

        for audit_id, audit in audits.items():
            score = audit.get("score")
            title = audit.get("title")
            description = audit.get("description")
            display_value = audit.get("displayValue")

            if score is not None and score < 1:
                print(f"📌 {title}")
                if display_value:
                    print(f"   ➤ {display_value}")
                if description:
                    print(f"   🧠 {description}")
                print()

        # Returnér performance score til API
        score = data["lighthouseResult"]["categories"]["performance"]["score"]
        print(f"Performance score for {input.url}: {score * 100}")
        return {
            "status": "ok",
            "url": input.url,
            "performance_score": score * 100
        }

    except ReadTimeout:
        return {"error": "Google PageSpeed API svarede ikke i tide. Prøv igen senere."}
    except Exception as e:
        return {"error": "Kunne ikke læse eller behandle data", "details": str(e)}
