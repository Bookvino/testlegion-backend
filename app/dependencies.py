from fastapi.templating import Jinja2Templates
from app.database import SessionLocal

# Jinja2 environment for admin templates
templates_admin = Jinja2Templates(directory="app/templates/admin")
templates_public = Jinja2Templates(directory="app/templates/public")


# Dependency for DB access
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
