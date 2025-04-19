import os
import httpx
from httpx import ReadTimeout
from dotenv import load_dotenv

load_dotenv()

async def fetch_single_analysis(url: str, strategy: str) -> dict:
    api_key = os.getenv("PAGESPEED_API_KEY")
    if not api_key:
        error_msg = f"❌ Missing API key for {strategy} analysis"
        print(error_msg)
        return {"error": error_msg}

    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": api_key,
        "strategy": strategy
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params, timeout=60.0)
            response.raise_for_status()  # Fanger fx 4xx og 5xx
            data = response.json()

        print(f"✅ PageSpeed data for {url} ({strategy}) hentet")

        score = data["lighthouseResult"]["categories"]["performance"]["score"]
        audits = data.get("lighthouseResult", {}).get("audits", {})

        improvements = []
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
        error_msg = f"❌ Timeout on {strategy} strategy"
        print(error_msg)
        return {"error": error_msg}
    except httpx.HTTPStatusError as http_error:
        error_msg = f"❌ HTTP error on {strategy}: {http_error.response.status_code} – {http_error.response.text}"
        print(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"❌ Unexpected error on {strategy}: {e}"
        print(error_msg)
        return {"error": error_msg, "details": str(e)}

async def run_pagespeed_analysis(url: str) -> dict:
    print(f"\n🔍 Starting analysis for {url}\n")

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



