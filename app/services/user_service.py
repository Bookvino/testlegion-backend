from sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Look up a user in the database by their email address.
    Returns the User object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()
