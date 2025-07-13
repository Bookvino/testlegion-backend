# app/routes/public.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates/public")

router = APIRouter()

@router.get("/", response_class=HTMLResponse, name="index")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/about", response_class=HTMLResponse, name="about")
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/privacy-policy", response_class=HTMLResponse, name="privacy_policy")
def privacy_policy(request: Request):
    return templates.TemplateResponse("privacy_policy.html", {"request": request})

@router.get("/terms-and-conditions", response_class=HTMLResponse, name="terms_and_conditions")
def terms_and_conditions(request: Request):
    return templates.TemplateResponse("terms_and_conditions.html", {"request": request})
