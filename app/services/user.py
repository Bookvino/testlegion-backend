from sqlalchemy.orm import Session
from app.models.user import User
from app.models.schemas import UserCreate
from app.utils.security import hash_password

def create_user(db: Session, user_data: UserCreate) -> User:
    hashed = hash_password(user_data.password)

    db_user = User(
        email=user_data.email,
        hashed_password=hashed
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
