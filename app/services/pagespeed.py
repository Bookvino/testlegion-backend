import os
import logging
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.pagespeed_analysis import PageSpeedAnalysis, PageSpeedAudit

load_dotenv()
logging.basicConfig(level=logging.INFO)

def run_pagespeed_analysis(url: str, db: Session = SessionLocal(), user_id: int = None):
    logging.info(f"\n🔍 STARTER analyse for {url}")
    strategies = ["desktop", "mobile"]

    for strategy in strategies:
        api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": url,
            "strategy": strategy,
            "key": os.getenv("PAGESPEED_API_KEY")
        }
        headers = {"Accept": "application/json"}
        response = requests.get(api_url, params=params, headers=headers)

        if response.status_code != 200:
            logging.error(f"❌ Fejl ved {strategy}-analyse for {url}")
            continue

        data = response.json()
        score = data["lighthouseResult"]["categories"]["performance"]["score"] * 100

        # Gem hovedanalysen
        analysis = PageSpeedAnalysis(
            url=url,
            strategy=strategy,
            performance_score=score,
            user_id=user_id
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # Hent audits og gem dem
        audits_data = data["lighthouseResult"].get("audits", {})
        for audit in audits_data.values():
            audit_score = audit.get("score")
            if audit_score is not None and audit_score < 1:
                db.add(PageSpeedAudit(
                    analysis_id=analysis.id,
                    title=audit.get("title"),
                    description=audit.get("description"),
                    display_value=audit.get("displayValue"),
                    audit_score=audit_score
                ))
        db.commit()

    logging.info(f"🎉 Analysis finished for {url}")

def get_latest_analysis_with_scores(db: Session):
    # Hent nyeste desktop og mobil analyse for samme URL (hvis muligt)
    desktop = (
        db.query(PageSpeedAnalysis)
        .filter(PageSpeedAnalysis.strategy == "desktop")
        .order_by(PageSpeedAnalysis.created_at.desc())
        .first()
    )
    mobile = (
        db.query(PageSpeedAnalysis)
        .filter(PageSpeedAnalysis.strategy == "mobile")
        .order_by(PageSpeedAnalysis.created_at.desc())
        .first()
    )

    # Brug den nyeste som hovedanalyse (typisk desktop), og returnér scores separat
    main_analysis = desktop or mobile
    desktop_score = desktop.performance_score if desktop else None
    mobile_score = mobile.performance_score if mobile else None

    return main_analysis, desktop_score, mobile_score

# Run reanalysis using latest URL in the database
def run_reanalysis(db: Session):
    latest = db.query(PageSpeedAnalysis).order_by(PageSpeedAnalysis.created_at.desc()).first()
    if not latest:
        logging.warning("⚠️ Ingen tidligere analyse fundet – kan ikke køre reanalyse.")
        return False

    url = latest.url
    logging.info(f"♻️ Starter reanalyse for seneste URL: {url}")
    run_pagespeed_analysis(url, db)
    return True
