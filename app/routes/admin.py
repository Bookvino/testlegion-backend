from fastapi import APIRouter, Request, Depends, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.services.pagespeed import run_pagespeed_analysis
from app.utils.session import require_login
from app.dependencies import templates_admin, get_db
from app.models.pagespeed_analysis import PageSpeedAnalysis

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_login)]
)

# Dashboard route – shows latest analyses
@router.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(request: Request, db: Session = Depends(get_db)):
    recent_analyses = db.query(PageSpeedAnalysis)\
        .order_by(PageSpeedAnalysis.created_at.desc())\
        .limit(10)\
        .all()

    desktop = db.query(PageSpeedAnalysis)\
        .filter(PageSpeedAnalysis.strategy == "desktop")\
        .order_by(PageSpeedAnalysis.created_at.desc())\
        .first()

    mobile = db.query(PageSpeedAnalysis)\
        .filter(PageSpeedAnalysis.strategy == "mobile")\
        .order_by(PageSpeedAnalysis.created_at.desc())\
        .first()

    audits = mobile.audits if mobile else []

    return templates_admin.TemplateResponse("dashboard.html", {
        "request": request,
        "analyses": recent_analyses,
        "desktop_score": desktop.performance_score if desktop else None,
        "mobile_score": mobile.performance_score if mobile else None,
        "analysis": mobile or desktop,
        "audits": audits
    })

# History page – shows all past analyses
@router.get("/history", response_class=HTMLResponse, name="admin_history")
async def show_history(request: Request, db: Session = Depends(get_db)):
    # Fetch all analyses, ordered newest first
    all_analyses = db.query(PageSpeedAnalysis)\
        .order_by(PageSpeedAnalysis.created_at.desc())\
        .all()

    return templates_admin.TemplateResponse("history.html", {
        "request": request,
        "analyses": all_analyses
    })

# Audits page – shows all past audits
@router.get("/audits", name="admin_audits", response_class=HTMLResponse)
async def audits_page(request: Request):
    return templates_admin.TemplateResponse("audits.html", {
        "request": request
    })


# Trigger reanalysis and redirect back to dashboard
@router.post("/reanalyse", name="admin.trigger_reanalysis")
async def reanalyse(
    url: str = Form(...),
    db: Session = Depends(get_db)
):
    run_pagespeed_analysis(url, db)
    return RedirectResponse(url="/admin/dashboard", status_code=303)

# Log out route
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

# Route to view all past analyses
@router.get("/analyses", response_class=HTMLResponse, name="admin_analyses")
async def view_analyses(request: Request, db: Session = Depends(get_db)):
    analyses = db.query(PageSpeedAnalysis).order_by(PageSpeedAnalysis.created_at.desc()).all()
    return templates_admin.TemplateResponse("analyses.html", {
        "request": request,
        "analyses": analyses
    })
