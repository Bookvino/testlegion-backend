import logging
import os

from fastapi import FastAPI, BackgroundTasks, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlalchemy.orm import Session

# Local imports
from app.database import Base, engine
from app.dependencies.common import get_db
from app.models.schemas import AnalyseInput
from app.services.pagespeed import run_pagespeed_analysis
from app.routes import admin, auth, public
from app.dependencies import common  

# -----------------------------------------------------------
# ✅ Logging
# -----------------------------------------------------------
logging.basicConfig(level=logging.INFO)

# -----------------------------------------------------------
# ✅ Initialize FastAPI app
# -----------------------------------------------------------
app = FastAPI()


# -----------------------------------------------------------
# ✅ Middleware
# -----------------------------------------------------------

# Session support
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "mysecret"))

# CORS (for local and deployed frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://testlegion.com",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# ✅ Static files
# -----------------------------------------------------------
app.mount("/static/public", StaticFiles(directory="app/static/public"), name="public_static")
app.mount("/admin/static", StaticFiles(directory="app/static/admin"), name="admin_static")

# -----------------------------------------------------------
# ✅ Templates setup
# -----------------------------------------------------------
templates_public = Jinja2Templates(directory="app/templates/public")
templates_admin = Jinja2Templates(directory="app/templates/admin")

# -----------------------------------------------------------
# ✅ Routers
# -----------------------------------------------------------
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(public.router)

# -----------------------------------------------------------
# ✅ Create database tables
# -----------------------------------------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------
# ✅ Analyse endpoint (API)
# -----------------------------------------------------------
@app.post("/analyse")
async def analyse(
    input: AnalyseInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    background_tasks.add_task(run_pagespeed_analysis, input.url, db)
    return {"message": "Analysen er startet i baggrunden"}
