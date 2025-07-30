from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.dependencies.common import get_db
from app.dependencies.common import templates_public as templates
from app.models.user import User
from app.utils.security import verify_password
from app.utils.csrf import validate_csrf_token, generate_csrf_token
from app.utils.token import verify_reset_token
from app.services.user_service import get_user_by_email
from app.services.email_service import send_confirmation_email, send_welcome_email

router = APIRouter()

# -----------------------------------------------------------
# ✅ Login form (GET)
# -----------------------------------------------------------
@router.get("/login", response_class=HTMLResponse, name="show_login")
def login_get(request: Request):
    # ✅ Save CSRF token in session so the template can access it
    request.session["csrf_token"] = generate_csrf_token(request)

    # Extract optional message from query params
    message = request.query_params.get("message")

    return templates.TemplateResponse("login.html", {
        "request": request,
    })

# -----------------------------------------------------------
# ✅ Forgot password (GET) – show form to request reset link
# -----------------------------------------------------------
@router.get("/forgot-password", response_class=HTMLResponse, name="forgot_password_get")
def forgot_password_get(request: Request):
    # Save CSRF token to session
    request.session["csrf_token"] = generate_csrf_token(request)

    return templates.TemplateResponse("forgot_password.html", {
        "request": request
    })

# -----------------------------------------------------------
# ✅ Password reset (GET)
# -----------------------------------------------------------
@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_form(request: Request, token: str):
    # Store token temporarily in session for POST handling
    request.session["reset_token"] = token

    return templates.TemplateResponse("reset_password_form.html", {
        "request": request,
        "token": token,  # optional if you want to include token in hidden field
        "csrf_token": generate_csrf_token(request)
    })

# -----------------------------------------------------------
# ✅ Password reset (POST)
# -----------------------------------------------------------
@router.post("/reset-password", name="reset_password_post")
async def reset_password_post(
    request: Request,
    password: str = Form(...),
    confirm_password: str = Form(...),
    token: str = Form(...),  # <-- hent token direkte fra form
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    
    
    # ✅ Validate CSRF token
    validate_csrf_token(request, csrf_token)

    # ✅ Decode token to get email
    email = verify_reset_token(token)
    print("📬 Decoded email from token:", email)

    if not email:
        return RedirectResponse(url="/login?message=session_expired", status_code=302)

    # ✅ Password match check
    if password != confirm_password:
        return templates.TemplateResponse("reset_password_form.html", {
            "request": request,
            "error": "Passwords do not match.",
            "csrf_token": generate_csrf_token(request),
            "token": token  # vigtigt at sende den tilbage
        })

    # ✅ Update password
    user = get_user_by_email(db, email)
    if not user:
        return RedirectResponse(url="/login?message=user_not_found", status_code=302)

    user.set_password(password)
    db.commit()

    # ✅ Redirect with success
    return RedirectResponse(
        url="/login?message=password_reset_success",
        status_code=status.HTTP_303_SEE_OTHER
    )


# -----------------------------------------------------------
# ✅ Login handler (POST)
# -----------------------------------------------------------
@router.post("/login", name="signup_post")
def login_post(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    validate_csrf_token(request, csrf_token)

    # Look up user by email
    user = db.query(User).filter(User.email == email).first()

    # Invalid email or password
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Incorrect email or password"
        })
    
    # Reject login if email is not confirmed
    if not user.is_verified:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "You must confirm your email before you can log in."
        })

    # Login success – save user ID in session
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
async def signup_post(
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
            "error": "E-mail is already registered"
        })

    new_user = User(email=email)
    new_user.set_password(password)
    db.add(new_user)
    db.commit()

        
    # Send welcome email
    await send_confirmation_email(email=email)

    return RedirectResponse(url="/login?message=signup_success", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/confirm-email")
async def confirm_email(token: str, db: Session = Depends(get_db)):
    # Decode the token to get the email
    try:
        email = email = verify_reset_token(token)

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Look up user in database
    user: User = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # If not yet verified, mark as verified and send welcome email
    if not user.is_verified:
        user.is_verified = True
        db.commit()
        await send_welcome_email(user.email)

    # Redirect to login with success message
    return RedirectResponse(url="/login?message=email_confirmed", status_code=status.HTTP_303_SEE_OTHER)


# -----------------------------------------------------------
# ✅ Forgot Password handler (POST)
# -----------------------------------------------------------
@router.post("/forgot-password")
async def forgot_password_post(
    request: Request,
    email: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    validate_csrf_token(request, csrf_token)

    user = get_user_by_email(db, email)
    if user:
        # User found – send email with reset link
        from app.services.email_service import send_password_reset_email
        await send_password_reset_email(user.email)

    return RedirectResponse(url="/login?message=resetlink_sent", status_code=302)

