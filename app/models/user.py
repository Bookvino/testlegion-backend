# app/models/user.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.utils.security import hash_password
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # ✅ Matches services/user.py
    analyses = relationship("PageSpeedAnalysis", back_populates="user")

    def set_password(self, plain_password: str):
        """Hashes and sets the user's password."""
        self.hashed_password = hash_password(plain_password)