from jinja2 import pass_context
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal

# ✅ Templates
templates_admin = Jinja2Templates(directory="app/templates/admin")
templates_public = Jinja2Templates(directory="app/templates/public")

# ✅ CSRF-token helper function
@pass_context
def csrf_token(context):
    request = context["request"]
    return request.session.get("csrf_token", "")

# ✅ Register as global in both template engines
templates_admin.env.globals["csrf_token"] = csrf_token
templates_public.env.globals["csrf_token"] = csrf_token

# ✅ DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
