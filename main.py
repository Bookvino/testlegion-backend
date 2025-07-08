import logging
logging.basicConfig(level=logging.INFO)

# FastAPI core imports
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Database and models
from sqlalchemy.orm import Session
from app.database import Base, engine
from app.models.pagespeed_analysis import PageSpeedAnalysis
from app.models.schemas import AnalyseInput
from app.dependencies import get_db

# Services
from app.services.pagespeed import run_pagespeed_analysis
from app.services.user import create_user

# Initialize FastAPI app
app = FastAPI()

# Add session middleware to enable secure cookie-based sessions
# This allows us to store login state (e.g. user_id) in the browser session
from starlette.middleware.sessions import SessionMiddleware
import os

# add .env later
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "mysecret"))

# Dependency function that ensures a user is logged in before accessing a route
def require_login(request: Request):
    if "user" not in request.session:
        # Redirect to login page if not logged in
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return request

# Static files (CSS, JS, Images)
app.mount("/static/public", StaticFiles(directory="app/static/public"), name="public_static")
app.mount("/admin/static", StaticFiles(directory="app/static/admin"), name="admin_static")

# Register the admin router
from app.routes import admin
from app.routes import auth
app.include_router(admin.router)
app.include_router(auth.router)


# Jinja2 templates (public-facing pages)
templates_public = Jinja2Templates(directory="app/templates/public")

# Jinja2 templates (admin-facing pages - login requried)
templates_admin = Jinja2Templates(directory="app/templates/admin")

# Create DB tables (if they don't exist yet)
Base.metadata.create_all(bind=engine)

# CORS setup to allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://testlegion.com", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------- API Routes -----------

# Run PageSpeed analysis (used by frontend/JS)
@app.post("/analyse")
async def analyse(
    input: AnalyseInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    background_tasks.add_task(run_pagespeed_analysis, input.url, db)
    return {"message": "Analysen er startet i baggrunden"}

# Root page
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates_public.TemplateResponse("index.html", {"request": request})




