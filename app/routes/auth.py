# app/routes/auth.py
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.schemas import UserCreate, UserOut
from app.models.user import User
from app.services.user import create_user
from app.services.auth import authenticate_user
from app.utils.security import hash_password
from app.dependencies import templates_public

router = APIRouter(tags=["auth"])


# Render signup form
@router.get("/signup", response_class=HTMLResponse)
async def show_signup(request: Request):
    return templates_public.TemplateResponse("signup.html", {"request": request})


# Handle signup form submission (HTML version)
@router.post("/signup-form", response_class=HTMLResponse)
async def signup_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates_public.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Email already registered"}
        )

    # Use schema to create user
    hashed = hash_password(password)
    user_create = UserCreate(email=email, password=password)
    create_user(db, user_create)

    # Redirect to login page on success
    return RedirectResponse(url="/login?signup=success", status_code=303)


# Render login form
@router.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    # Check if the user just signed up successfully
    signup_success = request.query_params.get("signup") == "success"
    return templates_public.TemplateResponse("login.html", {"request": request, "signup_success": signup_success})


# Handle login form submission, authenticate user, and start session
@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates_public.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"}
        )

    # Store user ID in session
    request.session["user_id"] = user.id
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# JSON-based API signup (used by API clients, not form)
@router.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)