import os
import httpx
from httpx import ReadTimeout
from dotenv import load_dotenv

load_dotenv()

async def fetch_single_analysis(url: str, strategy: str) -> dict:
    api_key = os.getenv("PAGESPEED_API_KEY")
    if not api_key:
        return {"error": "Missing API key"}

    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": api_key,
        "strategy": strategy
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params, timeout=60.0)
            data = response.json()

        print(f"✅ PageSpeed data for {url} ({strategy}):\n{data}")

        score = data["lighthouseResult"]["categories"]["performance"]["score"]
        improvements = []
        audits = data.get("lighthouseResult", {}).get("audits", {})

        for audit in audits.values():
            audit_score = audit.get("score")
            if audit_score is not None and audit_score < 1:
                improvements.append({
                    "title": audit.get("title"),
                    "description": audit.get("description"),
                    "display_value": audit.get("displayValue")
                })

        return {
            "strategy": strategy,
            "performance_score": score * 100,
            "improvements": improvements
        }

    except ReadTimeout:
        return {"error": f"Timeout on {strategy} strategy"}
    except Exception as e:
        print(f"❌ Error during {strategy} analysis: {e}")
        return {"error": f"Unexpected error on {strategy}", "details": str(e)}

async def run_pagespeed_analysis(url: str) -> dict:
    # I fremtiden kan vi her tjekke brugertype og kun kalde én strategi
    desktop_result = await fetch_single_analysis(url, "desktop")
    mobile_result = await fetch_single_analysis(url, "mobile")

    return {
        "status": "ok",
        "url": url,
        "results": {
            "desktop": desktop_result,
            "mobile": mobile_result
        }
    }


