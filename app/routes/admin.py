from fastapi import APIRouter, Request, Depends, status, HTTPException, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.services.pagespeed import run_pagespeed_analysis
from app.utils.session import require_login
from app.utils.csrf import generate_csrf_token, validate_csrf_token  # ✅ CSRF helpers
from app.dependencies.common import templates_admin, get_db
from app.models.pagespeed_analysis import PageSpeedAnalysis
from app.models.user import User

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_login)]
)

# -----------------------------------------------------------
# ✅ Dashboard view
# -----------------------------------------------------------
@router.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_login)
):
    request.session["csrf_token"] = generate_csrf_token(request)  # ✅ Generate CSRF token

    recent_analyses = db.query(PageSpeedAnalysis)\
        .filter(PageSpeedAnalysis.user_id == user.id)\
        .order_by(PageSpeedAnalysis.created_at.desc())\
        .limit(10)\
        .all()

    desktop = db.query(PageSpeedAnalysis)\
        .filter(PageSpeedAnalysis.strategy == "desktop", PageSpeedAnalysis.user_id == user.id)\
        .order_by(PageSpeedAnalysis.created_at.desc())\
        .first()

    mobile = db.query(PageSpeedAnalysis)\
        .filter(PageSpeedAnalysis.strategy == "mobile", PageSpeedAnalysis.user_id == user.id)\
        .order_by(PageSpeedAnalysis.created_at.desc())\
        .first()

    audits = mobile.audits if mobile else []

    return templates_admin.TemplateResponse("dashboard.html", {
        "request": request,
        "analyses": recent_analyses,
        "desktop_score": desktop.performance_score if desktop else None,
        "mobile_score": mobile.performance_score if mobile else None,
        "analysis": mobile or desktop,
        "audits": audits,
    })

# -----------------------------------------------------------
# ✅ Analysis history page
# -----------------------------------------------------------
@router.get("/analyses", response_class=HTMLResponse, name="admin_analyses")
async def show_history(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_login)
):
    request.session["csrf_token"] = generate_csrf_token(request)  # ✅ Generate CSRF token

    user_analyses = db.query(PageSpeedAnalysis)\
        .filter(PageSpeedAnalysis.user_id == user.id)\
        .order_by(PageSpeedAnalysis.created_at.desc())\
        .all()

    return templates_admin.TemplateResponse("analyses.html", {
        "request": request,
        "analyses": user_analyses
    })

# -----------------------------------------------------------
# ✅ Empty audits page (static)
# -----------------------------------------------------------
@router.get("/audits", name="admin_audits", response_class=HTMLResponse)
async def audits_page(request: Request):
    request.session["csrf_token"] = generate_csrf_token(request)  # ✅ Generate CSRF token

    return templates_admin.TemplateResponse("audits.html", {
        "request": request
    })

# -----------------------------------------------------------
# ✅ Reanalyse (form-based)
# -----------------------------------------------------------
@router.post("/reanalyse", name="admin.trigger_reanalysis")
async def reanalyse(
    request: Request,
    url: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_login)
):
    validate_csrf_token(request, csrf_token)
    run_pagespeed_analysis(url, db, user_id=user.id)
    return RedirectResponse(url="/admin/dashboard?message=reanalyse_startet", status_code=303)

# -----------------------------------------------------------
# ✅ Manual run (form-based)
# -----------------------------------------------------------
@router.post("/run-analysis", name="admin.run_analysis")
async def run_analysis(
    request: Request,
    url: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_login)
):
    validate_csrf_token(request, csrf_token)
    run_pagespeed_analysis(url, db, user_id=user.id)
    return RedirectResponse(url="/admin/dashboard?message=analyse_startet", status_code=status.HTTP_303_SEE_OTHER)

# -----------------------------------------------------------
# ✅ Logout (form-based)
# -----------------------------------------------------------
@router.post("/logout", name="admin.logout")
async def logout(
    request: Request,
    csrf_token: str = Form(...)
):
    validate_csrf_token(request, csrf_token)
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
