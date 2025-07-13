from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.dependencies.common import get_db
from app.dependencies.common import templates_public as templates
from app.models.user import User
from app.utils.security import verify_password
from app.utils.csrf import validate_csrf_token, generate_csrf_token  # ✅ Import both

router = APIRouter()

# -----------------------------------------------------------
# ✅ Login form (GET)
# -----------------------------------------------------------
@router.get("/login", response_class=HTMLResponse, name="show_login")
def login_get(request: Request):
    # ✅ Save CSRF token in session so the template can access it
    request.session["csrf_token"] = generate_csrf_token(request)

    return templates.TemplateResponse("login.html", {
        "request": request,
    })


# -----------------------------------------------------------
# ✅ Login handler (POST)
# -----------------------------------------------------------
@router.post("/login")
def login_post(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    validate_csrf_token(request, csrf_token)

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Forkert e-mail eller adgangskode"
        })

    request.session["user_id"] = user.id
    return RedirectResponse("/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)

# -----------------------------------------------------------
# ✅ Signup form (GET)
# -----------------------------------------------------------
@router.get("/signup", response_class=HTMLResponse, name="show_signup")
def signup_get(request: Request):
    # ✅ Save CSRF token in session for template use
    request.session["csrf_token"] = generate_csrf_token(request)
    return templates.TemplateResponse("signup.html", {
        "request": request
    })

# -----------------------------------------------------------
# ✅ Signup handler (POST)
# -----------------------------------------------------------
@router.post("/signup")
def signup_post(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    validate_csrf_token(request, csrf_token)

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": "E-mailen er allerede registreret"
        })

    new_user = User(email=email)
    new_user.set_password(password)
    db.add(new_user)
    db.commit()

    return RedirectResponse(url="/login?message=signup_success", status_code=status.HTTP_303_SEE_OTHER)

